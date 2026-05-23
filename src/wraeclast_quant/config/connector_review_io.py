from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from wraeclast_quant.config.connector_policy_models import (
    ConnectorPolicyError,
    ConnectorReview,
)


def write_connector_review_draft(review: ConnectorReview, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(review.model_dump(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def load_connector_review(path: str | Path) -> ConnectorReview:
    review_path = Path(path)
    try:
        raw = json.loads(review_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read connector review: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(f"Invalid connector review JSON: {error}") from error

    try:
        return ConnectorReview.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(f"Invalid connector review: {error}") from error
