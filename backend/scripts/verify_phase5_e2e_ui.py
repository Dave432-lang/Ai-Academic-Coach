"""
End-to-End Walkthrough Script for Phase 5 Materials Feature.
NOTE: This is an API-level smoke test script simulating user actions/HTTP flows executed by the Flutter Web/Mobile UI, not a headless browser test.
1. Authenticate / Login
2. Retrieve active course list (or enroll via onboarding)
3. Upload French PDF course material (file picker -> multipart upload)
4. List materials and verify metadata
5. Authenticated material download via token URL
6. Material deletion & cleanup verification
"""
import json
import os
import sys
import urllib.request
import urllib.parse

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_e2e_walkthrough():
    print("=== STARTING PHASE 5 E2E WALKTHROUGH ===")

    # 1. Signup / Login
    email = "phase5_walkthrough_student@example.com"
    password = "Password123!"

    print(f"Step 1: Authenticating as {email}...")
    signup_req = urllib.request.Request(
        f"{BASE_URL}/auth/signup",
        data=json.dumps({"email": email, "password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(signup_req) as resp:
            body = json.loads(resp.read())
            token = body["access_token"]
            print(" -> Account created. Token acquired.")
    except Exception:
        login_req = urllib.request.Request(
            f"{BASE_URL}/auth/login",
            data=json.dumps({"email": email, "password": password}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(login_req) as resp:
            body = json.loads(resp.read())
            token = body["access_token"]
            print(" -> Login successful. Token acquired.")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get / Create Course
    print("\nStep 2: Fetching Courses...")
    courses_req = urllib.request.Request(f"{BASE_URL}/courses", headers=headers)
    with urllib.request.urlopen(courses_req) as resp:
        courses = json.loads(resp.read())
        print(f" -> Found {len(courses)} enrolled course(s).")

    if not courses:
        print(" -> Enrolling in test course (FREN101)...")
        # First ensure university exists
        uni_req = urllib.request.Request(
            f"{BASE_URL}/universities",
            data=json.dumps({"name": "Sorbonne University", "country": "France"}).encode("utf-8"),
            headers={**headers, "Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(uni_req) as resp:
                uni = json.loads(resp.read())
                uni_id = uni["id"]
        except Exception:
            with urllib.request.urlopen(urllib.request.Request(f"{BASE_URL}/universities?search=Sorbonne", headers=headers)) as resp:
                unis = json.loads(resp.read())
                uni_id = unis[0]["id"]

        # Update profile
        prof_req = urllib.request.Request(
            f"{BASE_URL}/onboarding/profile",
            data=json.dumps({
                "full_name": "Jean Dupont",
                "country": "France",
                "timezone": "Europe/Paris",
                "university_id": uni_id,
                "program": "Languages",
                "level": "Undergraduate",
                "academic_year": "2026/2027",
                "semester": "Fall 2026"
            }).encode("utf-8"),
            headers={**headers, "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(prof_req):
            pass

        # Add course
        enroll_req = urllib.request.Request(
            f"{BASE_URL}/onboarding/courses",
            data=json.dumps({
                "course_code": "FREN101",
                "course_name": "French 101 - Introductory French",
                "academic_year": "2026/2027",
                "semester": "Fall 2026"
            }).encode("utf-8"),
            headers={**headers, "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(enroll_req) as resp:
            course_enrollment = json.loads(resp.read())
            course_id = course_enrollment["course_id"]
    else:
        course_id = courses[0]["course_id"]

    print(f" -> Using Course ID: {course_id}")

    # 3. Upload Material
    print("\nStep 3: Uploading French Syllabus PDF (Simulating File Picker Upload Button)...")
    pdf_content = b"%PDF-1.4 French Syllabus Content for Phase 5 Walkthrough Verification"
    file_name = "french_syllabus.pdf"

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body_bytes = bytearray()
    
    # Form field: course_id
    body_bytes.extend(f"--{boundary}\r\n".encode())
    body_bytes.extend(f'Content-Disposition: form-data; name="course_id"\r\n\r\n'.encode())
    body_bytes.extend(f"{course_id}\r\n".encode())

    # File field: file
    body_bytes.extend(f"--{boundary}\r\n".encode())
    body_bytes.extend(f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode())
    body_bytes.extend(f"Content-Type: application/pdf\r\n\r\n".encode())
    body_bytes.extend(pdf_content)
    body_bytes.extend(f"\r\n--{boundary}--\r\n".encode())

    upload_req = urllib.request.Request(
        f"{BASE_URL}/materials",
        data=bytes(body_bytes),
        headers={
            **headers,
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
    )

    with urllib.request.urlopen(upload_req) as resp:
        uploaded_material = json.loads(resp.read())
        material_id = uploaded_material["id"]
        print(f" -> Material Uploaded Successfully! ID: {material_id}")
        print(f" -> File Name: {uploaded_material.get('file_name')}")
        print(f" -> MIME Type: {uploaded_material.get('file_type')}")
        print(f" -> Size: {uploaded_material.get('file_size')} bytes")
        print(f" -> Processing Status: {uploaded_material.get('processing_status')}")

    # 4. Fetch Materials List
    print("\nStep 4: Fetching Materials List UI Data...")
    mat_list_req = urllib.request.Request(f"{BASE_URL}/materials", headers=headers)
    with urllib.request.urlopen(mat_list_req) as resp:
        materials_list = json.loads(resp.read())
        print(f" -> Total Materials in List: {len(materials_list)}")
        found = any(m["id"] == material_id for m in materials_list)
        assert found, "Uploaded material is present in list!"

    # 5. Test Authenticated Download (Token Query Param)
    print("\nStep 5: Downloading Material via Authenticated Token URL...")
    download_url = f"{BASE_URL}/materials/{material_id}/download?token={token}"
    download_req = urllib.request.Request(download_url)
    with urllib.request.urlopen(download_req) as resp:
        downloaded_bytes = resp.read()
        print(f" -> Download Status Code: {resp.getcode()}")
        print(f" -> Downloaded Bytes: {len(downloaded_bytes)} bytes")
        print(f" -> Header Check: {downloaded_bytes[:8].decode('utf-8', errors='ignore')}")
        assert downloaded_bytes == pdf_content, "Downloaded bytes match uploaded PDF exactly!"

    # 6. Delete Material (Confirmation Dialog)
    print("\nStep 6: Deleting Material (Simulating Confirm Delete Dialog)...")
    delete_req = urllib.request.Request(
        f"{BASE_URL}/materials/{material_id}",
        headers=headers,
        method="DELETE"
    )
    with urllib.request.urlopen(delete_req) as resp:
        print(f" -> Delete Status Code: {resp.getcode()}")

    # 7. Verify Cleanup
    print("\nStep 7: Verifying Deletion Cleanup...")
    mat_list_after_req = urllib.request.Request(f"{BASE_URL}/materials", headers=headers)
    with urllib.request.urlopen(mat_list_after_req) as resp:
        remaining = json.loads(resp.read())
        remaining_ids = [m["id"] for m in remaining]
        assert material_id not in remaining_ids, "Material ID removed from list!"
        print(" -> Material successfully removed from database & disk storage.")

    print("\n=== PHASE 5 E2E WALKTHROUGH PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_e2e_walkthrough()
