import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_review_evidence_updates_json_and_prints_status(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _approved_api_resources_text())
    review_path = _write_connector_review(tmp_path, source_terms_reviewed=False)

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--source-terms-url",
            "https://example.test/terms",
            "--robots-or-api-policy-url",
            "https://example.test/api-policy",
            "--reviewed-at",
            "2026-05-23",
            "--allowed-data-shape",
            "Derived currency summary rows only.",
            "--review-notes",
            "Manual review completed.",
            "--rate-limit-per-minute",
            "30",
            "--cache-ttl-seconds",
            "3600",
        ],
    )
    updated = json.loads(review_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Updated connector review evidence" in result.output
    assert "Connector Review Status" in result.output
    assert "Readiness" in result.output
    assert updated["source_terms_reviewed"] is True
    assert updated["robots_or_api_policy_reviewed"] is True
    assert updated["source_terms_url"] == "https://example.test/terms"
    assert updated["robots_or_api_policy_url"] == "https://example.test/api-policy"
    assert updated["reviewed_at"] == "2026-05-23"
    assert updated["allowed_data_shape"] == "Derived currency summary rows only."
    assert updated["rate_limit_per_minute"] == 30
    assert updated["cache_ttl_seconds"] == 3600
