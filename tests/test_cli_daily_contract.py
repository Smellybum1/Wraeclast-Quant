from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_daily_command_helpers import daily_args as _daily_args
from cli_doc_markdown_helpers import documented_bullets as _documented_bullets


runner = CliRunner()


def test_daily_pipeline_contract_doc_matches_printed_output_labels(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    doc_text = Path("docs/DAILY_PIPELINE.md").read_text(encoding="utf-8")
    output_labels = _documented_bullets(doc_text, "Successful daily runs print these output labels:")

    result = runner.invoke(
        app,
        _daily_args(
            sample_data=True,
            database_path=database_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
        ),
    )

    assert result.exit_code == 0
    assert output_labels == {"Database", "Market brief", "Public intel", "Dashboard"}
    for label in output_labels:
        assert f"{label}:" in result.output
    assert "Daily run #1 complete." in result.output
