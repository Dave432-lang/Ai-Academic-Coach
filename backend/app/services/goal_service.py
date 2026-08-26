from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import Goal
from app.schemas.goal import GoalCreate, GoalUpdate
from app.services.course_service import verify_course_enrollment


def create_goal(db: Session, student_id: uuid.UUID, data: GoalCreate) -> Goal:
    if data.course_id:
        verify_course_enrollment(db, student_id=student_id, course_id=data.course_id)

    goal = Goal(
        student_id=student_id,
        course_id=data.course_id,
        title=data.title,
        description=data.description,
        target_value=data.target_value,
        current_value=data.current_value,
        target_date=data.target_date,
        status=data.status,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def list_goals(
    db: Session,
    student_id: uuid.UUID,
    status_filter: Optional[str] = None,
    course_id: Optional[uuid.UUID] = None,
) -> List[Goal]:
    query = db.query(Goal).filter(Goal.student_id == student_id)
    if status_filter:
        query = query.filter(Goal.status == status_filter)
    if course_id:
        query = query.filter(Goal.course_id == course_id)
    return query.order_by(Goal.created_at.desc()).all()


def get_goal_by_id(db: Session, student_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    if goal.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this goal",
        )
    return goal


def update_goal(
    db: Session,
    student_id: uuid.UUID,
    goal_id: uuid.UUID,
    data: GoalUpdate,
) -> Goal:
    goal = get_goal_by_id(db, student_id, goal_id)
    update_dict = data.model_dump(exclude_unset=True)

    if "course_id" in update_dict and update_dict["course_id"] is not None:
        verify_course_enrollment(db, student_id=student_id, course_id=update_dict["course_id"])

    for field, value in update_dict.items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, student_id: uuid.UUID, goal_id: uuid.UUID) -> None:
    goal = get_goal_by_id(db, student_id, goal_id)
    db.delete(goal)
    db.commit()
