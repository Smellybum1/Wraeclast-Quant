# Source Review Template

Copy this template when proposing a future source-specific connector. Do not paste secrets, cookies, tokens, private URLs, or `.env` values into the review.

## Source

- Source name:
- Matching `RESOURCES.md` entry:
- Resource type:
- URL:
- Configured `allowed_use`:
- Current `wq preflight` status:

## Compliance Review

- Source terms reviewed:
- Source terms URL:
- API terms reviewed:
- Robots.txt or API policy reviewed:
- Robots.txt or API policy URL:
- Reviewed at:
- Allowed data shape:
- Authentication required:
- Authentication approved:
- Credential storage reviewed:
- Login wall, CAPTCHA, or access-control concerns:
- Discord-specific review required:
- Private data or private-message risk:

## Collection Plan

- Intended access method: API / RSS / downloadable file / manual export / other
- Data to collect:
- Data to exclude:
- Normalized output shape:
- Raw data retained locally:
- Derived fields allowed in `public_intel.json`:

## Rate Limits and Caching

- Documented rate limit:
- Connector request budget:
- Backoff behavior:
- Retry budget:
- Cache TTL:
- Failure behavior when limits are unclear:

## Safety Boundaries

- No gameplay automation:
- No in-game trading or whispers:
- No browser or client automation to bypass controls:
- No Discord user tokens:
- No private-message or private-channel collection:
- No external publishing or alert delivery:

## Tests Required

- Dry-run performs no network access:
- Successful fetch from approved source shape:
- Cache is used:
- Rate-limit or backoff behavior:
- Missing compliance metadata fails closed:
- Derived export excludes raw inputs and secrets:

## Decision

- Approved for implementation:
- Reviewer:
- Date:
- Notes:
