# MVP Daily Workflow

This is the local-first MVP loop for Wraeclast Quant. It uses user-supplied local observations, deterministic scoring, SQLite history, and derived-only local artifacts. It does not use OAuth, live HTTP, browser sessions, scraping, raw cache writes, publishing, or game-client interaction.

## Daily Loop

1. Prepare a local official Currency Exchange manual snapshot using `examples/pathofexile_currency_exchange_manual_snapshot_template.json` as the shape reference.
2. Validate and preview the observation:

```powershell
wq currency-exchange-manual-snapshot --input-path <current-snapshot>
```

3. When you have a previous local observation, export a connector fixture with preview rolling-baseline signals:

```powershell
wq currency-exchange-manual-snapshot --input-path <current-snapshot> --history-path <previous-snapshot> --output-fixture-path <fixture-output>
```

4. Convert the local fixture into normalized manual-import JSON:

```powershell
wq connector-fixture-export --review-path examples/reviews/pathofexile_currency_exchange_connector_review.json --fixture-path <fixture-output> --output-path <manual-import-output>
```

5. Validate the normalized input before recording a run:

```powershell
wq validate-import --input-path <manual-import-output>
```

6. Run the local daily pipeline:

```powershell
wq daily --input-path <manual-import-output>
```

7. Inspect health and review state:

```powershell
wq status --strict
wq review-queue
wq review-queue --output-path data/processed/review_queue.md
wq review-coverage
```

8. Record outcomes only after a human review decision:

```powershell
wq record-outcome --run-id <id> --item-name <name> --outcome positive|neutral|negative
```

## MVP Readiness

`wq status` includes an `MVP readiness` row. It summarizes whether the local no-OAuth loop has a latest run and points to the next manual action, usually a run-specific `wq review-queue --output-path data/processed/review_queue.md`, `wq record-outcome`, or the next `wq daily --input-path` run.

Before sharing or manually publishing static artifacts, run:

```powershell
wq publish-check
```

## Safety Notes

Public artifacts remain derived-only. They may include run metadata, scores, action labels, aggregate review coverage, and derived recommendations. They must not include secrets, cookies, OAuth tokens, raw source pages, private account data, raw signal inventories, or outcome notes.
