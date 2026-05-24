# Wraeclast Quant Progress

## 2026-05-24

- Health before work: `status --json` ok; `preflight` reports 22 resources, 1 automation-eligible resource (`poe_ninja_poe2_currency`); live poe.ninja collection remains unsupported pending official endpoint/field-contract evidence.
- Completed packet: extracted connector fixture payload writers into `tests/connector_policy_helpers.py` without changing connector-policy assertions or runtime behavior.
- Verification: `pytest tests/test_connector_policy.py`, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Completed packet: extracted approved Example API resource helpers for connector fixture/export tests without changing connector-policy assertions or runtime behavior.
- Verification: `pytest tests/test_connector_policy.py`, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Completed packet: split connector policy constants and error class behind the stable `connector_policy_models` facade without changing public imports.
- Verification: `pytest tests/test_connector_policy.py`, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Completed packet: split storage row converters by run, opportunity, artifact, provenance, and outcome domains behind the stable `repository_row_converters` facade.
- Verification: storage/outcome focused tests, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Completed packet: split alert rule helpers by candidate construction, threshold checks, action ranking, and sorting behind the stable `generate_alerts` facade.
- Verification: alert-focused tests, related delta/export/daily tests, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Completed packet: split connector policy models into focused review, check/status, approval, and report model modules behind the stable `connector_policy_models` facade.
- Verification: connector model facade import smoke, connector-policy tests, connector CLI slice, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Completed packet: split calibration report Markdown rendering into focused section helpers behind the stable `calibration_rendering` facade.
- Verification: calibration/outcome focused tests, calibration CLI slice, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Completed packet: split snapshot delta construction into focused new, removed, changed, and item-order helpers behind the stable `compare_opportunities` facade.
- Verification: snapshot-delta tests, related alert/public-intel/CLI tests, full `pytest`, `export`, `site`, `site-bundle`, `status --strict`, `publish-check`, `migration-readiness --strict`, and `Get-FileHash -Algorithm SHA256 RESOURCES.md` all passed.
- Protected resource hash: `79416C69ED4F29B7C540BDCAAD76A8A22F84673738B4F7E2043F1725D6196BF6`.
- Safety state: no live HTTP, scraping, Discord collection, publishing automation, schema migration, source approval, dependency change, or `RESOURCES.md` edit.
- Next likely unblocked work: continue bounded maintainability with small test-helper cleanup or status artifact row cleanup while live source work remains blocked.
