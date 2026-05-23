from __future__ import annotations

import json

from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord
from wraeclast_quant.storage.repository_support import (
    analysis_run_from_row,
    read_connection,
    stored_opportunity_from_row,
    utc_now,
)


class SnapshotDataMixin:
    def create_analysis_run(
        self,
        source_mode: str,
        item_count: int,
        created_at: str | None = None,
    ) -> AnalysisRunRecord:
        timestamp = created_at or utc_now()
        with connect(self.database_path) as connection:
            initialize_schema(connection)
            cursor = connection.execute(
                """
                INSERT INTO analysis_runs (created_at, source_mode, item_count)
                VALUES (?, ?, ?)
                """,
                (timestamp, source_mode, item_count),
            )
            connection.commit()
            return AnalysisRunRecord(
                id=int(cursor.lastrowid),
                created_at=timestamp,
                source_mode=source_mode,
                item_count=item_count,
            )

    def save_scored_opportunities(
        self,
        run_id: int,
        opportunities: list[ScoredOpportunity],
    ) -> None:
        rows = [
            (
                run_id,
                opportunity.item_name,
                opportunity.opportunity_score,
                opportunity.action,
                json.dumps(opportunity.inputs.model_dump(), sort_keys=True),
            )
            for opportunity in opportunities
        ]
        with connect(self.database_path) as connection:
            initialize_schema(connection)
            connection.executemany(
                """
                INSERT INTO scored_opportunities (
                    run_id,
                    item_name,
                    opportunity_score,
                    action,
                    inputs_json
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            connection.commit()

    def latest_run(self) -> AnalysisRunRecord | None:
        with read_connection(self.database_path) as connection:
            if connection is None:
                return None
            row = connection.execute(
                """
                SELECT id, created_at, source_mode, item_count
                FROM analysis_runs
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
        return analysis_run_from_row(row) if row is not None else None

    def previous_run_before(self, run_id: int) -> AnalysisRunRecord | None:
        with read_connection(self.database_path) as connection:
            if connection is None:
                return None
            row = connection.execute(
                """
                SELECT id, created_at, source_mode, item_count
                FROM analysis_runs
                WHERE id < ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
        return analysis_run_from_row(row) if row is not None else None

    def analysis_run(self, run_id: int) -> AnalysisRunRecord | None:
        with read_connection(self.database_path) as connection:
            if connection is None:
                return None
            row = connection.execute(
                """
                SELECT id, created_at, source_mode, item_count
                FROM analysis_runs
                WHERE id = ?
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
        return analysis_run_from_row(row) if row is not None else None

    def list_recent_runs(self, limit: int = 5) -> list[AnalysisRunRecord]:
        with read_connection(self.database_path) as connection:
            if connection is None:
                return []
            rows = connection.execute(
                """
                SELECT id, created_at, source_mode, item_count
                FROM analysis_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [analysis_run_from_row(row) for row in rows]

    def latest_scored_opportunities(self, limit: int = 5) -> list[StoredOpportunityRecord]:
        latest = self.latest_run()
        if latest is None:
            return []
        return self.scored_opportunities_for_run(latest.id, limit=limit)

    def scored_opportunities_for_run(
        self,
        run_id: int,
        limit: int | None = None,
    ) -> list[StoredOpportunityRecord]:
        query = """
            SELECT id, run_id, item_name, opportunity_score, action, inputs_json
            FROM scored_opportunities
            WHERE run_id = ?
            ORDER BY opportunity_score DESC, item_name ASC
        """
        params: tuple[int, ...] | tuple[int, int]
        if limit is None:
            params = (run_id,)
        else:
            query = f"{query} LIMIT ?"
            params = (run_id, limit)
        with read_connection(self.database_path) as connection:
            if connection is None:
                return []
            rows = connection.execute(query, params).fetchall()
        return [stored_opportunity_from_row(row) for row in rows]
