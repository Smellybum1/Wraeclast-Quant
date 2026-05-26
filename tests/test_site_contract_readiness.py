from pathlib import Path

from wraeclast_quant.reports.site_contract import write_site_contract

from site_bundle_helpers import write_publish_ready_bundle as _write_publish_ready_bundle


def test_site_contract_stale_bundle_writes_not_ready_blockers(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(
        tmp_path,
        artifact_run_id=1,
        database_runs=2,
    )
    output_path = tmp_path / "site_contract.json"

    _written_path, payload = write_site_contract(database_path, bundle_dir, output_path)

    assert payload["publish_readiness"]["ready"] is False
    assert payload["latest_database_run_id"] == 2
    assert payload["artifact_run_ids"]["bundle"] == 1
    assert any(
        "latest database run #2, bundle run #1" in blocker
        for blocker in payload["publish_readiness"]["blockers"]
    )


def test_site_contract_missing_bundle_does_not_create_bundle(tmp_path: Path) -> None:
    database_path, _bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    missing_dir = tmp_path / "missing_bundle"
    output_path = tmp_path / "site_contract.json"

    _written_path, payload = write_site_contract(database_path, missing_dir, output_path)

    assert output_path.exists()
    assert not missing_dir.exists()
    assert payload["publish_readiness"]["ready"] is False
    assert payload["bundle"]["valid"] is False
    assert any("not found" in blocker for blocker in payload["publish_readiness"]["blockers"])


def test_site_contract_invalid_bundle_reports_blockers(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")

    _written_path, payload = write_site_contract(
        database_path,
        bundle_dir,
        tmp_path / "site_contract.json",
    )

    assert payload["publish_readiness"]["ready"] is False
    assert payload["public_intel"]["valid"] is False
    assert any(
        "Public intel contract" in blocker
        for blocker in payload["publish_readiness"]["blockers"]
    )
