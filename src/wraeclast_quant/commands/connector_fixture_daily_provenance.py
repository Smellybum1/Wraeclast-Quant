from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands._connector_support import file_sha256
from wraeclast_quant.commands.connector_fixture_daily_inputs import ConnectorFixtureDailyInput
from wraeclast_quant.workflows.daily_pipeline import RunProvenanceInput


def connector_fixture_daily_provenance(
    *,
    daily_input: ConnectorFixtureDailyInput,
    review_path: Path,
    fixture_path: Path,
) -> RunProvenanceInput:
    assert daily_input.fixture_result.fixture is not None
    return RunProvenanceInput(
        source_kind="connector-fixture",
        resource_name=daily_input.connector.resource.name,
        connector_id=daily_input.connector.connector_id,
        access_method=daily_input.review.access_method,
        metadata={
            "connector_class": daily_input.connector.__class__.__name__,
            "fixture_source_name": daily_input.fixture_result.fixture.source_name,
            "fixture_generated_at": daily_input.fixture_result.fixture.generated_at,
            "fixture_item_count": len(daily_input.fixture_result.rows),
            "review_file": review_path.name,
            "review_sha256": file_sha256(review_path),
            "fixture_file": fixture_path.name,
            "fixture_sha256": file_sha256(fixture_path),
            "future_cache_path": str(daily_input.connector.fetch_plan.cache_path),
        },
    )


__all__ = ["connector_fixture_daily_provenance"]
