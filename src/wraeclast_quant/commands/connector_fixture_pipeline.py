from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.collectors.source_connector import FixtureSourceConnector
from wraeclast_quant.commands._connector_support import console, file_sha256, load_fixture_resources
from wraeclast_quant.commands.snapshot_rendering import print_alert_candidates
from wraeclast_quant.config.connector_fixtures import connector_fixture_signal_items, run_connector_fixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, load_connector_review
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.workflows.daily_pipeline import (
    RunProvenanceInput,
    create_alert_settings,
    run_daily_pipeline,
)


def register(app: typer.Typer) -> None:
    @app.command("connector-fixture-daily")
    def connector_fixture_daily(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        fixture_path: Path = typer.Option(..., "--fixture-path", help="Local connector fixture JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        brief_path: Path = typer.Option(Path("data/processed/market_brief.md"), "--brief-path"),
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
        watch_threshold: float = typer.Option(55.0, "--watch-threshold", min=0, max=100),
        buy_threshold: float = typer.Option(75.0, "--buy-threshold", min=0, max=100),
        big_delta: float = typer.Option(10.0, "--big-delta", min=0, max=100),
    ) -> None:
        try:
            alert_settings = _alert_settings(watch_threshold, buy_threshold, big_delta)
            review = load_connector_review(review_path)
            connector_resources = load_fixture_resources(resources_path)
            connector = FixtureSourceConnector.from_review(review, connector_resources)
            fixture_result = run_connector_fixture(review, connector_resources, fixture_path)
            if not fixture_result.ready:
                blockers = "\n".join(fixture_result.blockers)
                raise ConnectorPolicyError(blockers or "Connector fixture daily failed.")
            items = connector_fixture_signal_items(fixture_result.rows)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        opportunities = rank_opportunities(items)
        assert fixture_result.fixture is not None
        result = run_daily_pipeline(
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
        if result is None:
            console.print("No snapshots found.")
            return

        console.print(f"Connector fixture daily run #{result.run.id} complete.")
        console.print(f"Database: {database_path}")
        console.print(f"Market brief: {result.brief_path}")
        console.print(f"Public intel: {result.intel_path}")
        console.print(f"Dashboard: {result.site_path}")

        if result.comparison is None:
            console.print("No previous snapshot found for comparison.")
            return
        print_alert_candidates(result.alert_candidates, limit=limit)


def _alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    try:
        return create_alert_settings(watch_threshold, buy_threshold, big_delta)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error
