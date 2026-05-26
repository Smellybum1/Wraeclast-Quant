import pytest

from wraeclast_quant.config.connector_candidates import suggested_access_method
from wraeclast_quant.config.resources_loader import Resource


@pytest.mark.parametrize(
    ("allowed_use", "expected"),
    [
        ("api-or-manual-review", "api"),
        ("manual-or-api-if-available", "api"),
        ("manual-review-or-api-if-available", "api"),
        ("rss-or-manual-review", "rss"),
        ("download", "download"),
        ("manual-review", "manual-export"),
    ],
)
def test_connector_candidate_suggested_access_method_from_allowed_use(
    allowed_use: str,
    expected: str,
) -> None:
    assert suggested_access_method(Resource(name="Source", allowed_use=allowed_use)) == expected
