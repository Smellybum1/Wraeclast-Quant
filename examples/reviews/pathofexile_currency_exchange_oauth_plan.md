# Path of Exile Currency Exchange OAuth/App Registration Plan

This is a planning handoff only. It does not request OAuth access, create or store credentials, edit `.env`, fetch live data, write cache files, implement a connector, create snapshots, publish artifacts, or approve recommendation scoring.

## Current Status

- Resource draft: `official_currency_exchange_api`
- Resource allowed use: `api`
- Review file: `examples/reviews/pathofexile_currency_exchange_connector_review.json`
- Local raw fixture: `examples/pathofexile_currency_exchange_fixture.json`
- Parser/normalizer proof: `wraeclast_quant.collectors.pathofexile_currency_exchange`
- Preview signal policy: `examples/reviews/pathofexile_currency_exchange_signal_policy.md`
- OAuth runtime design: `examples/reviews/pathofexile_currency_exchange_oauth_runtime_design.md`
- Runtime ADR: `docs/adr/0003-currency-exchange-confidential-client-runtime.md`
- Source approval status: approved for API planning in `RESOURCES.md`
- Runtime preflight status: non-network settings and user-agent validation implemented
- Live implementation status: still blocked
- Reason: official Currency Exchange access requires `service:cxapi`, OAuth/app-registration credentials outside the repo, token exchange, dynamic rate-limit handling, cache/backoff behavior, and failure-closed live-network tests before live HTTP work.

## Official Documentation To Review Before Approval

- `https://www.pathofexile.com/developer/docs`
- `https://www.pathofexile.com/developer/docs/reference`
- `https://www.pathofexile.com/legal/terms-of-use-and-privacy-policy`

## Approval Decisions Needed

Completed:

- `official_currency_exchange_api` is approved as `allowed_use: api` in `RESOURCES.md`.

Still ask the user before doing any of these:

- Requesting or using Path of Exile OAuth application access.
- Choosing public-client versus confidential-client handling.
- Adding any client id, client secret, token, redirect URI, contact email, or `.env` configuration.
- Implementing live HTTP, token exchange, cache reads/writes, or snapshot creation from the API.

Runtime design now recommends a confidential-client `client_credentials` service-token flow for `service:cxapi`. Public-client OAuth, browser-cookie reuse, and trade-site session reuse remain out of scope.

## Recommended App Registration Packet

If the user approves pursuing official API access, keep the next packet non-code or config-only:

1. Confirm the intended application name and contact email for the required user agent.
2. Confirm the client type and grant flow allowed by the official docs for a local desktop tool.
3. Confirm whether the user wants to request only `service:cxapi`.
4. Record the approved scope, redirect URI approach, and secret-storage boundary in a local handoff note.
5. Do not store tokens or credentials in the repo.

## Recommended Implementation Packet After Approval

Only after source and auth approval:

1. Add a read-only runtime-plan/report helper that prints source readiness, endpoint, realm, cache path, user-agent readiness, and secret-source blockers without network access.
2. Reuse the existing raw fixture parser/normalizer proof for the documented hourly aggregate fields.
3. Review and approve the preview signal-normalization policy before manual-import export, daily snapshot, or scoring use.
4. Add cache-only and fixture tests before any live request code.
5. Add live fetch code behind explicit policy checks.
6. Fail closed on missing credentials, missing user-agent/contact config, 401/403/429, `Retry-After`, malformed JSON, unknown schema, missing required fields, or cache write errors.
7. Keep public artifacts derived-only and do not create snapshots on failures.

## Proposed Conservative Runtime Defaults

- Realm: `poe2`
- Endpoint shape: `/currency-exchange/poe2[/<id>]`
- Cache TTL: `3600s`
- Initial configured request budget: `6/min` until response rate-limit headers are parsed and obeyed.
- Public export: derived-only summaries and normalized Wraeclast Quant signals.

## Not Approved Yet

- Live API calls.
- Browser-cookie or trade-site session reuse.
- OAuth token storage.
- Credential prompts.
- Background polling.
- Snapshot writes from live official API data.
- Publishing, webhooks, Discord posting, or game-client interaction.
