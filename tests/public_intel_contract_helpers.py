import json
from pathlib import Path

from cli_public_intel_payload_helpers import public_intel_payload as _public_intel_payload


def write_public_intel_payload(tmp_path: Path, payload: dict[str, object]) -> Path:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(payload), encoding="utf-8")
    return intel_path


def public_intel_payload() -> dict[str, object]:
    payload = _public_intel_payload()
    payload["alerts"] = [
        {
            "severity": "high",
            "item_name": "Stormglass Catalyst",
            "reason": "Score crossed into BUY",
            "latest_score": 76.0,
            "score_delta": 26.0,
        }
    ]
    return payload


__all__ = ["public_intel_payload", "write_public_intel_payload"]
