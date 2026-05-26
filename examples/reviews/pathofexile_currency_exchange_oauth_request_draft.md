# Path of Exile OAuth Application Request Draft

This is a local draft for the user to review and edit before sending to Grinding Gear Games. It is not an approval record. It does not request credentials from inside Wraeclast Quant, store secrets, fetch live data, write caches, create snapshots, publish artifacts, or approve live collection.

## Recipient

`oauth@grindinggear.com`

## Subject

OAuth application request for Wraeclast Quant, `service:cxapi`

## Draft Email

Hello Grinding Gear Games OAuth team,

I would like to request OAuth application access for a Path of Exile 2 market research and decision-support project named Wraeclast Quant.

My Path of Exile account name is:

`<your-account-name#1234>`

Application name:

`Wraeclast Quant`

Application type requested:

`Confidential client`

Grant type requested:

`client_credentials`

Scope requested:

`service:cxapi`

Contact for OAuth user-agent:

`<your-contact-email-or-url>`

Intended user-agent format:

`OAuth <client-id>/<version> (contact: <contact>) WraeclastQuant`

Purpose:

Wraeclast Quant is intended to be a local-first, manual-review market intelligence tool for Path of Exile 2. It would use the official Currency Exchange API only for hourly historical aggregate Currency Exchange market data documented at `GET /currency-exchange/poe2[/<id>]`.

The tool is not intended to automate gameplay, interact with the game client, send whispers, perform trades, click UI, read the screen, bypass access controls, reuse browser sessions, use POESESSID, or use trade-site cookies.

Data handling:

- The application would request only `service:cxapi`.
- It would use documented hourly historical aggregate Currency Exchange data only.
- It would not request account profile, stash, character, guild, private-league, or private player data.
- OAuth client secrets and bearer tokens would be stored outside the project repository.
- Access tokens would initially be memory-only for a single command invocation.
- Public or shareable artifacts would include only derived summaries and local decision-support scores, not raw API payloads, credentials, tokens, cookies, or private data.

Rate-limit and reliability plan:

- The application would parse and obey dynamic rate-limit headers.
- It would stop immediately on `401`, `403`, `429`, or `Retry-After` rather than retrying aggressively.
- It would use conservative local request budgets and cache/backoff behavior before any repeated collection.
- It would treat malformed or unexpected responses as failures and would not create recommendation snapshots from failed requests.

Current implementation status:

The project currently has only local fixture parsing, dry-run connector proof, non-network OAuth runtime preflight models, redaction helpers, and secret-source validation. It does not make live API requests yet. Live collection would remain disabled unless OAuth access is approved and the runtime safety checks are implemented.

Please let me know whether this use case is acceptable under your current API policies, and whether a confidential client using `client_credentials` with the `service:cxapi` scope is the appropriate application type for this request.

Thank you,

`<your-name-or-handle>`

## Before Sending Checklist

- Replace `<your-account-name#1234>`.
- Replace `<your-contact-email-or-url>`.
- Replace `<client-id>` only if GGG has already supplied one; otherwise leave the user-agent as an intended format.
- Replace `<your-name-or-handle>`.
- Confirm whether you want to describe this as a website/backend service, a local private research tool, or both.
- Do not include a client secret, token, POESESSID, cookie, or private URL.

## Safety Notes

The official docs say registration is handled at GGG's discretion and recent low-effort or LLM-generated requests may be rejected. The user should edit this draft into their own words before sending.

