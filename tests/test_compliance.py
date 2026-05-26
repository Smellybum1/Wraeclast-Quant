from wraeclast_quant.config.compliance import assess_resource, assess_resources
from wraeclast_quant.config.resources_loader import Resource


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
