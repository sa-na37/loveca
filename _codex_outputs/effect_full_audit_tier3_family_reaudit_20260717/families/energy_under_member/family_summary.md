# Family: energy_under_member

- target_count: 1
- representative: PL!N-bp7-004#A01 / PL!N-bp7-004
- matcher: NO_MATCH
- trigger_hook: 起動
- resolver: none observed
- UI route: required for some rows
- pass_count: 0
- unresolved_count: 1
- confirmed_backlog_count: 1

## Common Cause
Most rows remain matcher or event-hook unresolved; no row is promoted to NOT_IMPLEMENTED_CONFIRMED without a dedicated resolver audit.

## Recommended Fix Unit
Implement by family-level generic matcher/resolver, then run representative browser checks where UI is required.
