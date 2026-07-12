---
id: DEC-009
entity: decision
title: The skill registration record is the invocation interface
status: accepted
date: 2026-07-12
addresses: [REQ-004]
---

Registering a skill produces a standardized record: what installed skill it wraps, its status here, what report type(s) it can generate in this space, what input it needs and what document it produces. Orchestrators consult these records — invocation is a registry lookup, never improvisation over skill descriptions. Constraints a skill’s contributions carry (e.g. sections that must not be retired from compositions) are declared in its record as data each space manages, not hardcoded in kernel operations. Registration verifies the wrapped capability exists on disk; that correspondence stays outside the hard contract and is auditable on demand.
