import os
from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables and .env file.
    Validates required configuration upon application startup.
    """
    APP_TITLE: str = "AI Academic Coach API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", description="Application runtime environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging output level")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://academic_coach:academic_coach_dev_pass@localhost:5432/ai_academic_coach",
        description="SQLAlchemy compatible database connection string"
    )

    # Security Parameters
    SECRET_KEY: str = Field(
        default="dev_insecure_secret_key_change_in_production_1234567890",
        description="Secret key for signing tokens and session data"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signature algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token expiration window in minutes")

    # CORS Settings
    ALLOWED_ORIGINS: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://localhost",
        description="Comma separated list of allowed HTTP origins"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "testing", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got '{v}'")
        return v.lower()

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_production_secret_key(cls, v: str, info) -> str:
        # Require secure SECRET_KEY in production environments
        env = os.getenv("ENVIRONMENT", "development").lower()
        if env == "production" and ("insecure" in v or "change_this" in v or len(v) < 32):
            raise ValueError(
                "CRITICAL: A secure, strong SECRET_KEY (minimum 32 chars) must be provided in production!"
            )
        return v

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance for fast access across application components.
    """
    return Settings()


settings = get_settings()
