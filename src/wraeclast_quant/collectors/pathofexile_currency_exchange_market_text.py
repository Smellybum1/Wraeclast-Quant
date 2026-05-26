from __future__ import annotations

from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def currency_exchange_market_pair(market_id: str) -> tuple[str, str]:
    parts = [part.strip() for part in market_id.split("|")]
    if len(parts) != 2 or not all(parts):
        raise ConnectorPolicyError(
            "Currency Exchange market_id must contain two currency codes separated by '|'."
        )
    return parts[0], parts[1]


def currency_exchange_currency_label(code: str) -> str:
    labels = {
        "chaos": "Chaos Orb",
        "divine": "Divine Orb",
        "exalted": "Exalted Orb",
        "regal": "Regal Orb",
    }
    return labels.get(code, code.replace("_", " ").title())


def format_currency_exchange_mapping(values: dict[str, int]) -> str:
    return ", ".join(f"{key}={values[key]}" for key in sorted(values))


__all__ = [
    "currency_exchange_currency_label",
    "currency_exchange_market_pair",
    "format_currency_exchange_mapping",
]
