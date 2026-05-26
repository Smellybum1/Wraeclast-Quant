# Path of Exile Currency Exchange Rolling Baseline Policy

This note records the chosen direction for future official Currency Exchange preview scoring. It does not approve live collection, OAuth, credential storage, cache writes, schema changes, snapshots, manual-import export, daily pipeline wiring, public artifacts, or recommendation scoring.

## Decision

Use a rolling local baseline before promoting official Currency Exchange API signals.

The current fixture-only preview policy scores liquidity and demand relative to a single hourly payload. That is useful for shape testing, but it is too sensitive to which markets happen to be present. A rolling local baseline should compare each market against its own recent local history before any score can influence recommendations.

Fixed thresholds may still be used as guardrails, but not as the primary scoring policy.

## Baseline Scope

- Partition baselines by `source_id`, league, and `market_id`.
- Treat each hourly aggregate payload as one observation per market.
- Keep raw payload handling separate from derived baseline rows.
- Do not combine leagues, realm variants, or patch eras unless a later reviewed packet defines the rule.
- Do not derive build, patch, historical spike, or price-discount scores from Currency Exchange data alone.

## Required Observation Fields

Future local baseline observations should derive only these aggregate fields unless a later review approves more:

- Capture time and source payload `next_change_id`.
- League and `market_id`.
- Total `volume_traded`.
- Total `highest_stock`.
- Ratio spread from `lowest_ratio` and `highest_ratio`.
- Optional local freshness age derived from capture time and `next_change_id`.

## Candidate Rolling Metrics

The first implementation should stay preview-only and produce explainable diagnostics:

- Demand momentum: current total volume versus the market's rolling median or percentile band.
- Liquidity score: blend of current volume and stock versus the market's own rolling baseline.
- Manipulation risk: blend of low liquidity, elevated spread versus baseline, and thin sample count.
- Stale-data penalty: age-based penalty from capture time and expected hourly cadence.
- Confidence: sample-count and freshness label used to block promotion when the baseline is too thin.

## Minimum Promotion Gates

Before any Currency Exchange signal reaches import, daily, snapshots, public intel, static site, or recommendation scoring:

- Source approval, OAuth/app-registration, user-agent/contact, rate/backoff, cache, and failure-closed behavior must be explicitly approved.
- Baseline storage or cache format must be reviewed before implementation.
- A fresh local backup and migration-readiness check are required before any schema change.
- Preview baseline tests must cover empty history, insufficient history, stable/liquid markets, thin/high-spread markets, broad payload sensitivity, stale captures, and league separation.
- Neutral placeholder signals must remain excluded from recommendation scoring unless real evidence exists.
- Public artifacts must remain derived-only and exclude raw source payloads.

## Fixed Threshold Guardrails

Fixed thresholds are allowed only as conservative blockers or warning labels, for example:

- Too few local observations to score.
- Capture is older than the expected hourly cadence plus a reviewed tolerance.
- Spread is extreme even after baseline comparison.
- Current volume or stock is too low for a confident recommendation.

These guardrails should lower confidence or block scoring; they should not become the main source of demand or liquidity scores.

## Next Implementation Packet

The fixture-only baseline prototype is implemented as `preview_currency_exchange_rolling_baseline_diagnostics`. It accepts synthetic local payload history, calculates preview diagnostics, blocks markets with insufficient local history, and proves that adding unrelated high-volume markets does not materially change a market's own demand/liquidity diagnostics.

It does not write caches, edit schemas, call live HTTP, export manual-import rows, create snapshots, or wire any output into recommendations.

## Prototype Findings

- The prototype partitions history by league and `market_id`.
- The same `chaos|divine` row produces identical demand, liquidity, and spread diagnostics in the narrow and broad current payloads when compared to the same local history.
- A broad-payload market with no local history, such as `chaos|regal`, is blocked with `insufficient local baseline history`.
- A thin/high-spread `chaos|divine` current payload compared to the local baseline produces `0.46` demand index, `0.98` liquidity index, and `100.0` spread index.
- Freshness diagnostics use `next_change_id` cadence only. By default, a current payload up to two expected hourly intervals after the latest local baseline observation is `fresh`; older payloads are warnings with stale penalties, and out-of-order captures are warnings with a stronger penalty.
- League separation and configurable minimum history are covered by fixture-only regressions: same `market_id` in another league is blocked until that league has local history, and `min_observations` prevents thin baselines from becoming preview diagnostics.
- The prototype remains diagnostic-only and is not a scoring or recommendation policy.

## Next Safe Packet

The growing fixture-only Currency Exchange prototype has been split behind the stable `wraeclast_quant.collectors.pathofexile_currency_exchange` facade into focused model, fixture, metric, signal-preview, and baseline-preview helpers.

The source is approved for API planning in `RESOURCES.md`, and cache/storage planning is documented in `examples/reviews/pathofexile_currency_exchange_cache_storage_policy.md`. The preview path still stays local and must not write cache files, change schemas, call live HTTP, or feed recommendations until those implementation packets are explicitly built and verified.
