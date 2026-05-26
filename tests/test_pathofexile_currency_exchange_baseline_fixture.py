import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_payload,
    preview_currency_exchange_signal_fixture_from_baseline,
)
from wraeclast_quant.config.connector_fixtures import connector_fixture_signal_items
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def test_currency_exchange_preview_signal_fixture_exports_only_unblocked_baselines() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    preview = preview_currency_exchange_signal_fixture_from_baseline(baseline, [baseline])

    assert preview.source_name == "Path of Exile Currency Exchange API Preview"
    assert all(item.signals is not None for item in preview.items)
    exported = connector_fixture_signal_items(preview.items)
    assert exported[0]["name"] == "Chaos Orb / Divine Orb"
    assert exported[0]["signals"]["demand_momentum"] == 50.0
    assert exported[0]["signals"]["liquidity_score"] == 50.0
    assert exported[0]["signals"]["manipulation_risk"] == 50.0


def test_currency_exchange_preview_signal_fixture_blocks_missing_history_signals() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_broad_fixture.json")
    preview = preview_currency_exchange_signal_fixture_from_baseline(payload, [])

    assert all(item.signals is None for item in preview.items)
    assert {item.confidence for item in preview.items} == {"blocked"}
    with pytest.raises(ConnectorPolicyError, match="requires normalized signals"):
        connector_fixture_signal_items(preview.items)
