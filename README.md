# komunejo

A Claude Code plugin that creates and maintains **collaboration spaces**: one directory per space, under git, where humans and their agents collaborate in natural language while the structured facts underneath — who, what, in which state, related how — live as typed records validated by a deterministic engine. Humans and agents keep working in prose; the space never depends on either's memory or discipline for its integrity.

The kernel serves any human–agent collaboration — a peer-review group, a personal Zettelkasten, a research log. Domains are particularizations added on top; the kernel itself knows nothing about any of them.

Status: v0 — the kernel. Spaces it creates speak the language their profile declares; the plugin itself is English-only.

## What it ships

- **The engine** — the vendored [`entity-management`](skills/entity-management/) skill (MPL-2.0), an exact copy of a tagged upstream release, never edited here; the pin is recorded in [docs/engine-pin.md](docs/engine-pin.md).
- **The skill manager** ([skills/skill-manager/](skills/skill-manager/)) — a space's capabilities and their derived views: registration end to end, capability audit, README regeneration.
- **The interviewer** ([skills/interviewer/](skills/interviewer/)) — conversational intake driven by interview definitions as data; space creation is its bundled configuration.
- **Kernel assets** ([kernel/](kernel/)) — the four entity schemas every space starts with (profile, skill, section, composition), the block-policy contract configuration, and the space templates.

## Trying it locally

From a folder that is not this repository:

```
claude --plugin-dir <path-to-this-repository>
```

then ask for a collaboration space in your own words. Creation asks only the essentials — name, working language, focus, location — and completes on validator green.

## Repository layout

| | |
|---|---|
| `.claude-plugin/` | plugin manifest |
| `skills/` | the three kernel skills |
| `kernel/` | schemas and templates installed into each space |
| `docs/` | design narrative, engine pin, fixed interface messages |
| `schemas/`, `entities/` | this repository's own design registry (see below) |

## Design

[docs/design.md](docs/design.md) is the authoritative design narrative. The decisions and requirements behind it are typed, validated records under [entities/](entities/entities.md) — this repository manages its own design with the engine it ships. Design decisions belong to the owner; open questions enter the record backlog as proposed decisions.

## License

MPL-2.0 — see [LICENSE.md](LICENSE.md). Use is subject to the acknowledgments in [WAIVER.md](WAIVER.md).
