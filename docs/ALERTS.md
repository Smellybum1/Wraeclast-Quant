# Alert Rules Contract

Wraeclast Quant alert candidates are local preview signals derived from snapshot comparisons. They are not notifications, trade instructions, Discord posts, webhooks, or game actions.

## Commands

```powershell
wq alerts
wq export
wq daily --sample-data
wq daily --input-path <file>
```

`wq alerts` prints local alert candidates from the latest-versus-previous snapshot comparison.

`wq export` includes alert candidates in `public_intel.json`.

`wq daily` prints alert candidates after it records one local run and compares it with the previous run.

## Default Settings

Default alert settings:

- `watch_threshold`: `55.0`
- `buy_threshold`: `75.0`
- `big_positive_delta`: `10.0`

CLI options:

- `--watch-threshold`
- `--buy-threshold`
- `--big-delta`

Thresholds must be between `0` and `100`, inclusive. `buy_threshold` must be greater than or equal to `watch_threshold`.

## Rules

Alert reasons:

- `Score crossed into BUY`
- `Score crossed into WATCH`
- `New WATCH-or-better item`
- `Action changed upward`
- `Score increased by at least +<big_positive_delta>`

Severity rules:

- `Score crossed into BUY`: `high`
- all other alert candidates: `medium`

The BUY threshold check takes priority over the WATCH threshold check for the same item movement. Duplicate alerts with the same item name and reason are suppressed.

## Local-Only Boundary

Alert candidates are displayed locally and may be included as derived data in `public_intel.json` and the static dashboard preview. They are not delivered externally.

The alert system must not send Discord messages, email, webhooks, desktop notifications, whispers, trades, game inputs, clicks, movement, or game-client interactions. It must not scrape, fetch network resources, bypass source terms, or publish artifacts.
