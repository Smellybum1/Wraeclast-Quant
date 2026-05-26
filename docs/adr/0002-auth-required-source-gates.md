# ADR 0002: Auth-Required Source Gates

## Status

Accepted

## Context

Official API sources may require OAuth scopes, identifiable user-agent/contact configuration, and credential handling before live collection is possible. The Path of Exile Currency Exchange API is the first source in this project where source approval, authentication approval, credential-storage review, dry-run proof, and live runtime behavior need to be distinct.

If those states are collapsed into one "approved" flag, future agents could accidentally treat source approval as permission to store secrets, perform token exchange, write caches, or make live requests.

## Decision

Authentication-required source reviews use separate gates:

- `allowed_use: api` in `RESOURCES.md` records source approval for planning.
- `authentication_approved` records approval to proceed with auth-aware planning and dry-run implementation.
- `credential_storage_reviewed` records that credentials and tokens must be stored outside the repo and excluded from fixtures, public artifacts, logs intended for sharing, committed files, and review notes.
- Live HTTP remains unsupported until a later implementation explicitly adds OAuth/runtime handling, user-agent/contact configuration, dynamic rate-limit parsing, cache/backoff behavior, failure-closed tests, and safe credential loading.

## Consequences

- `wq connector-check` can distinguish an auth-required review that is source-approved but still missing auth or credential-storage review.
- Dry-run connectors and fetch plans may be implemented for an auth-required source without storing secrets or making network requests.
- Live connector work still needs a separate packet and verification path.
- Review templates, checklists, status rows, and evidence commands must keep these fields visible.

## Alternatives Considered

- Keep authentication-required sources permanently blocked. Rejected because it prevents safe local planning and fixture proof for official APIs.
- Treat `allowed_use: api` as enough for live collection. Rejected because it would blur source approval with secret handling and runtime behavior.
- Store credentials in project config or review files. Rejected because it violates the local compliance and derived-only artifact boundaries.

## Review Triggers

- A live OAuth implementation is proposed.
- The project adds a secret manager, credential helper, or token cache.
- Official API terms or OAuth requirements change.
- A source requires account data, private data, browser cookies, or login-wall automation.
