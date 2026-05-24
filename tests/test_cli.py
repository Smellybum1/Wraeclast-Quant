import json
import sqlite3
import time
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.reports.market_brief import write_market_brief
from wraeclast_quant.reports.site_bundle import write_site_bundle
from wraeclast_quant.reports.static_site import write_static_site
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_backup_helpers import sample_data_backup as _sample_data_backup
from cli_backup_helpers import sample_data_database as _sample_data_database
from cli_connector_helpers import approved_api_resources_text as _approved_api_resources_text
from cli_connector_helpers import conditional_api_resources_text as _conditional_api_resources_text
from cli_connector_helpers import connector_review as _connector_review
from cli_connector_helpers import discord_resources_text as _discord_resources_text
from cli_connector_helpers import manual_source_resources_text as _manual_source_resources_text
from cli_connector_helpers import poe_ninja_currency_resources_text as _poe_ninja_currency_resources_text
from cli_connector_helpers import write_connector_resources as _write_connector_resources
from cli_connector_helpers import write_connector_review as _write_connector_review
from cli_daily_helpers import previous_stormglass_database as _previous_stormglass_database
from cli_daily_helpers import small_mover_daily_setup as _small_mover_daily_setup
from cli_doc_helpers import documented_bullets as _documented_bullets
from cli_domain_helpers import manual_item as _manual_item
from cli_domain_helpers import opportunity as _opportunity
from cli_manual_import_helpers import write_manual_import_csv as _write_manual_import_csv
from cli_manual_import_helpers import write_manual_import_json as _write_manual_import_json
from cli_market_flow_helpers import buy_crossing_database as _buy_crossing_database
from cli_market_flow_helpers import (
    comparison_database_with_changes as _comparison_database_with_changes,
)
from cli_market_flow_helpers import single_buy_database as _single_buy_database
from cli_market_flow_helpers import small_mover_database as _small_mover_database
from cli_market_flow_helpers import stable_watch_database as _stable_watch_database
from cli_outcome_helpers import calibration_reviewed_database as _calibration_reviewed_database
from cli_outcome_helpers import (
    partially_reviewed_two_item_database as _partially_reviewed_two_item_database,
)
from cli_outcome_helpers import (
    reviewed_single_opportunity_database as _reviewed_single_opportunity_database,
)
from cli_outcome_helpers import (
    two_run_database_with_second_reviewed as _two_run_database_with_second_reviewed,
)
from cli_public_artifact_helpers import (
    database_with_two_runs as _database_with_two_runs,
    public_intel_payload as _public_intel_payload,
    status_args as _status_args,
    status_json_args as _status_json_args,
    write_manual_resources as _write_manual_resources,
    write_publish_ready_bundle as _write_publish_ready_bundle,
)
from cli_readonly_helpers import (
    read_only_missing_database_command_cases as _read_only_missing_database_command_cases,
)
from cli_snapshot_helpers import save_scored_run as _save_scored_run
from cli_snapshot_helpers import save_single_opportunity_run as _save_single_opportunity_run


runner = CliRunner()

PUBLIC_COMMANDS = [
    "schema",
    "status",
    "db-check",
    "snapshots",
    "compare",
    "alerts",
    "report",
    "export",
    "site",
    "validate-intel",
    "site-bundle",
    "publish-check",
    "publish-handoff",
    "site-contract",
    "daily",
    "schedule-helper",
    "backup-db",
    "verify-backup",
    "backups",
    "restore-helper",
    "migration-readiness",
    "run-provenance",
    "record-outcome",
    "outcomes",
    "review-queue",
    "review-coverage",
    "outcome-review",
    "outcome-report",
    "calibration",
    "calibration-report",
    "collect",
    "compliance",
    "preflight",
    "connector-candidates",
    "connector-draft",
    "connector-review-prep",
    "connector-review-evidence",
    "connector-check",
    "connector-review-status",
    "connector-approval-helper",
    "connector-review-report",
    "connector-approval-patch",
    "connector-fixture-run",
    "connector-dry-run",
    "connector-fixture-export",
    "connector-fixture-daily",
    "connector-plan",
    "analyze",
    "import",
    "validate-import",
    "inspect-import",
    "watchlist",
]


def test_top_level_help_lists_public_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    for command in PUBLIC_COMMANDS:
        assert command in result.output


def test_public_command_help_smoke_matrix() -> None:
    for command in PUBLIC_COMMANDS:
        result = runner.invoke(app, [command, "--help"])

        assert result.exit_code == 0, command


def test_collect_dry_run() -> None:
    result = runner.invoke(app, ["collect", "--dry-run"])

    assert result.exit_code == 0
    assert "POE2 Scout" in result.output
    assert "PriceSiteCollector" in result.output


