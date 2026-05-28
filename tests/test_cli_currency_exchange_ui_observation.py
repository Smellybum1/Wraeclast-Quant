import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation import (
    write_currency_exchange_ui_observation_manual_import,
)
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_daily_command_helpers import daily_args as _daily_args


runner = CliRunner()


def write_ui_observation(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "league": "Standard",
                "observed_at": "2026-05-27T17:00:00+00:00",
                "observations": [
                    {
                        "want_currency": "Chaos Orb",
                        "have_currency": "Divine Orb",
                        "market_ratio": "30:1",
                        "stock_rows": [
                            {"ratio": "30:1", "stock": 18150},
                            {"ratio": "25:1", "stock": 182850},
                            {"ratio": "23.71:1", "stock": 735},
                            {"ratio": "23:1", "stock": 2300},
                            {"ratio": "22:1", "stock": 4400},
                            {"ratio": "22:1", "stock": 214257, "comparator": "less_than"},
                        ],
                    },
                    {
                        "want_currency": "Exalted Orb",
                        "have_currency": "Divine Orb",
                        "market_ratio": "650:1",
                        "stock_rows": [
                            {"ratio": "900:1", "stock": 900},
                            {"ratio": "650:1", "stock": 83200},
                            {"ratio": "641:1", "stock": 6410},
                            {"ratio": "640:1", "stock": 19200},
                            {"ratio": "621:1", "stock": 6210},
                            {"ratio": "621:1", "stock": 1230149, "comparator": "less_than"},
                        ],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def ui_observation_args(
    input_path: Path,
    output_path: Path,
    *,
    review_notes_output_path: Path | None = None,
) -> list[str]:
    args = [
        "currency-exchange-ui-observation",
        "--input-path",
        str(input_path),
        "--output-path",
        str(output_path),
    ]
    if review_notes_output_path is not None:
        args.extend(["--review-notes-output-path", str(review_notes_output_path)])
    return args


def test_currency_exchange_ui_observation_writes_manual_import_json(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    output_path = tmp_path / "manual_import.json"
    write_ui_observation(input_path)

    result = runner.invoke(app, ui_observation_args(input_path, output_path))
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Currency Exchange UI Observation Export" in result.output
    assert "Capture Flags" in result.output
    assert "Capture review flags: none." in result.output
    assert "No OAuth, live HTTP, scraping, game-client automation" in result.output
    assert "wq validate-import" in result.output
    assert payload["items"][0]["name"] == "Chaos Orb / Divine Orb (Standard UI)"
    assert "signals" in payload["items"][0]


def test_currency_exchange_ui_observation_writes_review_notes_sidecar(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    output_path = tmp_path / "manual_import.json"
    review_notes_path = tmp_path / "ui_observation_review.md"
    write_ui_observation(input_path)

    result = runner.invoke(
        app,
        ui_observation_args(
            input_path,
            output_path,
            review_notes_output_path=review_notes_path,
        ),
    )
    notes = review_notes_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Review sidecar" in result.output
    assert "Capture review flags: none." in result.output
    assert "--context-path" in result.output
    assert str(review_notes_path) in result.output
    assert "Chaos Orb / Divine Orb (Standard UI)" in notes
    assert "<621:1 stock 1,230,149" in notes
    assert "No OAuth, live HTTP, scraping, OCR, game-client automation" in notes


def test_currency_exchange_ui_observation_export_result_counts_capture_flags(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "ui_observation.json"
    output_path = tmp_path / "manual_import.json"
    review_notes_path = tmp_path / "ui_observation_review.md"
    input_path.write_text(
        json.dumps(
            {
                "league": "Standard",
                "observations": [
                    {
                        "want_currency": "Divine Orb",
                        "have_currency": "Regal Orb",
                        "market_ratio": "1:1",
                        "no_stock": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = write_currency_exchange_ui_observation_manual_import(
        input_path=input_path,
        output_path=output_path,
        review_notes_output_path=review_notes_path,
    )

    assert result.capture_review_flag_count == 1
    assert "Capture Review Flags" in review_notes_path.read_text(encoding="utf-8")


def test_currency_exchange_ui_observation_output_runs_daily_pipeline(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    output_path = tmp_path / "manual_import.json"
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    write_ui_observation(input_path)

    export_result = runner.invoke(app, ui_observation_args(input_path, output_path))
    daily_result = runner.invoke(
        app,
        _daily_args(
            input_path=output_path,
            database_path=database_path,
            intel_path=intel_path,
            site_dir=site_dir,
        ),
    )
    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)

    assert export_result.exit_code == 0
    assert daily_result.exit_code == 0
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"
    assert "Chaos Orb / Divine Orb (Standard UI)" in intel_path.read_text(encoding="utf-8")


def test_currency_exchange_ui_observation_rejects_empty_observations(tmp_path: Path) -> None:
    input_path = tmp_path / "empty.json"
    output_path = tmp_path / "manual_import.json"
    input_path.write_text('{"league": "Standard", "observations": []}', encoding="utf-8")

    result = runner.invoke(app, ui_observation_args(input_path, output_path))

    assert result.exit_code != 0
    assert "Invalid value" in result.output
    assert not output_path.exists()
