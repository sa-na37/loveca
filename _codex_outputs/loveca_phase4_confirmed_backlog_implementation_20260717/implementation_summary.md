# Implementation Summary

- Implemented a hand-activated ability route for activated abilities whose cost moves the source card from hand to waiting room.
- Implemented a generic hand MEMBER reveal cost-sum pending for activated abilities that reveal any number of member cards and check totals 10/20/30/40/50.
- Public reveal evidence is emitted through `show_revealed_cards_ack`; selected cards remain in hand.
- Temporary blade and live-total score bonuses use existing stage slot `temp_blade` / `temp_score` with `temp_until=end_of_live`.
- Undo is command-granular; evidence includes one-step undo and multi-step restoration to initial state.

## Browser Verification Addendum

- PL!HS-bp6-014: hand card shows `能力`; pending displays source card and active effect; choosing stage target applies blade.
- PL!SP-bp1-003: pending candidate list filters to MEMBER cards; 0-card submit resolves as condition unmet; 1 card cost10 resolves as condition met and public reveal is visible.
- UI state retention fix: selected reveal cards are keyed by pending identity so 250ms state refresh does not reset the pending selection before submit.
