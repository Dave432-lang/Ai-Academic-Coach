"""Create users and student_profiles tables

Revision ID: 003_users_and_profiles
Revises: 002_enums
Create Date: 2026-08-22 00:00:02.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '003_users_and_profiles'
down_revision: Union[str, None] = '002_enums'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    account_status_enum = sa.Enum("active", "suspended", "pending", "deleted", name="account_status", create_type=False)

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("account_status", account_status_enum, nullable=False, server_default=sa.text("'active'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "student_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("university_id", UUID(as_uuid=True), nullable=True),
        sa.Column("program", sa.String(200), nullable=True),
        sa.Column("level", sa.String(50), nullable=True),
        sa.Column("semester", sa.String(50), nullable=True),
        sa.Column("academic_year", sa.String(20), nullable=True),
        sa.Column("timezone", sa.String(100), nullable=False, server_default=sa.text("'UTC'")),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("student_profiles")
    op.drop_table("users")
