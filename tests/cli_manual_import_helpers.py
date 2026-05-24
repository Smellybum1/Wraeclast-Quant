from __future__ import annotations

import json
from pathlib import Path

from cli_domain_helpers import manual_item


def write_manual_import_json(tmp_path: Path, *item_names: str) -> Path:
    input_path = tmp_path / "items.json"
    input_path.write_text(
        json.dumps([manual_item(name) for name in item_names]),
        encoding="utf-8",
    )
    return input_path


def write_invalid_manual_import_json(
    tmp_path: Path,
    item_name: str = "Stormglass Catalyst",
) -> Path:
    input_path = tmp_path / "items.json"
    item = manual_item(item_name)
    item["signals"]["demand_momentum"] = 101  # type: ignore[index]
    input_path.write_text(json.dumps([item]), encoding="utf-8")
    return input_path


def write_manual_import_csv(tmp_path: Path) -> Path:
    input_path = tmp_path / "items.csv"
    input_path.write_text(
        "\n".join(
            [
                "name,demand_momentum,build_dependency_score,price_discount_score,"
                "liquidity_score,historical_spike_score,patch_relevance_score,"
                "manipulation_risk,stale_data_penalty",
                "Ashen Rune Core,72,80,66,62,55,70,20,10",
            ]
        ),
        encoding="utf-8",
    )
    return input_path


def import_args(input_path: Path, database_path: Path) -> list[str]:
    return ["import", "--input-path", str(input_path), "--database-path", str(database_path)]


def validate_import_args(input_path: Path) -> list[str]:
    return ["validate-import", "--input-path", str(input_path)]


def inspect_import_args(input_path: Path) -> list[str]:
    return ["inspect-import", "--input-path", str(input_path)]


__all__ = [
    "import_args",
    "inspect_import_args",
    "validate_import_args",
    "write_invalid_manual_import_json",
    "write_manual_import_csv",
    "write_manual_import_json",
]
