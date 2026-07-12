---
id: DEC-018
entity: decision
title: The vendored engine is pinned to a tagged upstream release
status: accepted
date: 2026-07-12
addresses: [REQ-006]
---

The bundled `entity-management` skill ([[DEC-001]]) is always an exact copy of a tagged upstream release, with the pinned version recorded in this repository. Updating the copy is a deliberate act — new pin, changelog entry — never a silent refresh toward “latest.” The anti-silent-change constitution ([[REQ-006]]) applied to the engine itself.
