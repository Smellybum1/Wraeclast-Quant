from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.models import ReviewCoverageRecord
from wraeclast_quant.storage.repository_support import read_connection


def review_coverage_for_run_query(database_path: Path, run_id: int) -> ReviewCoverageRecord:
    with read_connection(database_path) as connection:
        if connection is None:
            return ReviewCoverageRecord(
                run_id=run_id,
                total_recommendations=0,
                reviewed_recommendations=0,
                unreviewed_recommendations=0,
                reviewed_percent=0.0,
            )
        total = int(
            connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM scored_opportunities
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()["count"]
        )
        reviewed = int(
            connection.execute(
                """
                SELECT COUNT(DISTINCT lower(outcomes.item_name)) AS count
                FROM recommendation_outcomes AS outcomes
                JOIN scored_opportunities AS scored
                  ON scored.run_id = outcomes.run_id
                 AND lower(scored.item_name) = lower(outcomes.item_name)
                WHERE outcomes.run_id = ?
                """,
                (run_id,),
            ).fetchone()["count"]
        )
    unreviewed = max(total - reviewed, 0)
    reviewed_percent = (reviewed / total * 100.0) if total else 0.0
    return ReviewCoverageRecord(
        run_id=run_id,
        total_recommendations=total,
        reviewed_recommendations=reviewed,
        unreviewed_recommendations=unreviewed,
        reviewed_percent=reviewed_percent,
    )


def item_exists_for_run_query(database_path: Path, run_id: int, item_name: str) -> bool:
    normalized = item_name.strip().casefold()
    with read_connection(database_path) as connection:
        if connection is None:
            return False
        row = connection.execute(
            """
            SELECT 1
            FROM scored_opportunities
            WHERE run_id = ? AND lower(item_name) = lower(?)
            LIMIT 1
            """,
            (run_id, normalized),
        ).fetchone()
    return row is not None
