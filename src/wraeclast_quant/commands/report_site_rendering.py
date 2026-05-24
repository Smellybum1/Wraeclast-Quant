from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console(width=260)


def print_missing_public_intel_export() -> None:
    console.print("No public intel export found. Run wq export first.")


def print_public_intel_contract_errors(errors: list[str]) -> None:
    console.print("Public intel contract validation failed:")
    for error in errors:
        console.print(f"- {error}")


def print_static_site_written(output_path: Path) -> None:
    console.print(f"Wrote local dashboard preview to {output_path}")
