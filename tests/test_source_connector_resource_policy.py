from pathlib import Path

import pytest

from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector
from wraeclast_quant.collectors.pathofexile_currency_exchange_connector import (
    OfficialCurrencyExchangeConnector,
)
from wraeclast_quant.collectors.source_connector import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import ConnectorPolicyError

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import minimal_fixture_payload as _minimal_fixture_payload
from connector_policy_helpers import write_connector_fixture as _write_connector_fixture


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
