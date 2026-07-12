---
id: DEC-006
entity: decision
title: Creation runs in the main conversation; there is no generation agent
status: accepted
date: 2026-07-12
addresses: [REQ-003]
---

A generation agent earns its place when generation is large and drift-prone. The validator removes the drift risk and minimal creation ([[DEC-003]]) removes the size, so the structured handoff contract to a writing agent retires with both: the conversation talks, the engine (`new`, `validate`) does the mechanics.
