from pathlib import Path

from wraeclast_quant.commands.daily_run_rendering import (
    daily_manual_review_next_action,
)


def test_daily_manual_review_next_action_preserves_cli_output() -> None:
    database_path = Path("data/wraeclast_quant.db")

    assert daily_manual_review_next_action(run_id=13, database_path=database_path) == (
        f"Next: wq run-provenance --database-path {database_path} "
        f"--run-id 13; wq review-coverage --database-path {database_path} "
        "--run-id 13"
    )
