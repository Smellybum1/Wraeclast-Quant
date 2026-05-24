from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.daily_schedule_quoting import (
    powershell_daily_argument,
    quote_cli_arg,
    quote_powershell_string,
)


def build_daily_command(
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
    return " ".join(quote_cli_arg(part) for part in parts)


def build_schtasks_command(daily_command: str, cwd: Path, run_time: str) -> str:
    task_run = f"powershell.exe {powershell_daily_argument(daily_command, cwd)}"
    return (
        'schtasks /Create /SC DAILY /TN "Wraeclast Quant Daily" '
        f"/ST {run_time} /TR {quote_cli_arg(task_run)}"
    )


def build_powershell_schedule_command(daily_command: str, cwd: Path, run_time: str) -> str:
    task_run = powershell_daily_argument(daily_command, cwd)
    action = (
        "$action = New-ScheduledTaskAction -Execute 'powershell.exe' "
        f"-Argument {quote_powershell_string(task_run)}"
    )
    trigger = f"$trigger = New-ScheduledTaskTrigger -Daily -At {run_time}"
    register = (
        "Register-ScheduledTask -TaskName 'Wraeclast Quant Daily' "
        "-Action $action -Trigger $trigger "
        "-Description 'Runs Wraeclast Quant daily pipeline'"
    )
    return f"{action}; {trigger}; {register}"


__all__ = [
    "build_daily_command",
    "build_powershell_schedule_command",
    "build_schtasks_command",
    "powershell_daily_argument",
    "quote_cli_arg",
    "quote_powershell_string",
]
