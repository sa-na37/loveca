# Loveca choose-player green-bottom family audit 20260605a

BUILD_TAG: `audit_choose_player_green_bottom_family_20260605a`
compiled: `/mnt/data/cards_compiled_v7h.json`

## Summary

candidates: 5
- implemented_choose_player_live_bottom_draw: 2
- implemented_choose_player_member_upto_bottom: 1
- needs_audit_unmatched_choose_player: 2

## Rows

- `PL!N-bp3-010` 三船栞子 — **implemented_choose_player_member_upto_bottom**
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるメンバーカードを2枚まで、好きな順番でデッキの一番下に置く。
- `PL!N-bp4-002` 中須かすみ — **needs_audit_unmatched_choose_player**
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーのデッキの一番上のカードを見る。自分はそのカードを控え室に置いてもよい。
- `PL!S-PR-041` 黒澤ルビィ — **implemented_choose_player_live_bottom_draw**
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるライブカードを1枚、そのプレイヤーのデッキの一番下に置く。そうした場合、自分はカードを1枚引く。
- `PL!S-bp3-007` 国木田花丸 — **implemented_choose_player_live_bottom_draw**
  - cost: <(E)>
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるライブカードを1枚、そのプレイヤーのデッキの一番下に置く。そうした場合、自分はカードを1枚引く。
- `PL!S-pb1-008` 小原鞠莉 — **needs_audit_unmatched_choose_player**
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーのデッキの上からカードを2枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。
