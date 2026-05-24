from __future__ import annotations


def fresh_artifact_status(
    status_value: str,
    artifact_run_id: int | None,
    latest_database_run_id: int | None,
) -> str:
    if status_value != "ok":
        return status_value
    if artifact_run_id is None or latest_database_run_id is None:
        return status_value
    if artifact_run_id != latest_database_run_id:
        return "needs attention"
    return status_value


def fresh_artifact_details(
    artifact_run_id: int | None,
    latest_database_run_id: int | None,
    artifact_label: str,
    guidance: str,
) -> str:
    if artifact_run_id is None or latest_database_run_id is None:
        return ""
    if artifact_run_id == latest_database_run_id:
        return ""
    return (
        f"; stale; latest database run #{latest_database_run_id}, "
        f"{artifact_label} run #{artifact_run_id}; {guidance}"
    )
