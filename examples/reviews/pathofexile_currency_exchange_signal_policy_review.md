# Path of Exile Currency Exchange Preview Signal Policy Review

This review evaluates the preview signal policy only. It does not approve source access, OAuth, live HTTP, cache writes, snapshots, manual-import export, daily pipeline wiring, public artifacts, or recommendation scoring from the official Currency Exchange API.

## Verdict

Keep the policy preview-only. It is useful for inspecting whether the official hourly aggregate fields can produce deterministic candidate `OpportunityInputs`, but it is not ready to drive recommendations.

## What Looks Good

- The policy is deterministic and local-only.
- It uses only documented aggregate fields from the fixture: `volume_traded`, `highest_stock`, `lowest_ratio`, and `highest_ratio`.
- It avoids inventing build, patch, historical, and discount evidence by keeping those fields neutral at `50.0`.
- It keeps connector rows unwired with `signals=None`, so existing export, daily, and scoring paths cannot accidentally consume it.

## Blocking Risks Before Wiring

- Relative scoring is scoped to one payload, so the same market can receive different demand/liquidity scores depending on which other markets are present.
- A single hourly payload cannot establish trend, discount, or historical-spike context.
- Neutral `50.0` placeholders may still materially affect the weighted score if wired into recommendations.
- The fixed `20.0` stale-data penalty is conservative, but it is not tied to actual capture age or current-hour availability.
- Ratio spread is only a first-pass manipulation-risk proxy and needs more fixtures before use.

## Fixture Stability Findings

- Additional fixtures now cover a thin/high-spread market and a broader multi-market payload.
- In the thin fixture, `chaos|divine` produces `1.72` demand momentum, `2.15` liquidity, and `70.38` manipulation risk, while the liquid reference market stays at `100.0` demand, `100.0` liquidity, and `1.74` manipulation risk.
- In the broad fixture, the same `chaos|divine` row drops from `100.0` demand momentum in the narrow payload to `42.31`, and from `92.53` liquidity to `33.75`.
- The fixture comparison confirms that the current relative policy can surface thin-market risk, but production scoring needs either a rolling local baseline or explicit fixed thresholds before signal promotion.

## Baseline Decision

Use a rolling local baseline before any signal promotion. Fixed thresholds may still be used as conservative blockers or warning labels, but they should not be the main source of demand or liquidity scoring. See `examples/reviews/pathofexile_currency_exchange_rolling_baseline_policy.md`.

## Rolling Baseline Prototype Findings

- `preview_currency_exchange_rolling_baseline_diagnostics` is fixture-only and diagnostic-only.
- It compares each market against local history partitioned by league and `market_id`, so unrelated high-volume markets do not change an existing market's own demand, liquidity, or spread diagnostics.
- It blocks markets with no local baseline history instead of assigning them recommendation-ready scores.
- It surfaces thin/high-spread current conditions against local history without wiring those diagnostics into `OpportunityInputs`.
- It now reports `next_change_id` cadence diagnostics: fresh lag, stale warnings, out-of-order capture warnings, and diagnostic-only stale penalties.
- It has fixture-only coverage for league separation and `min_observations`, so cross-league history and thin local baselines stay blocked.
- It has a preview-only conversion path for unblocked rolling-baseline diagnostics into normalized `OpportunityInputs`; blocked or warning diagnostics keep `signals=None`.

## Required Before Promotion

- Define local capture-time behavior if a future approved connector records capture timestamps in addition to source `next_change_id`.
- Decide whether neutral placeholder signals should be allowed in scored recommendations or kept out until real evidence exists.
- Keep public artifacts derived-only and exclude raw payloads.

## Recommendation

Do not wire these preview signals or baseline diagnostics into `connector-fixture-export`, `wq import`, `wq daily`, snapshots, public intel, or static dashboards yet. The next packet that changes live access, cache writes, schema, or scoring must preserve the gates in `examples/reviews/pathofexile_currency_exchange_cache_storage_policy.md`.
