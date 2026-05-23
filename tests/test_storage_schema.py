from pathlib import Path

from wraeclast_quant.storage.schema import (
    REQUIRED_SQLITE_TABLES,
    SQLITE_SCHEMA_VERSION,
    SQLITE_TABLE_DESCRIPTIONS,
)


def test_sqlite_schema_contract_lists_required_tables() -> None:
    assert SQLITE_SCHEMA_VERSION == "2"
    assert REQUIRED_SQLITE_TABLES == frozenset(
        {
            "analysis_runs",
            "scored_opportunities",
            "report_artifacts",
            "recommendation_outcomes",
            "run_provenance",
        }
    )
    assert set(SQLITE_TABLE_DESCRIPTIONS) == set(REQUIRED_SQLITE_TABLES)


def test_sqlite_schema_contract_doc_matches_constants() -> None:
    doc_text = Path("docs/SQLITE_SCHEMA.md").read_text(encoding="utf-8")
    documented_version = doc_text.split(
        "The current SQLite schema version is `", 1
    )[1].split("`", 1)[0]
    documented_tables = _documented_table_descriptions(doc_text)

    assert documented_version == SQLITE_SCHEMA_VERSION
    assert frozenset(documented_tables) == REQUIRED_SQLITE_TABLES
    assert documented_tables == SQLITE_TABLE_DESCRIPTIONS


def _documented_table_descriptions(doc_text: str) -> dict[str, str]:
    section = doc_text.split("Required SQLite tables:\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        table.strip("`"): description
        for table, description in (
            line.strip()[2:].split(": ", 1)
            for line in section.splitlines()
            if line.strip().startswith("- `")
        )
    }
