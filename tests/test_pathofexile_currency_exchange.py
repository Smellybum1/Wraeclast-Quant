from pathlib import Path

import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangeMarket,
    CurrencyExchangeRuntimeSettings,
    CurrencyExchangeSecretSource,
    currency_exchange_market_item,
    currency_exchange_runtime_settings_from_env,
    currency_exchange_user_agent,
    load_currency_exchange_connector_fixture,
    load_currency_exchange_payload,
    preview_currency_exchange_opportunity_inputs,
    preview_currency_exchange_rolling_baseline_diagnostics,
    preview_currency_exchange_runtime_plan,
    preview_currency_exchange_runtime_preflight,
    preview_currency_exchange_token_request_plan,
    preview_currency_exchange_token_response,
    preview_currency_exchange_signal_fixture_from_baseline,
    preview_currency_exchange_signal_inputs,
    preview_currency_exchange_storage_plan,
    redact_currency_exchange_secret_text,
)
from wraeclast_quant.config.connector_fixtures import connector_fixture_signal_items
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.config.fetch_policy_models import FetchPlan


def _fetch_plan_for_runtime_test(cache_path: Path) -> FetchPlan:
    return FetchPlan(
        resource_name="Path of Exile Currency Exchange API",
        url="https://www.pathofexile.com/developer/docs/reference",
        access_method="api",
        cache_ttl_seconds=3600,
        rate_limit_per_minute=6,
        min_seconds_between_requests=10,
        cache_path=cache_path,
    )


def test_currency_exchange_fixture_loads_documented_payload_shape() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")

    assert payload.next_change_id == 1770000000
    assert [market.market_id for market in payload.markets] == [
        "chaos|divine",
        "exalted|divine",
    ]
    assert payload.markets[0].volume_traded["chaos"] == 98200


def test_currency_exchange_fixture_converts_to_connector_rows() -> None:
    fixture = load_currency_exchange_connector_fixture(
        "examples/pathofexile_currency_exchange_fixture.json"
    )

    assert fixture.source_name == "Path of Exile Currency Exchange API"
    assert fixture.generated_at == "2026-02-02T02:40:00+00:00"
    assert [item.name for item in fixture.items] == [
        "Chaos Orb / Divine Orb",
        "Exalted Orb / Divine Orb",
    ]
    assert fixture.items[0].category == "currency"
    assert fixture.items[0].signals is None
    assert "hourly aggregate chaos|divine" in fixture.items[0].price_text
    assert "volume chaos=98200, divine=812" in fixture.items[0].notes


def test_currency_exchange_preview_storage_plan_is_non_writing_and_secret_free() -> None:
    plan = preview_currency_exchange_storage_plan()

    assert plan.resource_id == "official_currency_exchange_api"
    assert str(plan.raw_cache_path).replace("\\", "/").endswith(
        "data/raw/cache/path-of-exile-currency-exchange-api-d9b59150fbb2.cache"
    )
    assert str(plan.baseline_observations_path).replace("\\", "/").endswith(
        "data/processed/currency_exchange/baseline_observations.preview.json"
    )
    assert plan.cache_ttl_seconds == 3600
    assert plan.stores_credentials is False
    assert plan.writes_enabled is False


