from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import clamp_score
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.intelligence.scoring import OpportunityInputs


RatioValue = str | dict[str, float]


class CurrencyExchangeUiStockRow(BaseModel):
    ratio: RatioValue
    stock: int = Field(ge=0)
    comparator: Literal["exact", "less_than", "greater_than"] = "exact"


class CurrencyExchangeUiObservation(BaseModel):
    want_currency: str
    have_currency: str
    market_ratio: RatioValue | None = None
    stock_rows: list[CurrencyExchangeUiStockRow] = Field(default_factory=list)
    no_stock: bool = False
    league: str | None = None
    notes: str = ""


class CurrencyExchangeUiObservationSnapshot(BaseModel):
    league: str
    observed_at: str | None = None
    observations: list[CurrencyExchangeUiObservation]


@dataclass(frozen=True)
class CurrencyExchangeUiObservationExportResult:
    output_path: Path
    item_count: int
    source_name: str
    review_notes_path: Path | None = None


def load_currency_exchange_ui_observation(path: str | Path) -> CurrencyExchangeUiObservationSnapshot:
    observation_path = Path(path)
    try:
        raw = json.loads(observation_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read Currency Exchange UI observation: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange UI observation JSON: {error}"
        ) from error

    try:
        snapshot = CurrencyExchangeUiObservationSnapshot.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange UI observation: {error}"
        ) from error
    if not snapshot.observations:
        raise ConnectorPolicyError("Invalid Currency Exchange UI observation: observations must not be empty.")
    return snapshot


def write_currency_exchange_ui_observation_manual_import(
    *,
    input_path: str | Path,
    output_path: str | Path,
    review_notes_output_path: str | Path | None = None,
) -> CurrencyExchangeUiObservationExportResult:
    snapshot = load_currency_exchange_ui_observation(input_path)
    payload = currency_exchange_ui_observation_manual_import_payload(snapshot)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    review_notes_path = None
    if review_notes_output_path is not None:
        review_notes_path = Path(review_notes_output_path)
        review_notes_path.parent.mkdir(parents=True, exist_ok=True)
        review_notes_path.write_text(
            currency_exchange_ui_observation_review_notes(snapshot),
            encoding="utf-8",
        )
    return CurrencyExchangeUiObservationExportResult(
        output_path=destination,
        item_count=len(payload["items"]),
        source_name="Path of Exile Currency Exchange UI Observation",
        review_notes_path=review_notes_path,
    )


def currency_exchange_ui_observation_manual_import_payload(
    snapshot: CurrencyExchangeUiObservationSnapshot,
) -> dict[str, list[dict[str, object]]]:
    totals = [visible_stock_total(observation) for observation in snapshot.observations]
    max_total = max(totals) if totals else 0
    return {
        "items": [
            currency_exchange_ui_observation_item(snapshot.league, observation, max_total)
            for observation in snapshot.observations
        ]
    }


def currency_exchange_ui_observation_item(
    default_league: str,
    observation: CurrencyExchangeUiObservation,
    max_visible_stock: int,
) -> dict[str, object]:
    signals = currency_exchange_ui_observation_signals(observation, max_visible_stock)
    league = observation.league or default_league
    return {
        "name": f"{currency_name(observation.want_currency)} / {currency_name(observation.have_currency)} ({league} UI)",
        "signals": signals.model_dump(),
    }


