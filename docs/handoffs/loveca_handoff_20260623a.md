# Loveca handoff 20260623a

## Status

- 20260622k added cost-filtered group member top-k.
- 20260623a adds a top-k reorder typo variant and a top1 optional mill route.
- Debug checks are tracked in `docs/debug/loveca_implementation_debug_notes_20260622.md`.

## Change

- Accepted DB typo `順場` for the existing top-k reorder route.
- Added support for this generic effect-template shape:

```text
自分のデッキの上からカードを1枚見る。そのカードを控え室に置いてもよい。
```

## BUILD_TAG

- `engine.py`: `topk_reorder_typo_and_top1_optional_20260623a`

## Covered examples

- `PL!-sd1-019` START：DASH!!
- `PL!HS-cl1-001` 日野下花帆

## Notes

- No cardnumber-specific branch was added.
- `PL!-sd1-019` uses the existing reorder-top-k pending UI.
- `PL!HS-cl1-001` reuses the existing top1 green/keep pending UI.
