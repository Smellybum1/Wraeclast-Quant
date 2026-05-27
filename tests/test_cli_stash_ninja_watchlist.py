import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity as _opportunity
from cli_snapshot_helpers import save_scored_run as _save_scored_run


runner = CliRunner()


def _stash_ninja_args(
    database_path: Path,
    output_path: Path,
    markdown_output_path: Path | None = None,
    run_id: int | None = None,
    limit: int | None = None,
    min_score: float | None = None,
) -> list[str]:
    args = [
        "stash-ninja-watchlist",
        "--database-path",
        str(database_path),
        "--output-path",
        str(output_path),
    ]
    if markdown_output_path is not None:
        args.extend(["--markdown-output-path", str(markdown_output_path)])
    if run_id is not None:
        args.extend(["--run-id", str(run_id)])
    if limit is not None:
        args.extend(["--limit", str(limit)])
    if min_score is not None:
        args.extend(["--min-score", str(min_score)])
    return args


def test_stash_ninja_watchlist_writes_derived_only_json_and_markdown(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    run = _save_scored_run(
        repository,
        [
            _opportunity("Divine Orb", 82.5, "BUY"),
            _opportunity("Exalted Orb", 69.35, "WATCH"),
            _opportunity("Low Signal Base", 40.0, "HOLD / SELL SELECTIVELY"),
        ],
        source_mode="connector-fixture",
    )
    repository.save_recommendation_outcome(run.id, "Divine Orb", "positive")
    output_path = tmp_path / "stash_ninja.json"
    markdown_path = tmp_path / "stash_ninja.md"

    result = runner.invoke(
        app,
        _stash_ninja_args(
            repository.database_path,
            output_path,
            markdown_output_path=markdown_path,
            limit=2,
        ),
    )

    assert result.exit_code == 0
    assert "Wrote derived-only Stash-Ninja companion watchlist" in result.output
    assert "no Exile-UI files or game-client state were touched" in result.output
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["latest_run"]["id"] == run.id
    assert payload["latest_run"]["source_mode"] == "connector-fixture"
    assert payload["review_coverage"]["reviewed_recommendations"] == 1
    assert payload["review_coverage"]["unreviewed_recommendations"] == 2
    assert payload["safety"] == {
        "derived_only": True,
        "manual_application_required": True,
        "no_exile_ui_writes": True,
        "no_game_client_interaction": True,
        "no_live_http": True,
        "no_raw_signals": True,
    }
    assert payload["items"] == [
        {
            "item_name": "Divine Orb",
            "opportunity_score": 82.5,
            "action": "BUY",
            "suggested_stash_ninja_treatment": "bookmark-candidate",
        },
        {
            "item_name": "Exalted Orb",
            "opportunity_score": 69.35,
            "action": "WATCH",
            "suggested_stash_ninja_treatment": "watch",
        },
    ]

    payload_text = output_path.read_text(encoding="utf-8")
    assert "demand_momentum" not in payload_text
    assert "inputs_json" not in payload_text
    assert "positive" not in payload_text
    assert str(tmp_path) not in payload_text

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Manual application required" in markdown
    assert "| Divine Orb | 82.50 | BUY | bookmark-candidate |" in markdown
    assert "Low Signal Base" not in markdown


def test_stash_ninja_watchlist_can_select_run_and_score_threshold(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    selected = _save_scored_run(
        repository,
        [
            _opportunity("Selected Watch", 60.0, "WATCH"),
            _opportunity("Selected Skip", 54.0, "HOLD / SELL SELECTIVELY"),
        ],
        source_mode="manual-import",
    )
    _save_scored_run(
        repository,
        [_opportunity("Latest Item", 90.0, "BUY")],
        source_mode="connector-fixture",
    )
    output_path = tmp_path / "selected.json"

    result = runner.invoke(
        app,
        _stash_ninja_args(
            repository.database_path,
            output_path,
            run_id=selected.id,
            min_score=55.0,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["latest_run"]["id"] == selected.id
    assert [item["item_name"] for item in payload["items"]] == ["Selected Watch"]


def test_stash_ninja_watchlist_reports_missing_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _stash_ninja_args(tmp_path / "missing.db", tmp_path / "stash_ninja.json"),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output


def test_stash_ninja_watchlist_reports_missing_run(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    _save_scored_run(repository, [_opportunity("Known Item", 60.0, "WATCH")])

    result = runner.invoke(
        app,
        _stash_ninja_args(repository.database_path, tmp_path / "stash_ninja.json", run_id=99),
    )

    assert result.exit_code == 0
    assert "Analysis run #99 was not found." in result.output
