from pathlib import Path

from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities

from cli_doc_markdown_helpers import documented_bullets as _documented_bullets
from snapshot_delta_helpers import stored_opportunity as _stored


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
