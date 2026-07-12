---
id: DEC-004
entity: decision
title: Ship on_unresolvable=block as the constitution of every generated space
status: accepted
date: 2026-07-12
addresses: [REQ-006]
---

Generated spaces get `policy.on_unresolvable: block` without being asked at creation: the kernel’s contracts are deliberately thin, so red is rare, local, and always a real question for a human. `relax-and-report` would hand a non-technical owner’s agent the power to loosen the contract — exactly the silent drift the engine exists to eliminate. A technical owner can change the policy in their space’s `entity-manager.yaml` afterward.
