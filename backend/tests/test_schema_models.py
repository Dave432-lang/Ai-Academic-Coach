"""
Unit tests for SQLAlchemy ORM models, metadata declarations, constraints, and Alembic migration revision graph integrity.
Runs entirely offline without requiring a live PostgreSQL database connection.
"""
import sys
from pathlib import Path

# Ensure backend directory is in sys.path for IDEs and test runners
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import UniqueConstraint, CheckConstraint

try:
    from app.database.models import (
        Base,
        User,
        StudentProfile,
        University,
        Course,
        CourseEnrollment,
        AcademicEvent,
        Task,
        StudySession,
        Goal,
        Grade,
        CourseMaterial,
        DocumentChunk,
        Conversation,
        Message,
        Memory,
        Permission,
        AgentAction,
        Notification,
        AccountStatus,
        EnrollmentStatus,
        EventType,
        PriorityLevel,
        AcademicStatus,
        GoalStatus,
        MaterialProcessingStatus,
        MessageRole,
        MemoryType,
        AgentType,
        ActionStatus,
        PermissionMode,
        NotificationStatus,
    )
except ImportError:
    from backend.app.database.models import (  # type: ignore
        Base,
        User,
        StudentProfile,
        University,
        Course,
        CourseEnrollment,
        AcademicEvent,
        Task,
        StudySession,
        Goal,
        Grade,
        CourseMaterial,
        DocumentChunk,
        Conversation,
        Message,
        Memory,
        Permission,
        AgentAction,
        Notification,
        AccountStatus,
        EnrollmentStatus,
        EventType,
        PriorityLevel,
        AcademicStatus,
        GoalStatus,
        MaterialProcessingStatus,
        MessageRole,
        MemoryType,
        AgentType,
        ActionStatus,
        PermissionMode,
        NotificationStatus,
    )


def test_all_18_model_classes_and_tables():
    """
    Verify all 18 database model classes are correctly mapped to their respective table names.
    """
    model_table_map = {
        User: "users",
        University: "universities",
        StudentProfile: "student_profiles",
        Course: "courses",
        CourseEnrollment: "course_enrollments",
        AcademicEvent: "academic_events",
        Task: "tasks",
        StudySession: "study_sessions",
        Goal: "goals",
        Grade: "grades",
        CourseMaterial: "course_materials",
        DocumentChunk: "document_chunks",
        Conversation: "conversations",
        Message: "messages",
        Memory: "memories",
        Permission: "permissions",
        AgentAction: "agent_actions",
        Notification: "notifications",
    }

    for model_cls, table_name in model_table_map.items():
        assert model_cls.__tablename__ == table_name

    registered_tables = set(Base.metadata.tables.keys())
    expected_tables = set(model_table_map.values())
    assert expected_tables.issubset(registered_tables), f"Missing tables: {expected_tables - registered_tables}"


def test_enum_definitions():
    """
    Verify all 13 Python Enum classes match specified string values.
    """
    assert AccountStatus.ACTIVE.value == "active"
    assert EnrollmentStatus.COMPLETED.value == "completed"
    assert EventType.ASSIGNMENT.value == "assignment"
    assert PriorityLevel.CRITICAL.value == "critical"
    assert AcademicStatus.IN_PROGRESS.value == "in_progress"
    assert GoalStatus.ACHIEVED.value == "achieved"
    assert MaterialProcessingStatus.PENDING.value == "pending"
    assert MessageRole.ASSISTANT.value == "assistant"
    assert MemoryType.LEARNING_PATTERN.value == "learning_pattern"
    assert AgentType.COORDINATOR.value == "coordinator"
    assert ActionStatus.AWAITING_APPROVAL.value == "awaiting_approval"
    assert PermissionMode.REQUIRE_CONFIRMATION.value == "require_confirmation"
    assert NotificationStatus.SCHEDULED.value == "scheduled"


def test_table_constraints_and_indexes_declarations():
    """
    Verify table-level unique constraints, check constraints, and indexes.
    """
    # 1. Universities unique(name, country)
    univ_table = Base.metadata.tables["universities"]
    unique_names = {c.name for c in univ_table.constraints if isinstance(c, UniqueConstraint)}
    assert "uq_universities_name_country" in unique_names

    # 2. Courses constraints
    courses_table = Base.metadata.tables["courses"]
    course_uniques = {c.name for c in courses_table.constraints if isinstance(c, UniqueConstraint)}
    course_checks = {c.name for c in courses_table.constraints if isinstance(c, CheckConstraint)}
    assert "uq_courses_university_course_code" in course_uniques
    assert "ck_courses_credit_hours_positive" in course_checks

    # 3. Course Enrollments unique
    enroll_table = Base.metadata.tables["course_enrollments"]
    enroll_uniques = {c.name for c in enroll_table.constraints if isinstance(c, UniqueConstraint)}
    assert "uq_course_enrollments_student_course_term" in enroll_uniques

    # 4. Tasks check
    tasks_table = Base.metadata.tables["tasks"]
    task_checks = {c.name for c in tasks_table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_tasks_estimated_minutes_positive" in task_checks

    # 5. Study Sessions check
    study_table = Base.metadata.tables["study_sessions"]
    study_checks = {c.name for c in study_table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_study_sessions_scheduled_end_after_start" in study_checks
    assert "ck_study_sessions_completion_percentage_range" in study_checks
    assert "ck_study_sessions_actual_minutes_non_negative" in study_checks

    # 6. Grades check
    grades_table = Base.metadata.tables["grades"]
    grade_checks = {c.name for c in grades_table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_grades_score_non_negative" in grade_checks
    assert "ck_grades_max_score_positive" in grade_checks
    assert "ck_grades_score_lte_max_score" in grade_checks

    # 7. Document Chunks unique(material_id, chunk_index)
    chunks_table = Base.metadata.tables["document_chunks"]
    chunk_uniques = {c.name for c in chunks_table.constraints if isinstance(c, UniqueConstraint)}
    assert "uq_document_chunks_material_chunk_index" in chunk_uniques


def test_alembic_revision_graph_integrity():
    """
    Verify Alembic migration revision sequence from 001 to 012 without broken links.
    """
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    alembic_cfg = Config(str(backend_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    script = ScriptDirectory.from_config(alembic_cfg)

    revisions = list(script.walk_revisions())
    rev_ids = [r.revision for r in reversed(revisions)]
    expected_sequence = [
        "001_initial_pgvector",
        "002_enums",
        "003_users_and_profiles",
        "004_universities_and_courses",
        "005_academic_events",
        "006_tasks_and_study_sessions",
        "007_goals_and_grades",
        "008_materials_and_rag_preparation",
        "009_conversations_and_memory",
        "010_permissions_and_agent_actions",
        "011_notifications",
        "012_indexes_and_updated_at",
        "013_onboarding_fields",
    ]
    assert rev_ids == expected_sequence, f"Revision sequence mismatch: {rev_ids}"
