import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_daily_command_helpers import daily_args as _daily_args


runner = CliRunner()


def test_daily_can_write_stash_ninja_handoff_for_created_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    stash_path = tmp_path / "stash_ninja.json"
    stash_markdown_path = tmp_path / "stash_ninja.md"

    result = runner.invoke(
        app,
        _daily_args(
            sample_data=True,
            database_path=database_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
            stash_ninja=True,
            stash_ninja_path=stash_path,
            stash_ninja_markdown_path=stash_markdown_path,
        ),
    )

    latest = SnapshotRepository(database_path).latest_run()
    payload = json.loads(stash_path.read_text(encoding="utf-8"))
    markdown = stash_markdown_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert latest is not None
    assert payload["latest_run"]["id"] == latest.id
    assert payload["safety"]["derived_only"] is True
    assert payload["safety"]["no_exile_ui_writes"] is True
    assert payload["safety"]["no_game_client_interaction"] is True
    assert "demand_momentum" not in stash_path.read_text(encoding="utf-8")
    assert "Stash-Ninja handoff:" in result.output
    assert str(stash_path) in result.output
    assert str(stash_markdown_path) in result.output
    assert (
        f"Next: wq review-queue --run-id {latest.id} "
        f"--output-path data/processed/review_queue_run_{latest.id}.md"
    ) in result.output
    assert (
        f"wq review-queue --run-id {latest.id} --decisions-output-path "
        f"data/processed/outcome_decisions_run_{latest.id}.json"
    ) in result.output
    assert (
        f"wq record-outcomes --input-path "
        f"data/processed/outcome_decisions_run_{latest.id}.json --dry-run"
    ) in result.output
    assert "Manual application required" in markdown


def test_daily_does_not_write_stash_ninja_handoff_by_default(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    stash_path = tmp_path / "stash_ninja.json"

    result = runner.invoke(
        app,
        _daily_args(
            sample_data=True,
            database_path=database_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
            stash_ninja_path=stash_path,
        ),
    )

    assert result.exit_code == 0
    assert not stash_path.exists()
    assert "Stash-Ninja handoff:" not in result.output
