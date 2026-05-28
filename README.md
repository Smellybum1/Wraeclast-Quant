# Wraeclast Quant

Local-first, ToS-safe market intelligence for Path of Exile 2.

Wraeclast Quant reads user-configured public resources from `RESOURCES.md`, imports local item signal files, stores SQLite snapshots, and produces human-readable research outputs. It does not automate gameplay, send in-game inputs, bypass access controls, scrape without approval, or perform trades.

## Quick Start

```powershell
python -m pip install -e ".[dev]"
wq collect --dry-run
wq daily --sample-data
wq watchlist
wq snapshots
wq compare
wq alerts
wq export
wq site
wq site-bundle
wq publish-check
wq publish-handoff
wq site-contract
```

Open `data/processed/site/index.html` after `wq site` or `wq daily` to view the local static dashboard preview.

For the no-OAuth MVP daily loop, see `docs/MVP_DAILY_WORKFLOW.md`.

## Common Commands

- `wq collect --dry-run` loads `RESOURCES.md` and previews placeholder collectors.
- `wq compliance` summarizes configured resource compliance status.
- `wq status` shows local resource, snapshot, SQLite health, market brief, public-intel contract, static dashboard, site bundle, optional Stash-Ninja handoff, backup, review, and artifact health without writing data.
- `wq status --json` prints versioned machine-readable JSON with stable row maps and failure keys for local automation. See `docs/STATUS_JSON.md` for the contract.
- `wq status --strict` prints the same status table and exits nonzero if any health row, including backup verification, needs attention.
- `wq schema` prints the current local SQLite schema contract without opening the database. See `docs/SQLITE_SCHEMA.md` for the storage contract.
- `wq preflight` checks whether configured resources are ready for future connector work.
- `wq connector-candidates` ranks local resource review candidates and prints draft commands without writing files.
- `wq connector-review-prep --resource <id-or-name> --access-method api` writes a local review draft and human checklist without approving a source.
- `wq connector-review-evidence --review-path <file>` updates a local review draft from manually collected evidence.
- `wq connector-review-status --review-path <file>` inspects an incomplete or completed connector review without approving it.
- `wq connector-check --review-path <file>` validates a proposed connector review before implementation planning.
- `wq connector-approval-helper --review-path <file>` suggests the manual `RESOURCES.md` allowed-use change needed after a completed review.
- `wq connector-approval-patch --review-path <file> --output-path <file>` writes a read-only unified diff preview for that manual `RESOURCES.md` change when the review is complete.
- `wq connector-fixture-run --review-path <file> --fixture-path <file>` validates a local synthetic connector output fixture without network access.
- `wq connector-dry-run --review-path <file> --fixture-path <file>` runs the fixture-backed connector interface without network access.
- `wq connector-fixture-export --review-path <file> --fixture-path <file> --output-path <file>` writes manual-import-compatible JSON from a local fixture with normalized signals.
- `wq connector-fixture-daily --review-path <file> --fixture-path <file>` runs the full local pipeline from a normalized-signal fixture without network access.
- `wq connector-plan --review-path <file>` previews a local cache/rate-limit plan for a ready connector review without fetching.
- `wq currency-exchange-manual-snapshot --input-path <file>` validates a local official Currency Exchange manual snapshot and can write connector-fixture JSON when given `--history-path` and `--output-fixture-path`.
- `wq currency-exchange-ui-observation --input-path <file> --output-path <file> [--review-notes-output-path <file>]` converts a local transcription of visible in-game Currency Exchange ratio/stock rows into manual-import-compatible JSON and can write a local Markdown review sidecar without OAuth, live HTTP, scraping, OCR, game-client automation, snapshots, outcome recording, or publishing.
- `wq analyze --sample-data` scores sample items and records one SQLite run.
- `wq import --input-path <file>` scores a local JSON or CSV signal file and records one manual-import run.
- `wq validate-import --input-path <file>` checks a local JSON or CSV signal file without recording a run.
- `wq inspect-import --input-path <file>` shows read-only score and signal diagnostics for a local import file.
- `wq report --sample-data` writes `data/processed/market_brief.md`.
- `wq watchlist` shows top recommendations from the latest local SQLite run; add `--run-id <id>` for a specific run or `--sample-data` for deterministic demo data. For fully reviewed stored runs with calibration review prompts, it points back to `wq calibration` without changing scoring.
- `wq stash-ninja-watchlist` writes a derived-only local companion JSON/Markdown watchlist for manual Exile-UI Stash-Ninja use. Fully reviewed handoffs with calibration prompts point back to `wq calibration`; the command does not write Exile-UI files, automate the overlay, call live HTTP, or interact with the game client.
- `wq snapshots` shows recent persisted runs and top items.
- `wq db-check` verifies the local SQLite snapshot database and schema contract without writing files.
- `wq backup-db` writes and immediately verifies a local SQLite backup of snapshot history. See `docs/BACKUPS.md` for the backup and restore-helper contract.
- `wq backups` lists local SQLite backups and quick verification metadata.
- `wq verify-backup --backup-path <file>` checks a local SQLite backup and schema contract without writing files.
- `wq restore-helper --backup-path <file>` verifies a backup and prints a manual PowerShell restore command without writing files.
- `wq migration-readiness` checks whether the current database and latest backup are ready before future SQLite schema work. See `docs/MIGRATIONS.md`.
- `wq run-provenance` inspects local audit metadata for the latest run or a selected run, including path-safe manual-import daily provenance and connector-fixture proof provenance.
- `wq review-queue` shows recommendations from the latest run that still need manual outcome review; add `--run-id <id> --output-path <file>` to write a local Markdown review worksheet without recording outcomes, optionally add `--context-path <file>` to embed local review context such as a UI-observation sidecar, and add `--decisions-output-path <file>` to write an editable JSON template for `record-outcomes --dry-run`.
- `wq review-coverage` shows how much of a run has recorded manual outcome review.
- `wq record-outcome --run-id <id> --item-name <name> --outcome positive` records a local manual review result for a recommendation. See `docs/OUTCOMES.md` for the outcome review contract.
- `wq record-outcomes --input-path <file> --dry-run` validates a local batch of human-reviewed outcome decisions without writing records; omit `--dry-run` to record the validated batch.
- `wq outcomes` shows recent local recommendation outcomes and summary counts, then points to read-only review and calibration commands.
- `wq outcome-review` joins recorded outcomes to their original scores and actions, then points to local summary/report follow-up.
- `wq outcome-report --output-path data/processed/outcome_review.md` writes a local recommendation review artifact.
- `wq calibration` summarizes recorded outcomes by action, score bucket, outcome label, and local review prompts without changing scoring.
- `wq calibration-report --output-path data/processed/calibration_report.md` writes a local recommendation calibration artifact.
- `wq compare` compares the latest run against the previous run using the contract documented in `docs/SNAPSHOT_COMPARISONS.md`.
- `wq alerts` previews local alert candidates from snapshot changes.
- `wq export` writes derived public intel to `data/processed/public_intel.json`.
- `wq validate-intel` checks `public_intel.json` against the local derived-only contract documented in `docs/PUBLIC_INTEL_JSON.md`.
- `wq site` validates public intel and renders `data/processed/site/index.html`.
- `wq site-bundle` validates and packages the local static dashboard and public intel JSON with a small manifest for manual inspection. See `docs/STATIC_ARTIFACTS.md` for the local artifact contract.
- `wq publish-check` verifies the local site bundle is valid, derived-only, and fresh before any manual publishing.
- `wq publish-handoff` writes `data/processed/publish_handoff.md` with readiness evidence and a manual publishing checklist. It does not upload, host, or publish anything.
- `wq site-contract` writes `data/processed/site_contract.json`, a local derived-only descriptor for future public-site handoff. It does not upload, host, or publish anything.
- `wq daily --sample-data` runs the local sample-data pipeline end to end. See `docs/DAILY_PIPELINE.md` for the orchestration contract.
- `wq daily --input-path <file>` runs the same pipeline from a local manual import file and records path-safe local run provenance; add `--stash-ninja-watchlist` to write the local Stash-Ninja companion handoff for the created run.

