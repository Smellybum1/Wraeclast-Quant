import sqlite3
from pathlib import Path

DEFAULT_DATABASE_PATH = Path("data/wraeclast_quant.db")


def connect(database_path: Path = DEFAULT_DATABASE_PATH) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def connect_existing(database_path: Path = DEFAULT_DATABASE_PATH) -> sqlite3.Connection | None:
    if not database_path.exists():
        return None
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS analysis_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            source_mode TEXT NOT NULL,
            item_count INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scored_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
            item_name TEXT NOT NULL,
            opportunity_score REAL NOT NULL,
            action TEXT NOT NULL,
            inputs_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS report_artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recommendation_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
            item_name TEXT NOT NULL,
            outcome TEXT NOT NULL,
            notes TEXT NOT NULL,
            observed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS run_provenance (
            run_id INTEGER PRIMARY KEY REFERENCES analysis_runs(id) ON DELETE CASCADE,
            source_kind TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            connector_id TEXT NOT NULL,
            access_method TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    connection.commit()
