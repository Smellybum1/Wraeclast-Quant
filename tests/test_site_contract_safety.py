from pathlib import Path

from wraeclast_quant.reports.site_contract import write_site_contract

from site_bundle_helpers import write_publish_ready_bundle as _write_publish_ready_bundle


def test_site_contract_excludes_raw_inputs_and_sensitive_values(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "site_contract.json"

    write_site_contract(database_path, bundle_dir, output_path)

    contract = output_path.read_text(encoding="utf-8")
    forbidden = [
        "raw signal inputs",
        "resource notes:",
        "RESOURCES.md content",
        "secret-token-value",
        "cookie=",
        "api_key=",
        "Stormglass Catalyst inputs",
    ]
    for value in forbidden:
        assert value not in contract
