import json
from pathlib import Path

from wraeclast_quant.config.connector_policy import load_connector_review

from connector_policy_helpers import connector_review_payload as _review_payload


def test_load_connector_review_reads_json(tmp_path: Path) -> None:
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(_review_payload()), encoding="utf-8")

    review = load_connector_review(review_path)

    assert review.resource_name == "Approved API"
    assert review.access_method == "api"
