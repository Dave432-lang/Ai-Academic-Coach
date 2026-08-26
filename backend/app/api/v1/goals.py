from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.goal import GoalCreate, GoalUpdate, GoalRead
from app.services.course_service import get_student_profile_by_user_id
from app.services.goal_service import (
    create_goal,
    list_goals,
    get_goal_by_id,
    update_goal,
    delete_goal,
)

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal_endpoint(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return create_goal(db, profile.id, payload)


@router.get("", response_model=List[GoalRead])
def list_goals_endpoint(
    status_filter: Optional[str] = Query(None, alias="status"),
    course_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return list_goals(db, profile.id, status_filter=status_filter, course_id=course_id)


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal_endpoint(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return get_goal_by_id(db, profile.id, goal_id)


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal_endpoint(
    goal_id: uuid.UUID,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return update_goal(db, profile.id, goal_id, payload)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal_endpoint(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    delete_goal(db, profile.id, goal_id)
