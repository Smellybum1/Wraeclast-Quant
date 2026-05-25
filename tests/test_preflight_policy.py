from wraeclast_quant.config.preflight import assess_preflight_resource, summarize_preflight
from wraeclast_quant.config.resources_loader import Resource


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
