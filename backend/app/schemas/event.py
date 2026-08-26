from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.database.models.enums import EventType, PriorityLevel, AcademicStatus


class EventCreate(BaseModel):
    course_id: uuid.UUID
    event_type: EventType
    title: str = Field(..., min_length=1, max_length=255)
    due_at: datetime
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = PriorityLevel.MEDIUM
    status: Optional[AcademicStatus] = AcademicStatus.PENDING


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    event_type: Optional[EventType] = None
    due_at: Optional[datetime] = None
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[AcademicStatus] = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    course_id: uuid.UUID
    title: str
    description: Optional[str] = None
    event_type: EventType
    due_at: datetime
    priority: PriorityLevel
    status: AcademicStatus
    created_at: datetime
    updated_at: datetime
