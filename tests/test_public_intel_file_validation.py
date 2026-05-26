from pathlib import Path

import pytest

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)


def test_validate_public_intel_file_rejects_missing_file_without_creating_it(tmp_path: Path) -> None:
    intel_path = tmp_path / "missing" / "public_intel.json"

    with pytest.raises(PublicIntelContractError, match="Public intel file not found"):
        validate_public_intel_file(intel_path)

    assert not intel_path.exists()
    assert not intel_path.parent.exists()


def test_validate_public_intel_file_rejects_invalid_json(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text("{not json", encoding="utf-8")

    with pytest.raises(PublicIntelContractError, match="Invalid public intel JSON"):
        validate_public_intel_file(intel_path)
