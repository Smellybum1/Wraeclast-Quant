import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import opportunity as _opportunity
from cli_snapshot_helpers import save_scored_run as _save_scored_run
from cli_stash_ninja_helpers import stash_ninja_args as _stash_ninja_args


runner = CliRunner()


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
    assert f"Next: wq review-queue --run-id {run.id} --output-path data/processed/review_queue.md" in result.output
    assert (
        f"wq review-queue --run-id {run.id} --decisions-output-path "
        "data/processed/outcome_decisions.json"
    ) in result.output
    assert "wq record-outcomes --input-path data/processed/outcome_decisions.json" in result.output
    assert "--dry-run" in result.output
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
    assert f"wq review-queue --run-id {run.id} --output-path data/processed/review_queue.md" in markdown
    assert (
        f"wq review-queue --run-id {run.id} --decisions-output-path "
        "data/processed/outcome_decisions.json"
    ) in markdown
    assert "wq record-outcomes --input-path data/processed/outcome_decisions.json --dry-run" in markdown
    assert "| Divine Orb | 82.50 | BUY | bookmark-candidate |" in markdown
    assert "Low Signal Base" not in markdown
