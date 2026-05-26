# Connector Policy

This policy is the review gate for any future Wraeclast Quant connector that reads from an external source. It applies before a collector moves beyond the current dry-run placeholder behavior.

Wraeclast Quant is decision-support software only. A connector may gather research data for local analysis, snapshots, alerts, reports, and derived public-intel exports. A connector must never automate gameplay, in-game trading, whispers, UI clicks, movement, game-client interaction, or trades.

## Required Review

Before implementation, complete a source-specific review that answers:

- What source will be used, and is it configured in `RESOURCES.md`?
- What explicit `allowed_use` is configured for the source?
- Have source terms, API terms, and usage policies been reviewed?
- Has robots.txt or the source API policy been reviewed where applicable?
- Does the source require authentication, login, cookies, tokens, or account access?
- If authentication is required, has the auth method been explicitly approved?
- If authentication is required, has credential storage outside the repo been reviewed?
- What rate limit, backoff behavior, and retry budget will the connector use?
- What cache TTL will be used to avoid repeated source hits?
- What data shape will be collected, normalized, stored, and exported?
- What source terms URL, API/robots policy URL, review date, notes, and allowed data shape were recorded as local review evidence?
- What raw data must stay local and what derived fields may appear in `public_intel.json`?
- What tests will prove the connector respects dry-run mode, caching, and error handling?

If any answer is unclear, the connector remains ineligible and should stay manual-review or placeholder-only.

## Allowed Connector Patterns

Prefer sources that provide one of these compliant access paths:

- official API with documented terms and rate limits
- RSS or Atom feed intended for machine consumption
- downloadable public data with clear reuse terms
- manually exported summaries or files supplied by the user
- cached snapshots from a source that explicitly permits the planned use

Use `wq preflight` to inspect current `RESOURCES.md` readiness before planning connector work. Preflight eligibility is not implementation approval; it means the source is ready for a source-specific connector design review.

Use `wq connector-candidates` to rank configured resources for manual source review. Candidate reporting is advisory only: it does not approve automation, change `RESOURCES.md`, write review files, or permit live fetching.

Use `wq connector-review-prep --resource <id-or-name> --access-method api|rss|download|manual-export` to create a local review workspace with a conservative JSON draft and a human Markdown checklist. Review prep is local-only: it does not inspect websites, approve a source, edit `RESOURCES.md`, fetch data, or implement a connector.

Use `wq connector-draft --resource <id-or-name> --access-method api|rss|download|manual-export --output-path <file>` to create a local machine-readable review draft from a configured resource. The draft keeps human review confirmations set to false and evidence fields empty, so it should not pass the gate until source terms and API/robots policy have been manually reviewed and edited.

Evidence fields are optional while a review is still a draft. Once `source_terms_reviewed` and `robots_or_api_policy_reviewed` are set to true, `wq connector-check` requires the reviewed terms URL, reviewed robots/API policy URL, review date, and allowed data shape. Review notes remain optional.

Authentication-required sources must also set `authentication_approved` and `credential_storage_reviewed` before `wq connector-check` can pass. These fields approve planning and dry-run implementation only. They do not permit secrets in the repo, token storage, live HTTP, cache writes, or background polling unless a later implementation packet explicitly adds and verifies that runtime behavior.

Use `wq connector-review-evidence --review-path <file>` after manual human review to update the local review JSON without hand-editing. Evidence update only records user-provided values, writes the local review file, and prints review status. It does not verify URLs, browse, fetch, approve a source, edit `RESOURCES.md`, or implement a connector.

Use `wq connector-review-status --review-path <file>` while editing a draft to inspect the current checklist, evidence fields, preflight state, readiness, and blockers. Review status is advisory and read-only: it may exit successfully for a not-ready draft, and it does not approve automation.

For source candidates such as poe.ninja where public pages, community API notes, or data dump links exist but official access terms are not yet confirmed, keep a local research note next to the review draft. The note may list candidate URLs and open questions, but it must not set review booleans, approve an access method, or replace manual terms/API-policy review. For poe.ninja currency, the current local research note is `examples/reviews/poe_ninja_poe2_currency_research.md`.

Use `wq connector-approval-helper --review-path <file>` after review evidence is complete to inspect the matching `RESOURCES.md` entry and see whether a manual `allowed_use` change is appropriate. The helper is advisory only: it does not modify `RESOURCES.md`, approve a source, or permit live collection.

Use `wq connector-approval-patch --review-path <file> --output-path <file>` after the approval helper reports a manual change is appropriate. The command writes a local unified diff preview for the `allowed_use` metadata change only; it does not edit `RESOURCES.md`, approve a source, or permit live collection.

Use `wq connector-fixture-run --review-path <file> --fixture-path <file>` to validate a future connector's derived output shape from a local synthetic fixture. The fixture runner is design infrastructure only: it reads local files, performs no network requests, writes no cache files, and does not approve live collection.

Use `wq connector-dry-run --review-path <file> --fixture-path <file>` to exercise the future source-connector interface with local fixture data. The dry-run connector reports the connector class, normalized rows, and future cache path, but live collection remains unsupported.