def currency_exchange_ui_observation_review_notes(
    snapshot: CurrencyExchangeUiObservationSnapshot,
) -> str:
    lines = [
        "# Currency Exchange UI Observation Review Notes",
        "",
        "Local review notes only. This file is generated from manually transcribed in-game UI rows.",
        "No OAuth, live HTTP, scraping, OCR, game-client automation, snapshots, outcome recording, or publishing were performed.",
        "",
        f"- League: {snapshot.league}",
        f"- Observed at: {snapshot.observed_at or 'not supplied'}",
        f"- Observations: {len(snapshot.observations)}",
        "",
        "| Pair | Market ratio | Visible stock | Rows | Notes |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for observation in snapshot.observations:
        league = observation.league or snapshot.league
        pair = f"{currency_name(observation.want_currency)} / {currency_name(observation.have_currency)} ({league} UI)"
        rows = "; ".join(_stock_row_summary(row) for row in observation.stock_rows)
        if observation.no_stock and not rows:
            rows = "No stock"
        lines.append(
            "| "
            + " | ".join(
                [
                    _markdown_cell(pair),
                    _markdown_cell(_ratio_summary(observation.market_ratio, observation.no_stock)),
                    str(visible_stock_total(observation)),
                    _markdown_cell(rows or "none"),
                    _markdown_cell(observation.notes or ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Capture Review Flags",
            "",
            *currency_exchange_ui_observation_review_flags(snapshot),
            "",
            "Use this sidecar while choosing local outcome labels after `wq daily --input-path <manual-import-output>`.",
            "Do not record outcomes until a human review decision has been made.",
            "",
        ]
    )
    return "\n".join(lines)


def currency_exchange_ui_observation_review_flags(
    snapshot: CurrencyExchangeUiObservationSnapshot,
) -> list[str]:
    flags: list[str] = []
    for observation in snapshot.observations:
        league = observation.league or snapshot.league
        pair = f"{currency_name(observation.want_currency)} / {currency_name(observation.have_currency)} ({league} UI)"
        has_rows = bool(observation.stock_rows)
        if observation.no_stock:
            flags.append(
                f"- {pair}: No Stock was transcribed; verify this after the next market "
                "refresh before treating the absence as durable evidence."
            )
        elif not has_rows and observation.market_ratio is not None:
            flags.append(
                f"- {pair}: ratio-only capture; add visible stock-ladder rows before "
                "`wq daily` if possible because scoring treats missing stock conservatively."
            )
        elif not has_rows:
            flags.append(
                f"- {pair}: missing market ratio and stock-ladder rows; "
                "recapture before `wq daily` if possible."
            )
        elif observation.market_ratio is None:
            flags.append(
                f"- {pair}: stock-ladder rows were captured without an order-entry market "
                "ratio; verify the ratio before outcome review."
            )
    if not flags:
        return ["- No capture review flags detected."]
    return flags


def currency_exchange_ui_observation_signals(
    observation: CurrencyExchangeUiObservation,
    max_visible_stock: int,
) -> OpportunityInputs:
    stock_total = visible_stock_total(observation)
    row_count = len(observation.stock_rows)
    spread = visible_ratio_spread_percent(observation)

    if stock_total <= 0:
        liquidity_score = 0.0 if observation.no_stock else 20.0
        demand_momentum = 20.0 if observation.no_stock else 35.0
        price_discount_score = 20.0 if observation.no_stock else 35.0
        stale_data_penalty = 25.0 if observation.no_stock else 15.0
    else:
        liquidity_score = clamp_score(15.0 + (stock_total / max(max_visible_stock, 1)) * 85.0)
        demand_momentum = clamp_score(35.0 + liquidity_score * 0.45 + min(row_count, 6) * 3.0)
        price_discount_score = clamp_score(65.0 - spread * 0.75)
        stale_data_penalty = 5.0

    manipulation_risk = clamp_score(
        (100.0 - liquidity_score) * 0.55
        + spread * 0.70
        + (25.0 if observation.no_stock else 0.0)
    )

    return OpportunityInputs(
        demand_momentum=demand_momentum,
        build_dependency_score=50.0,
        price_discount_score=price_discount_score,
        liquidity_score=liquidity_score,
        historical_spike_score=50.0,
        patch_relevance_score=50.0,
        manipulation_risk=manipulation_risk,
        stale_data_penalty=stale_data_penalty,
    )


def visible_stock_total(observation: CurrencyExchangeUiObservation) -> int:
    return sum(row.stock for row in observation.stock_rows)


def visible_ratio_spread_percent(observation: CurrencyExchangeUiObservation) -> float:
    ratios = [ratio_to_float(row.ratio) for row in observation.stock_rows]
    if not ratios:
        return 100.0 if observation.no_stock else 50.0

    baseline = ratio_to_float(observation.market_ratio) if observation.market_ratio is not None else ratios[0]
    if baseline <= 0:
        return 100.0
    return clamp_score(((max(ratios) - min(ratios)) / baseline) * 100.0)


def ratio_to_float(value: RatioValue) -> float:
    if isinstance(value, str):
        parts = [part.strip().replace(",", "") for part in value.split(":")]
        if len(parts) != 2:
            raise ConnectorPolicyError(f"Invalid ratio value: {value}")
        left = _positive_float(parts[0], value)
        right = _positive_float(parts[1], value)
        return left / right

    if isinstance(value, dict):
        if "want" not in value or "have" not in value:
            raise ConnectorPolicyError("Ratio objects must include want and have values.")
        left = _positive_float(value["want"], value)
        right = _positive_float(value["have"], value)
        return left / right

    raise ConnectorPolicyError(f"Invalid ratio value: {value}")


def _positive_float(value: Any, original: object) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ConnectorPolicyError(f"Invalid ratio value: {original}") from error
    if parsed <= 0:
        raise ConnectorPolicyError(f"Ratio values must be positive: {original}")
    return parsed


def currency_name(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("_", " ").split())


def _stock_row_summary(row: CurrencyExchangeUiStockRow) -> str:
    prefix = {"exact": "", "less_than": "<", "greater_than": ">"}[row.comparator]
    return f"{prefix}{format_ratio_value(row.ratio)} stock {row.stock:,}"


def _ratio_summary(value: RatioValue | None, no_stock: bool) -> str:
    if no_stock:
        return "No Stock"
    if value is None:
        return "not supplied"
    return format_ratio_value(value)


def format_ratio_value(value: RatioValue) -> str:
    if isinstance(value, str):
        return value
    return f"{value['want']:g}:{value['have']:g}"


def _markdown_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


__all__ = [
    "CurrencyExchangeUiObservation",
    "CurrencyExchangeUiObservationExportResult",
    "CurrencyExchangeUiObservationSnapshot",
    "CurrencyExchangeUiStockRow",
    "currency_exchange_ui_observation_item",
    "currency_exchange_ui_observation_manual_import_payload",
    "currency_exchange_ui_observation_review_flags",
    "currency_exchange_ui_observation_review_notes",
    "currency_exchange_ui_observation_signals",
    "format_ratio_value",
    "load_currency_exchange_ui_observation",
    "ratio_to_float",
    "visible_ratio_spread_percent",
    "visible_stock_total",
    "write_currency_exchange_ui_observation_manual_import",
]
