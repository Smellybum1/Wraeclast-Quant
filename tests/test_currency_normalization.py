from decimal import Decimal

from wraeclast_quant.normalizers.currency import normalize_currency_name, parse_currency_amount


def test_currency_normalization() -> None:
    assert normalize_currency_name("Exalted Orb") == "exalted_orb"
    assert normalize_currency_name("div") == "divine_orb"


def test_parse_currency_amount() -> None:
    amount = parse_currency_amount("12.5 ex")

    assert amount.amount == Decimal("12.5")
    assert amount.currency == "exalted_orb"

