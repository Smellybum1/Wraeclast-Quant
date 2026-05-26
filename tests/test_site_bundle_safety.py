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
