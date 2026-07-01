# Loveca handoff 20260622i

## Status

- 20260622h generalized live-start yell heart color conversion.
- 20260622i adds a generic top-k multi-pick route.
- Debug commands should be provided in chat only, not embedded in this handoff.

## Change

- Added support for this generic effect-template shape:

```text
自分のデッキの上からカードをK枚見る。その中からカードをN枚手札に加え、残りを控え室に置く。
```

- Changed file:
  - `llocg_ui/engine.py`
- Updated audit files:
  - `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
  - `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`

## BUILD_TAG

- `engine.py`: `topk_choose_n_to_hand_20260622i`

## Covered example

- `LL-bp6-001` 南ことり＆黒澤ダイヤ＆徒町小鈴
  - 登場時: top 6, choose 2 to hand, rest to waiting room.

## Notes

- No cardnumber-specific branch was added.
- Reuses the existing `choose_from_topk` pending UI.
- Single-pick top-k behavior is preserved; multi-pick activates only when `pick_count` is present.

## Confirmed

- Effect-template matcher maps the LL-bp6-001 shape to `look_top_choose_n`.
- Engine-only pending test: choose 2 from top 6 sends the selected 2 to hand and the remaining 4 to waiting room.
- Python compile check passed for `engine.py`, `server.py`, `engine_effect.py`, and `effects/*.py`.
