# Family: draw

- target_count: 3
- representative: PL!-pb1-015#A02 / PL!-pb1-015
- matcher: NO_MATCH
- trigger_hook: BODY
- resolver: none observed
- UI route: not required for representative state checks
- pass_count: 0
- unresolved_count: 3
- confirmed_backlog_count: 3

## Common Cause
Most rows remain matcher or event-hook unresolved; no row is promoted to NOT_IMPLEMENTED_CONFIRMED without a dedicated resolver audit.

## Recommended Fix Unit
Implement by family-level generic matcher/resolver, then run representative browser checks where UI is required.
