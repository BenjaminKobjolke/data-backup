"""Tests for config loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from databackup.config import load_config
from databackup.exceptions import ConfigError
from tests.conftest import DB_REL, TXT_REL, WriteConfig


def test_load_valid_config(
    write_config: WriteConfig, config_dict: dict[str, object], source_dir: Path
) -> None:
    path = write_config(config_dict)
    config = load_config("test", config_dir=path.parent)
    assert config.source == source_dir
    assert config.files == (DB_REL, TXT_REL)
    assert config.target.suffix == ".zip"


def test_json_suffix_is_optional(write_config: WriteConfig, config_dict: dict[str, object]) -> None:
    path = write_config(config_dict)
    assert load_config("test.json", config_dir=path.parent) == load_config(
        "test", config_dir=path.parent
    )


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config("nope", config_dir=tmp_path)


def test_invalid_json_raises(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError, match="Invalid config"):
        load_config("bad", config_dir=tmp_path)


def test_missing_key_raises(write_config: WriteConfig, config_dict: dict[str, object]) -> None:
    del config_dict["target"]
    path = write_config(config_dict)
    with pytest.raises(ConfigError, match="target"):
        load_config("test", config_dir=path.parent)


def test_missing_source_dir_raises(
    write_config: WriteConfig, config_dict: dict[str, object], tmp_path: Path
) -> None:
    config_dict["source"] = str(tmp_path / "missing")
    path = write_config(config_dict)
    with pytest.raises(ConfigError, match="source"):
        load_config("test", config_dir=path.parent)


@pytest.mark.parametrize("bad", ["C:/abs/file.db", "/abs/file.db", "../escape.db"])
def test_non_relative_file_rejected(
    write_config: WriteConfig, config_dict: dict[str, object], bad: str
) -> None:
    config_dict["files"] = [bad]
    path = write_config(config_dict)
    with pytest.raises(ConfigError, match="relative"):
        load_config("test", config_dir=path.parent)


def test_empty_files_rejected(write_config: WriteConfig, config_dict: dict[str, object]) -> None:
    config_dict["files"] = []
    path = write_config(config_dict)
    with pytest.raises(ConfigError, match="files"):
        load_config("test", config_dir=path.parent)


def test_non_zip_target_rejected(
    write_config: WriteConfig, config_dict: dict[str, object], tmp_path: Path
) -> None:
    config_dict["target"] = str(tmp_path / "out.tar")
    path = write_config(config_dict)
    with pytest.raises(ConfigError, match=r"\.zip"):
        load_config("test", config_dir=path.parent)
