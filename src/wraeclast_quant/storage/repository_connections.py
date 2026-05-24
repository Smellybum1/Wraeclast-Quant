from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from wraeclast_quant.storage.db import connect_existing, initialize_schema


@contextmanager
def read_connection(database_path: Path) -> Iterator[sqlite3.Connection | None]:
    connection = connect_existing(database_path)
    if connection is None:
        yield None
        return
    try:
        initialize_schema(connection)
        yield connection
    finally:
        connection.close()


__all__ = ["read_connection"]
