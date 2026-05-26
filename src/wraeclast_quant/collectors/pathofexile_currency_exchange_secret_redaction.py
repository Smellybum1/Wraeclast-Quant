from __future__ import annotations

import re


def redact_currency_exchange_secret_text(text: str) -> str:
    redacted = re.sub(
        r"(?i)(access_token|refresh_token|client_secret)([\"'\s:=]+)([^\"'\s,&}]+)",
        r"\1\2[REDACTED]",
        text,
    )
    return re.sub(r"(?i)(Authorization:\s*Bearer\s+)[^\s]+", r"\1[REDACTED]", redacted)


__all__ = ["redact_currency_exchange_secret_text"]
