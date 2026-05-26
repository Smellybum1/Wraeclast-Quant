from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.backups import backup_database
from wraeclast_quant.storage.backup_models import DatabaseBackupResult
from wraeclast_quant.storage.models import AnalysisRunRecord
from wraeclast_quant.storage.repositories import SnapshotRepository


def sample_database(tmp_path: Path) -> tuple[Path, AnalysisRunRecord, list[ScoredOpportunity]]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=len(opportunities),
        created_at="2026-05-23T00:00:00+00:00",
    )
    repository.save_scored_opportunities(run.id, opportunities)
    return database_path, run, opportunities


def sample_backup(
    tmp_path: Path,
) -> tuple[DatabaseBackupResult, AnalysisRunRecord, list[ScoredOpportunity]]:
    database_path, run, opportunities = sample_database(tmp_path)
    backup = backup_database(
        database_path=database_path,
        output_dir=tmp_path / "backups",
        created_at="2026-05-23T01:00:00+00:00",
    )
    assert backup is not None
    return backup, run, opportunities
