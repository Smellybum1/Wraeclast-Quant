from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_review_status_rendering import print_connector_review_status
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    connector_review_status,
    load_connector_review,
    update_connector_review_evidence,
    write_connector_review_draft,
)
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-review-evidence")
    def connector_review_evidence(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        source_terms_url: str | None = typer.Option(None, "--source-terms-url"),
        robots_or_api_policy_url: str | None = typer.Option(None, "--robots-or-api-policy-url"),
        reviewed_at: str | None = typer.Option(None, "--reviewed-at", help="Review date in YYYY-MM-DD format."),
        allowed_data_shape: str | None = typer.Option(None, "--allowed-data-shape"),
        review_notes: str | None = typer.Option(None, "--review-notes"),
        rate_limit_per_minute: float | None = typer.Option(None, "--rate-limit-per-minute"),
        cache_ttl_seconds: int | None = typer.Option(None, "--cache-ttl-seconds"),
        authentication_required: bool | None = typer.Option(
            None,
            "--authentication-required/--no-authentication-required",
        ),
        login_required: bool | None = typer.Option(None, "--login-required/--no-login-required"),
        captcha_gated: bool | None = typer.Option(None, "--captcha-gated/--no-captcha-gated"),
        private_data_risk: bool | None = typer.Option(
            None,
            "--private-data-risk/--no-private-data-risk",
        ),
    ) -> None:
        try:
            review = load_connector_review(review_path)
            updated = update_connector_review_evidence(
                review,
                source_terms_url=source_terms_url,
                robots_or_api_policy_url=robots_or_api_policy_url,
                reviewed_at=reviewed_at,
                allowed_data_shape=allowed_data_shape,
                review_notes=review_notes,
                rate_limit_per_minute=rate_limit_per_minute,
                cache_ttl_seconds=cache_ttl_seconds,
                authentication_required=authentication_required,
                login_required=login_required,
                captcha_gated=captcha_gated,
                private_data_risk=private_data_risk,
            )
            write_connector_review_draft(updated, review_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        console.print(f"Updated connector review evidence in {review_path}")
        print_connector_review_status(
            connector_review_status(updated, load_resources(resources_path))
        )
        console.print(
            "Evidence update is local-only. It did not edit RESOURCES.md, fetch data, or approve a connector."
        )
