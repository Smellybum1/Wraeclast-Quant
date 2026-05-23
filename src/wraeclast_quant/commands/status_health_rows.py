from __future__ import annotations

import re


def add_status_row(
    rows: list[dict[str, str]],
    check: str,
    status_value: str,
    details: str,
) -> None:
    rows.append(
        {
            "key": status_row_key(check),
            "check": check,
            "status": status_value,
            "details": details,
        }
    )


def status_row_key(check: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", check.strip().lower()).strip("_")


def strict_failure_keys(strict_failures: list[str]) -> list[str]:
    return [status_row_key(label) for label in strict_failures]


def status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = status_row_key(row["status"])
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def rows_by_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["key"]: row for row in rows}
