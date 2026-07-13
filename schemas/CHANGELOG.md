# Schema changelog

## 2026-07-12 — initial schema set

Created `decision` (DEC) and `requirement` (REQ). Contract policy set to `block` in `entity-manager.yaml`, consistent with the constitution komunejo ships to the spaces it generates (DEC-004). Author: the project owner, via session agent.

## 2026-07-13 — proposal and issue types

Added `proposal` (PROP) and `issue` (ISS). `proposal` mirrors the type in the upstream `entity-manager` skill (the plugin's improvement backlog: title, status, date, `addresses` refs to requirements, tags). `issue` is new: a field-defect log (title, status open/resolved/wontfix, date, tags), recording problems found while using komunejo or a space it generated. Motivated by a defect encountered using `index__synced-artifacts` (ISS-001) and the proposal it triggered (PROP-001). Author: the project owner, via session agent.
