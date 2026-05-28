# Skill Feedback Loop

This file is the lightweight, SkillOpt-inspired feedback loop for improving Wraeclast Quant agent guidance. It trains project procedure, not model weights, and it does not add a runtime dependency.

Use it when a Codex run reveals a repeated workflow issue, missed safety boundary, unclear project term, avoidable verification gap, or recurring handoff friction. Do not use it for one-off preferences or to bypass user approval.

## Operating Rules

- Keep entries local-first and derived-only: do not include secrets, credentials, raw source pages, private data, outcome notes, or unredacted local-only sensitive paths.
- Treat proposed guidance edits as candidates until validation passes and the edit is accepted by a normal project packet.
- Prefer bounded edits to existing guidance files or skills; avoid broad rewrites.
- Preserve Wraeclast Quant safety boundaries: no gameplay automation, trade automation, scraping, live HTTP collection, OAuth work, Discord collection, Exile-UI mutation, or publishing automation without explicit approval and review.
- Record rejected or deferred candidates so future agents do not rediscover the same bad idea.

## Entry Template

Copy this block under `Feedback Log` when there is useful evidence.

```md
### YYYY-MM-DD - Short Title

- Status: Proposed | Accepted | Rejected | Deferred
- Evidence: What happened? Include command names, docs, tests, or repeated workflow symptom.
- Candidate guidance edit: What small instruction, skill change, doc update, or checklist change would prevent this?
- Validation gate: What would prove the edit helped without regressing behavior? Prefer concrete commands or review checks.
- Decision: Why was it accepted, rejected, or deferred?
- Follow-up: Optional next packet or owner.
```

## Acceptance Gate

A candidate becomes accepted only after:

- the edit is implemented in the smallest appropriate guidance surface, such as `AGENTS.md`, `docs/CONTEXT.md`, `.codex/progress.md`, or a local skill;
- the relevant narrow verification passes;
- broader checks run when the edit changes autonomous execution, source compliance, persistence, public artifacts, or command behavior;
- the accepted entry names the evidence and verification that justified the change.

## Feedback Log

### 2026-05-28 - Adopt SkillOpt-Inspired Guidance Process

- Status: Accepted
- Evidence: User asked whether Microsoft SkillOpt would help Wraeclast Quant workflow. Review found the useful part is the evidence-driven loop: rollout evidence, bounded edits, validation gates, and rejected-edit memory. The full SkillOpt toolchain would add benchmark data, credentials, repeated model calls, and dependency overhead that are not needed for this repo right now.
- Candidate guidance edit: Add this local feedback log plus concise project guidance so future agents can propose and validate instruction/skill improvements without adding SkillOpt as a dependency.
- Validation gate: Docs-only review, `git diff --check`, and local readiness checks after editing.
- Decision: Accepted as a lightweight project process. Direct SkillOpt integration remains deferred.
- Follow-up: Use this log when future packets reveal repeated workflow friction or a candidate update to project skills/guidance.
