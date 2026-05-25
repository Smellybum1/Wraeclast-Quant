from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource


def test_fetch_plan_is_created_for_valid_review() -> None:
    result = build_fetch_plan(_review(), [_eligible_resource()])

    assert result.plan is not None
    assert result.check.ready is True
    assert result.plan.resource_name == "Approved API"
    assert result.plan.url == "https://example.test/api"
    assert result.plan.access_method == "api"
    assert result.plan.dry_run_required is True
    assert result.plan.public_export_derived_only is True


def test_fetch_plan_minimum_request_interval_uses_rate_limit() -> None:
    result = build_fetch_plan(_review(rate_limit_per_minute=30), [_eligible_resource()])

    assert result.plan is not None
    assert result.plan.min_seconds_between_requests == 2.0


def test_fetch_plan_cache_path_is_deterministic_under_cache_root() -> None:
    first = build_fetch_plan(_review(), [_eligible_resource()])
    second = build_fetch_plan(_review(), [_eligible_resource()])

    assert first.plan is not None
    assert second.plan is not None
    assert first.plan.cache_path == second.plan.cache_path
    assert str(first.plan.cache_path).replace("\\", "/").startswith("data/raw/cache/")


def test_fetch_plan_is_not_created_for_missing_url() -> None:
    result = build_fetch_plan(
        _review(),
        [Resource(name="Approved API", type="official", allowed_use="api")],
    )

    assert result.plan is None
    assert result.check.ready is False
    assert any("URL" in blocker or "missing a URL" in blocker for blocker in result.check.blockers)


def test_fetch_plan_is_not_created_for_failed_connector_review() -> None:
    result = build_fetch_plan(
        _review(source_terms_reviewed=False),
        [_eligible_resource()],
    )

    assert result.plan is None
    assert result.check.ready is False
    assert "Source terms must be reviewed." in result.check.blockers


def test_fetch_plan_cache_path_hides_query_string_and_unsafe_characters() -> None:
    resource = Resource(
        name="Approved API: Query/Unsafe?",
        type="official",
        url="https://example.test/api?token=secret&league=Dawn",
        allowed_use="api",
    )
    result = build_fetch_plan(_review(resource_name=resource.name), [resource])

    assert result.plan is not None
    cache_name = result.plan.cache_path.name
    assert "?" not in cache_name
    assert "&" not in cache_name
    assert "secret" not in cache_name
    assert ":" not in cache_name
    assert "/" not in cache_name
