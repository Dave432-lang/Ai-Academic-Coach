"""Create tasks and study_sessions tables

Revision ID: 006_tasks_and_study_sessions
Revises: 005_academic_events
Create Date: 2026-08-22 00:00:05.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM

revision: str = '006_tasks_and_study_sessions'
down_revision: Union[str, None] = '005_academic_events'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    priority_level_enum = ENUM("low", "medium", "high", "critical", name="priority_level", create_type=False)
    academic_status_enum = ENUM("pending", "in_progress", "completed", "cancelled", "missed", name="academic_status", create_type=False)

    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("academic_event_id", UUID(as_uuid=True), sa.ForeignKey("academic_events.id", ondelete="CASCADE"), nullable=True),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("priority", priority_level_enum, nullable=False, server_default=sa.text("'medium'")),
        sa.Column("status", academic_status_enum, nullable=False, server_default=sa.text("'pending'")),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("estimated_minutes IS NULL OR estimated_minutes > 0", name="ck_tasks_estimated_minutes_positive"),
    )

    op.create_table(
        "study_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", academic_status_enum, nullable=False, server_default=sa.text("'pending'")),
        sa.Column("completion_percentage", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("actual_minutes", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("scheduled_end > scheduled_start", name="ck_study_sessions_scheduled_end_after_start"),
        sa.CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100", name="ck_study_sessions_completion_percentage_range"),
        sa.CheckConstraint("actual_minutes IS NULL OR actual_minutes >= 0", name="ck_study_sessions_actual_minutes_non_negative"),
    )


def downgrade() -> None:
    op.drop_table("study_sessions")
    op.drop_table("tasks")
