# Data Backup

CLI tool to back up data files into rotated `.zip` archives. SQLite databases are snapshotted
through SQLite's backup API, so a database in use by a running app is copied consistently.
Sibling of [sql-backup](../sql-backup).

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Dependency: `pydantic` (config validation)

## Setup

```bash
install.bat
```

## Configuration

```bash
cp configs_example/example.json configs/my_job.json
```

Edit `source`, `files` and `target`. The `configs/` folder is gitignored. See
[docs/BACKUP.md](docs/BACKUP.md#config) for the keys.

## Usage

| Command | Purpose |
|---|---|
| [`--backup`](docs/BACKUP.md) | Zip the configured files (incremental rotation, SQLite-safe) |

```bash
start.bat --backup --config mindspark --incremental 30
```

## Development

```bash
tools\run_tests.bat               # unit tests
tools\run_integration_tests.bat   # integration tests
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/
update.bat                        # update dependencies
```
