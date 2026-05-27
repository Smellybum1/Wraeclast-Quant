# Recommendation Outcome Contract

Wraeclast Quant can record local manual review outcomes for recommendations. This is a feedback loop for evaluating recommendation quality, not a trade log, broker connection, automation system, or publishing workflow.

## Commands

```powershell
wq review-queue
wq review-coverage
wq record-outcome --run-id <id> --item-name <name> --outcome positive
wq outcomes
wq outcome-review
wq outcome-report
wq calibration
wq calibration-report
```

`review-queue` shows recommendations from a run that do not yet have a recorded outcome. It includes the run source mode, a local decision-support caveat, outcome-label guidance, and item-specific `record-outcome` command templates.

`review-coverage` shows reviewed, unreviewed, and reviewed-percent counts for a run. It includes the run source mode and the same local-only caveat.

`record-outcome` records one local manual outcome for an item from an existing analysis run.

`outcomes` lists recent local outcome records and summary counts.

`outcome-review` joins outcomes back to original recommendation score and action.

`outcome-report` writes `data/processed/outcome_review.md`.

`calibration` summarizes reviewed recommendations by action, score bucket, and outcome label. It is read-only and does not change scoring weights or thresholds.

`calibration-report` writes `data/processed/calibration_report.md` for local calibration review.

## Allowed Outcomes

Allowed outcome labels:

- `negative`
- `neutral`
- `positive`

Outcome labels are normalized to lowercase. Any other label is rejected.

MVP review wording:

- `positive`: the recommendation was useful after manual review.
- `neutral`: the recommendation was mixed, stale, or unclear.
- `negative`: the recommendation was not useful after manual review.

## Required References

An outcome can only be recorded when:

- the analysis run exists
- the item exists in that analysis run

This keeps local review records tied to recommendations Wraeclast Quant actually produced.

## Local Report Markers

The local outcome review report includes:

- `# Wraeclast Quant Outcome Review`
- `Local review artifact only.`
- `## Outcome Summary By Action`
- `## Recent Reviewed Recommendations`

The local calibration report includes:

- `# Wraeclast Quant Recommendation Calibration`
- `## Outcome Counts By Action`
- `## Outcome Counts By Score Bucket`
- `## Average Score By Outcome`
- `## Recent Reviewed Recommendations`

If no reviewed recommendations exist, the report says:

```text
No reviewed recommendation outcomes found.
Next: run wq review-queue, then record human decisions with wq record-outcome --run-id <id> --item-name <name> --outcome positive|neutral|negative.
Outcome labels: positive=useful signal, neutral=mixed or unclear, negative=not useful after review.
```

## Public Export Boundary

Outcome summary counts and review coverage may appear in `public_intel.json`.

Manual outcome notes must not appear in `public_intel.json`, the static dashboard, site bundles, or other derived public artifacts. Notes may contain private user context and should remain local.

## Safety Notes

Outcome review is local decision support. It must not automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, scraping, Discord collection, webhooks, publishing, hosting, or source-term bypasses.
