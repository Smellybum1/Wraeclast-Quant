from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from wraeclast_quant.commands.maintenance_outcome_records_rendering import (
    print_no_outcomes,
    print_outcome_record,
    print_recent_outcomes,
)
from wraeclast_quant.reports.review_queue_commands import record_outcomes_command
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES, SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command("record-outcome")
    def record_outcome(
        run_id: int = typer.Option(..., "--run-id", min=1, help="Analysis run id."),
        item_name: str = typer.Option(..., "--item-name", help="Item name from the analysis run."),
        outcome: str = typer.Option(..., "--outcome", help="positive, neutral, or negative."),
        notes: str = typer.Option("", "--notes", help="Optional local review notes."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        repository = SnapshotRepository(database_path)
        try:
            record = repository.save_recommendation_outcome(
                run_id=run_id,
                item_name=item_name,
                outcome=outcome,
                notes=notes,
            )
        except ValueError as error:
            raise typer.BadParameter(str(error)) from error

        print_outcome_record(record)

    @app.command("record-outcomes")
    def record_outcomes(
        input_path: Path = typer.Option(
            ...,
            "--input-path",
            help="Local JSON file with run_id and human-reviewed outcome decisions.",
        ),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Validate the local outcome batch without writing records.",
        ),
    ) -> None:
        repository = SnapshotRepository(database_path)
        try:
            run_id, decisions = load_batch_outcome_decisions(input_path)
            validate_batch_outcome_decisions(repository, run_id, decisions)
            if dry_run:
                typer.echo(
                    f"Validated {len(decisions)} outcome decision(s) for run #{run_id} "
                    f"from {input_path}; no records written."
                )
                typer.echo(f"Next: {record_outcomes_command(str(input_path))}")
                return
            records = [
                repository.save_recommendation_outcome(
                    run_id=run_id,
                    item_name=decision["item_name"],
                    outcome=decision["outcome"],
                    notes=decision["notes"],
                )
                for decision in decisions
            ]
        except ValueError as error:
            raise typer.BadParameter(str(error)) from error

        typer.echo(f"Recorded {len(records)} outcome(s) for run #{run_id} from {input_path}.")
        typer.echo(
            f"Next: wq review-coverage --run-id {run_id}; "
            "run wq export, wq site, and wq site-bundle when you want derived artifacts refreshed."
        )

    @app.command()
    def outcomes(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        records = repository.list_recent_outcomes(limit=limit)
        if not records:
            print_no_outcomes()
            return

        summary = repository.outcome_summary()
        print_recent_outcomes(records, summary)


def load_batch_outcome_decisions(input_path: Path) -> tuple[int, list[dict[str, str]]]:
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"could not read outcome decisions: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid outcome decisions JSON: {error}") from error

    if not isinstance(payload, dict):
        raise ValueError("outcome decisions must be a JSON object.")
    run_id = payload.get("run_id")
    if not isinstance(run_id, int) or run_id < 1:
        raise ValueError("outcome decisions must include a positive integer run_id.")
    raw_decisions = payload.get("decisions")
    if not isinstance(raw_decisions, list) or not raw_decisions:
        raise ValueError("outcome decisions must include a non-empty decisions list.")

    decisions: list[dict[str, str]] = []
    seen_items: set[str] = set()
    for index, raw_decision in enumerate(raw_decisions, start=1):
        decision = normalize_batch_outcome_decision(index, raw_decision)
        item_name = decision["item_name"]
        if item_name in seen_items:
            raise ValueError(f"decision {index} duplicates item_name '{item_name}'.")
        seen_items.add(item_name)
        decisions.append(decision)
    return run_id, decisions


def normalize_batch_outcome_decision(index: int, raw_decision: Any) -> dict[str, str]:
    if not isinstance(raw_decision, dict):
        raise ValueError(f"decision {index} must be an object.")
    item_name = raw_decision.get("item_name")
    if not isinstance(item_name, str) or not item_name.strip():
        raise ValueError(f"decision {index} must include a non-empty item_name.")
    outcome = raw_decision.get("outcome")
    if not isinstance(outcome, str):
        raise ValueError(f"decision {index} must include an outcome.")
    normalized_outcome = outcome.strip().lower()
    allowed = ", ".join(sorted(ALLOWED_OUTCOMES))
    if not normalized_outcome:
        raise ValueError(
            f"decision {index} outcome is blank; fill it with one of: {allowed}, "
            "then rerun record-outcomes --dry-run."
        )
    if normalized_outcome not in ALLOWED_OUTCOMES:
        raise ValueError(f"decision {index} outcome must be one of: {allowed}.")
    notes = raw_decision.get("notes", "")
    if not isinstance(notes, str):
        raise ValueError(f"decision {index} notes must be a string when supplied.")
    return {
        "item_name": item_name.strip(),
        "outcome": normalized_outcome,
        "notes": notes,
    }


def validate_batch_outcome_decisions(
    repository: SnapshotRepository,
    run_id: int,
    decisions: list[dict[str, str]],
) -> None:
    if repository.analysis_run(run_id) is None:
        raise ValueError(f"analysis run #{run_id} was not found")
    item_names = {
        opportunity.item_name
        for opportunity in repository.scored_opportunities_for_run(run_id, limit=None)
    }
    for decision in decisions:
        item_name = decision["item_name"]
        if item_name not in item_names:
            raise ValueError(f"item '{item_name}' was not found in analysis run #{run_id}")
