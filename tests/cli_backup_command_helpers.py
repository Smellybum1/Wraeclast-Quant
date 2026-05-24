from __future__ import annotations

from pathlib import Path


def backup_db_args(database_path: Path, backup_dir: Path) -> list[str]:
    return [
        "backup-db",
        "--database-path",
        str(database_path),
        "--output-dir",
        str(backup_dir),
    ]


def migration_readiness_args(database_path: Path, backup_dir: Path) -> list[str]:
    return [
        "migration-readiness",
        "--database-path",
        str(database_path),
        "--backup-dir",
        str(backup_dir),
    ]


def migration_readiness_json_args(database_path: Path, backup_dir: Path) -> list[str]:
    return [
        "migration-readiness",
        "--json",
        "--database-path",
        str(database_path),
        "--backup-dir",
        str(backup_dir),
    ]


def verify_backup_args(backup_path: Path) -> list[str]:
    return ["verify-backup", "--backup-path", str(backup_path)]


def db_check_args(database_path: Path) -> list[str]:
    return ["db-check", "--database-path", str(database_path)]


def backups_args(backup_dir: Path) -> list[str]:
    return ["backups", "--backup-dir", str(backup_dir)]


def restore_helper_args(backup_path: Path, database_path: Path) -> list[str]:
    return [
        "restore-helper",
        "--backup-path",
        str(backup_path),
        "--database-path",
        str(database_path),
    ]


__all__ = [
    "backups_args",
    "backup_db_args",
    "db_check_args",
    "migration_readiness_args",
    "migration_readiness_json_args",
    "restore_helper_args",
    "verify_backup_args",
]
