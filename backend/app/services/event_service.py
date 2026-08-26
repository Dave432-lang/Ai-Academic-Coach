from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import AcademicEvent
from app.schemas.event import EventCreate, EventUpdate
from app.services.course_service import verify_course_enrollment


def create_academic_event(db: Session, student_id: uuid.UUID, data: EventCreate) -> AcademicEvent:
    verify_course_enrollment(db, student_id=student_id, course_id=data.course_id)
    event = AcademicEvent(
        student_id=student_id,
        course_id=data.course_id,
        title=data.title,
        description=data.description,
        event_type=data.event_type,
        due_at=data.due_at,
        priority=data.priority,
        status=data.status,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_academic_events(
    db: Session,
    student_id: uuid.UUID,
    course_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
) -> List[AcademicEvent]:
    query = db.query(AcademicEvent).filter(AcademicEvent.student_id == student_id)
    if course_id:
        query = query.filter(AcademicEvent.course_id == course_id)
    if status_filter:
        query = query.filter(AcademicEvent.status == status_filter)
    return query.order_by(AcademicEvent.due_at.asc()).all()


def get_academic_event_by_id(db: Session, student_id: uuid.UUID, event_id: uuid.UUID) -> AcademicEvent:
    event = db.query(AcademicEvent).filter(AcademicEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic event not found",
        )
    if event.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this academic event",
        )
    return event


def update_academic_event(
    db: Session,
    student_id: uuid.UUID,
    event_id: uuid.UUID,
    data: EventUpdate,
) -> AcademicEvent:
    event = get_academic_event_by_id(db, student_id, event_id)
    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete_academic_event(db: Session, student_id: uuid.UUID, event_id: uuid.UUID) -> None:
    event = get_academic_event_by_id(db, student_id, event_id)
    db.delete(event)
    db.commit()
