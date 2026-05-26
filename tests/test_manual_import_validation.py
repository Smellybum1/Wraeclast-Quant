import json
from pathlib import Path

import pytest

from wraeclast_quant.importers.manual import ManualImportError, load_manual_items

from manual_import_helpers import manual_import_item as _item


def test_missing_required_signal_fails_clearly(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    item = _item("Stormglass Catalyst")
    del item["signals"]["liquidity_score"]  # type: ignore[index]
    path.write_text(json.dumps([item]), encoding="utf-8")

    with pytest.raises(ManualImportError, match="liquidity_score"):
        load_manual_items(path)


def test_out_of_range_signal_fails_clearly(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    item = _item("Stormglass Catalyst")
    item["signals"]["demand_momentum"] = 101  # type: ignore[index]
    path.write_text(json.dumps([item]), encoding="utf-8")

    with pytest.raises(ManualImportError, match="demand_momentum"):
        load_manual_items(path)


def test_unsupported_extension_fails_clearly(tmp_path: Path) -> None:
    path = tmp_path / "items.txt"
    path.write_text("not an import file", encoding="utf-8")

    with pytest.raises(ManualImportError, match="Unsupported import file extension"):
        load_manual_items(path)
