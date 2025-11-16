"""Application-wide logging utilities."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from utils.helpers import get_script_folder


LOG_FILENAME = "app_errors.log"
LOG_DIRNAME = "logs"
LOG_MAX_BYTES = 512 * 1024  # 512KB
LOG_BACKUP_COUNT = 5

_logger: Optional[logging.Logger] = None


def _ensure_log_directory() -> Path:
    base_path = Path(get_script_folder())
    log_dir = base_path / LOG_DIRNAME
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_logger() -> logging.Logger:
    global _logger
    if _logger:
        return _logger

    log_dir = _ensure_log_directory()
    log_path = log_dir / LOG_FILENAME

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Avoid duplicate handlers when get_logger is called multiple times
    if not logger.handlers:
        logger.addHandler(handler)

    logger.propagate = False
    _logger = logger
    return logger


def log_exception(message: str, exc: BaseException | None = None) -> None:
    logger = get_logger()
    if exc is not None:
        logger.error(message, exc_info=exc)
    else:
        logger.error(message)


def log_error(message: str, exc: BaseException | None = None) -> None:
    logger = get_logger()
    if exc is not None:
        logger.error(message, exc_info=exc)
    else:
        logger.error(message)


def log_warning(message: str, exc: BaseException | None = None) -> None:
    logger = get_logger()
    if exc is not None:
        logger.warning(message, exc_info=exc)
    else:
        logger.warning(message)


def log_info(message: str) -> None:
    get_logger().info(message)


def install_global_exception_handler() -> None:
    """Route unhandled exceptions through the application logger."""

    def _handle(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        get_logger().error(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = _handle
