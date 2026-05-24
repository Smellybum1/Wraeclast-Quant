# Goal Mode Operating Prompt

Use this file when starting a self-directed Wraeclast Quant run from Codex Goal mode.

## Short Goal To Paste

```text
Work autonomously in D:\Codex\Wraeclast Quant by following docs/GOAL_MODE.md. Start by reading AGENTS.md, README.md, docs/ROADMAP.md, then run status --json and preflight. Choose the highest-impact unblocked local-first task, implement one focused packet, verify it, and stop only for decisions that affect architecture, data model, public API, security, source approval, persistence, pricing, or user experience.
```

## Operating Loop

1. Start each packet by reading `AGENTS.md`, `README.md`, `docs/ROADMAP.md`, and this file.
2. Run `git status --short --branch`, `wq status --json`, and `wq preflight`.
3. If `wq` is not on PATH, use the bundled Typer entrypoint:

```powershell
& 'C:\Users\moxhe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from wraeclast_quant.cli import app; app()" status --json
```

4. Choose the highest-impact unblocked task from the roadmap and current health output.
5. Before editing, state the packet goal, success criteria, likely files, and narrow verification path.
6. Implement one focused packet only.
7. Run the narrowest relevant tests first, then broader checks when shared behavior changes.
8. If tests or proof runs stale generated artifacts, rerun `export`, `site`, and `site-bundle`, then verify `status --strict` and `publish-check`.
9. Commit and push only after green verification, if the current thread/user has allowed git writes.
10. Handoff with changed files, checks run, risks, and the next recommended packet.

## Guardrails

- Keep Wraeclast Quant local-first and decision-support only.
- Do not automate gameplay, in-game trading, whispers, UI clicks, movement, keyboard or mouse input, or game-client interaction.
- Do not bypass CAPTCHAs, login walls, robots.txt, source terms, API limits, rate limits, or access controls.
- Do not implement live HTTP, scraping, Discord collection, external publishing, webhooks, or hosted behavior unless explicitly requested and reviewed.
- Keep poe.ninja live fetching unsupported until official endpoint, query parameter, response-field schema, reuse terms, cache/rate policy, and failure behavior are confirmed.
- Preserve `RESOURCES.md` unless the user explicitly approves a manual source edit.
- Preserve public CLI names, command output wording, JSON schemas, SQLite schema, public-intel contract, connector review schema, fixture schema, and generated artifact contracts unless the task explicitly approves a public-interface change.
- For persistence or schema work, require `status --strict`, `backup-db`, `migration-readiness --strict`, and backup verification before changing schema behavior.

## Ask Before

Ask the user before decisions that materially change architecture, product direction, data model, public API, security posture, source approval, persistence semantics, pricing, or user experience.

Otherwise, proceed with the highest-impact unblocked task within these guardrails.
