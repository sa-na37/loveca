# pending_residue_after

Runtime fix verified on 2026-07-16.

## Mandatory no-selection NEXT

- phase after NEXT: `MAIN`
- pending kind after NEXT: `choose_enter_effect_mode`
- mandatory flag: `True`
- allow_skip flag: `False`
- selection message present: `True`
- UI message present: `True`
- UI choice options present: `True`

## After valid choice

- pending after valid draw/discard resolution: `[]`
- UI mandatory message still visible: `False`
- UI choose popup still visible: `False`

## Screenshots

- `regression/ui/mandatory_choice_next_block.png`
- `regression/ui/mandatory_choice_after_valid_resolution.png`
