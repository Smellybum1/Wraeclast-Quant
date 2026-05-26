from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeRuntimeSettings,
    CurrencyExchangeSecretSource,
    currency_exchange_runtime_settings_from_env,
    currency_exchange_user_agent,
    load_currency_exchange_client_secret,
    preview_currency_exchange_runtime_plan,
    preview_currency_exchange_runtime_preflight,
    preview_currency_exchange_storage_plan,
    preview_currency_exchange_token_request_plan,
    preview_currency_exchange_token_response,
    redact_currency_exchange_secret_text,
)
from wraeclast_quant.config.fetch_policy_models import FetchPlan


def _fetch_plan_for_runtime_test(cache_path: Path) -> FetchPlan:
    return FetchPlan(
        resource_name="Path of Exile Currency Exchange API",
        url="https://www.pathofexile.com/developer/docs/reference",
        access_method="api",
        cache_ttl_seconds=3600,
        rate_limit_per_minute=6,
        min_seconds_between_requests=10,
        cache_path=cache_path,
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


def test_currency_exchange_runtime_plan_is_read_only_and_uses_fetch_plan(
    tmp_path: Path,
) -> None:
    storage_plan = preview_currency_exchange_storage_plan(cache_root=tmp_path / "cache")
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
    )

    runtime_plan = preview_currency_exchange_runtime_plan(
        settings,
        _fetch_plan_for_runtime_test(storage_plan.raw_cache_path),
        workspace_root=tmp_path,
    )

    assert runtime_plan.ready is True
    assert runtime_plan.resource_name == "Path of Exile Currency Exchange API"
    assert runtime_plan.endpoint_path == "/currency-exchange/poe2"
    assert runtime_plan.scope == "service:cxapi"
    assert runtime_plan.token_grant_type == "client_credentials"
    assert runtime_plan.cache_path == storage_plan.raw_cache_path
    assert runtime_plan.request_budget == 1
    assert runtime_plan.user_agent == (
        "OAuth wraeclast-quant/0.1.0 (contact: user@example.test) WraeclastQuant"
    )


def test_currency_exchange_token_response_preview_keeps_token_value_out() -> None:
    preview = preview_currency_exchange_token_response(
        {
            "access_token": "secret-token-value",
            "token_type": "bearer",
            "scope": "service:cxapi",
            "expires_in": 3600,
        }
    )

    assert preview.ready is True
    assert preview.access_token_present is True
    assert preview.token_type == "bearer"
    assert preview.scope == "service:cxapi"
    assert preview.expires_in == 3600
    assert "secret-token-value" not in repr(preview)


def test_currency_exchange_token_response_preview_fails_closed() -> None:
    preview = preview_currency_exchange_token_response(
        {
            "access_token": "",
            "token_type": "mac",
            "scope": "account:profile",
        }
    )

    assert preview.ready is False
    assert preview.access_token_present is False
    assert preview.blockers == (
        "access token is missing.",
        "token_type must be bearer.",
        "token scope must be service:cxapi.",
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
