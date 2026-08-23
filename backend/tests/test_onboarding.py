"""
Phase 3 Unit and Integration Test Suite: Onboarding & Academic Profile API.
Tests University search/creation, profile updates, course enrollments, duplicate rejection, and onboarding finalization.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base, get_db
from app.database.models import Course, CourseEnrollment, StudentProfile, University, User
from app.main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_onboarding_db():
    """
    Initialize fresh database schema before each test.
    """
    Base.metadata.create_all(
        bind=test_engine,
        tables=[
            User.__table__,
            StudentProfile.__table__,
            University.__table__,
            Course.__table__,
            CourseEnrollment.__table__,
        ],
    )

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(
        bind=test_engine,
        tables=[
            CourseEnrollment.__table__,
            Course.__table__,
            University.__table__,
            StudentProfile.__table__,
            User.__table__,
        ],
    )


def _get_auth_headers(client: TestClient, email: str = "onboarding@example.com") -> dict:
    signup_res = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123"},
    )
    token = signup_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_unauthenticated_onboarding_rejected(client: TestClient):
    """
    Test onboarding endpoints require authentication token.
    """
    res1 = client.get("/api/v1/onboarding/status")
    assert res1.status_code == status.HTTP_401_UNAUTHORIZED

    res2 = client.post("/api/v1/onboarding/profile", json={"full_name": "Test Student"})
    assert res2.status_code == status.HTTP_401_UNAUTHORIZED


def test_university_search_and_creation(client: TestClient):
    """
    Test creating a university, duplicate university handling, and searching.
    """
    headers = _get_auth_headers(client, "univ@example.com")

    # Create university
    payload = {
        "name": "Pentecost University",
        "country": "Ghana",
        "website": "https://pentvars.edu.gh",
        "timezone": "Africa/Accra",
    }
    res = client.post("/api/v1/universities", json=payload, headers=headers)
    assert res.status_code == status.HTTP_201_CREATED
    univ_data = res.json()
    assert univ_data["name"] == "Pentecost University"
    assert univ_data["country"] == "Ghana"
    univ_id = univ_data["id"]

    # Duplicate creation returns existing university without error
    res_dup = client.post("/api/v1/universities", json=payload, headers=headers)
    assert res_dup.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    assert res_dup.json()["id"] == univ_id

    # Search university
    search_res = client.get("/api/v1/universities?search=Pentecost", headers=headers)
    assert search_res.status_code == status.HTTP_200_OK
    search_data = search_res.json()
    assert len(search_data) >= 1
    assert search_data[0]["name"] == "Pentecost University"


def test_student_profile_update_and_status(client: TestClient):
    """
    Test updating student academic profile.
    """
    headers = _get_auth_headers(client, "profile@example.com")

    # Create university first
    univ_res = client.post(
        "/api/v1/universities",
        json={"name": "University of Ghana", "country": "Ghana"},
        headers=headers,
    )
    univ_id = univ_res.json()["id"]

    profile_payload = {
        "full_name": "Kofi Mensah",
        "country": "Ghana",
        "timezone": "Africa/Accra",
        "university_id": univ_id,
        "program": "Computer Science",
        "level": "Undergraduate Level 300",
        "academic_year": "2026/2027",
        "semester": "Semester 1",
    }
    res = client.post("/api/v1/onboarding/profile", json=profile_payload, headers=headers)
    assert res.status_code == status.HTTP_200_OK
    pdata = res.json()
    assert pdata["full_name"] == "Kofi Mensah"
    assert pdata["university_name"] == "University of Ghana"
    assert pdata["program"] == "Computer Science"
    assert pdata["onboarding_completed"] is False

    status_res = client.get("/api/v1/onboarding/status", headers=headers)
    assert status_res.status_code == status.HTTP_200_OK
    sdata = status_res.json()
    assert sdata["has_profile"] is True
    assert sdata["has_university"] is True
    assert sdata["has_academic_info"] is True
    assert sdata["active_course_count"] == 0
    assert "At least one active course enrollment" in sdata["missing_requirements"]


def test_course_enrollment_and_duplicate_prevention(client: TestClient):
    """
    Test adding courses, course enrollment creation, and duplicate enrollment rejection.
    """
    headers = _get_auth_headers(client, "course@example.com")

    # Setup profile with university
    univ_res = client.post(
        "/api/v1/universities",
        json={"name": "KNUST", "country": "Ghana"},
        headers=headers,
    )
    univ_id = univ_res.json()["id"]

    client.post(
        "/api/v1/onboarding/profile",
        json={
            "full_name": "Ama Serwaa",
            "timezone": "Africa/Accra",
            "university_id": univ_id,
            "academic_year": "2026/2027",
            "semester": "Semester 1",
        },
        headers=headers,
    )

    # Add course
    course_payload = {
        "course_code": "CS302",
        "course_name": "Database Systems",
        "credit_hours": 3,
    }
    cres = client.post("/api/v1/onboarding/courses", json=course_payload, headers=headers)
    assert cres.status_code == status.HTTP_201_CREATED
    cdata = cres.json()
    assert cdata["course_code"] == "CS302"
    assert cdata["course_name"] == "Database Systems"
    assert cdata["status"] == "active"

    # Duplicate course enrollment attempt returns 409 Conflict
    dup_res = client.post("/api/v1/onboarding/courses", json=course_payload, headers=headers)
    assert dup_res.status_code == status.HTTP_409_CONFLICT
    assert "already enrolled" in dup_res.json()["detail"]


def test_complete_onboarding_requires_at_least_one_course(client: TestClient):
    """
    Test that onboarding cannot be completed without at least one active course enrollment.
    """
    headers = _get_auth_headers(client, "incomplete@example.com")

    # Profile created without courses
    univ_res = client.post(
        "/api/v1/universities",
        json={"name": "Ashesi University", "country": "Ghana"},
        headers=headers,
    )
    univ_id = univ_res.json()["id"]

    client.post(
        "/api/v1/onboarding/profile",
        json={
            "full_name": "Abena Osei",
            "timezone": "Africa/Accra",
            "university_id": univ_id,
            "program": "Business Administration",
            "level": "Undergraduate Level 200",
            "academic_year": "2026/2027",
            "semester": "Semester 1",
        },
        headers=headers,
    )

    complete_res = client.post("/api/v1/onboarding/complete", headers=headers)
    assert complete_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "At least one active course enrollment" in complete_res.json()["detail"]


def test_complete_onboarding_success(client: TestClient):
    """
    Test completing onboarding successfully after filling profile and adding a course.
    """
    headers = _get_auth_headers(client, "completesuccess@example.com")

    univ_res = client.post(
        "/api/v1/universities",
        json={"name": "Ashesi University", "country": "Ghana"},
        headers=headers,
    )
    univ_id = univ_res.json()["id"]

    client.post(
        "/api/v1/onboarding/profile",
        json={
            "full_name": "Yaw Boateng",
            "timezone": "Africa/Accra",
            "university_id": univ_id,
            "program": "Computer Engineering",
            "level": "Undergraduate Level 400",
            "academic_year": "2026/2027",
            "semester": "Semester 1",
        },
        headers=headers,
    )

    client.post(
        "/api/v1/onboarding/courses",
        json={"course_code": "CE401", "course_name": "Embedded Systems"},
        headers=headers,
    )

    complete_res = client.post("/api/v1/onboarding/complete", headers=headers)
    assert complete_res.status_code == status.HTTP_200_OK
    cdata = complete_res.json()
    assert cdata["onboarding_completed"] is True
    assert cdata["onboarding_completed_at"] is not None

    # Check /auth/me now reflects onboarding_completed = True
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == status.HTTP_200_OK
    assert me_res.json()["onboarding_completed"] is True
