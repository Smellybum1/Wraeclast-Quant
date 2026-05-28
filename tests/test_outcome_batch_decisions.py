import pytest

from wraeclast_quant.commands.maintenance_outcome_batch_decisions import (
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
