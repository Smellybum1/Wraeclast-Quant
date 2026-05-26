from pathlib import Path

from wraeclast_quant.storage.repositories import SnapshotRepository


def test_save_and_fetch_run_provenance(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    run = repository.create_analysis_run(source_mode="connector-fixture", item_count=2)

    saved = repository.save_run_provenance(
        run_id=run.id,
        source_kind="connector-fixture",
        resource_name="Example Approved API",
        connector_id="fixture-source-connector",
        access_method="api",
        metadata={
            "connector_class": "FixtureSourceConnector",
            "fixture_item_count": 2,
            "future_cache_path": "data/raw/cache/example.cache",
        },
    )
    fetched = repository.run_provenance(run.id)
    latest = repository.latest_run_provenance()

    assert saved.run_id == run.id
    assert fetched is not None
    assert fetched.resource_name == "Example Approved API"
    assert fetched.metadata["fixture_item_count"] == 2
    assert latest is not None
    assert latest.run_id == run.id


def test_save_report_artifact(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    run = repository.create_analysis_run(source_mode="sample-data", item_count=0)

    artifact = repository.save_report_artifact(run.id, Path("data/processed/market_brief.md"))

    assert artifact.run_id == run.id
    assert artifact.path == "data\\processed\\market_brief.md" or artifact.path == "data/processed/market_brief.md"
    assert artifact.created_at
    assert repository.report_artifacts_for_run(run.id)[0].id == artifact.id
