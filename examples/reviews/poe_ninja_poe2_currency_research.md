# poe.ninja POE2 Currency Review Research

This note is a local research handoff for `poe_ninja_poe2_currency`. It does not approve automation, edit `RESOURCES.md`, fetch data, scrape pages, implement a connector, or permit live collection.

## Current Finding

poe.ninja POE2 Currency is now the first manually approved Wraeclast Quant API resource. The local review, fixture, dry-run, and fixture-daily proof paths are complete. Live collection remains blocked because no confirmed official poe.ninja POE2 machine endpoint, response-field contract, explicit reuse license, or official rate-limit table was found during the May 24, 2026 endpoint-contract review pass.

This distinction matters: `RESOURCES.md` approval and `wq connector-check` readiness allow source-specific planning, but they do not by themselves prove that a live HTTP implementation is safe or complete.

A follow-up evidence pass on May 24, 2026 rechecked the official poe.ninja home, POE2 economy page, POE2 currency page, FAQ, privacy page, data-dumps link, and POE2 economy announcement. This pass confirmed the public POE2 economy surface and table-shaped currency fields, but it did not find an official machine-readable POE2 endpoint contract. Live fetching therefore remains blocked.

## Reviewed Evidence Recorded

- Source terms/policy URL recorded in the review JSON: `https://poe.ninja/privacy`
- Robots/API/data-policy URL recorded in the review JSON: `https://poe.ninja/poe1/data`
- Review date recorded in the review JSON: `2026-05-24`
- Approved access method in `RESOURCES.md`: `api`
- Conservative rate and cache policy remain `6/min` and `86400s`.
- Allowed data shape is limited to derived POE2 currency economy summary rows and normalized Wraeclast Quant signals.

The linked privacy page is the clearest official policy page found in the poe.ninja footer. The configured currency page and official data-dumps surface were reviewed, but the exact POE2 endpoint and field contract remain undocumented in the reviewed public pages. The data dumps page is an official poe.ninja data surface, but it is PoE1-labeled and is not a dedicated PoE2 API policy. That gap should stay visible during manual approval.

## Endpoint Contract Review - 2026-05-24

Official pages reviewed:

- poe.ninja home: `https://poe.ninja/`
- Public POE2 economy landing page: `https://poe.ninja/poe2/economy/`
- poe.ninja POE2 economy announcement: `https://poe.ninja/posts/poe2-economy-and-rise-of-the-abyssal`
- Public POE2 currency page: `https://poe.ninja/poe2/economy/standard/currency`
- poe.ninja FAQ: `https://poe.ninja/faq`
- poe.ninja privacy page: `https://poe.ninja/privacy`
- poe.ninja data dumps page: `https://poe.ninja/poe1/data`

Officially evidenced:

- poe.ninja publicly links `Data dumps` and `Privacy Policy` from the site footer.
- The POE2 economy announcement describes POE2 economic overviews based on Currency Exchange data.
- The announcement says values are normalized against Chaos Orbs, Divine Orbs, and Exalted Orbs.
- The public POE2 currency page presents currency rows with `Name`, `Value`, `Last 7 days`, `Volume / Hour`, and `Most Popular` columns.
- The FAQ documents character/ladder API usage for listings, but no POE2 economy endpoint or response schema was found there.
- The privacy page is the clearest official policy page found and says it was updated September 28th, 2024.
- No authentication, login, CAPTCHA, account, credential, cookie, or private-data requirement was identified for the public review pages.

Still unconfirmed:

- Exact POE2 endpoint URL and required query parameters for currency summary data.
- Official response schema and field meanings for POE2 currency rows.
- Whether the PoE1-labeled data dumps surface applies to POE2 currency data.
- Whether the public POE2 currency table is backed by a supported API, a private site endpoint, generated static data, or another implementation detail.
- Official cache/retry/backoff guidance beyond the local conservative policy.
- Explicit source-owner permission or reuse terms for automated POE2 currency collection.

Endpoint contract status: `not ready for live implementation`.

## Candidate Access Surfaces To Review

- Public PoE2 currency/economy page: `https://poe.ninja/poe2/economy/standard/currency`
- Public PoE2 economy landing page: `https://poe.ninja/poe2/economy/`
- poe.ninja PoE2 economy announcement: `https://poe.ninja/posts/poe2-economy-and-rise-of-the-abyssal`
- poe.ninja PoE2 unique item announcement: `https://poe.ninja/posts/poe2-unique-items`
- poe.ninja privacy page: `https://poe.ninja/privacy`
- poe.ninja data dumps page: `https://poe.ninja/poe1/data`
- Community-maintained API notes for older PoE1-style endpoints: `https://github.com/ayberkgezer/poe.ninja-API-Document`

Community API notes and browser-observed endpoints may be useful research context, but they are not official poe.ninja endpoint-contract evidence and must not be treated as approval.

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

1. Seek source-owner documentation or confirmation for the exact POE2 currency endpoint and field contract.
2. If no official contract can be confirmed, keep live collection unsupported and continue with local fixtures or maintainability work.
3. If official contract evidence is confirmed, update this research note and the live-fetch design note before implementing HTTP.
4. Re-run `wq connector-review-status`, `wq connector-check`, and `wq connector-plan`.
