from wraeclast_quant.config.connector_policy import (
    build_connector_review_draft,
    connector_review_status,
)

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


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
