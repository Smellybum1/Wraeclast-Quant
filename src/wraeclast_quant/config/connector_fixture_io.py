from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from wraeclast_quant.config.connector_fixture_models import ConnectorFixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def load_connector_fixture(path: str | Path) -> ConnectorFixture:
    fixture_path = Path(path)
    try:
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read connector fixture: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(f"Invalid connector fixture JSON: {error}") from error

    try:
        return ConnectorFixture.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(f"Invalid connector fixture: {error}") from error
