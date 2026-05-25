# poe.ninja POE2 Currency Live Fetch Design Note

This note is a design handoff for `poe_ninja_poe2_currency`. It does not implement live HTTP, fetch data, write cache files, create snapshots, publish artifacts, approve a new resource, or change `RESOURCES.md`.

## Status

- Review date: `2026-05-24`
- Follow-up source check: `2026-05-26`
- Resource id: `poe_ninja_poe2_currency`
- Connector id: `poe-ninja-poe2-currency`
- Current execution status: fixture, dry-run, and fixture-daily only
- Live implementation status: `blocked`
- Blocker: no confirmed official POE2 currency endpoint URL, query parameter contract, or response-field schema was found in reviewed poe.ninja public pages.

## Reviewed Official Surfaces

- `https://poe.ninja/`
- `https://poe.ninja/poe2/economy/`
- `https://poe.ninja/posts/poe2-economy-and-rise-of-the-abyssal`
- `https://poe.ninja/privacy`
- `https://poe.ninja/poe1/data`

The POE2 economy announcement supports the product-level data shape: POE2 economy overviews based on Currency Exchange data, normalized against Chaos Orbs, Divine Orbs, and Exalted Orbs. It does not document a machine endpoint or response schema.

## Separate Official API Candidate

On `2026-05-26`, the official Path of Exile developer docs were checked as a separate source candidate:

- `https://www.pathofexile.com/developer/docs`
- `https://www.pathofexile.com/developer/docs/reference`

The official docs list a `Currency Exchange` API with `poe2` as a supported realm and documented hourly market fields. This is not poe.ninja evidence and does not unblock the poe.ninja connector. Treat it as a separate future resource/review candidate because it requires official API policy review, the `service:cxapi` scope, application/user-agent requirements, rate-limit handling, and user approval before any live HTTP implementation.

## Proposed Contract If Officially Confirmed Later

- Access method: `api`
- Cache TTL: `86400s`
- Rate limit: `6/min`
- Minimum request spacing: `10.00s`
- Cache path: use the existing fetch plan path from `wq connector-plan`
- Auth: none
- Login: none
- CAPTCHA: none
- Private data: none
- Credentials, cookies, account data, and session state: disallowed
- Public export: derived-only

Allowed local row shape should stay narrow:

- currency/item name
- category
- league, if officially present
- normalized exchange value when publicly presented
- recent movement/trend when officially present
- volume/hour or popularity metric when officially present
- source timestamp when officially present
- normalized Wraeclast Quant `0-100` signal fields after local transformation

Do not store or export raw HTML, raw pages, credentials, cookies, private account data, full raw source payloads, or source notes in public artifacts.

## Failure Behavior For A Future Live Packet

- Fail closed if connector review, resource approval, fetch plan, endpoint contract, or cache policy is missing.
- Prefer a fresh cache read when inside TTL.
- On network failure, invalid JSON, unknown schema, missing required fields, or unexpected auth/CAPTCHA/login response, return a connector policy error and do not create snapshots.
- Do not infer scores directly from raw price text; convert only confirmed fields into the existing normalized signal contract.
- Keep fixture and dry-run paths available and network-free.

## Next Recommendation

Do not implement live collection yet. Either obtain source-owner documentation/confirmation for the POE2 currency endpoint and field schema, or switch the next packet to bounded maintainability work such as `config/resources_loader.py`.