Alert preview sensitivity can be tuned per command with `--watch-threshold`, `--buy-threshold`, and `--big-delta` on `wq alerts`, `wq export`, and `wq daily`. Local alert rules are documented in `docs/ALERTS.md`.

Deterministic opportunity scoring weights and action thresholds are documented in `docs/SCORING.md`.

## Manual Import Format

Manual import is normalized input only. Each item needs a name and eight `0-100` signal scores. JSON may be a list or an object with an `items` list:

```json
[
  {
    "name": "Stormglass Catalyst",
    "signals": {
      "demand_momentum": 88,
      "build_dependency_score": 82,
      "price_discount_score": 76,
      "liquidity_score": 70,
      "historical_spike_score": 68,
      "patch_relevance_score": 74,
      "manipulation_risk": 18,
      "stale_data_penalty": 8
    }
  }
]
```

CSV uses the same fields:

```csv
name,demand_momentum,build_dependency_score,price_discount_score,liquidity_score,historical_spike_score,patch_relevance_score,manipulation_risk,stale_data_penalty
Stormglass Catalyst,88,82,76,70,68,74,18,8
```

Starter templates live at `examples/manual_import_template.json` and `examples/manual_import_template.csv`. See `docs/MANUAL_IMPORT.md` for the full import contract. Use `wq validate-import --input-path <file>` before `wq import` or `wq daily --input-path` when you want a read-only schema check. Use `wq inspect-import --input-path <file>` when you want read-only action counts, score ranges, and signal averages before recording a snapshot.

