from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource

from connector_policy_helpers import connector_review as _review


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
