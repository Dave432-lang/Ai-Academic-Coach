"""
Security Foundation Module (Phase 1 Placeholder).
Authentication, password hashing, and token verification utilities will be expanded in Phase 2.
"""
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("security")


def get_security_config_summary() -> dict:
    """
    Returns non-sensitive security parameters for system health/readiness inspection.
    """
    return {
        "algorithm": settings.JWT_ALGORITHM,
        "token_expiration_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "environment": settings.ENVIRONMENT,
    }
