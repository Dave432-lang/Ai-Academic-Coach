"""Create academic_events table

Revision ID: 005_academic_events
Revises: 004_universities_and_courses
Create Date: 2026-08-22 00:00:04.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM

revision: str = '005_academic_events'
down_revision: Union[str, None] = '004_universities_and_courses'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    event_type_enum = ENUM("assignment", "quiz", "exam", "project", "presentation", "other", name="event_type", create_type=False)
    priority_level_enum = ENUM("low", "medium", "high", "critical", name="priority_level", create_type=False)
    academic_status_enum = ENUM("pending", "in_progress", "completed", "cancelled", "missed", name="academic_status", create_type=False)

    op.create_table(
        "academic_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_type", event_type_enum, nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("priority", priority_level_enum, nullable=False, server_default=sa.text("'medium'")),
        sa.Column("status", academic_status_enum, nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("academic_events")
