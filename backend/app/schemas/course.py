from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.database.models.enums import EnrollmentStatus


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    university_id: uuid.UUID
    course_code: str
    course_name: str
    description: Optional[str] = None
    credit_hours: Optional[int] = None
    created_at: datetime


class CourseEnrollmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    course_id: uuid.UUID
    academic_year: str
    semester: str
    status: EnrollmentStatus
    course: CourseRead
    created_at: datetime
