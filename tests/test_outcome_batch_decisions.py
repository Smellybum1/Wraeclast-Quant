import json
from pathlib import Path

import pytest

from wraeclast_quant.commands.maintenance_outcome_batch_decisions import (
    load_batch_outcome_decisions,
    normalize_batch_outcome_decision,
)


def test_batch_decision_blank_outcome_error_names_item() -> None:
    with pytest.raises(ValueError) as error:
        normalize_batch_outcome_decision(
            1,
            {"item_name": "Exalted Orb / Divine Orb (Standard UI)", "outcome": ""},
        )

    message = str(error.value)
    assert "decision 1 for 'Exalted Orb / Divine Orb (Standard UI)' blank outcome" in message
    assert "use: negative, neutral, positive" in message
    assert "record-outcomes --dry-run" in message


def test_batch_decision_invalid_outcome_error_names_item() -> None:
    with pytest.raises(ValueError) as error:
        normalize_batch_outcome_decision(
            2,
            {"item_name": "Chaos Orb / Divine Orb (Standard UI)", "outcome": "maybe"},
        )

    assert (
        "decision 2 for 'Chaos Orb / Divine Orb (Standard UI)' outcome must be one of: "
        "negative, neutral, positive."
    ) in str(error.value)


def test_batch_decision_notes_type_error_names_item() -> None:
    with pytest.raises(ValueError) as error:
        normalize_batch_outcome_decision(
            3,
            {
                "item_name": "Regal Orb / Divine Orb (Standard UI)",
                "outcome": "neutral",
                "notes": 12,
            },
        )

    assert (
        "decision 3 for 'Regal Orb / Divine Orb (Standard UI)' notes must be a string"
    ) in str(error.value)


def test_batch_decision_loader_reports_multiple_row_errors(tmp_path: Path) -> None:
    decisions_path = tmp_path / "outcome_decisions.json"
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 13,
                "decisions": [
                    {
                        "item_name": "Exalted Orb / Divine Orb (Standard UI)",
                        "outcome": "neutral",
                    },
                    {
                        "item_name": "Chaos Orb / Divine Orb (Standard UI)",
                        "outcome": "",
                    },
                    {
                        "item_name": "Exalted Orb / Divine Orb (Standard UI)",
                        "outcome": "positive",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as error:
        load_batch_outcome_decisions(decisions_path)

    message = str(error.value)
    assert "outcome decisions have 2 validation errors:" in message
    assert "decision 2 for 'Chaos Orb / Divine Orb (Standard UI)' blank outcome" in message
    assert (
        "decision 3 duplicates item_name 'Exalted Orb / Divine Orb (Standard UI)' "
        "(first seen at decision 1)."
    ) in message
