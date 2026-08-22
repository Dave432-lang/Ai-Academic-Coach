"""Create required indexes, partial indexes, vector HNSW index, and updated_at triggers

Revision ID: 012_indexes_and_updated_at
Revises: 011_notifications
Create Date: 2026-08-22 00:00:11.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '012_indexes_and_updated_at'
down_revision: Union[str, None] = '011_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEXES = [
    ("idx_student_profiles_university_id", "student_profiles", ["university_id"], False, None),
    ("idx_course_enrollments_student_id", "course_enrollments", ["student_id"], False, None),
    ("idx_course_enrollments_course_id", "course_enrollments", ["course_id"], False, None),
    ("idx_academic_events_student_due_at", "academic_events", ["student_id", "due_at"], False, None),
    ("idx_academic_events_course_id", "academic_events", ["course_id"], False, None),
    ("idx_tasks_student_status", "tasks", ["student_id", "status"], False, None),
    ("idx_study_sessions_student_scheduled_start", "study_sessions", ["student_id", "scheduled_start"], False, None),
    ("idx_study_sessions_task_id", "study_sessions", ["task_id"], False, None),
    ("idx_goals_student_status", "goals", ["student_id", "status"], False, None),
    ("idx_grades_student_course", "grades", ["student_id", "course_id"], False, None),
    ("idx_course_materials_student_course", "course_materials", ["student_id", "course_id"], False, None),
    ("idx_messages_conversation_created_at", "messages", ["conversation_id", "created_at"], False, None),
    ("idx_memories_student_is_active", "memories", ["student_id", "is_active"], False, None),
    ("idx_agent_actions_student_created_at", "agent_actions", ["student_id", "created_at"], False, None),
    ("idx_notifications_student_status", "notifications", ["student_id", "status"], False, None),
    ("idx_notifications_scheduled_for", "notifications", ["scheduled_for"], False, "status = 'scheduled'"),
]

UPDATED_AT_TABLES = [
    "users",
    "universities",
    "student_profiles",
    "courses",
    "course_enrollments",
    "academic_events",
    "tasks",
    "study_sessions",
    "goals",
    "grades",
    "course_materials",
    "conversations",
    "memories",
    "permissions",
]


def upgrade() -> None:
    # 1. Create standard & partial indexes
    for name, table, columns, unique, where in INDEXES:
        op.create_index(
            name,
            table,
            columns,
            unique=unique,
            postgresql_where=sa.text(where) if where else None,
        )

    # 2. Create HNSW Vector Index on document_chunks(embedding)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
    )

    # 3. Create update_updated_at_column PL/pgSQL function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 4. Attach trigger to all tables with updated_at
    for table_name in UPDATED_AT_TABLES:
        trigger_name = f"trg_{table_name}_updated_at"
        op.execute(
            f"""
            CREATE TRIGGER {trigger_name}
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            """
        )


def downgrade() -> None:
    # 1. Drop triggers
    for table_name in reversed(UPDATED_AT_TABLES):
        trigger_name = f"trg_{table_name}_updated_at"
        op.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};")

    # 2. Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # 3. Drop HNSW vector index
    op.execute("DROP INDEX IF EXISTS idx_document_chunks_embedding_hnsw;")

    # 4. Drop standard & partial indexes
    for name, table, _, _, _ in reversed(INDEXES):
        op.drop_index(name, table_name=table)
