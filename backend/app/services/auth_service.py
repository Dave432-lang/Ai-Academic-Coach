"""
Authentication Service.
Handles student signup, secure login, credential verification, and user state retrieval.
"""
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.database.models import AccountStatus, StudentProfile, User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserMeResponse,
    UserResponse,
    UserSignupRequest,
)


def signup_user(db: Session, request: UserSignupRequest) -> TokenResponse:
    """
    Registers a new student account.
    Normalizes email, verifies minimum password requirements, creates user and profile shell,
    and returns JWT token for immediate onboarding.
    """
    normalized_email = request.email.strip().lower()

    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    hashed_pw = hash_password(request.password)

    new_user = User(
        email=normalized_email,
        password_hash=hashed_pw,
        account_status=AccountStatus.ACTIVE,
    )
    db.add(new_user)
    db.flush()

    # Create associated student profile shell
    profile = StudentProfile(
        user_id=new_user.id,
        full_name="",
        timezone="UTC",
        onboarding_completed=False,
    )
    db.add(profile)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(subject=str(new_user.id))

    user_resp = UserResponse(
        id=new_user.id,
        email=new_user.email,
        account_status=new_user.account_status,
        onboarding_completed=False,
        created_at=new_user.created_at,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_resp,
    )


def login_user(db: Session, request: UserLoginRequest) -> TokenResponse:
    """
    Authenticates a student login attempt.
    Validates credentials without revealing whether an email exists, verifies account status,
    updates last_login_at, and issues JWT access token.
    """
    normalized_email = request.email.strip().lower()

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or inactive",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))

    onboarding_completed = False
    if user.profile:
        onboarding_completed = user.profile.onboarding_completed

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        account_status=user.account_status,
        onboarding_completed=onboarding_completed,
        created_at=user.created_at,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_resp,
    )


def get_user_me(user: User) -> UserMeResponse:
    """
    Returns current authenticated user details and onboarding completion status.
    """
    onboarding_completed = False
    if user.profile:
        onboarding_completed = user.profile.onboarding_completed

    return UserMeResponse(
        id=user.id,
        email=user.email,
        account_status=user.account_status,
        onboarding_completed=onboarding_completed,
    )
