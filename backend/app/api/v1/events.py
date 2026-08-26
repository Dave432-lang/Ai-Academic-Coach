from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.event import EventCreate, EventUpdate, EventRead
from app.services.course_service import get_student_profile_by_user_id
from app.services.event_service import (
    create_academic_event,
    list_academic_events,
    get_academic_event_by_id,
    update_academic_event,
    delete_academic_event,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event_endpoint(
    payload: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return create_academic_event(db, profile.id, payload)


@router.get("", response_model=List[EventRead])
def list_events_endpoint(
    course_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return list_academic_events(db, profile.id, course_id=course_id, status_filter=status_filter)


@router.get("/{event_id}", response_model=EventRead)
def get_event_endpoint(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return get_academic_event_by_id(db, profile.id, event_id)


@router.patch("/{event_id}", response_model=EventRead)
def update_event_endpoint(
    event_id: uuid.UUID,
    payload: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return update_academic_event(db, profile.id, event_id, payload)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_endpoint(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    delete_academic_event(db, profile.id, event_id)
