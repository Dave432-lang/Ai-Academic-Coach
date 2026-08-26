from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.course import CourseEnrollmentRead
from app.services.course_service import (
    get_student_profile_by_user_id,
    get_student_courses,
    get_student_course_by_id,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=List[CourseEnrollmentRead])
def list_enrolled_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return get_student_courses(db, profile.id)


@router.get("/{course_id}", response_model=CourseEnrollmentRead)
def get_enrolled_course_detail(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return get_student_course_by_id(db, profile.id, course_id)
