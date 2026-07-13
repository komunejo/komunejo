---
id: DEC-020
entity: decision
title: The space carries its operating skills; the hook fires their bundled validator
status: accepted
date: 2026-07-13
supersedes: DEC-019
addresses: [REQ-002, REQ-003]
tags: [creation, skills, hooks, portability]
---

DEC-019 copied only the validator into the space. That protected integrity but not capability: every record operation runs through the kernel skills, so a collaborator without the plugin could have their edits validated yet could not actually operate the space — and requiring a user-level plugin installation from every collaborator is a burden the space itself can remove.

Creation therefore copies the two kernel skills that operate the space — `entity-management` (the engine) and `skill-manager` — into the space's own `.claude/skills/`, the project-level skills location Claude Code documents. The kernel applies to itself the `space` installation mode that DEC-014 made the default for registered capabilities. The interviewer is not copied: it serves creation, not operation.

The PostToolUse hook in `.claude/settings.json` invokes the validator where it already lives, inside the copied engine (`.claude/skills/entity-management/scripts/entity_lint.py`) — no separate validator copy exists anymore. Skills and validator travel as one vendored unit, pinned at the engine version the space was born with (DEC-018 applied per space, unchanged), which removes the skew DEC-019 allowed between a pinned validator and floating plugin skills.

Consequence: a clone of a space is a working space — capability and integrity both — on any machine with git, Claude Code, and Python. The plugin is needed to create spaces, never to work in them.
