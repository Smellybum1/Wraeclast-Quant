from pathlib import Path

from wraeclast_quant.config.connector_fixtures import run_connector_fixture
from wraeclast_quant.config.connector_policy import load_connector_review

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import example_approved_api_resources as _example_approved_api_resources
from connector_policy_helpers import minimal_fixture_payload as _minimal_fixture_payload
from connector_policy_helpers import write_connector_fixture as _write_connector_fixture


def test_connector_fixture_runner_refuses_failed_review() -> None:
    result = run_connector_fixture(
        _review(source_terms_reviewed=False),
        [_eligible_resource()],
        "examples/connector_fixture_api_example.json",
    )

    assert result.ready is False
    assert result.fixture is None
    assert "Source terms must be reviewed." in result.blockers


def test_connector_fixture_runner_accepts_approved_example_review() -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    result = run_connector_fixture(
        review,
        _example_approved_api_resources(),
        "examples/connector_fixture_api_example.json",
    )

    assert result.ready is True
    assert result.fixture is not None
    assert result.fetch_plan is not None
    assert len(result.rows) == 2
    assert result.fetch_plan.cache_path.name.endswith(".cache")


def test_connector_fixture_runner_does_not_write_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = _write_connector_fixture(tmp_path, _minimal_fixture_payload())
    result = run_connector_fixture(
        _review(),
        [_eligible_resource()],
        fixture_path,
    )

    assert result.ready is True
    assert not Path("data/raw/cache").exists()
