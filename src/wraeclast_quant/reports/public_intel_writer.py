from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel_constants import DEFAULT_PUBLIC_INTEL_PATH


def write_public_intel(payload: dict[str, Any], output_path: Path = DEFAULT_PUBLIC_INTEL_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path
