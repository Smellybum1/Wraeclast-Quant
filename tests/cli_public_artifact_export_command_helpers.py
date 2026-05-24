from __future__ import annotations

from pathlib import Path


def export_args(
    database_path: Path,
    output_path: Path,
    *,
    big_delta: int | None = None,
) -> list[str]:
    args = [
        "export",
        "--database-path",
        str(database_path),
        "--output-path",
        str(output_path),
    ]
    if big_delta is not None:
        args.extend(["--big-delta", str(big_delta)])
    return args


def validate_intel_args(intel_path: Path) -> list[str]:
    return ["validate-intel", "--intel-path", str(intel_path)]


def site_args(intel_path: Path, output_dir: Path) -> list[str]:
    return ["site", "--intel-path", str(intel_path), "--output-dir", str(output_dir)]


def site_bundle_args(intel_path: Path, site_dir: Path, output_dir: Path) -> list[str]:
    return [
        "site-bundle",
        "--intel-path",
        str(intel_path),
        "--site-dir",
        str(site_dir),
        "--output-dir",
        str(output_dir),
    ]


__all__ = [
    "export_args",
    "site_args",
    "site_bundle_args",
    "validate_intel_args",
]
