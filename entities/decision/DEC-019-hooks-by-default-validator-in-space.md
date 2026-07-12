---
id: DEC-019
entity: decision
title: Validation hooks are installed by default; each space carries its own validator copy
status: accepted
date: 2026-07-12
addresses: [REQ-002, REQ-003]
---

Creation installs the engine's PostToolUse validation hook in every space by default, replacing the original "offered, not imposed" stance. Two reasons: the offer forces the owner to understand what a validation hook is — exactly the vocabulary creation promises to avoid ([[REQ-003]]) — and automatic firing is what makes integrity independent of anyone's discipline ([[REQ-002]]).

To keep the hook portable, creation copies the engine's single-file validator (`entity_lint.py`) into the space itself (`.claude/entity_lint.py`): the hook references a stable in-space path and the space validates on any machine, whatever path the plugin is installed at — the same self-containment reasoning that made `space` the default installation mode ([[DEC-014]]). The copy pins the engine version the space was born with; refreshing it is a deliberate act, the per-space application of [[DEC-018]]'s discipline.
