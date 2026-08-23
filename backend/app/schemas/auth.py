"""
Authentication Schemas.
Pydantic models for user registration, login, token responses, and user profile retrieval.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.database.models.enums import AccountStatus


class UserSignupRequest(BaseModel):
    email: EmailStr = Field(..., description="Student email address")
    password: str = Field(
        ...,
        min_length=8,
        description="User password (minimum 8 characters)",
    )


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Student email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: UUID
    email: str
    account_status: AccountStatus
    onboarding_completed: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserMeResponse(BaseModel):
    id: UUID
    email: str
    account_status: AccountStatus
    onboarding_completed: bool

    model_config = ConfigDict(from_attributes=True)
