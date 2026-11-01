"""Backup job configuration loading and validation."""

from __future__ import annotations

from pathlib import Path, PurePath

from pydantic import BaseModel, ConfigDict, DirectoryPath, Field, ValidationError, field_validator

from databackup.constants import (
    CONFIG_DIR,
    CONFIG_EXT,
    ERR_CONFIG_INVALID,
    ERR_CONFIG_NOT_FOUND,
    ERR_FILE_NOT_RELATIVE,
    ERR_TARGET_NOT_ZIP,
    ZIP_EXT,
)
from databackup.exceptions import ConfigError


class DataConfig(BaseModel):
    """One backup job: which files under *source* go into the *target* zip."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: DirectoryPath
    files: tuple[str, ...] = Field(min_length=1)
    target: Path

    @field_validator("files")
    @classmethod
    def _files_relative(cls, files: tuple[str, ...]) -> tuple[str, ...]:
        normalized = []
        for file in files:
            path = PurePath(file)
            # anchor catches "C:/x", "C:x" and "/x" on Windows; ".." would escape source.
            if path.anchor or ".." in path.parts:
                raise ValueError(ERR_FILE_NOT_RELATIVE.format(file=file))
            normalized.append(path.as_posix())
        return tuple(normalized)

    @field_validator("target")
    @classmethod
    def _target_zip(cls, target: Path) -> Path:
        if target.suffix.lower() != ZIP_EXT:
            raise ValueError(ERR_TARGET_NOT_ZIP.format(target=target))
        return target


def load_config(name: str, *, config_dir: Path | None = None) -> DataConfig:
    """Load a backup job config by name (``.json`` optional) or absolute path.

    Args:
        name: Config name under *config_dir*, with or without ``.json``.
        config_dir: Override config directory. Defaults to ``./configs/``.
    """
    if config_dir is None:
        config_dir = Path.cwd() / CONFIG_DIR

    if name.lower().endswith(CONFIG_EXT):
        name = name[: -len(CONFIG_EXT)]

    # An absolute *name* replaces config_dir in the join.
    path = config_dir / f"{name}{CONFIG_EXT}"
    if not path.is_file():
        raise ConfigError(ERR_CONFIG_NOT_FOUND.format(path=path))

    try:
        return DataConfig.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as exc:
        raise ConfigError(ERR_CONFIG_INVALID.format(path=path, error=exc)) from exc
