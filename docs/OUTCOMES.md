# Recommendation Outcome Contract

Wraeclast Quant can record local manual review outcomes for recommendations. This is a feedback loop for evaluating recommendation quality, not a trade log, broker connection, automation system, or publishing workflow.

## Commands

```powershell
wq review-queue
wq review-queue --run-id <id> --output-path data/processed/review_queue.md
wq review-queue --run-id <id> --decisions-output-path data/processed/outcome_decisions.json
wq review-queue --run-id <id> --output-path data/processed/review_queue.md --context-path data/processed/ui_observation_review.md
wq review-coverage
wq record-outcome --run-id <id> --item-name <name> --outcome positive
wq record-outcomes --input-path data/processed/outcome_decisions.json --dry-run
wq record-outcomes --input-path data/processed/outcome_decisions.json
wq outcomes
wq outcome-review
wq outcome-report
wq calibration
wq calibration-report
```

`review-queue` shows recommendations from a run that do not yet have a recorded outcome. It includes the run source mode, a local decision-support caveat, outcome-label guidance, and item-specific `record-outcome` command templates. Add `--run-id <id> --output-path <file>` to write the same local-only queue as a Markdown worksheet without recording outcomes. Add `--context-path <file>` with `--output-path` to embed a local Markdown context file, such as a Currency Exchange UI-observation sidecar, into the worksheet. Add `--decisions-output-path <file>` to write an editable local JSON template for `record-outcomes`; the command prints the matching `record-outcomes --dry-run` validation step. The worksheet includes exact positive, neutral, and negative command options plus local notes fields for each item so a human can choose one outcome without editing the outcome label by hand.

`review-coverage` shows reviewed, unreviewed, and reviewed-percent counts for a run. It includes the run source mode, the same local-only caveat, and a worksheet plus decisions-template dry-run next action when unreviewed recommendations remain.

`record-outcome` records one local manual outcome for an item from an existing analysis run. It rejects a second outcome for the same run item so accidental reruns do not duplicate local feedback. After recording, rerun `wq review-coverage --run-id <id>`, then use `wq outcomes`, `wq outcome-review`, and `wq calibration` for local feedback. Refresh derived artifacts with `wq export`, `wq site`, and `wq site-bundle` when you want local dashboard or public handoff files to reflect the new review state.

`record-outcomes` records a local batch of human-reviewed outcome decisions from a JSON file. The whole file is validated before any outcome is written, so a bad item name, duplicate item, already-reviewed item, missing run, invalid label, or malformed decision prevents partial writes. The valid batch is then written in one local SQLite transaction, so a write failure rolls back the batch instead of leaving partial outcome rows. Add `--dry-run` to validate the same file without writing outcome records. After a successful write, it points to review coverage, recent outcomes, outcome review, calibration, and optional derived-artifact refresh.

Batch outcome JSON shape:

```json
{
  "local_review_only": true,
  "instructions": "Fill each outcome with one of: positive, neutral, negative. Then run record-outcomes --dry-run before recording.",
  "allowed_outcomes": ["positive", "neutral", "negative"],
  "run_id": 11,
  "decisions": [
    {
      "item_name": "Exalted Orb / Divine Orb (Standard UI)",
      "opportunity_score": 56.16,
      "action": "WATCH",
      "outcome": "neutral",
      "notes": "Optional local note."
    }
  ]
}
```

`outcomes` lists recent local outcome records and summary counts.

`outcome-review` joins outcomes back to original recommendation score and action, then points to `wq calibration` and `wq outcome-report --output-path data/processed/outcome_review.md` for the next read-only summary/report steps.

`outcome-report` writes `data/processed/outcome_review.md`.

`calibration` summarizes reviewed recommendations by action, score bucket, and outcome label. It is read-only, does not change scoring weights or thresholds, and points to `wq calibration-report --output-path data/processed/calibration_report.md` when you want a local Markdown calibration artifact.

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
- that run item does not already have a recorded outcome

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

The local review queue worksheet includes:

- `# Wraeclast Quant Review Queue`
- `## Outcome Labels`
- `## Unreviewed Recommendations`
- `## Review Checklist`
- `## Batch Outcome Template`
- `## Outcome Command Options`
- `## Manual Review Notes`

If no reviewed recommendations exist, the report says:

```text
No reviewed recommendation outcomes found.
Next: wq review-queue --run-id <id> --output-path data/processed/review_queue.md; wq review-queue --run-id <id> --decisions-output-path data/processed/outcome_decisions.json; fill outcomes; wq record-outcomes --input-path data/processed/outcome_decisions.json --dry-run. After the dry-run passes, record the reviewed batch with wq record-outcomes --input-path data/processed/outcome_decisions.json.
Outcome labels: positive=useful signal, neutral=mixed or unclear, negative=not useful after review.
```

## Public Export Boundary

Outcome summary counts and review coverage may appear in `public_intel.json`.

Manual outcome notes must not appear in `public_intel.json`, the static dashboard, site bundles, or other derived public artifacts. Notes may contain private user context and should remain local.

## Safety Notes

Outcome review is local decision support. It must not automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, scraping, Discord collection, webhooks, publishing, hosting, or source-term bypasses.
