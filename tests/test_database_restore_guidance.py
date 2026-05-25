from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.backups import backup_database, build_restore_guidance
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_build_restore_guidance_verifies_backup_without_writing_target(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    target_path = tmp_path / "restored" / "snapshots.db"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    backup = backup_database(
        database_path=database_path,
        output_dir=backup_dir,
        created_at="2026-05-23T00:00:00+00:00",
    )
    assert backup is not None

    guidance = build_restore_guidance(
        backup_path=backup.backup_path,
        database_path=target_path,
    )

    assert guidance.backup_path == backup.backup_path
    assert guidance.database_path == target_path
    assert guidance.latest_run_id == run.id
    assert guidance.latest_run_source_mode == "sample-data"
    assert guidance.latest_run_item_count == len(opportunities)
    assert guidance.target_exists is False
    assert guidance.target_parent_exists is False
    assert "Copy-Item -LiteralPath" in guidance.powershell_command
    assert not target_path.exists()
    assert not target_path.parent.exists()
