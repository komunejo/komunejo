---
name: interviewer
description: >-
  Conversational intake for komunejo collaboration spaces. Use this skill whenever someone wants to create a new collaboration space ("create a space", "set up a place for my reading group", "I want somewhere my agents and I can work on X"), or whenever a space's own interview definitions call for structured intake of data the owner provides in conversation. The interview definition is data — this skill executes whichever definition applies; space creation is its first and bundled configuration. Do NOT trigger for registering skills into an existing space (that is the skill-manager's) or for plain record operations (that is entity-management's).
---

# Interviewer

General-purpose conversational intake. What to ask and which messages to deliver come from an **interview definition** — data, not prose baked into this skill. The bundled definition is space creation (`${CLAUDE_PLUGIN_ROOT}/skills/interviewer/interviews/space-creation.md`); spaces may carry their own definitions for later intake, and this skill executes them the same way.

The interview happens in the conversation's language. Fixed messages (`references/fixed-messages.md`) are interface text: delivered verbatim, never paraphrased, translated faithfully into the conversation's language — minding that language's own sentence order and idiom. `{placeholders}` are resolved at delivery time.

## Running an interview

1. **Load the definition.** It states the interview's purpose, the data it must obtain, what is derivable (never asked), and the fixed messages it delivers.
2. **Plan-mode gate.** If the session is in plan mode and the interview's work writes files, open the first reply with the plan-mode notice (verbatim, translated) and pass the exit-plan text to the plan-exit mechanism. Continue only in an action mode.
3. **Ask only what the definition marks as required and non-derivable.** One thing at a time, conversationally — no forms, no field names, no filesystem vocabulary unless the owner uses it first.
4. **Confirm the key details back** before acting on them.
5. **Execute the definition's procedure**, validate as it prescribes, and deliver its closing fixed message.

## Space creation, in brief

The bundled definition drives it; the outline (details in the definition):

1. Intake: the space's name, working language, and focus — the required fields of the profile schema — plus the location, resolved conversationally: propose a parent folder, never a directory holding unrelated work.
2. Skeleton: the directory, `git init`, `.gitignore` from `${CLAUDE_PLUGIN_ROOT}/kernel/space-gitignore`.
3. Registry: `schemas/` (the four kernel types) and `entity-manager.yaml` copied from `${CLAUDE_PLUGIN_ROOT}/kernel/`, `schemas/CHANGELOG.md` from the template with `{date}` resolved, and the profile record created through the engine (`${CLAUDE_PLUGIN_ROOT}/skills/entity-management/scripts/entity_lint.py`), `status: active`, body left for the owner's agreements. The kernel seeds no other records.
4. The space's own validator (DEC-019, by default — never an option the owner must understand to accept): copy `${CLAUDE_PLUGIN_ROOT}/skills/entity-management/scripts/entity_lint.py` to `.claude/entity_lint.py`, and install the validation hook from `${CLAUDE_PLUGIN_ROOT}/kernel/space-settings.json` as the space's `.claude/settings.json`.
5. The space's `CLAUDE.md`: `${CLAUDE_PLUGIN_ROOT}/kernel/space-claude-md.md` written in the space's language with placeholders resolved. The space's `README.md`: regenerated from the registry (the skill-manager's operation), plus the entity index (`entities/entities.md` unless the owner prefers elsewhere).
6. **`validate` green is the completion criterion.** Not a bespoke gate: the engine's exit code. On red, fix before saying the space exists.
7. Deliver the post-creation notice verbatim, `{useful-data}` derived from what the seeded schemas can use, named in plain language — never as field names.
8. Offer — never impose — an initial commit. It does not happen without an explicit yes.

Nothing beyond the required minimum is interviewed at creation. There is no separate reconfiguration flow: changing the space afterward is editing records and regenerating their derived views.
