from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity
from cli_snapshot_helpers import save_scored_run, save_single_opportunity_run


def reviewed_single_opportunity_database(
    tmp_path: Path,
    *,
    item_name: str = "Stormglass Catalyst",
    score: float = 76.0,
    action: str = "BUY",
    outcome: str = "positive",
    notes: str = "",
) -> tuple[Path, AnalysisRunRecord]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = save_single_opportunity_run(repository, item_name, score, action)
    repository.save_recommendation_outcome(
        run.id,
        item_name,
        outcome,
        notes=notes,
    )
    return database_path, run


def partially_reviewed_two_item_database(tmp_path: Path) -> tuple[Path, AnalysisRunRecord]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = save_scored_run(
        repository,
        [
            opportunity("Reviewed Catalyst", 76.0, "BUY"),
            opportunity("Open Catalyst", 60.0, "WATCH"),
        ],
    )
    repository.save_recommendation_outcome(run.id, "Reviewed Catalyst", "positive")
    return database_path, run


def two_run_database(tmp_path: Path) -> tuple[Path, AnalysisRunRecord, AnalysisRunRecord]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    first = save_single_opportunity_run(repository, "First Run Item", 50.0, "WATCH")
    second = save_single_opportunity_run(repository, "Second Run Item", 70.0, "BUY")
    return database_path, first, second


def two_run_database_with_second_reviewed(
    tmp_path: Path,
) -> tuple[Path, AnalysisRunRecord, AnalysisRunRecord]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    first = save_single_opportunity_run(repository, "First Run Item", 50.0, "WATCH")
    second = save_single_opportunity_run(repository, "Second Run Item", 70.0, "BUY")
    repository.save_recommendation_outcome(second.id, "Second Run Item", "positive")
    return database_path, first, second


def calibration_reviewed_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = save_scored_run(
        repository,
        [
            opportunity("Stormglass Catalyst", 76.0, "BUY"),
            opportunity("Watch Relic", 60.0, "WATCH"),
            opportunity("Hold Core", 40.0, "HOLD / SELL SELECTIVELY"),
        ],
    )
    repository.save_recommendation_outcome(run.id, "Stormglass Catalyst", "positive")
    repository.save_recommendation_outcome(run.id, "Watch Relic", "negative")
    repository.save_recommendation_outcome(run.id, "Hold Core", "neutral")
    return database_path


def fully_reviewed_calibration_prompt_database(
    tmp_path: Path,
) -> tuple[Path, AnalysisRunRecord]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = save_scored_run(
        repository,
        [
            opportunity("Avoid Good", 20.0, "AVOID"),
            opportunity("Watch Mixed", 60.0, "WATCH"),
        ],
        source_mode="manual-import",
    )
    repository.save_recommendation_outcome(run.id, "Avoid Good", "positive")
    repository.save_recommendation_outcome(run.id, "Watch Mixed", "neutral")
    return database_path, run


__all__ = [
    "calibration_reviewed_database",
    "fully_reviewed_calibration_prompt_database",
    "partially_reviewed_two_item_database",
    "reviewed_single_opportunity_database",
    "two_run_database",
    "two_run_database_with_second_reviewed",
]
