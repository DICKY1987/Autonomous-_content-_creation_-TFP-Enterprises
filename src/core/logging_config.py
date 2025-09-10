"""Central logging configuration for the project.

This module exposes ``configure_logging`` and ``get_logger`` helpers that
set up a JSON formatted logging configuration using ``logging.config.dictConfig``.
Configuration is driven by environment variables so the verbosity and the
location of log files can be adjusted without code changes.

Environment variables:

``LOG_LEVEL``        - Logging level (default ``INFO``)
``LOG_FILE``         - File path for the rotating file handler (default ``app.log``)
``LOG_MAX_BYTES``    - Maximum bytes per log file before rotation (default ``1048576``)
``LOG_BACKUP_COUNT`` - Number of rotated files to keep (default ``3``)
"""

from __future__ import annotations

import json
import logging
import logging.config
import os
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


_CONFIGURED = False


def configure_logging() -> None:
    """Configure logging for the application.

    Uses ``logging.config.dictConfig`` to apply a JSON formatter, a console
    handler and a rotating file handler. The logging level and file location
    are controlled via environment variables.
    """

    global _CONFIGURED
    if _CONFIGURED:
        return

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "app.log")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", 1_048_576))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", 3))

    config = {
        "version": 1,
        "formatters": {
            "json": {
                "()": JsonFormatter,
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": log_file,
                "maxBytes": max_bytes,
                "backupCount": backup_count,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"],
        },
    }

    logging.config.dictConfig(config)
    _CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-level logger configured for JSON output."""

    configure_logging()
    return logging.getLogger(name)

