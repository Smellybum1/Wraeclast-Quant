# Path of Exile Currency Exchange API Research Note

This note is a local source-review handoff for a possible future official Path of Exile Currency Exchange API connector. It does not approve automation, edit `RESOURCES.md`, request OAuth access, store credentials, fetch data, write cache files, implement a connector, create snapshots, publish artifacts, or permit live collection.

## Status

- Review date: `2026-05-26`
- Candidate resource name: `Path of Exile Currency Exchange API`
- Access method: `api`
- Current execution status: review evidence only
- Live implementation status: `blocked`
- Primary blockers: no approved `RESOURCES.md` entry, OAuth/app-registration handling is not approved, the endpoint requires `service:cxapi`, dynamic rate-limit headers must be implemented, and user-agent/contact configuration must be approved before live HTTP.

## Reviewed Official Surfaces

- `https://www.pathofexile.com/developer/docs`
- `https://www.pathofexile.com/developer/docs/reference`
- `https://www.pathofexile.com/legal/terms-of-use-and-privacy-policy`

## Findings

The official developer docs state that Path of Exile API access is generally read-only snapshot access and that applications must adhere to the API policies, Terms of Service, and Privacy Policy.

The API reference documents `GET /currency-exchange[/<realm>][/<id>]`, with `poe2` as a supported realm. It returns hourly aggregate Currency Exchange trade history and explicitly does not provide current-hour data.

The documented response shape includes:

- `next_change_id`
- `markets`
- `league`
- `market_id`
- `volume_traded`
- `lowest_stock`
- `highest_stock`
- `lowest_ratio`
- `highest_ratio`

The endpoint requires the `service:cxapi` scope. The developer docs describe OAuth 2.1, application registration, identifiable OAuth user-agent requirements, dynamic rate-limit response headers, retry-after handling, and invalid-request restrictions.

## Allowed Draft Data Shape

If this source is approved later, keep the local data shape narrow:

- league
- market currency pair
- hourly digest timestamp
- volume and stock aggregates
- ratio aggregates
- local source timestamp
- normalized Wraeclast Quant `0-100` signal fields after local transformation

Do not store or export OAuth tokens, client credentials, cookies, private account data, account profile data, stash data, character data, raw full API payloads in public artifacts, or source notes in public artifacts.

## Required Before Any Live Packet

- Ask the user before editing `RESOURCES.md` to add or approve this resource.
- Ask the user before adding OAuth/app-registration configuration, credentials, scopes, client id handling, contact email/user-agent configuration, or live network behavior.
- Implement only a dry-run and fixture path first.
- Specify cache reads/writes, TTL behavior, dynamic rate-limit parsing, retry-after handling, invalid-request limits, and failure-closed behavior.
- Add tests for dry-run, fixture shape, cache hit, cache miss, 401/403/429, retry-after, malformed JSON, unknown schema, missing fields, and no snapshot writes on failures.
- Keep public artifacts derived-only.

## Recommendation

Do not implement live collection yet. The official API is a stronger candidate than the poe.ninja page because it has a documented `poe2` endpoint and response fields, but it crosses an auth/source-approval boundary and therefore requires explicit user approval before code can add live HTTP, OAuth handling, or a `RESOURCES.md` approval change.
