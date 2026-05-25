# Data Sources

`RESOURCES.md` is the source of truth. The app does not hardcode market resources, and automation must not overwrite or approve resources on its own. The parser contract is documented in `docs/RESOURCE_CONFIGURATION.md`.

Supported Markdown shapes include:

- Headings such as `## Price Data`
- Bullets with links
- Bullets with indented metadata
- Simple Markdown tables

Default metadata is conservative:

- `type`: inferred from heading or URL, otherwise `unknown`
- `priority`: `medium`
- `allowed_use`: `manual-review`
- `notes`: empty string

All current external collection is dry-run or placeholder-only. `wq preflight` currently reports one automation-eligible resource, `poe_ninja_poe2_currency`, after human review evidence and manual `RESOURCES.md` approval. `official_currency_exchange_api` is present as a manual-review official API draft only; it remains blocked until the user explicitly approves the resource, OAuth/app-registration path, user-agent/contact configuration, cache/backoff behavior, and live-network tests. Live connector work remains blocked for every other conditional source until a human completes source review evidence and manually updates the matching `RESOURCES.md` allowed use when appropriate.

Use these read-only or local-only helpers before any connector work:

- `wq preflight`
- `wq connector-candidates`
- `wq connector-review-prep`
- `wq connector-review-status`
- `wq connector-review-report`
- `wq connector-approval-helper`
- `wq connector-approval-patch`
- `wq connector-check`
- `wq connector-plan`

Connector fixture commands may validate synthetic local data shapes, but they do not approve live source access.
