"""Application logging configuration with rotating file handler."""

import logging
import sys
from logging.handlers import RotatingFileHandler

from app.utils.paths import get_log_dir

LOG_FILE_NAME = "videodownloader.log"
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure root logger with console and rotating file handlers."""
    log_dir = get_log_dir()
    log_file = log_dir / LOG_FILE_NAME

    logger = logging.getLogger("videodownloader")
    logger.setLevel(level)

    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] [%(threadName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler
    try:
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning("Failed to initialize rotating file logger: %s", e)

    logger.info("Logging initialized. Log file: %s", log_file)
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under videodownloader namespace."""
    return logging.getLogger(f"videodownloader.{name}")
