from pathlib import Path

import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_manual_snapshot,
    load_currency_exchange_payload,
    preview_currency_exchange_rolling_baseline_diagnostics,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def test_currency_exchange_manual_snapshot_template_converts_to_payload() -> None:
    payload = load_currency_exchange_manual_snapshot(
        "examples/pathofexile_currency_exchange_manual_snapshot_template.json"
    )

    assert payload.next_change_id == 1770000000
    assert [market.market_id for market in payload.markets] == [
        "chaos|divine",
        "exalted|divine",
    ]
    assert payload.markets[0].volume_traded == {"chaos": 98200, "divine": 812}
    assert payload.markets[0].highest_ratio == {"chaos": 124, "divine": 1}


def test_currency_exchange_manual_snapshot_can_feed_preview_diagnostics() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    payload = load_currency_exchange_manual_snapshot(
        "examples/pathofexile_currency_exchange_manual_snapshot_template.json"
    )

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(payload, [baseline])

    assert diagnostics["chaos|divine"].confidence == "preview"
    assert diagnostics["chaos|divine"].observations == 1
    assert diagnostics["exalted|divine"].confidence == "preview"


def test_currency_exchange_manual_snapshot_rejects_invalid_shape(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "manual_snapshot.json"
    snapshot_path.write_text('{"markets": []}', encoding="utf-8")

    with pytest.raises(ConnectorPolicyError, match="manual snapshot"):
        load_currency_exchange_manual_snapshot(snapshot_path)
