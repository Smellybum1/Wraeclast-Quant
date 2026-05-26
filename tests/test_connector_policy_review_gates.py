import pytest

from wraeclast_quant.config.connector_policy import check_connector_review

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


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
