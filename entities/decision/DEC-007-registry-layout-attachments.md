---
id: DEC-007
entity: decision
title: Records live in the registry layout; domain documents are referenced attachments
status: accepted
date: 2026-07-12
addresses: [REQ-002]
---

Records live where the engine expects them (`entities/<type>/<ID>-slug.md`), not scattered in place through a space’s working tree. Domain documents — a shared text, a report, a note — stay wherever the space’s work puts them and are *referenced from* records as attached documents (path fields). The engine stays generic and unmodified; the structural price of the registry layout was weighed and accepted.
