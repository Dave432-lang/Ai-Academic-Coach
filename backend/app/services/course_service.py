from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import CourseEnrollment, Course, StudentProfile, EnrollmentStatus


def get_student_profile_by_user_id(db: Session, user_id: uuid.UUID) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return profile


def get_student_courses(db: Session, student_id: uuid.UUID) -> List[CourseEnrollment]:
    return (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE,
        )
        .all()
    )


def get_student_course_by_id(db: Session, student_id: uuid.UUID, course_id: uuid.UUID) -> CourseEnrollment:
    enrollment = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.course_id == course_id,
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course enrollment not found or student is not enrolled in this course",
        )
    return enrollment


def verify_course_enrollment(db: Session, student_id: uuid.UUID, course_id: uuid.UUID) -> bool:
    enrollment = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.course_id == course_id,
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course enrollment not found or access denied",
        )
    return True
