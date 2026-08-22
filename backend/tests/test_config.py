import pytest
from app.core.config import Settings


def test_settings_default_values(settings):
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
