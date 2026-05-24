from __future__ import annotations

import sqlite3

from wraeclast_quant.storage.models import AnalysisRunRecord


def analysis_run_from_row(row: sqlite3.Row) -> AnalysisRunRecord:
    return AnalysisRunRecord(
        id=int(row["id"]),
        created_at=str(row["created_at"]),
        source_mode=str(row["source_mode"]),
        item_count=int(row["item_count"]),
    )


__all__ = ["analysis_run_from_row"]
