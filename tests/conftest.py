"""Shared test fixtures: a source folder with one SQLite DB and one plain file."""

from __future__ import annotations

import json
import sqlite3
import zipfile
from collections.abc import Callable
from contextlib import closing
from pathlib import Path

import pytest

DB_REL = "data/app.db"
TXT_REL = "data/notes.txt"
TXT_CONTENT = "hello"
DB_ROWS = [(1, "alpha"), (2, "beta")]

WriteConfig = Callable[[dict[str, object]], Path]


def create_sqlite(path: Path) -> None:
    """Create a SQLite DB at *path* holding DB_ROWS in table ``items``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
        conn.executemany("INSERT INTO items VALUES (?, ?)", DB_ROWS)
        conn.commit()


def read_rows(path: Path) -> list[tuple[int, str]]:
    with closing(sqlite3.connect(path)) as conn:
        rows: list[tuple[int, str]] = conn.execute(
            "SELECT id, name FROM items ORDER BY id"
        ).fetchall()
        return rows


def extract_member(zip_path: Path, member: str, out_dir: Path) -> Path:
    """Extract *member* from *zip_path* into *out_dir* and return the extracted path."""
    with zipfile.ZipFile(zip_path) as zf:
        return Path(zf.extract(member, out_dir))


def zip_members(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return sorted(zf.namelist())


@pytest.fixture()
def source_dir(tmp_path: Path) -> Path:
    src = tmp_path / "source"
    create_sqlite(src / DB_REL)
    (src / TXT_REL).write_text(TXT_CONTENT, encoding="utf-8")
    return src


@pytest.fixture()
def target_zip(tmp_path: Path) -> Path:
    return tmp_path / "backups" / "app.zip"


@pytest.fixture()
def config_dict(source_dir: Path, target_zip: Path) -> dict[str, object]:
    return {"source": str(source_dir), "files": [DB_REL, TXT_REL], "target": str(target_zip)}


@pytest.fixture()
def write_config(tmp_path: Path) -> WriteConfig:
    """Return a writer that stores a config dict as ``configs/test.json`` under tmp_path."""

    def _write(data: dict[str, object]) -> Path:
        config_dir = tmp_path / "configs"
        config_dir.mkdir(exist_ok=True)
        path = config_dir / "test.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return _write
