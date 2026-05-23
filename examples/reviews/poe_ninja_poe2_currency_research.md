# poe.ninja POE2 Currency Review Research

This note is a local research handoff for `poe_ninja_poe2_currency`. It does not approve automation, edit `RESOURCES.md`, fetch data, scrape pages, implement a connector, or permit live collection.

## Current Finding

poe.ninja is a promising source, but it remains `needs-review` for Wraeclast Quant until `RESOURCES.md` is manually approved. Public pages suggest useful data surfaces exist, but no confirmed official poe.ninja API terms, documented PoE2 endpoint contract, explicit reuse license, or official rate-limit table were found during the May 24, 2026 review pass.

## Reviewed Evidence Recorded

- Source terms/policy URL recorded in the review JSON: `https://poe.ninja/privacy`
- Robots/API/data-policy URL recorded in the review JSON: `https://poe.ninja/poe1/data`
- Review date recorded in the review JSON: `2026-05-24`
- Proposed access method remains `api`, but live access remains blocked until manual approval.
- Conservative rate and cache policy remain `6/min` and `86400s`.
- Allowed data shape is limited to derived POE2 currency economy summary rows and normalized Wraeclast Quant signals.

The linked privacy page is the clearest official policy page found in the poe.ninja footer. The configured currency page and official data-dumps surface were reviewed, but the exact POE2 endpoint and field contract remain undocumented in the reviewed public pages. The data dumps page is an official poe.ninja data surface, but it is PoE1-labeled and is not a dedicated PoE2 API policy. That gap should stay visible during manual approval.

## Candidate Access Surfaces To Review

- Public PoE2 currency/economy page: `https://poe.ninja/poe2/economy/standard/currency`
- Public PoE2 economy landing page: `https://poe.ninja/poe2/economy/`
- poe.ninja PoE2 economy announcement: `https://poe.ninja/posts/poe2-economy-and-rise-of-the-abyssal`
- poe.ninja PoE2 unique item announcement: `https://poe.ninja/posts/poe2-unique-items`
- poe.ninja privacy page: `https://poe.ninja/privacy`
- poe.ninja data dumps page: `https://poe.ninja/poe1/data`
- Community-maintained API notes for older PoE1-style endpoints: `https://github.com/ayberkgezer/poe.ninja-API-Document`

## Evidence Gaps

- Confirm whether poe.ninja publishes official API terms or explicit permission for automated access beyond the reviewed public pages.
- Confirm whether there is a preferred PoE2 data dump or API endpoint for currency summaries.
- Confirm robots.txt or API policy expectations beyond the official data dumps surface.
- Confirm official rate limits, request spacing, cache expectations, and attribution requirements.
- Confirm whether authentication, login, cookies, CAPTCHA, or account access are required.
- Confirm the exact allowed data shape before setting `allowed_data_shape` in the review JSON.

## Conservative Interpretation

- Public pages are not the same as approval for automated collection.
- Community API documentation is useful research context but is not official poe.ninja approval.
- Data dumps, if available and permitted for PoE2, should be preferred over scraping rendered pages.
- Any future connector should collect only derived currency summary rows, cache aggressively, support dry-run, and exclude raw source pages from public exports.

## Next Manual Steps

1. Inspect poe.ninja terms, privacy, data dump, API, and contact/support pages manually.
2. Decide whether the reviewed access method is `api`, `download`, or `manual-export`.
3. Record only verified evidence with `wq connector-review-evidence`.
4. Re-run `wq connector-review-status`.
5. Use `wq connector-approval-helper` and `wq connector-approval-patch` only after evidence is complete.
6. Run `wq connector-check` and `wq connector-plan` before any source-specific implementation plan.
