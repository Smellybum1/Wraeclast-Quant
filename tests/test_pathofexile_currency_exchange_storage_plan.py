from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    preview_currency_exchange_storage_plan,
)


def test_currency_exchange_preview_storage_plan_is_non_writing_and_secret_free() -> None:
    plan = preview_currency_exchange_storage_plan()

    assert plan.resource_id == "official_currency_exchange_api"
    assert str(plan.raw_cache_path).replace("\\", "/").endswith(
        "data/raw/cache/path-of-exile-currency-exchange-api-d9b59150fbb2.cache"
    )
    assert str(plan.baseline_observations_path).replace("\\", "/").endswith(
        "data/processed/currency_exchange/baseline_observations.preview.json"
    )
    assert plan.cache_ttl_seconds == 3600
    assert plan.stores_credentials is False
    assert plan.writes_enabled is False
