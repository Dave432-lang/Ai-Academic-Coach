from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.orm import Session
from app.database.models import (
    StudentProfile,
    CourseEnrollment,
    AcademicEvent,
    Task,
    StudySession,
    Grade,
    AcademicStatus,
    EnrollmentStatus,
)
from app.schemas.dashboard import DashboardSummaryRead
from app.schemas.grade import GradeRead
from app.services.course_service import get_student_profile_by_user_id


def get_dashboard_summary(db: Session, user_id: uuid.UUID) -> DashboardSummaryRead:
    profile = get_student_profile_by_user_id(db, user_id)
    student_id = profile.id

    now = datetime.now(timezone.utc)
    seven_days_later = now + timedelta(days=7)
    start_of_week = now - timedelta(days=now.weekday())

    # 1. Enrolled courses count
    enrolled_courses_count = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE,
        )
        .count()
    )

    # 2. Upcoming events count (next 7 days)
    upcoming_events_count = (
        db.query(AcademicEvent)
        .filter(
            AcademicEvent.student_id == student_id,
            AcademicEvent.due_at >= now,
            AcademicEvent.due_at <= seven_days_later,
        )
        .count()
    )

    # 3. Active tasks count (status != COMPLETED)
    active_tasks_count = (
        db.query(Task)
        .filter(
            Task.student_id == student_id,
            Task.status != AcademicStatus.COMPLETED,
        )
        .count()
    )

    # 4. Study sessions this week count
    study_sessions_this_week_count = (
        db.query(StudySession)
        .filter(
            StudySession.student_id == student_id,
            StudySession.scheduled_start >= start_of_week,
        )
        .count()
    )

    # 5. Most recent 3 grades
    recent_grade_records = (
        db.query(Grade)
        .filter(Grade.student_id == student_id)
        .order_by(Grade.created_at.desc())
        .limit(3)
        .all()
    )

    recent_grades = [GradeRead.model_validate(g) for g in recent_grade_records]

    return DashboardSummaryRead(
        student_name=profile.full_name,
        onboarding_completed=profile.onboarding_completed,
        enrolled_courses_count=enrolled_courses_count,
        upcoming_events_count=upcoming_events_count,
        active_tasks_count=active_tasks_count,
        study_sessions_this_week_count=study_sessions_this_week_count,
        recent_grades=recent_grades,
    )
