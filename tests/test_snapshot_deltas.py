from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities

from snapshot_delta_helpers import stored_opportunity as _stored


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
