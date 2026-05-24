from __future__ import annotations

import zipfile
from pathlib import Path


def write_bundle_archive(archive_path: Path, paths: list[Path]) -> None:
    if archive_path.exists():
        archive_path.unlink()
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, arcname=path.name)


__all__ = ["write_bundle_archive"]
