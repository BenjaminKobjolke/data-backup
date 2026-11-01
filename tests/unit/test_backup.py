"""Tests for the backup logic."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from databackup.backup import backup_files, cleanup_old_backups
from databackup.config import DataConfig
from databackup.exceptions import BackupError
from tests.conftest import (
    DB_REL,
    DB_ROWS,
    TXT_CONTENT,
    TXT_REL,
    extract_member,
    read_rows,
    zip_members,
)


@pytest.fixture()
def config(config_dict: dict[str, object]) -> DataConfig:
    return DataConfig.model_validate(config_dict)


def test_zip_holds_files_at_relative_paths(config: DataConfig) -> None:
    result = backup_files(config)
    assert result == config.target
    assert zip_members(result) == [DB_REL, TXT_REL]
    with zipfile.ZipFile(result) as zf:
        assert zf.read(TXT_REL).decode("utf-8") == TXT_CONTENT


def test_sqlite_snapshot_has_same_rows(config: DataConfig, tmp_path: Path) -> None:
    restored = extract_member(backup_files(config), DB_REL, tmp_path / "out")
    assert read_rows(restored) == DB_ROWS


def test_missing_source_file_raises_and_leaves_nothing(config: DataConfig) -> None:
    broken = config.model_copy(update={"files": (DB_REL, "data/missing.bin")})
    with pytest.raises(BackupError, match="missing.bin"):
        backup_files(broken)
    assert not config.target.parent.exists()


def test_existing_target_raises(config: DataConfig) -> None:
    config.target.parent.mkdir(parents=True)
    config.target.write_bytes(b"old")
    with pytest.raises(BackupError, match="already exists"):
        backup_files(config)
    assert config.target.read_bytes() == b"old"


def test_failed_build_leaves_no_temp_file(
    config: DataConfig, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(src: Path, dst: Path) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("databackup.backup._snapshot_sqlite", _boom)
    with pytest.raises(OSError, match="disk full"):
        backup_files(config)
    assert list(config.target.parent.iterdir()) == []


def test_incremental_prefixes_timestamp(config: DataConfig) -> None:
    result = backup_files(config, incremental=5)
    assert result.parent == config.target.parent
    assert result.name.endswith("_" + config.target.name)
    assert result.name != config.target.name


def test_cleanup_keeps_newest(target_zip: Path) -> None:
    target_zip.parent.mkdir(parents=True)
    names = [f"2026010{i}_120000_{target_zip.name}" for i in range(1, 6)]
    for name in names:
        (target_zip.parent / name).write_bytes(b"x")
    (target_zip.parent / "unrelated.zip").write_bytes(b"x")
    cleanup_old_backups(target_zip, keep=2)
    remaining = sorted(p.name for p in target_zip.parent.iterdir())
    assert remaining == sorted([*names[-2:], "unrelated.zip"])
