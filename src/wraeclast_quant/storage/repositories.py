from __future__ import annotations

import sqlite3
from contextlib import AbstractContextManager
from pathlib import Path

from wraeclast_quant.storage.db import connect, initialize_schema
from wraeclast_quant.storage.repository_artifacts import ArtifactProvenanceMixin
from wraeclast_quant.storage.repository_outcomes import ALLOWED_OUTCOMES, OutcomeReviewMixin
from wraeclast_quant.storage.repository_snapshots import SnapshotDataMixin
from wraeclast_quant.storage.repository_support import read_connection


class SnapshotRepository(SnapshotDataMixin, ArtifactProvenanceMixin, OutcomeReviewMixin):
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize_schema(self) -> None:
        with connect(self.database_path) as connection:
            initialize_schema(connection)

    def _read_connection(self) -> AbstractContextManager[sqlite3.Connection | None]:
        return read_connection(self.database_path)
