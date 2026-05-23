from pathlib import Path

from wraeclast_quant.intelligence.scoring import OpportunityInputs, action_for_score, score_opportunity


def test_score_formula_is_deterministic() -> None:
    inputs = OpportunityInputs(
        demand_momentum=80,
        build_dependency_score=70,
        price_discount_score=60,
        liquidity_score=50,
        historical_spike_score=40,
        patch_relevance_score=30,
        manipulation_risk=20,
        stale_data_penalty=10,
    )

    assert score_opportunity(inputs) == 52.5


def test_action_mapping() -> None:
    assert action_for_score(75) == "BUY"
    assert action_for_score(55) == "WATCH"
    assert action_for_score(35) == "HOLD / SELL SELECTIVELY"
    assert action_for_score(34.99) == "AVOID"


def test_scoring_contract_doc_matches_scorer() -> None:
    doc_text = Path("docs/SCORING.md").read_text(encoding="utf-8")
    documented_weights = _documented_mapping(doc_text, "The opportunity score uses these weighted signals:")
    documented_thresholds = _documented_mapping(doc_text, "Scores map to actions as follows:")

    assert documented_weights == _live_signal_weights()
    assert action_for_score(float(documented_thresholds["BUY"].removeprefix(">="))) == "BUY"
    assert action_for_score(float(documented_thresholds["WATCH"].removeprefix(">="))) == "WATCH"
    assert (
        action_for_score(
            float(documented_thresholds["HOLD / SELL SELECTIVELY"].removeprefix(">="))
        )
        == "HOLD / SELL SELECTIVELY"
    )
    avoid_boundary = float(documented_thresholds["AVOID"].removeprefix("<"))
    assert action_for_score(avoid_boundary - 0.01) == "AVOID"


def _live_signal_weights() -> dict[str, str]:
    fields = list(OpportunityInputs.model_fields)
    weights: dict[str, str] = {}
    for field in fields:
        low_inputs = OpportunityInputs(**{name: 50 for name in fields} | {field: 0})
        high_inputs = OpportunityInputs(**{name: 50 for name in fields} | {field: 100})
        weight = (score_opportunity(high_inputs) - score_opportunity(low_inputs)) / 100
        weights[field] = f"{weight:+.2f}"
    return weights


def _documented_mapping(doc_text: str, heading: str) -> dict[str, str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        key.strip("`"): value.strip("`")
        for key, value in (
            line.strip()[2:].split(": ", 1)
            for line in section.splitlines()
            if line.strip().startswith("- `")
        )
    }
