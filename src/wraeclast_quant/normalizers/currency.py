from decimal import Decimal, InvalidOperation

from pydantic import BaseModel

from wraeclast_quant.normalizers.text import normalize_whitespace


class CurrencyAmount(BaseModel):
    amount: Decimal
    currency: str


_ALIASES = {
    "ex": "exalted_orb",
    "exalt": "exalted_orb",
    "exalted": "exalted_orb",
    "exalted orb": "exalted_orb",
    "div": "divine_orb",
    "divine": "divine_orb",
    "divine orb": "divine_orb",
    "chaos": "chaos_orb",
    "chaos orb": "chaos_orb",
    "regal": "regal_orb",
    "regal orb": "regal_orb",
}


def normalize_currency_name(name: str) -> str:
    key = normalize_whitespace(name).lower().replace("_", " ")
    return _ALIASES.get(key, key.replace(" ", "_"))


def parse_currency_amount(value: str) -> CurrencyAmount:
    parts = normalize_whitespace(value).split(" ", 1)
    if len(parts) != 2:
        raise ValueError("Currency amount must include an amount and currency name.")
    try:
        amount = Decimal(parts[0])
    except InvalidOperation as exc:
        raise ValueError(f"Invalid currency amount: {parts[0]}") from exc
    return CurrencyAmount(amount=amount, currency=normalize_currency_name(parts[1]))

