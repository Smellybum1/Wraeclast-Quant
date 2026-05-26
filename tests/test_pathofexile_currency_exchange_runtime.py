from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeRuntimeSettings,
    CurrencyExchangeSecretSource,
    currency_exchange_user_agent,
    preview_currency_exchange_runtime_preflight,
)


def test_currency_exchange_runtime_preflight_builds_identifiable_user_agent(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is True
    assert preflight.blockers == ()
    assert preflight.user_agent == (
        "OAuth wraeclast-quant/0.1.0 (contact: user@example.test) WraeclastQuant"
    )
    assert currency_exchange_user_agent(settings) == preflight.user_agent
