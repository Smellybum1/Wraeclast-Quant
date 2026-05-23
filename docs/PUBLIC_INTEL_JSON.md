# Public Intel JSON Contract

`wq export` writes `data/processed/public_intel.json`, a local, derived-only JSON payload for Wraeclast Quant dashboard previews and future public-site work.

This contract is local-first. It does not scrape, fetch, publish, send alerts, call webhooks, run a server, or interact with the game client.

## Commands

```powershell
wq export
wq validate-intel
wq site
wq site-bundle
```

`wq validate-intel` checks an existing `public_intel.json` file against this derived-only contract. `wq site` and `wq site-bundle` also validate the contract before rendering or packaging local static artifacts.

## Current Schema

The current public intel schema version is `1.0`.

Required top-level fields:

- `schema_version`
- `generated_at`
- `latest_run`
- `recent_runs`
- `top_opportunities`
- `score_trends`
- `snapshot_changes`
- `alerts`
- `outcome_summary`
- `review_coverage`
- `compliance_summary`

## Field Summary

- `schema_version`: public intel contract version, currently `1.0`.
- `generated_at`: UTC ISO-8601 timestamp for the export.
- `latest_run`: latest analysis run metadata.
- `recent_runs`: recent analysis run metadata, capped by the command limit.
- `top_opportunities`: highest-scoring derived recommendations from the latest run.
- `score_trends`: recent per-run score/action points for top opportunity item names.
- `snapshot_changes`: latest-versus-previous run deltas.
- `alerts`: local alert candidates derived from snapshot comparisons.
- `outcome_summary`: aggregate manual outcome counts. The local outcome review contract is documented in `docs/OUTCOMES.md`.
- `review_coverage`: aggregate manual review coverage for the latest run.
- `compliance_summary`: aggregate resource compliance counts.

## Common Shapes

`latest_run` and each `recent_runs` entry include:

- `id`
- `created_at`
- `source_mode`
- `item_count`

Each `top_opportunities` entry includes:

- `item_name`
- `opportunity_score`
- `action`

Each `score_trends` entry includes:

- `item_name`
- `points`

Each trend point includes:

- `run_id`
- `score`
- `action`

`snapshot_changes` includes:

- `previous_run_id`
- `latest_run_id`
- `top_movers`
- `status_changes`

Each alert candidate may include:

- `severity`
- `item_name`
- `reason`
- `previous_score`
- `latest_score`
- `score_delta`
- `previous_action`
- `latest_action`

## Derived-Only Rules

The public intel payload may include derived fields such as item names, scores, actions, score deltas, alert reasons, run metadata, aggregate compliance counts, and aggregate review counts.

It must not include:

- raw signal `inputs`
- resource `notes`
- source URLs
- raw resource inventories
- raw source pages or private data
- secrets, cookies, tokens, API keys, credentials, or `.env` values
- manual outcome notes

The validator rejects raw/private field names such as `inputs`, `notes`, `url`, `urls`, `resources`, and `raw_resources`, and it rejects raw URLs in string values.

## Compatibility Rules

- Check `schema_version` before assuming field behavior.
- Treat unknown top-level fields as additive only after validation still passes.
- Use `latest_run.id`, `top_opportunities`, `snapshot_changes`, and `alerts` for dashboard or automation summaries instead of parsing rendered HTML.
- Do not assume `alerts`, `top_movers`, `status_changes`, or `score_trends` are non-empty.

Future schema versions may add fields. Breaking changes should bump `schema_version`.

## Safety Notes

`public_intel.json` is a local artifact and a future website contract, not a publisher. Creating or validating it must not perform network requests, scrape websites, post to Discord, send webhooks, automate gameplay, execute trades, send whispers, click UI, move characters, or interact with the game client.
