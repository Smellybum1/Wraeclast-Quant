import zipfile
from pathlib import Path

from wraeclast_quant.reports.site_bundle import write_site_bundle

from site_bundle_helpers import write_inputs as _write_inputs


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


def test_site_bundle_excludes_local_review_queue_worksheet(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"
    (intel_path.parent / "review_queue.md").write_text("local review worksheet", encoding="utf-8")
    (site_dir / "review_queue.md").write_text("local review worksheet", encoding="utf-8")

    result = write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    assert not (output_dir / "review_queue.md").exists()
    with zipfile.ZipFile(result.archive_path) as archive:
        assert "review_queue.md" not in archive.namelist()


def test_site_bundle_excludes_stash_ninja_companion_exports(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"
    (intel_path.parent / "exile_ui_stash_ninja_watchlist.json").write_text("{}", encoding="utf-8")
    (intel_path.parent / "exile_ui_stash_ninja_watchlist.md").write_text(
        "local companion handoff",
        encoding="utf-8",
    )
    (site_dir / "exile_ui_stash_ninja_watchlist.json").write_text("{}", encoding="utf-8")

    result = write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    assert not (output_dir / "exile_ui_stash_ninja_watchlist.json").exists()
    assert not (output_dir / "exile_ui_stash_ninja_watchlist.md").exists()
    with zipfile.ZipFile(result.archive_path) as archive:
        assert "exile_ui_stash_ninja_watchlist.json" not in archive.namelist()
        assert "exile_ui_stash_ninja_watchlist.md" not in archive.namelist()


def test_site_bundle_excludes_local_outcome_and_calibration_reports(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"
    (intel_path.parent / "outcome_review.md").write_text(
        "local outcome notes: private context",
        encoding="utf-8",
    )
    (intel_path.parent / "calibration_report.md").write_text(
        "local calibration review",
        encoding="utf-8",
    )
    (site_dir / "outcome_review.md").write_text(
        "local outcome notes: private context",
        encoding="utf-8",
    )
    (site_dir / "calibration_report.md").write_text(
        "local calibration review",
        encoding="utf-8",
    )

    result = write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    assert not (output_dir / "outcome_review.md").exists()
    assert not (output_dir / "calibration_report.md").exists()
    with zipfile.ZipFile(result.archive_path) as archive:
        assert "outcome_review.md" not in archive.namelist()
        assert "calibration_report.md" not in archive.namelist()
