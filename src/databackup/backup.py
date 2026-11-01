"""Back up the configured files into one zip archive."""

from __future__ import annotations

import contextlib
import os
import sqlite3
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from databackup.config import DataConfig
from databackup.constants import (
    ERR_BACKUP_PATH_EXISTS,
    ERR_SOURCE_FILES_MISSING,
    SQLITE_HEADER,
    TIMESTAMP_FORMAT,
    TMP_PREFIX,
    ZIP_EXT,
)
from databackup.exceptions import BackupError


def resolve_incremental_path(base_path: Path) -> Path:
    """Return a timestamped version of *base_path*.

    Example: ``backups/app.zip`` becomes ``backups/20260213_143022_app.zip``.
    """
    timestamp = datetime.now(UTC).strftime(TIMESTAMP_FORMAT)
    return base_path.parent / f"{timestamp}_{base_path.name}"


def cleanup_old_backups(base_path: Path, keep: int) -> None:
    """Delete old incremental backups of *base_path*, keeping the *keep* newest."""
    matches = sorted(base_path.parent.glob(f"*_{base_path.name}"))
    for old in matches[:-keep]:
        old.unlink()


def _is_sqlite(path: Path) -> bool:
    with path.open("rb") as f:
        return f.read(len(SQLITE_HEADER)) == SQLITE_HEADER


def _snapshot_sqlite(src: Path, dst: Path) -> None:
    """Copy a SQLite DB via the backup API: consistent even while another process writes."""
    with (
        contextlib.closing(sqlite3.connect(src)) as src_conn,
        contextlib.closing(sqlite3.connect(dst)) as dst_conn,
    ):
        src_conn.backup(dst_conn)


def _write_archive(config: DataConfig, zip_path: Path) -> None:
    with (
        tempfile.TemporaryDirectory() as snapshot_dir,
        zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf,
    ):
        for index, rel in enumerate(config.files):
            src = config.source / rel
            if _is_sqlite(src):
                # index keeps two DBs with the same file name apart.
                snapshot = Path(snapshot_dir) / f"{index}_{src.name}"
                _snapshot_sqlite(src, snapshot)
                src = snapshot
            zf.write(src, arcname=rel)


def backup_files(config: DataConfig, incremental: int | None = None) -> Path:
    """Zip the configured files to the target and return the written path.

    Args:
        config: Backup job configuration.
        incremental: If set, prefix a timestamp and keep only the N newest backups.
    """
    missing = [f for f in config.files if not (config.source / f).is_file()]
    if missing:
        raise BackupError(ERR_SOURCE_FILES_MISSING.format(files=", ".join(missing)))

    final_path = config.target if incremental is None else resolve_incremental_path(config.target)
    if final_path.exists():
        raise BackupError(ERR_BACKUP_PATH_EXISTS.format(path=final_path))
    final_path.parent.mkdir(parents=True, exist_ok=True)

    # Build under a temp name next to the target, then atomically rename, so a
    # synced folder (Syncthing) never sees a half-written archive under the final name.
    fd, tmp_name = tempfile.mkstemp(prefix=TMP_PREFIX, suffix=ZIP_EXT, dir=final_path.parent)
    os.close(fd)
    tmp_zip = Path(tmp_name)
    try:
        _write_archive(config, tmp_zip)
        os.replace(tmp_zip, final_path)
    except BaseException:
        # suppress: a failed cleanup must not mask the error that got us here.
        with contextlib.suppress(OSError):
            tmp_zip.unlink(missing_ok=True)
        raise

    if incremental is not None:
        cleanup_old_backups(config.target, keep=incremental)
    return final_path
