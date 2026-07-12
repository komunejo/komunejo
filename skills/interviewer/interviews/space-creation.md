# Interview definition: space creation

The interviewer's bundled configuration. An interview definition is data: it
states what to obtain, what is derived, the procedure, and the fixed messages
it delivers. The interviewer executes it; it never invents questions beyond it.

## Purpose

Create a working collaboration space, asking only what the kernel's schemas
require and cannot derive.

## Fixed messages used

From `../references/fixed-messages.md`: the plan-mode notice, the plan-mode
exit plan, the post-creation notice.

## Intake

| item | ask or derive | notes |
|---|---|---|
| name | ask | the collaboration's name, in the owner's words |
| language | ask, or confirm the conversation's | the space's working language |
| focus | ask | what this space is about, in the owner's words |
| location | resolve conversationally | propose a parent folder; never a directory holding unrelated work; no filesystem vocabulary unless the owner speaks it first |
| perspective | never asked at creation | belongs to the post-creation notice's useful data |
| status | derive | `active` |

Nothing beyond this is interviewed at creation.

## Procedure

1. Confirm the key details (name, language, focus, location) back to the
   owner; create nothing before that confirmation.
2. Skeleton: create the directory, `git init`, `.gitignore` from
   `kernel/space-gitignore`.
3. Registry: copy `kernel/schemas/` (profile, skill, section, composition)
   and `kernel/entity-manager.yaml`; write `schemas/CHANGELOG.md` from
   `kernel/schemas-changelog.md` with `{date}` resolved to today; create the
   profile record through the engine with the intake values, `status:
   active`, body empty for the owner's future agreements.
4. The space's validator, by default — this is not an intake question and is
   never offered as an option: copy the engine's `entity_lint.py` to
   `.claude/entity_lint.py`; install `kernel/space-settings.json` as the
   space's `.claude/settings.json`.
5. Write the space's `CLAUDE.md` from `kernel/space-claude-md.md`, in the
   space's language, placeholders resolved.
6. Regenerate the derived views: the entity index (`entities/entities.md`
   unless the owner prefers elsewhere) and the space's `README.md` (the
   skill-manager's regeneration).
7. Run `validate`. Green is the completion criterion; on red, fix before
   claiming the space exists.
8. Deliver the post-creation notice. Useful data to derive `{useful-data}`
   from, at this stage: whose perspective the space materializes; the
   collaboration's agreements and conventions (the profile's body);
   capabilities worth registering (skills the space should have).
9. Offer, never impose: an initial commit.
