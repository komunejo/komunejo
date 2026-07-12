---
id: REQ-006
entity: requirement
title: A space's contract never changes silently
status: open
priority: must
date: 2026-07-12
---

Schema evolution in a space is first-class and always documented: every change lands in the space’s schema changelog, and no agent loosens the contract to keep work flowing ([[DEC-004]]). Inherited verbatim from the engine’s constitution; the kernel must preserve it in every space it generates.
