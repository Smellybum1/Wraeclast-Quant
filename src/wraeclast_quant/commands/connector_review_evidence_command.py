from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_review_evidence_rendering import (
    print_connector_review_evidence_update,
)
from wraeclast_quant.commands.connector_review_evidence_workflow import (
    update_review_evidence_file,
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
        update = update_review_evidence_file(
            review_path=review_path,
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

        print_connector_review_evidence_update(
            update,
            review_path=review_path,
            resources=load_resources(resources_path),
        )


__all__ = ["register"]
