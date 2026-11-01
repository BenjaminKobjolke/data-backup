"""End-to-end: config file in ./configs -> CLI -> rotated zip with an intact SQLite DB."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from databackup.cli import main
from tests.conftest import DB_REL, DB_ROWS, WriteConfig, extract_member, read_rows


def test_cli_backup_with_rotation(
    write_config: WriteConfig,
    config_dict: dict[str, object],
    target_zip: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write_config(config_dict)
    monkeypatch.chdir(tmp_path)
    target_zip.parent.mkdir(parents=True)
    for day in ("20250101", "20250102"):
        (target_zip.parent / f"{day}_000000_{target_zip.name}").write_bytes(b"old")

    main(["--backup", "--config", "test", "--incremental", "2"])

    backups = sorted(target_zip.parent.glob(f"*_{target_zip.name}"))
    assert len(backups) == 2
    newest = backups[-1]
    assert not newest.name.startswith("2025")
    restored = extract_member(newest, DB_REL, tmp_path / "out")
    with closing(sqlite3.connect(restored)) as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    assert read_rows(restored) == DB_ROWS
    assert not list(target_zip.parent.glob(".databak-*"))
