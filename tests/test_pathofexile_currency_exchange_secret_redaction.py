from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    redact_currency_exchange_secret_text,
)


def test_currency_exchange_secret_redaction_handles_tokens_and_headers() -> None:
    text = (
        'client_secret="super-secret" access_token: bearer-token '
        "refresh_token=refresh-secret Authorization: Bearer header-secret"
    )

    redacted = redact_currency_exchange_secret_text(text)

    assert "super-secret" not in redacted
    assert "bearer-token" not in redacted
    assert "refresh-secret" not in redacted
    assert "header-secret" not in redacted
    assert redacted.count("[REDACTED]") == 4
