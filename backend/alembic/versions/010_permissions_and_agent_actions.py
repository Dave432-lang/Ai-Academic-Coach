"""Create permissions and agent_actions tables

Revision ID: 010_permissions_and_agent_actions
Revises: 009_conversations_and_memory
Create Date: 2026-08-22 00:00:09.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM

revision: str = '010_permissions_and_agent_actions'
down_revision: Union[str, None] = '009_conversations_and_memory'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    permission_mode_enum = ENUM("allow", "require_approval", "require_confirmation", "deny", name="permission_mode", create_type=False)
    agent_type_enum = ENUM("coordinator", "planner", "study", "progress", name="agent_type", create_type=False)
    action_status_enum = ENUM("pending", "awaiting_approval", "approved", "rejected", "executing", "completed", "failed", "cancelled", name="action_status", create_type=False)

    op.create_table(
        "permissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("permission_mode", permission_mode_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "action_type", name="uq_permissions_student_action_type"),
    )

    op.create_table(
        "agent_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", UUID(as_uuid=True), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_type", agent_type_enum, nullable=False),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("request_data", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_data", JSONB, nullable=True),
        sa.Column("status", action_status_enum, nullable=False, server_default=sa.text("'pending'")),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("agent_actions")
    op.drop_table("permissions")
