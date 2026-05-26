import json
from pathlib import Path

from wraeclast_quant.importers.manual import load_manual_items

from manual_import_helpers import manual_import_item as _item


def test_json_list_imports_successfully(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    path.write_text(json.dumps([_item("Stormglass Catalyst")]), encoding="utf-8")

    items = load_manual_items(path)

    assert items == [_item("Stormglass Catalyst")]


def test_json_import_tolerates_utf8_bom(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    path.write_text(json.dumps([_item("Stormglass Catalyst")]), encoding="utf-8-sig")

    items = load_manual_items(path)

    assert items == [_item("Stormglass Catalyst")]


def test_json_object_items_imports_successfully(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    path.write_text(json.dumps({"items": [_item("Ashen Rune Core")]}), encoding="utf-8")

    items = load_manual_items(path)

    assert items == [_item("Ashen Rune Core")]


def test_csv_imports_successfully(tmp_path: Path) -> None:
    path = tmp_path / "items.csv"
    path.write_text(
        "\n".join(
            [
                "name,demand_momentum,build_dependency_score,price_discount_score,"
                "liquidity_score,historical_spike_score,patch_relevance_score,"
                "manipulation_risk,stale_data_penalty",
                "Waystone of Embers,64,58,82,78,49,45,14,12",
            ]
        ),
        encoding="utf-8",
    )

    items = load_manual_items(path)

    assert items == [
        {
            "name": "Waystone of Embers",
            "signals": {
                "demand_momentum": 64.0,
                "build_dependency_score": 58.0,
                "price_discount_score": 82.0,
                "liquidity_score": 78.0,
                "historical_spike_score": 49.0,
                "patch_relevance_score": 45.0,
                "manipulation_risk": 14.0,
                "stale_data_penalty": 12.0,
            },
        }
    ]


def test_json_template_imports_successfully() -> None:
    items = load_manual_items(Path("examples/manual_import_template.json"))

    assert len(items) == 2
    assert items[0]["name"] == "Stormglass Catalyst"


def test_csv_template_imports_successfully() -> None:
    items = load_manual_items(Path("examples/manual_import_template.csv"))

    assert len(items) == 2
    assert items[0]["name"] == "Stormglass Catalyst"
