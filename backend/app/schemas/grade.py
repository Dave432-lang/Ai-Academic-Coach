from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class GradeCreate(BaseModel):
    course_id: uuid.UUID
    assessment_name: str = Field(..., min_length=1, max_length=255)
    score: Decimal = Field(..., ge=0)
    max_score: Decimal = Field(..., gt=0)
    assessment_type: Optional[str] = Field(None, max_length=100)
    graded_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_score_lte_max_score(self):
        if self.score > self.max_score:
            raise ValueError("Score cannot exceed max score")
        return self


class GradeUpdate(BaseModel):
    assessment_name: Optional[str] = Field(None, min_length=1, max_length=255)
    score: Optional[Decimal] = Field(None, ge=0)
    max_score: Optional[Decimal] = Field(None, gt=0)
    assessment_type: Optional[str] = Field(None, max_length=100)
    graded_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_score_lte_max_score(self):
        if self.score is not None and self.max_score is not None:
            if self.score > self.max_score:
                raise ValueError("Score cannot exceed max score")
        return self


class GradeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    course_id: uuid.UUID
    assessment_name: str
    assessment_type: Optional[str] = None
    score: Decimal
    max_score: Decimal
    percentage: Optional[float] = None
    graded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def calculate_percentage(self):
        if self.max_score and self.max_score > 0:
            self.percentage = round(float(self.score / self.max_score) * 100, 2)
        return self
