from __future__ import annotations

from pathlib import Path


def publish_check_args(
    database_path: Path,
    bundle_dir: Path,
    *,
    json_output: bool = False,
    strict: bool = False,
) -> list[str]:
    args = ["publish-check"]
    if json_output:
        args.append("--json")
    if strict:
        args.append("--strict")
    return [
        *args,
        "--database-path",
        str(database_path),
        "--bundle-dir",
        str(bundle_dir),
    ]


def publish_handoff_args(
    database_path: Path,
    bundle_dir: Path,
    output_path: Path,
    *,
    strict: bool = False,
) -> list[str]:
    args = ["publish-handoff"]
    if strict:
        args.append("--strict")
    return [
        *args,
        "--database-path",
        str(database_path),
        "--bundle-dir",
        str(bundle_dir),
        "--output-path",
        str(output_path),
    ]


def site_contract_args(
    database_path: Path,
    bundle_dir: Path,
    output_path: Path,
    *,
    strict: bool = False,
) -> list[str]:
    args = ["site-contract"]
    if strict:
        args.append("--strict")
    return [
        *args,
        "--database-path",
        str(database_path),
        "--bundle-dir",
        str(bundle_dir),
        "--output-path",
        str(output_path),
    ]


__all__ = [
    "publish_check_args",
    "publish_handoff_args",
    "site_contract_args",
]
