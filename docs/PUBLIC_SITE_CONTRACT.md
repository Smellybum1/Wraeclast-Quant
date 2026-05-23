# Public Site Contract

`wq site-contract` writes `data/processed/site_contract.json`, a local, derived-only descriptor for future static-site handoff work.

The command reads the current SQLite snapshot state and the existing local site bundle, then reuses `wq publish-check` readiness rules. It does not create snapshots, regenerate public intel, rebuild the dashboard, upload files, host a site, make network requests, scrape sources, approve sources, or interact with the game client.

## Command

```powershell
wq site-contract
```

Useful options:

- `--database-path`: SQLite snapshot database, default `data/wraeclast_quant.db`.
- `--bundle-dir`: local site bundle directory, default `data/processed/site_bundle`.
- `--output-path`: contract JSON path, default `data/processed/site_contract.json`.
- `--strict`: exit nonzero when the bundle is not ready.

## Contract Fields

The current site contract schema version is `1.0`.

Top-level keys:

- `schema_version`
- `generated_at`
- `product`
- `latest_database_run_id`
- `artifact_run_ids`
- `public_intel`
- `static_site`
- `bundle`
- `required_bundle_files`
- `publish_readiness`
- `safety`

`public_intel.json` remains its own contract at schema version `1.0`; `site_contract.json` only summarizes the static-site handoff state around it.

## Safety Boundary

The site contract may include run IDs, schema versions, bundle file names, artifact sizes, readiness checks, and blockers.

It must not include raw source pages, raw signal inputs, resource notes, full source inventories, private data, secrets, cookies, tokens, API keys, credentials, `.env` values, manual outcome notes, or raw `RESOURCES.md` content.

The site contract is not a publisher. Any external publishing remains a manual action outside Wraeclast Quant.
