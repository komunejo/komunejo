---
id: ISS-001
entity: issue
title: "index__synced-artifacts was not scaffolded per DEC-019"
status: resolved
date: 2026-07-13
tags: [creation, conformance, dec019]
---

## What happened

`index__synced-artifacts`, a space managed by the engine (it has `entity-manager.yaml`, `schemas/`, `entities/`), was found missing the artifacts DEC-019 mandates at creation:

- no `.gitignore` (creation step 1) — one had to be written by hand when the space was brought under git;
- no `.claude/` — neither the copied validator `.claude/entity_lint.py` nor the PostToolUse hook in `.claude/settings.json` (step 3);
- no `CLAUDE.md` (step 4).

Its `README.md` was present.

## Why it matters

The absent `.gitignore` is a **latent** defect: it has not caused a failure because the space has not yet been synchronized across machines — but on synchronization it would have, with machine-local paths and session state entering the shared history. The absent validator copy and hook mean the deterministic-integrity mechanism ([[REQ-002]]) does not fire automatically in this space at all: every validation there has been a manual, remembered act — exactly what the engine exists to remove.

## Scope and cause

Single root cause: the space was not scaffolded through the creation flow. The defect is the plugin's, and the plugin no longer has it: creation now installs the full scaffolding — operating skills in `.claude/skills/`, hook in `.claude/settings.json`, conscious `.gitignore`, tracked `CLAUDE.md` ([[DEC-020]], [[DEC-021]]) — verified end to end on a freshly created space (2026-07-13). Repairing the space that surfaced this issue is that repository's own business, not the plugin's.

Even a conformant creation would not fully suffice, because the validator and hook land in `.claude/`, which the standard `.gitignore` excludes, so they would not travel to a second machine. That systemic side is tracked separately in [[PROP-001]].
