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
- Read `docs/CONTEXT.md` when work depends on project language, domain concepts, connector/source-compliance meaning, public artifact contracts, persistence, or autonomous execution terms.
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

## Autonomous Roadmap Execution

When asked to "advance the project", "continue the roadmap", "work autonomously", "pick the next task", "do the next packet", or similar, operate as a self-directed execution loop even if Goal Mode is unavailable.

Default behavior:

- Read `AGENTS.md`, `README.md`, `docs/ROADMAP.md`, `PLAN.md` if present, relevant TODOs/issues, tests, and recent local logs or generated handoff notes when they exist before choosing work.
- Run `git status --short --branch` before editing.
- Rank available work by project impact, user value, dependency-unblocking value, risk, and implementation effort.
- Pick the highest-impact unblocked task that does not require user input.
- Work on one small packet at a time: one feature slice, one refactor, one bug fix, one proof path, or one documentation/update task.
- Before editing, state the packet goal, why it is the best next task, acceptance criteria, likely files touched, narrow verification path, and rollback notes when rollback is non-obvious.
- Make the smallest useful change that satisfies the acceptance criteria.
- Run focused verification first, then broader tests/checks when shared behavior, CLI behavior, generated artifacts, persistence, or core paths change.
- Update the roadmap, progress log, or relevant planning document only when the completed packet changes project state, next steps, or handoff context.
- Update `docs/CONTEXT.md` only when a packet creates or clarifies durable project language that future agents should reuse.
- Add an ADR under `docs/adr/` only for decisions that are hard to reverse, surprising without context, or the result of a real trade-off.
- After a packet passes verification, continue to the next highest-impact unblocked packet when the user asked for autonomous progress; otherwise hand off with the next recommended packet.
- If context becomes long, do not stop solely for that reason. First create or update a concise checkpoint in `.codex/progress.md` with current branch/worktree state, completed packet summaries, verification history, known risks, and the next recommended packet, then continue from that checkpoint after any context compaction.
- If running in normal chat mode instead of Goal Mode, treat a prompt such as "advance the project according to AGENTS.md" as permission to run this loop packet-by-packet without requiring the user to paste the full instructions again.

Stop and ask the user only when:

- A decision materially changes architecture, product direction, data model, public API, auth/security, deployment, persistence semantics, pricing, major UX behavior, or source approval.
- Requirements conflict.
- Validation cannot be run or repeatedly fails for unclear reasons.
- Secrets, credentials, paid services, deployment access, or external accounts are required.
- A new dependency, migration, schema change, public command, or risky source edit is needed.
- The approved task queue is complete.

Git rules:

- Commit only after verification passes and the diff contains only intended changes.
- Do not push without explicit user approval.
- If commits are not requested, leave changes uncommitted and summarize the diff.

Reporting after each packet:

- What changed.
- Why it was chosen.
- Files changed.
- Verification run and results.
- Risks or follow-ups.
- Next recommended packet.

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
