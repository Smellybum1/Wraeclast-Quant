from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import ConnectorReview


def add_review_safety_blockers(review: ConnectorReview, blockers: list[str]) -> None:
    if review.authentication_required:
        blockers.append("Authentication-required sources are not eligible in this gate.")
    if review.login_required:
        blockers.append("Login-required sources are not eligible in this gate.")
    if review.captcha_gated:
        blockers.append("CAPTCHA-gated sources are not eligible.")
    if review.private_data_risk:
        blockers.append("Private data or private-message risk is not eligible.")
    if review.rate_limit_per_minute <= 0:
        blockers.append("rate_limit_per_minute must be positive.")
    if review.cache_ttl_seconds <= 0:
        blockers.append("cache_ttl_seconds must be positive.")
    if not review.dry_run_supported:
        blockers.append("Dry-run support must be explicitly confirmed.")
    if not review.public_export_derived_only:
        blockers.append("Public export must be derived-only.")


__all__ = ["add_review_safety_blockers"]
