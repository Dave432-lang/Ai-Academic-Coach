from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.database.models.enums import AcademicStatus


class StudySessionCreate(BaseModel):
    course_id: Optional[uuid.UUID] = None
    task_id: Optional[uuid.UUID] = None
    scheduled_start: datetime
    scheduled_end: datetime
    topic: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    status: Optional[AcademicStatus] = AcademicStatus.PENDING


class StudySessionUpdate(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: Optional[AcademicStatus] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    actual_minutes: Optional[int] = Field(None, ge=0)
    completed_at: Optional[datetime] = None
    topic: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class StudySessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    course_id: Optional[uuid.UUID] = None
    task_id: Optional[uuid.UUID] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    scheduled_start: datetime
    scheduled_end: datetime
    status: AcademicStatus
    completion_percentage: int
    actual_minutes: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
