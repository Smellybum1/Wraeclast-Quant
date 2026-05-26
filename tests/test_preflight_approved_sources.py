from wraeclast_quant.config.preflight import assess_preflight_resource
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
