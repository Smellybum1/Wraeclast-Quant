from __future__ import annotations

from pathlib import Path


def connector_fixture_run_args(
    *,
    review_path: str | Path = "examples/connector_review_api_example.json",
    fixture_path: str | Path = "examples/connector_fixture_api_example.json",
) -> list[str]:
    return [
        "connector-fixture-run",
        "--review-path",
        str(review_path),
        "--fixture-path",
        str(fixture_path),
    ]


def connector_dry_run_args(
    *,
    review_path: str | Path = "examples/connector_review_api_example.json",
    fixture_path: str | Path = "examples/connector_fixture_api_example.json",
    resources_path: str | Path | None = None,
) -> list[str]:
    args = [
        "connector-dry-run",
        "--review-path",
        str(review_path),
        "--fixture-path",
        str(fixture_path),
    ]
    if resources_path is not None:
        args.extend(["--resources-path", str(resources_path)])
    return args


def connector_fixture_export_args(
    *,
    output_path: Path,
    review_path: str | Path = "examples/connector_review_api_example.json",
    fixture_path: str | Path = "examples/connector_fixture_signals_example.json",
) -> list[str]:
    return [
        "connector-fixture-export",
        "--review-path",
        str(review_path),
        "--fixture-path",
        str(fixture_path),
        "--output-path",
        str(output_path),
    ]


def connector_fixture_daily_args(
    *,
    review_path: str | Path = "examples/connector_review_api_example.json",
    fixture_path: str | Path = "examples/connector_fixture_signals_example.json",
    database_path: Path | None = None,
    brief_path: Path | None = None,
    intel_path: Path | None = None,
    site_dir: Path | None = None,
    big_delta: str | int | None = None,
) -> list[str]:
    args = [
        "connector-fixture-daily",
        "--review-path",
        str(review_path),
        "--fixture-path",
        str(fixture_path),
    ]
    if database_path is not None:
        args.extend(["--database-path", str(database_path)])
        brief_path = brief_path or database_path.parent / "market_brief.md"
        intel_path = intel_path or database_path.parent / "public_intel.json"
        site_dir = site_dir or database_path.parent / "site"
    if brief_path is not None:
        args.extend(["--brief-path", str(brief_path)])
    if intel_path is not None:
        args.extend(["--intel-path", str(intel_path)])
    if site_dir is not None:
        args.extend(["--site-dir", str(site_dir)])
    if big_delta is not None:
        args.extend(["--big-delta", str(big_delta)])
    return args


__all__ = [
    "connector_dry_run_args",
    "connector_fixture_daily_args",
    "connector_fixture_export_args",
    "connector_fixture_run_args",
]
