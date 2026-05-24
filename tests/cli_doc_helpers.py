from __future__ import annotations

PUBLIC_COMMANDS = [
    "schema",
    "status",
    "db-check",
    "snapshots",
    "compare",
    "alerts",
    "report",
    "export",
    "site",
    "validate-intel",
    "site-bundle",
    "publish-check",
    "publish-handoff",
    "site-contract",
    "daily",
    "schedule-helper",
    "backup-db",
    "verify-backup",
    "backups",
    "restore-helper",
    "migration-readiness",
    "run-provenance",
    "record-outcome",
    "outcomes",
    "review-queue",
    "review-coverage",
    "outcome-review",
    "outcome-report",
    "calibration",
    "calibration-report",
    "collect",
    "compliance",
    "preflight",
    "connector-candidates",
    "connector-draft",
    "connector-review-prep",
    "connector-review-evidence",
    "connector-check",
    "connector-review-status",
    "connector-approval-helper",
    "connector-review-report",
    "connector-approval-patch",
    "connector-fixture-run",
    "connector-dry-run",
    "connector-fixture-export",
    "connector-fixture-daily",
    "connector-plan",
    "analyze",
    "import",
    "validate-import",
    "inspect-import",
    "watchlist",
]


def top_level_help_args() -> list[str]:
    return ["--help"]


def command_help_args(command: str) -> list[str]:
    return [command, "--help"]


def documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }


def documented_status_row_keys(doc_text: str) -> list[str]:
    documented_keys_section = doc_text.split("Current row keys:\n\n", 1)[1].split(
        "\n\n", 1
    )[0]
    return [
        line.strip()[3:-1]
        for line in documented_keys_section.splitlines()
        if line.strip().startswith("- `")
    ]


__all__ = [
    "PUBLIC_COMMANDS",
    "command_help_args",
    "documented_bullets",
    "documented_status_row_keys",
    "top_level_help_args",
]
