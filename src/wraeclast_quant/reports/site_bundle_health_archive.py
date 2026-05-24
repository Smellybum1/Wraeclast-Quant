from __future__ import annotations

import zipfile
from pathlib import Path

from wraeclast_quant.reports.site_bundle_models import REQUIRED_ARCHIVE_MEMBERS


def archive_member_errors(archive_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = set(archive.namelist())
    except zipfile.BadZipFile:
        members = set()
        errors.append("bundle archive is not a valid zip file")

    missing_members = sorted(REQUIRED_ARCHIVE_MEMBERS - members)
    if missing_members:
        errors.append("archive is missing: " + ", ".join(missing_members))
    return errors


__all__ = ["archive_member_errors"]
