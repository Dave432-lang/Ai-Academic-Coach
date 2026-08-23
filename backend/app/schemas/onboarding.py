"""
Onboarding Schemas.
Pydantic schemas for university search/creation, student profile updates, course onboarding, and onboarding status.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.database.models.enums import EnrollmentStatus


class UniversitySearchResponse(BaseModel):
    id: UUID
    name: str
    country: str
    website: Optional[str] = None
    timezone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UniversityCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="University full name")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    website: Optional[str] = Field(default=None, description="Official website URL")
    timezone: Optional[str] = Field(default=None, description="University primary timezone")


class StudentProfileUpdateRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150, description="Student full name")
    country: Optional[str] = Field(default=None, max_length=100, description="Home/study country")
    timezone: str = Field(default="UTC", max_length=100, description="Student preferred timezone")
    university_id: Optional[UUID] = Field(default=None, description="Selected university ID")
    program: Optional[str] = Field(default=None, max_length=200, description="Degree programme / major")
    level: Optional[str] = Field(default=None, max_length=50, description="Academic level (e.g. Undergraduate, Masters)")
    academic_year: Optional[str] = Field(default=None, max_length=20, description="Academic year (e.g. 2026/2027)")
    semester: Optional[str] = Field(default=None, max_length=50, description="Current semester (e.g. Fall, Semester 1)")


class StudentProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    country: Optional[str] = None
    timezone: str = "UTC"
    university_id: Optional[UUID] = None
    university_name: Optional[str] = None
    program: Optional[str] = None
    level: Optional[str] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    onboarding_completed: bool = False
    onboarding_completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CourseAddRequest(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=50, description="Course code (e.g. CS101)")
    course_name: str = Field(..., min_length=1, max_length=255, description="Course title (e.g. Introduction to Computer Science)")
    description: Optional[str] = Field(default=None, description="Course description")
    credit_hours: Optional[int] = Field(default=None, gt=0, description="Credit hours / units")
    academic_year: Optional[str] = Field(default=None, max_length=20, description="Academic year (uses profile default if omitted)")
    semester: Optional[str] = Field(default=None, max_length=50, description="Semester (uses profile default if omitted)")


class CourseEnrollmentResponse(BaseModel):
    id: UUID
    course_id: UUID
    course_code: str
    course_name: str
    academic_year: str
    semester: str
    status: EnrollmentStatus

    model_config = ConfigDict(from_attributes=True)


class OnboardingStatusResponse(BaseModel):
    onboarding_completed: bool
    has_profile: bool
    has_university: bool
    has_academic_info: bool
    active_course_count: int
    missing_requirements: List[str]
