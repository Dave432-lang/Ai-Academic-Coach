"""
Phase 3 Unit and Integration Test Suite: Authentication API.
Tests Signup, Login, Password Hashing, JWT Tokens, Account Status, and Current User retrieval.
"""
from datetime import datetime, timedelta, timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, verify_password
from app.database.connection import Base, get_db
from app.database.models import AccountStatus, Course, CourseEnrollment, StudentProfile, University, User
from app.main import app


# Set up isolated in-memory SQLite database with StaticPool for thread-safe test execution
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_auth_db():
    """
    Initialize fresh database schema before each test and override get_db dependency.
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


def test_signup_success(client: TestClient):
    """
    Test successful user registration returns access_token and safe user response.
    """
    payload = {"email": "newstudent@example.com", "password": "securepassword123"}
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newstudent@example.com"
    assert data["user"]["account_status"] == "active"
    assert data["user"]["onboarding_completed"] is False
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_signup_duplicate_email_rejected(client: TestClient):
    """
    Test duplicate email signup returns 400 Bad Request.
    """
    payload = {"email": "duplicate@example.com", "password": "password123"}
    res1 = client.post("/api/v1/auth/signup", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = client.post("/api/v1/auth/signup", json=payload)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in res2.json()["detail"]


def test_signup_password_hashed_in_database(client: TestClient):
    """
    Test password stored in database is hashed with Argon2id and not plaintext.
    """
    raw_pw = "mysecretpassword123"
    payload = {"email": "hashtest@example.com", "password": raw_pw}
    res = client.post("/api/v1/auth/signup", json=payload)
    assert res.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "hashtest@example.com").first()
    assert user is not None
    assert user.password_hash != raw_pw
    assert user.password_hash.startswith("$argon2id$")
    assert verify_password(raw_pw, user.password_hash) is True
    db.close()


def test_signup_short_password_rejected(client: TestClient):
    """
    Test password shorter than 8 characters is rejected.
    """
    payload = {"email": "shortpw@example.com", "password": "short"}
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, 422]


def test_login_success(client: TestClient):
    """
    Test successful login returns access token and updates last_login_at timestamp.
    """
    signup_payload = {"email": "logintest@example.com", "password": "validpassword123"}
    client.post("/api/v1/auth/signup", json=signup_payload)

    login_payload = {"email": "logintest@example.com", "password": "validpassword123"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "logintest@example.com"

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "logintest@example.com").first()
    assert user.last_login_at is not None
    db.close()


def test_login_invalid_password(client: TestClient):
    """
    Test login with wrong password returns 401 Unauthorized.
    """
    signup_payload = {"email": "wrongpw@example.com", "password": "validpassword123"}
    client.post("/api/v1/auth/signup", json=signup_payload)

    login_payload = {"email": "wrongpw@example.com", "password": "incorrectpassword"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email or password"


def test_login_unknown_email(client: TestClient):
    """
    Test login with non-existent email returns safe 401 Unauthorized without disclosing user existence.
    """
    login_payload = {"email": "nonexistent@example.com", "password": "somepassword123"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email or password"


def test_login_suspended_account_rejected(client: TestClient):
    """
    Test suspended account login returns 403 Forbidden.
    """
    signup_payload = {"email": "suspended@example.com", "password": "validpassword123"}
    client.post("/api/v1/auth/signup", json=signup_payload)

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "suspended@example.com").first()
    user.account_status = AccountStatus.SUSPENDED
    db.commit()
    db.close()

    login_payload = {"email": "suspended@example.com", "password": "validpassword123"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "suspended" in response.json()["detail"]


def test_get_me_success(client: TestClient):
    """
    Test /auth/me endpoint returns authenticated user details.
    """
    signup_res = client.post(
        "/api/v1/auth/signup",
        json={"email": "metest@example.com", "password": "password123"},
    )
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "metest@example.com"
    assert data["account_status"] == "active"
    assert data["onboarding_completed"] is False
    assert "password" not in data
    assert "password_hash" not in data


def test_get_me_missing_token(client: TestClient):
    """
    Test accessing protected /auth/me without Bearer token returns 401.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_invalid_token(client: TestClient):
    """
    Test accessing protected /auth/me with invalid token returns 401.
    """
    headers = {"Authorization": "Bearer invalid_token_xyz"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_expired_token(client: TestClient):
    """
    Test accessing protected /auth/me with expired token returns 401.
    """
    signup_res = client.post(
        "/api/v1/auth/signup",
        json={"email": "expired@example.com", "password": "password123"},
    )
    user_id = signup_res.json()["user"]["id"]

    expired_token = create_access_token(
        subject=str(user_id),
        expires_delta=timedelta(seconds=-10),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
