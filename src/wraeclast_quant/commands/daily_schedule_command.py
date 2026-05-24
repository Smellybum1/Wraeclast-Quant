from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.commands.daily_schedule_builder import (
    build_daily_command,
    build_powershell_schedule_command,
    build_schtasks_command,
)
from wraeclast_quant.commands.daily_schedule_validation import (
    validate_schedule_input,
    validate_schedule_time,
)
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("schedule-helper")
    def schedule_helper(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        input_path: Path | None = typer.Option(None, "--input-path", help="Local JSON or CSV signal file."),
        run_time: str = typer.Option("09:00", "--time", help="Daily run time in HH:MM format."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        brief_path: Path = typer.Option(Path("data/processed/market_brief.md"), "--brief-path"),
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
    ) -> None:
        validate_schedule_time(run_time)
        validate_schedule_input(sample_data, input_path)

        daily_command = build_daily_command(
            sample_data=sample_data,
            input_path=input_path,
            database_path=database_path,
            resources_path=resources_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
        )
        cwd = Path.cwd()
        task_command = build_schtasks_command(daily_command, cwd, run_time)
        powershell_command = build_powershell_schedule_command(daily_command, cwd, run_time)

        console.print("Daily command:")
        _print_command_line(daily_command)
        console.print()
        console.print("Windows Task Scheduler example:")
        _print_command_line(task_command)
        console.print()
        console.print("PowerShell one-liner alternative:")
        _print_command_line(powershell_command)
        console.print()
        console.print("This helper only prints commands. It does not create scheduled tasks.")


def _print_command_line(value: str) -> None:
    console.print(value, soft_wrap=True)
