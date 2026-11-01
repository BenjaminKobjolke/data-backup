"""Central logger: the only place that writes to the console."""

from __future__ import annotations

import logging
import sys

from databackup.constants import LOG_FORMAT, LOGGER_NAME


class _BelowWarning(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.WARNING


class AppLogger:
    """Info goes to stdout, warnings and errors to stderr. ``configure`` is the one toggle."""

    _logger = logging.getLogger(LOGGER_NAME)

    @classmethod
    def configure(cls, level: int = logging.INFO) -> None:
        # Handlers are rebuilt each call so they bind the current sys.stdout/stderr
        # (pytest swaps them per test).
        cls._logger.handlers.clear()
        cls._logger.setLevel(level)
        cls._logger.propagate = False
        formatter = logging.Formatter(LOG_FORMAT)

        out = logging.StreamHandler(sys.stdout)
        out.addFilter(_BelowWarning())
        out.setFormatter(formatter)
        err = logging.StreamHandler(sys.stderr)
        err.setLevel(logging.WARNING)
        err.setFormatter(formatter)
        cls._logger.addHandler(out)
        cls._logger.addHandler(err)

    @classmethod
    def info(cls, message: str) -> None:
        cls._logger.info(message)

    @classmethod
    def error(cls, message: str) -> None:
        cls._logger.error(message)
