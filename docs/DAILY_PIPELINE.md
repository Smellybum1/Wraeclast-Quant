# Daily Pipeline Contract

`wq daily` is Wraeclast Quant's local daily-driver command. It runs the existing local pipeline once from either built-in sample data or a user-provided manual import file.

It is orchestration only. It is not a daemon, scheduler, scraper, publisher, webhook sender, Discord bot, server, or game automation tool.

`wq connector-fixture-daily` reuses the same local pipeline from a reviewed synthetic connector fixture with normalized signals. It is a fixture-backed proof path only, not live ingestion.

## Commands

```powershell
wq daily --sample-data
wq daily --input-path <file>
wq daily --input-path <file> --stash-ninja-watchlist
wq connector-fixture-daily --review-path <file> --fixture-path <file>
```

For `wq daily`, exactly one input mode is required:

- `--sample-data`
- `--input-path <file>`

Passing both fails. Passing neither fails.

## Flow

One daily run:

1. Loads sample items or a local manual import file.
2. Scores opportunities with the deterministic scoring contract.
3. Creates exactly one SQLite analysis run.
4. Saves scored opportunities for that run.
5. Records local run provenance for manual-import daily runs using path-safe metadata.
6. Compares the new run against the previous run when one exists.
7. Writes the delta-aware Markdown market brief.
8. Records the market brief as a report artifact.
9. Builds and writes derived-only `public_intel.json`.
10. Renders the local static dashboard from the same public intel payload.
11. Optionally writes a derived-only Stash-Ninja companion handoff when `--stash-ninja-watchlist` is passed.
12. Prints local alert candidates when a comparison exists.

Daily does not call other CLI commands internally. It reuses lower-level scoring, storage, report, export, site, and alert functions so one run id is used consistently across artifacts.

Manual-import daily runs record local provenance with the input file name, suffix, relative path when one was supplied, redacted absolute-path metadata when needed, file size, SHA-256 hash, item count, and explicit `live_collection=false` / `source_approval=false` flags. Connector fixture daily uses the shared workflow after connector review/check and fetch-plan readiness pass. It records `source_mode="connector-fixture"` and local provenance for the created run, then writes the same market brief, public intel, static dashboard, and alert preview artifacts from that run.

## Default Paths

- `database_path`: `data/wraeclast_quant.db`
- `resources_path`: `RESOURCES.md`
- `brief_path`: `data/processed/market_brief.md`
- `intel_path`: `data/processed/public_intel.json`
- `site_dir`: `data/processed/site`
- `stash_ninja_path`: `data/processed/exile_ui_stash_ninja_watchlist.json`

The Stash-Ninja handoff is opt-in for daily runs. When `--stash-ninja-watchlist` is passed, the command also writes JSON and Markdown companion files for the created run. They are local manual handoffs only and do not write Exile-UI files, call live HTTP, include raw signals, or interact with the game client.

## Printed Output Labels

Successful daily runs print these output labels:

- `Database`
- `Market brief`
- `Public intel`
- `Dashboard`

The command also prints the completed daily run id.

Manual-import daily runs also print the matching `wq run-provenance --database-path <database> --run-id <id>` and `wq review-coverage --database-path <database> --run-id <id>` next actions for the created run.

When `--stash-ninja-watchlist` is passed, the command also prints `Stash-Ninja handoff` and `Stash-Ninja handoff Markdown` output paths.

## Alert Settings

Daily accepts the same local alert tuning options as `wq alerts` and `wq export`:

- `--watch-threshold`
- `--buy-threshold`
- `--big-delta`

Alert candidates remain local preview output only.

## Safety Notes

`wq daily` may write local SQLite snapshots and local generated artifacts at the configured paths.

`wq connector-fixture-daily` may read only the local review and fixture files, then write local SQLite snapshots and generated artifacts at configured paths.

Neither command may scrape, fetch live resources, publish, host a website, send Discord messages, call webhooks, send email, run continuously, install scheduled tasks, automate gameplay, perform trades, send whispers, click UI, move characters, or interact with the game client.
