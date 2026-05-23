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

## Safety Notes

Manual import files remain user-owned local inputs. Wraeclast Quant does not rewrite, move, normalize in place, or delete them.

Manual import is decision support only. It must not automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, scraping, Discord collection, webhooks, publishing, hosting, or source-term bypasses.