Use `wq connector-fixture-export --review-path <file> --fixture-path <file> --output-path <file>` only when a local synthetic fixture includes normalized `0-100` signal scores for every row. The command writes manual-import-compatible JSON for `wq validate-import`, `wq import`, or `wq daily --input-path`; it does not infer signals from raw price text, create snapshots, fetch data, or approve live collection.

Use `wq connector-fixture-daily --review-path <file> --fixture-path <file>` to prove that a fixture-backed connector shape can drive the full local pipeline. The command requires a ready review and normalized fixture signals, creates a local `connector-fixture` snapshot run, and writes local derived artifacts only. It is not live collection approval.

Use `wq currency-exchange-manual-snapshot --input-path <file>` for user-supplied official Currency Exchange observations when OAuth or live HTTP is unavailable or intentionally parked. The command reads only local manual snapshot JSON, validates the Currency Exchange shape, and optionally writes connector-fixture JSON when `--output-fixture-path` is supplied. It does not approve live collection, reuse browser sessions, read credentials, exchange tokens, fetch from the trade site or API, create raw caches, write database snapshots, or publish artifacts.

Use `wq connector-check --review-path <file>` with a machine-readable review based on `examples/connector_review_template.json`, `examples/connector_review_api_example.json`, `examples/connector_review_rss_example.json`, or `examples/connector_review_download_example.json` before implementation planning. A passing connector check is still a readiness gate only; it does not approve live collection by itself.

Use `wq connector-plan --review-path <file>` after a review passes to preview the local cache path, cache TTL, rate limit, and minimum request interval for a future connector. This planning step is read-only and performs no network requests.

## Disallowed Connector Patterns

Do not implement connectors that:

- bypass CAPTCHAs, login walls, permissions, or access controls
- ignore robots.txt, API terms, rate limits, or source terms
- scrape private messages, private channels, or non-public data
- use Discord user tokens or impersonate users
- collect session cookies, credentials, or private account data
- automate browser flows to work around missing APIs
- automate Path of Exile 2 gameplay, trading, whispers, inputs, or client interaction
- publish, post, or send alerts externally without a separate explicit approval

## Discord Rule

Discord is always compliance-gated. Future Discord work must use an approved bot added to accessible channels, Discord API-compliant collection, or manual exported summaries. Never use user tokens, private-message scraping, permission bypasses, or private-channel collection.

## Dry-Run and Caching Requirements

Every real connector must keep a dry-run path that performs no network access and explains what would be collected. Live collection must cache aggressively, obey source limits, and fail closed when compliance metadata is missing or unclear.

Authentication-required connectors must also fail closed when credentials, token refresh, user-agent/contact configuration, rate-limit headers, or cache writes are missing or invalid. Credentials and tokens must be configured outside the repo and must never appear in review files, source code, fixtures, public artifacts, logs intended for sharing, or `.env` files committed to the project.

The first implementation for a source should be narrow: one source, one data shape, one cache policy, and focused tests. Broad scraping frameworks are out of scope.

## Derived Public Intel

Public-facing artifacts must remain derived-only. `public_intel.json` and the static dashboard may include item names, scores, actions, deltas, alert reasons, run metadata, and compliance counts. They must not include raw source pages, raw resource notes, full source inventories, credentials, cookies, tokens, `.env` values, or private data.

## Approval Checklist

A future connector can be considered for implementation only when:

- the source exists in `RESOURCES.md`
- `wq preflight` does not report the source as blocked, Discord-gated, missing URL, or unclear
- `wq connector-candidates` identifies the source as worth manual review
- a completed source review exists, starting from `wq connector-review-prep` or `wq connector-draft` when useful
- `wq connector-review-evidence --review-path <file>` has recorded manually collected evidence when useful
- `wq connector-review-status --review-path <file>` shows no unresolved blockers
- `wq connector-approval-helper --review-path <file>` has been used before any manual `RESOURCES.md` approval edit
- `wq connector-approval-patch --review-path <file> --output-path <file>` has been used to preview any proposed manual `RESOURCES.md` approval edit when applicable
- `wq connector-fixture-run --review-path <file> --fixture-path <file>` passes for a local synthetic output fixture
- `wq connector-dry-run --review-path <file> --fixture-path <file>` passes for the fixture-backed source connector
- `wq connector-fixture-export --review-path <file> --fixture-path <file> --output-path <file>` passes when the fixture is intended to feed manual import scoring
- `wq connector-fixture-daily --review-path <file> --fixture-path <file>` passes when the fixture is intended to feed the full local pipeline
- `wq connector-check --review-path <file>` passes
- `wq connector-plan --review-path <file>` produces a safe local fetch plan
- rate limits, backoff, cache TTL, and dry-run behavior are specified
- review evidence records source terms URL, policy URL, review date, notes, and allowed data shape
- authentication-required reviews record explicit auth approval and credential-storage review
- raw-vs-derived data handling is specified
- tests are planned for success, dry-run, cache use, limit handling, and failure modes

Until all checklist items are complete, keep the source as a dry-run placeholder or manual-review workflow.
