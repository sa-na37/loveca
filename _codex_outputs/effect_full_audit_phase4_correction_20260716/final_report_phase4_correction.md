PHASE4_CORRECTION_PARTIAL

## Summary

Phase 4 classifications were treated as provisional. All 136 rows were checked for duplicate, fragment, and trigger/body split issues. Tier 1 was redesigned per trigger type and re-run with corrected setup assumptions. Implementation backlog and research backlog are separated.

## Coverage

- original_rows: 136
- duplicate_rows: 9
- fragment_rows: 3
- nested_granted_rows: 0
- trigger_reclassified_rows: 84
- canonical_abilities: 124
- excluded_rows: 12
- tier1_total: 11
- tier1_designs_completed: 11
- tier1_setups_valid: 8
- tier1_triggers_reached: 4
- tier1_effects_resolved: 3
- tier1_cleanup_passed: 3
- tier1_undo_exact: 0
- tier1_ui_checked: 11
- tier1_still_unresolved: 8
- implementation_backlog_count: 2
- research_backlog_count: 119
- excluded_backlog_count: 12
- behavioral_issues: 0
- watch_items: 1

## Tier 1 classifications

- IMPLEMENTED_AND_REACHABLE: 3
- ROUTE_UNRESOLVED: 3
- SETUP_INVALID: 3
- TRIGGER_REACHED_RESOLVER_BLOCKED: 1
- UI_ROUTE_MISSING: 1

## Backlog Policy

- Implementation backlog includes only confirmed missing UI/resolver/routes from corrected Tier 1 evidence.
- Research backlog contains setup/route unresolved rows, former Tier 3 generic unresolved rows, and former Tier 4 high-confidence candidates pending trigger-appropriate tests.
- Fragment/duplicate rows and the empty-string-as-zero watch item are excluded from implementation backlog.
