from __future__ import annotations

from pathlib import Path

from wraeclast_quant.importers.manual_formats import load_csv_items, load_json_items
from wraeclast_quant.importers.manual_models import ManualImportError, SIGNAL_FIELDS
from wraeclast_quant.importers.manual_validation import validate_item


def load_manual_items(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise ManualImportError(f"Import file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        raw_items = load_json_items(path)
    elif suffix == ".csv":
        raw_items = load_csv_items(path)
    else:
        raise ManualImportError("Unsupported import file extension. Use .json or .csv.")

    return [validate_item(item, index) for index, item in enumerate(raw_items, start=1)]

__all__ = ["SIGNAL_FIELDS", "ManualImportError", "load_manual_items"]
