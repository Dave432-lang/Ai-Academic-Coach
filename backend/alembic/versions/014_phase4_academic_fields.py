"""Add Phase 4 academic management fields to tasks and study_sessions

Revision ID: 014_phase4_academic_fields
Revises: 013_onboarding_fields
Create Date: 2026-08-25 01:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '014_phase4_academic_fields'
down_revision: Union[str, None] = '013_onboarding_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add course_id and due_date to tasks
    op.add_column('tasks', sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_tasks_course_id', 'tasks', 'courses', ['course_id'], ['id'], ondelete='CASCADE')
    op.create_index('idx_tasks_course_id', 'tasks', ['course_id'])

    # Add course_id, topic, notes to study_sessions, and make task_id nullable
    op.add_column('study_sessions', sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('study_sessions', sa.Column('topic', sa.String(255), nullable=True))
    op.add_column('study_sessions', sa.Column('notes', sa.Text(), nullable=True))
    op.create_foreign_key('fk_study_sessions_course_id', 'study_sessions', 'courses', ['course_id'], ['id'], ondelete='CASCADE')
    op.alter_column('study_sessions', 'task_id', existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.create_index('idx_study_sessions_course_id', 'study_sessions', ['course_id'])


def downgrade() -> None:
    op.drop_index('idx_study_sessions_course_id', table_name='study_sessions')
    op.drop_constraint('fk_study_sessions_course_id', 'study_sessions', type_='foreignkey')
    op.execute("DELETE FROM study_sessions WHERE task_id IS NULL")
    op.alter_column('study_sessions', 'task_id', existing_type=postgresql.UUID(as_uuid=True), nullable=False)
    op.drop_column('study_sessions', 'notes')
    op.drop_column('study_sessions', 'topic')
    op.drop_column('study_sessions', 'course_id')

    op.drop_index('idx_tasks_course_id', table_name='tasks')
    op.drop_constraint('fk_tasks_course_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'course_id')
