# Wraeclast Quant Context

This file defines shared project language for humans and Codex agents. Use it to keep plans, code, docs, and handoffs aligned. It is not a product spec; detailed contracts live in the focused docs.

## Product Frame

Wraeclast Quant is a local-first Path of Exile 2 market intelligence and decision-support app. It helps the user inspect market signals, snapshots, alerts, reports, and recommendations for manual review. It must not automate gameplay, trading, whispers, UI input, publishing, or access-control bypasses.

## Bounded Contexts

### Source Compliance

Source compliance covers `RESOURCES.md`, source review drafts, connector approval helpers, fetch plans, and preflight checks.

- `RESOURCES.md`: the user-owned source inventory. Agents may read it, but must not overwrite or approval-edit it unless explicitly asked.
- Resource: a configured source entry parsed from `RESOURCES.md`.
- Automation-eligible resource: a resource whose configured allowed use and completed review evidence permit local automation planning.
- Source review: a source-specific evidence file documenting terms, access method, robots/API policy, auth/CAPTCHA/private-data flags, rate limits, cache TTL, and allowed data shape.
- Connector approval: a manual allowed-use change in `RESOURCES.md`, optionally previewed by helper commands. It is not automatic.
- Auth approval: explicit permission for an authentication-required source review to proceed with local planning or dry-run implementation. It is not permission to commit secrets, store tokens, or make live requests.
- Credential-storage review: confirmation that credentials/tokens for an auth-required source will be stored outside the repo and excluded from public artifacts, fixtures, logs intended for sharing, and committed files.
- Confidential-client runtime: a future live-source runtime that uses source-approved application credentials outside the repo for a service-token flow. It is not browser-session reuse, trade-site login automation, or public-client OAuth.
- Memory-only token: an access token held only for one command invocation and never written to the repo, fixtures, logs intended for sharing, public artifacts, or review notes.
- Fetch plan: a local plan describing allowed method, rate/cache policy, future cache path, and blockers. A fetch plan is not live collection.

### Connector Proof Paths

Connector proof paths validate shape and safety before live network access.

- Fixture: a local synthetic or reviewed sample payload used to prove connector-shaped output.
- Dry-run connector: a connector interface that returns fetch-plan and fixture proof information without network access or cache writes.
- Fixture-daily run: an end-to-end local proof that writes a SQLite run from fixture data and regenerates derived artifacts.
- Currency Exchange manual snapshot: a user-supplied local JSON observation of official Currency Exchange hourly market rows. It can be converted into connector-fixture and manual-import formats, but it is not live API access, browser-session reuse, source approval, raw cache storage, or automatic trading.
- Currency Exchange UI observation: a user-supplied local transcription of visible in-game Currency Exchange order-entry and stock-ladder rows. It can be converted directly into manual-import format using conservative derived signals, but it is not API data, source approval, screen scraping, OCR, automation, or live collection.
- Live connector: a future network-capable source implementation. Live connectors stay unsupported until official endpoint, query parameters, response-field schema, reuse terms, auth/runtime requirements when applicable, cache/rate policy, and failure behavior are confirmed.
- poe.ninja POE2 Currency: the first approved API resource for fixture and dry-run proof. Live fetching remains blocked.

### Public Artifacts

Public artifacts are local files that may be manually reviewed for static handoff.

- Public intel: `data/processed/public_intel.json`, a versioned derived-only JSON contract for local/static consumers.
- Static site: `data/processed/site/index.html`, a local dashboard preview rendered from derived data.
- Site bundle: `data/processed/site_bundle/wraeclast_quant_site_bundle.zip`, a local archive for manual publishing review.
- Derived-only: public/handoff output may include scores, summaries, counts, run metadata, and recommendations, but not raw source pages, secrets, private data, raw signals, full inventories, or local-only sensitive notes.
- Publish readiness: local checks proving artifacts are fresh, contract-valid, and manual-publishing-ready. It does not upload or host anything.

### SQLite Persistence

SQLite persistence is the local audit trail for runs, scored opportunities, artifacts, provenance, and outcome reviews.

- Run: one stored analysis execution in SQLite.
- Latest run: the newest run used for freshness checks and public artifact generation.
- Run provenance: local audit metadata explaining how a run was produced, including connector-fixture runs and manual-import daily runs. Manual-import provenance should avoid exposing absolute local paths in routine output.
- Backup freshness: the newest verified backup covers the latest database run.
- Migration readiness: read-only checks proving schema-change planning is safe. Actual schema changes require strict health, fresh backup, and explicit migration work.

### Scoring And Outcomes

Scoring and outcomes are deterministic local decision-support surfaces.

- Opportunity score: deterministic local score derived from normalized signals.
- Action: human-readable recommendation label for manual review only.
- Market brief: Markdown decision-support report under `data/processed/`.
- Outcome review: local user feedback about recommendation results. Outcome notes stay local and must not leak into public artifacts.
- Calibration report: local summary of outcomes by action/score bucket. It does not retune scoring automatically.

### Autonomous Execution

Autonomous execution means Codex advances the project one bounded packet at a time.

- Packet: one focused feature slice, refactor, proof path, bug fix, or docs update with narrow verification.
- Highest-impact unblocked task: the best next task that fits current guardrails and does not require user decisions.
- Stop-and-ask decision: a decision affecting architecture, product direction, data model, public API, auth/security, deployment, persistence semantics, pricing, major UX behavior, source approval, dependencies, migrations, or live network behavior.
- Green handoff: relevant focused checks passed, broader checks ran when needed, artifacts are fresh when affected, risks are named, and the next packet is clear.

## Language Preferences

- Say "decision-support", not "trading bot".
- Say "manual publishing readiness", not "published site", unless the user explicitly performed publishing.
- Say "live collection unsupported" when endpoint/field-contract evidence is missing.
- Say "fixture proof" or "dry-run proof" for local connector validation without network access.
- Say "derived-only public artifacts" for outputs that may be manually shared.
- Say "source approval" only for explicit user-approved resource changes, not for research notes or observed endpoints.

## When To Update This File

Update this file when a packet introduces a durable term, clarifies a recurring ambiguity, or changes the meaning of an existing project concept. Do not update it for one-off implementation details, temporary task plans, or routine refactors.
