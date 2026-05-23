# Connector Review Report: poe.ninja POE2 Currency

This report is a local audit handoff. It does not approve automation, fetch data, edit RESOURCES.md, publish artifacts, or implement a connector.

## Resource

- Resource name: `poe.ninja POE2 Currency`
- Resource id: `poe_ninja_poe2_currency`
- Resource type: `price_site`
- Current allowed_use: `api`
- Requested access method: `api`

## Preflight And Readiness

- Preflight status: `approved-api`
- Connector-check readiness: `ready`
- Approval suggestion: `None`
- Approval helper reason: No approval change needed; resource is already automation-eligible.

## Review Checklist

| Check | Value | Status |
| --- | --- | --- |
| Resource match | poe.ninja POE2 Currency | ok |
| Access method | api | ok |
| Preflight | approved-api | ok |
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
| Readiness | ready | ok |

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

- None

## Fetch Plan Summary

- Cache path: `data\raw\cache\poe-ninja-poe2-currency-a1953252fcbf.cache`
- Cache TTL: `86400s`
- Rate limit: `6/min`
- Minimum request interval: `10.00s`
- Dry-run required: `yes`
- Derived-only public export: `yes`

## Next Step

Connector review is ready for `wq connector-plan` and source-specific implementation planning.
