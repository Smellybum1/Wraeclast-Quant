from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from wraeclast_quant.intelligence.scoring import OpportunityInputs

SIGNAL_FIELDS = [
    "demand_momentum",
    "build_dependency_score",
    "price_discount_score",
    "liquidity_score",
    "historical_spike_score",
    "patch_relevance_score",
    "manipulation_risk",
    "stale_data_penalty",
]


class ManualImportError(ValueError):
    """Raised when a local manual import file cannot be parsed or validated."""


def load_manual_items(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise ManualImportError(f"Import file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        raw_items = _load_json_items(path)
    elif suffix == ".csv":
        raw_items = _load_csv_items(path)
    else:
        raise ManualImportError("Unsupported import file extension. Use .json or .csv.")

    return [_validate_item(item, index) for index, item in enumerate(raw_items, start=1)]


def _load_json_items(path: Path) -> list[Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ManualImportError(f"Invalid JSON import file: {error.msg}") from error

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ManualImportError("JSON import must be a list or an object with an items list.")


def _load_csv_items(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        required_headers = {"name", *SIGNAL_FIELDS}
        missing_headers = sorted(required_headers - headers)
        if missing_headers:
            raise ManualImportError(
                f"CSV import is missing required columns: {', '.join(missing_headers)}"
            )
        return [
            {
                "name": row.get("name", ""),
                "signals": {field: row.get(field, "") for field in SIGNAL_FIELDS},
            }
            for row in reader
        ]


def _validate_item(item: Any, index: int) -> dict[str, object]:
    if not isinstance(item, dict):
        raise ManualImportError(f"Item {index} must be an object.")

    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ManualImportError(f"Item {index} is missing a non-empty name.")

    signals = item.get("signals")
    if not isinstance(signals, dict):
        raise ManualImportError(f"Item {index} is missing a signals object.")

    missing_signals = [field for field in SIGNAL_FIELDS if field not in signals]
    if missing_signals:
        raise ManualImportError(
            f"Item {index} is missing required signals: {', '.join(missing_signals)}"
        )

    try:
        inputs = OpportunityInputs(**{field: signals[field] for field in SIGNAL_FIELDS})
    except ValidationError as error:
        details = "; ".join(
            f"{'.'.join(str(part) for part in issue['loc'])}: {issue['msg']}"
            for issue in error.errors()
        )
        raise ManualImportError(f"Item {index} has invalid signals: {details}") from error

    return {"name": name.strip(), "signals": inputs.model_dump()}
