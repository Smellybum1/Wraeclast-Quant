import json
from pathlib import Path

import pytest

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    check_connector_review,
    load_connector_review,
)

from connector_policy_helpers import connector_review_payload as _review_payload
from connector_policy_helpers import eligible_resource as _eligible_resource


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
