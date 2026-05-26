from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping


DEFAULT_CLIENT_SECRET_ENV = "WQ_POE_CLIENT_SECRET"
DEFAULT_CLIENT_SECRET_FILE_ENV = "WQ_POE_CLIENT_SECRET_FILE"


@dataclass(frozen=True)
class CurrencyExchangeSecretSource:
    kind: str
    identifier: str


@dataclass(frozen=True, repr=False)
class CurrencyExchangeClientSecret:
    value: str
    source: CurrencyExchangeSecretSource

    def __repr__(self) -> str:
        source = (
            f"env:{self.source.identifier}"
            if self.source.kind == "env"
            else self.source.kind
        )
        return (
            "CurrencyExchangeClientSecret("
            f"source={source}, value=[REDACTED])"
        )


@dataclass(frozen=True)
class CurrencyExchangeClientSecretResult:
    ready: bool
    secret: CurrencyExchangeClientSecret | None
    source_description: str | None
    blockers: tuple[str, ...]


def secret_source_from_env(
    env: Mapping[str, str],
    *,
    client_secret_env: str,
    client_secret_file_env: str,
) -> CurrencyExchangeSecretSource | None:
    secret_file = env.get(client_secret_file_env, "").strip()
    if secret_file:
        return CurrencyExchangeSecretSource("file", secret_file)
    if env.get(client_secret_env, "").strip():
        return CurrencyExchangeSecretSource("env", client_secret_env)
    return None


def secret_source_blockers(
    secret_source: CurrencyExchangeSecretSource | None,
    workspace_root: Path,
) -> list[str]:
    if secret_source is None:
        return ["client secret source is required."]
    if secret_source.kind == "env":
        if not secret_source.identifier.strip():
            return ["client secret environment variable name is required."]
        return []
    if secret_source.kind == "file":
        if not secret_source.identifier.strip():
            return ["client secret file path is required."]
        if _path_is_inside_workspace(Path(secret_source.identifier), workspace_root):
            return ["client secret file must be outside the repository workspace."]
        return []
    return ["client secret source kind must be env or file."]


def load_currency_exchange_client_secret(
    secret_source: CurrencyExchangeSecretSource | None,
    *,
    env: Mapping[str, str],
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeClientSecretResult:
    blockers = secret_source_blockers(secret_source, Path(workspace_root))
    if blockers:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description=None,
            blockers=tuple(blockers),
        )
    assert secret_source is not None
    if secret_source.kind == "env":
        return _load_env_secret(secret_source, env)
    if secret_source.kind == "file":
        return _load_file_secret(secret_source)
    return CurrencyExchangeClientSecretResult(
        ready=False,
        secret=None,
        source_description=None,
        blockers=("client secret source kind must be env or file.",),
    )


def redact_currency_exchange_secret_text(text: str) -> str:
    redacted = re.sub(
        r"(?i)(access_token|refresh_token|client_secret)([\"'\s:=]+)([^\"'\s,&}]+)",
        r"\1\2[REDACTED]",
        text,
    )
    return re.sub(r"(?i)(Authorization:\s*Bearer\s+)[^\s]+", r"\1[REDACTED]", redacted)


def _load_env_secret(
    secret_source: CurrencyExchangeSecretSource,
    env: Mapping[str, str],
) -> CurrencyExchangeClientSecretResult:
    value = env.get(secret_source.identifier, "").strip()
    if not value:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description=f"env:{secret_source.identifier}",
            blockers=("client secret environment variable is empty or missing.",),
        )
    return CurrencyExchangeClientSecretResult(
        ready=True,
        secret=CurrencyExchangeClientSecret(value=value, source=secret_source),
        source_description=f"env:{secret_source.identifier}",
        blockers=(),
    )


def _load_file_secret(
    secret_source: CurrencyExchangeSecretSource,
) -> CurrencyExchangeClientSecretResult:
    path = Path(secret_source.identifier).expanduser()
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description="file",
            blockers=("client secret file could not be read.",),
        )
    if not value:
        return CurrencyExchangeClientSecretResult(
            ready=False,
            secret=None,
            source_description="file",
            blockers=("client secret file is empty.",),
        )
    return CurrencyExchangeClientSecretResult(
        ready=True,
        secret=CurrencyExchangeClientSecret(value=value, source=secret_source),
        source_description="file",
        blockers=(),
    )


def _path_is_inside_workspace(path: Path, workspace_root: Path) -> bool:
    resolved_path = path.expanduser().resolve(strict=False)
    resolved_root = workspace_root.expanduser().resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return False
    return True


__all__ = [
    "CurrencyExchangeClientSecret",
    "CurrencyExchangeClientSecretResult",
    "CurrencyExchangeSecretSource",
    "DEFAULT_CLIENT_SECRET_ENV",
    "DEFAULT_CLIENT_SECRET_FILE_ENV",
    "load_currency_exchange_client_secret",
    "redact_currency_exchange_secret_text",
    "secret_source_blockers",
    "secret_source_from_env",
]