## Generated Local Artifacts

- `data/wraeclast_quant.db` stores local SQLite snapshot history.
- `data/backups/` contains optional local SQLite backups when generated.
- `data/processed/market_brief.md` contains the Markdown market brief.
- `data/processed/review_queue.md` contains a local manual recommendation review worksheet when generated.
- `data/processed/outcome_review.md` contains a local recommendation outcome review report when generated.
- `data/processed/calibration_report.md` contains a local recommendation calibration report when generated.
- `data/processed/public_intel.json` contains versioned, derived public intelligence only, including aggregate recommendation outcome counts and review coverage but not outcome notes.
- `data/processed/site/index.html` is a local static dashboard preview.
- `data/processed/site_bundle/` contains an optional local bundle and zip for manual inspection.
- `data/processed/publish_handoff.md` contains the local manual publishing handoff report when generated.
- `data/processed/site_contract.json` contains a local derived-only static-site handoff contract when generated.
- `data/processed/exile_ui_stash_ninja_watchlist.json` and `.md` are optional local companion handoffs for manual Stash-Ninja review; they are not site-bundle inputs.

Use `wq restore-helper --backup-path <file>` before restoring a local SQLite backup. The command is read-only: it verifies backup structure and prints the manual PowerShell copy command, but it does not replace `data/wraeclast_quant.db` for you. The backup and restore-helper contract is documented in `docs/BACKUPS.md`.

## Local Scheduling

Use `wq schedule-helper --sample-data` or `wq schedule-helper --input-path <file>` to print Windows Task Scheduler guidance for `wq daily`. The helper validates inputs and prints copy-pasteable commands, but it does not create scheduled tasks, install a service, run in the background, or execute the daily pipeline.

## Autonomous Project Work

Codex agents should follow `AGENTS.md` for project guardrails. When Goal Mode is available, `docs/GOAL_MODE.md` provides a short pasteable goal plus the longer local operating loop for autonomous packet-by-packet work.

The autonomous loop is still bounded: it should choose the highest-impact unblocked local task, work in one small packet at a time, preserve local-first/source-compliance boundaries, and stop for decisions that affect architecture, data model, public APIs, security, source approval, persistence, pricing, or user experience.

## Resource Configuration

`RESOURCES.md` is the source of truth for configured resources. The loader is intentionally tolerant and supports loose Markdown headings, bullets, links, metadata blocks, and simple tables. Missing metadata is filled with safe defaults. See `docs/RESOURCE_CONFIGURATION.md` for the parser contract.

Run `wq preflight` before planning any source-specific connector. API/RSS resources need explicit URLs and clear allowed use, Discord remains compliance-gated, and all collectors stay dry-run placeholders until a connector is explicitly approved.

Future live connectors must follow `docs/CONNECTOR_POLICY.md` and complete the current machine-readable source review workflow before any scraping, API fetching, Discord collection, or publishing work begins. Start from `wq connector-review-prep`, `wq connector-draft`, or `examples/connector_review_template.json`, then record manually reviewed evidence before `wq connector-check` and `wq connector-plan`.

Use `wq connector-candidates` to see which configured resources are worth reviewing first. The safe workflow is `wq preflight`, `wq connector-candidates`, `wq connector-review-prep`, manual human review, `wq connector-review-evidence`, `wq connector-review-status`, `wq connector-review-report`, `wq connector-approval-helper`, `wq connector-approval-patch`, manual `RESOURCES.md` approval edit if appropriate, `wq connector-check`, then `wq connector-plan`.

