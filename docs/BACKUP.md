# `--backup`

Zip the files listed in a config into one archive.

```bash
databackup --backup --config mindspark
```

Fails if the target file already exists (use `--incremental` to timestamp it automatically).

## Config

Config files live in `configs/` (gitignored); copy `configs_example/example.json` to start.

```json
{
    "source": "D:/GIT/GitHub/MindSpark",
    "files": ["data/mindspark.db"],
    "target": "E:/[--Sync--]/Backups/mindspark_mindmaps/mindspark.zip"
}
```

| Key | Meaning |
|---|---|
| `source` | Existing folder the files are read from |
| `files` | One or more paths relative to `source`; stored at the same relative path in the zip |
| `target` | Archive to write; must end with `.zip` |

The `--config` value is a name under `configs/` (`.json` optional) or an absolute path.
All source files must exist, otherwise nothing is written.

## Incremental backup

`--incremental N` prefixes the target name with a UTC timestamp and keeps only the N newest
backups:

```bash
databackup --backup --config mindspark --incremental 30
```

This produces files like `mindspark_mindmaps/20261101_101500_mindspark.zip`. Once there are more
than 30 matching backups, the oldest are deleted. Deletion only runs after the new backup
succeeded.

## SQLite files

Files that start with the SQLite header are copied through SQLite's backup API instead of a raw
file copy, so the snapshot is consistent even while the owning app (e.g. MindSpark) is writing.

## Writing to a synced folder

The archive is built under a temp name (`.databak-*.zip`) in the target folder and atomically
renamed once complete, so the final `.zip` never appears partially written. In Syncthing you can
ignore `.databak-*` to skip the transient temp files.
