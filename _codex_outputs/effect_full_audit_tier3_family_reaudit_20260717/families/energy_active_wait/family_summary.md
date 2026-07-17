# Family: energy_active_wait

- target_count: 9
- representative: PL!HS-pb1-001#A01 / PL!HS-pb1-001
- matcher: NO_MATCH
- trigger_hook: BODY
- resolver: none observed
- UI route: required for some rows
- pass_count: 0
- unresolved_count: 9
- confirmed_backlog_count: 9

## Common Cause
Most rows remain matcher or event-hook unresolved; no row is promoted to NOT_IMPLEMENTED_CONFIRMED without a dedicated resolver audit.

## Recommended Fix Unit
Implement by family-level generic matcher/resolver, then run representative browser checks where UI is required.
