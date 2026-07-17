# Family: deck_top_or_bottom_move

- target_count: 2
- representative: PL!S-bp6-002#A01 / PL!S-bp6-002
- matcher: NO_MATCH
- trigger_hook: BODY
- resolver: none observed
- UI route: required for some rows
- pass_count: 0
- unresolved_count: 2
- confirmed_backlog_count: 2

## Common Cause
Most rows remain matcher or event-hook unresolved; no row is promoted to NOT_IMPLEMENTED_CONFIRMED without a dedicated resolver audit.

## Recommended Fix Unit
Implement by family-level generic matcher/resolver, then run representative browser checks where UI is required.
