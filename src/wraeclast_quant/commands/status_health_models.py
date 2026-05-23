from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from wraeclast_quant.commands.status_health_rows import rows_by_key, status_counts

STATUS_JSON_SCHEMA_VERSION = "1.5"


@dataclass(frozen=True)
class StatusHealthReport:
    rows: list[dict[str, str]]
    strict_failures: list[str]
    strict_failure_keys: list[str]

    def json_payload(self, *, strict: bool) -> dict[str, object]:
        return {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "product": "Wraeclast Quant",
            "schema_version": STATUS_JSON_SCHEMA_VERSION,
            "strict": strict,
            "ok": not self.strict_failures,
            "status_counts": status_counts(self.rows),
            "strict_failure_keys": self.strict_failure_keys,
            "strict_failures": self.strict_failures,
            "rows": self.rows,
            "rows_by_key": rows_by_key(self.rows),
        }
