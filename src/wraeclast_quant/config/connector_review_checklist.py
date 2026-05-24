from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_policy_models import ConnectorReview


def render_review_checklist(review: ConnectorReview, review_path: Path) -> str:
    return "\n".join(
        [
            f"# Connector Review Checklist: {review.resource_name}",
            "",
            "This checklist is for manual source review only. It does not approve automation.",
            "",
            "## Draft",
            "",
            f"- Review JSON: `{review_path}`",
            f"- Access method: `{review.access_method}`",
            "",
            "## Human Evidence To Record",
            "",
            "- [ ] Source terms URL",
            "- [ ] Robots.txt or API policy URL",
            "- [ ] Reviewed date",
            "- [ ] Allowed data shape",
            "- [ ] Authentication required: yes/no",
            "- [ ] Login required: yes/no",
            "- [ ] CAPTCHA gated: yes/no",
            "- [ ] Private data risk: yes/no",
            "- [ ] Rate limit per minute",
            "- [ ] Cache TTL seconds",
            "- [ ] Dry-run support confirmed",
            "- [ ] Derived-only public export confirmed",
            "",
            "## Safety Notes",
            "",
            "- Do not edit `RESOURCES.md` until the review evidence is complete.",
            "- Do not fetch, scrape, bypass access controls, or implement a connector from this checklist.",
            "- Keep raw source data, secrets, cookies, tokens, and private data out of review files.",
            "",
            "## Next Local Commands",
            "",
            f"```powershell\nwq connector-review-status --review-path {review_path}\n```",
            "",
            f"```powershell\nwq connector-approval-helper --review-path {review_path}\n```",
            "",
            f"```powershell\nwq connector-check --review-path {review_path}\n```",
            "",
            f"```powershell\nwq connector-plan --review-path {review_path}\n```",
            "",
        ]
    )
