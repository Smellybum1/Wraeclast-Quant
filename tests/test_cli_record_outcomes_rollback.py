import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.db import connect
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_outcome_command_helpers import record_outcomes_args as _record_outcomes_args
from cli_report_helpers import analyze_sample_args as _analyze_sample_args


runner = CliRunner()


def test_record_outcomes_command_rolls_back_if_batch_write_fails(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    decisions_path = tmp_path / "outcome_decisions.json"
    runner.invoke(app, _analyze_sample_args(database_path))
    with connect(database_path) as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_ashen_rune_core_outcome
            BEFORE INSERT ON recommendation_outcomes
            WHEN NEW.item_name = 'Ashen Rune Core'
            BEGIN
                SELECT RAISE(ABORT, 'blocked batch insert');
            END;
            """
        )
        connection.commit()
    decisions_path.write_text(
        json.dumps(
            {
                "run_id": 1,
                "decisions": [
                    {"item_name": "Stormglass Catalyst", "outcome": "positive"},
                    {"item_name": "Ashen Rune Core", "outcome": "negative"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, _record_outcomes_args(database_path, decisions_path))

    assert result.exit_code != 0
    assert "could not record outcome batch" in result.output
    assert "no records written" in result.output
    assert "blocked batch insert" in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes(limit=10) == []