def test_currency_exchange_runtime_preflight_builds_identifiable_user_agent(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is True
    assert preflight.blockers == ()
    assert preflight.user_agent == (
        "OAuth wraeclast-quant/0.1.0 (contact: user@example.test) WraeclastQuant"
    )
    assert currency_exchange_user_agent(settings) == preflight.user_agent


def test_currency_exchange_runtime_preflight_fails_closed_without_network_config(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="",
        app_version="",
        contact="",
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is False
    assert preflight.user_agent is None
    assert preflight.blockers == (
        "client_id is required.",
        "app_version is required.",
        "user-agent contact is required.",
        "client secret source is required.",
    )


def test_currency_exchange_runtime_preflight_rejects_repo_secret_file(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource(
            "file",
            str(tmp_path / "secret.txt"),
        ),
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is False
    assert preflight.blockers == (
        "client secret file must be outside the repository workspace.",
    )


def test_currency_exchange_runtime_settings_from_env_does_not_expose_secret_value(
    tmp_path: Path,
) -> None:
    settings = currency_exchange_runtime_settings_from_env(
        {"WQ_POE_CLIENT_SECRET": "super-secret-value"},
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is True
    assert settings.secret_source == CurrencyExchangeSecretSource(
        "env",
        "WQ_POE_CLIENT_SECRET",
    )
    assert "super-secret-value" not in repr(settings)
    assert "super-secret-value" not in str(preflight)


def test_currency_exchange_runtime_settings_from_env_prefers_secret_file_reference(
    tmp_path: Path,
) -> None:
    secret_file = tmp_path.parent / "poe-client-secret.txt"

    settings = currency_exchange_runtime_settings_from_env(
        {
            "WQ_POE_CLIENT_SECRET_FILE": str(secret_file),
            "WQ_POE_CLIENT_SECRET": "super-secret-value",
        },
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is True
    assert settings.secret_source == CurrencyExchangeSecretSource("file", str(secret_file))
    assert "super-secret-value" not in repr(settings)


def test_currency_exchange_runtime_preflight_keeps_scope_and_realm_strict(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
        realm="pc",
        scope="account:profile",
        request_budget=0,
    )

    preflight = preview_currency_exchange_runtime_preflight(
        settings,
        workspace_root=tmp_path,
    )

    assert preflight.ready is False
    assert preflight.blockers == (
        "Currency Exchange runtime currently supports only the poe2 realm.",
        "Currency Exchange runtime requires the service:cxapi scope.",
        "request_budget must be at least 1.",
    )


def test_currency_exchange_runtime_plan_is_read_only_and_uses_fetch_plan(
    tmp_path: Path,
) -> None:
    storage_plan = preview_currency_exchange_storage_plan(cache_root=tmp_path / "cache")
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
    )

    runtime_plan = preview_currency_exchange_runtime_plan(
        settings,
        _fetch_plan_for_runtime_test(storage_plan.raw_cache_path),
        workspace_root=tmp_path,
    )

    assert runtime_plan.ready is True
    assert runtime_plan.resource_name == "Path of Exile Currency Exchange API"
    assert runtime_plan.endpoint_path == "/currency-exchange/poe2"
    assert runtime_plan.scope == "service:cxapi"
    assert runtime_plan.token_grant_type == "client_credentials"
    assert runtime_plan.cache_path == storage_plan.raw_cache_path
    assert runtime_plan.request_budget == 1
    assert runtime_plan.user_agent == (
        "OAuth wraeclast-quant/0.1.0 (contact: user@example.test) WraeclastQuant"
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


def test_currency_exchange_token_request_plan_contains_no_secret_value(
    tmp_path: Path,
) -> None:
    settings = CurrencyExchangeRuntimeSettings(
        client_id="wraeclast-quant",
        app_version="0.1.0",
        contact="user@example.test",
        secret_source=CurrencyExchangeSecretSource("env", "WQ_POE_CLIENT_SECRET"),
    )

    plan = preview_currency_exchange_token_request_plan(
        settings,
        workspace_root=tmp_path,
    )

    assert plan.ready is True
    assert plan.token_url == "https://www.pathofexile.com/oauth/token"
    assert plan.grant_type == "client_credentials"
    assert plan.scope == "service:cxapi"
    assert plan.client_id == "wraeclast-quant"
    assert plan.form_fields == ("client_id", "client_secret", "grant_type", "scope")
    assert "WQ_POE_CLIENT_SECRET" not in repr(plan)
    assert "client_secret=" not in repr(plan)


def test_currency_exchange_token_request_plan_reuses_preflight_blockers(
    tmp_path: Path,
) -> None:
    plan = preview_currency_exchange_token_request_plan(
        CurrencyExchangeRuntimeSettings(client_id="", app_version="", contact=""),
        workspace_root=tmp_path,
    )

    assert plan.ready is False
    assert plan.user_agent is None
    assert plan.blockers == (
        "client_id is required.",
        "app_version is required.",
        "user-agent contact is required.",
        "client secret source is required.",
    )


def test_currency_exchange_market_id_requires_pipe_pair() -> None:
    market = CurrencyExchangeMarket(
        league="Dawn of the Hunt",
        market_id="chaos-divine",
        volume_traded={"chaos": 1},
        lowest_stock={"chaos": 1},
        highest_stock={"chaos": 1},
        lowest_ratio={"chaos": 1},
        highest_ratio={"chaos": 1},
    )

    with pytest.raises(ConnectorPolicyError, match="market_id"):
        currency_exchange_market_item(1770000000, market)


def test_currency_exchange_preview_signals_are_deterministic_and_unwired() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    fixture = load_currency_exchange_connector_fixture(
        "examples/pathofexile_currency_exchange_fixture.json"
    )

    signals = preview_currency_exchange_signal_inputs(payload)

    chaos_divine = signals["chaos|divine"]
    exalted_divine = signals["exalted|divine"]
    assert chaos_divine.demand_momentum == 100.0
    assert chaos_divine.liquidity_score == 92.53
    assert chaos_divine.manipulation_risk == 5.64
    assert exalted_divine.demand_momentum == 52.32
    assert exalted_divine.liquidity_score == 66.62
    assert exalted_divine.manipulation_risk == 21.48
    assert chaos_divine.build_dependency_score == 50.0
    assert chaos_divine.price_discount_score == 50.0
    assert chaos_divine.historical_spike_score == 50.0
    assert chaos_divine.patch_relevance_score == 50.0
    assert chaos_divine.stale_data_penalty == 20.0
    assert all(item.signals is None for item in fixture.items)


def test_currency_exchange_preview_signals_handle_empty_payload() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    empty_payload = payload.model_copy(update={"markets": []})

    assert preview_currency_exchange_signal_inputs(empty_payload) == {}


def test_currency_exchange_preview_signals_surface_low_liquidity_spread_risk() -> None:
    payload = load_currency_exchange_payload(
        "examples/pathofexile_currency_exchange_low_liquidity_fixture.json"
    )

    signals = preview_currency_exchange_signal_inputs(payload)

    thin = signals["chaos|divine"]
    liquid = signals["exalted|divine"]
    assert thin.demand_momentum == 1.72
    assert thin.liquidity_score == 2.15
    assert thin.manipulation_risk == 70.38
    assert liquid.demand_momentum == 100.0
    assert liquid.liquidity_score == 100.0
    assert liquid.manipulation_risk == 1.74


def test_currency_exchange_preview_signals_show_relative_payload_sensitivity() -> None:
    narrow = preview_currency_exchange_signal_inputs(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    )
    broad = preview_currency_exchange_signal_inputs(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_broad_fixture.json")
    )

    assert narrow["chaos|divine"].demand_momentum == 100.0
    assert broad["chaos|divine"].demand_momentum == 42.31
    assert narrow["chaos|divine"].liquidity_score == 92.53
    assert broad["chaos|divine"].liquidity_score == 33.75
    assert narrow["exalted|divine"].liquidity_score == 66.62
    assert broad["exalted|divine"].liquidity_score == 21.0


def test_currency_exchange_rolling_baseline_is_stable_across_payload_composition() -> None:
    history = [load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")]
    narrow = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json"),
        history,
    )
    broad = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_broad_fixture.json"),
        history,
    )

    assert narrow["chaos|divine"].demand_index == broad["chaos|divine"].demand_index
    assert narrow["chaos|divine"].liquidity_index == broad["chaos|divine"].liquidity_index
    assert narrow["chaos|divine"].spread_index == broad["chaos|divine"].spread_index
    assert broad["chaos|divine"].freshness_lag_seconds == 7200
    assert broad["chaos|divine"].freshness_status == "fresh"
    assert broad["chaos|divine"].stale_data_penalty == 0.0
    assert broad["chaos|regal"].confidence == "blocked"
    assert broad["chaos|regal"].blockers == ("insufficient local baseline history",)


def test_currency_exchange_rolling_baseline_surfaces_thin_market_diagnostics() -> None:
    history = [load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")]
    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_low_liquidity_fixture.json"),
        history,
    )

    thin = diagnostics["chaos|divine"]
    liquid = diagnostics["exalted|divine"]
    assert thin.observations == 1
    assert thin.demand_index == 0.46
    assert thin.liquidity_index == 0.98
    assert thin.spread_index == 100.0
    assert thin.confidence == "preview"
    assert liquid.demand_index == 50.87
    assert liquid.liquidity_index == 51.44
    assert liquid.spread_index == 60.08


def test_currency_exchange_rolling_baseline_flags_stale_cadence() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    stale_current = baseline.model_copy(update={"next_change_id": baseline.next_change_id + 10800})

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        stale_current,
        [baseline],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.freshness_lag_seconds == 10800
    assert chaos_divine.freshness_status == "stale"
    assert chaos_divine.stale_data_penalty == 20.0
    assert chaos_divine.confidence == "warning"
    assert chaos_divine.blockers == ("current payload is stale versus local baseline cadence",)


def test_currency_exchange_rolling_baseline_flags_out_of_order_capture() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    older_current = baseline.model_copy(update={"next_change_id": baseline.next_change_id - 3600})

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        older_current,
        [baseline],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.freshness_lag_seconds == -3600
    assert chaos_divine.freshness_status == "out-of-order"
    assert chaos_divine.stale_data_penalty == 40.0
    assert chaos_divine.confidence == "warning"
    assert chaos_divine.blockers == ("current payload predates local baseline history",)


def test_currency_exchange_rolling_baseline_requires_local_history() -> None:
    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json"),
        [],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.observations == 0
    assert chaos_divine.demand_index == 0.0
    assert chaos_divine.confidence == "blocked"
    assert chaos_divine.blockers == ("insufficient local baseline history",)


def test_currency_exchange_rolling_baseline_keeps_leagues_separate() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    other_league_current = baseline.model_copy(
        update={
            "markets": [
                market.model_copy(update={"league": "Different League"})
                for market in baseline.markets
            ]
        }
    )

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        other_league_current,
        [baseline],
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.league == "Different League"
    assert chaos_divine.observations == 0
    assert chaos_divine.confidence == "blocked"
    assert chaos_divine.blockers == ("insufficient local baseline history",)


def test_currency_exchange_rolling_baseline_honors_minimum_history() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")

    diagnostics = preview_currency_exchange_rolling_baseline_diagnostics(
        baseline,
        [baseline],
        min_observations=2,
    )

    chaos_divine = diagnostics["chaos|divine"]
    assert chaos_divine.observations == 1
    assert chaos_divine.demand_index == 0.0
    assert chaos_divine.confidence == "blocked"
    assert chaos_divine.blockers == ("insufficient local baseline history",)


def test_currency_exchange_preview_signal_fixture_exports_only_unblocked_baselines() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    preview = preview_currency_exchange_signal_fixture_from_baseline(baseline, [baseline])

    assert preview.source_name == "Path of Exile Currency Exchange API Preview"
    assert all(item.signals is not None for item in preview.items)
    exported = connector_fixture_signal_items(preview.items)
    assert exported[0]["name"] == "Chaos Orb / Divine Orb"
    assert exported[0]["signals"]["demand_momentum"] == 50.0
    assert exported[0]["signals"]["liquidity_score"] == 50.0
    assert exported[0]["signals"]["manipulation_risk"] == 50.0


def test_currency_exchange_preview_signal_fixture_blocks_missing_history_signals() -> None:
    payload = load_currency_exchange_payload("examples/pathofexile_currency_exchange_broad_fixture.json")
    preview = preview_currency_exchange_signal_fixture_from_baseline(payload, [])

    assert all(item.signals is None for item in preview.items)
    assert {item.confidence for item in preview.items} == {"blocked"}
    with pytest.raises(ConnectorPolicyError, match="requires normalized signals"):
        connector_fixture_signal_items(preview.items)


def test_currency_exchange_opportunity_inputs_skip_warning_diagnostics() -> None:
    baseline = load_currency_exchange_payload("examples/pathofexile_currency_exchange_fixture.json")
    stale_current = baseline.model_copy(update={"next_change_id": baseline.next_change_id + 10800})
    diagnostic = preview_currency_exchange_rolling_baseline_diagnostics(
        stale_current,
        [baseline],
    )["chaos|divine"]

    assert diagnostic.confidence == "warning"
    assert preview_currency_exchange_opportunity_inputs(diagnostic) is None


def test_currency_exchange_invalid_fixture_fails_clearly(tmp_path: Path) -> None:
    fixture_path = tmp_path / "currency_exchange.json"
    fixture_path.write_text('{"markets": []}', encoding="utf-8")

    with pytest.raises(ConnectorPolicyError, match="Invalid Currency Exchange fixture"):
        load_currency_exchange_payload(fixture_path)
