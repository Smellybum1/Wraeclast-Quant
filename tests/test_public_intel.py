from pathlib import Path

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.reports.public_intel import (
    build_public_intel,
)
from wraeclast_quant.storage.repositories import SnapshotRepository

from public_intel_helpers import repository_with_delta_only_runs as _repository_with_delta_only_runs
from public_intel_helpers import repository_with_runs as _repository_with_runs
from public_intel_helpers import resources as _resources


def test_public_intel_includes_latest_run_and_top_opportunities(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources), limit=1)

    assert payload is not None
    assert payload["latest_run"]["source_mode"] == "sample-data"
    assert payload["top_opportunities"] == [
        {
            "item_name": "Stormglass Catalyst",
            "opportunity_score": 76.0,
            "action": "BUY",
        }
    ]


def test_public_intel_includes_deltas_and_alerts(tmp_path: Path) -> None:
    repository = _repository_with_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is not None
    assert payload["snapshot_changes"]["previous_run_id"] == 1
    assert payload["snapshot_changes"]["latest_run_id"] == 2
    assert payload["snapshot_changes"]["top_movers"][0]["item_name"] == "Stormglass Catalyst"
    assert payload["alerts"][0]["reason"] == "Score crossed into BUY"


def test_public_intel_uses_tuned_alert_settings(tmp_path: Path) -> None:
    repository = _repository_with_delta_only_runs(tmp_path)
    resources = _resources()

    payload = build_public_intel(
        repository,
        resources,
        assess_resources(resources),
        alert_settings=AlertRuleSettings(big_positive_delta=20.0),
    )

    assert payload is not None
    assert payload["alerts"] == []


def test_public_intel_returns_none_without_snapshots(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    resources = _resources()

    payload = build_public_intel(repository, resources, assess_resources(resources))

    assert payload is None
