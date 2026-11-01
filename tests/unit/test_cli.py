"""Tests for the command-line interface."""

from __future__ import annotations

from pathlib import Path

import pytest

from databackup.cli import main
from tests.conftest import WriteConfig


def test_requires_backup_action() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--config", "x"])
    assert exc.value.code == 2


def test_rejects_non_positive_incremental() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--backup", "--config", "x", "--incremental", "0"])
    assert exc.value.code == 2


def test_error_exits_1_and_reports(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--backup", "--config", str(tmp_path / "missing")])
    assert exc.value.code == 1
    assert "Error:" in capsys.readouterr().err


def test_success_reports_path(
    write_config: WriteConfig,
    config_dict: dict[str, object],
    target_zip: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = write_config(config_dict)
    main(["--backup", "--config", str(path)])
    assert target_zip.exists()
    assert f"Backup complete: {target_zip}" in capsys.readouterr().out
