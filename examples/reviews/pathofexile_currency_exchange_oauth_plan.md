# Path of Exile Currency Exchange OAuth/App Registration Plan

This is a planning handoff only. It does not request OAuth access, create or store credentials, edit `.env`, fetch live data, write cache files, implement a connector, create snapshots, publish artifacts, or approve automation.

## Current Status

- Resource draft: `official_currency_exchange_api`
- Resource allowed use: `manual-review`
- Review file: `examples/reviews/pathofexile_currency_exchange_connector_review.json`
- Live implementation status: `blocked`
- Reason: official Currency Exchange access requires `service:cxapi`, OAuth/app-registration handling, identifiable user-agent/contact configuration, dynamic rate-limit handling, cache/backoff behavior, and explicit user approval before live HTTP work.

## Official Documentation To Review Before Approval

- `https://www.pathofexile.com/developer/docs`
- `https://www.pathofexile.com/developer/docs/reference`
- `https://www.pathofexile.com/legal/terms-of-use-and-privacy-policy`

## Approval Decisions Needed

Ask the user before doing any of these:

- Changing `official_currency_exchange_api` from `manual-review` to `api` in `RESOURCES.md`.
- Requesting or using Path of Exile OAuth application access.
- Choosing public-client versus confidential-client handling.
- Adding any client id, client secret, token, redirect URI, contact email, or `.env` configuration.
- Implementing live HTTP, token exchange, cache reads/writes, or snapshot creation from the API.

## Recommended App Registration Packet

If the user approves pursuing official API access, keep the next packet non-code or config-only:

1. Confirm the intended application name and contact email for the required user agent.
2. Confirm the client type and grant flow allowed by the official docs for a local desktop tool.
3. Confirm whether the user wants to request only `service:cxapi`.
4. Record the approved scope, redirect URI approach, and secret-storage boundary in a local handoff note.
5. Do not store tokens or credentials in the repo.

## Recommended Implementation Packet After Approval

Only after source and auth approval:

1. Add a dry-run connector path that prints the endpoint, realm, cache path, and required headers without network access.
2. Add a fixture that mirrors the documented hourly aggregate market fields.
3. Add cache-only and fixture tests before any live request code.
4. Add live fetch code behind explicit policy checks.
5. Fail closed on missing credentials, missing user-agent/contact config, 401/403/429, `Retry-After`, malformed JSON, unknown schema, missing required fields, or cache write errors.
6. Keep public artifacts derived-only and do not create snapshots on failures.

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
