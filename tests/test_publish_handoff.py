from pathlib import Path

from wraeclast_quant.reports.publish_check import (
    check_publish_readiness,
    write_publish_handoff,
)

from site_bundle_helpers import write_publish_ready_bundle as _write_publish_ready_bundle


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
