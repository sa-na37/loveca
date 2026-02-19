# v45 Layout Locked Baseline

This package is identical to llocg_ui_clean_slim_v45.zip, plus this note.

Layout policy (hand/stage/etc.):
- Treat the v45 hand + stage layout as canonical.
- Future UI fixes must NOT change these layout-affecting files/sections unless explicitly requested:
  - run_llocg_ui_web.py HTML/CSS for hand & stage positioning
  - Any CSS rules controlling: hand zone, stage zone, waiting room positions/sizes

If you need to apply bugfixes later, do it surgically and re-run a visual regression check
against this baseline.
