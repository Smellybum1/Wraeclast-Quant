# ADR 0003: Currency Exchange Confidential-Client Runtime

## Status

Accepted

## Context

The official Path of Exile Currency Exchange API requires the `service:cxapi` scope. The official authorization docs classify service scopes as requiring a confidential client with the `client_credentials` grant type.

Wraeclast Quant is a local-first desktop CLI. A direct public-client OAuth flow, browser-session reuse, or trade-site cookie reuse would blur the safety boundary and would not satisfy the documented `service:*` scope requirement.

## Decision

The future live Currency Exchange runtime should use a confidential-client service-token design.

- Application credentials must be created and approved outside Wraeclast Quant.
- Client secrets and bearer tokens must stay outside the repo.
- The first implementation should use memory-only access tokens for a single command invocation.
- Persistent token caching is out of scope until a separate credential-storage review approves its location and lifecycle.
- Runtime configuration must fail closed before network requests when client id, client secret source, app version, contact, realm, source review, or rate-limit safety state is missing.
- Browser cookies, trade-site sessions, public-client PKCE, POESESSID, and login-wall automation are not valid access methods for this source.

## Consequences

- The first code packet can safely implement typed configuration, user-agent construction, and failure-closed validation without making live requests.
- That first non-network settings/preflight packet now exists behind the Currency Exchange collector facade.
- A user who wants live collection must separately obtain official application credentials with the `service:cxapi` scope.
- Wraeclast Quant avoids storing long-lived secrets in project files or public artifacts.
- Persistent token caching, raw cache writes, and live fetch behavior remain separate packets with their own tests.

## Alternatives Considered

- Public-client OAuth with PKCE: rejected for this source because the required `service:cxapi` scope is a service scope.
- Browser-cookie or trade-site session reuse: rejected because it risks login-wall/session automation and bypasses the official API authorization model.
- Store client secret in project config or `.env`: rejected because repo-adjacent secrets are too easy to commit, print, or leak into artifacts.
- Persistent token cache in phase 1: deferred until a separate credential-storage review.

## Review Triggers

- The official docs change the `service:cxapi` scope or grant-type requirements.
- The user chooses a concrete secret-storage mechanism.
- Live token exchange is implemented.
- Raw cache writes or persistent token caching are implemented.
