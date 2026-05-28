# Design

Wraeclast Quant is a local-first Path of Exile 2 market intelligence tool. It turns configured public resources, local manual signal files, deterministic scoring, SQLite snapshots, and derived reports into decision-support output for manual review.

It does not automate gameplay, perform trades, send whispers, scrape without approval, bypass source controls, publish externally, or run a server.

## Current Local Pipeline

1. Load configured resources from `RESOURCES.md` with the tolerant Markdown parser documented in `docs/RESOURCE_CONFIGURATION.md`.
2. Preview source handling through dry-run placeholder collectors.
3. Import local normalized item signals from JSON or CSV when provided.
4. Score items deterministically with the public scoring contract documented in `docs/SCORING.md`.
5. Store analysis runs and scored opportunities in local SQLite.
6. Record local run provenance for manual-import and connector-fixture pipeline runs.
7. Compare the latest run with the previous run for score and action changes using the contract documented in `docs/SNAPSHOT_COMPARISONS.md`.
8. Generate local alert candidates from snapshot changes.
9. Write Markdown reports, derived JSON, and a local static dashboard. The daily orchestration contract is documented in `docs/DAILY_PIPELINE.md`.
10. Validate local static bundles with publish-readiness, publish-handoff, and site-contract checks before any manual publishing outside the app.

`wq daily --input-path` records path-safe local provenance for manual-import runs. `wq connector-fixture-daily` proves that a reviewed, fixture-backed connector shape can drive the same local pipeline without live source access. It requires normalized local fixture signals, writes a `connector-fixture` run, and stays local-only.

`wq currency-exchange-manual-snapshot` is a source-specific local bridge for user-supplied official Currency Exchange observations when live API access is parked. It validates local JSON, can write connector-fixture JSON, and can be chained through `connector-fixture-export`, `validate-import`, or `daily --input-path` without OAuth, live HTTP, raw cache writes, or publishing.

`wq currency-exchange-ui-observation` is a local bridge for manually transcribed in-game Currency Exchange ratio/stock rows when API-shaped hourly fields are not available. It writes manual-import-compatible JSON from visible UI data only and does not scrape, OCR, fetch, write snapshots, approve source access, or publish artifacts.

`wq watchlist` reads the latest local SQLite run by default, with `--run-id` for historical runs and `--sample-data` for deterministic demos. `wq stash-ninja-watchlist` can write a derived-only local companion JSON/Markdown handoff for manual Exile-UI Stash-Ninja review without writing third-party files, calling live HTTP, or interacting with the game client.

## Storage and History

SQLite is the canonical local history store for the MVP. The default database path is `data/wraeclast_quant.db`.

Stored history includes analysis runs, scored opportunities, signal inputs, and report artifact metadata. Snapshot comparisons use item name as the comparison key for now.

The current local SQLite schema contract is version `2` and is defined in `wraeclast_quant.storage.schema`. Both `wq db-check` and backup verification use that shared table contract so live database checks and backup checks do not drift. The storage contract is documented in `docs/SQLITE_SCHEMA.md`.

Local SQLite backup and restore-helper behavior is documented in `docs/BACKUPS.md`. Restore remains manual: the app verifies backups and prints guidance, but it does not replace the live database automatically.

Manual recommendation outcome review is documented in `docs/OUTCOMES.md`. Outcome notes stay local and are excluded from derived public intel.

Calibration commands summarize recorded recommendation outcomes by action, score bucket, outcome label, and local review prompts. They are local decision-support only and do not retune scoring automatically.

## Derived Public Intel

`wq export` writes `data/processed/public_intel.json`. This file is intended as a future public website contract, but it remains local-only today.

The export includes a top-level `schema_version` plus derived fields such as item names, scores, actions, deltas, alert reasons, latest run metadata, and compliance counts. It excludes raw source data, resource notes, credentials, cookies, tokens, `.env` values, and raw `RESOURCES.md` content.

`wq site` validates that JSON and renders `data/processed/site/index.html`. The static dashboard uses local inline HTML/CSS only and does not make network requests.

`wq validate-intel` checks the exported JSON against the local v1 contract documented in `docs/PUBLIC_INTEL_JSON.md`. `wq site` and `wq site-bundle` also enforce that contract before rendering or packaging. Site bundle manifests include validated public-intel metadata such as schema version and latest run id without source URLs or raw inputs. `wq publish-check`, `wq publish-handoff`, and `wq site-contract` provide local readiness and handoff evidence without uploading, hosting, or publishing. The local static artifact contract is documented in `docs/STATIC_ARTIFACTS.md`.

## CLI Surfaces

- `collect` and `compliance` inspect configured resources without fetching live data.
- `preflight`, `connector-candidates`, connector review, approval, fixture, dry-run, and connector-plan commands gate future connector work.
- `analyze` and `report` support deterministic sample-data workflows; `watchlist` reads local stored runs by default and keeps sample data opt-in.
- `import`, `validate-import`, and `inspect-import` handle local normalized JSON/CSV signal files using the contract documented in `docs/MANUAL_IMPORT.md`.
- `currency-exchange-manual-snapshot` validates user-supplied local Currency Exchange observations and can bridge them into connector-fixture or manual-import workflows without live source access.
- `currency-exchange-ui-observation` converts user-transcribed in-game Currency Exchange rows into normalized manual-import JSON without live source access.
- `snapshots`, `compare`, and `alerts` inspect persisted local history. Snapshot comparisons are documented in `docs/SNAPSHOT_COMPARISONS.md`, and alert rules are documented in `docs/ALERTS.md`.
- `export`, `stash-ninja-watchlist`, `validate-intel`, `site`, `site-bundle`, `publish-check`, `publish-handoff`, and `site-contract` render and validate derived local artifacts.
- `daily` orchestrates one local pipeline run from sample data or a manual import file using the contract documented in `docs/DAILY_PIPELINE.md`.
- `backup-db`, `verify-backup`, `backups`, `restore-helper`, and `migration-readiness` protect local SQLite data before future schema work.
- `record-outcome`, `outcomes`, review coverage, outcome reports, and calibration commands support local recommendation review.
- `run-provenance` inspects local audit metadata for runs that record provenance, including manual-import daily runs and connector-fixture proof runs.

## Extension Points

- `collectors/registry.py` maps resource types to collector classes.
- `importers/` handles local user-provided input formats.
- `normalizers/` contains deterministic cleanup for item names, currency labels, and text.
- `intelligence/scoring.py` holds the public scoring contract documented in `docs/SCORING.md`.
- `intelligence/snapshot_deltas.py` and `intelligence/alerts.py` derive local changes and alert candidates documented in `docs/ALERTS.md`.
- `reports/` renders Markdown, JSON, and static dashboard outputs.
- `storage/` owns the SQLite schema and repository methods.

The codebase now favors stable public facades and command aggregators with focused internal modules for maintainability. Preserve those facades when decomposing internals.

Real collectors should only be added after source-specific compliance review covering terms, robots.txt or API policy, authentication, rate limits, caching, allowed use, and data retention.

Connector work is gated by `docs/CONNECTOR_POLICY.md`. Use `wq preflight`, `wq connector-candidates`, `wq connector-review-prep` or `wq connector-draft`, `wq connector-review-evidence`, `wq connector-review-status`, `wq connector-review-report`, `wq connector-approval-helper`, `wq connector-approval-patch`, `wq connector-check`, and `wq connector-plan` before designing any source-specific API, RSS, download, or scraping connector. Until review evidence and manual `RESOURCES.md` approval are complete, collectors remain dry-run placeholders.
