---
id: PROP-001
entity: proposal
title: "The generated .gitignore must not exclude a space's validator and hook"
status: proposed
date: 2026-07-13
addresses: [REQ-002]
tags: [creation, gitignore, hooks, portability]
---

## Motivation

DEC-019 installs each space's own validator (`.claude/entity_lint.py`) and the PostToolUse validation hook (`.claude/settings.json`) at creation, and the design guarantees the hook "holds on any machine" because every space carries its own copy of the validator. That guarantee only holds if those files travel with the repository.

The `.gitignore` conventionally applied to a workspace repo ignores `.claude/` wholesale, so the validator copy and the hook configuration are excluded from version control and never reach a second machine — the deterministic-integrity mechanism ([[REQ-002]]) silently stops firing there. Surfaced by [[ISS-001]]: `index__synced-artifacts` was brought under git with a `.gitignore` that ignores `.claude/`.

## Sketch

- The `.gitignore` that space creation writes must keep the DEC-019 artifacts tracked. Either ignore `.claude/` selectively — e.g. `/.claude/*` with `!/.claude/entity_lint.py` and `!/.claude/settings.json` — or relocate the validator and hook outside `.claude/`.
- Whichever path, `.claude/settings.local.json` (machine-local Claude Code state) must stay ignored.

## Open questions

- Selective un-ignore inside `.claude/`, or move the validator and hook out of `.claude/` entirely?
- Is `.claude/settings.json` the right tracked home for a hook meant to be identical on every machine, given Claude Code also writes machine-local state under `.claude/`?
- Should the space's `CLAUDE.md` (DEC-019 step 4) be tracked or ignored? Some owners deliberately keep a space free of a `CLAUDE.md`.
