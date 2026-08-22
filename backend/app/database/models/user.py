import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base
from app.database.models.enums import AccountStatus

if TYPE_CHECKING:
    from app.database.models.university import University
    from app.database.models.course import CourseEnrollment
    from app.database.models.academic import AcademicEvent, Task, StudySession, Goal, Grade
    from app.database.models.material import CourseMaterial
    from app.database.models.conversation import Conversation
    from app.database.models.memory import Memory
    from app.database.models.permission import Permission, AgentAction
    from app.database.models.notification import Notification


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    account_status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus, name="account_status", create_type=False),
        nullable=False,
        default=AccountStatus.ACTIVE,
        server_default=text("'active'"),
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
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    profile: Mapped[Optional["StudentProfile"]] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    university_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("universities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    program: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    level: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    semester: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    academic_year: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="UTC",
        server_default=text("'UTC'"),
    )
    country: Mapped[Optional[str]] = mapped_column(
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

    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
    )
    university: Mapped[Optional["University"]] = relationship(
        "University",
        back_populates="student_profiles",
    )
    enrollments: Mapped[list["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    academic_events: Mapped[list["AcademicEvent"]] = relationship(
        "AcademicEvent",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(
        "StudySession",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    goals: Mapped[list["Goal"]] = relationship(
        "Goal",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    grades: Mapped[list["Grade"]] = relationship(
        "Grade",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    course_materials: Mapped[list["CourseMaterial"]] = relationship(
        "CourseMaterial",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    memories: Mapped[list["Memory"]] = relationship(
        "Memory",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    agent_actions: Mapped[list["AgentAction"]] = relationship(
        "AgentAction",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="student",
        cascade="all, delete-orphan",
    )
