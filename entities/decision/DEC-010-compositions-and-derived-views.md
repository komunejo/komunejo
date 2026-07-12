---
id: DEC-010
entity: decision
title: Compositions are ordered ref lists; views are derived, regenerated, never hand-edited
status: accepted
date: 2026-07-12
addresses: [REQ-004, REQ-005]
---

A composition record’s content is the ordered list of refs to section records — order lives in one engine-validated list, not in fields scattered across sections. Producing a document means reading its composition, loading the referenced sections’ skills, and writing. Derived views (the engine’s `INDEX.md`, the space’s `README.md` as its map and command reference) are always regenerated from records. No configuration dotfile and no template directory exist: typed facts live in records, the collaboration’s prose in record bodies, orientation in the README.
