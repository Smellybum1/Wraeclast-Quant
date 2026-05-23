from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.site_contract_constants import DEFAULT_SITE_CONTRACT_PATH
from wraeclast_quant.reports.site_contract_payload import build_site_contract


def write_site_contract(
    database_path: Path,
    bundle_dir: Path,
    output_path: str | Path = DEFAULT_SITE_CONTRACT_PATH,
) -> tuple[Path, dict[str, Any]]:
    payload = build_site_contract(database_path=database_path, bundle_dir=bundle_dir)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path, payload
