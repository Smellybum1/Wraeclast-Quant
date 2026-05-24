from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.connector_fixture_io import load_connector_fixture
from wraeclast_quant.config.connector_fixture_models import ConnectorFixtureRunResult
from wraeclast_quant.config.connector_policy import ConnectorReview, check_connector_review
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource


def run_connector_fixture(
    review: ConnectorReview,
    resources: list[Resource],
    fixture_path: str | Path,
) -> ConnectorFixtureRunResult:
    check = check_connector_review(review, resources)
    if not check.ready:
        return ConnectorFixtureRunResult(
            fixture=None,
            rows=[],
            fetch_plan=None,
            ready=False,
            blockers=check.blockers,
        )

    plan_result = build_fetch_plan(review, resources)
    if plan_result.plan is None:
        return ConnectorFixtureRunResult(
            fixture=None,
            rows=[],
            fetch_plan=None,
            ready=False,
            blockers=plan_result.check.blockers,
        )

    fixture = load_connector_fixture(fixture_path)
    return ConnectorFixtureRunResult(
        fixture=fixture,
        rows=fixture.items,
        fetch_plan=plan_result.plan,
        ready=True,
        blockers=[],
    )
