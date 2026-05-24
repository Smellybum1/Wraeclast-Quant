# Roadmap

## Completed MVP Foundation

- Tolerant `RESOURCES.md` loader with safe defaults.
- Documented resource configuration parser contract with drift coverage.
- Resource compliance, preflight, connector-check, and connector-plan gates.
- Dry-run placeholder collectors only.
- Deterministic opportunity scoring and action mapping.
- Documented deterministic scoring contract with drift coverage.
- Local manual JSON/CSV signal import with templates, validation, and diagnostics.
- Documented manual import JSON/CSV contract with template drift coverage.
- SQLite snapshot persistence for analysis runs and scored opportunities.
- Local run provenance metadata for connector-fixture auditability.
- Latest-versus-previous snapshot comparisons.
- Documented snapshot comparison contract with drift coverage.
- Tunable local alert candidate previews.
- Documented local alert rule contract with drift coverage.
- Delta-aware Markdown market brief.
- Derived-only `public_intel.json` export with recent runs, score trends, outcome summary, and review coverage.
- Local static dashboard preview and local site bundle.
- `wq daily` orchestration for sample data or manual import files.
- Documented daily pipeline orchestration contract with drift coverage.
- Local schedule-helper guidance for user-controlled Windows Task Scheduler setup.
- Recommendation outcome recording, review queues, coverage, outcome review reports, and local calibration reports.
- Documented recommendation outcome review contract with drift coverage.
- Read-only project status command.
- Strict local status mode for health-gated checks.
- Machine-readable JSON output for local status checks.
- Versioned status JSON contract with generation timestamps.
- Stable status JSON row keys for local automation.
- Top-level status JSON row map for local automation.
- Status JSON health summary counts for local automation.
- Stable status JSON failure keys for strict local automation.
- Documented status JSON v1.5 contract with derived artifact freshness checks.
- SQLite health summary in the local status command.
- Market brief metadata health in the local status command.
- Public-intel contract health in the local status command.
- Static dashboard metadata health in the local status command.
- Site bundle manifest health in the local status command.
- Read-only repository behavior for missing SQLite databases.
- Read-only SQLite database health check.
- Shared local SQLite schema contract for database and backup verification.
- Documented local SQLite schema contract with drift coverage.
- Read-only CLI schema contract inspection.
- Versioned derived public-intel contract.
- Documented public-intel JSON v1.0 contract for future local/static-site consumers.
- Local SQLite backup command for snapshot history.
- Immediate post-create verification for local SQLite backups.
- Read-only SQLite backup verification.
- Read-only local backup listing.
- Backup health summary in the local status command.
- Strict status failure for invalid local backup health.
- Read-only backup restore helper with manual PowerShell guidance.
- Documented local backup and restore-helper contract with drift coverage.
- Schema contract visibility in local backup verification.
- Connector review examples and fixture coverage for API/RSS/download sources.
- Read-only public-intel contract validation.
- Public-intel contract enforcement for local site rendering and bundling.
- Validated public-intel metadata in local site bundle manifests.
- Local publish readiness check for static site bundles before manual publishing.
- Local manual publish handoff report for static site bundles before any external publishing.
- Versioned local public-site contract descriptor for future static publishing handoff.
- Static dashboard contract metadata tags for local/public artifact inspection.
- Documented local static artifact and site bundle contract.
- CLI decomposed into focused command modules with public command registration preserved.
- Connector command module decomposed into focused review, approval, fixture, candidate, and planning registrations.
- Connector policy service decomposed into focused review, readiness, approval, report, patch, and shared-helper modules.
- Maintenance command module decomposed into focused backup, migration/provenance, outcome, and calibration registrations.
- Status health logic decomposed into focused command rendering and report-building service modules.
- Storage repository decomposed into focused snapshot, artifact/provenance, outcome, and shared support modules.
- Static dashboard rendering decomposed into focused facade, health, and HTML rendering modules.
- Publish readiness decomposed into focused facade, readiness, handoff, and model modules.
- Report command registration decomposed into focused report/export, static artifact, and publish handoff modules.
- Static artifact command registration decomposed into focused site, public-intel validation, and site-bundle modules behind the stable report artifact aggregator.
- Publishing command registration decomposed into focused publish-check, publish-handoff, and site-contract modules behind the stable report publishing aggregator.
- Report export command registration decomposed into focused market-brief report and public-intel export modules behind the stable report export aggregator.
- Daily pipeline orchestration decomposed into a shared workflow service used by manual/sample and connector-fixture daily commands.
- Connector fixture command registration decomposed into focused inspection, export, and pipeline modules.
- Snapshot command registration and local table rendering decomposed into focused listing, comparison, alert, and rendering modules.
- Public intel service decomposed into focused facade, builder, payload, constant, and writer modules.
- Site bundle service decomposed into focused facade, model, manifest, writer, and health modules.
- Site contract service decomposed into focused facade, constants, summaries, payload, and writer modules.
- Publish readiness follow-up cleanup split artifact checks, freshness row helpers, and payload conversion behind the stable facade.
- Status health helper logic decomposed into focused model, row, storage, and artifact modules behind the stable status orchestration entry point.
- Static site rendering helper logic decomposed into focused section, HTML helper, and style modules behind the stable renderer entry point.
- Outcome repository helper logic decomposed into focused policy, record, review-query, and coverage modules behind the stable repository mixin.
- Daily command registration decomposed into focused daily-run and schedule-helper modules behind the stable command aggregator.
- Daily run result rendering split into a focused helper behind the stable `daily` command.
- Daily schedule-helper command logic decomposed into focused command, validation, and command-builder modules behind the stable schedule-helper aggregator.
- Connector fixture daily pipeline command cleanup split local fixture preparation and provenance assembly from command rendering.
- Connector fixture daily command result rendering split into a focused helper behind the stable fixture-daily command.
- Connector fixture inspection command registration decomposed into focused fixture-run and dry-run modules behind the stable inspection aggregator.
- Connector fixture run command rendering split into a focused helper behind the stable fixture-run command.
- Connector dry-run command rendering split into a focused helper behind the stable dry-run command.
- Connector fixture export command rendering split into a focused helper behind the stable `connector-fixture-export` command.
- Connector review command registration decomposed into focused draft/prep, evidence/status, and readiness-check modules behind the stable connector review aggregator.
- Connector review prep command rendering split into a focused helper behind the stable draft/prep command module.
- Connector review evidence/status command registration split into focused evidence-update and status-display modules behind the stable status aggregator.
- Connector review status table rendering split into a focused helper behind stable evidence/status commands.
- Backup storage service decomposed into focused model, writer, verifier, listing, and restore-guidance modules behind the stable backup facade.
- Maintenance outcome command registration decomposed into focused record/list, review queue/coverage, and report modules behind the stable outcome aggregator.
- Maintenance outcome command table rendering split into focused helpers behind the stable outcome command modules.
- Maintenance backup command registration decomposed into focused backup creation, inspection, and restore-guidance modules behind the stable backup command aggregator.
- Maintenance backup command table rendering split into focused helpers behind the stable backup command modules.
- Migration readiness service decomposed into focused model, row helper, readiness evaluation, and payload modules behind the stable migration facade.
- Maintenance migration/provenance command rendering split into a focused helper behind stable read-only commands.
- Calibration command table rendering split into a focused helper behind the stable calibration command registration.
- Connector review file service decomposed into focused draft, evidence update, JSON I/O, and prep/checklist modules behind the stable review-file facade.
- Connector policy utility helpers decomposed into focused resource, patch, text-formatting, and status-row modules behind the stable utility facade.
- Connector review checks decomposed into focused readiness evaluation and status-row assembly modules behind the stable review-check facade.
- Connector review check command rendering split into a focused helper behind the stable `connector-check` command.
- Connector review report command rendering split into a focused helper behind the stable report command.
- Connector approval command rendering split into focused helper/patch table rendering behind stable approval commands.
- Connector planning command rendering split into a focused helper behind the stable `connector-plan` command.
- Resource loader decomposed into focused model, type-inference, and Markdown parser modules behind the stable `resources_loader` facade.
- Resource command registration decomposed into focused collect, compliance, and preflight modules behind the stable resource command aggregator.
- Status command registration decomposed into focused schema, status-report, and database-check modules behind the stable status command aggregator.
- SQLite database-check command rendering split into a focused helper behind the stable `db-check` command.
- Intake command registration decomposed into focused sample-analysis, manual-import, watchlist, and shared-rendering modules behind the stable intake command aggregator.
- Reusable general Codex skills extracted for behavior-preserving decomposition and local compliance data workflows.
- Autonomous roadmap execution guidance added to `AGENTS.md`, with a short Goal Mode prompt and operating loop in `docs/GOAL_MODE.md`.
- Markdown documentation refreshed to reflect connector review, fixture pipeline, publishing handoff, migration readiness, provenance, calibration, and recent decomposition work.
- Design documentation updated to match SQLite schema contract version `2`.
- Read-only SQLite migration-readiness check and documented future schema-change workflow.
- Public command help smoke coverage for the `wq` command surface.
- Local connector review draft workflow for source-specific compliance review.
- Local connector review prep workflow with human checklist generation.
- Local connector review evidence update workflow for manually collected source review fields.
- Local connector candidate report for prioritizing source-specific reviews.
- Connector candidate command rendering split into a focused helper behind the stable candidate report command.
- Local connector review status checklist for inspecting incomplete review drafts.
- Optional connector review evidence fields for local source-term auditability.
- Connector review evidence gate requiring reviewed URLs, review date, and allowed data shape before readiness.
- Read-only connector approval helper for manual `RESOURCES.md` allowed-use changes after completed review.
- Read-only connector approval patch preview for manual `RESOURCES.md` allowed-use changes.
- Local connector fixture runner for synthetic output-shape validation before live connector work.
- Fixture-backed dry-run source connector interface with live collection explicitly unsupported.
- Local connector fixture signal export to manual-import-compatible JSON.
- Local connector fixture daily pipeline for end-to-end derived artifact generation without live collection.
- First human-approved API resource: `poe_ninja_poe2_currency`.
- Ready poe.ninja POE2 currency connector review with safe fetch plan.
- poe.ninja POE2 currency fixture, dry-run, and manual-import export proof without live collection.
- Source-specific poe.ninja POE2 currency dry-run connector facade with live collection still unsupported.
- poe.ninja POE2 currency fixture-daily proof through SQLite snapshots, derived public intel, static dashboard, site bundle, run provenance, and fresh local backup coverage.
- poe.ninja POE2 currency live endpoint-contract review recorded; live collection remains blocked until an official endpoint and response-field contract are confirmed.

