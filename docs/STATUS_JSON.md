# Status JSON Contract

`wq status --json` prints a versioned, machine-readable local health summary for Wraeclast Quant. It is intended for local automation, scheduler wrappers, and manual diagnostics that need stable keys instead of Rich table text.

The command is read-only. It does not create snapshots, mutate SQLite data, fetch network resources, publish artifacts, send alerts, or interact with the game client.

## Commands

```powershell
wq status --json
wq status --strict --json
```

`--strict` keeps the same JSON shape and sets `strict` to `true`. In strict mode, rows with status `needs attention` are also returned in `strict_failures` and `strict_failure_keys`, and the CLI exits nonzero.

## Current Schema

The current status JSON schema version is `1.5`.

Top-level fields:

- `schema_version`: status JSON contract version, currently `1.5`.
- `generated_at`: UTC ISO-8601 timestamp for the status payload.
- `product`: product name, currently `Wraeclast Quant`.
- `ok`: `true` when no status row needs attention.
- `strict`: `true` when `--strict` was passed.
- `strict_failures`: human-readable check labels for rows that need attention.
- `strict_failure_keys`: stable row keys for rows that need attention.
- `status_counts`: counts by normalized status value.
- `rows`: ordered list of status rows for display.
- `rows_by_key`: map of stable row key to row object.

Each row has this shape:

```json
{
  "key": "public_intel",
  "check": "Public intel",
  "status": "ok",
  "details": "data/processed/public_intel.json; schema 1.0; latest run 12"
}
```

Row fields:

- `key`: stable machine key.
- `check`: human-readable label.
- `status`: local health status.
- `details`: human-readable local diagnostic detail.

## Stable Row Keys

Current row keys:

- `resources`
- `database`
- `database_health`
- `latest_run`
- `review_coverage`
- `mvp_readiness`
- `calibration_prompts`
- `market_brief`
- `public_intel`
- `static_site`
- `site_bundle`
- `stash_ninja_handoff`
- `backups`
- `safety_boundary`

Consumers should prefer `rows_by_key` for lookups instead of matching `check` labels.

## Status Values

Current status values:

- `ok`
- `yes`
- `no`
- `none`
- `needs attention`

`status_counts` normalizes spaces to underscores, so `needs attention` appears as `needs_attention` in that count map.

Treat `needs attention` and non-empty `strict_failure_keys` as actionable. Missing optional local artifacts can appear as `no` or `none` without failing strict mode.

Existing derived artifacts are also checked for freshness. When a valid `public_intel.json`, static site, site bundle, or Stash-Ninja companion handoff reports a latest run id that differs from the latest SQLite run id, the matching row is marked `needs attention` with guidance to regenerate the local artifact. Missing optional artifacts remain non-fatal.

## Compatibility Rules

- Check `schema_version` before assuming field behavior.
- Use `rows_by_key` and `strict_failure_keys` for automation decisions.
- Treat unknown top-level fields as additive.
- Treat unknown row keys as additive.
- Do not parse file paths, counts, or run ids out of `details` when a structured field already exists.

Future schema versions may add rows or fields. Breaking changes should bump `schema_version`.

## Safety Notes

The status payload is derived from local files and local SQLite metadata. It should not include secrets, cookies, tokens, API keys, `.env` values, raw source data, or raw `RESOURCES.md` content.

`wq status --json` is a diagnostic contract only. It must not be used to automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, source-term bypasses, Discord collection, webhooks, or publishing.
