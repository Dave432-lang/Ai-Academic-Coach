import io
import os
import uuid
import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import SessionLocal
from app.database.models import CourseMaterial, MaterialProcessingStatus, StudentProfile, User
from app.core.security import hash_password


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_student_and_course(db: Session):
    """
    Setup fixture creating an authenticated student user, profile, university, and course enrollment.
    """
    from app.database.models import AccountStatus, Course, CourseEnrollment, EnrollmentStatus, University

    suffix = str(uuid.uuid4())[:8]
    email = f"materials_student_{suffix}@example.com"
    user = User(email=email, password_hash=hash_password("password123"), account_status=AccountStatus.ACTIVE)
    db.add(user)
    db.commit()
    db.refresh(user)

    univ = University(name=f"Materials Univ {suffix}", country="Ghana")
    db.add(univ)
    db.commit()
    db.refresh(univ)

    profile = StudentProfile(user_id=user.id, full_name=f"Student {suffix}", university_id=univ.id, timezone="UTC")
    db.add(profile)
    db.commit()
    db.refresh(profile)

    course = Course(university_id=univ.id, course_code=f"MAT{suffix}", course_name="Materials Testing Course")
    db.add(course)
    db.commit()
    db.refresh(course)

    enrollment = CourseEnrollment(student_id=profile.id, course_id=course.id, academic_year="2026/2027", semester="Semester 1", status=EnrollmentStatus.ACTIVE)
    db.add(enrollment)
    db.commit()

    return {"user": user, "profile": profile, "course": course}


