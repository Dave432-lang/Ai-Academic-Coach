from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import Grade
from app.schemas.grade import GradeCreate, GradeUpdate
from app.services.course_service import verify_course_enrollment


def create_grade(db: Session, student_id: uuid.UUID, data: GradeCreate) -> Grade:
    verify_course_enrollment(db, student_id=student_id, course_id=data.course_id)
    if data.score > data.max_score:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Score cannot exceed max score",
        )

    grade = Grade(
        student_id=student_id,
        course_id=data.course_id,
        assessment_name=data.assessment_name,
        assessment_type=data.assessment_type,
        score=data.score,
        max_score=data.max_score,
        graded_at=data.graded_at,
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


def list_grades(
    db: Session,
    student_id: uuid.UUID,
    course_id: Optional[uuid.UUID] = None,
) -> List[Grade]:
    query = db.query(Grade).filter(Grade.student_id == student_id)
    if course_id:
        query = query.filter(Grade.course_id == course_id)
    return query.order_by(Grade.created_at.desc()).all()


def get_grade_by_id(db: Session, student_id: uuid.UUID, grade_id: uuid.UUID) -> Grade:
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found",
        )
    if grade.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this grade record",
        )
    return grade


def update_grade(
    db: Session,
    student_id: uuid.UUID,
    grade_id: uuid.UUID,
    data: GradeUpdate,
) -> Grade:
    grade = get_grade_by_id(db, student_id, grade_id)
    update_dict = data.model_dump(exclude_unset=True)

    new_score = update_dict.get("score", grade.score)
    new_max = update_dict.get("max_score", grade.max_score)
    if new_score > new_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Score cannot exceed max score",
        )

    for field, value in update_dict.items():
        setattr(grade, field, value)
    db.commit()
    db.refresh(grade)
    return grade


def delete_grade(db: Session, student_id: uuid.UUID, grade_id: uuid.UUID) -> None:
    grade = get_grade_by_id(db, student_id, grade_id)
    db.delete(grade)
    db.commit()
