from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    preview_currency_exchange_token_response,
)


def test_currency_exchange_token_response_preview_keeps_token_value_out() -> None:
    preview = preview_currency_exchange_token_response(
        {
            "access_token": "secret-token-value",
            "token_type": "bearer",
            "scope": "service:cxapi",
            "expires_in": 3600,
        }
    )

    assert preview.ready is True
    assert preview.access_token_present is True
    assert preview.token_type == "bearer"
    assert preview.scope == "service:cxapi"
    assert preview.expires_in == 3600
    assert "secret-token-value" not in repr(preview)


def test_currency_exchange_token_response_preview_fails_closed() -> None:
    preview = preview_currency_exchange_token_response(
        {
            "access_token": "",
            "token_type": "mac",
            "scope": "account:profile",
        }
    )

    assert preview.ready is False
    assert preview.access_token_present is False
    assert preview.blockers == (
        "access token is missing.",
        "token_type must be bearer.",
        "token scope must be service:cxapi.",
    )
