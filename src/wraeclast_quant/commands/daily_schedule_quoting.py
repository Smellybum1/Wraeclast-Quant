from __future__ import annotations

from pathlib import Path


def powershell_daily_argument(daily_command: str, cwd: Path) -> str:
    cwd_value = str(cwd).replace("'", "''")
    return f"-NoProfile -Command \"Set-Location -LiteralPath '{cwd_value}'; {daily_command}\""


def quote_cli_arg(value: str) -> str:
    if not value or any(character.isspace() for character in value) or '"' in value:
        return f'"{value.replace(chr(34), chr(92) + chr(34))}"'
    return value


def quote_powershell_string(value: str) -> str:
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


__all__ = ["powershell_daily_argument", "quote_cli_arg", "quote_powershell_string"]
