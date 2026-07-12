---
id: DEC-017
entity: decision
title: README regeneration is a skill-manager operation, with a CLAUDE.md backstop
status: accepted
date: 2026-07-12
addresses: [REQ-004]
---

The space’s README derives chiefly from skill registrations ([[DEC-010]]), so the skill manager owns its regeneration: registering, retiring, or editing a registration fires it. Its remit reads “the space’s capabilities and their derived views.”

Backstop: every generated space’s `CLAUDE.md` instructs that after any significant structural edit — schemas, registrations, compositions — the README must be checked against the registry and regenerated if stale. The trigger is the mechanism; the backstop catches what slips past it.
