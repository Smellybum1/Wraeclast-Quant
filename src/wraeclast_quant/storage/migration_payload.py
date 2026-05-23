from __future__ import annotations

from wraeclast_quant.storage.migration_models import MigrationReadinessResult


def migration_readiness_payload(result: MigrationReadinessResult) -> dict[str, object]:
    return {
        "ready": result.ready,
        "schema_version": result.schema_version,
        "latest_database_run_id": result.latest_database_run_id,
        "latest_backup_run_id": result.latest_backup_run_id,
        "checks": [row.__dict__ for row in result.checks],
        "blockers": result.blockers,
    }
