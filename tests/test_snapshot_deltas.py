from pathlib import Path

from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.storage.models import StoredOpportunityRecord

from cli_doc_markdown_helpers import documented_bullets as _documented_bullets


def test_score_increases_and_decreases_are_calculated() -> None:
    comparison = compare_opportunities(
        previous=[
            _stored("Rising Item", 10.0, "AVOID"),
            _stored("Falling Item", 60.0, "WATCH"),
        ],
        latest=[
            _stored("Rising Item", 25.5, "AVOID"),
            _stored("Falling Item", 55.0, "WATCH"),
        ],
        previous_run_id=1,
        latest_run_id=2,
    )
    deltas = {delta.item_name: delta for delta in comparison.deltas}

    assert deltas["Rising Item"].score_delta == 15.5
    assert deltas["Falling Item"].score_delta == -5.0


def test_action_changes_are_detected() -> None:
    comparison = compare_opportunities(
        previous=[_stored("Stormglass Catalyst", 70.0, "WATCH")],
        latest=[_stored("Stormglass Catalyst", 76.0, "BUY")],
    )

    assert comparison.status_changes[0].item_name == "Stormglass Catalyst"
    assert comparison.status_changes[0].previous_action == "WATCH"
    assert comparison.status_changes[0].latest_action == "BUY"
    assert comparison.status_changes[0].action_changed is True


def test_new_and_removed_items_are_detected() -> None:
    comparison = compare_opportunities(
        previous=[
            _stored("Removed Item", 40.0, "HOLD / SELL SELECTIVELY"),
            _stored("Shared Item", 50.0, "HOLD / SELL SELECTIVELY"),
        ],
        latest=[
            _stored("New Item", 62.0, "WATCH"),
            _stored("Shared Item", 50.0, "HOLD / SELL SELECTIVELY"),
        ],
    )
    statuses = {delta.item_name: delta.status for delta in comparison.deltas}

    assert statuses["New Item"] == "new"
    assert statuses["Removed Item"] == "removed"
    assert statuses["Shared Item"] == "changed"


def test_empty_comparison_without_previous_run_ids_is_clear() -> None:
    comparison = compare_opportunities(previous=[], latest=[], latest_run_id=1)

    assert comparison.has_comparison is False
    assert comparison.deltas == []


def test_snapshot_comparison_contract_doc_matches_statuses_and_views() -> None:
    doc_text = Path("docs/SNAPSHOT_COMPARISONS.md").read_text(encoding="utf-8")
    documented_statuses = _documented_bullets(doc_text, "Each compared item has one status:")
    documented_status_changes = _documented_bullets(doc_text, "`status_changes` includes:")
    comparison = compare_opportunities(
        previous=[
            _stored("Alpha Item", 50.0, "WATCH"),
            _stored("Beta Item", 20.0, "AVOID"),
            _stored("Removed Item", 40.0, "HOLD / SELL SELECTIVELY"),
        ],
        latest=[
            _stored("Alpha Item", 35.0, "HOLD / SELL SELECTIVELY"),
            _stored("Beta Item", 30.0, "AVOID"),
            _stored("New Item", 60.0, "WATCH"),
        ],
        previous_run_id=1,
        latest_run_id=2,
    )

    assert documented_statuses == {"changed", "new", "removed"}
    assert documented_status_changes == {
        "new items",
        "removed items",
        "changed items where action_changed is true",
    }
    assert [delta.item_name for delta in comparison.top_movers] == [
        "Alpha Item",
        "Beta Item",
    ]
    assert {delta.status for delta in comparison.deltas} == documented_statuses
    assert [delta.item_name for delta in comparison.status_changes] == [
        "Alpha Item",
        "New Item",
        "Removed Item",
    ]


def _stored(name: str, score: float, action: str) -> StoredOpportunityRecord:
    return StoredOpportunityRecord(
        id=1,
        run_id=1,
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs={
            "demand_momentum": 0,
            "build_dependency_score": 0,
            "price_discount_score": 0,
            "liquidity_score": 0,
            "historical_spike_score": 0,
            "patch_relevance_score": 0,
            "manipulation_risk": 0,
            "stale_data_penalty": 0,
        },
    )
