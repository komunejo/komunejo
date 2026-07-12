# Schema language specification

Schemas are YAML declarations, one file per entity type, living in `schemas/<type>.yaml` (`.yml` is also accepted). The engine (`entity_lint.py`) meta-validates the schemas themselves before validating any record, so a typo in a schema is caught the same way a typo in a record is — including keys that do not apply to a field's type (a `pattern` on an integer, a `max` on an enum), which are rejected rather than silently ignored.

## Contents

- [Project configuration](#project-configuration)
- [Schema file](#schema-file)
- [Field types](#field-types)
- [Aggregate constraints](#aggregate-constraints)
- [Record file format](#record-file-format)
- [Inline references in prose](#inline-references-in-prose)
- [YAML pitfalls the engine catches](#yaml-pitfalls-the-engine-catches)
- [Design guidance](#design-guidance)

## Project configuration

`entity-manager.yaml` at the project root, optional. Defaults:

```yaml
schemas_dir: schemas
entities_dir: entities
policy:
  on_unresolvable: block    # block | relax-and-report
```

`policy.on_unresolvable` is the project's contract policy, chosen explicitly by the user when the first schema is created (see [`SKILL.md`](../SKILL.md), "When the contract cannot be satisfied"). `block` means the contract is untouchable and unresolvable records are surfaced as an honest red; `relax-and-report` allows the agent to loosen the contract, always documented in `schemas/CHANGELOG.md` and reported. When the key is absent, behave as `block`. Schema changes are never silent, under either policy.

The engine finds the project root by walking upward from the current directory until it sees `entity-manager.yaml` or a `schemas/` directory; `--root` overrides.

## Schema file

```yaml
entity: decision            # must match the filename (decision.yaml)
description: >              # optional, for humans and agents
  What this entity type represents.
id:
  prefix: DEC               # unique across ALL schemas in the project
  width: 3                  # MINIMUM digits, zero-padded: DEC-001 (default 3); more digits are accepted as the registry grows past 999
dir: decision               # subdirectory under entities/ (default: entity name; must be unique across schemas)
# path: registry/decision   # optional: project-root-relative home for this type's records,
                            # overriding entities/<dir>. No '..'; locations must be unique
                            # across schemas and must not nest inside one another.
strict: true                # unknown frontmatter fields are errors (default true); with strict: false they are warnings, which never affect the exit code
fields:
  title:    {type: string, required: true}
  status:   {type: enum, values: [proposed, accepted, superseded], required: true}
  date:     {type: date, required: true}
  supersedes: {type: ref, entity: decision}
  addresses:  {type: list, items: {type: ref, entity: requirement}}
  weight:     {type: number, min: 0, max: 1}
```

`id` and `entity` are reserved record fields added automatically — do not declare them in `fields`.

## Field types

| type | accepts | extra keys |
|---|---|---|
| `string` / `text` | YAML string | `pattern` (full-match regex) |
| `integer` | integer (not boolean) | `min`, `max` |
| `number` | integer or float | `min`, `max` |
| `boolean` | true / false | |
| `date` | unquoted `YYYY-MM-DD` (a YAML date, not a string) | |
| `datetime` | unquoted ISO 8601 date or datetime | |
| `enum` | one of `values` | `values` (required, non-empty list) |
| `ref` | the ID of an existing entity of type `entity` | `entity` (required) |
| `list` | YAML list; every item validated against `items` | `items` (required field spec, may itself be a `ref`) |

Every field also accepts `required: true` (default false), `description`, and `default` (documentation only — the engine does not inject defaults; absent optional fields are simply absent).

Refs are checked at two levels: the schema's `entity` target must be a declared entity type (meta-validation), and each record's value must resolve to an existing ID of exactly that type.

## Aggregate constraints

Field specs constrain one record at a time. Some rules live *between* records ("a piece can only be submitted once", "at most 3 submissions per student") — declare those in an optional `constraints` list on the schema, and the engine enforces them project-wide on every `validate` run:

```yaml
constraints:
  - rule: unique
    fields: [piece]
    description: a piece can only be submitted once
  - rule: max_count_per
    group_by: piece.student
    max: 3
    description: at most 3 pieces per student; participation is voluntary
```

`unique` requires the combination of the listed field values to be unique among this entity's records (records where any listed field is absent are skipped, so optional fields work naturally); the reserved field `id` may be included in the combination. `max_count_per` groups this entity's records by the value of `group_by` and errors when a group exceeds `max`; `group_by` may be a dot-path that hops through `ref` fields (`piece.student` = "the student of the referenced piece"), and records whose path does not resolve are skipped — absence never violates an aggregate constraint, which is what makes voluntary participation modelable. Both rules accept an optional `description` that is echoed in the error message.

Constraint declarations are meta-validated like everything else (unknown rules, undeclared fields, paths through non-ref fields are reported), and an invalid constraint is pruned with an error rather than disabling the whole schema. The vocabulary is deliberately small and implemented once in the engine — if a rule cannot be expressed with it, document the rule in the schema `description` and handle it as soft integrity (assisted review), never with a per-project bespoke validator.

## Record file format

`entities/<dir>/<ID>-slug.md` — or `<path>/<ID>-slug.md` when the schema declares `path`. The filename must start with the ID.

```markdown
---
id: DEC-001
entity: decision
title: One file per entity
status: accepted
date: 2026-07-12
addresses: [REQ-002, REQ-003]
---

Free prose. Everything the schema cannot capture lives here, including
inline links to other entities like [[REQ-002]] or [[DEC-004|that decision]].
```

Rules enforced by the engine: frontmatter parses and is a mapping; `id` is present, unique project-wide, matches `<prefix>-<at least width digits>` and the filename; `entity` matches the schema implied by the directory; required fields present; all values type-check; refs resolve to the right type; undeclared fields are errors in `strict` schemas and warnings otherwise.

**Folder notes are not records.** A Markdown file named exactly like its own directory (`entities/entities.md`, `registry/skill/skill.md`) is treated as an Obsidian folder note and skipped by record discovery — the natural home for the generated index in vault projects. The exemption is exact-name-only; any other `.md` outside a declared entity location still errors.

## Inline references in prose

`[[DEC-001]]` and `[[DEC-001|display text]]` in the body are validated: the prefix must belong to a declared entity type and the ID must exist. Fenced code blocks (``` … ```) are skipped, so examples never trigger false errors.

## YAML pitfalls the engine catches

These are the reasons "YAML + Markdown" needs a linter at all:

- `title: yes` → YAML parses a **boolean**, not the word "yes". The engine reports the type mismatch with a hint to quote the value.
- `date: 2026-07-12` unquoted is a date; `date: "2026-07-12"` quoted is a string. `date`-typed fields require the real date, so a quoted one errors.
- `version: 1.0` is a float — declare `string` and quote it if you mean a version label.
- Indentation errors and tab characters produce YAML parse errors, reported per file rather than crashing the run.

## Design guidance

Model only the facts that must not drift. A field earns its place in the schema when (a) more than one document depends on it, (b) an agent might plausibly get it wrong from memory, or (c) you want to query or index by it. Everything else is prose — that is a feature, not a failure of modeling: the prose is the interface, the schema is the safety net. Prefer `enum` over free `string` wherever the vocabulary is closed; enums are where drift dies. Prefer one `ref` field per relation over encoding relations in prose alone; you can (and should) still mention the relation in prose with `[[ID]]`, which keeps human readability and gets validated too.
