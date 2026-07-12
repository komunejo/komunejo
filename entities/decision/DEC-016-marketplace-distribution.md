---
id: DEC-016
entity: decision
title: Distribution through a marketplace for the komunejo family
status: accepted
date: 2026-07-12
---

The plugin is distributed through a Claude Code marketplace serving the komunejo family (the kernel and its future domain packages), so installing and updating is a catalog operation rather than a manual checkout.

The marketplace is the owner’s own infrastructure, no third party: a `marketplace.json` catalog in a repository of the komunejo GitHub organization, which users add with `/plugin marketplace add komunejo/<repo>` — and, as the public face, the same catalog reachable from komunejo.net, addable by URL. Setting it up is an implementation task of v0.
