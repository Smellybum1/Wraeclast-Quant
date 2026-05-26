# Path of Exile Currency Exchange Preview Signal Policy

This is a preview-only policy for local shape testing. It does not approve live collection, edit `RESOURCES.md`, request OAuth access, store credentials, fetch data, write cache files, create snapshots, export manual-import files, or change recommendation scoring behavior.

## Status

- Resource id: `official_currency_exchange_api`
- Source fixture: `examples/pathofexile_currency_exchange_fixture.json`
- Parser/normalizer: `wraeclast_quant.collectors.pathofexile_currency_exchange`
- Policy status: preview-only
- Baseline direction: rolling local baseline before any signal promotion
- Live implementation status: `blocked`
- Review: `examples/reviews/pathofexile_currency_exchange_signal_policy_review.md`
- Rolling baseline handoff: `examples/reviews/pathofexile_currency_exchange_rolling_baseline_policy.md`
- Cache/storage handoff: `examples/reviews/pathofexile_currency_exchange_cache_storage_policy.md`

## Candidate Signals

The preview policy maps a single hourly Currency Exchange payload into candidate `OpportunityInputs` for inspection only:

- `demand_momentum`: relative total `volume_traded` versus the highest-volume market in the payload.
- `liquidity_score`: `70%` relative total volume plus `30%` relative highest stock.
- `manipulation_risk`: inverse liquidity plus average ratio spread.
- `build_dependency_score`: neutral `50.0`.
- `price_discount_score`: neutral `50.0`.
- `historical_spike_score`: neutral `50.0`.
- `patch_relevance_score`: neutral `50.0`.
- `stale_data_penalty`: conservative `20.0`, because the endpoint is hourly historical data rather than current-hour live market state.

## Guardrails

- The converter still emits `ConnectorFixtureItem` rows with `signals=None`.
- `preview_currency_exchange_signal_fixture_from_baseline` may create local preview rows with normalized signals only for unblocked rolling-baseline diagnostics.
- These candidate signals must not be used by `wq connector-fixture-export`, `wq import`, `wq daily`, snapshots, recommendations, public intel, or static dashboards until a later approved packet explicitly wires them in.
- A future preview packet should use a rolling local baseline, not single-payload relative scores, before any wiring is reconsidered.
- A future wiring packet must test the signal formulas against more than one fixture and clearly document how age, volume, stock, ratio spread, market pair, league, and baseline confidence affect recommendations.
- This policy should remain preview-only until the review blockers are resolved.
