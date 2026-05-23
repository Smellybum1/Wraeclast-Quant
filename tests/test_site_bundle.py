import json
import zipfile
from pathlib import Path

import pytest

from wraeclast_quant.reports.site_bundle import (
    REQUIRED_ARCHIVE_MEMBERS,
    REQUIRED_MANIFEST_KEYS,
    SiteBundleError,
    check_site_bundle_health,
    write_site_bundle,
)
from wraeclast_quant.reports.site_contract import (
    REQUIRED_SITE_CONTRACT_KEYS,
    SITE_CONTRACT_SCHEMA_VERSION,
    write_site_contract,
)
from wraeclast_quant.reports.publish_check import (
    check_publish_readiness,
    publish_check_payload,
    write_publish_handoff,
)
from wraeclast_quant.reports.static_site import REQUIRED_STATIC_SITE_MARKERS, write_static_site
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_write_site_bundle_copies_derived_artifacts_and_manifest(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"

    result = write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    assert result.bundle_dir == output_dir
    assert (output_dir / "index.html").read_text(encoding="utf-8") == "<h1>Wraeclast Quant</h1>"
    assert json.loads((output_dir / "public_intel.json").read_text(encoding="utf-8"))[
        "latest_run"
    ]["id"] == 7
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["product"] == "Wraeclast Quant"
    assert manifest["derived_only"] is True
    assert manifest["network_behavior"] == "none"
    assert manifest["public_intel_schema_version"] == "1.0"
    assert manifest["public_intel_latest_run_id"] == 7
    assert manifest["public_intel_top_opportunities"] == 0
    assert manifest["public_intel_alerts"] == 0


def test_write_site_bundle_creates_zip_with_expected_files(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"

    result = write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    assert result.archive_path == output_dir / "wraeclast_quant_site_bundle.zip"
    with zipfile.ZipFile(result.archive_path) as archive:
        assert sorted(archive.namelist()) == [
            "index.html",
            "manifest.json",
            "public_intel.json",
        ]


def test_write_site_bundle_rejects_missing_public_intel(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")

    with pytest.raises(SiteBundleError, match="No public intel export found"):
        write_site_bundle(
            intel_path=tmp_path / "missing.json",
            site_dir=site_dir,
            output_dir=tmp_path / "bundle",
        )


def test_write_site_bundle_rejects_missing_static_site(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_public_intel_payload()), encoding="utf-8")

    with pytest.raises(SiteBundleError, match="No static site found"):
        write_site_bundle(
            intel_path=intel_path,
            site_dir=tmp_path / "missing_site",
            output_dir=tmp_path / "bundle",
        )


def test_write_site_bundle_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    intel_path.write_text(json.dumps({"latest_run": {"id": 7}}), encoding="utf-8")
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")

    with pytest.raises(SiteBundleError, match="Public intel contract validation failed"):
        write_site_bundle(
            intel_path=intel_path,
            site_dir=site_dir,
            output_dir=tmp_path / "bundle",
        )


def test_site_bundle_manifest_excludes_source_paths_and_secrets(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"

    write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    manifest_text = (output_dir / "manifest.json").read_text(encoding="utf-8")
    assert str(tmp_path) not in manifest_text
    assert "secret-token-value" not in manifest_text
    assert ".env" in manifest_text


def test_check_site_bundle_health_reports_manifest_metadata(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=output_dir)

    health = check_site_bundle_health(output_dir)

    assert health is not None
    assert health.valid is True
    assert health.errors == []
    assert health.schema_version == "1.0"
    assert health.latest_run_id == 7
    assert health.top_opportunities_count == 0
    assert health.alerts_count == 0
    assert health.archive_size_bytes > 0


def test_check_site_bundle_health_reports_missing_manifest(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    archive_path = bundle_dir / "wraeclast_quant_site_bundle.zip"
    with zipfile.ZipFile(archive_path, mode="w") as archive:
        archive.writestr("index.html", "<h1>Wraeclast Quant</h1>")

    health = check_site_bundle_health(bundle_dir)

    assert health is not None
    assert health.valid is False
    assert "manifest.json is missing" in health.errors
    assert "archive is missing: manifest.json, public_intel.json" in health.errors


def test_check_site_bundle_health_missing_archive_returns_none(tmp_path: Path) -> None:
    assert check_site_bundle_health(tmp_path / "missing") is None


def test_static_artifact_contract_doc_matches_constants() -> None:
    doc_text = Path("docs/STATIC_ARTIFACTS.md").read_text(encoding="utf-8")

    assert _documented_bullets(doc_text, "The generated `index.html` should include these health markers:") == set(
        REQUIRED_STATIC_SITE_MARKERS
    )
    assert _documented_bullets(doc_text, "The generated `manifest.json` must include:") == REQUIRED_MANIFEST_KEYS
    assert _documented_bullets(doc_text, "The generated zip archive must include:") == REQUIRED_ARCHIVE_MEMBERS
    assert _documented_bullets(doc_text, "Top-level keys:") == REQUIRED_SITE_CONTRACT_KEYS


def test_publish_check_ready_for_fresh_valid_bundle(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is True
    assert result.latest_database_run_id == run_id
    assert result.bundle_latest_run_id == run_id
    assert result.blockers == []
    assert result.files == ["index.html", "manifest.json", "public_intel.json"]
    assert {row.key: row.status for row in result.checks}["manual_publish_readiness"] == "ready"


def test_publish_check_reports_stale_bundle(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path, artifact_run_id=1, database_runs=2)

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is False
    assert result.latest_database_run_id == 2
    assert result.bundle_latest_run_id == 1
    assert any("latest database run #2, bundle run #1" in blocker for blocker in result.blockers)


def test_publish_check_missing_bundle_is_non_mutating(tmp_path: Path) -> None:
    database_path, _bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    missing_dir = tmp_path / "missing_bundle"

    result = check_publish_readiness(database_path=database_path, bundle_dir=missing_dir)

    assert result.ready is False
    assert any("not found" in blocker for blocker in result.blockers)
    assert not missing_dir.exists()


def test_publish_check_reports_invalid_public_intel(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is False
    assert any("Public intel contract" in blocker for blocker in result.blockers)


def test_publish_check_reports_invalid_archive(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "wraeclast_quant_site_bundle.zip").write_bytes(b"not a zip")

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is False
    assert any("not a valid zip file" in blocker for blocker in result.blockers)


def test_publish_check_json_payload_has_stable_keys(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)

    payload = publish_check_payload(check_publish_readiness(database_path, bundle_dir))

    assert payload["ready"] is True
    assert payload["latest_database_run_id"] == run_id
    assert payload["bundle_latest_run_id"] == run_id
    assert isinstance(payload["checks"], list)
    assert payload["blockers"] == []


def test_publish_handoff_ready_bundle_writes_markdown(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)
    result = check_publish_readiness(database_path, bundle_dir)
    output_path = tmp_path / "publish_handoff.md"

    written_path = write_publish_handoff(result, output_path)

    report = written_path.read_text(encoding="utf-8")
    assert written_path == output_path
    assert "# Wraeclast Quant Manual Publish Handoff" in report
    assert "Manual publishing readiness: `ready`" in report
    assert f"Latest database run: `#{run_id}`" in report
    assert "wraeclast_quant_site_bundle.zip" in report
    assert "`index.html`" in report
    assert "Manual Publishing Checklist" in report
    assert "did not upload, host, publish" in report


def test_publish_handoff_not_ready_bundle_writes_blockers(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(
        tmp_path,
        artifact_run_id=1,
        database_runs=2,
    )
    result = check_publish_readiness(database_path, bundle_dir)
    output_path = tmp_path / "publish_handoff.md"

    write_publish_handoff(result, output_path)

    report = output_path.read_text(encoding="utf-8")
    assert "Manual publishing readiness: `not ready`" in report
    assert "latest database run #2, bundle run #1" in report


def test_publish_handoff_missing_bundle_does_not_create_bundle(tmp_path: Path) -> None:
    database_path, _bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    missing_dir = tmp_path / "missing_bundle"
    output_path = tmp_path / "publish_handoff.md"
    result = check_publish_readiness(database_path, missing_dir)

    write_publish_handoff(result, output_path)

    assert output_path.exists()
    assert not missing_dir.exists()
    assert "not found" in output_path.read_text(encoding="utf-8")


def test_publish_handoff_excludes_raw_inputs_and_sensitive_values(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    result = check_publish_readiness(database_path, bundle_dir)
    output_path = tmp_path / "publish_handoff.md"

    write_publish_handoff(result, output_path)

    report = output_path.read_text(encoding="utf-8")
    forbidden = [
        "raw signal inputs",
        "resource notes:",
        "RESOURCES.md content",
        "secret-token-value",
        "cookie=",
        "api_key=",
        "Stormglass Catalyst inputs",
    ]
    for value in forbidden:
        assert value not in report


def test_site_contract_ready_bundle_writes_versioned_json(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "site_contract.json"

    written_path, payload = write_site_contract(database_path, bundle_dir, output_path)

    persisted = json.loads(written_path.read_text(encoding="utf-8"))
    assert written_path == output_path
    assert persisted == payload
    assert payload["schema_version"] == SITE_CONTRACT_SCHEMA_VERSION
    assert payload["product"] == "Wraeclast Quant"
    assert payload["latest_database_run_id"] == run_id
    assert payload["artifact_run_ids"] == {
        "bundle": run_id,
        "public_intel": run_id,
        "static_site": run_id,
    }
    assert payload["public_intel"]["schema_version"] == "1.0"
    assert payload["bundle"]["bundle_type"] == "local-static-preview"
    assert payload["required_bundle_files"] == sorted(REQUIRED_ARCHIVE_MEMBERS)
    assert payload["publish_readiness"]["ready"] is True
    assert payload["safety"]["derived_only"] is True
    assert payload["safety"]["network_behavior"] == "none"


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
    assert any("Public intel contract" in blocker for blocker in payload["publish_readiness"]["blockers"])


def test_site_contract_excludes_raw_inputs_and_sensitive_values(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "site_contract.json"

    write_site_contract(database_path, bundle_dir, output_path)

    contract = output_path.read_text(encoding="utf-8")
    forbidden = [
        "raw signal inputs",
        "resource notes:",
        "RESOURCES.md content",
        "secret-token-value",
        "cookie=",
        "api_key=",
        "Stormglass Catalyst inputs",
    ]
    for value in forbidden:
        assert value not in contract


def _write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_public_intel_payload()), encoding="utf-8")
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")
    return intel_path, site_dir


def _write_publish_ready_bundle(
    tmp_path: Path,
    artifact_run_id: int | None = None,
    database_runs: int = 1,
) -> tuple[Path, Path, int]:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    latest_run_id = 0
    for _ in range(database_runs):
        latest_run_id = repository.create_analysis_run(source_mode="sample-data", item_count=1).id
    run_id = artifact_run_id or latest_run_id
    intel_path = tmp_path / "public_intel.json"
    payload = _public_intel_payload(run_id=run_id)
    intel_path.write_text(json.dumps(payload), encoding="utf-8")
    site_dir = tmp_path / "site"
    write_static_site(payload, site_dir)
    bundle_dir = tmp_path / "bundle"
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=bundle_dir)
    return database_path, bundle_dir, latest_run_id


def _public_intel_payload(run_id: int = 7) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "latest_run": {
            "id": run_id,
            "created_at": "2026-05-23T00:00:00+00:00",
            "source_mode": "sample-data",
            "item_count": 1,
        },
        "recent_runs": [],
        "top_opportunities": [],
        "score_trends": [],
        "snapshot_changes": {
            "previous_run_id": None,
            "latest_run_id": run_id,
            "top_movers": [],
            "status_changes": [],
        },
        "alerts": [],
        "outcome_summary": {"positive": 0, "neutral": 0, "negative": 0},
        "review_coverage": {
            "run_id": run_id,
            "total_recommendations": 1,
            "reviewed_recommendations": 0,
            "unreviewed_recommendations": 1,
            "reviewed_percent": 0.0,
        },
        "compliance_summary": {
            "total_resources": 1,
            "status_counts": {"manual-review": 1},
            "automation_eligible_count": 0,
        },
    }


def _documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }
