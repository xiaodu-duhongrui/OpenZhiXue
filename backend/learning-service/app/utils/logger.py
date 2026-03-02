import logging
import sys
from typing import Optional

from app.config import settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    log_level = level or ("DEBUG" if settings.DEBUG else "INFO")
    log_format = format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logger = logging.getLogger("learning-service")
    logger.setLevel(getattr(logging, log_level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level.upper()))
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
