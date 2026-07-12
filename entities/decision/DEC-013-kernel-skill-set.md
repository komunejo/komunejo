---
id: DEC-013
entity: decision
title: The kernel ships three skills, no more
status: accepted
date: 2026-07-12
addresses: [REQ-002, REQ-003, REQ-004]
---

1. **The engine** — the vendored `entity-management` skill ([[DEC-001]]): the space relies on it for every record operation.
2. **A skill manager** — operates skill registration end to end: reaches the source (a repository, local files), hands the structured facts to the engine (the Skill/Section/Composition records), and installs the capability into the space. Installation mode per [[DEC-014]].
3. **An interviewer** — general-purpose conversational intake, configured per space with the interview sections and messages it must deliver; the interview definition is data, not prose baked into the skill. Space creation is its first configuration.

No other kernel skill. One assignment still open: where the regeneration of the space’s README ([[DEC-010]]) lives — plausibly a skill-manager operation, since the README derives chiefly from skill registrations.
