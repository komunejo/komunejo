# Waiver and Acknowledgment

By installing or using komunejo — its validation engine, its skill instructions, or its documentation — I acknowledge and agree to the following.

**I run agentic AI on my own responsibility.** komunejo is designed to be operated by AI agents that read, create, and modify files in my projects. I remain the owner of those projects and the reviewer of last resort: I will keep my work under version control or backed up, and I will review changes that agents make to my files.

**I understand what is guaranteed and what is not.** The engine guarantees *hard integrity only*: types, required fields, enums, unique IDs, resolvable references, and declared aggregate constraints, as checked by `entity_lint.py` at the moment it runs. It does not and cannot guarantee *soft integrity* — factual correctness of prose, absence of contradictions in free text, or the truth of any recorded value. A green validation means "the records conform to the declared schemas", never "the records are true".

**Schemas and policies are mine.** The schemas, the contract policy (`policy.on_unresolvable`), and every schema change logged in `schemas/CHANGELOG.md` are decisions of my project, not of the software's author. Consequences of a lax schema, a relaxed contract, or an unreviewed migration are my own.

**I release the author from liability.** To the maximum extent permitted by law, I release, hold harmless, and agree to indemnify V. Gracia from and against any claim, damage, data loss, or other harm arising from my use of this software and documentation. The software is provided "as is", without warranty of any kind, as further detailed in the warranty disclaimer and limitation of liability of the Mozilla Public License 2.0 (see [`LICENSE.md`](LICENSE.md)), which are incorporated here by reference.

**Third-party terms are theirs.** My use of any AI service to operate this software (for example Anthropic's Claude) is governed by that provider's own terms and policies, which this project neither modifies nor answers for.
