from pathlib import Path

from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR

from cli_doc_markdown_helpers import documented_bullets as _documented_bullets
from cli_doc_markdown_helpers import documented_mapping as _documented_mapping


def test_backup_contract_doc_matches_defaults_and_verification_fields() -> None:
    doc_text = Path("docs/BACKUPS.md").read_text(encoding="utf-8")
    default_paths = _documented_mapping(doc_text, "## Default Paths")
    verification_fields = _documented_bullets(doc_text, "Backup verification reports:")

    assert default_paths["backup_dir"] == str(DEFAULT_BACKUP_DIR).replace("\\", "/")
    assert verification_fields == {
        "schema_version",
        "required_tables",
        "size_bytes",
        "analysis_run_count",
        "scored_opportunity_count",
        "report_artifact_count",
        "recommendation_outcome_count",
        "latest_run_id",
        "latest_run_created_at",
        "latest_run_source_mode",
        "latest_run_item_count",
    }
