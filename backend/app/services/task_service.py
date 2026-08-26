from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import Task, AcademicEvent
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.course_service import verify_course_enrollment


def create_task(db: Session, student_id: uuid.UUID, data: TaskCreate) -> Task:
    if data.course_id:
        verify_course_enrollment(db, student_id=student_id, course_id=data.course_id)
    if data.academic_event_id:
        event = db.query(AcademicEvent).filter(AcademicEvent.id == data.academic_event_id).first()
        if not event or event.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Academic event not found or access denied",
            )

    task = Task(
        student_id=student_id,
        course_id=data.course_id,
        academic_event_id=data.academic_event_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        status=data.status,
        estimated_minutes=data.estimated_minutes,
        due_date=data.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    student_id: uuid.UUID,
    status_filter: Optional[str] = None,
    course_id: Optional[uuid.UUID] = None,
    event_id: Optional[uuid.UUID] = None,
) -> List[Task]:
    query = db.query(Task).filter(Task.student_id == student_id)
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if course_id:
        query = query.filter(Task.course_id == course_id)
    if event_id:
        query = query.filter(Task.academic_event_id == event_id)
    return query.order_by(Task.order_index.asc(), Task.created_at.desc()).all()


def get_task_by_id(db: Session, student_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if task.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this task",
        )
    return task


def update_task(
    db: Session,
    student_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
) -> Task:
    task = get_task_by_id(db, student_id, task_id)
    update_dict = data.model_dump(exclude_unset=True)

    if "course_id" in update_dict and update_dict["course_id"] is not None:
        verify_course_enrollment(db, student_id=student_id, course_id=update_dict["course_id"])
    if "academic_event_id" in update_dict and update_dict["academic_event_id"] is not None:
        event = db.query(AcademicEvent).filter(AcademicEvent.id == update_dict["academic_event_id"]).first()
        if not event or event.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Academic event not found or access denied",
            )

    for field, value in update_dict.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, student_id: uuid.UUID, task_id: uuid.UUID) -> None:
    task = get_task_by_id(db, student_id, task_id)
    db.delete(task)
    db.commit()
