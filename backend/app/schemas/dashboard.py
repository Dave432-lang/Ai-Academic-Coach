from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict
from app.schemas.grade import GradeRead


class DashboardSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_name: str
    onboarding_completed: bool
    enrolled_courses_count: int
    upcoming_events_count: int
    active_tasks_count: int
    study_sessions_this_week_count: int
    recent_grades: List[GradeRead]
