import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_resource_file_helpers import write_connector_resources as _write_connector_resources
from cli_connector_resource_text_helpers import (
    approved_api_resources_text as _approved_api_resources_text,
)
from cli_connector_resource_text_helpers import discord_resources_text as _discord_resources_text
from cli_connector_resource_text_helpers import (
    manual_source_resources_text as _manual_source_resources_text,
)
from cli_connector_resource_text_helpers import (
    poe_ninja_currency_resources_text as _poe_ninja_currency_resources_text,
)
from cli_connector_review_file_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_check_ready_review_prints_ready_status(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Review Check" in result.output
    assert "Approved API" in result.output
    assert "yes" in result.output
    assert "ready for source-specific implementation planning" in result.output


def test_connector_candidates_prints_candidate_rows_and_draft_commands(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(
            allowed_use="manual-or-api-if-available",
            include_manual_source=True,
        ),
    )

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert "Connector Review Candidates" in result.output
    assert "poe.ninja POE2 Currency" in result.output
    assert "price_site" in result.output
    assert "needs-review" in result.output
    assert "wq connector-draft" in result.output
    assert "--resource poe_ninja_poe2_currency" in result.output
    assert "--access-method api" in result.output
    assert "advisory only" in result.output


def test_connector_candidates_marks_discord_as_compliance_gated(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert "Official Discord" in result.output
    assert "discord-gated" in result.output
    assert "Compliance-gated" in result.output


def test_connector_candidates_is_read_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available"),
    )

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert not (tmp_path / "examples").exists()
    assert not (tmp_path / "data").exists()


def test_connector_draft_writes_local_review_json(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(),
    )
    output_path = tmp_path / "review.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    from wraeclast_quant.config.connector_policy import load_connector_review

    review = load_connector_review(output_path)
    assert result.exit_code == 0
    assert "Wrote connector review draft" in result.output
    assert output_path.exists()
    assert review.resource_name == "poe.ninja POE2 Currency"
    assert review.access_method == "api"
    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert review.reviewed_at == ""
    assert review.review_notes == ""
    assert review.allowed_data_shape == ""
    assert review.dry_run_supported is True
    assert review.public_export_derived_only is True


def test_connector_review_prep_writes_draft_and_checklist(tmp_path: Path) -> None:
    resources_text = _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available")
    resources_path = _write_connector_resources(tmp_path, resources_text)
    output_dir = tmp_path / "reviews"

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    review_path = output_dir / "poe_ninja_poe2_currency_connector_review.json"
    checklist_path = output_dir / "poe_ninja_poe2_currency_review_checklist.md"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    checklist = checklist_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Connector Review Prep" in result.output
    assert "wq connector-review-status --review-path" in result.output
    assert "wq connector-approval-helper --review-path" in result.output
    assert "wq connector-check --review-path" in result.output
    assert "wq connector-plan --review-path" in result.output
    assert review["resource_name"] == "poe.ninja POE2 Currency"
    assert review["source_terms_reviewed"] is False
    assert review["robots_or_api_policy_reviewed"] is False
    assert "Source terms URL" in checklist
    assert "Allowed data shape" in checklist
    assert resources_path.read_text(encoding="utf-8") == resources_text


def test_connector_review_prep_untouched_draft_fails_connector_check(
    tmp_path: Path,
) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available"),
    )
    output_dir = tmp_path / "reviews"

    prep_result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    check_result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(output_dir / "poe_ninja_poe2_currency_connector_review.json"),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert prep_result.exit_code == 0
    assert check_result.exit_code != 0
    assert "Source terms must be reviewed." in check_result.output


def test_connector_review_prep_rejects_missing_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        "\n## Price Data\n- name: Manual Source\n  allowed_use: manual-review\n",
    )

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "missing",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(tmp_path / "reviews"),
        ],
    )

    assert result.exit_code != 0
    assert "No matching resource" in result.output


def test_connector_review_prep_rejects_discord_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "Official Discord",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(tmp_path / "reviews"),
        ],
    )

    assert result.exit_code != 0
    assert "Discord resources require explicit" in result.output


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


def test_connector_review_evidence_preserves_unrelated_fields_and_resources(
    tmp_path: Path,
) -> None:
    resources_text = _approved_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, resources_text)
    review_path = _write_connector_review(
        tmp_path,
        review_notes="Existing note.",
        rate_limit_per_minute=12,
    )

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--reviewed-at",
            "2026-05-23",
        ],
    )
    updated = json.loads(review_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert updated["review_notes"] == "Existing note."
    assert updated["rate_limit_per_minute"] == 12
    assert updated["reviewed_at"] == "2026-05-23"
    assert resources_path.read_text(encoding="utf-8") == resources_text


def test_connector_review_evidence_invalid_values_exit_nonzero(tmp_path: Path) -> None:
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--rate-limit-per-minute",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "rate_limit_per_minute must be positive" in result.output


def test_connector_check_on_untouched_draft_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _approved_api_resources_text())
    review_path = tmp_path / "draft.json"
    draft_result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "approved_api",
            "--access-method",
            "api",
            "--output-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )
    check_result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert draft_result.exit_code == 0
    assert check_result.exit_code != 0
    assert "Source terms must be reviewed." in check_result.output
    assert "Robots.txt or API policy must be reviewed." in check_result.output


def test_connector_review_status_incomplete_review_exits_zero_with_blockers(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _approved_api_resources_text())
    review_path = tmp_path / "draft.json"
    draft_result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "approved_api",
            "--access-method",
            "api",
            "--output-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )
    status_result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert draft_result.exit_code == 0
    assert status_result.exit_code == 0
    assert "Connector Review Status" in status_result.output
    assert "Approved API" in status_result.output
    assert "Source terms URL" in status_result.output
    assert "Robots/API policy URL" in status_result.output
    assert "Allowed data shape" in status_result.output
    assert "not ready" in status_result.output
    assert "Source terms must be reviewed." in status_result.output
    assert "Robots.txt or API policy must be reviewed." in status_result.output


def test_connector_review_status_invalid_json_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = tmp_path / "review.json"
    review_path.write_text("{not json", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Invalid connector review JSON" in result.output


def test_connector_draft_rejects_missing_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    output_path = tmp_path / "draft.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "Missing API",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "No matching resource found" in result.output
    assert not output_path.exists()


def test_connector_draft_rejects_discord_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())
    output_path = tmp_path / "draft.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "Official Discord",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Discord resources require explicit" in result.output
    assert not output_path.exists()


def test_connector_check_invalid_review_exits_nonzero_with_blockers(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _manual_source_resources_text())
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Manual Source",
        source_terms_reviewed=False,
    )

    result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Connector Review Check" in result.output
    assert "Manual Source" in result.output
    assert "not automation-eligible" in result.output
    assert "Source terms must be reviewed." in result.output


def test_connector_check_missing_claimed_evidence_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        source_terms_url="",
        robots_or_api_policy_url="",
        reviewed_at="",
        allowed_data_shape="",
    )

    result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Connector Review Check" in result.output
    assert "source_terms_url is required" in result.output
    assert "robots_or_api_policy_url is required" in result.output
    assert "reviewed_at is required" in result.output
    assert "allowed_data_shape is required" in result.output


def test_connector_review_status_marks_missing_claimed_evidence_blocked(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        source_terms_url="",
        robots_or_api_policy_url="",
        reviewed_at="",
        allowed_data_shape="",
    )

    result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Review Status" in result.output
    assert "Source terms URL" in result.output
    assert "blocked" in result.output
    assert "source_terms_url is required" in result.output
