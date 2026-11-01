"""Centralized string constants."""

LOGGER_NAME = "databackup"
LOG_FORMAT = "%(message)s"

CONFIG_DIR = "configs"
CONFIG_EXT = ".json"
ZIP_EXT = ".zip"
TMP_PREFIX = ".databak-"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

SQLITE_HEADER = b"SQLite format 3\x00"

MSG_BACKUP_COMPLETE = "Backup complete: {path}"
MSG_ERROR = "Error: {error}"

ERR_CONFIG_NOT_FOUND = "Config file not found: {path}"
ERR_CONFIG_INVALID = "Invalid config {path}: {error}"
ERR_FILE_NOT_RELATIVE = "File must be a relative path inside source: {file}"
ERR_TARGET_NOT_ZIP = "Target must end with .zip: {target}"
ERR_SOURCE_FILES_MISSING = "Source file(s) not found: {files}"
ERR_BACKUP_PATH_EXISTS = "Backup file already exists: {path}"
ERR_INCREMENTAL_NOT_POSITIVE = "--incremental must be a positive integer, got: {value}"
