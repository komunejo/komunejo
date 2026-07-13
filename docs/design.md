# Komunejo — kernel design

Architectural narrative of the komunejo plugin. The decisions and requirements themselves are typed records in `entities/` (see the index at `entities/entities.md`), validated by this project’s own engine; this document is the connective prose and cites them by ID. Open questions are listed at the end and are the owner’s to close.

## What komunejo is

A Claude Code plugin that creates and maintains **collaboration spaces**: one directory per space, under git, where humans and their agents collaborate in natural language while the structured facts underneath — who, what, in which state, related how — live as typed records validated by a deterministic engine. Humans and agents keep working in prose; the space never depends on either’s memory or discipline for its integrity.

The kernel serves *any* human–agent collaboration: a peer-review group, a personal Zettelkasten, a research log. Domains are **particularizations** added on top (see below); the kernel itself knows nothing about any of them.

## Foundations

- **The engine is the bundled `entity-management` skill** (DEC-001; vendored, MPL-2.0). Schemas as per-project YAML data, records as Markdown files with typed YAML frontmatter and free prose bodies, a deterministic validator (`entity_lint.py`), stable IDs (`<PREFIX>-NNN`), typed refs, aggregate constraints, first-class schema evolution (`schemas/CHANGELOG.md`), explicit contract policy. Komunejo never forks the engine; improvements go upstream.
- **Hard vs soft integrity, honestly separated.** Types, required fields, enums, refs, uniqueness: guaranteed by the validator — never claimed from memory. Everything else (prose consistency, record-to-installed-capability correspondence, operation-level rules) is assisted review, labeled as such.
- **Contract policy is `block`, shipped as the constitution of every generated space** (DEC-004). The contract is deliberately thin — a handful of required fields, the collaboration’s prose outside it — so red is rare, local to the violating record, and always a real question for a human. `relax-and-report` (the agent may loosen the contract, documented) is not offered at creation: for a non-technical space owner it reintroduces exactly the silent drift the engine exists to eliminate. A technical user can change the policy in `entity-manager.yaml` afterward.
- **Dependencies of a generated space**: Claude Code, git, Python 3.8+ with PyYAML (DEC-005); stated at creation, no degraded no-Python mode.

## The four kernel entities

The kernel installs exactly four entity types (DEC-002). Everything else arrives later as particularization.

1. **Profile** (DEC-012) — the collaboration’s configuration: its name, working language, focus (what this space is about, in the owner’s words), whose perspective the space materializes, and status (active/paused/closed). Prose bodies carry what the collaboration writes about itself — agreements, conventions, anything the schema should not capture. One record per space.
2. **Skill** — a registered capability. Registering a skill in the space is an act with a record: which installed skill it wraps, its status here, **what report type(s) it can generate in this space**, what input it needs (a file, a record, a prior report) and what document it produces. The skill record is the interface the orchestrator consults — invocation resolves through the registry, never through improvisation over skill descriptions. Constraints a skill’s contributions carry (e.g. sections that must not be retired from compositions) are declared *in its record*, as data each space manages, not hardcoded in kernel operations.
3. **Section** — a unit of composable report content: its provenance (backed by a registered skill’s shipped material, or drafted from the owner’s own description — typed, so honest labeling is structural), the document type it belongs to, and, as its body, the section content itself, adapted to the space’s language at registration time. The adapted body belongs to the space: upstream improvements to a skill’s material never rewrite it silently; refreshing a section from its skill is a deliberate operation with its own history entry.
4. **Composition** — a document type assembled from sections: its content is the *ordered list of refs* to section records. Order lives here (native list of refs, engine-validated), not as fields scattered across sections. Producing a document of some type means reading its composition, loading the referenced sections’ skills, and writing the document — the composition is data, so “how documents are produced here” is uniform, queryable, and has history.

Derived views are regenerated, never hand-edited: the engine’s entity index (its location is a per-space preference; the folder-note form `entities/entities.md` keeps the registry Obsidian-friendly), and the space’s `README.md` (see below).

## Space creation (minimal by design)

Creation asks only what the kernel’s schemas require and cannot derive — the required fields of Profile (name, language, focus) plus the location, resolved conversationally (propose a parent folder, never a directory holding unrelated work, no filesystem vocabulary unless the owner speaks it first). Then:

