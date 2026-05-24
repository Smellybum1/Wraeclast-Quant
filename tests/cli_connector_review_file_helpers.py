from __future__ import annotations

import json
from pathlib import Path

from cli_connector_review_payload_helpers import connector_review


def write_connector_review(tmp_path: Path, **overrides) -> Path:
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(connector_review(**overrides)), encoding="utf-8")
    return review_path


__all__ = ["write_connector_review"]