@pytest.fixture
def auth_headers(client, test_student_and_course):
    user = test_student_and_course["user"]
    res = client.post("/api/v1/auth/login", json={"email": user.email, "password": "password123"})
    assert res.status_code == status.HTTP_200_OK
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_student_headers(client, db: Session):
    from app.database.models import AccountStatus, StudentProfile, University, User
    suffix = str(uuid.uuid4())[:8]
    email = f"other_student_{suffix}@example.com"
    user = User(email=email, password_hash=hash_password("password123"), account_status=AccountStatus.ACTIVE)
    db.add(user)
    db.commit()
    db.refresh(user)

    univ = University(name=f"Other Univ {suffix}", country="Ghana")
    db.add(univ)
    db.commit()
    db.refresh(univ)

    profile = StudentProfile(user_id=user.id, full_name=f"Other Student {suffix}", university_id=univ.id, timezone="UTC")
    db.add(profile)
    db.commit()

    res = client.post("/api/v1/auth/login", json={"email": user.email, "password": "password123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_valid_pdf_material(client, auth_headers, test_student_and_course):
    course = test_student_and_course["course"]
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    
    files = {"file": ("syllabus.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"course_id": str(course.id), "title": "Syllabus Notes"}

    response = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    assert response.status_code == status.HTTP_201_CREATED
    payload = response.json()
    assert payload["file_name"] == "Syllabus Notes.pdf"
    assert payload["file_type"] == "application/pdf"
    assert payload["file_size"] == len(pdf_content)
    assert payload["processing_status"] == "pending"
    assert payload["course_code"] == course.course_code


def test_upload_rejects_invalid_extension(client, auth_headers, test_student_and_course):
    course = test_student_and_course["course"]
    exe_content = b"MZ\x90\x00\x03\x00\x00\x00"
    files = {"file": ("malicious.exe", io.BytesIO(exe_content), "application/octet-stream")}
    data = {"course_id": str(course.id)}

    response = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert "not allowed" in response.json()["detail"]


def test_upload_rejects_invalid_magic_bytes(client, auth_headers, test_student_and_course):
    course = test_student_and_course["course"]
    fake_pdf = b"NOT_A_REAL_PDF_HEADER_TEXT"
    files = {"file": ("fake.pdf", io.BytesIO(fake_pdf), "application/pdf")}
    data = {"course_id": str(course.id)}

    response = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert "magic bytes" in response.json()["detail"]


def test_upload_rejects_oversized_file(client, auth_headers, test_student_and_course, monkeypatch):
    course = test_student_and_course["course"]
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)  # 1 MB threshold for test speed
    big_pdf = b"%PDF-1.4\n" + b"X" * (1024 * 1024 + 500)
    files = {"file": ("big.pdf", io.BytesIO(big_pdf), "application/pdf")}
    data = {"course_id": str(course.id)}

    response = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


def test_upload_rejects_unenrolled_course(client, auth_headers):
    fake_course_id = str(uuid.uuid4())
    pdf_content = b"%PDF-1.4\n%%EOF"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"course_id": fake_course_id}

    response = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


def test_cannot_access_or_delete_other_student_material(client, auth_headers, second_student_headers, test_student_and_course):
    course = test_student_and_course["course"]
    pdf_content = b"%PDF-1.4\n%%EOF"
    files = {"file": ("private.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"course_id": str(course.id)}

    upload_res = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    assert upload_res.status_code == status.HTTP_201_CREATED
    material_id = upload_res.json()["id"]

    # Second student tries GET metadata
    get_res = client.get(f"/api/v1/materials/{material_id}", headers=second_student_headers)
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

    # Second student tries GET download
    dl_res = client.get(f"/api/v1/materials/{material_id}/download", headers=second_student_headers)
    assert dl_res.status_code == status.HTTP_404_NOT_FOUND

    # Second student tries DELETE
    del_res = client.delete(f"/api/v1/materials/{material_id}", headers=second_student_headers)
    assert del_res.status_code == status.HTTP_404_NOT_FOUND


def test_list_materials_filtering(client, auth_headers, test_student_and_course):
    course = test_student_and_course["course"]
    pdf_content = b"%PDF-1.4\n%%EOF"

    files = {"file": ("doc1.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"course_id": str(course.id)}
    client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)

    res = client.get(f"/api/v1/materials?course_id={course.id}", headers=auth_headers)
    assert res.status_code == status.HTTP_200_OK
    items = res.json()
    assert len(items) >= 1
    assert all(i["course_id"] == str(course.id) for i in items)


def test_delete_material_removes_file_and_db_record(client, auth_headers, test_student_and_course, db: Session):
    course = test_student_and_course["course"]
    pdf_content = b"%PDF-1.4\n%%EOF"
    files = {"file": ("to_delete.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"course_id": str(course.id)}

    upload_res = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    assert upload_res.status_code == status.HTTP_201_CREATED
    material_id = upload_res.json()["id"]
    storage_key = upload_res.json()["storage_key"]

    abs_path = os.path.abspath(os.path.join(settings.STORAGE_PATH, storage_key))
    assert os.path.exists(abs_path)

    # Delete material
    del_res = client.delete(f"/api/v1/materials/{material_id}", headers=auth_headers)
    assert del_res.status_code == status.HTTP_200_OK

    # Assert file removed from disk and DB record removed
    assert not os.path.exists(abs_path)
    mat_db = db.query(CourseMaterial).filter(CourseMaterial.id == uuid.UUID(material_id)).first()
    assert mat_db is None


def test_delete_handles_missing_disk_file_gracefully(client, auth_headers, test_student_and_course, db: Session):
    course = test_student_and_course["course"]
    pdf_content = b"%PDF-1.4\n%%EOF"
    files = {"file": ("missing_disk.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"course_id": str(course.id)}

    upload_res = client.post("/api/v1/materials", headers=auth_headers, data=data, files=files)
    material_id = upload_res.json()["id"]
    storage_key = upload_res.json()["storage_key"]

    abs_path = os.path.abspath(os.path.join(settings.STORAGE_PATH, storage_key))
    if os.path.exists(abs_path):
        os.remove(abs_path)  # Manually delete file from disk before API call

    # Delete should succeed cleanly without 500 error
    del_res = client.delete(f"/api/v1/materials/{material_id}", headers=auth_headers)
    assert del_res.status_code == status.HTTP_200_OK
