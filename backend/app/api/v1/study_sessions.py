from typing import List, Optional
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.study_session import StudySessionCreate, StudySessionUpdate, StudySessionRead
from app.services.course_service import get_student_profile_by_user_id
from app.services.study_session_service import (
    create_study_session,
    list_study_sessions,
    get_study_session_by_id,
    update_study_session,
    delete_study_session,
)

router = APIRouter(prefix="/study-sessions", tags=["study-sessions"])


@router.post("", response_model=StudySessionRead, status_code=status.HTTP_201_CREATED)
def create_study_session_endpoint(
    payload: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return create_study_session(db, profile.id, payload)


@router.get("", response_model=List[StudySessionRead])
def list_study_sessions_endpoint(
    course_id: Optional[uuid.UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return list_study_sessions(
        db,
        profile.id,
        course_id=course_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{session_id}", response_model=StudySessionRead)
def get_study_session_endpoint(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return get_study_session_by_id(db, profile.id, session_id)


@router.patch("/{session_id}", response_model=StudySessionRead)
def update_study_session_endpoint(
    session_id: uuid.UUID,
    payload: StudySessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return update_study_session(db, profile.id, session_id, payload)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_session_endpoint(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    delete_study_session(db, profile.id, session_id)
