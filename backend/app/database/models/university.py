import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, UniqueConstraint, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base

if TYPE_CHECKING:
    from app.database.models.user import StudentProfile
    from app.database.models.course import Course


class University(Base):
    __tablename__ = "universities"
    __table_args__ = (
        UniqueConstraint("name", "country", name="uq_universities_name_country"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    website: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    timezone: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    student_profiles: Mapped[list["StudentProfile"]] = relationship(
        "StudentProfile",
        back_populates="university",
    )
    courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="university",
        cascade="all, delete-orphan",
    )
