# Backup and Restore Helper Contract

Wraeclast Quant can create and inspect local SQLite backups for snapshot history. Backups are local data-protection artifacts only. The app does not automatically restore over the live database.

## Commands

```powershell
wq backup-db
wq backups
wq verify-backup --backup-path <file>
wq restore-helper --backup-path <file>
```

`wq backup-db` copies an existing SQLite database to the backup directory and immediately verifies the copy.

`wq backups` lists local backup files and quick verification metadata. If the backup directory is missing, it reports no backups without creating the directory.

`wq verify-backup` opens a backup read-only, checks the SQLite schema contract, and reports counts and latest-run metadata.

`wq restore-helper` verifies a backup and prints a manual PowerShell restore command. It does not copy files, replace the live database, create the target directory, or mutate local data.

## Default Paths

- `database_path`: `data/wraeclast_quant.db`
- `backup_dir`: `data/backups`

Backup filenames are based on the source database stem and a safe UTC timestamp, for example:

```text
wraeclast_quant_20260523T000000Z.db
```

## Verification Fields

Backup verification reports:

- `schema_version`
- `required_tables`
- `size_bytes`
- `analysis_run_count`
- `scored_opportunity_count`
- `report_artifact_count`
- `recommendation_outcome_count`
- `latest_run_id`
- `latest_run_created_at`
- `latest_run_source_mode`
- `latest_run_item_count`

The required table list comes from the shared SQLite schema contract documented in `docs/SQLITE_SCHEMA.md`.

## Restore Boundary

Restores are manual. The helper prints a PowerShell command that uses:

```powershell
New-Item -ItemType Directory -Force -Path <target-parent>
Copy-Item -LiteralPath <backup> -Destination <database> -Force
```

The user must review and run that command manually.

## Safety Notes

Backups may contain local snapshot history, scored opportunities, signal inputs, report artifact paths, and manual outcome notes. Treat backup files as local user data.

Backup and restore-helper commands must not expose secrets, cookies, API keys, Discord tokens, private account data, or `.env` values. They must not scrape, fetch network resources, publish, post alerts, automate gameplay, send whispers, click UI, move characters, or interact with the game client.
