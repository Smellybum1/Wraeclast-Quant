from __future__ import annotations

from wraeclast_quant.storage.health import DatabaseHealthResult


def exists_label(exists: bool) -> str:
    return "yes" if exists else "no"


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


def database_health_status(health: DatabaseHealthResult | None) -> str:
    if health is None:
        return "none"
    return "ok" if health.ok else "needs attention"


def database_health_details(health: DatabaseHealthResult | None) -> str:
    if health is None:
        return "No database found."
    if health.ok:
        return (
            f"schema v{health.schema_version}; integrity {health.integrity_message}; "
            f"{health.analysis_run_count or 0} runs; "
            f"{health.scored_opportunity_count or 0} scored opportunities"
        )
    missing = ", ".join(health.missing_tables) if health.missing_tables else "none"
    return (
        f"schema v{health.schema_version}; integrity {health.integrity_message}; "
        f"missing tables: {missing}"
    )


def latest_run_empty_details(health: DatabaseHealthResult | None) -> str:
    if health is not None and not health.ok:
        return "Database health check did not pass."
    return "No snapshots found."
