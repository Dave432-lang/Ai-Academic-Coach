"""
Phase 4 Unit and Integration Test Suite: Academic Management API.
Tests Courses, Events, Tasks, Study Sessions, Goals, Grades, and Dashboard Summary endpoints.
Executed directly against live PostgreSQL database to verify ENUM mappings, FK checks, ownership isolation, and validation rules.
"""
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.database.connection import SessionLocal
from app.database.models import User, StudentProfile, University, Course, CourseEnrollment, AcademicStatus


def _get_auth_headers(client: TestClient, email: str) -> dict:
    unique_email = f"{uuid.uuid4().hex[:6]}_{email}"
    signup_res = client.post(
        "/api/v1/auth/signup",
        json={"email": unique_email, "password": "password123"},
    )
    if signup_res.status_code != status.HTTP_201_CREATED:
        login_res = client.post(
            "/api/v1/auth/login",
            data={"username": unique_email, "password": "password123"},
        )
        token = login_res.json()["access_token"]
    else:
        token = signup_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _setup_student_with_course(client: TestClient, email: str, univ_name: str, course_code: str, course_name: str) -> dict:
    headers = _get_auth_headers(client, email)

    univ_res = client.post(
        "/api/v1/universities",
        json={"name": univ_name, "country": "Ghana"},
        headers=headers,
    )
    univ_id = univ_res.json()["id"]

    client.post(
        "/api/v1/onboarding/profile",
        json={
            "full_name": f"Student {email}",
            "timezone": "UTC",
            "university_id": univ_id,
            "academic_year": "2026/2027",
            "semester": "Semester 1",
        },
        headers=headers,
    )

    cres = client.post(
        "/api/v1/onboarding/courses",
        json={"course_code": course_code, "course_name": course_name},
        headers=headers,
    )
    course_id = cres.json()["course_id"]

    client.post("/api/v1/onboarding/complete", headers=headers)

    return {
        "headers": headers,
        "course_id": course_id,
        "email": email,
    }


def test_courses_endpoints(client: TestClient):
    user_data = _setup_student_with_course(client, "course_user@example.com", "Legon", "DCIT301", "Operating Systems")
    headers = user_data["headers"]
    course_id = user_data["course_id"]

    # 1. List enrolled courses
    res = client.get("/api/v1/courses", headers=headers)
    assert res.status_code == status.HTTP_200_OK
    courses = res.json()
    assert len(courses) >= 1
    codes = [c["course"]["course_code"] for c in courses]
    assert "DCIT301" in codes

    # 2. Get course detail
    detail_res = client.get(f"/api/v1/courses/{course_id}", headers=headers)
    assert detail_res.status_code == status.HTTP_200_OK
    assert detail_res.json()["course"]["course_code"] == "DCIT301"

    # 3. Non-existent / non-enrolled course ID returns 404
    fake_id = str(uuid.uuid4())
    fake_res = client.get(f"/api/v1/courses/{fake_id}", headers=headers)
    assert fake_res.status_code == status.HTTP_404_NOT_FOUND


