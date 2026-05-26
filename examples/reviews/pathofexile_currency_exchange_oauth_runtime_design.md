# Path of Exile Currency Exchange OAuth Runtime Design

This is a design packet only. It does not implement OAuth, request credentials, store secrets, call live HTTP endpoints, write raw caches, create snapshots, publish artifacts, or wire Currency Exchange data into recommendation scoring.

## Source Review Date

- Reviewed on: 2026-05-26
- Resource id: `official_currency_exchange_api`
- Required source scope: `service:cxapi`
- Intended endpoint: `GET /currency-exchange/poe2[/<id>]`
- Current implementation status: dry-run fixture conversion plus non-network runtime preflight models

## Official Documentation Inputs

- Path of Exile Developer Docs: `https://www.pathofexile.com/developer/docs`
- Authorization docs: `https://www.pathofexile.com/developer/docs/authorization`
- API reference: `https://www.pathofexile.com/developer/docs/reference`
- Changelog: `https://www.pathofexile.com/developer/docs/changelog`

## Relevant Constraints

- The developer docs say API details and availability can change without notice.
- Applications must follow the API policies and Terms of Service.
- API requests must use an identifiable OAuth user-agent header with client id, version, and contact.
- Rate limits are dynamic and must be read from response headers.
- Too many invalid `4xx` requests can restrict access, including `401`, `403`, and `429`.
- Currency Exchange requires the `service:cxapi` scope.
- Service scopes require a confidential client with the `client_credentials` grant.
- Public desktop clients cannot use `service:*` scopes.
- Currency Exchange data is hourly historical aggregate data and does not include the current hour.

## Design Decision

The first live-runtime implementation should use a confidential-client service-token design and should not use browser cookies, trade-site sessions, public-client PKCE, or account-login automation.

Because Wraeclast Quant is a local-first desktop CLI, the runtime should require the user to provide already-approved application credentials outside the repo. The CLI may later read those credentials from environment variables or an explicitly configured secret file path outside the workspace, but it must never create, print, commit, or copy secrets into project files.

## Runtime Configuration Boundary

Non-secret configuration may be explicit in commands, local docs, or a future local-only user config:

- `client_id`
- app version
- contact email or contact URL for the user-agent
- realm, defaulting to `poe2`
- conservative local request budget
- cache directory path

Secret material must stay outside the repo:

- client secret
- access token
- any future token cache
- OAuth responses containing bearer tokens

The first implementation should prefer one of these secret inputs:

- `WQ_POE_CLIENT_SECRET_FILE`, pointing to a file outside `D:\Codex\Wraeclast Quant`
- `WQ_POE_CLIENT_SECRET`, read from the process environment and never logged

If both are missing, live collection must fail closed before any network request.

## Token Handling

Phase 1 should use memory-only access tokens for a single command invocation.

- Request a token with `grant_type=client_credentials` and scope `service:cxapi`.
- Do not persist the access token in the repo.
- Do not write token responses to fixtures, logs intended for sharing, public artifacts, or review notes.
- Redact token-like values from all user-facing errors.
- Treat `401` and `403` as hard failures requiring user action.

A persistent token cache can be designed later only after a separate credential-storage review. If added, it must live outside the repo and must be excluded from public artifacts, tests, fixtures, and Git.

## User-Agent Design

The runtime must build an identifiable user-agent from non-secret settings:

```text
OAuth {client_id}/{version} (contact: {contact}) WraeclastQuant
```

Missing client id, version, or contact should fail closed before token exchange or data requests.

## Rate-Limit And Backoff Design

The runtime should maintain a small local request budget before response headers are known.

- Default request budget: at most one Currency Exchange market request per command run unless explicitly overridden.
- Parse `X-Rate-Limit-Policy`, `X-Rate-Limit-Rules`, matching `X-Rate-Limit-*` headers, and `Retry-After`.
- On `429`, stop immediately and report the retry time without another request.
- On malformed or missing expected rate-limit headers, keep the stricter local budget.
- On repeated `4xx` failures, stop rather than probing.

## Currency Exchange Fetch Flow

1. Validate resource review and source gates.
2. Validate non-secret runtime config.
3. Load the client secret from an approved out-of-repo source.
4. Request a service token with `client_credentials` and `service:cxapi`.
5. Fetch one hourly page for `poe2`, optionally with a previously known `next_change_id`.
6. Parse with the existing fixture parser.
7. Write only approved local cache material after cache implementation is separately reviewed.
8. Convert to dry-run connector rows or preview diagnostics only.

## Cache Boundary

Cache writes remain a separate implementation decision.

Before raw cache writes are enabled:

- Choose an out-of-public-artifact raw cache directory.
- Define cache TTL and cleanup policy.
- Prove raw payloads never enter `public_intel.json`, static site, bundles, review reports, or Markdown market briefs.
- Add failure-closed tests for cache write errors.

## Failure-Closed Requirements

Live collection must fail before data requests when any of these are missing or invalid:

- source review does not pass
- `service:cxapi` is not approved for the application
- client id
- client secret
- app version
- user-agent contact
- realm
- token response shape
- bearer token
- rate-limit safety state

Live collection must stop without snapshots or public artifacts on:

- `401`
- `403`
- `429`
- malformed JSON
- missing `next_change_id`
- missing or invalid `markets`
- cache write failure, once cache writes exist

## Not In Scope

- Trade-site session reuse
- POESESSID or browser-cookie collection
- CAPTCHA or login-wall automation
- Public-client PKCE for `service:cxapi`
- In-game trading, whispers, clicks, movement, or gameplay automation
- Background polling
- Persistent token cache
- Raw payload publishing
- Recommendation scoring from live data

## Completed Non-Network Preflight Packet

The first safe code packet added configuration and preflight models only:

- a typed runtime settings object
- user-agent construction with redaction-safe validation
- secret-source validation that does not read or print a secret in tests
- failure-closed unit tests for missing config
- no network client and no token exchange

## Completed Runtime Plan Packet

The next safe code packet added a read-only runtime-plan helper that combines runtime preflight blockers with fetch-plan details for inspection. It does not expose a public command, read secrets, exchange tokens, fetch data, write cache files, create snapshots, or publish artifacts.

## Completed Token Shape And Redaction Packet

The next safe code packet added redaction helpers and token-response shape models for failure-closed validation without making requests or storing tokens.

## Completed Token Request Plan Packet

The next safe code packet added a token-request plan model that records the token endpoint, grant type, scope, client id, user-agent readiness, and required form-field names without sending a request or reading a secret.

## Next Implementation Packet

The next implementation packet would cross into live token exchange or live HTTP design. Ask the user before proceeding because it requires concrete credential handling, external account/application setup, and network behavior.
