from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.models import ReportArtifactRecord
from wraeclast_quant.storage.repository_support import (
    read_connection,
    report_artifact_from_row,
    utc_now,
)


def insert_report_artifact(
    database_path: Path,
    run_id: int,
    path: Path,
    created_at: str | None = None,
) -> ReportArtifactRecord:
    timestamp = created_at or utc_now()
    path_value = str(path)
    with connect(database_path) as connection:
        initialize_schema(connection)
        cursor = connection.execute(
            """
            INSERT INTO report_artifacts (run_id, path, created_at)
            VALUES (?, ?, ?)
            """,
            (run_id, path_value, timestamp),
        )
        connection.commit()
        return ReportArtifactRecord(
            id=int(cursor.lastrowid),
            run_id=run_id,
            path=path_value,
            created_at=timestamp,
        )


def select_report_artifacts_for_run(
    database_path: Path,
    run_id: int,
) -> list[ReportArtifactRecord]:
    with read_connection(database_path) as connection:
        if connection is None:
            return []
        rows = connection.execute(
            """
            SELECT id, run_id, path, created_at
            FROM report_artifacts
            WHERE run_id = ?
            ORDER BY id DESC
            """,
            (run_id,),
        ).fetchall()
    return [report_artifact_from_row(row) for row in rows]
