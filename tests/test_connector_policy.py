import json
from pathlib import Path

import pytest

from wraeclast_quant.collectors.poe_ninja import PoeNinjaCurrencyConnector
from wraeclast_quant.collectors.source_connector import (
    FixtureSourceConnector,
    source_connector_from_review,
)
from wraeclast_quant.config.connector_candidates import connector_candidates, suggested_access_method
from wraeclast_quant.config.connector_fixtures import (
    export_connector_fixture_signals,
    load_connector_fixture,
    run_connector_fixture,
)
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    build_connector_review_draft,
    connector_approval_patch,
    check_connector_review,
    connector_approval_helper,
    connector_review_report,
    connector_review_status,
    load_connector_review,
    prepare_connector_review_workspace,
    update_connector_review_evidence,
    write_connector_review_report,
)
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource
from wraeclast_quant.importers.manual import load_manual_items

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import connector_review_payload as _review_payload
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import poe_ninja_currency_resource as _poe_ninja_currency_resource


def test_valid_api_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(),
        [
            Resource(
                name="Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            )
        ],
    )

    assert result.ready is True
    assert result.blockers == []


def test_valid_rss_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(access_method="rss"),
        [
            Resource(
                name="Approved API",
                type="official",
                url="https://example.test/feed.xml",
                allowed_use="rss",
            )
        ],
    )

    assert result.ready is True


def test_valid_download_review_for_eligible_resource_passes() -> None:
    result = check_connector_review(
        _review(access_method="download", resource_name="Approved Download"),
        [
            Resource(
                name="Approved Download",
                type="official",
                url="https://example.test/data.json",
                allowed_use="download",
            )
        ],
    )

    assert result.ready is True
    assert result.blockers == []


