# Manual Import Contract

Manual import is the safe local path for using real Wraeclast Quant data before any live collectors exist. It accepts normalized user-provided item signal scores, ranks them with the deterministic scorer, and can persist a local SQLite snapshot when used through `wq import` or `wq daily --input-path`.

Manual import never scrapes, fetches network resources, publishes data, sends alerts, posts to Discord, or interacts with the game client.

## Commands

```powershell
wq validate-import --input-path <file>
wq inspect-import --input-path <file>
wq import --input-path <file>
wq daily --input-path <file>
```

- `validate-import` is read-only and checks that the file can be loaded and scored.
- `inspect-import` is read-only and prints score and signal diagnostics.
- `import` scores the file and records one `manual-import` analysis run.
- `daily --input-path` runs the full local pipeline from the file using the contract documented in `docs/DAILY_PIPELINE.md`.

## Supported Files

Manual import supports:

- `.json`
- `.csv`

Files are read as UTF-8 and may include a UTF-8 BOM. Unsupported extensions fail before any snapshot is written.

## JSON Shape

JSON may be either a list of item objects or an object with an `items` list.

```json
[
  {
    "name": "Stormglass Catalyst",
    "signals": {
      "demand_momentum": 88,
      "build_dependency_score": 82,
      "price_discount_score": 76,
      "liquidity_score": 70,
      "historical_spike_score": 68,
      "patch_relevance_score": 74,
      "manipulation_risk": 18,
      "stale_data_penalty": 8
    }
  }
]
```

## CSV Shape

CSV must include a `name` column plus every required signal column:

```csv
name,demand_momentum,build_dependency_score,price_discount_score,liquidity_score,historical_spike_score,patch_relevance_score,manipulation_risk,stale_data_penalty
Stormglass Catalyst,88,82,76,70,68,74,18,8
```

## Required Signals

Each item must include:

- `demand_momentum`
- `build_dependency_score`
- `price_discount_score`
- `liquidity_score`
- `historical_spike_score`
- `patch_relevance_score`
- `manipulation_risk`
- `stale_data_penalty`

Signal values must be numeric and between `0` and `100`, inclusive.

## Templates

Starter templates:

- `examples/manual_import_template.json`
- `examples/manual_import_template.csv`

Use `wq validate-import --input-path <file>` before persisting a new manual snapshot.

## Currency Exchange Manual Snapshots

Official Currency Exchange manual snapshots are a source-specific local intake path, not the normalized manual-import format above. Use this path when OAuth/live API access is parked and the user supplies local hourly observations:

```powershell
wq currency-exchange-manual-snapshot --input-path examples/pathofexile_currency_exchange_manual_snapshot_template.json
wq currency-exchange-manual-snapshot --input-path <current-snapshot> --history-path <previous-snapshot> --output-fixture-path <fixture-output>
```

The command validates a local Currency Exchange snapshot, previews derived connector-fixture rows, and can write connector-fixture JSON only when `--output-fixture-path` is supplied. Use `wq connector-fixture-export --fixture-path <fixture-output> --output-path <manual-import-output>` to convert the fixture into the normalized manual-import shape, then `wq validate-import --input-path <manual-import-output>` before any scoring import or `wq daily --input-path` run. It does not run `wq import`, create SQLite snapshots, fetch live data, read OAuth credentials, write raw caches, or publish artifacts.

Each Currency Exchange manual snapshot has:

- `next_change_id`
- `markets`

Each Currency Exchange manual market has:

- `league`
- `left_currency`
- `right_currency`
- `left_volume_traded`
- `right_volume_traded`
- `left_lowest_stock`
- `right_lowest_stock`
- `left_highest_stock`
- `right_highest_stock`
- `left_lowest_ratio`
- `right_lowest_ratio`
- `left_highest_ratio`
- `right_highest_ratio`

Currency names are normalized to lowercase underscore codes before fixture conversion, so either `divine` or `Divine Orb` can be used in local manual observations.

## Currency Exchange UI Observations

Currency Exchange UI observations are a separate local intake path for manually transcribed in-game ratio and stock-ladder rows when API-shaped hourly fields are not available:

```powershell
wq currency-exchange-ui-observation --input-path examples/pathofexile_currency_exchange_ui_observation_template.json --output-path <manual-import-output> --review-notes-output-path data/processed/ui_observation_review.md
wq validate-import --input-path <manual-import-output>
wq daily --input-path <manual-import-output>
```

The UI observation command writes normal manual-import JSON using conservative derived signals from visible UI data only. The optional review-notes sidecar is a local Markdown summary of the transcribed ratios, visible stock rows, and capture review flags for human outcome review. It calls out ratio-only captures, No Stock rows, missing stock ladders, and missing order-entry ratios before those observations are used for outcome review. It does not use OAuth, read credentials, call live HTTP, scrape or OCR screenshots, create SQLite snapshots, approve a source, record outcomes, or publish artifacts.

UI observation JSON has:

- `league`
- optional `observed_at`
- `observations`

Each observation has:

- `want_currency`
- `have_currency`
- optional `market_ratio`, either `"30:1"` or `{"want": 30, "have": 1}`
- optional `stock_rows`
- optional `no_stock`
- optional `notes`

Each stock row has:

- `ratio`, either `"30:1"` or `{"want": 30, "have": 1}`
- `stock`
- optional `comparator`: `exact`, `less_than`, or `greater_than`

## Safety Notes

Manual import files remain user-owned local inputs. Wraeclast Quant does not rewrite, move, normalize in place, or delete them.

Manual import is decision support only. It must not automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, scraping, Discord collection, webhooks, publishing, hosting, or source-term bypasses.
