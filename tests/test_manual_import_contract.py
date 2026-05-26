import json
from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeManualMarket,
    CurrencyExchangeManualSnapshot,
)
from wraeclast_quant.importers.manual import SIGNAL_FIELDS

from cli_doc_markdown_helpers import documented_bullet_list as _documented_bullets


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
