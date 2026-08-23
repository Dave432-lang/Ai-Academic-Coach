import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Enum as SQLEnum,
    text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base
from app.database.models.enums import EnrollmentStatus

if TYPE_CHECKING:
    from app.database.models.university import University
    from app.database.models.user import StudentProfile
    from app.database.models.academic import AcademicEvent, Goal, Grade
    from app.database.models.material import CourseMaterial


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("university_id", "course_code", name="uq_courses_university_course_code"),
        CheckConstraint("credit_hours IS NULL OR credit_hours > 0", name="ck_courses_credit_hours_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    university_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    course_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    credit_hours: Mapped[Optional[int]] = mapped_column(
        Integer,
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

    university: Mapped["University"] = relationship(
        "University",
        back_populates="courses",
    )
    enrollments: Mapped[list["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    academic_events: Mapped[list["AcademicEvent"]] = relationship(
        "AcademicEvent",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    goals: Mapped[list["Goal"]] = relationship(
        "Goal",
        back_populates="course",
    )
    grades: Mapped[list["Grade"]] = relationship(
        "Grade",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    course_materials: Mapped[list["CourseMaterial"]] = relationship(
        "CourseMaterial",
        back_populates="course",
        cascade="all, delete-orphan",
    )


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            "academic_year",
            "semester",
            name="uq_course_enrollments_student_course_term",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    academic_year: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    semester: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        SQLEnum(EnrollmentStatus, name="enrollment_status", create_type=False),
        nullable=False,
        default=EnrollmentStatus.ACTIVE,
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
        back_populates="enrollments",
    )
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="enrollments",
    )
