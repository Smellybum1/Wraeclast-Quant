from __future__ import annotations

from pathlib import Path


def collect_dry_run_args() -> list[str]:
    return ["collect", "--dry-run"]


def compliance_args() -> list[str]:
    return ["compliance"]


def preflight_args(resources_path: Path) -> list[str]:
    return ["preflight", "--resources-path", str(resources_path)]


def schema_args() -> list[str]:
    return ["schema"]


def write_preflight_resources(tmp_path: Path) -> Path:
    resources_path = tmp_path / "RESOURCES.md"
    resources_path.write_text(
        """
## Official Sources
- name: Approved API
  type: official
  url: https://example.test/api
  allowed_use: api
- name: Missing URL API
  type: official
  allowed_use: api
- name: Official Discord
  type: discord
  url: https://discord.com/channels/example
  allowed_use: api
- name: Manual Source
  allowed_use: manual-review
""",
        encoding="utf-8",
    )
    return resources_path


__all__ = [
    "collect_dry_run_args",
    "compliance_args",
    "preflight_args",
    "schema_args",
    "write_preflight_resources",
]
