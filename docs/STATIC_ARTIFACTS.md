# Static Artifact Contract

Wraeclast Quant can turn local derived intelligence into a static dashboard preview and an optional local site bundle. These artifacts are local files only. They do not publish, host, fetch, scrape, call webhooks, post to Discord, or interact with the game client.

## Commands

```powershell
wq site
wq site-bundle
wq publish-check
wq publish-handoff
wq site-contract
wq status
```

`wq site` reads a validated `public_intel.json` payload and writes `data/processed/site/index.html`.

`wq site-bundle` validates `public_intel.json`, copies the static dashboard and JSON export into `data/processed/site_bundle/`, writes `manifest.json`, and creates `wraeclast_quant_site_bundle.zip` for manual inspection.

Local review worksheets such as `data/processed/review_queue.md` are not site-bundle inputs and must stay out of `data/processed/site_bundle/` and `wraeclast_quant_site_bundle.zip`.

Local companion handoffs such as `data/processed/exile_ui_stash_ninja_watchlist.json` and `.md` are also not site-bundle inputs. They are for manual local review only and must stay out of public static handoff bundles.

`wq publish-check` verifies that the bundle is valid, derived-only, contract-compliant, and fresh against the latest SQLite run.

`wq publish-handoff` writes `data/processed/publish_handoff.md` with readiness evidence, blockers if present, archive details, bundled file names, and a manual publishing checklist. It does not upload, host, publish, or make network requests.

`wq site-contract` writes `data/processed/site_contract.json`, a versioned local descriptor of the static-site handoff contract. It summarizes artifact run IDs, bundle metadata, required files, publish readiness, blockers, and the derived-only safety boundary.

`wq status` checks the generated static site and bundle metadata without writing files.

The safe manual handoff flow is:

```powershell
wq export
wq site
wq site-bundle
wq publish-check
wq publish-handoff
wq site-contract
```

Any external publishing remains a manual action outside Wraeclast Quant.

## Static Site Markers

The generated `index.html` should include these health markers:

- `title`
- `heading`
- `schema-version`
- `generated-at`
- `latest-run-id`

These markers let `wq status` verify that the local dashboard looks like a Wraeclast Quant artifact and includes enough metadata for local inspection.

## Bundle Manifest Keys

The generated `manifest.json` must include:

- `generated_at`
- `product`
- `bundle_type`
- `derived_only`
- `network_behavior`
- `public_intel_schema_version`
- `public_intel_latest_run_id`
- `public_intel_top_opportunities`
- `public_intel_alerts`
- `files`
- `safety`

Important manifest values:

- `product` must be `Wraeclast Quant`.
- `bundle_type` is `local-static-preview`.
- `derived_only` must be `true`.
- `network_behavior` must be `none`.
- `files` lists bundled file names and sizes only, not local source paths.

## Bundle Archive Members

The generated zip archive must include:

- `index.html`
- `manifest.json`
- `public_intel.json`

The archive and publish handoff report are local handoff artifacts. They are not uploaded or published by Wraeclast Quant.

## Site Contract Descriptor

The generated `site_contract.json` uses schema version `1.0`.

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

The descriptor is for future static-site and manual publishing handoff work. It does not change the `public_intel.json` contract, which remains version `1.0`.

## Derived-Only Rules

Static artifacts may include derived fields from `public_intel.json`: item names, scores, actions, deltas, alert reasons, run metadata, aggregate compliance counts, and aggregate review counts.

They must not include raw source pages, raw signal inputs, resource notes, full source inventories, private data, secrets, cookies, tokens, API keys, credentials, `.env` values, or manual outcome notes.

Local review worksheets and Stash-Ninja companion watchlists are for the manual feedback loop only. They are not public site artifacts and must not be bundled for static handoff.

## Safety Notes

Static artifact generation is local-only. It must not automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, scraping, Discord collection, webhooks, publishing, hosting, or source-term bypasses.
