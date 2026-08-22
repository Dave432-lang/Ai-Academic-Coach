import uuid
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Enum as SQLEnum,
    text,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base
from app.database.models.enums import PermissionMode, AgentType, ActionStatus

if TYPE_CHECKING:
    from app.database.models.user import StudentProfile


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("student_id", "action_type", name="uq_permissions_student_action_type"),
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
    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    permission_mode: Mapped[PermissionMode] = mapped_column(
        SQLEnum(PermissionMode, name="permission_mode", create_type=False),
        nullable=False,
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
        back_populates="permissions",
    )


class AgentAction(Base):
    __tablename__ = "agent_actions"
    __table_args__ = (
        Index("idx_agent_actions_student_created_at", "student_id", "created_at"),
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
    agent_type: Mapped[AgentType] = mapped_column(
        SQLEnum(AgentType, name="agent_type", create_type=False),
        nullable=False,
    )
    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    request_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    result_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )
    status: Mapped[ActionStatus] = mapped_column(
        SQLEnum(ActionStatus, name="action_status", create_type=False),
        nullable=False,
        default=ActionStatus.PENDING,
        server_default=text("'pending'"),
    )
    requires_approval: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="agent_actions",
    )
