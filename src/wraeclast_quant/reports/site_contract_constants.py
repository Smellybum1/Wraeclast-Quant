from __future__ import annotations

from pathlib import Path

SITE_CONTRACT_SCHEMA_VERSION = "1.0"
DEFAULT_SITE_CONTRACT_PATH = Path("data/processed/site_contract.json")
REQUIRED_SITE_CONTRACT_KEYS = {
    "schema_version",
    "generated_at",
    "product",
    "latest_database_run_id",
    "artifact_run_ids",
    "public_intel",
    "static_site",
    "bundle",
    "required_bundle_files",
    "publish_readiness",
    "safety",
}
SAFETY_STATEMENT = (
    "Local derived static-site handoff only. Wraeclast Quant did not upload, host, "
    "publish, start a server, make network calls, call webhooks, post to Discord, "
    "scrape sources, approve sources, automate gameplay, perform trades, send "
    "whispers, click UI, move characters, or interact with the game client."
)
