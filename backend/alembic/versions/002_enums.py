"""Create PostgreSQL enums

Revision ID: 002_enums
Revises: 001_initial_pgvector
Create Date: 2026-08-22 00:00:01.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_enums'
down_revision: Union[str, None] = '001_initial_pgvector'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ENUMS = [
    ("account_status", ("active", "suspended", "pending", "deleted")),
    ("enrollment_status", ("active", "completed", "dropped", "withdrawn")),
    ("event_type", ("assignment", "quiz", "exam", "project", "presentation", "other")),
    ("priority_level", ("low", "medium", "high", "critical")),
    ("academic_status", ("pending", "in_progress", "completed", "cancelled", "missed")),
    ("goal_status", ("active", "achieved", "paused", "cancelled")),
    ("material_processing_status", ("pending", "processing", "completed", "failed")),
    ("message_role", ("user", "assistant", "system")),
    ("memory_type", ("preference", "goal", "academic_context", "learning_pattern")),
    ("agent_type", ("coordinator", "planner", "study", "progress")),
    ("action_status", ("pending", "awaiting_approval", "approved", "rejected", "executing", "completed", "failed", "cancelled")),
    ("permission_mode", ("allow", "require_approval", "require_confirmation", "deny")),
    ("notification_status", ("scheduled", "sent", "read", "dismissed", "failed", "cancelled")),
]


def upgrade() -> None:
    for enum_name, values in ENUMS:
        sa.Enum(*values, name=enum_name).create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    for enum_name, values in reversed(ENUMS):
        sa.Enum(*values, name=enum_name).drop(op.get_bind(), checkfirst=True)
