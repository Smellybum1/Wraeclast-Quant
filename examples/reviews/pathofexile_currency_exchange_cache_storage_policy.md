# Path of Exile Currency Exchange Cache And Storage Policy

This policy records the approved local direction for official Currency Exchange API planning. It does not add live HTTP, OAuth token exchange, credential storage, cache writes, schema changes, snapshots, daily pipeline wiring, or recommendation scoring.

## Source Approval

- Resource id: `official_currency_exchange_api`
- Approved `RESOURCES.md` use: `api`
- Required scope from source review: `service:cxapi`
- Live implementation status: blocked until OAuth/app-registration, user-agent/contact configuration, dynamic rate-limit handling, credential storage outside the repo, and failure-closed live-network tests are implemented.

## Cache Plan

The preview cache/storage plan is exposed by `preview_currency_exchange_storage_plan`.

- Raw cache path: `data/raw/cache/path-of-exile-currency-exchange-api-d9b59150fbb2.cache`
- Cache TTL: `3600s`
- Baseline observations preview path: `data/processed/currency_exchange/baseline_observations.preview.json`
- Baseline diagnostics preview path: `data/processed/currency_exchange/baseline_diagnostics.preview.json`
- Credentials and tokens must never be stored in these paths.
- The preview plan is read-only by default: `writes_enabled=false`.

## Baseline Storage Direction

When storage is later approved, store derived baseline observations separately from raw source payloads:

- `source_id`
- league
- `market_id`
- source `next_change_id`
- local capture timestamp
- total `volume_traded`
- total `highest_stock`
- ratio spread percentage

Raw source payloads should remain local-only cache material and must not appear in public artifacts.

## Preview Import Direction

`preview_currency_exchange_signal_fixture_from_baseline` converts unblocked rolling-baseline diagnostics into connector fixture rows with normalized `OpportunityInputs` for local inspection only.

- Rows with `confidence=preview` and no blockers may receive normalized signals.
- Rows with stale, out-of-order, missing-history, or insufficient-history diagnostics keep `signals=None`.
- Default `load_currency_exchange_connector_fixture` rows remain unwired with `signals=None`.
- No CLI command, daily run, snapshot, public intel, or static site consumes these preview rows automatically.

## Source-Specific Dry Run

`OfficialCurrencyExchangeConnector` is a source-specific dry-run connector for the approved API resource. It can convert local raw Currency Exchange fixtures into connector rows and expose the fetch/cache plan, but it still refuses live collection.

- Fixture rows remain unwired with `signals=None`.
- Fixture collection does not create `data/raw/cache`.
- Live collection reports blockers for OAuth token exchange, credential storage outside the repo, dynamic rate-limit parsing, and cache writes.

## Promotion Gates

Before live data or scoring integration:

- OAuth/app registration must be documented.
- User-agent/contact configuration must be explicit and non-secret.
- Secrets/tokens must live outside the repo.
- Cache writes must fail closed and obey response rate-limit headers.
- Storage schema changes require backup and migration-readiness checks.
- Preview rows must be manually reviewed before any daily/import/scoring integration.
