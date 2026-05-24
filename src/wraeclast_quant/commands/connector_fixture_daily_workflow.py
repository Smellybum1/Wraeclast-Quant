from __future__ import annotations

from pathlib import Path

from wraeclast_quant.collectors.source_connector import source_connector_from_review
from wraeclast_quant.commands._connector_support import file_sha256, load_fixture_resources
from wraeclast_quant.config.connector_fixtures import connector_fixture_signal_items, run_connector_fixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, load_connector_review
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.workflows.daily_pipeline import DailyPipelineResult, RunProvenanceInput, run_daily_pipeline


def run_connector_fixture_daily_pipeline(
    *,
    review_path: Path,
    fixture_path: Path,
    resources_path: Path,
    database_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    limit: int,
    alert_settings: AlertRuleSettings,
) -> DailyPipelineResult | None:
    review = load_connector_review(review_path)
    connector_resources = load_fixture_resources(resources_path)
    connector = source_connector_from_review(review, connector_resources)
    fixture_result = run_connector_fixture(review, connector_resources, fixture_path)
    if not fixture_result.ready:
        blockers = "\n".join(fixture_result.blockers)
        raise ConnectorPolicyError(blockers or "Connector fixture daily failed.")

    items = connector_fixture_signal_items(fixture_result.rows)
    opportunities = rank_opportunities(items)
    assert fixture_result.fixture is not None
    return run_daily_pipeline(
        opportunities=opportunities,
        source_mode="connector-fixture",
        database_path=database_path,
        resources_path=resources_path,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        limit=limit,
        alert_settings=alert_settings,
        provenance=RunProvenanceInput(
            source_kind="connector-fixture",
            resource_name=connector.resource.name,
            connector_id=connector.connector_id,
            access_method=review.access_method,
            metadata={
                "connector_class": connector.__class__.__name__,
                "fixture_source_name": fixture_result.fixture.source_name,
                "fixture_generated_at": fixture_result.fixture.generated_at,
                "fixture_item_count": len(fixture_result.rows),
                "review_file": review_path.name,
                "review_sha256": file_sha256(review_path),
                "fixture_file": fixture_path.name,
                "fixture_sha256": file_sha256(fixture_path),
                "future_cache_path": str(connector.fetch_plan.cache_path),
            },
        ),
    )
