from pathlib import Path

import pytest

from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector
from wraeclast_quant.collectors.pathofexile_currency_exchange_connector import (
    OfficialCurrencyExchangeConnector,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_runtime import (
    CurrencyExchangeRuntimeSettings,
    CurrencyExchangeSecretSource,
)
from wraeclast_quant.collectors.source_connector import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.config.connector_policy import load_connector_review

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import minimal_fixture_payload as _minimal_fixture_payload
from connector_policy_helpers import write_connector_fixture as _write_connector_fixture
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


def test_poe_ninja_currency_connector_refuses_other_resources() -> None:
    with pytest.raises(ConnectorPolicyError, match="poe_ninja_poe2_currency"):
        PoeNinjaCurrencyConnector.from_review(_review(), [_eligible_resource()])


def test_official_currency_exchange_connector_refuses_other_resources() -> None:
    with pytest.raises(ConnectorPolicyError, match="official_currency_exchange_api"):
        OfficialCurrencyExchangeConnector.from_review(_review(), [_eligible_resource()])


def test_fixture_source_connector_refuses_incomplete_review() -> None:
    with pytest.raises(ConnectorPolicyError, match="Source terms must be reviewed"):
        FixtureSourceConnector.from_review(
            _review(source_terms_reviewed=False),
            [_eligible_resource()],
        )


def test_fixture_source_connector_exposes_fetch_plan_without_cache_writes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = _write_connector_fixture(tmp_path, _minimal_fixture_payload())
    connector = FixtureSourceConnector.from_review(_review(), [_eligible_resource()])
    result = connector.collect_fixture(fixture_path)

    assert result.fetch_plan.cache_path == connector.fetch_plan.cache_path
    assert not Path("data/raw/cache").exists()
