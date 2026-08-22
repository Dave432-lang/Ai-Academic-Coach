import logging
import sys
from typing import Optional


class SensitiveDataFilter(logging.Filter):
    """
    Filter to sanitize sensitive keywords (passwords, tokens, keys) from log messages.
    """
    SENSITIVE_PATTERNS = ["password", "secret", "token", "authorization", "bearer", "api_key"]

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage().lower()
        # Ensure log message does not print plain authorization headers or raw secret tokens
        for pattern in self.SENSITIVE_PATTERNS:
            if f"{pattern}=" in message or f"{pattern}:" in message:
                record.msg = "[SENSITIVE DATA MASKED]"
                record.args = ()
                break
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging format and output destination.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to prevent duplicate output
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Suppress verbose noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieve a named logger instance.
    """
    return logging.getLogger(name or "ai_academic_coach")
