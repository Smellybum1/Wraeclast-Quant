from pathlib import Path

from wraeclast_quant.config.connector_policy import (
    build_connector_review_draft,
    connector_review_report,
    write_connector_review_report,
)
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


def test_connector_review_report_incomplete_review_includes_blockers() -> None:
    report = connector_review_report(
        build_connector_review_draft("Approved API", "api", [_eligible_resource()]),
        [_eligible_resource()],
    )

    assert "Connector Review Report: Approved API" in report.markdown
    assert "Connector-check readiness: `not ready`" in report.markdown
    assert "Source terms must be reviewed." in report.markdown
    assert "Robots.txt or API policy must be reviewed." in report.markdown
    assert "No fetch plan is available" in report.markdown


def test_connector_review_report_ready_review_includes_fetch_plan() -> None:
    report = connector_review_report(_review(), [_eligible_resource()])

    assert report.check_result.ready is True
    assert "Connector-check readiness: `ready`" in report.markdown
    assert "## Fetch Plan Summary" in report.markdown
    assert "data/raw/cache" in report.markdown.replace("\\", "/")
    assert "Minimum request interval: `2.00s`" in report.markdown


def test_connector_review_report_auth_review_includes_auth_gates() -> None:
    report = connector_review_report(
        _review(
            authentication_required=True,
            authentication_approved=True,
            credential_storage_reviewed=True,
        ),
        [_eligible_resource()],
    )

    assert report.check_result.ready is True
    assert "Authentication required: `yes`" in report.markdown
    assert "Authentication approved: `yes`" in report.markdown
    assert "Credential storage reviewed: `yes`" in report.markdown


def test_connector_review_report_conditional_review_includes_approval_suggestion() -> None:
    report = connector_review_report(
        _review(resource_name="Conditional API"),
        [
            Resource(
                id="conditional_api",
                name="Conditional API",
                type="price_site",
                url="https://example.test/api",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert report.check_result.ready is False
    assert report.approval.suggestion_available is True
    assert "Approval suggestion: `allowed_use: api`" in report.markdown
    assert "manually update `RESOURCES.md` with `allowed_use: api`" in report.markdown


def test_connector_review_report_discord_or_missing_resource_has_no_suggestion() -> None:
    missing = connector_review_report(_review(resource_name="Missing Source"), [])
    discord = connector_review_report(
        _review(resource_name="Official Discord"),
        [
            Resource(
                name="Official Discord",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="api",
            )
        ],
    )

    assert missing.approval.suggestion_available is False
    assert "Approval suggestion: `None`" in missing.markdown
    assert "No matching resource found in RESOURCES.md." in missing.markdown
    assert discord.approval.suggestion_available is False
    assert "Approval suggestion: `None`" in discord.markdown
    assert "Discord resources require explicit approved-bot/API review." in discord.markdown


def test_connector_review_report_excludes_notes_query_strings_and_raw_data(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "review_report.md"
    review = _review(
        source_terms_url="https://example.test/terms?token=SECRET",
        robots_or_api_policy_url="https://example.test/api-policy?cookie=SECRET",
        review_notes="token SECRET cookie .env demand_momentum raw fixture row",
    )

    write_connector_review_report(review, [_eligible_resource()], output_path)
    markdown = output_path.read_text(encoding="utf-8")

    assert "https://example.test/terms" in markdown
    assert "https://example.test/api-policy" in markdown
    assert "SECRET" not in markdown
    assert "token" not in markdown.casefold()
    assert "cookie" not in markdown.casefold()
    assert ".env" not in markdown
    assert "demand_momentum" not in markdown
    assert "raw fixture row" not in markdown
