from __future__ import annotations

from pathlib import Path


def run_provenance_args(database_path: Path, *, run_id: int | None = None) -> list[str]:
    args = ["run-provenance", "--database-path", str(database_path)]
    if run_id is not None:
        args.extend(["--run-id", str(run_id)])
    return args


__all__ = ["run_provenance_args"]
