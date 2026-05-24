from __future__ import annotations

import zipfile
from pathlib import Path


def archive_members(archive_path: Path) -> list[str]:
    if not archive_path.exists():
        return []
    try:
        with zipfile.ZipFile(archive_path) as archive:
            return sorted(archive.namelist())
    except zipfile.BadZipFile:
        return []


__all__ = ["archive_members"]
