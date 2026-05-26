import json
from pathlib import Path

from wraeclast_quant.reports.static_site import load_public_intel, write_static_site

from static_site_helpers import payload as _payload


def test_write_static_site_and_load_public_intel(tmp_path: Path) -> None:
    output_path = write_static_site(_payload(), tmp_path / "site")
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_payload()), encoding="utf-8")

    assert output_path == tmp_path / "site" / "index.html"
    assert output_path.exists()
    assert load_public_intel(intel_path)["latest_run"]["id"] == 7
    assert load_public_intel(tmp_path / "missing.json") is None
