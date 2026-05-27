from __future__ import annotations

from pathlib import Path


def status_json_args(
    tmp_path: Path,
    *,
    database_path: Path,
    resources_path: Path,
    intel_path: Path | None = None,
    site_dir: Path | None = None,
    bundle_dir: Path | None = None,
    stash_ninja_path: Path | None = None,
) -> list[str]:
    return status_args(
        tmp_path,
        database_path=database_path,
        resources_path=resources_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
        stash_ninja_path=stash_ninja_path,
        json_output=True,
    )


def status_args(
    tmp_path: Path,
    *,
    database_path: Path,
    resources_path: Path,
    brief_path: Path | None = None,
    intel_path: Path | None = None,
    site_dir: Path | None = None,
    bundle_dir: Path | None = None,
    stash_ninja_path: Path | None = None,
    backup_dir: Path | None = None,
    strict: bool = False,
    json_output: bool = False,
) -> list[str]:
    args = ["status"]
    if strict:
        args.append("--strict")
    if json_output:
        args.append("--json")
    return [
        *args,
        "--database-path",
        str(database_path),
        "--resources-path",
        str(resources_path),
        "--brief-path",
        str(brief_path or tmp_path / "missing.md"),
        "--intel-path",
        str(intel_path or tmp_path / "missing.json"),
        "--site-dir",
        str(site_dir or tmp_path / "missing_site"),
        "--bundle-dir",
        str(bundle_dir or tmp_path / "missing_bundle"),
        "--stash-ninja-path",
        str(stash_ninja_path or tmp_path / "missing_stash_ninja.json"),
        "--backup-dir",
        str(backup_dir or tmp_path / "missing_backups"),
    ]


__all__ = ["status_args", "status_json_args"]
