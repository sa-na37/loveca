# Loveca full effect audit summary 20260716

## Scope

- Fixed ability population: 1036 audit_id rows.
- Baseline test cases preserved: 4195 rows.
- Runtime/DB modified during audit: NO. Only `_codex_outputs/effect_full_audit_20260716` was written.
- Worktree dirty at start/current: YES. See `environment_snapshot.txt`; uncommitted changes were not reset.

## Implementation Mapping Counts

- DB_DATA_MISMATCH: 31
- IMPLEMENTED: 869
- NOT_IMPLEMENTED: 107
- PARTIAL: 1
- UNREACHABLE: 28

## Test Result Counts

- BLOCKED: 9
- DB_DATA_MISMATCH: 144
- NEEDS_MANUAL_CONFIRMATION: 3448
- NOT_IMPLEMENTED: 509
- UNREACHABLE: 85

## Important Caveat

No case is marked PASS because the instruction requires both internal state and UI verification. This run completed full static mapping plus generated reproducible commands and manual UI checklist; browser UI execution remains required for PASS classification.

## Main Output Files

- `implementation_mapping.csv`
- `test_plan_expanded.csv`
- `test_results.csv`
- `coverage_report.csv`
- `issues.md` / `issues.csv`
- `db_mismatches.csv`
- `debug_commands/`
- `logs/`
- `manual_ui_checklist.md`
