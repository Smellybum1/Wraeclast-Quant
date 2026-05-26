from wraeclast_quant.collectors.source_connector import FixtureSourceConnector
from wraeclast_quant.config.connector_policy import load_connector_review

from connector_policy_helpers import example_approved_api_resources as _example_approved_api_resources


def test_fixture_source_connector_returns_normalized_rows() -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    connector = FixtureSourceConnector.from_review(
        review,
        _example_approved_api_resources(),
    )

    result = connector.collect_fixture("examples/connector_fixture_api_example.json")

    assert result.connector_id == "fixture-source-connector"
    assert result.connector_class == "FixtureSourceConnector"
    assert result.resource_name == "Example Approved API"
    assert len(result.rows) == 2
    assert result.rows[0].name == "Stormglass Catalyst"
