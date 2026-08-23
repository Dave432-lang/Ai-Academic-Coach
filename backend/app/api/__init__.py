"""
API Router Package.
Assembles versioned API endpoints (/api/v1/auth, /api/v1/onboarding, /api/v1/universities) and health checks.
"""
from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.onboarding import router as onboarding_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(onboarding_router)

api_router = APIRouter()
api_router.include_router(v1_router)
api_router.include_router(health_router)

__all__ = ["api_router"]
