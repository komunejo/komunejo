---
id: DEC-015
entity: decision
title: Visibility is declared at the type level, from v0
status: accepted
date: 2026-07-12
addresses: [REQ-001]
---

Every document type the space knows is classifiable as public or private, and the classification is a property of the *type* — declared where the type is declared (the composition or report-type registration) — never of the individual instance. Rationale: the future public/private split of a synchronized multi-instance space must be mechanically expressible (ignore rules and sync rules match by pattern); per-instance flags make the split unenforceable by pattern and invite drift. A document that needs different visibility is a different document type, declared as such.
