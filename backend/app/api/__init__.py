"""
API Router Package.
Assembles versioned API endpoints (/api/v1/auth, /api/v1/onboarding, /api/v1/universities) and health checks.
"""
from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.courses import router as courses_router
from app.api.v1.events import router as events_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.study_sessions import router as study_sessions_router
from app.api.v1.goals import router as goals_router
from app.api.v1.grades import router as grades_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.materials import router as materials_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(onboarding_router)
v1_router.include_router(courses_router)
v1_router.include_router(events_router)
v1_router.include_router(tasks_router)
v1_router.include_router(study_sessions_router)
v1_router.include_router(goals_router)
v1_router.include_router(grades_router)
v1_router.include_router(dashboard_router)
v1_router.include_router(materials_router)

api_router = APIRouter()
api_router.include_router(v1_router)
api_router.include_router(health_router)

__all__ = ["api_router"]
