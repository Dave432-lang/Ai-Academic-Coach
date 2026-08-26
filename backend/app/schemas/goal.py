from typing import Optional
import uuid
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.database.models.enums import GoalStatus


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: Optional[uuid.UUID] = None
    target_value: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    target_date: Optional[date] = None
    status: Optional[GoalStatus] = GoalStatus.ACTIVE


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: Optional[uuid.UUID] = None
    target_value: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    target_date: Optional[date] = None
    status: Optional[GoalStatus] = None


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    course_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    target_value: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    target_date: Optional[date] = None
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
