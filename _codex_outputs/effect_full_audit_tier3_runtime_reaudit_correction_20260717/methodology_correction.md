# Methodology Correction

- Previous final statuses were discarded; only `target_61_canonicalized.csv` was retained as the target list.
- Route checks are split into registry, engine parser, engine/effects special, and server/UI route columns.
- Each ability has positive and negative setup evidence. Live-start rows execute through `LIVE_SET -> LIVE_CONFIRM`; activated rows execute hand/stage activation routes; continuous/BODY rows use positive/negative numeric state snapshots.
- Browser evidence is not counted as checked unless actually executed. This run records UI representative IDs only.
- Runtime and DB were not modified.
