import sqlite3
from pathlib import Path

import pytest

from wraeclast_quant.storage.health import DatabaseHealthError, check_database_health


def test_check_database_health_reports_missing_required_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "not_wq.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")

    result = check_database_health(database_path)

    assert result is not None
    assert result.ok is False
    assert result.schema_version == "2"
    assert "scored_opportunities" in result.required_tables
    assert result.integrity_ok is True
    assert result.schema_ok is False
    assert "analysis_runs" in result.missing_tables
    assert result.analysis_run_count is None
    assert result.latest_run_id is None


def test_check_database_health_rejects_directory_path(tmp_path: Path) -> None:
    with pytest.raises(DatabaseHealthError, match="not a file"):
        check_database_health(tmp_path)
