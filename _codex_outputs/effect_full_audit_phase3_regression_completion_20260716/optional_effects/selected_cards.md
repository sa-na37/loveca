# Selected real optional effect cards

## Type A: PL!S-sd1-004

- Optional type: `してもよい`
- Effect: `カードを1枚引いてもよい。そうした場合、手札2枚を好きな順番でデッキの上に置く。`
- Route: live-start auto order -> `confirm_effect`
- Reason: already implemented generic `optional_draw_then_hand_top`, deterministic debug setup, skip and execute both available.

## Type B: PL!SP-bp2-013

- Optional type: `1枚まで`
- Effect: `自分の控え室からカードを1枚までデッキの一番上に置く。`
- Route: enter trigger -> `topdeck_from_green`
- Reason: implemented generic `topdeck_green_any_upto1`, deterministic waiting-room candidate, `allow_less=True` skip and execute both available.
