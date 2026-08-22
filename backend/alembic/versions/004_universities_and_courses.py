"""Create universities and courses tables

Revision ID: 004_universities_and_courses
Revises: 003_users_and_profiles
Create Date: 2026-08-22 00:00:03.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '004_universities_and_courses'
down_revision: Union[str, None] = '003_users_and_profiles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    enrollment_status_enum = sa.Enum("active", "completed", "dropped", "withdrawn", name="enrollment_status", create_type=False)

    op.create_table(
        "universities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("website", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", "country", name="uq_universities_name_country"),
    )

    op.create_foreign_key(
        "fk_student_profiles_university_id",
        "student_profiles",
        "universities",
        ["university_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "courses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("university_id", UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_code", sa.String(50), nullable=False),
        sa.Column("course_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("credit_hours", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("university_id", "course_code", name="uq_courses_university_course_code"),
        sa.CheckConstraint("credit_hours IS NULL OR credit_hours > 0", name="ck_courses_credit_hours_positive"),
    )

    op.create_table(
        "course_enrollments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("academic_year", sa.String(20), nullable=False),
        sa.Column("semester", sa.String(50), nullable=False),
        sa.Column("status", enrollment_status_enum, nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "course_id", "academic_year", "semester", name="uq_course_enrollments_student_course_term"),
    )


def downgrade() -> None:
    op.drop_table("course_enrollments")
    op.drop_table("courses")
    op.drop_constraint("fk_student_profiles_university_id", "student_profiles", type_="foreignkey")
    op.drop_table("universities")
