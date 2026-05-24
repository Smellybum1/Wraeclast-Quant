from __future__ import annotations

from wraeclast_quant.reports.site_contract_constants import SAFETY_STATEMENT


def safety_payload() -> dict[str, object]:
    return {
        "derived_only": True,
        "network_behavior": "none",
        "publishing_behavior": "manual-outside-app-only",
        "statement": SAFETY_STATEMENT,
    }


__all__ = ["safety_payload"]
