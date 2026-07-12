# {space-name} — collaboration space

<!--
  komunejo template. English is the template's language only: at creation this
  file is written in the space's working language, faithfully translated and
  with the {placeholders} resolved. It ships with the space, so it must stand
  alone — no komunejo design vocabulary, no references back to the plugin's
  repository.
-->

This folder is a collaboration space. The structured facts underneath the
collaboration — who, what, in which state, related how — live as typed records
in `entities/`, validated by a deterministic engine. Everything else is prose.

## Language

This space speaks {language}. Every document, record body, and message to the
owner is written in it. Record frontmatter field names stay as the schemas
declare them.

## Working with records

- Records are created, edited, and validated through the entity-management
  skill — never by improvising frontmatter from memory.
- After any change to `schemas/` or `entities/`, run the validator; its exit
  code is the claim of integrity. Never report the registry consistent without
  a green run.
- Schema changes are recorded in `schemas/CHANGELOG.md`, never applied
  silently. The contract policy in `entity-manager.yaml` is `block`: when a
  record cannot satisfy the contract, surface the red to the owner — do not
  loosen the contract.

## Derived views

The entity index and this space's `README.md` are regenerated from the
records, never hand-edited. After any significant structural change — a skill
registered or retired, a document type added, the profile edited — check the
README against the registry and regenerate it if stale.

## Skills

Capabilities available here are registered as skill records in
`entities/skill/`. To run one, consult its record: what it wraps, what input
it needs, what it produces. Invocation resolves through the registry.
