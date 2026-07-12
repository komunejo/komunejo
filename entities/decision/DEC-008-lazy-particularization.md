---
id: DEC-008
entity: decision
title: Particularization is lazy, through two paths
status: accepted
date: 2026-07-12
addresses: [REQ-001, REQ-003]
---

Domain entities are installed when the domain first needs them, never at creation. Two paths land in the same registry: **construction with the owner** (design the schema conversationally with the engine’s init workflow) and **plugins on the plugin** (a domain package shipping ready-made schemas, seed records, skills, and operations; ingestion can start from a skill repository pointer or a modeling document).