def test_example_connector_review_files_are_ready_for_matching_resources() -> None:
    cases = [
        (
            Path("examples/connector_review_api_example.json"),
            Resource(
                name="Example Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            ),
            "api",
        ),
        (
            Path("examples/connector_review_rss_example.json"),
            Resource(
                name="Example Approved RSS",
                type="official",
                url="https://example.test/feed.xml",
                allowed_use="rss",
            ),
            "rss",
        ),
        (
            Path("examples/connector_review_download_example.json"),
            Resource(
                name="Example Approved Download",
                type="official",
                url="https://example.test/data.json",
                allowed_use="download",
            ),
            "download",
        ),
    ]

    for review_path, resource, access_method in cases:
        review = load_connector_review(review_path)
        check = check_connector_review(review, [resource])
        plan = build_fetch_plan(review, [resource])

        assert review.access_method == access_method
        assert check.ready is True
        assert check.blockers == []
        assert plan.plan is not None
        assert plan.plan.access_method == access_method


def test_missing_resource_fails_clearly() -> None:
    result = check_connector_review(_review(), [])

    assert result.ready is False
    assert "No matching resource found in RESOURCES.md." in result.blockers


def test_preflight_ineligible_resource_fails() -> None:
    result = check_connector_review(
        _review(),
        [Resource(name="Approved API", allowed_use="manual-review")],
    )

    assert result.ready is False
    assert any("not automation-eligible" in blocker for blocker in result.blockers)


def test_discord_review_fails_even_if_fields_look_permissive() -> None:
    result = check_connector_review(
        _review(),
        [
            Resource(
                name="Approved API",
                type="discord",
                url="https://discord.com/channels/example",
                allowed_use="api",
            )
        ],
    )

    assert result.ready is False
    assert any("Discord" in blocker for blocker in result.blockers)


def test_missing_terms_or_policy_review_fails() -> None:
    result = check_connector_review(
        _review(source_terms_reviewed=False, robots_or_api_policy_reviewed=False),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "Source terms must be reviewed." in result.blockers
    assert "Robots.txt or API policy must be reviewed." in result.blockers


def test_missing_source_terms_url_blocks_when_terms_are_marked_reviewed() -> None:
    result = check_connector_review(
        _review(source_terms_url=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "source_terms_url is required when source terms are reviewed." in result.blockers


def test_missing_robots_or_api_policy_url_blocks_when_policy_is_marked_reviewed() -> None:
    result = check_connector_review(
        _review(robots_or_api_policy_url=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert (
        "robots_or_api_policy_url is required when robots/API policy is reviewed."
        in result.blockers
    )


def test_missing_reviewed_at_blocks_when_review_confirmations_are_complete() -> None:
    result = check_connector_review(
        _review(reviewed_at=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "reviewed_at is required when review confirmations are complete." in result.blockers


def test_missing_allowed_data_shape_blocks_when_review_confirmations_are_complete() -> None:
    result = check_connector_review(
        _review(allowed_data_shape=""),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert (
        "allowed_data_shape is required when review confirmations are complete."
        in result.blockers
    )


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("authentication_required", "Authentication-required"),
        ("login_required", "Login-required"),
        ("captcha_gated", "CAPTCHA-gated"),
        ("private_data_risk", "Private data"),
    ],
)
def test_auth_login_captcha_or_private_data_flags_fail(field: str, expected: str) -> None:
    result = check_connector_review(_review(**{field: True}), [_eligible_resource()])

    assert result.ready is False
    assert any(expected in blocker for blocker in result.blockers)


def test_non_positive_cache_or_rate_limit_fails() -> None:
    result = check_connector_review(
        _review(rate_limit_per_minute=0, cache_ttl_seconds=0),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "rate_limit_per_minute must be positive." in result.blockers
    assert "cache_ttl_seconds must be positive." in result.blockers


def test_missing_dry_run_or_derived_only_export_confirmation_fails() -> None:
    result = check_connector_review(
        _review(dry_run_supported=False, public_export_derived_only=False),
        [_eligible_resource()],
    )

    assert result.ready is False
    assert "Dry-run support must be explicitly confirmed." in result.blockers
    assert "Public export must be derived-only." in result.blockers


def test_unsupported_access_method_fails() -> None:
    result = check_connector_review(_review(access_method="browser"), [_eligible_resource()])

    assert result.ready is False
    assert any("access_method" in blocker for blocker in result.blockers)


def test_load_connector_review_reads_json(tmp_path: Path) -> None:
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(_review_payload()), encoding="utf-8")

    review = load_connector_review(review_path)

    assert review.resource_name == "Approved API"
    assert review.access_method == "api"


def test_load_connector_review_accepts_legacy_json_without_evidence(tmp_path: Path) -> None:
    review_path = tmp_path / "legacy_review.json"
    payload = _review_payload()
    for key in [
        "source_terms_url",
        "robots_or_api_policy_url",
        "reviewed_at",
        "review_notes",
        "allowed_data_shape",
    ]:
        del payload[key]
    review_path.write_text(json.dumps(payload), encoding="utf-8")

    review = load_connector_review(review_path)
    result = check_connector_review(review, [_eligible_resource()])

    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert review.reviewed_at == ""
    assert review.review_notes == ""
    assert review.allowed_data_shape == ""
    assert result.ready is False
    assert "source_terms_url is required when source terms are reviewed." in result.blockers
    assert (
        "robots_or_api_policy_url is required when robots/API policy is reviewed."
        in result.blockers
    )
    assert "reviewed_at is required when review confirmations are complete." in result.blockers
    assert (
        "allowed_data_shape is required when review confirmations are complete."
        in result.blockers
    )


def test_load_connector_review_rejects_invalid_json(tmp_path: Path) -> None:
    review_path = tmp_path / "review.json"
    review_path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ConnectorPolicyError, match="Invalid connector review JSON"):
        load_connector_review(review_path)


def test_connector_review_draft_resolves_resource_by_id() -> None:
    review = build_connector_review_draft(
        resource_name="approved_api",
        access_method="api",
        resources=[
            Resource(
                id="approved_api",
                name="Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            )
        ],
    )

    assert review.resource_name == "Approved API"
    assert review.access_method == "api"


def test_connector_review_draft_resolves_resource_by_name() -> None:
    review = build_connector_review_draft(
        resource_name="Approved API",
        access_method="rss",
        resources=[
            Resource(
                id="approved_api",
                name="Approved API",
                type="official",
                url="https://example.test/feed.xml",
                allowed_use="rss",
            )
        ],
    )

    assert review.resource_name == "Approved API"
    assert review.access_method == "rss"


def test_connector_review_draft_rejects_unsupported_access_method() -> None:
    with pytest.raises(ConnectorPolicyError, match="access_method"):
        build_connector_review_draft(
            resource_name="Approved API",
            access_method="browser",
            resources=[_eligible_resource()],
        )


def test_connector_review_draft_rejects_missing_resource() -> None:
    with pytest.raises(ConnectorPolicyError, match="No matching resource"):
        build_connector_review_draft(
            resource_name="Missing API",
            access_method="api",
            resources=[_eligible_resource()],
        )


def test_connector_review_draft_rejects_discord_resource() -> None:
    with pytest.raises(ConnectorPolicyError, match="Discord resources require explicit"):
        build_connector_review_draft(
            resource_name="Official Discord",
            access_method="api",
            resources=[
                Resource(
                    name="Official Discord",
                    type="discord",
                    url="https://discord.gg/example",
                    allowed_use="api",
                )
            ],
        )


def test_connector_review_draft_defaults_are_conservative_and_not_ready() -> None:
    review = build_connector_review_draft(
        resource_name="Approved API",
        access_method="api",
        resources=[_eligible_resource()],
    )
    result = check_connector_review(review, [_eligible_resource()])

    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert review.reviewed_at == ""
    assert review.review_notes == ""
    assert review.allowed_data_shape == ""
    assert review.authentication_required is False
    assert review.login_required is False
    assert review.captcha_gated is False
    assert review.private_data_risk is False
    assert review.rate_limit_per_minute == 6
    assert review.cache_ttl_seconds == 86400
    assert review.dry_run_supported is True
    assert review.public_export_derived_only is True
    assert result.ready is False
    assert "Source terms must be reviewed." in result.blockers
    assert "Robots.txt or API policy must be reviewed." in result.blockers


def test_connector_review_prep_resolves_resource_and_writes_workspace(
    tmp_path: Path,
) -> None:
    prep = prepare_connector_review_workspace(
        resource_name="poe_ninja_poe2_currency",
        access_method="api",
        resources=[
            Resource(
                id="poe_ninja_poe2_currency",
                name="poe.ninja POE2 Currency",
                type="price_site",
                url="https://poe.ninja/poe2/economy/vaal/currency",
                allowed_use="manual-or-api-if-available",
            )
        ],
        output_dir=tmp_path,
    )
    review = load_connector_review(prep.review_path)
    checklist = prep.checklist_path.read_text(encoding="utf-8")
    result = check_connector_review(review, [_eligible_resource()])

    assert prep.review_path == tmp_path / "poe_ninja_poe2_currency_connector_review.json"
    assert prep.checklist_path == tmp_path / "poe_ninja_poe2_currency_review_checklist.md"
    assert review.resource_name == "poe.ninja POE2 Currency"
    assert review.access_method == "api"
    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert "Source terms URL" in checklist
    assert "Robots.txt or API policy URL" in checklist
    assert "Allowed data shape" in checklist
    assert "Dry-run support confirmed" in checklist
    assert any("connector-review-status" in command for command in prep.next_commands)
    assert result.ready is False


def test_connector_review_prep_rejects_missing_resource(tmp_path: Path) -> None:
    with pytest.raises(ConnectorPolicyError, match="No matching resource"):
        prepare_connector_review_workspace(
            resource_name="missing",
            access_method="api",
            resources=[_eligible_resource()],
            output_dir=tmp_path,
        )


def test_connector_review_prep_rejects_discord_resource(tmp_path: Path) -> None:
    with pytest.raises(ConnectorPolicyError, match="Discord resources require explicit"):
        prepare_connector_review_workspace(
            resource_name="Official Discord",
            access_method="api",
            resources=[
                Resource(
                    name="Official Discord",
                    type="discord",
                    url="https://discord.gg/example",
                    allowed_use="api",
                )
            ],
            output_dir=tmp_path,
        )


def test_connector_review_evidence_source_terms_url_sets_reviewed() -> None:
    updated = update_connector_review_evidence(
        build_connector_review_draft("Approved API", "api", [_eligible_resource()]),
        source_terms_url="https://example.test/terms",
    )

    assert updated.source_terms_reviewed is True
    assert updated.source_terms_url == "https://example.test/terms"
    assert updated.robots_or_api_policy_reviewed is False


def test_connector_review_evidence_policy_url_sets_reviewed() -> None:
    updated = update_connector_review_evidence(
        build_connector_review_draft("Approved API", "api", [_eligible_resource()]),
        robots_or_api_policy_url="https://example.test/api-policy",
    )

    assert updated.robots_or_api_policy_reviewed is True
    assert updated.robots_or_api_policy_url == "https://example.test/api-policy"
    assert updated.source_terms_reviewed is False


def test_connector_review_evidence_preserves_omitted_fields() -> None:
    review = _review(review_notes="Existing note.", rate_limit_per_minute=12)

    updated = update_connector_review_evidence(
        review,
        reviewed_at="2026-05-23",
        allowed_data_shape="Derived currency summary rows only.",
    )

    assert updated.review_notes == "Existing note."
    assert updated.rate_limit_per_minute == 12
    assert updated.reviewed_at == "2026-05-23"
    assert updated.allowed_data_shape == "Derived currency summary rows only."


def test_connector_review_evidence_rejects_invalid_rate_limit_or_cache_ttl() -> None:
    review = build_connector_review_draft("Approved API", "api", [_eligible_resource()])

    with pytest.raises(ConnectorPolicyError, match="rate_limit_per_minute"):
        update_connector_review_evidence(review, rate_limit_per_minute=0)

    with pytest.raises(ConnectorPolicyError, match="cache_ttl_seconds"):
        update_connector_review_evidence(review, cache_ttl_seconds=0)


def test_connector_review_evidence_complete_review_can_pass_evidence_gate() -> None:
    updated = update_connector_review_evidence(
        build_connector_review_draft("Approved API", "api", [_eligible_resource()]),
        source_terms_url="https://example.test/terms",
        robots_or_api_policy_url="https://example.test/api-policy",
        reviewed_at="2026-05-23",
        allowed_data_shape="Derived currency summary rows only.",
        review_notes="Manual review completed.",
        rate_limit_per_minute=30,
        cache_ttl_seconds=3600,
    )
    result = check_connector_review(updated, [_eligible_resource()])

    assert result.ready is True
    assert result.blockers == []


def test_connector_review_status_reports_incomplete_draft_blockers() -> None:
    review = build_connector_review_draft(
        resource_name="Approved API",
        access_method="api",
        resources=[_eligible_resource()],
    )
    status = connector_review_status(review, [_eligible_resource()])
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Resource match"].status == "ok"
    assert row_by_check["Source terms reviewed"].value == "no"
    assert row_by_check["Source terms reviewed"].status == "needs-review"
    assert row_by_check["Source terms URL"].status == "needs-review"
    assert row_by_check["Robots/API policy reviewed"].status == "needs-review"
    assert row_by_check["Robots/API policy URL"].status == "needs-review"
    assert row_by_check["Reviewed at"].status == "optional"
    assert row_by_check["Allowed data shape"].status == "optional"
    assert row_by_check["Readiness"].value == "not ready"
    assert "Source terms must be reviewed." in status.check_result.blockers


def test_connector_review_status_reports_ready_review() -> None:
    status = connector_review_status(_review(), [_eligible_resource()])
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is True
    assert row_by_check["Preflight"].status == "ok"
    assert row_by_check["Source terms URL"].status == "ok"
    assert row_by_check["Robots/API policy URL"].status == "ok"
    assert row_by_check["Reviewed at"].status == "ok"
    assert row_by_check["Allowed data shape"].status == "ok"
    assert row_by_check["Readiness"].value == "ready"
    assert status.check_result.blockers == []


def test_connector_review_status_marks_missing_claimed_evidence_blocked() -> None:
    status = connector_review_status(
        _review(
            source_terms_url="",
            robots_or_api_policy_url="",
            reviewed_at="",
            allowed_data_shape="",
        ),
        [_eligible_resource()],
    )
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Source terms reviewed"].status == "ok"
    assert row_by_check["Source terms URL"].status == "blocked"
    assert row_by_check["Robots/API policy URL"].status == "blocked"
    assert row_by_check["Reviewed at"].status == "blocked"
    assert row_by_check["Allowed data shape"].status == "blocked"


def test_connector_review_status_reports_missing_resource_as_blocked() -> None:
    status = connector_review_status(_review(), [])
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Resource match"].status == "blocked"
    assert row_by_check["Preflight"].value == "missing"
    assert "No matching resource found in RESOURCES.md." in status.check_result.blockers


def test_connector_review_status_keeps_discord_blocked() -> None:
    status = connector_review_status(
        _review(),
        [
            Resource(
                name="Approved API",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="api",
            )
        ],
    )
    row_by_check = {row.check: row for row in status.rows}

    assert status.check_result.ready is False
    assert row_by_check["Preflight"].value == "discord-gated"
    assert any("Discord" in blocker for blocker in status.check_result.blockers)


def test_poe_ninja_currency_review_workspace_is_incomplete() -> None:
    review = load_connector_review("examples/poe_ninja_poe2_currency_connector_review.json")
    result = check_connector_review(
        review,
        [
            Resource(
                id="poe_ninja_poe2_currency",
                name="poe.ninja POE2 Currency",
                type="price_site",
                url="https://poe.ninja/poe2/economy/vaal/currency",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert result.ready is False
    assert "Source terms must be reviewed." in result.blockers


def test_connector_approval_helper_suggests_allowed_use_for_complete_conditional_review() -> None:
    result = connector_approval_helper(
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

    assert result.suggestion_available is True
    assert result.approval_suggestion == "allowed_use: api"
    assert result.evidence_ready is True
    assert result.connector_check_ready is False


def test_connector_approval_helper_with_incomplete_evidence_has_no_suggestion() -> None:
    result = connector_approval_helper(
        _review(resource_name="Conditional API", source_terms_url=""),
        [
            Resource(
                name="Conditional API",
                url="https://example.test/api",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert result.suggestion_available is False
    assert result.approval_suggestion == "None"
    assert result.evidence_ready is False
    assert "source_terms_url is required" in "\n".join(result.blockers)


def test_connector_approval_helper_has_no_suggestion_for_discord() -> None:
    result = connector_approval_helper(
        _review(resource_name="Official Discord"),
        [
            Resource(
                name="Official Discord",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="manual-or-api-if-available",
            )
        ],
    )

    assert result.suggestion_available is False
    assert "Discord" in result.reason


def test_connector_approval_helper_has_no_suggestion_for_missing_resource() -> None:
    result = connector_approval_helper(_review(resource_name="Missing Source"), [])

    assert result.suggestion_available is False
    assert result.resource is None
    assert "No matching resource" in result.reason


def test_connector_approval_helper_reports_no_change_for_already_eligible_resource() -> None:
    result = connector_approval_helper(_review(), [_eligible_resource()])

    assert result.suggestion_available is False
    assert result.connector_check_ready is True
    assert result.approval_suggestion == "None"
    assert "already automation-eligible" in result.reason


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


def test_connector_approval_patch_complete_conditional_review_changes_allowed_use_only() -> None:
    resources_markdown = """
## Price Data
- id: conditional_api
  name: Conditional API
  type: price_site
  url: https://example.test/api
  allowed_use: manual-or-api-if-available
  notes: keep this private
"""
    resource = Resource(
        id="conditional_api",
        name="Conditional API",
        type="price_site",
        url="https://example.test/api",
        allowed_use="manual-or-api-if-available",
        notes="keep this private",
    )

    result = connector_approval_patch(
        _review(resource_name="Conditional API"),
        [resource],
        resources_markdown,
    )

    assert result.patch_available is True
    assert "-  allowed_use: manual-or-api-if-available" in result.patch_text
    assert "+  allowed_use: api" in result.patch_text
    assert "notes" not in result.patch_text
    assert "https://example.test/api" not in result.patch_text


def test_connector_approval_patch_incomplete_evidence_has_no_patch() -> None:
    resource = Resource(
        name="Conditional API",
        type="price_site",
        url="https://example.test/api",
        allowed_use="manual-or-api-if-available",
    )

    result = connector_approval_patch(
        _review(resource_name="Conditional API", source_terms_url=""),
        [resource],
        "- name: Conditional API\n  allowed_use: manual-or-api-if-available\n",
    )

    assert result.patch_available is False
    assert result.patch_text == ""
    assert "source_terms_url is required" in "\n".join(result.blockers)


def test_connector_approval_patch_discord_and_missing_resource_have_no_patch() -> None:
    missing = connector_approval_patch(
        _review(resource_name="Missing Source"),
        [],
        "",
    )
    discord = connector_approval_patch(
        _review(resource_name="Official Discord"),
        [
            Resource(
                name="Official Discord",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="api",
            )
        ],
        "- name: Official Discord\n  allowed_use: api\n",
    )

    assert missing.patch_available is False
    assert "No matching resource" in missing.reason
    assert discord.patch_available is False
    assert "Discord" in discord.reason


def test_connector_approval_patch_already_eligible_has_no_patch() -> None:
    result = connector_approval_patch(
        _review(),
        [_eligible_resource()],
        "- name: Approved API\n  allowed_use: api\n",
    )

    assert result.patch_available is False
    assert result.patch_text == ""
    assert "already automation-eligible" in result.reason


def test_connector_approval_patch_sanitizes_patch_preview() -> None:
    resources_markdown = """
## Price Data
- id: conditional_api
  name: Conditional API
  type: price_site
  url: https://example.test/api?token=SECRET
  allowed_use: manual-or-api-if-available
  notes: cookie SECRET .env demand_momentum raw fixture row
"""
    resource = Resource(
        id="conditional_api",
        name="Conditional API",
        type="price_site",
        url="https://example.test/api?token=SECRET",
        allowed_use="manual-or-api-if-available",
        notes="cookie SECRET .env demand_momentum raw fixture row",
    )

    result = connector_approval_patch(
        _review(resource_name="Conditional API"),
        [resource],
        resources_markdown,
    )

    assert result.patch_available is True
    assert "allowed_use: api" in result.patch_text
    assert "SECRET" not in result.patch_text
    assert "cookie" not in result.patch_text.casefold()
    assert ".env" not in result.patch_text
    assert "demand_momentum" not in result.patch_text
    assert "raw fixture row" not in result.patch_text


def test_connector_approval_patch_preserves_escaped_allowed_use_key() -> None:
    resources_markdown = """
## Price Data
\\- id: conditional\\_api
&#x20; name: Conditional API
&#x20; type: price\\_site
&#x20; url: https://example.test/api
&#x20; allowed\\_use: manual-or-api-if-available
"""
    resource = Resource(
        id="conditional_api",
        name="Conditional API",
        type="price_site",
        url="https://example.test/api",
        allowed_use="manual-or-api-if-available",
    )

    result = connector_approval_patch(
        _review(resource_name="Conditional API"),
        [resource],
        resources_markdown,
    )

    assert result.patch_available is True
    assert "-&#x20; allowed\\_use: manual-or-api-if-available" in result.patch_text
    assert "+&#x20; allowed\\_use: api" in result.patch_text


def test_connector_candidates_rank_needs_review_before_manual_review() -> None:
    candidates = connector_candidates(
        [
            Resource(name="Manual Source", allowed_use="manual-review", priority="critical"),
            Resource(
                name="Conditional API",
                id="conditional_api",
                allowed_use="api-or-manual-review",
                priority="medium",
                url="https://example.test/api",
            ),
        ]
    )

    assert [candidate.resource.name for candidate in candidates[:2]] == [
        "Conditional API",
        "Manual Source",
    ]
    assert candidates[0].preflight.status == "needs-review"
    assert "wq connector-draft" in candidates[0].draft_command


@pytest.mark.parametrize(
    ("allowed_use", "expected"),
    [
        ("api-or-manual-review", "api"),
        ("manual-or-api-if-available", "api"),
        ("manual-review-or-api-if-available", "api"),
        ("rss-or-manual-review", "rss"),
        ("download", "download"),
        ("manual-review", "manual-export"),
    ],
)
def test_connector_candidate_suggested_access_method_from_allowed_use(
    allowed_use: str,
    expected: str,
) -> None:
    assert suggested_access_method(Resource(name="Source", allowed_use=allowed_use)) == expected


def test_connector_candidates_mark_discord_as_compliance_gated() -> None:
    candidates = connector_candidates(
        [
            Resource(
                name="Official Discord",
                type="discord",
                url="https://discord.gg/example",
                allowed_use="api",
            )
        ]
    )

    assert candidates[0].preflight.status == "discord-gated"
    assert candidates[0].draft_command == ""
    assert "Discord-gated" in candidates[0].recommendation


def test_connector_candidates_respect_limit() -> None:
    candidates = connector_candidates(
        [
            Resource(name="First", allowed_use="api-or-manual-review", url="https://example.test/1"),
            Resource(name="Second", allowed_use="api-or-manual-review", url="https://example.test/2"),
        ],
        limit=1,
    )

    assert len(candidates) == 1


def test_connector_candidates_missing_id_uses_name_in_draft_command() -> None:
    candidates = connector_candidates(
        [
            Resource(
                name="Conditional API Source",
                allowed_use="api-or-manual-review",
                url="https://example.test/api",
            )
        ]
    )

    assert '--resource "Conditional API Source"' in candidates[0].draft_command
    assert "conditional_api_source_connector_review.json" in candidates[0].draft_command


def test_fetch_plan_is_created_for_valid_review() -> None:
    result = build_fetch_plan(_review(), [_eligible_resource()])

    assert result.plan is not None
    assert result.check.ready is True
    assert result.plan.resource_name == "Approved API"
    assert result.plan.url == "https://example.test/api"
    assert result.plan.access_method == "api"
    assert result.plan.dry_run_required is True
    assert result.plan.public_export_derived_only is True


def test_fetch_plan_minimum_request_interval_uses_rate_limit() -> None:
    result = build_fetch_plan(_review(rate_limit_per_minute=30), [_eligible_resource()])

    assert result.plan is not None
    assert result.plan.min_seconds_between_requests == 2.0


def test_fetch_plan_cache_path_is_deterministic_under_cache_root() -> None:
    first = build_fetch_plan(_review(), [_eligible_resource()])
    second = build_fetch_plan(_review(), [_eligible_resource()])

    assert first.plan is not None
    assert second.plan is not None
    assert first.plan.cache_path == second.plan.cache_path
    assert str(first.plan.cache_path).replace("\\", "/").startswith("data/raw/cache/")


def test_fetch_plan_is_not_created_for_missing_url() -> None:
    result = build_fetch_plan(
        _review(),
        [Resource(name="Approved API", type="official", allowed_use="api")],
    )

    assert result.plan is None
    assert result.check.ready is False
    assert any("URL" in blocker or "missing a URL" in blocker for blocker in result.check.blockers)


def test_fetch_plan_is_not_created_for_failed_connector_review() -> None:
    result = build_fetch_plan(
        _review(source_terms_reviewed=False),
        [_eligible_resource()],
    )

    assert result.plan is None
    assert result.check.ready is False
    assert "Source terms must be reviewed." in result.check.blockers


def test_fetch_plan_cache_path_hides_query_string_and_unsafe_characters() -> None:
    resource = Resource(
        name="Approved API: Query/Unsafe?",
        type="official",
        url="https://example.test/api?token=secret&league=Dawn",
        allowed_use="api",
    )
    result = build_fetch_plan(_review(resource_name=resource.name), [resource])

    assert result.plan is not None
    cache_name = result.plan.cache_path.name
    assert "?" not in cache_name
    assert "&" not in cache_name
    assert "secret" not in cache_name
    assert ":" not in cache_name
    assert "/" not in cache_name


def test_connector_fixture_loads_and_normalizes_rows() -> None:
    fixture = load_connector_fixture("examples/connector_fixture_api_example.json")

    assert fixture.source_name == "Example Approved API"
    assert len(fixture.items) == 2
    assert fixture.items[0].name == "Stormglass Catalyst"
    assert fixture.items[0].category == "currency"


def test_connector_fixture_loads_optional_normalized_signals() -> None:
    fixture = load_connector_fixture("examples/connector_fixture_signals_example.json")

    assert fixture.items[0].signals is not None
    assert fixture.items[0].signals.demand_momentum == 88


def test_connector_fixture_missing_items_fails_clearly(tmp_path: Path) -> None:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps({"source_name": "Example Approved API", "generated_at": "now"}),
        encoding="utf-8",
    )

    with pytest.raises(ConnectorPolicyError, match="Invalid connector fixture"):
        load_connector_fixture(fixture_path)


def test_connector_fixture_item_without_name_fails_clearly(tmp_path: Path) -> None:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "Example Approved API",
                "generated_at": "now",
                "items": [{"category": "currency"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConnectorPolicyError, match="Invalid connector fixture"):
        load_connector_fixture(fixture_path)


def test_connector_fixture_invalid_signals_fail_clearly(tmp_path: Path) -> None:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "Example Approved API",
                "generated_at": "2026-05-23T00:00:00+00:00",
                "items": [
                    {
                        "name": "Stormglass Catalyst",
                        "signals": {
                            "demand_momentum": 101,
                            "build_dependency_score": 82,
                            "price_discount_score": 76,
                            "liquidity_score": 70,
                            "historical_spike_score": 68,
                            "patch_relevance_score": 74,
                            "manipulation_risk": 18,
                            "stale_data_penalty": 8,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConnectorPolicyError, match="Invalid connector fixture"):
        load_connector_fixture(fixture_path)


def test_connector_fixture_runner_refuses_failed_review() -> None:
    result = run_connector_fixture(
        _review(source_terms_reviewed=False),
        [_eligible_resource()],
        "examples/connector_fixture_api_example.json",
    )

    assert result.ready is False
    assert result.fixture is None
    assert "Source terms must be reviewed." in result.blockers


def test_connector_fixture_runner_accepts_approved_example_review() -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    result = run_connector_fixture(
        review,
        [
            Resource(
                name="Example Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            )
        ],
        "examples/connector_fixture_api_example.json",
    )

    assert result.ready is True
    assert result.fixture is not None
    assert result.fetch_plan is not None
    assert len(result.rows) == 2
    assert result.fetch_plan.cache_path.name.endswith(".cache")


def test_connector_fixture_signal_export_writes_manual_import_json(tmp_path: Path) -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    output_path = tmp_path / "manual_import.json"

    export = export_connector_fixture_signals(
        review,
        [
            Resource(
                name="Example Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            )
        ],
        "examples/connector_fixture_signals_example.json",
        output_path,
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    imported = load_manual_items(output_path)

    assert export.item_count == 2
    assert payload["items"][0]["name"] == "Stormglass Catalyst"
    assert "signals" in payload["items"][0]
    assert imported[0]["name"] == "Stormglass Catalyst"


def test_connector_fixture_signal_export_requires_signals(tmp_path: Path) -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    output_path = tmp_path / "manual_import.json"

    with pytest.raises(ConnectorPolicyError, match="requires normalized signals"):
        export_connector_fixture_signals(
            review,
            [
                Resource(
                    name="Example Approved API",
                    type="official",
                    url="https://example.test/api",
                    allowed_use="api",
                )
            ],
            "examples/connector_fixture_api_example.json",
            output_path,
        )

    assert not output_path.exists()


def test_connector_fixture_signal_export_refuses_failed_review(tmp_path: Path) -> None:
    output_path = tmp_path / "manual_import.json"

    with pytest.raises(ConnectorPolicyError, match="Source terms must be reviewed"):
        export_connector_fixture_signals(
            _review(source_terms_reviewed=False),
            [_eligible_resource()],
            "examples/connector_fixture_signals_example.json",
            output_path,
        )

    assert not output_path.exists()


def test_connector_fixture_runner_does_not_write_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "Approved API",
                "generated_at": "2026-05-23T00:00:00+00:00",
                "items": [{"name": "Stormglass Catalyst"}],
            }
        ),
        encoding="utf-8",
    )
    result = run_connector_fixture(
        _review(),
        [_eligible_resource()],
        fixture_path,
    )

    assert result.ready is True
    assert not Path("data/raw/cache").exists()


def test_fixture_source_connector_returns_normalized_rows() -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    connector = FixtureSourceConnector.from_review(
        review,
        [
            Resource(
                name="Example Approved API",
                type="official",
                url="https://example.test/api",
                allowed_use="api",
            )
        ],
    )

    result = connector.collect_fixture("examples/connector_fixture_api_example.json")

    assert result.connector_id == "fixture-source-connector"
    assert result.connector_class == "FixtureSourceConnector"
    assert result.resource_name == "Example Approved API"
    assert len(result.rows) == 2
    assert result.rows[0].name == "Stormglass Catalyst"


def test_source_connector_factory_selects_poe_ninja_currency_connector() -> None:
    review = load_connector_review("examples/reviews/poe_ninja_poe2_currency_connector_review.json")

    connector = source_connector_from_review(review, [_poe_ninja_currency_resource()])

    assert isinstance(connector, PoeNinjaCurrencyConnector)
    assert connector.connector_id == "poe-ninja-poe2-currency"


def test_source_connector_factory_keeps_generic_fixture_connector() -> None:
    connector = source_connector_from_review(_review(), [_eligible_resource()])

    assert isinstance(connector, FixtureSourceConnector)
    assert not isinstance(connector, PoeNinjaCurrencyConnector)
    assert connector.connector_id == "fixture-source-connector"


def test_poe_ninja_currency_connector_returns_fixture_rows_without_cache_writes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    review_path = Path("examples/reviews/poe_ninja_poe2_currency_connector_review.json").resolve()
    fixture_path = Path("examples/poe_ninja_poe2_currency_fixture.json").resolve()
    review = load_connector_review(review_path)
    monkeypatch.chdir(tmp_path)

    connector = PoeNinjaCurrencyConnector.from_review(
        review,
        [_poe_ninja_currency_resource()],
    )
    result = connector.collect_fixture(fixture_path)

    assert result.connector_id == "poe-ninja-poe2-currency"
    assert result.connector_class == "PoeNinjaCurrencyConnector"
    assert result.resource_name == "poe.ninja POE2 Currency"
    assert [row.name for row in result.rows] == ["Exalted Orb", "Divine Orb", "Chaos Orb"]
    assert result.fetch_plan.cache_path == connector.fetch_plan.cache_path
    assert not Path("data/raw/cache").exists()


def test_poe_ninja_currency_connector_refuses_other_resources() -> None:
    with pytest.raises(ConnectorPolicyError, match="poe_ninja_poe2_currency"):
        PoeNinjaCurrencyConnector.from_review(_review(), [_eligible_resource()])


def test_poe_ninja_currency_connector_live_collection_is_unsupported() -> None:
    review = load_connector_review("examples/reviews/poe_ninja_poe2_currency_connector_review.json")
    connector = PoeNinjaCurrencyConnector.from_review(
        review,
        [_poe_ninja_currency_resource()],
    )

    with pytest.raises(ConnectorPolicyError, match="Live connector collection is unsupported"):
        connector.collect_live()


def test_fixture_source_connector_live_collection_is_unsupported() -> None:
    connector = FixtureSourceConnector.from_review(_review(), [_eligible_resource()])

    with pytest.raises(ConnectorPolicyError, match="Live connector collection is unsupported"):
        connector.collect_live()


def test_fixture_source_connector_refuses_incomplete_review() -> None:
    with pytest.raises(ConnectorPolicyError, match="Source terms must be reviewed"):
        FixtureSourceConnector.from_review(
            _review(source_terms_reviewed=False),
            [_eligible_resource()],
        )


def test_fixture_source_connector_exposes_fetch_plan_without_cache_writes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "Approved API",
                "generated_at": "2026-05-23T00:00:00+00:00",
                "items": [{"name": "Stormglass Catalyst"}],
            }
        ),
        encoding="utf-8",
    )
    connector = FixtureSourceConnector.from_review(_review(), [_eligible_resource()])
    result = connector.collect_fixture(fixture_path)

    assert result.fetch_plan.cache_path == connector.fetch_plan.cache_path
    assert not Path("data/raw/cache").exists()

