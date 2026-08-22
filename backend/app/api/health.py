from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.core.config import settings
from app.database.connection import check_database_connection

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health(detailed: bool = False):
    """
    Health check endpoint for application readiness and liveness probes.
    Returns status: 'ok' required by Phase 1 foundation specs.
    """
    response = {
        "status": "ok"
    }

    if detailed:
        response.update({
            "app": settings.APP_TITLE,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": check_database_connection(),
        })

    return response
