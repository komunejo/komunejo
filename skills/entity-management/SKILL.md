---
name: entity-management
description: >-
  Use this skill whenever Markdown files with YAML frontmatter act as a registry of typed records — ADRs, requirements, vendors, clients, NPCs, characters, or any entities — and the user wants those records created, kept consistent, validated, migrated, queried, or reported on. Trigger for: enforcing a schema/template with required fields; checking the structural consistency of a project's documents; validating cross-references between files; migrating or renaming fields across many records; enforcing rules like "at most N per group"; fixing drift or contradictions across a wiki, Obsidian vault, or campaign notes; bulk-creating records from CSV rows; generating indexes or CSV exports; and computing reports FROM the records (totals, per-person or per-date listings) even when the user just calls them "the records" or "the notes". Queries may arrive in any language. Do NOT trigger for real databases (SQL/ORM), JSON Schema validation, blog frontmatter rendering, or one-off prose.
---

# Entity Management

Give Markdown-based projects the integrity guarantees of a database without giving up natural language as the working interface. Humans and agents keep collaborating in prose; underneath, typed records are validated deterministically.

## Core model

Three layers with different life cycles — keep them separate:

1. **Engine** (`scripts/entity_lint.py`) — generic, domain-agnostic, stable. It reads schema declarations and validates records. Never rewrite it per project and never regenerate it when schemas change: a bug in the validator is worse than a bug in the data, because it corrupts trust in the whole system.
2. **Schemas** (`schemas/*.yaml`) — data, not code. One YAML declaration per entity type. Redesigning the model means editing declarations.
3. **Records** (`entities/<type>/<ID>-slug.md`) — one Markdown file per entity. YAML frontmatter is the typed record; the body is free prose.

Two kinds of integrity — be honest about the difference:

- **Hard integrity** (types, required fields, enums, unique IDs, resolvable references) is *guaranteed* by the engine. Never claim documents are consistent from memory — run the validator and let its output be the claim.
- **Soft integrity** (contradictions inside prose) cannot be caught by a schema. Offer the review workflow below, and present its results as review, not guarantee.

## Project layout

```
project-root/
├── entity-manager.yaml      # optional config (defaults shown inside)
├── schemas/
│   ├── decision.yaml        # one schema per entity type
│   └── requirement.yaml
└── entities/
    ├── decision/
    │   └── DEC-001-frontmatter-as-record.md
    └── requirement/
        └── REQ-001-user-definable-schemas.md
```

Entities are referenced by stable IDs (`DEC-001`), never by names or titles — renames are the great destroyer of coherence in Markdown. Each type has a unique ID prefix. Frontmatter refs (`supersedes: DEC-001`) are typed and validated; prose can link entities inline as `[[DEC-001]]`, also validated.

A schema may relocate its records anywhere in the project with the optional `path` key (project-root-relative; see the schema language reference) — useful to separate, say, an instance's management records from the owner's working records. The default layout above needs no declaration.

Read [`references/schema-language.md`](references/schema-language.md) before writing your first schema — it is the full specification (field types, aggregate constraints like `unique` and `max_count_per`, YAML pitfalls like unquoted `yes` becoming a boolean). Rules that live between records ("at most 3 per student") belong in the schema's `constraints` list, enforced by the engine — never in a per-project bespoke validator.

## The golden rule

After ANY change to `schemas/` or `entities/` — yours or the user's — run:

```bash
python3 <skill-path>/scripts/entity_lint.py validate --root <project-root>
```

Exit 0 means integrity holds; exit 1 comes with a precise list of violations; exit 2 means the run itself was invalid (no project root, missing PyYAML, a path filter that matched nothing) — never read exit 2 as "no violations". You can restrict record checks to specific files with `validate <paths...>` (aggregate constraints still run project-wide). Fix every error and re-run until green. Use `--json` when you need to act on the output programmatically. Do not report a task as done while the validator fails. If hooks are installed (see [`references/hooks.md`](references/hooks.md)), the validator also fires automatically after every file edit — treat its failures as blocking.