Machine-readable connector reviews can start from `wq connector-review-prep --resource <id-or-name> --access-method api`, `wq connector-draft --resource <id-or-name> --access-method api --output-path <file>`, `examples/connector_review_template.json`, or the API/RSS/download examples in `examples/`. Prep writes both a conservative JSON draft and a Markdown checklist. Drafts are intentionally not approval; manually review source terms and API/robots policy, then record the reviewed URLs, review date, notes, and allowed data shape before running `wq connector-check --review-path <file>`. Evidence fields may be empty in drafts, but reviewed URLs, review date, and allowed data shape are required before `connector-check` can pass.

Use `wq connector-review-status --review-path <file>` while editing a draft to inspect missing confirmations, evidence fields, and blockers. The command is read-only and may exit successfully for not-ready reviews so you can use it as a checklist.

Use `wq connector-review-evidence --review-path <file>` after manually reviewing source terms and API/robots policy. The command updates only the local JSON review file from values you provide; it does not browse URLs, verify source terms, edit `RESOURCES.md`, approve a source, or fetch data.

For sources where useful public pages or community notes exist but official automation terms are still unclear, keep research notes separate from completed evidence. For poe.ninja currency, `examples/reviews/poe_ninja_poe2_currency_research.md` records reviewed evidence, remaining gaps around the exact POE2 endpoint/field contract, and the narrow derived-only data shape used for local fixture proof.

Use `wq connector-approval-helper --review-path <file>` after the review evidence is complete to see whether a manual `RESOURCES.md` change such as `allowed_use: api` is appropriate. The helper does not edit files or approve a source by itself.

Use `wq connector-approval-patch --review-path <file> --output-path <file>` only after the helper says an approval change is appropriate. It writes a local unified diff preview and does not edit `RESOURCES.md`; the user still applies any approval change manually.

Use `wq connector-fixture-run --review-path <file> --fixture-path <file>` to test a future connector's derived output shape against a local JSON fixture. The runner is local-only, uses synthetic fixture data, performs no network requests, and writes no cache files.

Use `wq connector-dry-run --review-path <file> --fixture-path <file>` to exercise the future source-connector interface against the same local fixture. It prints the connector class, normalized rows, and future cache path without collecting live data.

Use `wq connector-fixture-export --review-path <file> --fixture-path <file> --output-path <file>` when a local fixture includes normalized `signals` for every row. The command writes manual-import-compatible JSON that can be checked with `wq validate-import --input-path <file>` or used by `wq import` and `wq daily --input-path`. It does not create snapshots, fetch data, or infer scores from raw prices.

Use `wq connector-fixture-daily --review-path <file> --fixture-path <file>` to run the existing local daily pipeline directly from a normalized-signal fixture. It creates one SQLite run with `source_mode="connector-fixture"`, writes the market brief, public intel JSON, and static dashboard, and previews local alert candidates without any network access.

After a review passes, use `wq connector-plan --review-path <file>` to preview the local cache path, cache TTL, and request spacing a future connector would use. This command is read-only and performs no network requests.

Use `wq currency-exchange-manual-snapshot --input-path examples/pathofexile_currency_exchange_manual_snapshot_template.json` to validate local official Currency Exchange observations. Add `--history-path <previous-snapshot>` to preview rolling-baseline diagnostics from a prior local observation, and add `--output-fixture-path <file>` to write connector-fixture JSON for local review. That fixture can then be passed to `wq connector-fixture-export` and `wq validate-import` before any manual scoring import or `wq daily --input-path` run. This path does not use OAuth, read credentials, call live HTTP, create raw caches, write snapshots, or publish artifacts.

Use `wq currency-exchange-ui-observation --input-path examples/pathofexile_currency_exchange_ui_observation_template.json --output-path <manual-import-output> --review-notes-output-path data/processed/ui_observation_review.md` when the user manually transcribes visible in-game Currency Exchange rows rather than API-shaped hourly fields. The UI observation file records league, want/have currencies, visible market ratios, stock-ladder rows, and optional no-stock observations. The command writes conservative manual-import-compatible signals directly from visible UI data, and the optional sidecar writes a local Markdown summary for human outcome review; it does not use OAuth, read credentials, call live HTTP, scrape or OCR screenshots, create snapshots, approve a source, record outcomes, or publish artifacts. Validate the output with `wq validate-import --input-path <manual-import-output>` before `wq daily --input-path <manual-import-output>`.

## Safety Boundary

Collectors remain dry-run placeholders unless a compliant source-specific connector is explicitly approved. Wraeclast Quant is decision support only: it may produce research, alerts, watchlists, local dashboards, and recommendations for manual review, but the user must manually execute all trades.

Do not use this project to automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, CAPTCHAs, login walls, private messages, or source-term bypasses.

## Development

```powershell
pytest
```
