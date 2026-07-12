---
name: skill-manager
description: >-
  Manages a collaboration space's capabilities and their derived views. Use this skill inside a komunejo collaboration space (a folder with entities/, schemas/, and an entity-manager.yaml) whenever a capability is registered, retired, refreshed, or audited, or the space's README needs regenerating. Trigger for: adding a skill to the space ("install this skill here", "I want this space to be able to X", a repository URL or local skill files offered for the space); retiring or suspending a registered capability; checking that registered capabilities actually exist on disk (capability audit); refreshing a section from its skill's upstream material; and regenerating the space's README after any registration change. Do NOT trigger for creating a new space (that is the interviewer's) or for plain record operations on domain entities (that is entity-management's).
---

# Skill manager

Operates a space's skill registrations end to end and keeps the views derived
from them fresh. Every structured fact goes through the entity-management
engine; this skill never writes frontmatter by hand and never edits the
engine.

Space-facing text — record bodies, section content, the README, anything the
owner reads — is written in the space's working language (the `language` field
of the profile record). This document's English is for the agent only.

## The registry is the interface

A capability exists in the space when its skill record exists (`entities/skill/`).
The record says what it wraps, where its files live (`installation`), what
document types it generates, what input it needs, and what it produces.
Invocation is a registry lookup: to run a capability, read its record — never
improvise over skill descriptions. Constraints a skill's contributions carry
(e.g. `protected_sections`: sections that must not be retired from
compositions) are data in its record, managed per space.

## Registering a skill

1. **Reach the source.** A repository (clone or fetch it), or local files. If
   the source is ambiguous, ask; never guess a repository.
2. **Read what it ships.** The skill's SKILL.md, and any report material it
   provides (sections, document types).
3. **Install per mode** — the mode is a recorded fact (one of two, never both,
   never implicit):
   - `space` (default): copy the skill's files into the space's own
     `.claude/skills/<name>/`. The space stays self-contained and portable.
   - `user`: the capability already exists at the user level
     (`~/.claude/skills/<name>/`) and is referenced without duplication.
     Accepted on request only; record the consequence in the record body: the
     space is not self-sufficient on another machine until that skill is
     installed there.
4. **Record the facts through the engine.** Use
   `${CLAUDE_PLUGIN_ROOT}/skills/entity-management/scripts/entity_lint.py new`
   to scaffold, then fill:
   - a **skill** record (`title`, `wraps`, `installation`, `source`, `status:
     active`, `generates`, `input`, `output`);
   - a **composition** record per document type the skill introduces
     (`visibility` is declared here, at the type level — ask the owner if the
     material does not state it);
   - a **section** record per unit of shipped report content, `provenance:
     skill`, body adapted to the space's language at registration time. The
     adapted body belongs to the space from then on.
5. **Verify the wrapped capability exists on disk** at the declared location.
   This correspondence stays outside the hard contract; state what was checked.
6. **Validate.** `entity_lint.py validate` green is the completion criterion
   of every registration operation. On red, fix or surface — never report a
   registration complete without it.
7. **Regenerate the README** (below).

## Retiring a skill

Set the record's `status` to `retired` (through the engine), decide with the
owner what happens to the sections it contributed — sections listed in any
skill's `protected_sections` are not retired from compositions — then
validate and regenerate the README. Files installed in the space are removed
only if the owner asks.

## Refreshing a section from its skill

Upstream improvements never rewrite an adapted section silently. On request:
re-read the skill's shipped material, re-adapt, show the owner what changes,
and only then update the section body through an ordinary edit. The change is
its own history entry (git); validate afterward.

## Capability audit

On demand, and honestly labeled as assisted review: for every skill record
with `status: active`, check the wrapped skill is present at its declared
location (`.claude/skills/` of the space for `installation: space`, the user
level for `installation: user`). Report presence and absence record by
record; absence is a finding for the owner, not something to repair silently.

## README regeneration

The README is the space's map, derived from the registry like any other view —
regenerated, never hand-edited. Fired by every registration change; also
available on demand. Build it, in the space's language, from:

- **What this space is** — from the profile record (name, focus, perspective)
  and the agreements in its body.
- **How it is laid out** — the registry, the derived views, where domain
  documents live.
- **Workflows** — what each document type is and how it is produced (from
  composition records and the sections they order).
- **The command map** — for each active skill record, one or two example
  phrases the owner can say to launch it, written in the space's language,
  derived from what the record declares it generates and needs.

The entity index is regenerated with `entity_lint.py index` at the location
the space prefers (`index --write <path>`; the folder-note form
`entities/entities.md` keeps it Obsidian-friendly).

## Rules that never bend

- Every record operation goes through the engine; green from `validate` is
  the only claim of integrity.
- Schema changes are never silent: `schemas/CHANGELOG.md`, and the contract
  policy is the space's (`block` unless its owner changed it).
- The engine (`entity-management`) is never edited — not in the plugin, not
  in a space.
- Nothing is committed to git without the owner's explicit confirmation.
