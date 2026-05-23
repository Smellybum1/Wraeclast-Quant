# SQLite Migration Readiness

Wraeclast Quant does not have a migration framework yet. Schema changes should be small, explicit, backed up, and verified before they touch local user data.

The current SQLite schema version is `2`.

## Commands

```powershell
wq status --strict
wq backup-db
wq migration-readiness --strict
wq verify-backup --backup-path <file>
wq restore-helper --backup-path <file>
```

`wq migration-readiness` is read-only. It checks the live database health, current schema contract version, latest analysis run, latest backup verification, and whether the latest backup run matches the latest database run.

It does not create backups, run migrations, mutate SQLite, create missing directories, fetch network resources, publish artifacts, or interact with the game client.

## Future Schema Change Workflow

Before a future schema change:

1. Run `wq status --strict`.
2. Run `wq backup-db`.
3. Run `wq migration-readiness --strict`.
4. Confirm `wq verify-backup --backup-path <file>` passes for the latest backup.
5. Confirm `wq restore-helper --backup-path <file>` prints a manual restore command.

During a future schema change:

1. Prefer idempotent `CREATE TABLE IF NOT EXISTS` for additive tables.
2. Use explicit migration logic for destructive, renaming, or column-changing work.
3. Preserve existing local data unless the user explicitly approves a destructive migration.
4. Keep migration code local-only and deterministic.
5. Update the SQLite schema contract, docs, and tests in the same packet.

After a future schema change:

1. Run `pytest tests/test_storage_schema.py`.
2. Run `pytest tests/test_database_health.py`.
3. Run `pytest tests/test_database_backups.py`.
4. Run `pytest`.
5. Run `wq status --strict`.
6. Create and verify a fresh backup.

## Safety Notes

Migration readiness and future schema changes must not scrape, fetch network resources, publish, post alerts, automate gameplay, send whispers, click UI, move characters, or interact with the game client.

Backups may contain local snapshot history, scored opportunities, signal inputs, report artifact paths, and manual outcome notes. Treat backups and databases as local user data.
