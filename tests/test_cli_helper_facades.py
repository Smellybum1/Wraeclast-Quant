import importlib


def test_cli_helper_facades_preserve_reexported_names() -> None:
    expected_exports = {
        "cli_connector_helpers": {
            "connector_fixture_run_args",
            "connector_review",
            "write_connector_resources",
            "write_connector_review",
        },
        "cli_public_artifact_helpers": {
            "export_args",
            "public_intel_payload",
            "status_args",
            "write_publish_ready_bundle",
        },
        "cli_public_artifact_command_helpers": {
            "export_args",
            "publish_check_args",
            "site_args",
            "site_contract_args",
        },
        "cli_status_helpers": {
            "status_args",
            "status_json_args",
            "status_workspace",
            "write_stale_public_intel",
        },
        "cli_outcome_helpers": {
            "calibration_args",
            "calibration_reviewed_database",
            "record_outcome_args",
            "reviewed_single_opportunity_database",
        },
        "cli_market_flow_helpers": {
            "alerts_args",
            "buy_crossing_database",
            "compare_args",
            "comparison_database_with_changes",
        },
        "cli_backup_helpers": {
            "backup_db_args",
            "invalid_backup_dir",
            "migration_readiness_args",
            "sample_data_backup",
        },
        "cli_daily_helpers": {
            "daily_args",
            "previous_stormglass_database",
            "schedule_helper_args",
            "small_mover_daily_setup",
        },
        "cli_connector_resource_helpers": {
            "approved_api_resources_text",
            "conditional_api_resources_text",
            "poe_ninja_currency_resources_text",
            "write_connector_resources",
        },
        "cli_connector_review_helpers": {
            "connector_review",
            "write_connector_review",
        },
        "cli_provenance_helpers": {
            "latest_connector_fixture_provenance_database",
            "missing_provenance_database",
            "run_provenance_args",
            "two_run_provenance_database",
        },
        "cli_manual_import_helpers": {
            "import_args",
            "inspect_import_args",
            "validate_import_args",
            "write_manual_import_json",
        },
        "cli_doc_helpers": {
            "PUBLIC_COMMANDS",
            "command_help_args",
            "documented_bullet_list",
            "documented_bullets",
            "documented_status_row_keys",
        },
    }

    for module_name, names in expected_exports.items():
        module = importlib.import_module(module_name)

        assert names <= set(module.__all__)
        for name in names:
            assert hasattr(module, name)
