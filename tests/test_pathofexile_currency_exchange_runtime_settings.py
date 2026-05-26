from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeSecretSource,
    currency_exchange_runtime_settings_from_env,
    preview_currency_exchange_runtime_preflight,
)


def test_currency_exchange_runtime_settings_from_env_does_not_expose_secret_value(
    tmp_path: Path,
) -> None:
    settings = currency_exchange_runtime_settings_from_env(
        {"WQ_POE_CLIENT_SECRET": "super-secret-value"},
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is True
    assert settings.secret_source == CurrencyExchangeSecretSource(
        "env",
        "WQ_POE_CLIENT_SECRET",
    )
    assert "super-secret-value" not in repr(settings)
    assert "super-secret-value" not in str(preflight)


def test_currency_exchange_runtime_settings_from_env_prefers_secret_file_reference(
    tmp_path: Path,
) -> None:
    secret_file = tmp_path.parent / "poe-client-secret.txt"

    settings = currency_exchange_runtime_settings_from_env(
        {
            "WQ_POE_CLIENT_SECRET_FILE": str(secret_file),
            "WQ_POE_CLIENT_SECRET": "super-secret-value",
        },
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is True
    assert settings.secret_source == CurrencyExchangeSecretSource("file", str(secret_file))
    assert "super-secret-value" not in repr(settings)
