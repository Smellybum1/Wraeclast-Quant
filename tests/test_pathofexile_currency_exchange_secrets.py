from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeSecretSource,
    load_currency_exchange_client_secret,
    redact_currency_exchange_secret_text,
)


def test_currency_exchange_secret_redaction_handles_tokens_and_headers() -> None:
    text = (
        'client_secret="super-secret" access_token: bearer-token '
        "refresh_token=refresh-secret Authorization: Bearer header-secret"
    )

    redacted = redact_currency_exchange_secret_text(text)

    assert "super-secret" not in redacted
    assert "bearer-token" not in redacted
    assert "refresh-secret" not in redacted
    assert "header-secret" not in redacted
    assert redacted.count("[REDACTED]") == 4


def test_currency_exchange_client_secret_loads_from_env_without_repr_leak(
    tmp_path: Path,
) -> None:
    result = load_currency_exchange_client_secret(
        CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
        env={"WQ_POE_CLIENT_SECRET": "super-secret-value"},
        workspace_root=tmp_path,
    )

    assert result.ready is True
    assert result.secret is not None
    assert result.secret.value == "super-secret-value"
    assert result.source_description == "env:WQ_POE_CLIENT_SECRET"
    assert "super-secret-value" not in repr(result.secret)
    assert "super-secret-value" not in repr(result)


def test_currency_exchange_client_secret_env_fails_closed_when_missing(
    tmp_path: Path,
) -> None:
    result = load_currency_exchange_client_secret(
        CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
        env={},
        workspace_root=tmp_path,
    )

    assert result.ready is False
    assert result.secret is None
    assert result.blockers == ("client secret environment variable is empty or missing.",)


def test_currency_exchange_client_secret_loads_from_out_of_workspace_file(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    secret_file = tmp_path / "poe-secret.txt"
    secret_file.write_text("file-secret-value\n", encoding="utf-8")

    result = load_currency_exchange_client_secret(
        CurrencyExchangeSecretSource("file", str(secret_file)),
        env={},
        workspace_root=workspace,
    )

    assert result.ready is True
    assert result.secret is not None
    assert result.secret.value == "file-secret-value"
    assert result.source_description == "file"
    assert str(secret_file) not in repr(result)
    assert "file-secret-value" not in repr(result)


def test_currency_exchange_client_secret_rejects_workspace_file_before_reading(
    tmp_path: Path,
) -> None:
    secret_file = tmp_path / "poe-secret.txt"
    secret_file.write_text("file-secret-value\n", encoding="utf-8")

    result = load_currency_exchange_client_secret(
        CurrencyExchangeSecretSource("file", str(secret_file)),
        env={},
        workspace_root=tmp_path,
    )

    assert result.ready is False
    assert result.secret is None
    assert result.blockers == (
        "client secret file must be outside the repository workspace.",
    )