## Recommended Next Milestones

- Keep live poe.ninja collection unsupported until a separate implementation packet specifies the exact endpoint/field contract, cache read/write behavior, HTTP failures, and tests.
- Use the poe.ninja fixture export with `wq validate-import`, `wq import`, or `wq daily --input-path` when proving manual-import scoring from connector-shaped rows.
- Obtain source-owner documentation or confirmation for the poe.ninja POE2 currency endpoint and response-field schema before enabling any live network collection.
- Plan future static publishing only after `wq publish-check`, `wq publish-handoff`, and `wq site-contract` are ready and manually reviewed.
- Use the `AGENTS.md` autonomous roadmap loop and `docs/GOAL_MODE.md` prompt when asking Codex to advance the project packet-by-packet.
- Continue maintainability with another bounded command/storage/report service when human source review is blocked; likely next targets include resource command rendering cleanup or report artifact rendering cleanup.

## Later Intelligence Improvements

- Build popularity trend ingestion from compliant sources after connector approval.
- Richer liquidity and manipulation-risk modeling.
- Confidence labels for recommendations based on signal freshness and manual-review coverage.
- Better manual-review workflows for uncertain or low-confidence signals.
- Historical performance review of prior recommendations.

## Future: Discord Signal Collector

Discord remains future-only and compliance-gated. Do not implement Discord collection without explicit approval and a source-specific compliance review.

Potential signals:

- Message volume by class/build channel.
- Rate of change in activity per channel.
- Repeated mentions of skills, uniques, support gems, bases, ascendancies, and mechanics.
- Creator or high-reputation user posts.
- Questions like "what weapon do I use for X build?"
- Complaints about scarcity or expensive required items.

Safety and compliance:

- Do not scrape Discord with a user token.
- Do not bypass Discord permissions.
- Prefer an approved bot added to accessible channels, Discord API-compliant collection, or manual exported summaries.
- Store only aggregate activity metrics and relevant public text snippets where allowed.
- Never collect private messages.

## Hard Boundaries

- No gameplay automation, in-game trading, whispers, UI clicks, movement, keyboard or mouse input, or game-client interaction.
- No CAPTCHAs, login walls, robots.txt, source terms, API limits, or access-control bypasses.
- No external publishing, webhooks, Discord posting, or hosted website behavior until explicitly requested and reviewed.
- `RESOURCES.md` remains user-owned and is never overwritten.
