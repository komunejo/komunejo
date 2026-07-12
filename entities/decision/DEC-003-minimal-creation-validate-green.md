---
id: DEC-003
entity: decision
title: Creation is minimal and completes on validator green
status: accepted
date: 2026-07-12
addresses: [REQ-002, REQ-003]
---

Creation resolves only Profile’s required fields (name, language, focus) plus the location, seeds the kernel records, and is done when `validate` exits green on the fresh space — the engine’s exit code is the completion criterion, not a bespoke verification gate. Immediately after, a fixed message tells the owner which data would make the space more useful and that all of it can arrive later. There is no separate reconfiguration flow: changing the space is editing records and regenerating derived views.
