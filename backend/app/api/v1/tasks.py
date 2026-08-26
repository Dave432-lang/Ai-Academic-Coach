from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.services.course_service import get_student_profile_by_user_id
from app.services.task_service import (
    create_task,
    list_tasks,
    get_task_by_id,
    update_task,
    delete_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return create_task(db, profile.id, payload)


@router.get("", response_model=List[TaskRead])
def list_tasks_endpoint(
    status_filter: Optional[str] = Query(None, alias="status"),
    course_id: Optional[uuid.UUID] = Query(None),
    event_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return list_tasks(
        db,
        profile.id,
        status_filter=status_filter,
        course_id=course_id,
        event_id=event_id,
    )


@router.get("/{task_id}", response_model=TaskRead)
def get_task_endpoint(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return get_task_by_id(db, profile.id, task_id)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    return update_task(db, profile.id, task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_student_profile_by_user_id(db, current_user.id)
    delete_task(db, profile.id, task_id)
