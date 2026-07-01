# Loveca handoff 20260622k

## Status

- 20260622j added top-k sentence variant and simple mill.
- 20260622k adds a cost-filtered group member top-k route.
- Debug checks are tracked in `docs/debug/loveca_implementation_debug_notes_20260622.md`.

## Change

- Added support for this generic effect-template shape:

```text
自分のデッキの上からカードをK枚見る。その中からコストN以上の『GROUP』のメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。
```

## BUILD_TAG

- `engine.py`: `topk_group_member_cost_filter_20260622k`

## Covered examples

- `PL!HS-bp5-008` 桂城泉
- `PL!-bp4-006` 西木野真姫 is now classified as covered by existing success-zone wrapper plus existing group-member top-k route.

## Notes

- No cardnumber-specific branch was added.
- The new route reuses existing filtered `choose_from_topk` pending UI.
- Internal filter test confirmed only matching cost 9+ Hasunosora member cards are clickable.