def test_academic_events_crud_and_ownership(client: TestClient):
    student1 = _setup_student_with_course(client, "event_s1@example.com", "UG", "MATH201", "Calculus II")
    student2 = _setup_student_with_course(client, "event_s2@example.com", "KNUST", "MATH201", "Calculus II")

    headers1 = student1["headers"]
    course_id1 = student1["course_id"]
    headers2 = student2["headers"]

    due_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()

    # 1. Create event
    event_payload = {
        "course_id": course_id1,
        "event_type": "exam",
        "title": "Midterm Exam",
        "due_at": due_time,
        "description": "Calculus II Midterm Exam",
        "priority": "high",
    }
    res = client.post("/api/v1/events", json=event_payload, headers=headers1)
    assert res.status_code == status.HTTP_201_CREATED
    event_data = res.json()
    event_id = event_data["id"]
    assert event_data["title"] == "Midterm Exam"
    assert event_data["event_type"] == "exam"

    # 2. List events
    list_res = client.get(f"/api/v1/events?course_id={course_id1}", headers=headers1)
    assert list_res.status_code == status.HTTP_200_OK
    assert len(list_res.json()) >= 1

    # 3. Ownership check: student 2 cannot view student 1's event
    s2_view = client.get(f"/api/v1/events/{event_id}", headers=headers2)
    assert s2_view.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    # 4. Student 1 cannot create event for student 2's course ID
    invalid_create = client.post(
        "/api/v1/events",
        json={
            "course_id": student2["course_id"],
            "event_type": "quiz",
            "title": "Unauthorized Quiz",
            "due_at": due_time,
        },
        headers=headers1,
    )
    assert invalid_create.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    # 5. Patch event
    patch_res = client.patch(f"/api/v1/events/{event_id}", json={"status": "completed"}, headers=headers1)
    assert patch_res.status_code == status.HTTP_200_OK
    assert patch_res.json()["status"] == "completed"

    # 6. Delete event
    del_res = client.delete(f"/api/v1/events/{event_id}", headers=headers1)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT


def test_tasks_crud_and_validation(client: TestClient):
    student = _setup_student_with_course(client, "task_user@example.com", "UCC", "CS201", "Data Structures")
    headers = student["headers"]
    course_id = student["course_id"]

    # Create task linked to course
    task_payload = {
        "title": "Implement Binary Tree",
        "description": "Lab assignment 3",
        "priority": "high",
        "estimated_minutes": 120,
        "course_id": course_id,
    }
    res = client.post("/api/v1/tasks", json=task_payload, headers=headers)
    assert res.status_code == status.HTTP_201_CREATED
    tdata = res.json()
    task_id = tdata["id"]
    assert tdata["title"] == "Implement Binary Tree"
    assert tdata["estimated_minutes"] == 120

    # List tasks
    lres = client.get(f"/api/v1/tasks?course_id={course_id}", headers=headers)
    assert lres.status_code == status.HTTP_200_OK
    assert len(lres.json()) >= 1

    # Update task (mark complete)
    ures = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "completed"}, headers=headers)
    assert ures.status_code == status.HTTP_200_OK
    assert ures.json()["status"] == "completed"

    # Delete task
    dres = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert dres.status_code == status.HTTP_204_NO_CONTENT


def test_study_sessions_crud(client: TestClient):
    student = _setup_student_with_course(client, "study_user@example.com", "Pentecost", "ENG101", "Communication")
    headers = student["headers"]
    course_id = student["course_id"]

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    # 1. Create study session
    payload = {
        "course_id": course_id,
        "scheduled_start": start.isoformat(),
        "scheduled_end": end.isoformat(),
        "topic": "Essay Writing Techniques",
        "notes": "Focus on thesis statement creation",
    }
    res = client.post("/api/v1/study-sessions", json=payload, headers=headers)
    assert res.status_code == status.HTTP_201_CREATED
    sdata = res.json()
    session_id = sdata["id"]
    assert sdata["topic"] == "Essay Writing Techniques"

    # 2. Invalid schedule end before start returns 422
    bad_payload = {
        "course_id": course_id,
        "scheduled_start": end.isoformat(),
        "scheduled_end": start.isoformat(),
    }
    bad_res = client.post("/api/v1/study-sessions", json=bad_payload, headers=headers)
    assert bad_res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # 3. Update session
    ures = client.patch(
        f"/api/v1/study-sessions/{session_id}",
        json={"completion_percentage": 100, "status": "completed", "actual_minutes": 120},
        headers=headers,
    )
    assert ures.status_code == status.HTTP_200_OK
    assert ures.json()["completion_percentage"] == 100

    # 4. Delete session
    dres = client.delete(f"/api/v1/study-sessions/{session_id}", headers=headers)
    assert dres.status_code == status.HTTP_204_NO_CONTENT


