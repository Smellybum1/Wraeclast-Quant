from __future__ import annotations

from pathlib import Path


MANUAL_SNAPSHOT_TEMPLATE = Path(
    "examples/pathofexile_currency_exchange_manual_snapshot_template.json"
)


def currency_exchange_manual_snapshot_args(
    *,
    input_path: str | Path = MANUAL_SNAPSHOT_TEMPLATE,
    history_path: str | Path | None = None,
    output_fixture_path: str | Path | None = None,
) -> list[str]:
    args = [
        "currency-exchange-manual-snapshot",
        "--input-path",
        str(input_path),
    ]
    if history_path is not None:
        args.extend(["--history-path", str(history_path)])
    if output_fixture_path is not None:
        args.extend(["--output-fixture-path", str(output_fixture_path)])
    return args


__all__ = [
    "MANUAL_SNAPSHOT_TEMPLATE",
    "currency_exchange_manual_snapshot_args",
]
