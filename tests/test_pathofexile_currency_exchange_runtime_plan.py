from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeRuntimeSettings,
    CurrencyExchangeSecretSource,
    preview_currency_exchange_runtime_plan,
    preview_currency_exchange_storage_plan,
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