def test_goals_crud(client: TestClient):
    student = _setup_student_with_course(client, "goal_user@example.com", "UPSA", "ACCT101", "Financial Accounting")
    headers = student["headers"]
    course_id = student["course_id"]

    goal_payload = {
        "title": "Achieve Grade A in Accounting",
        "description": "Maintain 85%+ score on all assignments",
        "course_id": course_id,
        "target_value": 85.0,
        "current_value": 75.0,
    }
    res = client.post("/api/v1/goals", json=goal_payload, headers=headers)
    assert res.status_code == status.HTTP_201_CREATED
    gdata = res.json()
    goal_id = gdata["id"]
    assert gdata["title"] == "Achieve Grade A in Accounting"

    # Update goal progress
    ures = client.patch(f"/api/v1/goals/{goal_id}", json={"current_value": 88.0, "status": "achieved"}, headers=headers)
    assert ures.status_code == status.HTTP_200_OK
    assert ures.json()["status"] == "achieved"

    # Delete goal
    dres = client.delete(f"/api/v1/goals/{goal_id}", headers=headers)
    assert dres.status_code == status.HTTP_204_NO_CONTENT


def test_grades_crud_and_validation(client: TestClient):
    student = _setup_student_with_course(client, "grade_user@example.com", "UMaT", "MIN101", "Mining Engineering")
    headers = student["headers"]
    course_id = student["course_id"]

    # 1. Successful grade creation
    payload = {
        "course_id": course_id,
        "assessment_name": "Mid-Semester Quiz",
        "assessment_type": "quiz",
        "score": 18.5,
        "max_score": 20.0,
    }
    res = client.post("/api/v1/grades", json=payload, headers=headers)
    assert res.status_code == status.HTTP_201_CREATED
    gdata = res.json()
    grade_id = gdata["id"]
    assert gdata["percentage"] == 92.5

    # 2. Score > max_score validation failure returns 422
    bad_payload = {
        "course_id": course_id,
        "assessment_name": "Invalid Test",
        "score": 25.0,
        "max_score": 20.0,
    }
    bad_res = client.post("/api/v1/grades", json=bad_payload, headers=headers)
    assert bad_res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Score cannot exceed max score" in str(bad_res.json())

    # 3. List grades
    lres = client.get(f"/api/v1/grades?course_id={course_id}", headers=headers)
    assert lres.status_code == status.HTTP_200_OK
    assert len(lres.json()) >= 1

    # 4. Delete grade
    dres = client.delete(f"/api/v1/grades/{grade_id}", headers=headers)
    assert dres.status_code == status.HTTP_204_NO_CONTENT


def test_dashboard_summary(client: TestClient):
    student = _setup_student_with_course(client, "dash_user@example.com", "AAMUSTED", "EDU101", "Education Foundations")
    headers = student["headers"]
    course_id = student["course_id"]

    # Create 1 event, 1 task, 1 study session, 1 grade
    due_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    client.post(
        "/api/v1/events",
        json={"course_id": course_id, "event_type": "assignment", "title": "Term Paper", "due_at": due_time},
        headers=headers,
    )
    client.post(
        "/api/v1/tasks",
        json={"course_id": course_id, "title": "Outline Introduction", "status": "pending"},
        headers=headers,
    )
    client.post(
        "/api/v1/study-sessions",
        json={
            "course_id": course_id,
            "scheduled_start": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "scheduled_end": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
            "topic": "Literature Review",
        },
        headers=headers,
    )
    client.post(
        "/api/v1/grades",
        json={"course_id": course_id, "assessment_name": "Quiz 1", "score": 90, "max_score": 100},
        headers=headers,
    )

    # Fetch dashboard summary
    res = client.get("/api/v1/dashboard/summary", headers=headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["enrolled_courses_count"] >= 1
    assert data["upcoming_events_count"] >= 1
    assert data["active_tasks_count"] >= 1
    assert data["study_sessions_this_week_count"] >= 1
    assert len(data["recent_grades"]) >= 1
    assert data["recent_grades"][0]["assessment_name"] == "Quiz 1"
