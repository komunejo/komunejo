# entity-management skill changelog

The engine and skill evolve by versioned maintenance, never by per-project regeneration (DEC-002). Every engine or skill change gets an entry here, mirroring the discipline that schemas/CHANGELOG.md imposes on schemas (REQ-006).

## 0.4.0 — 2026-07-12

- Engine: `index --write` computes every link relative to the index file's own location (stdout falls back to the project root), so the index works at any path the project prefers (DEC-012).
- Engine: folder notes are never records — a Markdown file named exactly like its own directory (`entities/entities.md`, `registry/skill/skill.md`) is skipped by record discovery, letting the generated index live as the registry's folder note in vault projects; the exemption is exact-name-only and stray detection is otherwise unchanged (DEC-012).
- Engine: optional per-schema `path` (project-root-relative, no `..`, unique, non-nesting) places a type's records anywhere in the project, overriding `<entities_dir>/<dir>`; record discovery scans declared locations, `new` suggests the declared home, and the default layout needs no declaration (DEC-013).
- Docs: `path`, the folder-note exemption, and free index placement documented in the schema language reference and SKILL.md.

## 0.3.0 — 2026-07-12

- SKILL.md description compacted to the packager's 1024-char limit; trigger performance re-measured intact (26/26 on the bilingual eval set).
- Engine hardening after adversarial review (12 reproduced defects fixed, zero remaining crashes across the review fixture suite): UTF-8 BOM tolerated everywhere (`utf-8-sig`); non-UTF-8 files, invalid `pattern` regexes, non-numeric `min`/`max`, non-string config dirs and non-string `dir` now report errors instead of crashing; aggregate constraints no longer crash on list/dict values; duplicate `dir` across schemas rejected; `index` escapes `|` in titles and creates parent directories on `--write`; path filters resolve against the project root and a filter matching no record exits 2 instead of producing a false green.
- Stricter meta-validation: field keys that do not apply to the declared type (a `pattern` on an integer) are rejected rather than silently ignored.
- Docs: PostToolUse hook snippet corrected — feedback reaches the agent only via stderr + exit 2, the previously documented form was invisible to it; `--json` payload shape and exit codes (0/1/2) documented; `width` documented as minimum zero-padding; warnings semantics for non-strict schemas documented.
- SKILL.md: three workflows the description promised but the body never taught, now taught — bulk-create from CSV/spreadsheet rows, index/summary/CSV export generation, and computed reports/queries over the records.

## 0.2.1 — 2026-07-12

- SKILL.md description replaced after measured trigger optimization: 26/26 on a 26-query bilingual eval set (15 positive / 11 adversarial negative), vs 17/26 for the original. Leads with the registry-of-typed-records condition, enumerates lifecycle workflows including bulk CSV import, exports, and computed reports/queries over records, and carries explicit non-triggers (SQL/ORM, JSON Schema, blog frontmatter rendering, one-off prose).

## 0.2.0 — 2026-07-12

- Engine: aggregate constraints in the schema language — `unique` and `max_count_per` (with dot-paths through refs), enforced project-wide on every validate; meta-validated and pruned-with-error when misdeclared (DEC-009).
- Engine: `engine_version` included in `--json` output.
- SKILL.md: per-project contract policy `policy.on_unresolvable` (block | relax-and-report), asked explicitly at first-schema creation, default block (DEC-007); mixed rule defining "unresolvable" under block (DEC-008); schema changes always logged in schemas/CHANGELOG.md, never silent (REQ-006).

## 0.1.0 — 2026-07-12

- Initial release: generic validation engine (types, required, enums, unique prefixed IDs, typed refs, inline `[[ID]]` refs outside code fences), `validate` / `index` / `new` commands, schema language specification, hooks reference, workflows for init, record creation, migration, rename and soft-integrity review.
