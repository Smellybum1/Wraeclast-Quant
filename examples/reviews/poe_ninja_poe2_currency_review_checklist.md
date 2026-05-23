# Connector Review Checklist: poe.ninja POE2 Currency

This checklist is for manual source review only. It does not approve automation.

## Draft

- Review JSON: `examples\reviews\poe_ninja_poe2_currency_connector_review.json`
- Access method: `api`

## Human Evidence To Record

- [ ] Source terms URL
- [ ] Robots.txt or API policy URL
- [ ] Reviewed date
- [ ] Allowed data shape
- [ ] Authentication required: yes/no
- [ ] Login required: yes/no
- [ ] CAPTCHA gated: yes/no
- [ ] Private data risk: yes/no
- [ ] Rate limit per minute
- [ ] Cache TTL seconds
- [ ] Dry-run support confirmed
- [ ] Derived-only public export confirmed

## Research References

Research note: `examples\reviews\poe_ninja_poe2_currency_research.md`

Candidate surfaces to inspect manually:

- `https://poe.ninja/poe2/economy/standard/currency`
- `https://poe.ninja/poe2/economy/`
- `https://poe.ninja/posts/poe2-economy-and-rise-of-the-abyssal`
- `https://poe.ninja/posts/poe2-unique-items`
- `https://poe.ninja/privacy`
- `https://poe.ninja/poe1/data`
- `https://github.com/ayberkgezer/poe.ninja-API-Document`

These links are research starting points only. Do not mark source terms, API policy, review date, or allowed data shape as complete until the user manually verifies the source policy and intended access method.

## Safety Notes

- Do not edit `RESOURCES.md` until the review evidence is complete.
- Do not fetch, scrape, bypass access controls, or implement a connector from this checklist.
- Keep raw source data, secrets, cookies, tokens, and private data out of review files.
- Keep `allowed_data_shape` empty in the review JSON until the reviewed data shape is explicitly confirmed.

## Next Local Commands

```powershell
wq connector-review-status --review-path examples\reviews\poe_ninja_poe2_currency_connector_review.json
```

```powershell
wq connector-approval-helper --review-path examples\reviews\poe_ninja_poe2_currency_connector_review.json
```

```powershell
wq connector-check --review-path examples\reviews\poe_ninja_poe2_currency_connector_review.json
```

```powershell
wq connector-plan --review-path examples\reviews\poe_ninja_poe2_currency_connector_review.json
```
