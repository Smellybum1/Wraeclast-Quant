import json
from pathlib import Path

import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeManualMarket,
    CurrencyExchangeManualSnapshot,
)
from wraeclast_quant.importers.manual import (
    SIGNAL_FIELDS,
    ManualImportError,
    load_manual_items,
)

from cli_doc_markdown_helpers import documented_bullet_list as _documented_bullets


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


def test_manual_import_contract_doc_and_templates_match_signal_fields() -> None:
    doc_text = Path("docs/MANUAL_IMPORT.md").read_text(encoding="utf-8")
    documented_signals = _documented_bullets(doc_text, "Each item must include:")
    json_template = json.loads(Path("examples/manual_import_template.json").read_text(encoding="utf-8"))
    csv_header = Path("examples/manual_import_template.csv").read_text(
        encoding="utf-8"
    ).splitlines()[0].split(",")

    assert documented_signals == SIGNAL_FIELDS
    assert list(json_template[0]["signals"]) == SIGNAL_FIELDS
    assert csv_header == ["name", *SIGNAL_FIELDS]


def test_currency_exchange_manual_snapshot_doc_matches_template_and_model() -> None:
    doc_text = Path("docs/MANUAL_IMPORT.md").read_text(encoding="utf-8")
    documented_snapshot_fields = _documented_bullets(
        doc_text,
        "Each Currency Exchange manual snapshot has:",
    )
    documented_market_fields = _documented_bullets(
        doc_text,
        "Each Currency Exchange manual market has:",
    )
    template = json.loads(
        Path("examples/pathofexile_currency_exchange_manual_snapshot_template.json").read_text(
            encoding="utf-8",
        )
    )

    assert documented_snapshot_fields == list(CurrencyExchangeManualSnapshot.model_fields)
    assert documented_market_fields == list(CurrencyExchangeManualMarket.model_fields)
    assert list(template) == documented_snapshot_fields
    assert list(template["markets"][0]) == documented_market_fields


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


def _item(name: str) -> dict[str, object]:
    return {
        "name": name,
        "signals": {
            "demand_momentum": 88.0,
            "build_dependency_score": 82.0,
            "price_discount_score": 76.0,
            "liquidity_score": 70.0,
            "historical_spike_score": 68.0,
            "patch_relevance_score": 74.0,
            "manipulation_risk": 18.0,
            "stale_data_penalty": 8.0,
        },
    }
