from pathlib import Path

from wraeclast_quant.reports.static_site import check_static_site_health, write_static_site

from static_site_helpers import payload as _payload


def test_check_static_site_health_reports_metadata(tmp_path: Path) -> None:
    output_path = write_static_site(_payload(), tmp_path / "site")

    health = check_static_site_health(output_path)

    assert health is not None
    assert health.valid is True
    assert health.missing_markers == []
    assert health.schema_version == "1.0"
    assert health.latest_run_id == 7
    assert health.size_bytes > 0


def test_check_static_site_health_reports_missing_markers(tmp_path: Path) -> None:
    index_path = tmp_path / "site" / "index.html"
    index_path.parent.mkdir()
    index_path.write_text("<html><title>Other</title></html>", encoding="utf-8")

    health = check_static_site_health(index_path)

    assert health is not None
    assert health.valid is False
    assert "heading" in health.missing_markers
    assert "schema-version" in health.missing_markers
    assert health.schema_version == ""
    assert health.latest_run_id is None


def test_check_static_site_health_missing_file_returns_none(tmp_path: Path) -> None:
    assert check_static_site_health(tmp_path / "missing" / "index.html") is None