def test_analyze_sample_data(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(app, ["analyze", "--sample-data", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Stormglass Catalyst" in result.output


def test_import_json_records_manual_import_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(
        app,
        [
            "import",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
        ],
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert "Imported Opportunities" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Recorded manual import run" in result.output
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"


def test_import_csv_records_manual_import_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_csv(tmp_path)

    result = runner.invoke(
        app,
        [
            "import",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
        ],
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert "Ashen Rune Core" in result.output
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"


def test_import_invalid_input_exits_nonzero(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = tmp_path / "items.json"
    item = _manual_item("Stormglass Catalyst")
    item["signals"]["demand_momentum"] = 101  # type: ignore[index]
    input_path.write_text(json.dumps([item]), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "import",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
        ],
    )

    assert result.exit_code != 0
    assert "demand_momentum" in result.output


def test_validate_import_prints_valid_count_and_table(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(
        app,
        [
            "validate-import",
            "--input-path",
            str(input_path),
        ],
    )

    assert result.exit_code == 0
    assert "Manual Import Validation" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Valid manual import: 1 items." in result.output


def test_validate_import_invalid_input_exits_nonzero(tmp_path: Path) -> None:
    input_path = tmp_path / "items.json"
    item = _manual_item("Stormglass Catalyst")
    item["signals"]["demand_momentum"] = 101  # type: ignore[index]
    input_path.write_text(json.dumps([item]), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "validate-import",
            "--input-path",
            str(input_path),
        ],
    )

    assert result.exit_code != 0
    assert "demand_momentum" in result.output


def test_validate_import_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(
        app,
        [
            "validate-import",
            "--input-path",
            str(input_path),
        ],
    )

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()


def test_inspect_import_prints_read_only_diagnostics(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst", "Ashen Rune Core")

    result = runner.invoke(app, ["inspect-import", "--input-path", str(input_path)])

    assert result.exit_code == 0
    assert "Manual Import Diagnostics" in result.output
    assert "Items" in result.output
    assert "2" in result.output
    assert "Average score" in result.output
    assert "Signal Averages" in result.output
    assert "Top Imported Opportunities" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "read-only" in result.output


def test_inspect_import_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(app, ["inspect-import", "--input-path", str(input_path)])

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()


def test_inspect_import_invalid_input_exits_nonzero(tmp_path: Path) -> None:
    input_path = tmp_path / "items.json"
    item = _manual_item("Stormglass Catalyst")
    item["signals"]["demand_momentum"] = 101  # type: ignore[index]
    input_path.write_text(json.dumps([item]), encoding="utf-8")

    result = runner.invoke(app, ["inspect-import", "--input-path", str(input_path)])

    assert result.exit_code != 0
    assert "demand_momentum" in result.output


def test_compliance_command_uses_real_resources() -> None:
    result = runner.invoke(app, ["compliance"])

    assert result.exit_code == 0
    assert "Resource Compliance" in result.output
    assert "POE2 Scout Currency" in result.output
    assert "Official Path of Exile 2 Discord" in result.output


def test_status_command_prints_local_health(tmp_path: Path) -> None:
    resources_path = tmp_path / "RESOURCES.md"
    resources_path.write_text(
        """
## Official Sources
- name: Approved API
  type: official
  url: https://example.test/api
  allowed_use: api
""",
        encoding="utf-8",
    )
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = _save_scored_run(
        repository,
        [
            _opportunity("Reviewed Catalyst", 76.0, "BUY"),
            _opportunity("Open Catalyst", 60.0, "WATCH"),
        ],
    )
    repository.save_recommendation_outcome(run.id, "Reviewed Catalyst", "positive")
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    bundle_dir = tmp_path / "site_bundle"
    backup_dir = tmp_path / "backups"
    write_market_brief(
        [_opportunity("Reviewed Catalyst", 76.0, "BUY")],
        path=brief_path,
    )
    intel_payload = _public_intel_payload(run_id=run.id)
    intel_path.write_text(json.dumps(intel_payload), encoding="utf-8")
    write_static_site(intel_payload, site_dir)
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=bundle_dir)
    runner.invoke(
        app,
        [
            "backup-db",
            "--database-path",
            str(database_path),
            "--output-dir",
            str(backup_dir),
        ],
    )

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
            bundle_dir=bundle_dir,
            backup_dir=backup_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Wraeclast Quant Status" in result.output
    assert "Resources" in result.output
    assert "1 configured; 1 automation-eligible" in result.output
    assert "Database health" in result.output
    assert "schema v2" in result.output
    assert "integrity ok" in result.output
    assert "Latest run" in result.output
    assert "#1 sample-data; 2 items" in result.output
    assert "Review coverage" in result.output
    assert "1/2 reviewed" in result.output
    assert "50.0%" in result.output
    assert "Market brief" in result.output
    assert "no snapshot changes" in result.output
    assert "Public intel" in result.output
    assert "schema 1.0" in result.output
    assert "latest run #1" in result.output
    assert "Static site" in result.output
    assert "latest run #1" in result.output
    assert "Site bundle" in result.output
    assert "opportunities" in result.output
    assert "Backups" in result.output
    assert "Backups" in result.output
    assert "ok" in result.output
    assert "latest run #1" in result.output
    assert "collectors remain dry-run placeholders" in result.output


def test_status_command_does_not_create_missing_database(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = tmp_path / "missing.db"
    backup_dir = tmp_path / "missing_backups"

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            backup_dir=backup_dir,
        ),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
    assert "No database found." in result.output
    assert "No local database backups found." in result.output
    assert "Database" in result.output
    assert not database_path.exists()
    assert not backup_dir.exists()


def test_status_strict_allows_missing_optional_artifacts(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            strict=True,
        ),
    )

    assert result.exit_code == 0
    assert "Strict status failed" not in result.output


def test_status_json_outputs_machine_readable_rows(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)

    result = runner.invoke(
        app,
        [
            "status",
            "--json",
            "--database-path",
            str(tmp_path / "missing.db"),
            "--resources-path",
            str(resources_path),
            "--brief-path",
            str(tmp_path / "missing.md"),
            "--intel-path",
            str(tmp_path / "missing.json"),
            "--site-dir",
            str(tmp_path / "site"),
            "--bundle-dir",
            str(tmp_path / "site_bundle"),
            "--backup-dir",
            str(tmp_path / "missing_backups"),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["product"] == "Wraeclast Quant"
    assert payload["schema_version"] == "1.5"
    assert "T" in payload["generated_at"]
    assert payload["strict"] is False
    assert payload["ok"] is True
    assert payload["strict_failures"] == []
    assert payload["strict_failure_keys"] == []
    assert payload["status_counts"] == {"no": 6, "none": 3, "ok": 2}
    rows_by_key = {row["key"]: row for row in payload["rows"]}
    assert payload["rows_by_key"] == rows_by_key
    assert rows_by_key["database_health"]["check"] == "Database health"
    assert payload["rows_by_key"]["public_intel"]["status"] == "no"
    assert payload["rows_by_key"]["safety_boundary"] == {
        "key": "safety_boundary",
        "check": "Safety boundary",
        "status": "ok",
        "details": "Local-only status check; collectors remain dry-run placeholders.",
    }


def test_status_json_contract_doc_matches_cli_output(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)

    result = runner.invoke(
        app,
        [
            "status",
            "--json",
            "--database-path",
            str(tmp_path / "missing.db"),
            "--resources-path",
            str(resources_path),
            "--brief-path",
            str(tmp_path / "missing.md"),
            "--intel-path",
            str(tmp_path / "missing.json"),
            "--site-dir",
            str(tmp_path / "site"),
            "--bundle-dir",
            str(tmp_path / "site_bundle"),
            "--backup-dir",
            str(tmp_path / "missing_backups"),
        ],
    )

    payload = json.loads(result.output)
    doc_text = Path("docs/STATUS_JSON.md").read_text(encoding="utf-8")
    documented_version = doc_text.split(
        "The current status JSON schema version is `", 1
    )[1].split("`", 1)[0]
    documented_keys_section = doc_text.split("Current row keys:\n\n", 1)[1].split(
        "\n\n", 1
    )[0]
    documented_keys = [
        line.strip()[3:-1]
        for line in documented_keys_section.splitlines()
        if line.strip().startswith("- `")
    ]

    assert result.exit_code == 0
    assert documented_version == payload["schema_version"]
    assert documented_keys == [row["key"] for row in payload["rows"]]
    assert set(documented_keys) == set(payload["rows_by_key"])


def test_status_json_strict_exits_nonzero_with_parseable_failures(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            intel_path=intel_path,
            strict=True,
            json_output=True,
        ),
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["schema_version"] == "1.5"
    assert "generated_at" in payload
    assert payload["strict"] is True
    assert payload["ok"] is False
    assert payload["status_counts"]["needs_attention"] == 1
    assert payload["strict_failures"] == ["Public intel"]
    assert payload["strict_failure_keys"] == ["public_intel"]
    assert payload["rows_by_key"]["public_intel"]["status"] == "needs attention"
    assert "Strict status failed" not in result.output


def test_status_marks_stale_public_intel_needs_attention(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_public_intel_payload(run_id=1)), encoding="utf-8")

    result = runner.invoke(
        app,
        _status_json_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            intel_path=intel_path,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    row = payload["rows_by_key"]["public_intel"]
    assert row["status"] == "needs attention"
    assert "stale; latest database run #2, artifact run #1; run wq export and wq site" in row["details"]


def test_status_marks_stale_static_site_needs_attention(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    site_dir = tmp_path / "site"
    write_static_site(_public_intel_payload(run_id=1), site_dir)

    result = runner.invoke(
        app,
        _status_json_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            site_dir=site_dir,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    row = payload["rows_by_key"]["static_site"]
    assert row["status"] == "needs attention"
    assert "stale; latest database run #2, artifact run #1; run wq site" in row["details"]


def test_status_marks_stale_site_bundle_needs_attention(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    intel_path = tmp_path / "bundle_source_intel.json"
    site_dir = tmp_path / "bundle_source_site"
    bundle_dir = tmp_path / "site_bundle"
    stale_payload = _public_intel_payload(run_id=1)
    intel_path.write_text(json.dumps(stale_payload), encoding="utf-8")
    write_static_site(stale_payload, site_dir)
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=bundle_dir)

    result = runner.invoke(
        app,
        _status_json_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            bundle_dir=bundle_dir,
        ),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    row = payload["rows_by_key"]["site_bundle"]
    assert row["status"] == "needs attention"
    assert "stale; latest database run #2, bundle run #1; run wq site-bundle" in row["details"]


def test_status_strict_json_exits_nonzero_for_stale_artifacts(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = _database_with_two_runs(tmp_path)
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_public_intel_payload(run_id=1)), encoding="utf-8")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            intel_path=intel_path,
            strict=True,
            json_output=True,
        ),
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["strict_failures"] == ["Public intel"]
    assert payload["strict_failure_keys"] == ["public_intel"]
    assert payload["rows_by_key"]["public_intel"]["status"] == "needs attention"


def test_status_reports_invalid_latest_backup_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    invalid_backup = backup_dir / "invalid.db"
    with sqlite3.connect(invalid_backup) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            backup_dir=backup_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Backups" in result.output
    assert "needs attention" in result.output
    assert "invalid" in result.output
    assert "missing required tables" in result.output


def test_status_strict_exits_nonzero_for_invalid_latest_backup(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    invalid_backup = backup_dir / "invalid.db"
    with sqlite3.connect(invalid_backup) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    time.sleep(0.01)

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            backup_dir=backup_dir,
            strict=True,
        ),
    )

    assert result.exit_code == 1
    assert "Strict status failed: Backups" in result.output


def test_status_command_reports_invalid_public_intel_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    repository.create_analysis_run(source_mode="sample-data", item_count=0)
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
            intel_path=intel_path,
        ),
    )

    assert result.exit_code == 0
    assert "Public intel" in result.output
    assert "needs attention" in result.output
    assert "Missing required keys" in result.output


def test_status_strict_exits_nonzero_for_health_failures(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            intel_path=intel_path,
            strict=True,
        ),
    )

    assert result.exit_code == 1
    assert "Public intel" in result.output
    assert "needs attention" in result.output
    assert "Strict status failed: Public intel" in result.output


def test_status_command_reports_invalid_market_brief_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    brief_path = tmp_path / "market_brief.md"
    brief_path.write_text("# Wrong Report", encoding="utf-8")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            brief_path=brief_path,
        ),
    )

    assert result.exit_code == 0
    assert "Market brief" in result.output
    assert "needs attention" in result.output
    assert "missing markers" in result.output


def test_status_command_reports_invalid_static_site_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html><title>Other</title></html>", encoding="utf-8")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            site_dir=site_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Static site" in result.output
    assert "needs attention" in result.output
    assert "missing markers" in result.output


def test_status_command_reports_invalid_site_bundle_without_failing(tmp_path: Path) -> None:
    resources_path = _write_manual_resources(tmp_path)
    bundle_dir = tmp_path / "site_bundle"
    bundle_dir.mkdir()
    (bundle_dir / "wraeclast_quant_site_bundle.zip").write_bytes(b"not a zip")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=tmp_path / "missing.db",
            resources_path=resources_path,
            bundle_dir=bundle_dir,
        ),
    )

    assert result.exit_code == 0
    assert "Site bundle" in result.output
    assert "needs attention" in result.output
    assert "manifest.json is missing" in result.output
    assert "not a valid zip file" in result.output


def test_status_command_reports_unhealthy_database_without_initializing_schema(
    tmp_path: Path,
) -> None:
    resources_path = _write_manual_resources(tmp_path)
    database_path = tmp_path / "not_wq.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")

    result = runner.invoke(
        app,
        _status_args(
            tmp_path,
            database_path=database_path,
            resources_path=resources_path,
        ),
    )

    assert result.exit_code == 0
    assert "Database health" in result.output
    assert "needs attention" in result.output
    assert "missing tables" in result.output
    assert "Database health check did not pass." in result.output
    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
    assert tables == {"unrelated"}


