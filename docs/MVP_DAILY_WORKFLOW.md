# MVP Daily Workflow

This is the local-first MVP loop for Wraeclast Quant. It uses user-supplied local observations, deterministic scoring, SQLite history, and derived-only local artifacts. It does not use OAuth, live HTTP, browser sessions, scraping, raw cache writes, publishing, or game-client interaction.

## Daily Loop

1. Prepare a local official Currency Exchange manual snapshot using `examples/pathofexile_currency_exchange_manual_snapshot_template.json` as the shape reference.
2. Validate and preview the observation:

```powershell
wq currency-exchange-manual-snapshot --input-path <current-snapshot>
```

The validation-only output points to the rerun command with `--history-path <previous-snapshot> --output-fixture-path <fixture-output>` when you are ready to create a local fixture.

3. When you have a previous local observation, export a connector fixture with preview rolling-baseline signals:

```powershell
wq currency-exchange-manual-snapshot --input-path <current-snapshot> --history-path <previous-snapshot> --output-fixture-path <fixture-output>
```

When the fixture is written, the command prints the matching `wq connector-fixture-export --review-path examples/reviews/pathofexile_currency_exchange_connector_review.json --fixture-path <fixture-output> --output-path <manual-import-output>` next action.

4. Convert the local fixture into normalized manual-import JSON:

```powershell
wq connector-fixture-export --review-path examples/reviews/pathofexile_currency_exchange_connector_review.json --fixture-path <fixture-output> --output-path <manual-import-output>
```

When export succeeds, the command prints the matching `wq validate-import --input-path <manual-import-output>` next action.

5. Validate the normalized input before recording a run:

```powershell
wq validate-import --input-path <manual-import-output>
```

When validation passes, the command prints the matching `wq daily --input-path <manual-import-output>` next action.

If you only have manually transcribed in-game Currency Exchange ratio and stock-ladder rows, convert them directly into normalized manual-import JSON first:

```powershell
wq currency-exchange-ui-observation --input-path examples/pathofexile_currency_exchange_ui_observation_template.json --output-path <manual-import-output> --review-notes-output-path data/processed/ui_observation_review.md
wq validate-import --input-path <manual-import-output>
```

Before running the conversion, finish the local UI capture for every pair you intend to review:

- Capture the order-entry market ratio.
- Open the ratio/stock ladder and transcribe the visible rows, including the final aggregate row with `comparator: "less_than"` when the UI shows `<`.
- Use `no_stock: true` when the UI shows No Stock.
- Mark ratio-only observations clearly in `notes`; they remain valid, but scoring treats them conservatively because no visible stock ladder was captured.
- Prefer finishing all intended forward and reverse checks before `wq daily --input-path <manual-import-output>` so the stored run is not rewritten after review begins.

This UI observation path is local-only. The optional review-notes sidecar keeps a local Markdown summary of the manually transcribed rows and capture review flags for later human outcome review, including ratio-only captures, No Stock rows, missing stock ladders, and missing order-entry ratios. It does not use OAuth, live HTTP, scraping, OCR, game-client automation, raw cache writes, snapshots, outcome recording, or publishing.

When a sidecar is written, the conversion command prints the later `wq review-queue --run-id <id> --output-path data/processed/review_queue_run_<id>.md --context-path <sidecar>` handoff so the local notes can be reused after `wq daily` creates a run.

6. Run the local daily pipeline:

```powershell
wq daily --input-path <manual-import-output>
```

7. Inspect health and review state:

```powershell
wq status --strict
wq run-provenance --run-id <id>
wq watchlist
wq review-queue
wq review-queue --run-id <id> --output-path data/processed/review_queue_run_<id>.md
wq review-queue --run-id <id> --decisions-output-path data/processed/outcome_decisions_run_<id>.json
wq review-queue --run-id <id> --output-path data/processed/review_queue_run_<id>.md --context-path data/processed/ui_observation_review.md
wq review-coverage
```

Run provenance is local-only audit metadata for the run. For manual-import daily runs it records path-safe input metadata, file size, SHA-256 hash, item count, and explicit no-live-collection flags.

For stored runs, `wq watchlist`, `wq review-queue`, and `wq review-coverage` show review state and point fully reviewed runs with local calibration review prompts back to `wq calibration`. These prompts are read-only and do not retune scoring, publish artifacts, automate trades, or change recommendations.

The worksheet is local-only and includes exact positive, neutral, and negative `record-outcome` commands plus local notes fields for each unreviewed item. When you have a local context sidecar from `currency-exchange-ui-observation`, pass it with `--context-path` so the transcribed ratios and stock rows sit beside the outcome commands. Choose only one outcome per item after manual review.

8. Record outcomes only after a human review decision:

```powershell
wq record-outcome --run-id <id> --item-name <name> --outcome positive|neutral|negative
```

For a reviewed batch, put the human decisions in local JSON and record them together:

```powershell
wq review-queue --run-id <id> --decisions-output-path data/processed/outcome_decisions_run_<id>.json
wq record-outcomes --input-path data/processed/outcome_decisions_run_<id>.json --dry-run
wq record-outcomes --input-path data/processed/outcome_decisions_run_<id>.json
```

The dry run validates the edited run-scoped file without writing records and reports all row-level template errors together. The batch write command validates the whole file again before writing any outcome.

9. Inspect the local feedback loop after recording outcomes:

```powershell
wq review-coverage --run-id <id>
wq outcomes
wq outcome-review
wq calibration
wq outcome-report --output-path data/processed/outcome_review.md
wq calibration-report --output-path data/processed/calibration_report.md
```

These commands are local review aids. They do not retune scoring, publish artifacts, automate trades, or change recommendations without a separate implementation packet.

10. Optionally write a derived-only local companion handoff for manual Exile-UI Stash-Ninja review:

```powershell
wq stash-ninja-watchlist
```

This writes `data/processed/exile_ui_stash_ninja_watchlist.json` and `.md` from the latest local run. The files include item names, scores, actions, review coverage, suggested manual Stash-Ninja treatment, and an additive local calibration-prompt count. Unreviewed runs still point to the batch outcome-review flow; fully reviewed runs with calibration prompts point to `wq calibration`. They do not write Exile-UI settings or caches, automate the overlay, call live HTTP, read game-client state, include raw signals, retune scoring, change recommendations, or record outcomes.

You can also generate the same handoff during the daily run:

```powershell
wq daily --input-path <manual-import-output> --stash-ninja-watchlist
```

## MVP Readiness

`wq status` includes an `MVP readiness` row. It summarizes whether the local no-OAuth loop has a latest run and points to the next manual action. For unreviewed runs it points to `wq review-coverage --run-id <id>`, which prints the worksheet, outcome-decisions JSON template, and `record-outcomes --dry-run` checklist. For fully reviewed or empty loops it points back to preparing the next local Currency Exchange manual snapshot or UI observation, then the next `wq daily --input-path` run.

Before sharing or manually publishing static artifacts, run:

```powershell
wq publish-check
```

## Safety Notes

Public artifacts remain derived-only. They may include run metadata, scores, action labels, aggregate review coverage, and derived recommendations. They must not include secrets, cookies, OAuth tokens, raw source pages, private account data, raw signal inventories, or outcome notes.

The Stash-Ninja companion watchlist is also derived-only and local-only. It is a manual handoff aid, not a public site artifact and not an Exile-UI integration runtime.
