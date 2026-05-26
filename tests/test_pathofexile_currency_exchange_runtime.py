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


def test_currency_exchange_runtime_preflight_fails_closed_without_network_config(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="",
        app_version="",
        contact="",
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is False
    assert preflight.user_agent is None
    assert preflight.blockers == (
        "client_id is required.",
        "app_version is required.",
        "user-agent contact is required.",
        "client secret source is required.",
    )


def test_currency_exchange_runtime_preflight_rejects_repo_secret_file(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource(
            "file",
            str(tmp_path / "secret.txt"),
        ),
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is False
    assert preflight.blockers == (
        "client secret file must be outside the repository workspace.",
    )


def test_currency_exchange_runtime_preflight_keeps_scope_and_realm_strict(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
        realm="pc",
        scope="account:profile",
        request_budget=0,
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is False
    assert preflight.blockers == (
        "Currency Exchange runtime currently supports only the poe2 realm.",
        "Currency Exchange runtime requires the service:cxapi scope.",
        "request_budget must be at least 1.",
    )
