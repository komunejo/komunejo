---
id: DEC-021
entity: decision
title: "The generated .gitignore shares consciously: CLAUDE.md and the space's machinery travel"
status: accepted
date: 2026-07-13
addresses: [REQ-002, REQ-006]
tags: [creation, gitignore, portability]
---

The `.gitignore` creation writes (`kernel/space-gitignore`) is a full baseline — OS artifacts, editor state, language caches, secrets — plus a deliberate policy for `.claude/`: default-deny (`.claude/*`) with explicit exceptions for `.claude/settings.json` and `.claude/skills/`. What the space shares, it shares consciously: anything new that lands in `.claude/` stays local unless deliberately excepted, and machine-local state (`.claude/settings.local.json`) is ignored without needing to be named. The exceptions are not a local invention: Claude Code's own documentation designates `.claude/settings.json` as the settings file "checked into source control and shared with your team" — hooks included — with `settings.local.json` as its untracked counterpart.

Default-deny on contents (`.claude/*`), not on the directory (`.claude/`), is load-bearing: git cannot re-include a file whose parent directory is excluded, so exceptions under an excluded directory would be dead letters.

The space's `CLAUDE.md` is tracked. It exists precisely so the space behaves predictably for every collaborator, and it can only do that if every collaborator reads the same contract. This resolves the systemic defect PROP-001 recorded (surfaced by ISS-001, where a hand-written `.gitignore` following the ignore-`.claude/`-wholesale convention silently stopped the integrity mechanism from traveling).
