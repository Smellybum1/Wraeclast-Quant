from pathlib import Path


def test_migration_contract_doc_mentions_version_and_required_commands() -> None:
    doc_text = Path("docs/MIGRATIONS.md").read_text(encoding="utf-8")

    assert "The current SQLite schema version is `2`." in doc_text
    for command in [
        "wq status --strict",
        "wq backup-db",
        "wq migration-readiness --strict",
        "wq verify-backup --backup-path <file>",
        "wq restore-helper --backup-path <file>",
    ]:
        assert command in doc_text
