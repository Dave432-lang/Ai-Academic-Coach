"""
Onboarding & University API Endpoints (/api/v1/onboarding, /api/v1/universities).
Handles academic profile updates, university search/creation, course enrollments, and onboarding finalization.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.onboarding import (
    CourseAddRequest,
    CourseEnrollmentResponse,
    OnboardingStatusResponse,
    StudentProfileResponse,
    StudentProfileUpdateRequest,
    UniversityCreateRequest,
    UniversitySearchResponse,
)
from app.services import onboarding_service

router = APIRouter(tags=["Onboarding & Academic Profile"])


@router.get(
    "/universities",
    response_model=List[UniversitySearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search existing universities",
)
def list_universities(
    search: Optional[str] = Query(default=None, description="Search term for university name or country"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search universities by name or country.
    """
    return onboarding_service.search_universities(db=db, search=search, limit=limit)


@router.post(
    "/universities",
    response_model=UniversitySearchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new university",
)
def create_university(
    request: UniversityCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a new university to the system. Enforces UNIQUE(name, country).
    """
    return onboarding_service.create_university(db=db, request=request)


@router.get(
    "/onboarding/status",
    response_model=OnboardingStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current student onboarding completion status",
)
def get_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns step-by-step onboarding progress and missing requirement checklist for the authenticated student.
    """
    return onboarding_service.get_onboarding_status(db=db, user=current_user)


@router.post(
    "/onboarding/profile",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update student personal and academic information",
)
def update_profile(
    request: StudentProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates student full name, timezone, country, university selection, programme, level, year, and semester.
    """
    return onboarding_service.update_student_profile(db=db, user=current_user, request=request)


@router.post(
    "/onboarding/courses",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add course and enroll student",
)
def add_course(
    request: CourseAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates or matches a course at the student's selected university and registers active enrollment.
    """
    return onboarding_service.add_course_and_enroll(db=db, user=user_or_profile(current_user), request=request)


def user_or_profile(user: User) -> User:
    return user


@router.post(
    "/onboarding/complete",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalize student onboarding flow",
)
def complete(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Validates all mandatory onboarding fields and at least ONE active course enrollment, then sets onboarding_completed = true.
    """
    return onboarding_service.complete_onboarding(db=db, user=current_user)
