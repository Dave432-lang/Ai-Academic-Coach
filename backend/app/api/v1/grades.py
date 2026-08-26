from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.grade import GradeCreate, GradeUpdate, GradeRead
from app.services.course_service import get_student_profile_by_user_id
from app.services.grade_service import (
    create_grade,
    list_grades,
    get_grade_by_id,
    update_grade,
    delete_grade,
)

router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("", response_model=GradeRead, status_code=status.HTTP_201_CREATED)
def create_grade_endpoint(
    payload: GradeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return create_grade(db, profile.id, payload)


@router.get("", response_model=List[GradeRead])
def list_grades_endpoint(
    course_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return list_grades(db, profile.id, course_id=course_id)


@router.get("/{grade_id}", response_model=GradeRead)
def get_grade_endpoint(
    grade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return get_grade_by_id(db, profile.id, grade_id)


@router.patch("/{grade_id}", response_model=GradeRead)
def update_grade_endpoint(
    grade_id: uuid.UUID,
    payload: GradeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return update_grade(db, profile.id, grade_id, payload)


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade_endpoint(
    grade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    delete_grade(db, profile.id, grade_id)
