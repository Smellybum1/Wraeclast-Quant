from pathlib import Path

from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR


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


def _documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }
