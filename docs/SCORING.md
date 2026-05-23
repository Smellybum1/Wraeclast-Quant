# Scoring Contract

Wraeclast Quant scores normalized item signals with a deterministic local formula. Scores are decision-support signals only; they are not trading instructions and they do not automate any game action.

## Input Range

Each signal must be numeric and between `0` and `100`, inclusive. Manual imports validate this through the same `OpportunityInputs` model used by the scorer.

## Signal Weights

The opportunity score uses these weighted signals:

- `demand_momentum`: `+0.20`
- `build_dependency_score`: `+0.20`
- `price_discount_score`: `+0.20`
- `liquidity_score`: `+0.15`
- `historical_spike_score`: `+0.10`
- `patch_relevance_score`: `+0.10`
- `manipulation_risk`: `-0.15`
- `stale_data_penalty`: `-0.10`

Formula:

```text
opportunity_score =
  demand_momentum * 0.20
  + build_dependency_score * 0.20
  + price_discount_score * 0.20
  + liquidity_score * 0.15
  + historical_spike_score * 0.10
  + patch_relevance_score * 0.10
  - manipulation_risk * 0.15
  - stale_data_penalty * 0.10
```

The final score is clamped to the `0-100` range and rounded to two decimal places.

## Action Thresholds

Scores map to actions as follows:

- `BUY`: `>= 75`
- `WATCH`: `>= 55`
- `HOLD / SELL SELECTIVELY`: `>= 35`
- `AVOID`: `< 35`

These labels are recommendations for manual review only. The user decides whether to trade, and all trades must be executed manually.

## Safety Notes

Scoring is local and deterministic. It must not fetch live data, scrape, publish, post alerts, send whispers, automate trading, click UI, move characters, or interact with the game client.
