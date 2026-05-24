from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from wraeclast_quant.importers.manual_models import ManualImportError, SIGNAL_FIELDS


def load_json_items(path: Path) -> list[Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ManualImportError(f"Invalid JSON import file: {error.msg}") from error

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ManualImportError("JSON import must be a list or an object with an items list.")


def load_csv_items(path: Path) -> list[dict[str, object]]:
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
