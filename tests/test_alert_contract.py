from pathlib import Path

from wraeclast_quant.intelligence.alerts import (
    BIG_POSITIVE_DELTA,
    BUY_THRESHOLD,
    WATCH_THRESHOLD,
)

from alert_helpers import actual_alert_reasons as _actual_alert_reasons
from cli_doc_markdown_helpers import documented_bullets as _documented_bullets


def test_alert_rules_contract_doc_matches_defaults_and_reasons() -> None:
    doc_text = Path("docs/ALERTS.md").read_text(encoding="utf-8")
    documented_settings = _documented_mapping(doc_text, "Default alert settings:")
    documented_reasons = _documented_bullets(doc_text, "Alert reasons:")

    assert documented_settings == {
        "watch_threshold": str(WATCH_THRESHOLD),
        "buy_threshold": str(BUY_THRESHOLD),
        "big_positive_delta": str(BIG_POSITIVE_DELTA),
    }
    assert documented_reasons == {
        "Score crossed into BUY",
        "Score crossed into WATCH",
        "New WATCH-or-better item",
        "Action changed upward",
        "Score increased by at least +<big_positive_delta>",
    }
    assert _actual_alert_reasons() == {
        "Score crossed into BUY",
        "Score crossed into WATCH",
        "New WATCH-or-better item",
        "Action changed upward",
        f"Score increased by at least +{BIG_POSITIVE_DELTA:.2f}",
    }


def _documented_mapping(doc_text: str, heading: str) -> dict[str, str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        key.strip("`"): value.strip("`")
        for key, value in (
            line.strip()[2:].split(": ", 1)
            for line in section.splitlines()
            if line.strip().startswith("- `")
        )
    }
