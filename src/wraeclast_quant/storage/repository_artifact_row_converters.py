from __future__ import annotations

import sqlite3

from wraeclast_quant.storage.models import ReportArtifactRecord


def report_artifact_from_row(row: sqlite3.Row) -> ReportArtifactRecord:
    return ReportArtifactRecord(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        path=str(row["path"]),
        created_at=str(row["created_at"]),
    )


__all__ = ["report_artifact_from_row"]
