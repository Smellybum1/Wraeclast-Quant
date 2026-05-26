from __future__ import annotations

from dataclasses import dataclass


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


__all__ = [
    "CurrencyExchangeClientSecret",
    "CurrencyExchangeClientSecretResult",
    "CurrencyExchangeSecretSource",
]
