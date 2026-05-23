# Wraeclast Quant Agent Guidance

## Project Overview

- Product name: Wraeclast Quant.
- Repo/package: `wraeclast-quant` / `wraeclast_quant`.
- CLI command: `wq`.
- This is a local-first Path of Exile 2 market intelligence and decision-support app.
- The app may provide research, alerts, watchlists, market briefs, cached snapshots, and recommendations for manual review only.

## Safety and Scope Boundaries

- Never automate gameplay, in-game trading, whispers, UI clicks, movement, keyboard or mouse input, or game-client interaction.
- Never bypass rate limits, CAPTCHAs, login walls, robots.txt, source terms, API limits, or access controls.
- Never perform trades or take actions on behalf of the user.
- Keep recommendations human-readable and decision-support only; the user must manually execute all trades.
- Do not add scraping of websites or Discord without explicit approval and a compliance review.
- Do not use Discord user tokens, private-message scraping, or permission bypasses.

## Default Operating Mode

- Prefer small, focused work packets over broad "do everything" batches.
- Read the smallest set of files needed to act safely; expand context when architecture, persistence, data flow, or source compliance is affected.
- Run the narrowest useful check first, then broader checks when changes are cross-cutting.
- Use deterministic behavior for MVP logic, especially scoring and reports.
- Keep modules small, typed, and easy to test.
- Use the general `behavior-preserving-decomposition` skill when decomposing modules while preserving public behavior.
- Use the general `local-compliance-data-workflow` skill when planning connector, source-review, local artifact, backup, migration, or compliance-gated data workflow changes.

## Task Workflow

- For ambiguous or multi-file work, identify success criteria before editing.
- Direct execution is fine for obvious small tasks.
- For bug fixes, prefer adding or updating a focused regression test when practical.
- Before non-trivial edits, state assumptions, success criteria, and the narrow verification path.
- Push back when a request risks violating the project safety boundary or source terms.

## Implementation Discipline

- Prefer the smallest change that satisfies the request.
- Touch only files needed for the task.
- Match existing style, naming, and local patterns.
- Avoid new abstractions, dependencies, or broad refactors unless requested or clearly justified.
- Do not reformat unrelated files.
- Do not rename, move, or reorganize files unless the task requires it.
- Prefer typed Python and deterministic functions with focused tests.

## Resource and Collector Rules

- Preserve the user's existing `RESOURCES.md`; do not overwrite it.
- Treat `RESOURCES.md` as the source of truth for configured resources.
- Make the resource parser tolerant of Markdown headings, bullet-list resources, indented `key: value` metadata, tables, and missing optional fields.
- Do not hardcode configured resources in code or tests.
- External collectors should remain dry-run placeholders unless explicitly asked to implement a compliant source-specific connector.
- Prefer official APIs, RSS feeds, downloadable data, cached snapshots, or manual-review workflows.
- Before implementing any real connector, review source terms, robots.txt, authentication requirements, rate limits, caching expectations, and allowed use.
- Keep Discord collection manual-review or approved-bot/API compliant only; never use user tokens or private-message collection.

## Data and Persistence Rules

- Store only local data by default.
- Preserve local user data, snapshots, reports, and resource configuration unless explicitly asked to change them.
- Ask before changing persistence formats, migrations, backup behavior, or user-generated data.
- Cache aggressively when collection is later implemented.
- Reports should be clear Markdown artifacts under `data/processed/` unless the user requests otherwise.

## Dependency Discipline

- Do not add dependencies unless necessary.
- Before adding a dependency, explain why existing code or built-in Python features are insufficient.
- Prefer established, maintained packages already aligned with the project stack.
- Ask before adding dependencies that affect authentication, networking, scraping, persistence, deployment, or user data.

## Verification

- For docs-only changes, the smallest useful check may be reading the changed file.
- For parser changes, run focused resource-loader tests first.
- For scoring changes, run scoring tests and confirm deterministic expected values.
- For CLI changes, run the relevant `wq` command.
- Definition of done should include relevant tests passing and key CLI commands working when the change affects CLI behavior.
- Do not claim success for checks that were not run.

## Command Hygiene

- Prefer project scripts and narrow commands.
- Keep approval requests narrow and reusable.
- Avoid destructive commands unless explicitly requested and clearly justified.
- Be careful with commands that delete files, rewrite history, change permissions, modify secrets, or affect global machine state.
- If `wq` is not on PATH in the current shell, verify the installed entry point through the active Python environment and report the PATH limitation clearly.

## Secrets and Local Data

- Never print, commit, or expose secrets, API keys, tokens, credentials, cookies, private environment values, or `.env` contents.
- Do not modify `.env`, `.env.local`, or secret/config files unless explicitly asked.
- Do not store Discord tokens, session cookies, or private account credentials in the repo.
- Preserve local-first operation unless the user explicitly requests and approves a compliant external connector.

## Final Handoff

- Report what changed.
- Mention changed files when useful.
- Report what verification ran and whether it passed.
- Mention skipped checks, risks, known limitations, or follow-up work when relevant.
- If manual testing is needed, describe the smallest useful manual test.
