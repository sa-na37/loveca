# Family: stage_count_group_unit_name

- target_count: 4
- representative: PL!-bp6-009#A01 / PL!-bp6-009
- matcher: NO_MATCH
- trigger_hook: 常時
- resolver: none observed
- UI route: not required for representative state checks
- pass_count: 0
- unresolved_count: 4
- confirmed_backlog_count: 4

## Common Cause
Most rows remain matcher or event-hook unresolved; no row is promoted to NOT_IMPLEMENTED_CONFIRMED without a dedicated resolver audit.

## Recommended Fix Unit
Implement by family-level generic matcher/resolver, then run representative browser checks where UI is required.