def test_schema_command_prints_sqlite_schema_contract() -> None:
    result = runner.invoke(app, ["schema"])

    assert result.exit_code == 0
    assert "SQLite Schema Contract v2" in result.output
    assert "analysis_runs" in result.output
    assert "scored_opportunities" in result.output
    assert "report_artifacts" in result.output
    assert "recommendation_outcomes" in result.output
    assert "read-only" in result.output


def test_preflight_command_prints_table_and_summary(tmp_path: Path) -> None:
    resources_path = tmp_path / "RESOURCES.md"
    resources_path.write_text(
        """
## Official Sources
- name: Approved API
  type: official
  url: https://example.test/api
  allowed_use: api
- name: Missing URL API
  type: official
  allowed_use: api
- name: Official Discord
  type: discord
  url: https://discord.com/channels/example
  allowed_use: api
- name: Manual Source
  allowed_use: manual-review
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["preflight", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert "Connector Preflight" in result.output
    assert "Preflight Summary" in result.output
    assert "Approved API" in result.output
    assert "Ready for source-specific connector design" in result.output
    assert "Missing URL API" in result.output
    assert "missing a URL" in result.output
    assert "Official Discord" in result.output
    assert "discord-gated" in result.output
    assert "placeholder-only" in result.output


def test_connector_check_ready_review_prints_ready_status(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Review Check" in result.output
    assert "Approved API" in result.output
    assert "yes" in result.output
    assert "ready for source-specific implementation planning" in result.output


def test_connector_candidates_prints_candidate_rows_and_draft_commands(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(
            allowed_use="manual-or-api-if-available",
            include_manual_source=True,
        ),
    )

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert "Connector Review Candidates" in result.output
    assert "poe.ninja POE2 Currency" in result.output
    assert "price_site" in result.output
    assert "needs-review" in result.output
    assert "wq connector-draft" in result.output
    assert "--resource poe_ninja_poe2_currency" in result.output
    assert "--access-method api" in result.output
    assert "advisory only" in result.output


def test_connector_candidates_marks_discord_as_compliance_gated(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert "Official Discord" in result.output
    assert "discord-gated" in result.output
    assert "Compliance-gated" in result.output


def test_connector_candidates_is_read_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available"),
    )

    result = runner.invoke(
        app,
        ["connector-candidates", "--resources-path", str(resources_path)],
    )

    assert result.exit_code == 0
    assert not (tmp_path / "examples").exists()
    assert not (tmp_path / "data").exists()


def test_connector_draft_writes_local_review_json(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(),
    )
    output_path = tmp_path / "review.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    from wraeclast_quant.config.connector_policy import load_connector_review

    review = load_connector_review(output_path)
    assert result.exit_code == 0
    assert "Wrote connector review draft" in result.output
    assert output_path.exists()
    assert review.resource_name == "poe.ninja POE2 Currency"
    assert review.access_method == "api"
    assert review.source_terms_reviewed is False
    assert review.robots_or_api_policy_reviewed is False
    assert review.source_terms_url == ""
    assert review.robots_or_api_policy_url == ""
    assert review.reviewed_at == ""
    assert review.review_notes == ""
    assert review.allowed_data_shape == ""
    assert review.dry_run_supported is True
    assert review.public_export_derived_only is True


def test_connector_review_prep_writes_draft_and_checklist(tmp_path: Path) -> None:
    resources_text = _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available")
    resources_path = _write_connector_resources(tmp_path, resources_text)
    output_dir = tmp_path / "reviews"

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    review_path = output_dir / "poe_ninja_poe2_currency_connector_review.json"
    checklist_path = output_dir / "poe_ninja_poe2_currency_review_checklist.md"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    checklist = checklist_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Connector Review Prep" in result.output
    assert "wq connector-review-status --review-path" in result.output
    assert "wq connector-approval-helper --review-path" in result.output
    assert "wq connector-check --review-path" in result.output
    assert "wq connector-plan --review-path" in result.output
    assert review["resource_name"] == "poe.ninja POE2 Currency"
    assert review["source_terms_reviewed"] is False
    assert review["robots_or_api_policy_reviewed"] is False
    assert "Source terms URL" in checklist
    assert "Allowed data shape" in checklist
    assert resources_path.read_text(encoding="utf-8") == resources_text


def test_connector_review_prep_untouched_draft_fails_connector_check(
    tmp_path: Path,
) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _poe_ninja_currency_resources_text(allowed_use="manual-or-api-if-available"),
    )
    output_dir = tmp_path / "reviews"

    prep_result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "poe_ninja_poe2_currency",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(output_dir),
        ],
    )
    check_result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(output_dir / "poe_ninja_poe2_currency_connector_review.json"),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert prep_result.exit_code == 0
    assert check_result.exit_code != 0
    assert "Source terms must be reviewed." in check_result.output


def test_connector_review_prep_rejects_missing_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        "\n## Price Data\n- name: Manual Source\n  allowed_use: manual-review\n",
    )

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "missing",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(tmp_path / "reviews"),
        ],
    )

    assert result.exit_code != 0
    assert "No matching resource" in result.output


def test_connector_review_prep_rejects_discord_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())

    result = runner.invoke(
        app,
        [
            "connector-review-prep",
            "--resource",
            "Official Discord",
            "--access-method",
            "api",
            "--resources-path",
            str(resources_path),
            "--output-dir",
            str(tmp_path / "reviews"),
        ],
    )

    assert result.exit_code != 0
    assert "Discord resources require explicit" in result.output


def test_connector_review_evidence_updates_json_and_prints_status(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _approved_api_resources_text())
    review_path = _write_connector_review(tmp_path, source_terms_reviewed=False)

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--source-terms-url",
            "https://example.test/terms",
            "--robots-or-api-policy-url",
            "https://example.test/api-policy",
            "--reviewed-at",
            "2026-05-23",
            "--allowed-data-shape",
            "Derived currency summary rows only.",
            "--review-notes",
            "Manual review completed.",
            "--rate-limit-per-minute",
            "30",
            "--cache-ttl-seconds",
            "3600",
        ],
    )
    updated = json.loads(review_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Updated connector review evidence" in result.output
    assert "Connector Review Status" in result.output
    assert "Readiness" in result.output
    assert updated["source_terms_reviewed"] is True
    assert updated["robots_or_api_policy_reviewed"] is True
    assert updated["source_terms_url"] == "https://example.test/terms"
    assert updated["robots_or_api_policy_url"] == "https://example.test/api-policy"
    assert updated["reviewed_at"] == "2026-05-23"
    assert updated["allowed_data_shape"] == "Derived currency summary rows only."
    assert updated["rate_limit_per_minute"] == 30
    assert updated["cache_ttl_seconds"] == 3600


def test_connector_review_evidence_preserves_unrelated_fields_and_resources(
    tmp_path: Path,
) -> None:
    resources_text = _approved_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, resources_text)
    review_path = _write_connector_review(
        tmp_path,
        review_notes="Existing note.",
        rate_limit_per_minute=12,
    )

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--reviewed-at",
            "2026-05-23",
        ],
    )
    updated = json.loads(review_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert updated["review_notes"] == "Existing note."
    assert updated["rate_limit_per_minute"] == 12
    assert updated["reviewed_at"] == "2026-05-23"
    assert resources_path.read_text(encoding="utf-8") == resources_text


def test_connector_review_evidence_invalid_values_exit_nonzero(tmp_path: Path) -> None:
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-review-evidence",
            "--review-path",
            str(review_path),
            "--rate-limit-per-minute",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "rate_limit_per_minute must be positive" in result.output


def test_connector_check_on_untouched_draft_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _approved_api_resources_text())
    review_path = tmp_path / "draft.json"
    draft_result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "approved_api",
            "--access-method",
            "api",
            "--output-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )
    check_result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert draft_result.exit_code == 0
    assert check_result.exit_code != 0
    assert "Source terms must be reviewed." in check_result.output
    assert "Robots.txt or API policy must be reviewed." in check_result.output


def test_connector_review_status_incomplete_review_exits_zero_with_blockers(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _approved_api_resources_text())
    review_path = tmp_path / "draft.json"
    draft_result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "approved_api",
            "--access-method",
            "api",
            "--output-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )
    status_result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert draft_result.exit_code == 0
    assert status_result.exit_code == 0
    assert "Connector Review Status" in status_result.output
    assert "Approved API" in status_result.output
    assert "Source terms URL" in status_result.output
    assert "Robots/API policy URL" in status_result.output
    assert "Allowed data shape" in status_result.output
    assert "not ready" in status_result.output
    assert "Source terms must be reviewed." in status_result.output
    assert "Robots.txt or API policy must be reviewed." in status_result.output


def test_connector_review_status_invalid_json_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = tmp_path / "review.json"
    review_path.write_text("{not json", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Invalid connector review JSON" in result.output


def test_connector_draft_rejects_missing_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    output_path = tmp_path / "draft.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "Missing API",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "No matching resource found" in result.output
    assert not output_path.exists()


def test_connector_draft_rejects_discord_resource(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _discord_resources_text())
    output_path = tmp_path / "draft.json"

    result = runner.invoke(
        app,
        [
            "connector-draft",
            "--resource",
            "Official Discord",
            "--access-method",
            "api",
            "--output-path",
            str(output_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Discord resources require explicit" in result.output
    assert not output_path.exists()


def test_connector_check_invalid_review_exits_nonzero_with_blockers(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _manual_source_resources_text())
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Manual Source",
        source_terms_reviewed=False,
    )

    result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Connector Review Check" in result.output
    assert "Manual Source" in result.output
    assert "not automation-eligible" in result.output
    assert "Source terms must be reviewed." in result.output


def test_connector_check_missing_claimed_evidence_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        source_terms_url="",
        robots_or_api_policy_url="",
        reviewed_at="",
        allowed_data_shape="",
    )

    result = runner.invoke(
        app,
        [
            "connector-check",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Connector Review Check" in result.output
    assert "source_terms_url is required" in result.output
    assert "robots_or_api_policy_url is required" in result.output
    assert "reviewed_at is required" in result.output
    assert "allowed_data_shape is required" in result.output


def test_connector_review_status_marks_missing_claimed_evidence_blocked(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        source_terms_url="",
        robots_or_api_policy_url="",
        reviewed_at="",
        allowed_data_shape="",
    )

    result = runner.invoke(
        app,
        [
            "connector-review-status",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Review Status" in result.output
    assert "Source terms URL" in result.output
    assert "blocked" in result.output
    assert "source_terms_url is required" in result.output


def test_connector_approval_helper_prints_manual_allowed_use_suggestion(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _conditional_api_resources_text())
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")

    result = runner.invoke(
        app,
        [
            "connector-approval-helper",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Approval Helper" in result.output
    assert "Conditional API" in result.output
    assert "manual-or-api-if-available" in result.output
    assert "allowed_use: api" in result.output
    assert "read-only" in result.output


def test_connector_approval_helper_incomplete_review_prints_blockers_without_suggestion(
    tmp_path: Path,
) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _conditional_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Conditional API",
        source_terms_url="",
    )

    result = runner.invoke(
        app,
        [
            "connector-approval-helper",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Connector Approval Helper" in result.output
    assert "source_terms_url is required" in result.output
    assert "allowed_use: api" not in result.output
    assert "None" in result.output


def test_connector_approval_helper_is_read_only(tmp_path: Path) -> None:
    original = _conditional_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, original)
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")

    result = runner.invoke(
        app,
        [
            "connector-approval-helper",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert resources_path.read_text(encoding="utf-8") == original


def test_connector_review_report_writes_markdown(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _conditional_api_resources_text())
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "review_report.md"

    result = runner.invoke(
        app,
        [
            "connector-review-report",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )
    markdown = output_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Connector Review Report" in result.output
    assert "Conditional API" in result.output
    assert "allowed_use: api" in result.output
    assert output_path.exists()
    assert "# Connector Review Report: Conditional API" in markdown
    assert "Current allowed_use: `manual-or-api-if-available`" in markdown
    assert "Approval suggestion: `allowed_use: api`" in markdown
    assert "Connector-check readiness: `not ready`" in markdown


def test_connector_review_report_invalid_review_exits_nonzero(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = tmp_path / "review.json"
    output_path = tmp_path / "review_report.md"
    review_path.write_text("{not json", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "connector-review-report",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert "Invalid connector review JSON" in result.output
    assert not output_path.exists()


def test_connector_review_report_is_read_only_for_resources(tmp_path: Path) -> None:
    original = _conditional_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, original)
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "review_report.md"

    result = runner.invoke(
        app,
        [
            "connector-review-report",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert resources_path.read_text(encoding="utf-8") == original


def test_connector_approval_patch_writes_patch_preview(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _conditional_api_resources_text())
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "approval.patch"

    result = runner.invoke(
        app,
        [
            "connector-approval-patch",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )
    patch_text = output_path.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Connector Approval Patch Preview" in result.output
    assert "Patch available" in result.output
    assert "yes" in result.output
    assert output_path.exists()
    assert "-  allowed_use: manual-or-api-if-available" in patch_text
    assert "+  allowed_use: api" in patch_text


def test_connector_approval_patch_incomplete_review_writes_no_patch(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _conditional_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Conditional API",
        source_terms_url="",
    )
    output_path = tmp_path / "approval.patch"

    result = runner.invoke(
        app,
        [
            "connector-approval-patch",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 1
    assert "Connector Approval Patch Preview" in result.output
    assert "source_terms_url is required" in result.output
    assert not output_path.exists()


def test_connector_approval_patch_does_not_modify_resources(tmp_path: Path) -> None:
    original = _conditional_api_resources_text()
    resources_path = _write_connector_resources(tmp_path, original)
    review_path = _write_connector_review(tmp_path, resource_name="Conditional API")
    output_path = tmp_path / "approval.patch"

    result = runner.invoke(
        app,
        [
            "connector-approval-patch",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert resources_path.read_text(encoding="utf-8") == original


def test_connector_fixture_run_prints_rows_and_count() -> None:
    result = runner.invoke(
        app,
        [
            "connector-fixture-run",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_api_example.json",
        ],
    )

    assert result.exit_code == 0
    assert "Connector Fixture Rows" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Fixture rows: 2" in result.output
    assert "Fetch plan cache path" in result.output
    assert "No network requests were made" in result.output


def test_connector_fixture_run_refuses_incomplete_review() -> None:
    result = runner.invoke(
        app,
        [
            "connector-fixture-run",
            "--review-path",
            "examples/poe_ninja_poe2_currency_connector_review.json",
            "--fixture-path",
            "examples/connector_fixture_api_example.json",
        ],
    )

    assert result.exit_code != 0
    assert "Connector Fixture Run" in result.output
    assert "Source terms must be reviewed." in result.output


def test_connector_fixture_run_invalid_fixture_exits_nonzero(tmp_path: Path) -> None:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps({"source_name": "Example Approved API", "generated_at": "now"}),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "connector-fixture-run",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            str(fixture_path),
        ],
    )

    assert result.exit_code != 0
    assert "Invalid connector fixture" in result.output


def test_connector_dry_run_prints_connector_class_rows_and_cache_path() -> None:
    result = runner.invoke(
        app,
        [
            "connector-dry-run",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_api_example.json",
        ],
    )

    assert result.exit_code == 0
    assert "Connector Dry Run" in result.output
    assert "FixtureSourceConnector" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Future cache path" in result.output
    assert "No network requests were made" in result.output


def test_connector_dry_run_prints_poe_ninja_currency_connector() -> None:
    result = runner.invoke(
        app,
        [
            "connector-dry-run",
            "--review-path",
            "examples/reviews/poe_ninja_poe2_currency_connector_review.json",
            "--fixture-path",
            "examples/poe_ninja_poe2_currency_fixture.json",
        ],
    )

    assert result.exit_code == 0
    assert "PoeNinjaCurrencyConnector" in result.output
    assert "poe-ninja-poe2-currency" in result.output
    assert "Exalted Orb" in result.output
    assert "No network requests were made" in result.output


def test_connector_dry_run_refuses_incomplete_review() -> None:
    result = runner.invoke(
        app,
        [
            "connector-dry-run",
            "--review-path",
            "examples/poe_ninja_poe2_currency_connector_review.json",
            "--fixture-path",
            "examples/connector_fixture_api_example.json",
        ],
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output


def test_connector_dry_run_is_read_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "Approved API",
                "generated_at": "2026-05-23T00:00:00+00:00",
                "items": [{"name": "Stormglass Catalyst"}],
            }
        ),
        encoding="utf-8",
    )
    resources_path = _write_connector_resources(
        tmp_path,
        "\n## Fixture Sources\n- name: Approved API\n  type: official\n  url: https://example.test/api\n  allowed_use: api\n",
    )
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-dry-run",
            "--review-path",
            str(review_path),
            "--fixture-path",
            str(fixture_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert not Path("data/raw/cache").exists()
    assert not Path("data/wraeclast_quant.db").exists()


def test_connector_fixture_export_writes_manual_import_json(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        [
            "connector-fixture-export",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--output-path",
            str(output_path),
        ],
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Connector Fixture Export" in result.output
    assert "2" in result.output
    assert str(output_path) in result.output
    assert payload["items"][0]["name"] == "Stormglass Catalyst"
    assert "signals" in payload["items"][0]


def test_connector_fixture_export_rejects_fixture_without_signals(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        [
            "connector-fixture-export",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_api_example.json",
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert "requires normalized signals" in result.output
    assert not output_path.exists()


def test_connector_fixture_export_refuses_incomplete_review(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        [
            "connector-fixture-export",
            "--review-path",
            "examples/poe_ninja_poe2_currency_connector_review.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output
    assert not output_path.exists()


def test_connector_fixture_daily_writes_artifacts(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--database-path",
            str(database_path),
            "--brief-path",
            str(brief_path),
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    assert result.exit_code == 0
    assert brief_path.exists()
    assert intel_path.exists()
    assert (site_dir / "index.html").exists()
    assert "Connector fixture daily run #1 complete." in result.output
    assert str(brief_path) in result.output
    assert str(intel_path) in result.output


def test_connector_fixture_daily_creates_one_connector_fixture_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--database-path",
            str(database_path),
        ],
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert len(runs) == 1
    assert runs[0].source_mode == "connector-fixture"


def test_connector_fixture_daily_stores_sanitized_run_provenance(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--database-path",
            str(database_path),
        ],
    )

    provenance = SnapshotRepository(database_path).latest_run_provenance()
    assert result.exit_code == 0
    assert provenance is not None
    assert provenance.source_kind == "connector-fixture"
    assert provenance.resource_name == "Example Approved API"
    assert provenance.connector_id == "fixture-source-connector"
    assert provenance.access_method == "api"
    assert provenance.metadata["connector_class"] == "FixtureSourceConnector"
    assert provenance.metadata["fixture_item_count"] == 2
    assert provenance.metadata["review_file"] == "connector_review_api_example.json"
    assert provenance.metadata["fixture_file"] == "connector_fixture_signals_example.json"
    assert "review_sha256" in provenance.metadata
    assert "fixture_sha256" in provenance.metadata
    serialized = json.dumps(provenance.metadata, sort_keys=True)
    assert "https://" not in serialized
    assert "demand_momentum" not in serialized
    assert str(tmp_path) not in serialized


def test_connector_fixture_daily_uses_poe_ninja_connector_provenance(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/reviews/poe_ninja_poe2_currency_connector_review.json",
            "--fixture-path",
            "examples/poe_ninja_poe2_currency_fixture.json",
            "--database-path",
            str(database_path),
            "--brief-path",
            str(brief_path),
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    provenance = SnapshotRepository(database_path).latest_run_provenance()
    assert result.exit_code == 0
    assert provenance is not None
    assert provenance.connector_id == "poe-ninja-poe2-currency"
    assert provenance.metadata["connector_class"] == "PoeNinjaCurrencyConnector"


def test_connector_fixture_daily_public_intel_latest_run_matches_created_run(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--database-path",
            str(database_path),
            "--intel-path",
            str(intel_path),
        ],
    )

    latest = SnapshotRepository(database_path).latest_run()
    payload = json.loads(intel_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert latest is not None
    assert payload["latest_run"]["id"] == latest.id
    assert payload["latest_run"]["source_mode"] == "connector-fixture"


def test_connector_fixture_daily_static_site_includes_fixture_items(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--database-path",
            str(database_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    assert result.exit_code == 0
    site_text = (site_dir / "index.html").read_text(encoding="utf-8")
    assert "Stormglass Catalyst" in site_text
    assert "Ashen Rune Core" in site_text


def test_connector_fixture_daily_rejects_fixture_without_signals(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            "examples/connector_fixture_api_example.json",
            "--database-path",
            str(database_path),
        ],
    )

    assert result.exit_code != 0
    assert "requires normalized signals" in result.output
    assert not database_path.exists()


def test_connector_fixture_daily_refuses_incomplete_review(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/poe_ninja_poe2_currency_connector_review.json",
            "--fixture-path",
            "examples/connector_fixture_signals_example.json",
            "--database-path",
            str(database_path),
        ],
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output
    assert not database_path.exists()


def test_connector_fixture_daily_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "Example Approved API",
                "generated_at": "2026-05-23T00:00:00+00:00",
                "items": [
                    {
                        "name": "Stormglass Catalyst",
                        "signals": _manual_item("Stormglass Catalyst")["signals"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    repository = SnapshotRepository(database_path)
    _save_single_opportunity_run(
        repository,
        "Stormglass Catalyst",
        60.0,
        "WATCH",
        source_mode="connector-fixture",
    )

    result = runner.invoke(
        app,
        [
            "connector-fixture-daily",
            "--review-path",
            "examples/connector_review_api_example.json",
            "--fixture-path",
            str(fixture_path),
            "--database-path",
            str(database_path),
            "--big-delta",
            "20",
        ],
    )

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output


def test_run_provenance_prints_latest_provenance(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="connector-fixture", item_count=1)
    repository.save_run_provenance(
        run.id,
        source_kind="connector-fixture",
        resource_name="Example Approved API",
        connector_id="fixture-source-connector",
        access_method="api",
        metadata={"fixture_item_count": 1, "future_cache_path": "data/raw/cache/example.cache"},
    )

    result = runner.invoke(app, ["run-provenance", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Run Provenance - Run #1" in result.output
    assert "connector-fixture" in result.output
    assert "Example Approved API" in result.output
    assert "fixture_item_count" in result.output
    assert "Run provenance is local-only and read-only" in result.output


def test_run_provenance_prints_requested_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    first = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    second = repository.create_analysis_run(source_mode="connector-fixture", item_count=1)
    repository.save_run_provenance(
        first.id,
        source_kind="manual",
        resource_name="Manual",
        connector_id="none",
        access_method="manual",
        metadata={"label": "first"},
    )
    repository.save_run_provenance(
        second.id,
        source_kind="connector-fixture",
        resource_name="Example Approved API",
        connector_id="fixture-source-connector",
        access_method="api",
        metadata={"label": "second"},
    )

    result = runner.invoke(
        app,
        ["run-provenance", "--database-path", str(database_path), "--run-id", str(first.id)],
    )

    assert result.exit_code == 0
    assert "Run Provenance - Run #1" in result.output
    assert "first" in result.output
    assert "second" not in result.output


def test_run_provenance_missing_provenance_prints_clear_message(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    SnapshotRepository(database_path).create_analysis_run(source_mode="sample-data", item_count=0)

    result = runner.invoke(app, ["run-provenance", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "No run provenance found." in result.output


def test_run_provenance_missing_database_does_not_create_database(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = runner.invoke(app, ["run-provenance", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "No run provenance found." in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_connector_plan_ready_review_prints_fetch_plan(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-plan",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert "Safe Fetch Plan" in result.output
    assert "Approved API" in result.output
    assert "data\\raw\\cache" in result.output or "data/raw/cache" in result.output
    assert "2.00s" in result.output
    assert "No network requests were made" in result.output


def test_connector_plan_invalid_review_exits_nonzero_with_blockers(tmp_path: Path) -> None:
    resources_path = _write_connector_resources(tmp_path, _manual_source_resources_text())
    review_path = _write_connector_review(
        tmp_path,
        resource_name="Manual Source",
        source_terms_reviewed=False,
    )

    result = runner.invoke(
        app,
        [
            "connector-plan",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code != 0
    assert "Safe Fetch Plan" in result.output
    assert "not automation-eligible" in result.output
    assert "Source terms must be reviewed." in result.output


def test_connector_plan_does_not_create_cache_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    resources_path = _write_connector_resources(
        tmp_path,
        _approved_api_resources_text(include_id=False),
    )
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        [
            "connector-plan",
            "--review-path",
            str(review_path),
            "--resources-path",
            str(resources_path),
        ],
    )

    assert result.exit_code == 0
    assert not Path("data/raw/cache").exists()


def test_report_sample_data(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("data/processed").mkdir(parents=True)

    result = runner.invoke(app, ["report", "--sample-data"])

    assert result.exit_code == 0
    assert Path("data/processed/market_brief.md").exists()


def test_watchlist() -> None:
    result = runner.invoke(app, ["watchlist"])

    assert result.exit_code == 0
    assert "Watchlist" in result.output


def test_analyze_sample_data_records_snapshot(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        ["analyze", "--sample-data", "--database-path", str(database_path)],
    )

    assert result.exit_code == 0
    assert database_path.exists()
    assert "Recorded analysis run" in result.output


def test_report_sample_data_records_artifact(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        ["report", "--sample-data", "--database-path", str(database_path)],
    )

    assert result.exit_code == 0
    assert Path("data/processed/market_brief.md").exists()
    assert database_path.exists()
    assert "Recorded report artifact" in result.output


def test_report_sample_data_includes_snapshot_changes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    database_path = _previous_stormglass_database(tmp_path)

    result = runner.invoke(
        app,
        ["report", "--sample-data", "--database-path", str(database_path)],
    )

    report = Path("data/processed/market_brief.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "## Snapshot Changes" in report


def test_snapshots_command_prints_latest_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    runner.invoke(app, ["analyze", "--sample-data", "--database-path", str(database_path)])

    result = runner.invoke(app, ["snapshots", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Recent Analysis Runs" in result.output
    assert "Stormglass Catalyst" in result.output


def test_backup_db_command_writes_local_backup(tmp_path: Path) -> None:
    database_path = _sample_data_database(tmp_path)
    backup_dir = tmp_path / "backups"

    result = runner.invoke(
        app,
        [
            "backup-db",
            "--database-path",
            str(database_path),
            "--output-dir",
            str(backup_dir),
        ],
    )

    backups = list(backup_dir.glob("snapshots_*.db"))
    assert result.exit_code == 0
    assert "Local SQLite Backup" in result.output
    assert "local-only" in result.output
    assert "Verified" in result.output
    assert "Schema version" in result.output
    assert "Analysis runs" in result.output
    assert "Latest source" in result.output
    assert "sample-data" in result.output
    assert len(backups) == 1
    assert SnapshotRepository(backups[0]).latest_run() is not None


def test_backup_db_command_handles_missing_database_without_creating_output_dir(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"
    backup_dir = tmp_path / "backups"

    result = runner.invoke(
        app,
        [
            "backup-db",
            "--database-path",
            str(database_path),
            "--output-dir",
            str(backup_dir),
        ],
    )

    assert result.exit_code == 0
    assert "No database found to back up." in result.output
    assert not database_path.exists()
    assert not backup_dir.exists()


def test_verify_backup_command_prints_counts(tmp_path: Path) -> None:
    _database_path, _backup_dir, backup_path = _sample_data_backup(tmp_path)

    result = runner.invoke(app, ["verify-backup", "--backup-path", str(backup_path)])

    assert result.exit_code == 0
    assert "SQLite Backup Verification" in result.output
    assert "Schema version" in result.output
    assert "Required table names" in result.output
    assert "Analysis runs" in result.output
    assert "Scored opportunities" in result.output
    assert "10" in result.output
    assert "read-only" in result.output


def test_verify_backup_command_rejects_missing_file_without_creating_it(tmp_path: Path) -> None:
    backup_path = tmp_path / "missing" / "backup.db"

    result = runner.invoke(app, ["verify-backup", "--backup-path", str(backup_path)])

    assert result.exit_code != 0
    assert "Backup file not found" in result.output
    assert not backup_path.exists()
    assert not backup_path.parent.exists()


def test_db_check_command_prints_database_health(tmp_path: Path) -> None:
    database_path = _sample_data_database(tmp_path)

    result = runner.invoke(app, ["db-check", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "SQLite Database Check" in result.output
    assert "Schema version" in result.output
    assert "Required table names" in result.output
    assert "Integrity" in result.output
    assert "Required tables" in result.output
    assert "Analysis runs" in result.output
    assert "Latest source" in result.output
    assert "sample-data" in result.output
    assert "read-only" in result.output


def test_db_check_command_handles_missing_database_without_creating_it(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = runner.invoke(app, ["db-check", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "No database found." in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_backups_command_lists_local_backups(tmp_path: Path) -> None:
    _database_path, backup_dir, _backup_path = _sample_data_backup(tmp_path)

    result = runner.invoke(app, ["backups", "--backup-dir", str(backup_dir)])

    assert result.exit_code == 0
    assert "Local SQLite Backups" in result.output
    assert "valid" in result.output
    assert "snapshots_" in result.output
    assert "sample-data" in result.output
    assert "read-only" in result.output


def test_backups_command_handles_missing_directory_without_creating_it(tmp_path: Path) -> None:
    backup_dir = tmp_path / "missing_backups"

    result = runner.invoke(app, ["backups", "--backup-dir", str(backup_dir)])

    assert result.exit_code == 0
    assert "No database backups found." in result.output
    assert not backup_dir.exists()


def test_restore_helper_prints_manual_restore_command_without_writing_target(tmp_path: Path) -> None:
    _database_path, _backup_dir, backup_path = _sample_data_backup(tmp_path)
    target_path = tmp_path / "restore" / "snapshots.db"

    result = runner.invoke(
        app,
        [
            "restore-helper",
            "--backup-path",
            str(backup_path),
            "--database-path",
            str(target_path),
        ],
    )

    assert result.exit_code == 0
    assert "SQLite Restore Helper" in result.output
    assert "Manual PowerShell restore command" in result.output
    assert "Copy-Item -LiteralPath" in result.output
    assert "Restore helper is read-only" in result.output
    assert not target_path.exists()
    assert not target_path.parent.exists()


def test_restore_helper_rejects_missing_backup_without_creating_target(tmp_path: Path) -> None:
    backup_path = tmp_path / "missing" / "backup.db"
    target_path = tmp_path / "restore" / "snapshots.db"

    result = runner.invoke(
        app,
        [
            "restore-helper",
            "--backup-path",
            str(backup_path),
            "--database-path",
            str(target_path),
        ],
    )

    assert result.exit_code != 0
    assert "Backup file not found" in result.output
    assert not backup_path.exists()
    assert not backup_path.parent.exists()
    assert not target_path.exists()
    assert not target_path.parent.exists()


def test_migration_readiness_command_prints_table(tmp_path: Path) -> None:
    database_path, backup_dir, _backup_path = _sample_data_backup(tmp_path)

    result = runner.invoke(
        app,
        [
            "migration-readiness",
            "--database-path",
            str(database_path),
            "--backup-dir",
            str(backup_dir),
        ],
    )

    assert result.exit_code == 0
    assert "SQLite Migration Readiness" in result.output
    assert "Migration readiness" in result.output
    assert "ready" in result.output


def test_migration_readiness_json_outputs_stable_fields(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    backup_dir = tmp_path / "backups"
    run = SnapshotRepository(database_path).create_analysis_run(source_mode="sample-data", item_count=1)
    runner.invoke(
        app,
        [
            "backup-db",
            "--database-path",
            str(database_path),
            "--output-dir",
            str(backup_dir),
        ],
    )

    result = runner.invoke(
        app,
        [
            "migration-readiness",
            "--json",
            "--database-path",
            str(database_path),
            "--backup-dir",
            str(backup_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ready"] is True
    assert payload["schema_version"] == "2"
    assert payload["latest_database_run_id"] == run.id
    assert payload["latest_backup_run_id"] == run.id
    assert payload["blockers"] == []
    assert isinstance(payload["checks"], list)


def test_migration_readiness_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"
    backup_dir = tmp_path / "missing_backups"

    result = runner.invoke(
        app,
        [
            "migration-readiness",
            "--strict",
            "--database-path",
            str(database_path),
            "--backup-dir",
            str(backup_dir),
        ],
    )

    assert result.exit_code == 1
    assert "not ready" in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()
    assert not backup_dir.exists()


def test_read_only_snapshot_commands_do_not_create_missing_database(tmp_path: Path) -> None:
    for index, (command, expected_output) in enumerate(
        _read_only_missing_database_command_cases(tmp_path)
    ):
        database_path = tmp_path / f"missing-{index}" / "snapshots.db"
        result = runner.invoke(
            app,
            [
                *command,
                "--database-path",
                str(database_path),
            ],
        )

        assert result.exit_code == 0
        assert expected_output in result.output
        assert not database_path.exists()


def test_record_outcome_command_saves_manual_outcome(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    runner.invoke(app, ["analyze", "--sample-data", "--database-path", str(database_path)])

    result = runner.invoke(
        app,
        [
            "record-outcome",
            "--database-path",
            str(database_path),
            "--run-id",
            "1",
            "--item-name",
            "Stormglass Catalyst",
            "--outcome",
            "positive",
            "--notes",
            "Reviewed manually.",
        ],
    )

    records = SnapshotRepository(database_path).list_recent_outcomes()
    assert result.exit_code == 0
    assert "Recorded positive outcome" in result.output
    assert len(records) == 1
    assert records[0].item_name == "Stormglass Catalyst"
    assert records[0].notes == "Reviewed manually."


def test_record_outcome_command_rejects_missing_item(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    runner.invoke(app, ["analyze", "--sample-data", "--database-path", str(database_path)])

    result = runner.invoke(
        app,
        [
            "record-outcome",
            "--database-path",
            str(database_path),
            "--run-id",
            "1",
            "--item-name",
            "Missing Item",
            "--outcome",
            "positive",
        ],
    )

    assert result.exit_code != 0
    assert "Missing Item" in result.output
    assert SnapshotRepository(database_path).list_recent_outcomes() == []


def test_outcomes_command_prints_recent_outcomes_and_summary(tmp_path: Path) -> None:
    database_path, _run = _reviewed_single_opportunity_database(tmp_path)

    result = runner.invoke(app, ["outcomes", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Recommendation Outcomes" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Outcome Summary" in result.output
    assert "positive" in result.output


def test_outcomes_command_handles_empty_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["outcomes", "--database-path", str(tmp_path / "snapshots.db")],
    )

    assert result.exit_code == 0
    assert "No recommendation outcomes recorded." in result.output


def test_review_queue_command_prints_unreviewed_latest_run(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)

    result = runner.invoke(app, ["review-queue", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Recommendation Review Queue" in result.output
    assert "#1" in result.output
    assert "Open Catalyst" in result.output
    assert "Reviewed Catalyst" not in result.output
    assert "record-outcome" in result.output


def test_review_queue_command_uses_requested_run_id(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    first = _save_single_opportunity_run(repository, "First Run Item", 50.0, "WATCH")
    _save_single_opportunity_run(repository, "Second Run Item", 70.0, "BUY")

    result = runner.invoke(
        app,
        ["review-queue", "--database-path", str(database_path), "--run-id", str(first.id)],
    )

    assert result.exit_code == 0
    assert "First Run Item" in result.output
    assert "Second Run Item" not in result.output


def test_review_queue_command_handles_no_snapshots(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["review-queue", "--database-path", str(tmp_path / "snapshots.db")],
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output


def test_review_queue_command_handles_fully_reviewed_run(tmp_path: Path) -> None:
    database_path, _run = _reviewed_single_opportunity_database(
        tmp_path,
        item_name="Reviewed Catalyst",
    )

    result = runner.invoke(app, ["review-queue", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "No unreviewed recommendations found for run #1." in result.output


def test_review_queue_command_rejects_missing_run(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["review-queue", "--database-path", str(tmp_path / "snapshots.db"), "--run-id", "99"],
    )

    assert result.exit_code != 0
    assert "analysis run #99 was not found" in result.output


def test_review_coverage_command_prints_latest_run_coverage(tmp_path: Path) -> None:
    database_path, _run = _partially_reviewed_two_item_database(tmp_path)

    result = runner.invoke(app, ["review-coverage", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Recommendation Review Coverage" in result.output
    assert "#1" in result.output
    assert "50.0%" in result.output


def test_review_coverage_command_uses_requested_run_id(tmp_path: Path) -> None:
    database_path, first, _second = _two_run_database_with_second_reviewed(tmp_path)

    result = runner.invoke(
        app,
        ["review-coverage", "--database-path", str(database_path), "--run-id", str(first.id)],
    )

    assert result.exit_code == 0
    assert "0.0%" in result.output


def test_review_coverage_command_handles_no_snapshots(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["review-coverage", "--database-path", str(tmp_path / "snapshots.db")],
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output


def test_outcome_review_command_prints_joined_review_and_summary(tmp_path: Path) -> None:
    database_path, _run = _reviewed_single_opportunity_database(
        tmp_path,
        notes="Manual review.",
    )

    result = runner.invoke(app, ["outcome-review", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Recommendation Outcome Review" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "76.00" in result.output
    assert "BUY" in result.output
    assert "positive" in result.output
    assert "Outcome Review By Action" in result.output


def test_outcome_review_command_handles_empty_database(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["outcome-review", "--database-path", str(tmp_path / "snapshots.db")],
    )

    assert result.exit_code == 0
    assert "No reviewed recommendation outcomes found." in result.output


def test_outcome_report_command_writes_markdown_report(tmp_path: Path) -> None:
    output_path = tmp_path / "outcome_review.md"
    database_path, _run = _reviewed_single_opportunity_database(
        tmp_path,
        notes="Manual review.",
    )

    result = runner.invoke(
        app,
        [
            "outcome-report",
            "--database-path",
            str(database_path),
            "--output-path",
            str(output_path),
        ],
    )

    report = output_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Wrote outcome review report" in result.output
    assert "# Wraeclast Quant Outcome Review" in report
    assert "Stormglass Catalyst" in report
    assert "Manual review." in report


def test_outcome_report_command_writes_empty_report(tmp_path: Path) -> None:
    output_path = tmp_path / "outcome_review.md"

    result = runner.invoke(
        app,
        [
            "outcome-report",
            "--database-path",
            str(tmp_path / "snapshots.db"),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert "Wrote empty outcome review report" in result.output
    assert "No reviewed recommendation outcomes found." in output_path.read_text(encoding="utf-8")


def test_calibration_command_prints_local_summaries(tmp_path: Path) -> None:
    database_path = _calibration_reviewed_database(tmp_path)

    result = runner.invoke(app, ["calibration", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Calibration By Action" in result.output
    assert "Calibration By Score Bucket" in result.output
    assert "Average Score By Outcome" in result.output
    assert "Recent Reviewed Recommendations" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "local-only and read-only" in result.output


def test_calibration_command_missing_database_is_non_mutating(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = runner.invoke(app, ["calibration", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "No reviewed recommendation outcomes found." in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_calibration_report_command_writes_markdown(tmp_path: Path) -> None:
    output_path = tmp_path / "calibration_report.md"
    database_path, _run = _reviewed_single_opportunity_database(tmp_path)

    result = runner.invoke(
        app,
        [
            "calibration-report",
            "--database-path",
            str(database_path),
            "--output-path",
            str(output_path),
        ],
    )

    report = output_path.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Wrote calibration report" in result.output
    assert "# Wraeclast Quant Recommendation Calibration" in report
    assert "Stormglass Catalyst" in report
    assert "Outcome Counts By Action" in report


def test_compare_command_prints_delta(tmp_path: Path) -> None:
    database_path = _comparison_database_with_changes(tmp_path)

    result = runner.invoke(app, ["compare", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Top Movers" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "+26.00" in result.output
    assert "New Catalyst" in result.output
    assert "Removed Relic" in result.output


def test_compare_command_handles_missing_previous_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    repository.create_analysis_run(source_mode="sample-data", item_count=0)

    result = runner.invoke(app, ["compare", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "No previous snapshot found for comparison." in result.output


def test_alerts_command_prints_candidates(tmp_path: Path) -> None:
    database_path = _buy_crossing_database(tmp_path)

    result = runner.invoke(app, ["alerts", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "Local Alert Preview" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Score crossed into BUY" in result.output


def test_alerts_command_handles_stable_comparison(tmp_path: Path) -> None:
    database_path = _stable_watch_database(tmp_path)

    result = runner.invoke(app, ["alerts", "--database-path", str(database_path)])

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output


def test_alerts_command_uses_tuned_thresholds(tmp_path: Path) -> None:
    database_path = _buy_crossing_database(tmp_path)

    result = runner.invoke(
        app,
        [
            "alerts",
            "--database-path",
            str(database_path),
            "--watch-threshold",
            "55",
            "--buy-threshold",
            "90",
            "--big-delta",
            "100",
        ],
    )

    assert result.exit_code == 0
    assert "Score crossed into WATCH" in result.output
    assert "Score crossed into BUY" not in result.output


def test_alerts_command_rejects_invalid_threshold_order(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "alerts",
            "--database-path",
            str(tmp_path / "snapshots.db"),
            "--watch-threshold",
            "80",
            "--buy-threshold",
            "70",
        ],
    )

    assert result.exit_code != 0
    assert "buy_threshold" in result.output


def test_export_command_writes_public_intel(tmp_path: Path) -> None:
    database_path = _buy_crossing_database(tmp_path)
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        [
            "export",
            "--database-path",
            str(database_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Wrote public intel export" in result.output
    assert "Stormglass Catalyst" in output_path.read_text(encoding="utf-8")


def test_export_command_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path = _small_mover_database(tmp_path)
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        [
            "export",
            "--database-path",
            str(database_path),
            "--output-path",
            str(output_path),
            "--big-delta",
            "20",
        ],
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert payload["alerts"] == []


def test_export_command_handles_no_snapshots(tmp_path: Path) -> None:
    database_path = tmp_path / "empty.db"
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        [
            "export",
            "--database-path",
            str(database_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
    assert not output_path.exists()


def test_validate_intel_command_accepts_exported_public_intel(tmp_path: Path) -> None:
    database_path = _single_buy_database(tmp_path)
    output_path = tmp_path / "public_intel.json"
    runner.invoke(
        app,
        [
            "export",
            "--database-path",
            str(database_path),
            "--output-path",
            str(output_path),
        ],
    )

    result = runner.invoke(app, ["validate-intel", "--intel-path", str(output_path)])

    assert result.exit_code == 0
    assert "Public Intel Contract Validation" in result.output
    assert "Schema version" in result.output
    assert "1.0" in result.output
    assert "matches the local derived-only contract" in result.output


def test_validate_intel_command_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "generated_at": "2026-05-23T00:00:00+00:00",
                "latest_run": {
                    "id": 1,
                    "created_at": "2026-05-23T00:00:00+00:00",
                    "source_mode": "sample-data",
                    "item_count": 1,
                },
                "recent_runs": [],
                "top_opportunities": [{"item_name": "Bad", "inputs": {"demand_momentum": 1}}],
                "score_trends": [],
                "snapshot_changes": {"top_movers": [], "status_changes": []},
                "alerts": [],
                "outcome_summary": {},
                "review_coverage": {},
                "compliance_summary": {
                    "total_resources": 0,
                    "status_counts": {},
                    "automation_eligible_count": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["validate-intel", "--intel-path", str(intel_path)])

    assert result.exit_code != 0
    assert "Public Intel Contract Validation" in result.output
    assert "Raw/private field is not allowed" in result.output


def test_site_command_writes_index_html(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    output_dir = tmp_path / "site"
    intel_path.write_text(json.dumps(_public_intel_payload()), encoding="utf-8")

    result = runner.invoke(
        app,
        ["site", "--intel-path", str(intel_path), "--output-dir", str(output_dir)],
    )

    index_path = output_dir / "index.html"
    assert result.exit_code == 0
    assert index_path.exists()
    assert "Wrote local dashboard preview" in result.output
    assert "Stormglass Catalyst" in index_path.read_text(encoding="utf-8")


def test_site_command_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    output_dir = tmp_path / "site"
    payload = _public_intel_payload()
    del payload["schema_version"]
    intel_path.write_text(json.dumps(payload), encoding="utf-8")

    result = runner.invoke(
        app,
        ["site", "--intel-path", str(intel_path), "--output-dir", str(output_dir)],
    )

    assert result.exit_code != 0
    assert "Public intel contract validation failed" in result.output
    assert "Missing required keys: schema_version" in result.output
    assert not (output_dir / "index.html").exists()


def test_site_command_handles_missing_public_intel(tmp_path: Path) -> None:
    output_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        ["site", "--intel-path", str(tmp_path / "missing.json"), "--output-dir", str(output_dir)],
    )

    assert result.exit_code == 0
    assert "No public intel export found. Run wq export first." in result.output
    assert not (output_dir / "index.html").exists()


def test_site_bundle_command_writes_local_bundle(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    output_dir = tmp_path / "bundle"
    intel_path.write_text(json.dumps(_public_intel_payload()), encoding="utf-8")
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "site-bundle",
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Local Site Bundle" in result.output
    assert "wraeclast_quant_site_bundle.zip" in result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "public_intel.json").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "wraeclast_quant_site_bundle.zip").exists()


def test_site_bundle_command_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    output_dir = tmp_path / "bundle"
    intel_path.write_text(json.dumps({"latest_run": {"id": 7}}), encoding="utf-8")
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "site-bundle",
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code != 0
    assert "Public intel contract validation failed" in result.output
    assert not output_dir.exists()


def test_site_bundle_command_handles_missing_inputs(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "site-bundle",
            "--intel-path",
            str(tmp_path / "missing.json"),
            "--site-dir",
            str(tmp_path / "missing_site"),
            "--output-dir",
            str(tmp_path / "bundle"),
        ],
    )

    assert result.exit_code != 0
    assert "No public intel export found. Run wq export first." in result.output
    assert not (tmp_path / "bundle").exists()


def test_publish_check_ready_bundle_prints_readiness(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)

    result = runner.invoke(
        app,
        [
            "publish-check",
            "--database-path",
            str(database_path),
            "--bundle-dir",
            str(bundle_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Local Publish Readiness" in result.output
    assert "Manual publishing readiness" in result.output
    assert "ready" in result.output
    assert "Publish check is local-only" in result.output


def test_publish_check_json_outputs_stable_fields(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)

    result = runner.invoke(
        app,
        [
            "publish-check",
            "--json",
            "--database-path",
            str(database_path),
            "--bundle-dir",
            str(bundle_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ready"] is True
    assert payload["latest_database_run_id"] == run_id
    assert payload["bundle_latest_run_id"] == run_id
    assert payload["blockers"] == []
    assert isinstance(payload["checks"], list)


def test_publish_check_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    SnapshotRepository(database_path).create_analysis_run(source_mode="sample-data", item_count=1)
    missing_bundle = tmp_path / "missing_bundle"

    result = runner.invoke(
        app,
        [
            "publish-check",
            "--strict",
            "--database-path",
            str(database_path),
            "--bundle-dir",
            str(missing_bundle),
        ],
    )

    assert result.exit_code == 1
    assert "not found" in result.output
    assert not missing_bundle.exists()


def test_publish_handoff_ready_bundle_writes_report(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "publish_handoff.md"

    result = runner.invoke(
        app,
        [
            "publish-handoff",
            "--database-path",
            str(database_path),
            "--bundle-dir",
            str(bundle_dir),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert "Manual Publish Handoff" in result.output
    assert "ready" in result.output
    report = output_path.read_text(encoding="utf-8")
    assert f"Latest database run: `#{run_id}`" in report
    assert "Manual Publishing Checklist" in report


def test_publish_handoff_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")
    output_path = tmp_path / "publish_handoff.md"

    result = runner.invoke(
        app,
        [
            "publish-handoff",
            "--database-path",
            str(database_path),
            "--bundle-dir",
            str(bundle_dir),
            "--output-path",
            str(output_path),
            "--strict",
        ],
    )

    assert result.exit_code == 1
    assert output_path.exists()
    assert "not ready" in result.output
    assert "Public intel contract" in output_path.read_text(encoding="utf-8")


def test_site_contract_ready_bundle_writes_json(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "site_contract.json"

    result = runner.invoke(
        app,
        [
            "site-contract",
            "--database-path",
            str(database_path),
            "--bundle-dir",
            str(bundle_dir),
            "--output-path",
            str(output_path),
        ],
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert "Public Site Contract" in result.output
    assert "ready" in result.output
    assert payload["schema_version"] == "1.0"
    assert payload["product"] == "Wraeclast Quant"
    assert payload["latest_database_run_id"] == run_id
    assert payload["artifact_run_ids"]["bundle"] == run_id
    assert payload["artifact_run_ids"]["public_intel"] == run_id
    assert payload["artifact_run_ids"]["static_site"] == run_id
    assert payload["publish_readiness"]["ready"] is True
    assert payload["safety"]["derived_only"] is True


def test_site_contract_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")
    output_path = tmp_path / "site_contract.json"

    result = runner.invoke(
        app,
        [
            "site-contract",
            "--database-path",
            str(database_path),
            "--bundle-dir",
            str(bundle_dir),
            "--output-path",
            str(output_path),
            "--strict",
        ],
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.exit_code == 1
    assert output_path.exists()
    assert "not ready" in result.output
    assert payload["publish_readiness"]["ready"] is False
    assert "Public intel contract" in result.output


def test_daily_sample_data_writes_artifacts(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        [
            "daily",
            "--sample-data",
            "--database-path",
            str(database_path),
            "--brief-path",
            str(brief_path),
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    assert result.exit_code == 0
    assert brief_path.exists()
    assert intel_path.exists()
    assert (site_dir / "index.html").exists()
    assert "Daily run #1 complete." in result.output
    assert str(brief_path) in result.output
    assert str(intel_path) in result.output


def test_daily_creates_exactly_one_analysis_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        ["daily", "--sample-data", "--database-path", str(database_path)],
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert len(runs) == 1


def test_daily_brief_includes_snapshot_changes_with_previous_run(tmp_path: Path) -> None:
    database_path = _previous_stormglass_database(tmp_path)
    brief_path = tmp_path / "market_brief.md"

    result = runner.invoke(
        app,
        [
            "daily",
            "--sample-data",
            "--database-path",
            str(database_path),
            "--brief-path",
            str(brief_path),
        ],
    )

    assert result.exit_code == 0
    assert "## Snapshot Changes" in brief_path.read_text(encoding="utf-8")


def test_daily_public_intel_latest_run_matches_daily_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        [
            "daily",
            "--sample-data",
            "--database-path",
            str(database_path),
            "--intel-path",
            str(intel_path),
        ],
    )

    latest = SnapshotRepository(database_path).latest_run()
    payload = json.loads(intel_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert latest is not None
    assert payload["latest_run"]["id"] == latest.id


def test_daily_site_includes_title(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        [
            "daily",
            "--sample-data",
            "--database-path",
            str(database_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Wraeclast Quant" in (site_dir / "index.html").read_text(encoding="utf-8")


def test_daily_input_path_writes_artifacts(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        [
            "daily",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
            "--brief-path",
            str(brief_path),
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    assert result.exit_code == 0
    assert brief_path.exists()
    assert intel_path.exists()
    assert (site_dir / "index.html").exists()
    assert "Daily run #1 complete." in result.output
    assert "Manual Daily Catalyst" in intel_path.read_text(encoding="utf-8")


def test_daily_input_path_creates_one_manual_import_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        [
            "daily",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
        ],
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"


def test_daily_input_path_public_intel_latest_run_matches_created_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        [
            "daily",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
            "--intel-path",
            str(intel_path),
        ],
    )

    latest = SnapshotRepository(database_path).latest_run()
    payload = json.loads(intel_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert latest is not None
    assert payload["latest_run"]["id"] == latest.id


def test_daily_input_path_static_site_includes_imported_item(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    site_dir = tmp_path / "site"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        [
            "daily",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Manual Daily Catalyst" in (site_dir / "index.html").read_text(encoding="utf-8")


def test_daily_pipeline_contract_doc_matches_printed_output_labels(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    doc_text = Path("docs/DAILY_PIPELINE.md").read_text(encoding="utf-8")
    output_labels = _documented_bullets(doc_text, "Successful daily runs print these output labels:")

    result = runner.invoke(
        app,
        [
            "daily",
            "--sample-data",
            "--database-path",
            str(database_path),
            "--brief-path",
            str(brief_path),
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
        ],
    )

    assert result.exit_code == 0
    assert output_labels == {"Database", "Market brief", "Public intel", "Dashboard"}
    for label in output_labels:
        assert f"{label}:" in result.output
    assert "Daily run #1 complete." in result.output


def test_daily_rejects_sample_data_and_input_path(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        [
            "daily",
            "--sample-data",
            "--input-path",
            str(input_path),
            "--database-path",
            str(tmp_path / "snapshots.db"),
        ],
    )

    assert result.exit_code != 0
    assert "Use either --sample-data or --input-path, not both." in result.output


def test_daily_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path, input_path = _small_mover_daily_setup(tmp_path)

    result = runner.invoke(
        app,
        [
            "daily",
            "--input-path",
            str(input_path),
            "--database-path",
            str(database_path),
            "--big-delta",
            "20",
        ],
    )

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output


def test_daily_requires_sample_data_or_input_path(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["daily", "--database-path", str(tmp_path / "snapshots.db")],
    )

    assert result.exit_code != 0
    assert "Use --sample-data or --input-path for daily runs." in result.output


def test_schedule_helper_sample_data_prints_scheduler_guidance() -> None:
    result = runner.invoke(app, ["schedule-helper", "--sample-data", "--time", "09:30"])

    assert result.exit_code == 0
    assert "Daily command:" in result.output
    assert "wq daily --sample-data" in result.output
    assert "schtasks /Create" in result.output
    assert "/ST 09:30" in result.output
    assert "PowerShell one-liner alternative:" in result.output
    assert "does not create scheduled tasks" in result.output


def test_schedule_helper_input_path_validates_and_prints_daily_command(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        ["schedule-helper", "--input-path", str(input_path)],
    )

    assert result.exit_code == 0
    assert "wq daily --input-path" in result.output
    assert str(input_path) in result.output
    assert "schtasks /Create" in result.output


def test_schedule_helper_rejects_sample_data_and_input_path(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        ["schedule-helper", "--sample-data", "--input-path", str(input_path)],
    )

    assert result.exit_code != 0
    assert "Use either --sample-data or --input-path, not both." in result.output


def test_schedule_helper_requires_sample_data_or_input_path() -> None:
    result = runner.invoke(app, ["schedule-helper"])

    assert result.exit_code != 0
    assert "Use --sample-data or --input-path for schedule helper." in result.output


def test_schedule_helper_rejects_invalid_time() -> None:
    result = runner.invoke(app, ["schedule-helper", "--sample-data", "--time", "25:99"])

    assert result.exit_code != 0
    assert "Use --time in HH:MM 24-hour format." in result.output


def test_schedule_helper_rejects_invalid_import_file(tmp_path: Path) -> None:
    input_path = tmp_path / "items.json"
    item = _manual_item("Manual Daily Catalyst")
    item["signals"]["demand_momentum"] = 101  # type: ignore[index]
    input_path.write_text(json.dumps([item]), encoding="utf-8")

    result = runner.invoke(
        app,
        ["schedule-helper", "--input-path", str(input_path)],
    )

    assert result.exit_code != 0
    assert "demand_momentum" in result.output


def test_schedule_helper_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["schedule-helper", "--sample-data"])

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()
