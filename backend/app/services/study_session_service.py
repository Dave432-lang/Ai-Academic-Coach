from typing import List, Optional
import uuid
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import StudySession, Task
from app.schemas.study_session import StudySessionCreate, StudySessionUpdate
from app.services.course_service import verify_course_enrollment


def create_study_session(db: Session, student_id: uuid.UUID, data: StudySessionCreate) -> StudySession:
    if data.scheduled_end <= data.scheduled_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Scheduled end time must be after scheduled start time",
        )

    if data.course_id:
        verify_course_enrollment(db, student_id=student_id, course_id=data.course_id)

    if data.task_id:
        task = db.query(Task).filter(Task.id == data.task_id).first()
        if not task or task.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or access denied",
            )
        if not data.course_id and task.course_id:
            data.course_id = task.course_id

    session = StudySession(
        student_id=student_id,
        course_id=data.course_id,
        task_id=data.task_id,
        scheduled_start=data.scheduled_start,
        scheduled_end=data.scheduled_end,
        topic=data.topic,
        notes=data.notes,
        status=data.status,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_study_sessions(
    db: Session,
    student_id: uuid.UUID,
    course_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[StudySession]:
    query = db.query(StudySession).filter(StudySession.student_id == student_id)
    if course_id:
        query = query.filter(StudySession.course_id == course_id)
    if start_date:
        query = query.filter(StudySession.scheduled_start >= start_date)
    if end_date:
        query = query.filter(StudySession.scheduled_end <= end_date)
    return query.order_by(StudySession.scheduled_start.asc()).all()


def get_study_session_by_id(db: Session, student_id: uuid.UUID, session_id: uuid.UUID) -> StudySession:
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found",
        )
    if session.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this study session",
        )
    return session


def update_study_session(
    db: Session,
    student_id: uuid.UUID,
    session_id: uuid.UUID,
    data: StudySessionUpdate,
) -> StudySession:
    session = get_study_session_by_id(db, student_id, session_id)
    update_dict = data.model_dump(exclude_unset=True)

    new_start = update_dict.get("scheduled_start", session.scheduled_start)
    new_end = update_dict.get("scheduled_end", session.scheduled_end)
    if new_end <= new_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Scheduled end time must be after scheduled start time",
        )

    for field, value in update_dict.items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return session


def delete_study_session(db: Session, student_id: uuid.UUID, session_id: uuid.UUID) -> None:
    session = get_study_session_by_id(db, student_id, session_id)
    db.delete(session)
    db.commit()
