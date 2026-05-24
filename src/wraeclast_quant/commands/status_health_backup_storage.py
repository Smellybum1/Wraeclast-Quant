from __future__ import annotations


def backup_status(backups) -> str:
    if not backups:
        return "no"
    return "ok" if backups[0].valid else "needs attention"


def backup_status_details(backups) -> str:
    if not backups:
        return "No local database backups found."
    latest = backups[0]
    if latest.valid:
        return (
            f"{latest.backup_path}; latest run #{latest.latest_run_id or 'none'}; "
            f"{latest.analysis_run_count or 0} runs; modified {latest.modified_at}"
        )
    return f"{latest.backup_path}; invalid: {latest.error}"


__all__ = ["backup_status", "backup_status_details"]
