import sys
from pathlib import Path
import pytest

# Ensure backend directory is in sys.path for IDEs and test runners
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from app.core.config import Settings
except ImportError:
    from backend.app.core.config import Settings  # type: ignore


def test_settings_default_values(settings: Settings):
    """
    Test application settings initialization and default parameters.
    """
    assert settings.APP_TITLE == "AI Academic Coach API"
    assert settings.JWT_ALGORITHM == "HS256"
    assert isinstance(settings.cors_origins, list)
    assert len(settings.cors_origins) > 0


def test_settings_cors_origins_parsing():
    """
    Test comma-separated ALLOWED_ORIGINS string parsing into list.
    """
    custom_settings = Settings(
        ALLOWED_ORIGINS="http://localhost:3000, http://10.0.2.2:8000"
    )
    origins = custom_settings.cors_origins
    assert "http://localhost:3000" in origins
    assert "http://10.0.2.2:8000" in origins
