# Connector Review Report: poe.ninja POE2 Currency

This report is a local audit handoff. It does not approve automation, fetch data, edit RESOURCES.md, publish artifacts, or implement a connector.

## Resource

- Resource name: `poe.ninja POE2 Currency`
- Resource id: `poe_ninja_poe2_currency`
- Resource type: `price_site`
- Current allowed_use: `manual-or-api-if-available`
- Requested access method: `api`

## Preflight And Readiness

- Preflight status: `needs-review`
- Connector-check readiness: `not ready`
- Approval suggestion: `allowed_use: api`
- Approval helper reason: After human approval, manually update RESOURCES.md with the suggested allowed_use.

## Review Checklist

| Check | Value | Status |
| --- | --- | --- |
| Resource match | poe.ninja POE2 Currency | ok |
| Access method | api | ok |
| Preflight | needs-review | blocked |
| Source terms reviewed | yes | ok |
| Source terms URL | https://poe.ninja/privacy | ok |
| Robots/API policy reviewed | yes | ok |
| Robots/API policy URL | https://poe.ninja/poe1/data | ok |
| Reviewed at | 2026-05-24 | ok |
| Allowed data shape | Derived POE2 currency economy summary rows only: currency/item name, category, league, normalized exchange value when publicly presented, 7-day movement/trend, volume/hour or popularity metric when publicly presented, source timestamp, and normalized 0-100 Wraeclast Quant signals. Excludes raw pages, raw HTML, account data, credentials, cookies, private data, and public export of raw source content. | ok |
| Review notes | recorded | ok |
| Authentication required | no | ok |
| Login required | no | ok |
| CAPTCHA gated | no | ok |
| Private data risk | no | ok |
| Rate limit | 6/min | ok |
| Cache TTL | 86400s | ok |
| Dry-run supported | yes | ok |
| Derived-only public export | yes | ok |
| Readiness | not ready | blocked |

## Evidence

- Source terms reviewed: `yes`
- Source terms URL: `https://poe.ninja/privacy`
- Robots/API policy reviewed: `yes`
- Robots/API policy URL: `https://poe.ninja/poe1/data`
- Reviewed at: `2026-05-24`
- Allowed data shape: Derived POE2 currency economy summary rows only: currency/item name, category, league, normalized exchange value when publicly presented, 7-day movement/trend, volume/hour or popularity metric when publicly presented, source timestamp, and normalized 0-100 Wraeclast Quant signals. Excludes raw pages, raw HTML, account data, credentials, cookies, private data, and public export of raw source content.
- Review notes recorded: `yes`

## Safety Flags

- Authentication required: `no`
- Login required: `no`
- CAPTCHA gated: `no`
- Private data risk: `no`
- Dry-run supported: `yes`
- Derived-only public export: `yes`

## Limits

- Rate limit: `6/min`
- Cache TTL: `86400s`

## Blockers

- Resource is not automation-eligible: needs-review - Allowed use is conditional or unclear; review source terms before automation.

## Fetch Plan Summary

- No fetch plan is available until connector-check passes.

## Next Step

After human approval, manually update `RESOURCES.md` with `allowed_use: api`, then rerun `wq connector-check`.
