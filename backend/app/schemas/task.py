from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.database.models.enums import PriorityLevel, AcademicStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = PriorityLevel.MEDIUM
    status: Optional[AcademicStatus] = AcademicStatus.PENDING
    estimated_minutes: Optional[int] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    course_id: Optional[uuid.UUID] = None
    academic_event_id: Optional[uuid.UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[AcademicStatus] = None
    estimated_minutes: Optional[int] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    course_id: Optional[uuid.UUID] = None
    academic_event_id: Optional[uuid.UUID] = None
    order_index: Optional[int] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    course_id: Optional[uuid.UUID] = None
    academic_event_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    estimated_minutes: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: PriorityLevel
    status: AcademicStatus
    order_index: int
    created_at: datetime
    updated_at: datetime
