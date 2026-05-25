import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_doc_markdown_helpers import documented_status_row_keys as _documented_status_row_keys
from cli_status_command_helpers import status_args as _status_args
from cli_status_workspace_helpers import write_manual_resources as _write_manual_resources


runner = CliRunner()


def test_status_json_contract_doc_matches_cli_output(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            site_dir=tmp_path / "site",
            bundle_dir=tmp_path / "site_bundle",
            json_output=True,
        ),
    )

    payload = json.loads(result.output)
    doc_text = Path("docs/STATUS_JSON.md").read_text(encoding="utf-8")
    documented_version = doc_text.split(
        "The current status JSON schema version is `", 1
    )[1].split("`", 1)[0]
    documented_keys = _documented_status_row_keys(doc_text)

    assert result.exit_code == 0
    assert documented_version == payload["schema_version"]
    assert documented_keys == [row["key"] for row in payload["rows"]]
    assert set(documented_keys) == set(payload["rows_by_key"])
