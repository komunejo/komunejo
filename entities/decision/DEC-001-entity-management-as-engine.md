---
id: DEC-001
entity: decision
title: Bundle the entity-management skill as the kernel's engine
status: accepted
date: 2026-07-12
addresses: [REQ-002, REQ-006]
---

The kernel does not build its own record machinery: it vendors the `entity-management` skill (MPL-2.0) — schemas as data, records as Markdown with typed frontmatter, deterministic validator, stable IDs, typed refs, aggregate constraints, first-class schema evolution. The engine is never forked or edited here; improvements go upstream and the vendored copy tracks upstream releases.

Accepted price: generated spaces depend on Python 3.8+ with PyYAML ([[DEC-005]]).
