"""Custom exception hierarchy."""


class DataBackupError(Exception):
    """Base exception for databackup."""


class ConfigError(DataBackupError):
    """Configuration-related errors."""


class BackupError(DataBackupError):
    """Backup operation errors."""
