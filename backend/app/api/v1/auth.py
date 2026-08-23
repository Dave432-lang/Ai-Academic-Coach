"""
Authentication Endpoints (/api/v1/auth).
Provides student account registration, login, and current profile token verification.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserMeResponse,
    UserSignupRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
def signup(
    request: UserSignupRequest,
    db: Session = Depends(get_db),
):
    """
    Registers a new student, hashes password with Argon2id, creates profile shell,
    and returns JWT access token for immediate onboarding access.
    """
    return auth_service.signup_user(db=db, request=request)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate student credentials",
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticates email and password, checks account status, updates last_login_at timestamp,
    and issues JWT bearer access token.
    """
    return auth_service.login_user(db=db, request=request)


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current authenticated user details",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Returns current authenticated student user account and onboarding status.
    Never exposes password hash.
    """
    return auth_service.get_user_me(user=current_user)
