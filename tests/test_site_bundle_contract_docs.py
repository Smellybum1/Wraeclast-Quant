from pathlib import Path

from wraeclast_quant.reports.site_bundle import (
    REQUIRED_ARCHIVE_MEMBERS,
    REQUIRED_MANIFEST_KEYS,
)
from wraeclast_quant.reports.site_contract import REQUIRED_SITE_CONTRACT_KEYS
from wraeclast_quant.reports.static_site import REQUIRED_STATIC_SITE_MARKERS

from site_bundle_helpers import documented_bullets as _documented_bullets


def test_static_artifact_contract_doc_matches_constants() -> None:
    doc_text = Path("docs/STATIC_ARTIFACTS.md").read_text(encoding="utf-8")

    assert _documented_bullets(doc_text, "The generated `index.html` should include these health markers:") == set(
        REQUIRED_STATIC_SITE_MARKERS
    )
    assert _documented_bullets(doc_text, "The generated `manifest.json` must include:") == REQUIRED_MANIFEST_KEYS
    assert _documented_bullets(doc_text, "The generated zip archive must include:") == REQUIRED_ARCHIVE_MEMBERS
    assert _documented_bullets(doc_text, "Top-level keys:") == REQUIRED_SITE_CONTRACT_KEYS
