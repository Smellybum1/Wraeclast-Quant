from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping

from wraeclast_quant.config.fetch_policy_models import FetchPlan


DEFAULT_REALM = "poe2"
DEFAULT_SCOPE = "service:cxapi"
DEFAULT_REQUEST_BUDGET = 1
DEFAULT_CLIENT_SECRET_ENV = "WQ_POE_CLIENT_SECRET"
DEFAULT_CLIENT_SECRET_FILE_ENV = "WQ_POE_CLIENT_SECRET_FILE"
TOKEN_ENDPOINT_URL = "https://www.pathofexile.com/oauth/token"


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


@dataclass(frozen=True)
class CurrencyExchangeRuntimeSettings:
    client_id: str
    app_version: str
    contact: str
    secret_source: CurrencyExchangeSecretSource | None = None
    realm: str = DEFAULT_REALM
    scope: str = DEFAULT_SCOPE
    request_budget: int = DEFAULT_REQUEST_BUDGET


@dataclass(frozen=True)
class CurrencyExchangeRuntimePreflight:
    ready: bool
    user_agent: str | None
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class CurrencyExchangeRuntimePlan:
    resource_name: str
    endpoint_path: str
    realm: str
    scope: str
    token_grant_type: str
    cache_path: Path
    request_budget: int
    user_agent: str | None
    ready: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class CurrencyExchangeTokenResponsePreview:
    ready: bool
    token_type: str | None
    scope: str | None
    expires_in: int | None
    access_token_present: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class CurrencyExchangeTokenRequestPlan:
    token_url: str
    grant_type: str
    scope: str
    client_id: str
    user_agent: str | None
    form_fields: tuple[str, ...]
    ready: bool
    blockers: tuple[str, ...]


def currency_exchange_runtime_settings_from_env(
    env: Mapping[str, str],
    *,
    client_id: str = "",
    app_version: str = "",
    contact: str = "",
    realm: str = DEFAULT_REALM,
    request_budget: int = DEFAULT_REQUEST_BUDGET,
    client_secret_env: str = DEFAULT_CLIENT_SECRET_ENV,
    client_secret_file_env: str = DEFAULT_CLIENT_SECRET_FILE_ENV,
) -> CurrencyExchangeRuntimeSettings:
    return CurrencyExchangeRuntimeSettings(
        client_id=client_id,
        app_version=app_version,
        contact=contact,
        realm=realm,
        request_budget=request_budget,
        secret_source=_secret_source_from_env(
            env,
            client_secret_env=client_secret_env,
            client_secret_file_env=client_secret_file_env,
        ),
    )