1. Skeleton: the directory, `git init`, `.gitignore`.
2. Registry installation: `schemas/` (the four kernel types), `entity-manager.yaml` with `policy.on_unresolvable: block`, the Profile record, and whatever initial Skill/Section/Composition records the installing plugin seeds.
3. The space’s own machinery and its firing (DEC-020): the kernel skills that operate the space (`entity-management`, `skill-manager`) copied into `.claude/skills/`, and the engine’s PostToolUse validation hook installed in `.claude/settings.json`, firing the validator bundled inside the copied engine — by default, never as an option the owner must understand to accept.
4. `README.md` and `CLAUDE.md` for the space.
5. **`validate` green is the completion criterion** (DEC-003). Not a bespoke verification gate: the engine’s exit code.

Immediately after creation, a fixed message tells the owner: the space already works; certain data will make it more useful — and can be provided now or at any later moment. Nothing beyond the required minimum is interviewed at creation. There is no separate “reconfiguration” flow: changing the space *is* editing records and regenerating their derived views.

Fixed messages (plan-mode notice and exit plan, the post-creation notice) are verbatim interface text: never paraphrased, translated faithfully per conversation language. Their English templates live in `docs/fixed-messages.md`; their implementation home is the interviewer skill.

Generation runs in the main conversation through the kernel’s skills — there is no generation agent (DEC-006). The engine does the mechanics (`new`, `validate`); the conversation does the talking.

## Kernel skills

Three, no more (DEC-013): the **engine** — the vendored `entity-management` skill, relied on for every record operation, always an exact copy of a tagged upstream release (DEC-018); the **skill manager** — the space’s capabilities and their derived views: registration end to end — reach the source (a repository, local files), hand the structured facts to the engine, install the capability per its recorded installation mode (DEC-014) — and README regeneration, fired by registration changes (DEC-017); and the **interviewer** — general-purpose conversational intake whose interview definitions are per-space data, with space creation as its first configuration.

The engine and the skill manager operate spaces, so creation copies both into each space’s `.claude/skills/` (DEC-020) — the kernel applies to itself the `space` installation mode DEC-014 made the default. The interviewer serves creation, not operation, and stays in the plugin: the plugin is needed to create a space, never to work in one.

## Particularization

Two paths, both landing in the same registry (DEC-008):

- **Construction with the user.** The space needs to track something new (“I want to keep my sources as records”); the conversation designs the schema with the engine’s own init workflow (propose fields, meta-validate, changelog) and the entity enters the space’s registry. The engine already does this well; the kernel adds nothing but the discipline.
- **Plugins on the plugin.** A domain package — e.g. a peer-review workshop particularization — ships ready-made schemas, seed records, skills, and operations. Installing it registers its skills and installs its schemas. Ingestion can also start from a pointer: a skill repository URL or a modeling document describing what to track.

Particularization is **lazy**: domain entities are installed when the domain first needs them, not at creation. A space grows where use pushes it.

## The space’s README

The README is the space’s map, derived from the registry like any other view: what this space is (from Profile), how it is laid out, the workflows available, and — because skill records declare what they produce and how they are consulted — the **command map**: example phrases the owner can say to launch each operation, written in the space’s language. Instructions, workflows, and references (links to the records that matter, the agreements in Profile’s body included) in one visible file. No configuration dotfile exists: typed facts live in records, the collaboration’s prose lives in record bodies, orientation lives in the README.

Regeneration is the skill manager’s (DEC-017), fired by registration changes; as backstop, the space’s `CLAUDE.md` instructs that after any significant structural edit the README is checked against the registry and regenerated if stale.

## Validation firing points

- After any change to `schemas/` or `entities/` (the engine’s golden rule).
- As the completion criterion of creation and of every registration/edition operation.
- Automatically, via the engine’s PostToolUse hook, installed in every space at creation (DEC-020); each space carries its operating skills — validator included — under `.claude/skills/`, tracked by its `.gitignore` (DEC-021), so the hook holds on any machine, plugin installed or not.

## What the kernel deliberately does not do

- No domain vocabulary, no domain entities, no domain operations.
- No imposed structure on communication or working areas a space may create around the registry; records assert only what the registry can back.
- No silent schema changes, no fabricated values, no green claimed from memory — inherited verbatim from the engine’s constitution.

## Open questions (the owner’s)

None at the moment. New ones enter the record backlog (`entities/`) as proposed decisions, not this list.
