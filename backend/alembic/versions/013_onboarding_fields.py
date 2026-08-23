"""Add onboarding completion fields to student_profiles

Revision ID: 013_onboarding_fields
Revises: 012_indexes_and_updated_at
Create Date: 2026-08-23 00:00:13.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '013_onboarding_fields'
down_revision: Union[str, None] = '012_indexes_and_updated_at'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'student_profiles',
        sa.Column('onboarding_completed', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    )
    op.add_column(
        'student_profiles',
        sa.Column('onboarding_completed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('student_profiles', 'onboarding_completed_at')
    op.drop_column('student_profiles', 'onboarding_completed')
