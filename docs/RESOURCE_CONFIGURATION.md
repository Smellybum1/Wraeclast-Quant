# Resource Configuration Contract

`RESOURCES.md` is the source of truth for Wraeclast Quant resource configuration. It is user-owned and must not be overwritten, reformatted, deleted, or replaced by automation.

The loader is intentionally tolerant. It parses common Markdown patterns into typed `Resource` objects and fills missing metadata with safe local defaults.

## Commands

```powershell
wq collect --dry-run
wq compliance
wq preflight
wq connector-candidates
wq connector-review-prep --resource <id-or-name> --access-method api
wq connector-review-status --review-path <file>
wq connector-review-report --review-path <file> --output-path <file>
wq connector-approval-helper --review-path <file>
wq connector-approval-patch --review-path <file> --output-path <file>
wq connector-check --review-path <file>
wq connector-plan --review-path <file>
```

These commands read `RESOURCES.md`. Review prep writes only the requested local review workspace, and approval patch writes only the requested local diff preview. They do not edit `RESOURCES.md`, fetch live data, scrape, publish, post alerts, or interact with the game client.

## Supported Markdown Shapes

The loader supports:

- headings such as `## Price Data`, `## Build Data`, `## Social Signals`, and `## Official Sources`
- bullet links such as `- [Example Market](https://example.test/items)`
- bullet URLs such as `- Example Market https://example.test/items`
- bullet key/value starts such as `- name: Example Market`
- indented metadata lines such as `type: price_site`, `priority: high`, `allowed_use: manual-review`, and `notes: Terms require manual review`
- simple Markdown tables with headers such as `name`, `url`, `type`, `priority`, and `allowed_use`

The parser ignores top-level non-resource content and known non-resource sections such as `Rules` and `Field Guide`.

## Resource Fields

Parsed resources may include:

- `id`
- `name`
- `url`
- `type`
- `priority`
- `allowed_use`
- `collector`
- `refresh`
- `reliability`
- `notes`
- `section`

## Safe Defaults

If metadata is missing, the loader uses these safe defaults:

- `type`: `unknown`
- `priority`: `medium`
- `allowed_use`: `manual-review`
- `reliability`: `unknown`
- `id`: ``
- `url`: ``
- `collector`: ``
- `refresh`: ``
- `notes`: ``

`type` may be inferred from the section, URL, or name before falling back to `unknown`.

## Type Inference

Current type inference recognizes:

- `price_site`
- `build_site`
- `social`
- `youtube`
- `official`
- `unknown`

Discord resources can also be represented when explicitly configured in `RESOURCES.md`; they remain compliance-gated and ineligible for automation without explicit approved-bot/API review.

## Allowed Use

`allowed_use` controls the compliance posture:

- `api`: may become automation-eligible after preflight and source-specific review.
- `rss`: may become automation-eligible after preflight and source-specific review.
- `download`: may become automation-eligible after preflight and source-specific review.
- `manual-review`: local manual review only.
- `no-automation` or `blocked`: never automate.
- unclear or conditional values: require review before any automation.

Preflight eligibility is not approval to implement a connector. Future live connectors still require the connector policy and source-specific review gates.

Current project preflight has no automation-eligible resources. Conditional values such as `manual-or-api-if-available`, `manual-review-or-api-if-available`, and `api-or-manual-review` remain blocked until a human records source evidence and manually changes `RESOURCES.md` to an explicit approved value such as `api`, `rss`, or `download`.

## Safety Notes

Resource loading is local parsing only. It must not fetch URLs, scrape websites, bypass robots.txt, bypass source terms, bypass login walls, solve CAPTCHAs, collect Discord data, publish artifacts, send webhooks, automate gameplay, send whispers, click UI, move characters, or interact with the game client.
