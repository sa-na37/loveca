# Loveca handoff 20260623b

## Scope

Implemented a generic top-k mill conditional followup route in `llocg_ui/engine.py`.

## Runtime changes

- Updated `BUILD_TAG` to `topk_mill_conditional_followup_20260623b`.
- Added generic matcher/resolver support for:
  - mill top K, draw N if the milled cards contain a live card
  - mill top K, draw N if all milled cards are members
  - mill top K, gain icons if the milled cards contain a live card
  - mill top K, gain icons if all milled cards are members
  - mill top K, gain icons if all milled cards are members with a specified heart color
  - mill top K, gain icons if all milled cards match a group/unit label
- The resolver uses existing top-access refresh behavior before milling.
- Temporary heart/blade grants use the existing stage-member temporary icon helper.

## Newly covered top-k audit examples

- `PL!-sd1-007` 東條希 — `mill_top_k_draw_if_contains_live`
- `PL!HS-PR-019` 百生吟子 — `mill_top_k_gain_icons_if_all_member_heart_color`
- `PL!HS-PR-021` 安養寺姫芽 — `mill_top_k_gain_icons_if_all_member_heart_color`
- `PL!HS-bp1-008` 徒町小鈴 — `mill_top_k_draw_if_all_members`
- `PL!HS-bp5-001` 日野下花帆 — `mill_top_k_gain_icons_if_contains_live`
- `PL!HS-bp5-013` 徒町小鈴 — `mill_top_k_gain_icons_if_all_members`
- `PL!HS-bp6-009` 日野下花帆 — `mill_top_k_gain_icons_if_all_group_cards`
- `PL!HS-sd1-013` 徒町小鈴 — `mill_top_k_gain_icons_if_all_member_heart_color`

## Audit updates

- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
  - `implemented_existing_topk_or_deck`: 81 -> 89
  - `needs_audit_unmatched_topk`: 57 -> 49
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
  - updated the eight examples above from `needs_audit_unmatched_topk` to `implemented_existing_topk_or_deck`

## Checks

- Loaded the actual runtime DB and confirmed all eight target card texts match the expected generic route.
- Engine-only draw followup test confirmed top 5 cards move to waiting room and 1 card is drawn.
- Engine-only icon followup test confirmed top 3 cards move to waiting room and the source stage member gains a temporary green heart.
- Full compile check is tracked in `docs/debug/loveca_implementation_debug_notes_20260622.md`.

## Notes

- If the followup draw exhausts the remaining deck, the existing refresh rule may immediately shuffle waiting room into the deck. Use a deck with extra remaining cards when visually checking only the waiting-room result.
- No file moves, deletions, or new backups were performed in this step.
