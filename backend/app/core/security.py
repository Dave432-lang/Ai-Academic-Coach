"""
Security Module.
Provides password hashing using Argon2id and JWT access token creation/verification.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("security")

_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a plain text password using Argon2id.
    """
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against an Argon2id hash string.
    Returns True if match, False otherwise. Never throws.
    """
    try:
        return _password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError, Exception):
        return False


def create_access_token(
    subject: str,
    claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate a JWT access token with expiration time (default: settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60 mins).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    if claims:
        to_encode.update(claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.
    Returns payload dictionary if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            logger.warning("Token type mismatch in decode_access_token")
            return None
        return payload
    except jwt.PyJWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None


def get_security_config_summary() -> dict:
    """
    Returns non-sensitive security parameters for system health/readiness inspection.
    """
    return {
        "algorithm": settings.JWT_ALGORITHM,
        "token_expiration_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "environment": settings.ENVIRONMENT,
    }
