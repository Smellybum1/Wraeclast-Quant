# Snapshot Comparison Contract

Wraeclast Quant compares persisted analysis runs locally so reports, alert previews, public intel exports, and the static dashboard can explain what changed between snapshots.

Snapshot comparison is read-only. It does not create snapshots, fetch data, scrape, publish, send alerts, or interact with the game client.

## Commands

```powershell
wq compare
wq alerts
wq report --sample-data
wq export
wq daily --sample-data
wq daily --input-path <file>
```

`wq compare` compares the latest run against the previous run by default.

`wq report`, `wq export`, and `wq daily` reuse the same comparison semantics when prior history exists.

## Identity Key

Items are matched by exact item name for the MVP.

## Delta Statuses

Each compared item has one status:

- `changed`
- `new`
- `removed`

`changed` means the item exists in both runs. Its score delta is `latest_score - previous_score`, rounded to two decimal places.

`new` means the item appears only in the latest run.

`removed` means the item appears only in the previous run.

## Delta Fields

Each delta may include:

- `item_name`
- `status`
- `previous_score`
- `latest_score`
- `score_delta`
- `previous_action`
- `latest_action`
- `action_changed`

For `new` items, previous score/action fields are empty.

For `removed` items, latest score/action fields are empty.

For `changed` items, `action_changed` is `true` when the previous and latest actions differ.

## Derived Views

`top_movers` includes changed items with a non-zero score delta. It is sorted by absolute score delta descending, then item name ascending.

`status_changes` includes:

- `new items`
- `removed items`
- `changed items where action_changed is true`

If there is no previous run, comparison commands should print a clear no-comparison message rather than inventing deltas.

## Safety Notes

Snapshot comparison is local decision support only. It must not automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, scraping, Discord collection, webhooks, publishing, hosting, or source-term bypasses.
