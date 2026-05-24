# ADR 0001: Local-First Decision Support Boundary

## Status

Accepted

## Context

Wraeclast Quant analyzes Path of Exile 2 market signals and produces local reports, alerts, snapshots, and recommendations. The project must remain useful without crossing game automation, source-term, account, publishing, or private-data boundaries.

This boundary affects connector design, persistence, public artifacts, and autonomous agent behavior. It is easy for future work to blur "market intelligence" into scraping, live trading, posting, hosting, or gameplay automation unless the boundary is explicit.

## Decision

Wraeclast Quant is local-first decision-support software.

The app may produce local research, alerts, watchlists, market briefs, cached snapshots, fixture-backed proof runs, and derived public/static artifacts for manual review. It must not automate gameplay, in-game trading, whispers, UI clicks, movement, keyboard or mouse input, or game-client interaction.

External-source automation remains gated by source-specific review. Live collection is unsupported until the source's allowed access method, terms, robots/API policy, auth requirements, rate/cache policy, response-field contract, and failure behavior are reviewed and recorded. Public or static artifacts must remain derived-only.

## Consequences

- Connector work starts with source review, fetch plans, fixtures, and dry-run proof before any live HTTP implementation.
- `RESOURCES.md` remains user-owned and approval edits require explicit user approval.
- Public artifact commands may validate and package local outputs, but must not upload, host, post, or publish externally.
- Schema or persistence work must protect local user data with health checks, backups, and migration readiness.
- Recommendations must be human-readable and manually acted upon by the user.

## Alternatives Considered

- Build a live trading or gameplay automation tool. Rejected because it violates the project's safety boundary.
- Treat observed endpoints or community notes as sufficient for live collection. Rejected because source approval and field contracts need explicit evidence.
- Publish generated artifacts automatically. Rejected because manual handoff is safer and matches local-first operation.

## Review Triggers

- The user explicitly asks for a new external connector, source approval, publishing workflow, schema migration, or deployment behavior.
- Official source-owner documentation changes the allowed access method or response-field contract.
- The project expands from local decision-support into a hosted or multi-user product.
