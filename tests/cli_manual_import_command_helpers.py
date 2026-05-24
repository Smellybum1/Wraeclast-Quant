from __future__ import annotations

from pathlib import Path


def import_args(input_path: Path, database_path: Path) -> list[str]:
    return ["import", "--input-path", str(input_path), "--database-path", str(database_path)]


def validate_import_args(input_path: Path) -> list[str]:
    return ["validate-import", "--input-path", str(input_path)]


def inspect_import_args(input_path: Path) -> list[str]:
    return ["inspect-import", "--input-path", str(input_path)]


__all__ = [
    "import_args",
    "inspect_import_args",
    "validate_import_args",
]
