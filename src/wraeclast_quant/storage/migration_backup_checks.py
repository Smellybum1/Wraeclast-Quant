from __future__ import annotations

from wraeclast_quant.storage.migration_backup_freshness import add_backup_freshness_check
from wraeclast_quant.storage.migration_latest_backup_check import add_latest_backup_check


__all__ = ["add_backup_freshness_check", "add_latest_backup_check"]
