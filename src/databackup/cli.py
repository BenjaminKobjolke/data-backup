"""Command-line interface for databackup."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from databackup.app_logger import AppLogger
from databackup.backup import backup_files
from databackup.config import load_config
from databackup.constants import ERR_INCREMENTAL_NOT_POSITIVE, MSG_BACKUP_COMPLETE, MSG_ERROR
from databackup.exceptions import DataBackupError


def _positive_int(value: str) -> int:
    # keep=0 would slice matches[:-0] == [] and silently keep everything.
    try:
        number = int(value)
    except ValueError:
        number = 0
    if number < 1:
        raise argparse.ArgumentTypeError(ERR_INCREMENTAL_NOT_POSITIVE.format(value=value))
    return number


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="databackup",
        description="Back up data files (SQLite-safe) into rotated zip archives.",
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--backup", action="store_true", help="Zip the configured files")
    parser.add_argument(
        "--config", required=True, help="Config name under configs/ (.json optional) or path"
    )
    parser.add_argument(
        "--incremental",
        type=_positive_int,
        default=None,
        help="Prefix a timestamp and keep only the N most recent backups",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    AppLogger.configure()
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        path = backup_files(config, incremental=args.incremental)
    except DataBackupError as exc:
        AppLogger.error(MSG_ERROR.format(error=exc))
        sys.exit(1)
    AppLogger.info(MSG_BACKUP_COMPLETE.format(path=path))
