# SQLite Schema Contract

Wraeclast Quant stores local snapshot history in SQLite. The database is local-first and exists to support analysis history, comparisons, reports, alert previews, manual outcome review, backups, and local dashboard exports.

The schema is managed with Python stdlib `sqlite3`. There is no migration framework yet.

## Commands

```powershell
wq schema
wq db-check
wq backup-db
wq verify-backup --backup-path <file>
wq restore-helper --backup-path <file>
```

`wq schema` prints the current contract without opening or writing the database.

`wq db-check` validates an existing local database without creating a missing one.

Backup verification uses the same required-table contract as database health checks.

## Current Version

The current SQLite schema version is `2`.

## Required Tables

Required SQLite tables:

- `analysis_runs`: One row per scoring/import/report pipeline run.
- `scored_opportunities`: Ranked item recommendations and deterministic signal inputs.
- `report_artifacts`: Local report files generated from analysis runs.
- `recommendation_outcomes`: Manual review outcomes for prior recommendations.
- `run_provenance`: Local audit metadata for analysis run inputs and connector fixtures.

## Table Shapes

`analysis_runs` stores:

- `id`
- `created_at`
- `source_mode`
- `item_count`

`scored_opportunities` stores:

- `id`
- `run_id`
- `item_name`
- `opportunity_score`
- `action`
- `inputs_json`

`report_artifacts` stores:

- `id`
- `run_id`
- `path`
- `created_at`

`recommendation_outcomes` stores:

- `id`
- `run_id`
- `item_name`
- `outcome`
- `notes`
- `observed_at`

`run_provenance` stores:

- `run_id`
- `source_kind`
- `resource_name`
- `connector_id`
- `access_method`
- `metadata_json`
- `created_at`

## Read-Only Behavior

Read-only commands should not create an empty SQLite database or parent directories when the database is missing. They should report no data or no snapshots instead.

Write commands such as `wq analyze`, `wq import`, `wq report`, `wq daily`, and `wq record-outcome` may create or update the local database as part of their explicit purpose.

## Backup Boundary

Backups are local SQLite file copies. `wq backup-db` creates a backup only when a source database exists and then verifies it immediately. The backup and restore-helper contract is documented in `docs/BACKUPS.md`.

`wq verify-backup` and `wq restore-helper` are read-only. `restore-helper` prints a manual PowerShell restore command but does not replace the live database.

## Safety Notes

SQLite storage is local data only. It must not include credentials, cookies, API keys, Discord tokens, private account data, or `.env` values.

Schema commands and backup helpers must not scrape, fetch network resources, publish, post alerts, automate gameplay, send whispers, click UI, move characters, or interact with the game client.