def preview_currency_exchange_runtime_preflight(
    settings: CurrencyExchangeRuntimeSettings,
    *,
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeRuntimePreflight:
    blockers = _runtime_blockers(settings, Path(workspace_root))
    user_agent = None if blockers else currency_exchange_user_agent(settings)
    return CurrencyExchangeRuntimePreflight(
        ready=not blockers,
        user_agent=user_agent,
        blockers=tuple(blockers),
    )


def preview_currency_exchange_runtime_plan(
    settings: CurrencyExchangeRuntimeSettings,
    fetch_plan: FetchPlan,
    *,
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeRuntimePlan:
    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=workspace_root,
    )
    return CurrencyExchangeRuntimePlan(
        resource_name=fetch_plan.resource_name,
        endpoint_path=f"/currency-exchange/{settings.realm}",
        realm=settings.realm,
        scope=settings.scope,
        token_grant_type="client_credentials",
        cache_path=fetch_plan.cache_path,
        request_budget=settings.request_budget,
        user_agent=preflight.user_agent,
        ready=preflight.ready,
        blockers=preflight.blockers,
    )


def currency_exchange_user_agent(settings: CurrencyExchangeRuntimeSettings) -> str:
    return (
        f"OAuth {settings.client_id.strip()}/{settings.app_version.strip()} "
        f"(contact: {settings.contact.strip()}) WraeclastQuant"
    )


def preview_currency_exchange_token_response(
    payload: Mapping[str, object],
    *,
    expected_scope: str = DEFAULT_SCOPE,
) -> CurrencyExchangeTokenResponsePreview:
    token_type = _optional_str(payload.get("token_type"))
    scope = _optional_str(payload.get("scope"))
    expires_in = _optional_int(payload.get("expires_in"))
    access_token_present = bool(_optional_str(payload.get("access_token")))
    blockers = _token_response_blockers(
        access_token_present=access_token_present,
        token_type=token_type,
        scope=scope,
        expected_scope=expected_scope,
    )
    return CurrencyExchangeTokenResponsePreview(
        ready=not blockers,
        token_type=token_type,
        scope=scope,
        expires_in=expires_in,
        access_token_present=access_token_present,
        blockers=tuple(blockers),
    )


def preview_currency_exchange_token_request_plan(
    settings: CurrencyExchangeRuntimeSettings,
    *,
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeTokenRequestPlan:
    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=workspace_root,
    )
    return CurrencyExchangeTokenRequestPlan(
        token_url=TOKEN_ENDPOINT_URL,
        grant_type="client_credentials",
        scope=settings.scope,
        client_id=settings.client_id.strip(),
        user_agent=preflight.user_agent,
        form_fields=("client_id", "client_secret", "grant_type", "scope"),
        ready=preflight.ready,
        blockers=preflight.blockers,
    )


def load_currency_exchange_client_secret(
    secret_source: CurrencyExchangeSecretSource | None,
    *,
    env: Mapping[str, str],
    workspace_root: str | Path = Path.cwd(),
) -> CurrencyExchangeClientSecretResult:
    blockers = _secret_source_blockers(secret_source, Path(workspace_root))
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


def _secret_source_from_env(
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


def _runtime_blockers(
    settings: CurrencyExchangeRuntimeSettings,
    workspace_root: Path,
) -> list[str]:
    blockers: list[str] = []
    if not settings.client_id.strip():
        blockers.append("client_id is required.")
    if not settings.app_version.strip():
        blockers.append("app_version is required.")
    if not settings.contact.strip():
        blockers.append("user-agent contact is required.")
    if settings.realm != DEFAULT_REALM:
        blockers.append("Currency Exchange runtime currently supports only the poe2 realm.")
    if settings.scope != DEFAULT_SCOPE:
        blockers.append("Currency Exchange runtime requires the service:cxapi scope.")
    if settings.request_budget < 1:
        blockers.append("request_budget must be at least 1.")
    blockers.extend(_secret_source_blockers(settings.secret_source, workspace_root))
    return blockers


def _secret_source_blockers(
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


def _token_response_blockers(
    *,
    access_token_present: bool,
    token_type: str | None,
    scope: str | None,
    expected_scope: str,
) -> list[str]:
    blockers: list[str] = []
    if not access_token_present:
        blockers.append("access token is missing.")
    if (token_type or "").lower() != "bearer":
        blockers.append("token_type must be bearer.")
    if scope != expected_scope:
        blockers.append("token scope must be service:cxapi.")
    return blockers


def _optional_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _optional_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None


__all__ = [
    "CurrencyExchangeClientSecret",
    "CurrencyExchangeClientSecretResult",
    "CurrencyExchangeRuntimePreflight",
    "CurrencyExchangeRuntimePlan",
    "CurrencyExchangeRuntimeSettings",
    "CurrencyExchangeSecretSource",
    "CurrencyExchangeTokenRequestPlan",
    "CurrencyExchangeTokenResponsePreview",
    "currency_exchange_runtime_settings_from_env",
    "currency_exchange_user_agent",
    "load_currency_exchange_client_secret",
    "preview_currency_exchange_runtime_plan",
    "preview_currency_exchange_runtime_preflight",
    "preview_currency_exchange_token_request_plan",
    "preview_currency_exchange_token_response",
    "redact_currency_exchange_secret_text",
]
