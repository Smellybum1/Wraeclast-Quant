from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange_connector import (
    OfficialCurrencyExchangeConnector,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_runtime import (
    CurrencyExchangeRuntimeSettings,
    CurrencyExchangeSecretSource,
)
from wraeclast_quant.config.connector_policy import load_connector_review

from source_connector_helpers import official_currency_exchange_resource as _official_currency_exchange_resource


def test_official_currency_exchange_connector_exposes_read_only_runtime_plan(
    tmp_path: Path,
) -> None:
    review = load_connector_review("examples/reviews/pathofexile_currency_exchange_connector_review.json")
    connector = OfficialCurrencyExchangeConnector.from_review(
        review,
        [_official_currency_exchange_resource()],
    )
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
    )

    runtime_plan = connector.preview_runtime_plan(settings, workspace_root=tmp_path)

    assert runtime_plan.ready is True
    assert runtime_plan.resource_name == "Path of Exile Currency Exchange API"
    assert runtime_plan.cache_path == connector.fetch_plan.cache_path
    assert runtime_plan.endpoint_path == "/currency-exchange/poe2"
    assert runtime_plan.token_grant_type == "client_credentials"
