from __future__ import annotations

import re
from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.importers.manual import ManualImportError, load_manual_items
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
        _validate_schedule_time(run_time)
        _validate_schedule_input(sample_data, input_path)

        daily_command = _build_daily_command(
            sample_data=sample_data,
            input_path=input_path,
            database_path=database_path,
            resources_path=resources_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
        )
        cwd = Path.cwd()
        task_command = _build_schtasks_command(daily_command, cwd, run_time)
        powershell_command = _build_powershell_schedule_command(daily_command, cwd, run_time)

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


def _validate_schedule_input(sample_data: bool, input_path: Path | None) -> None:
    if sample_data and input_path is not None:
        raise typer.BadParameter("Use either --sample-data or --input-path, not both.")
    if not sample_data and input_path is None:
        raise typer.BadParameter("Use --sample-data or --input-path for schedule helper.")
    if input_path is not None:
        try:
            load_manual_items(input_path)
        except ManualImportError as error:
            raise typer.BadParameter(str(error)) from error


def _validate_schedule_time(run_time: str) -> None:
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", run_time):
        raise typer.BadParameter("Use --time in HH:MM 24-hour format.")


def _build_daily_command(
    sample_data: bool,
    input_path: Path | None,
    database_path: Path,
    resources_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
) -> str:
    parts = ["wq", "daily"]
    if sample_data:
        parts.append("--sample-data")
    elif input_path is not None:
        parts.extend(["--input-path", str(input_path)])
    parts.extend(
        [
            "--database-path",
            str(database_path),
            "--resources-path",
            str(resources_path),
            "--brief-path",
            str(brief_path),
            "--intel-path",
            str(intel_path),
            "--site-dir",
            str(site_dir),
        ]
    )
    return " ".join(_quote_cli_arg(part) for part in parts)


def _build_schtasks_command(daily_command: str, cwd: Path, run_time: str) -> str:
    task_run = f"powershell.exe {_powershell_daily_argument(daily_command, cwd)}"
    return (
        'schtasks /Create /SC DAILY /TN "Wraeclast Quant Daily" '
        f"/ST {run_time} /TR {_quote_cli_arg(task_run)}"
    )


def _build_powershell_schedule_command(daily_command: str, cwd: Path, run_time: str) -> str:
    task_run = _powershell_daily_argument(daily_command, cwd)
    action = (
        "$action = New-ScheduledTaskAction -Execute 'powershell.exe' "
        f"-Argument {_quote_powershell_string(task_run)}"
    )
    trigger = f"$trigger = New-ScheduledTaskTrigger -Daily -At {run_time}"
    register = (
        "Register-ScheduledTask -TaskName 'Wraeclast Quant Daily' "
        "-Action $action -Trigger $trigger "
        "-Description 'Runs Wraeclast Quant daily pipeline'"
    )
    return f"{action}; {trigger}; {register}"


def _powershell_daily_argument(daily_command: str, cwd: Path) -> str:
    cwd_value = str(cwd).replace("'", "''")
    return f"-NoProfile -Command \"Set-Location -LiteralPath '{cwd_value}'; {daily_command}\""


def _quote_cli_arg(value: str) -> str:
    if not value or any(character.isspace() for character in value) or '"' in value:
        return f'"{value.replace(chr(34), chr(92) + chr(34))}"'
    return value


def _quote_powershell_string(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _print_command_line(value: str) -> None:
    console.print(value, soft_wrap=True)
