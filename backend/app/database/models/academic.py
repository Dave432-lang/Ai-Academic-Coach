import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    Integer,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Enum as SQLEnum,
    text,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base
from app.database.models.enums import (
    EventType,
    PriorityLevel,
    AcademicStatus,
    GoalStatus,
)

if TYPE_CHECKING:
    from app.database.models.user import StudentProfile
    from app.database.models.course import Course


class AcademicEvent(Base):
    __tablename__ = "academic_events"
    __table_args__ = (
        Index("idx_academic_events_student_due_at", "student_id", "due_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    event_type: Mapped[EventType] = mapped_column(
        SQLEnum(EventType, name="event_type", create_type=False),
        nullable=False,
    )
    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    priority: Mapped[PriorityLevel] = mapped_column(
        SQLEnum(PriorityLevel, name="priority_level", create_type=False),
        nullable=False,
        default=PriorityLevel.MEDIUM,
        server_default=text("'medium'"),
    )
    status: Mapped[AcademicStatus] = mapped_column(
        SQLEnum(AcademicStatus, name="academic_status", create_type=False),
        nullable=False,
        default=AcademicStatus.PENDING,
        server_default=text("'pending'"),
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

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="academic_events",
    )
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="academic_events",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="academic_event",
        cascade="all, delete-orphan",
    )


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("estimated_minutes IS NULL OR estimated_minutes > 0", name="ck_tasks_estimated_minutes_positive"),
        Index("idx_tasks_student_status", "student_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    academic_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_events.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    estimated_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    priority: Mapped[PriorityLevel] = mapped_column(
        SQLEnum(PriorityLevel, name="priority_level", create_type=False),
        nullable=False,
        default=PriorityLevel.MEDIUM,
        server_default=text("'medium'"),
    )
    status: Mapped[AcademicStatus] = mapped_column(
        SQLEnum(AcademicStatus, name="academic_status", create_type=False),
        nullable=False,
        default=AcademicStatus.PENDING,
        server_default=text("'pending'"),
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("'0'"),
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

    academic_event: Mapped[Optional["AcademicEvent"]] = relationship(
        "AcademicEvent",
        back_populates="tasks",
    )
    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="tasks",
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(
        "StudySession",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class StudySession(Base):
    __tablename__ = "study_sessions"
    __table_args__ = (
        CheckConstraint("scheduled_end > scheduled_start", name="ck_study_sessions_scheduled_end_after_start"),
        CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100", name="ck_study_sessions_completion_percentage_range"),
        CheckConstraint("actual_minutes IS NULL OR actual_minutes >= 0", name="ck_study_sessions_actual_minutes_non_negative"),
        Index("idx_study_sessions_student_scheduled_start", "student_id", "scheduled_start"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    scheduled_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[AcademicStatus] = mapped_column(
        SQLEnum(AcademicStatus, name="academic_status", create_type=False),
        nullable=False,
        default=AcademicStatus.PENDING,
        server_default=text("'pending'"),
    )
    completion_percentage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("'0'"),
    )
    actual_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
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

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="study_sessions",
    )
    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="study_sessions",
    )


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        Index("idx_goals_student_status", "student_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    target_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    current_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    target_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    status: Mapped[GoalStatus] = mapped_column(
        SQLEnum(GoalStatus, name="goal_status", create_type=False),
        nullable=False,
        default=GoalStatus.ACTIVE,
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

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="goals",
    )
    course: Mapped[Optional["Course"]] = relationship(
        "Course",
        back_populates="goals",
    )


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint("score >= 0", name="ck_grades_score_non_negative"),
        CheckConstraint("max_score > 0", name="ck_grades_max_score_positive"),
        CheckConstraint("score <= max_score", name="ck_grades_score_lte_max_score"),
        Index("idx_grades_student_course", "student_id", "course_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    assessment_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    assessment_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    score: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    graded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
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

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="grades",
    )
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="grades",
    )
