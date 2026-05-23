from wraeclast_quant.config.compliance import assess_resource, assess_resources
from wraeclast_quant.config.preflight import assess_preflight_resource, summarize_preflight
from wraeclast_quant.config.resources_loader import Resource, parse_resources_markdown


def test_api_resource_is_automation_eligible() -> None:
    assessment = assess_resource(
        Resource(name="Approved API", type="official_docs", allowed_use="api")
    )

    assert assessment.status == "approved-api"
    assert assessment.automation_eligible is True


def test_rss_resource_is_automation_eligible() -> None:
    assessment = assess_resource(Resource(name="Approved RSS", type="youtube", allowed_use="rss"))

    assert assessment.status == "approved-rss"
    assert assessment.automation_eligible is True


def test_download_resource_is_automation_eligible() -> None:
    assessment = assess_resource(
        Resource(name="Approved Download", type="official", allowed_use="download")
    )

    assert assessment.status == "approved-download"
    assert assessment.automation_eligible is True


def test_manual_resource_is_not_automation_eligible() -> None:
    assessment = assess_resource(Resource(name="Manual Source", allowed_use="manual-review"))

    assert assessment.status == "manual-review"
    assert assessment.automation_eligible is False


def test_conditional_allowed_use_needs_review() -> None:
    assessment = assess_resource(
        Resource(name="Conditional Source", allowed_use="manual-or-api-if-available")
    )

    assert assessment.status == "needs-review"
    assert assessment.automation_eligible is False


def test_blocked_resource_is_not_automation_eligible() -> None:
    assessment = assess_resource(Resource(name="Blocked Source", allowed_use="no-automation"))

    assert assessment.status == "blocked"
    assert assessment.automation_eligible is False


def test_discord_is_manual_review_even_if_marked_api() -> None:
    assessment = assess_resource(Resource(name="Discord", type="discord", allowed_use="api"))

    assert assessment.status == "manual-review"
    assert assessment.automation_eligible is False


def test_assess_resources_preserves_order() -> None:
    assessments = assess_resources(
        [
            Resource(name="First", allowed_use="manual-review"),
            Resource(name="Second", allowed_use="api"),
        ]
    )

    assert [assessment.resource.name for assessment in assessments] == ["First", "Second"]


def test_parser_preserves_compliance_metadata() -> None:
    resources = parse_resources_markdown(
        """
## Price Data
- id: example_market
  name: Example Market
  type: price_site
  url: https://example.test
  allowed_use: manual-review
  collector: price_site_placeholder
  refresh: hourly
  reliability: medium
"""
    )

    assert resources[0].id == "example_market"
    assert resources[0].collector == "price_site_placeholder"
    assert resources[0].refresh == "hourly"
    assert resources[0].reliability == "medium"


def test_preflight_api_with_url_is_eligible() -> None:
    assessment = assess_preflight_resource(
        Resource(
            name="Approved API",
            type="official",
            allowed_use="api",
            url="https://example.test/api",
        )
    )

    assert assessment.status == "approved-api"
    assert assessment.automation_eligible is True
    assert "Ready for source-specific connector design" in assessment.next_step


def test_preflight_rss_with_url_is_eligible() -> None:
    assessment = assess_preflight_resource(
        Resource(
            name="Approved RSS",
            type="official",
            allowed_use="rss",
            url="https://example.test/feed.xml",
        )
    )

    assert assessment.status == "approved-rss"
    assert assessment.automation_eligible is True


def test_preflight_download_with_url_is_eligible() -> None:
    assessment = assess_preflight_resource(
        Resource(
            name="Approved Download",
            type="official",
            allowed_use="download",
            url="https://example.test/data.json",
        )
    )

    assert assessment.status == "approved-download"
    assert assessment.automation_eligible is True


def test_preflight_api_missing_url_is_ineligible() -> None:
    assessment = assess_preflight_resource(
        Resource(name="Missing URL API", type="official", allowed_use="api")
    )

    assert assessment.status == "needs-review"
    assert assessment.automation_eligible is False
    assert "missing a URL" in assessment.reason


def test_preflight_discord_is_gated_even_if_marked_api() -> None:
    assessment = assess_preflight_resource(
        Resource(
            name="Official Discord",
            type="discord",
            allowed_use="api",
            url="https://discord.com/channels/example",
        )
    )

    assert assessment.status == "discord-gated"
    assert assessment.automation_eligible is False
    assert "approved-bot/API" in assessment.reason


def test_preflight_manual_and_blocked_sources_are_ineligible() -> None:
    manual = assess_preflight_resource(
        Resource(name="Manual Source", allowed_use="manual-review")
    )
    blocked = assess_preflight_resource(
        Resource(name="Blocked Source", allowed_use="no-automation")
    )

    assert manual.status == "manual-review"
    assert manual.automation_eligible is False
    assert blocked.status == "blocked"
    assert blocked.automation_eligible is False


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
