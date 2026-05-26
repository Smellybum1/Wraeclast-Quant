from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeRuntimeSettings,
    CurrencyExchangeSecretSource,
    preview_currency_exchange_token_request_plan,
)


def test_currency_exchange_token_request_plan_contains_no_secret_value(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
    )

    plan = preview_currency_exchange_token_request_plan(
        settings,
        workspace_root=tmp_path,
    )

    assert plan.ready is True
    assert plan.token_url == "https://www.pathofexile.com/oauth/token"
    assert plan.grant_type == "client_credentials"
    assert plan.scope == "service:cxapi"
    assert plan.client_id == "wraeclast-quant"
    assert plan.form_fields == ("client_id", "client_secret", "grant_type", "scope")
    assert "WQ_POE_CLIENT_SECRET" not in repr(plan)
    assert "client_secret=" not in repr(plan)


def test_currency_exchange_token_request_plan_reuses_preflight_blockers(
    tmp_path: Path,
) -> None:
    plan = preview_currency_exchange_token_request_plan(
        CurrencyExchangeRuntimeSettings(client_id="", app_version="", contact=""),
        workspace_root=tmp_path,
    )

    assert plan.ready is False
    assert plan.user_agent is None
    assert plan.blockers == (
        "client_id is required.",
        "app_version is required.",
        "user-agent contact is required.",
        "client secret source is required.",
    )
