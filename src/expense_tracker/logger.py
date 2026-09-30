"""File logging configuration shared by every module."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import config

_ROOT_NAME = "expense_tracker"
# Library-style default: stay silent unless the application configures logging
logging.getLogger(_ROOT_NAME).addHandler(logging.NullHandler())


def setup_logging(log_file=None, level=logging.INFO):
    """Attach a rotating file handler (logs/app.log) to the application logger."""
    log_file = Path(log_file or config.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger(_ROOT_NAME)
    root.setLevel(level)
    if any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return root  # already configured
    handler = RotatingFileHandler(
        log_file, maxBytes=500_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    root.addHandler(handler)
    return root


def get_logger(name):
    """Return a child logger such as 'expense_tracker.auth'."""
    return logging.getLogger(f"{_ROOT_NAME}.{name}")
