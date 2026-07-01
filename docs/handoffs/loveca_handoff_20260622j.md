# Loveca handoff 20260622j

## Status

- 20260622i added generic top-k choose N to hand.
- 20260622j adds two small top-k variants.
- Debug commands and later UI smoke details are tracked in `docs/debug/loveca_implementation_debug_notes_20260622.md`.

## Change

- Added support for this sentence-split top-k choose-one shape:

```text
自分のデッキの上からカードをK枚見る。その中から1枚を手札に加える。残りを控え室に置く。
```

- Added support for simple top-k mill:

```text
自分のデッキの上からカードをK枚控え室に置く。
デッキの上からカードをK枚控え室に置く。
```

## BUILD_TAG

- `engine.py`: `topk_mill_and_choose_variants_20260622j`

## Covered examples

- `PL!-bp5-222` 優木あんじゅ
- `PL!HS-cl1-004` 百生吟子
- `PL!HS-cl1-007` セラス 柳田 リリエンフェルト

## Notes

- No cardnumber-specific branch was added.
- The choose-one variant reuses existing `look_top_choose`.
- The simple mill route uses deck refresh before top access, then moves the available top cards to waiting room.