## Workflows

### Initialize a project

1. Ask the user (or infer from the conversation) which entity types the project needs, which facts about each must stay consistent (those become schema fields), and which relations exist between types (those become refs). Prefer few fields that matter over exhaustive modeling: anything that can live happily as prose should stay prose.
2. Before creating the FIRST schema, explicitly ask the user which contract policy the project follows (see "When the contract cannot be satisfied" below) and record the answer in `entity-manager.yaml`. This is the project's constitution — do not guess it.
3. Create `schemas/<type>.yaml` for each type, `entities/<type>/` directories, `entity-manager.yaml`, and start `schemas/CHANGELOG.md` with an entry for the initial schema set.
4. Run `validate` — it must pass on the empty project.
5. Offer to install hooks ([`references/hooks.md`](references/hooks.md)).

### Create a record

1. Never invent IDs by hand — allocate with: `python3 .../entity_lint.py new <type> --title "..." --root <root>`. It prints a stub with the next free ID (stub on stdout, suggested file path on stderr).
2. Fill in the frontmatter from what the user said, in their words. Put everything schema-shaped in the frontmatter; put everything else in the prose body. Link related entities inline as `[[ID]]`.
3. Run `validate`.

### Bulk-create records from CSV / spreadsheet rows

1. Agree the column-to-field mapping with the user before writing anything: which column is the title, which map to enums (and how the spreadsheet's spellings map to the declared `values`), which columns are refs to other entities, and which stay out of the schema entirely. A wrong mapping multiplied by N rows is N migrations — settle it while it is still one decision.
2. Import referenced types first: if rows point at entities that do not exist yet (a `student` column naming people with no person records), create those records before the rows that reference them, or the refs cannot validate.
3. Allocate the ID block deterministically: run `new <type>` once to learn the next free ID, then number the rows sequentially from it inside the import script. Do not call `new` once per row without writing the previous file first — it computes the next ID from records on disk, so repeated calls against an unchanged project return the same ID every time.
4. Write the files with a throwaway script, never by hand: parse the source (Python `csv` module), emit one `entities/<dir>/<ID>-slug.md` per row with frontmatter from the mapped columns, and put leftover meaningful cells in the prose body. Quote values YAML would mistype (`yes`, `no`, version numbers, anything with leading zeros); leave real dates unquoted.
5. Run `validate`. The error list is the per-row repair worklist: fix mappings and re-run until green, ask the user for missing facts instead of fabricating them, and never repair by silently dropping rows — a row that cannot be imported is reported, not deleted.
6. Report how many records were created, where, and the final validator status.

### Generate an index, summary, or CSV export

For the standard index, use the engine: `entity_lint.py index --write <path> --root <root>` regenerates the full per-type table (ID, title — falling back to `name` — and file link). The index may live at any path the project prefers — links adapt to its location; `INDEX.md` at the root is the plain default, and the Obsidian folder-note form (`entities/entities.md`) is a natural home when the project is a vault. Always regenerate, never hand-edit: the file declares itself generated, and hand edits are lost on the next run.

For CSV exports or custom summaries (selected columns, filters, groupings), run `validate` first — an export of an invalid registry ships the corruption to everyone who reads it. Then produce the export with a small deterministic script that walks `entities/`, parses each record's frontmatter with PyYAML (the same parse the engine uses), and writes the output with the `csv` module. Never assemble exports by eyeballing files: a copying mistake in an export is invisible exactly where the registry was supposed to be reliable. Include the record ID in every exported row so each claim stays traceable to its file.

### Answer questions / compute reports from the records

1. Run `validate` first and state the result in the report — totals computed over an inconsistent registry are wrong before the query starts. Use `--json` when the report should embed the integrity status programmatically.
2. Compute, don't recall: answer totals, per-person or per-date listings, and who-is-up-to-date questions with a throwaway script over the frontmatter (walk `entities/`, `yaml.safe_load` each frontmatter block, aggregate). `entity_lint.py index` suffices when the question is only "what exists"; anything involving filtering, counting, or grouping deserves the three-line script, because eyeballed counts across dozens of files are exactly the drift this skill exists to prevent.
3. Keep the two evidence classes separate: figures derived from frontmatter are validator-backed hard integrity; anything read from prose bodies is assisted review — label it as such, exactly as in the soft-integrity workflow.
4. Cite record IDs for every figure and every listed row, so the user can audit any line of the report against the file it came from.

### Evolve a schema (migration)

Schemas are always evolving; this is the normal case, not the exception.

1. Edit the schema declaration(s) to the new design.
2. Run `validate`. Every error now listed IS the migration worklist — the records that no longer conform.
3. Migrate each listed record: fill new required fields (from the prose body or by asking the user — do not fabricate values), map renamed enum values, update refs. The agentic part is the migration; the deterministic part is the verification.
4. Re-run `validate` until green — or, if some records are unresolvable, follow the project's `on_unresolvable` policy (see below).
5. Append an entry to `schemas/CHANGELOG.md` (date, what changed, why, who) — this applies to every schema modification, no exceptions. Also record the change as an entity if the project tracks decisions.

### When the contract cannot be satisfied

Sometimes a record violates the schema and no available truth can fix it — a required field nobody knows the value of, a reference to something never registered. What happens next is a *project-level* decision, declared in `entity-manager.yaml`:

```yaml
policy:
  on_unresolvable: block            # or: relax-and-report
```

- **`block`** (the default when unset): the contract is untouchable. Leave validation red, list every record that cannot be managed without human intervention, and surface that list prominently. An honest red is the deliverable.

  Under `block`, apply the mixed rule to decide what is actually unresolvable. A violation whose repair requires NO new fact — a broken ref in an OPTIONAL field, a dangling inline `[[ID]]` — is repaired by demoting the claim to prose with a note and a pending question for the user: the information survives, the structure stops asserting what the registry cannot back, and the result is green. Red is reserved for violations that require a fact nobody has (a missing REQUIRED field, a required value with no evidence). This keeps red meaningful: every red item is a real question for a human, not a typo.

- **`relax-and-report`**: the agent may loosen the contract to keep work flowing (e.g. make a field optional), but the change must be documented in `schemas/CHANGELOG.md` and reported prominently to the user, with what is pending to restore it.

Under either policy, two things are absolute. Never fabricate a value to turn red into green. And NEVER change a schema silently: every schema modification — made by the agent *or* noticed as made by the human — gets an entry in `schemas/CHANGELOG.md` (date, what changed, why, who), and a mention in your report. A silently negotiated contract is worse than a violated one, because it corrupts trust in every green result after it.

### Rename / refactor

To rename an entity's *title* or file slug: IDs never change, so update the title field and optionally the filename slug (keep the `<ID>-` prefix), then run `validate`. To retire an entity, prefer a status field (e.g. `superseded`) over deletion — deleting breaks inbound references, and the validator will list every one of them if you try.

### Soft-integrity review (on request)

When asked to check consistency beyond structure ("does the prose contradict the records?"):

1. Run `validate` first — hard integrity is the foundation.
2. Generate the overview: `entity_lint.py index` gives all entities at a glance.
3. For each entity (or the subset in question), read the prose body and compare its claims against its own frontmatter and against the records it references. Report contradictions with file and quote.
4. Label the result as assisted review, not guarantee.

## Bundled resources

- [`scripts/entity_lint.py`](scripts/entity_lint.py) — the engine. Run it; do not modify it per project. Requires Python 3.8+ and PyYAML (`pip install pyyaml`).
- [`references/schema-language.md`](references/schema-language.md) — full schema + record format specification. Read when authoring or evolving schemas.
- [`references/hooks.md`](references/hooks.md) — automatic validation: Claude Code hooks, conversational triggers, optional git pre-commit. Read when setting up a project or when the user asks for automatic checks.
