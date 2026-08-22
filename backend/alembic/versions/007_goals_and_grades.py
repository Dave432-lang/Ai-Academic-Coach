"""Create goals and grades tables

Revision ID: 007_goals_and_grades
Revises: 006_tasks_and_study_sessions
Create Date: 2026-08-22 00:00:06.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '007_goals_and_grades'
down_revision: Union[str, None] = '006_tasks_and_study_sessions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    goal_status_enum = sa.Enum("active", "achieved", "paused", "cancelled", name="goal_status", create_type=False)

    op.create_table(
        "goals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_value", sa.Numeric(10, 2), nullable=True),
        sa.Column("current_value", sa.Numeric(10, 2), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", goal_status_enum, nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "grades",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assessment_name", sa.String(255), nullable=False),
        sa.Column("assessment_type", sa.String(100), nullable=True),
        sa.Column("score", sa.Numeric(10, 2), nullable=False),
        sa.Column("max_score", sa.Numeric(10, 2), nullable=False),
        sa.Column("graded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("score >= 0", name="ck_grades_score_non_negative"),
        sa.CheckConstraint("max_score > 0", name="ck_grades_max_score_positive"),
        sa.CheckConstraint("score <= max_score", name="ck_grades_score_lte_max_score"),
    )


def downgrade() -> None:
    op.drop_table("grades")
    op.drop_table("goals")
