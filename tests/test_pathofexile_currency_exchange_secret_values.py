from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_models import (
    CurrencyExchangeSecretSource,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_secret_values import (
    load_currency_exchange_env_secret,
    load_currency_exchange_file_secret,
)


def test_currency_exchange_env_secret_loader_preserves_source_description() -> None:
    result = load_currency_exchange_env_secret(
        CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
        {"WQ_POE_CLIENT_SECRET": " super-secret-value "},
    )

    assert result.ready is True
    assert result.secret is not None
    assert result.secret.value == "super-secret-value"
    assert result.source_description == "env:WQ_POE_CLIENT_SECRET"
    assert "super-secret-value" not in repr(result)


def test_currency_exchange_env_secret_loader_fails_closed_for_missing_value() -> None:
    result = load_currency_exchange_env_secret(
        CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
        {},
    )

    assert result.ready is False
    assert result.secret is None
    assert result.source_description == "env:WQ_POE_CLIENT_SECRET"
    assert result.blockers == ("client secret environment variable is empty or missing.",)


def test_currency_exchange_file_secret_loader_reads_trimmed_secret(tmp_path) -> None:
    secret_file = tmp_path / "poe-secret.txt"
    secret_file.write_text(" file-secret-value\n", encoding="utf-8")

    result = load_currency_exchange_file_secret(
        CurrencyExchangeSecretSource("file", str(secret_file)),
    )

    assert result.ready is True
    assert result.secret is not None
    assert result.secret.value == "file-secret-value"
    assert result.source_description == "file"
    assert "file-secret-value" not in repr(result)


def test_currency_exchange_file_secret_loader_fails_closed_for_empty_file(tmp_path) -> None:
    secret_file = tmp_path / "poe-secret.txt"
    secret_file.write_text(" \n", encoding="utf-8")

    result = load_currency_exchange_file_secret(
        CurrencyExchangeSecretSource("file", str(secret_file)),
    )

    assert result.ready is False
    assert result.secret is None
    assert result.blockers == ("client secret file is empty.",)
