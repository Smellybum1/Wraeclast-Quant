from wraeclast_quant.config.preflight import assess_preflight_resource, summarize_preflight
from wraeclast_quant.config.resources_loader import Resource


def test_preflight_summary_counts() -> None:
    assessments = [
        assess_preflight_resource(
            Resource(
                name="Approved API",
                allowed_use="api",
                url="https://example.test/api",
            )
        ),
        assess_preflight_resource(Resource(name="Manual Source", allowed_use="manual-review")),
        assess_preflight_resource(Resource(name="Missing URL API", allowed_use="api")),
        assess_preflight_resource(Resource(name="Blocked Source", allowed_use="blocked")),
        assess_preflight_resource(
            Resource(name="Discord", type="discord", allowed_use="api", url="https://discord.com")
        ),
    ]

    summary = summarize_preflight(assessments)

    assert summary.total == 5
    assert summary.eligible == 1
    assert summary.manual_review == 1
    assert summary.needs_review == 1
    assert summary.blocked == 1
    assert summary.discord_gated == 1
    assert summary.placeholder_only == 5
