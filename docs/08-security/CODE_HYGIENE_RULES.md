# Code Hygiene Rules

This document describes how Sophia AI manages short-lived scripts and other one-time artefacts.

## One-Time Artefact Policy

- Temporary migration scripts and backup folders must not remain in `main`.
- Any file flagged for one-time use should be archived for 30 days and then deleted.
- Inventory reports are generated with `make one-time-inventory`.
- Approved items are moved with `make one-time-archive` and purged with `make one-time-purge`.

See the automation scripts in `scripts/` for details.
