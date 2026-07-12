---
id: DEC-014
entity: decision
title: Skill installation mode is a recorded fact of each registration
status: accepted
date: 2026-07-12
addresses: [REQ-002, REQ-004]
---

A registered skill’s files live somewhere, and the Skill record says where: `installation: space` (the files are copied into the space’s own `.claude/skills/` — the default, because the space stays self-contained and portable) or `installation: user` (the capability already exists at the user level and is referenced without duplication — accepted on request, with the consequence recorded: the space is no longer self-sufficient on another machine until that skill is installed there). The capability audit checks presence at the declared source, whichever it is. No third mode: a skill either travels with the space or is declared external, never both and never implicitly.
