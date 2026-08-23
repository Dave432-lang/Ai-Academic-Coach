"""
Onboarding Service.
Manages university search/creation, student profile configuration, course enrollments,
and onboarding completion validation.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database.models import (
    Course,
    CourseEnrollment,
    EnrollmentStatus,
    StudentProfile,
    University,
    User,
)
from app.schemas.onboarding import (
    CourseAddRequest,
    CourseEnrollmentResponse,
    OnboardingStatusResponse,
    StudentProfileResponse,
    StudentProfileUpdateRequest,
    UniversityCreateRequest,
    UniversitySearchResponse,
)


def search_universities(
    db: Session, search: Optional[str] = None, limit: int = 20
) -> List[UniversitySearchResponse]:
    """
    Search existing universities by name or country.
    """
    query = db.query(University)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                University.name.ilike(term),
                University.country.ilike(term),
            )
        )
    safe_limit = min(max(1, limit), 100)
    universities = query.order_by(University.name.asc()).limit(safe_limit).all()
    return [UniversitySearchResponse.model_validate(u) for u in universities]


def create_university(
    db: Session, request: UniversityCreateRequest
) -> UniversitySearchResponse:
    """
    Creates a new university record while strictly avoiding duplicates for UNIQUE(name, country).
    """
    name_clean = request.name.strip()
    country_clean = request.country.strip()

    existing = (
        db.query(University)
        .filter(
            func.lower(University.name) == name_clean.lower(),
            func.lower(University.country) == country_clean.lower(),
        )
        .first()
    )
    if existing:
        return UniversitySearchResponse.model_validate(existing)

    new_univ = University(
        name=name_clean,
        country=country_clean,
        website=request.website.strip() if request.website else None,
        timezone=request.timezone.strip() if request.timezone else None,
    )
    db.add(new_univ)
    db.commit()
    db.refresh(new_univ)
    return UniversitySearchResponse.model_validate(new_univ)


def get_or_create_profile(db: Session, user: User) -> StudentProfile:
    """
    Ensures a StudentProfile object exists for the given User.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(
            user_id=user.id,
            full_name="",
            timezone="UTC",
            onboarding_completed=False,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_student_profile(
    db: Session, user: User, request: StudentProfileUpdateRequest
) -> StudentProfileResponse:
    """
    Updates the authenticated student's academic profile information.
    """
    profile = get_or_create_profile(db, user)

    if request.university_id:
        univ = db.query(University).filter(University.id == request.university_id).first()
        if not univ:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected university not found",
            )
        profile.university_id = request.university_id

    profile.full_name = request.full_name.strip()
    if request.country is not None:
        profile.country = request.country.strip() if request.country else None
    if request.timezone:
        profile.timezone = request.timezone.strip()
    if request.program is not None:
        profile.program = request.program.strip() if request.program else None
    if request.level is not None:
        profile.level = request.level.strip() if request.level else None
    if request.academic_year is not None:
        profile.academic_year = request.academic_year.strip() if request.academic_year else None
    if request.semester is not None:
        profile.semester = request.semester.strip() if request.semester else None

    db.commit()
    db.refresh(profile)

    return _build_profile_response(profile)


def add_course_and_enroll(
    db: Session, user: User, request: CourseAddRequest
) -> CourseEnrollmentResponse:
    """
    Creates or reuses a course for the student's university and enrolls the student.
    Enforces UNIQUE(student_id, course_id, academic_year, semester).
    """
    profile = get_or_create_profile(db, user)
    if not profile.university_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a university in your profile before adding courses",
        )

    academic_year = (request.academic_year or profile.academic_year or "").strip()
    semester = (request.semester or profile.semester or "").strip()

    if not academic_year or not semester:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Academic year and semester are required to enroll in a course",
        )

    code_clean = request.course_code.strip().upper()
    name_clean = request.course_name.strip()

    # Find existing course for university or create new
    course = (
        db.query(Course)
        .filter(
            Course.university_id == profile.university_id,
            func.upper(Course.course_code) == code_clean,
        )
        .first()
    )

    if not course:
        course = Course(
            university_id=profile.university_id,
            course_code=code_clean,
            course_name=name_clean,
            description=request.description.strip() if request.description else None,
            credit_hours=request.credit_hours,
        )
        db.add(course)
        db.flush()

    # Check existing active enrollment
    existing_enrollment = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.student_id == profile.id,
            CourseEnrollment.course_id == course.id,
            CourseEnrollment.academic_year == academic_year,
            CourseEnrollment.semester == semester,
        )
        .first()
    )

    if existing_enrollment:
        if existing_enrollment.status == EnrollmentStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student is already enrolled in this course for the specified academic term",
            )
        else:
            existing_enrollment.status = EnrollmentStatus.ACTIVE
            db.commit()
            db.refresh(existing_enrollment)
            enrollment = existing_enrollment
    else:
        enrollment = CourseEnrollment(
            student_id=profile.id,
            course_id=course.id,
            academic_year=academic_year,
            semester=semester,
            status=EnrollmentStatus.ACTIVE,
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)

    return CourseEnrollmentResponse(
        id=enrollment.id,
        course_id=course.id,
        course_code=course.course_code,
        course_name=course.course_name,
        academic_year=enrollment.academic_year,
        semester=enrollment.semester,
        status=enrollment.status,
    )


def get_onboarding_status(db: Session, user: User) -> OnboardingStatusResponse:
    """
    Evaluates current student onboarding progress and lists missing requirements.
    """
    profile = get_or_create_profile(db, user)

    has_profile = bool(profile.full_name and profile.full_name.strip() and profile.timezone)
    has_university = bool(profile.university_id)
    has_academic_info = bool(
        profile.program and profile.level and profile.academic_year and profile.semester
    )

    active_course_count = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.student_id == profile.id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE,
        )
        .count()
    )

    missing = []
    if not profile.full_name or not profile.full_name.strip():
        missing.append("Full name")
    if not profile.timezone:
        missing.append("Timezone")
    if not has_university:
        missing.append("University selection")
    if not profile.program:
        missing.append("Programme / Major")
    if not profile.level:
        missing.append("Academic level")
    if not profile.academic_year:
        missing.append("Academic year")
    if not profile.semester:
        missing.append("Semester")
    if active_course_count < 1:
        missing.append("At least one active course enrollment")

    is_complete = profile.onboarding_completed and len(missing) == 0

    return OnboardingStatusResponse(
        onboarding_completed=is_complete,
        has_profile=has_profile,
        has_university=has_university,
        has_academic_info=has_academic_info,
        active_course_count=active_course_count,
        missing_requirements=missing,
    )


def complete_onboarding(db: Session, user: User) -> StudentProfileResponse:
    """
    Finalizes student onboarding after verifying all required fields and at least one active course enrollment.
    """
    status_info = get_onboarding_status(db, user)
    if status_info.missing_requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete onboarding. Missing requirements: {', '.join(status_info.missing_requirements)}",
        )

    profile = get_or_create_profile(db, user)
    profile.onboarding_completed = True
    profile.onboarding_completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)

    return _build_profile_response(profile)


def _build_profile_response(profile: StudentProfile) -> StudentProfileResponse:
    univ_name = profile.university.name if profile.university else None
    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        country=profile.country,
        timezone=profile.timezone,
        university_id=profile.university_id,
        university_name=univ_name,
        program=profile.program,
        level=profile.level,
        academic_year=profile.academic_year,
        semester=profile.semester,
        onboarding_completed=profile.onboarding_completed,
        onboarding_completed_at=profile.onboarding_completed_at,
    )
