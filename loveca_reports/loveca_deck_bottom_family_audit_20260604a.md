# Loveca deck-bottom family audit 20260604a

BUILD_TAG: `audit_deck_bottom_family_20260604a`
compiled: `/mnt/data/cards_compiled_v7h.json`

## Summary

candidates: 16
- implemented_draw_then_hand_bottom: 3
- implemented_existing_named_green_cost_to_bottom: 1
- implemented_existing_yell_to_bottom: 1
- implemented_green_kind_upto_bottom: 1
- implemented_green_member2_costsum_bottom: 1
- implemented_hand_live_cost_to_bottom: 1
- needs_mass_bottom_threshold: 1
- needs_opponent_mass_bottom: 1
- needs_opponent_player_choice: 3
- needs_top_or_bottom_choice: 3

## Rows

- `LL-bp3-001` 園田海未＆津島善子＆天王寺璃奈 — **implemented_existing_named_green_cost_to_bottom**
  - cost: 自分の控え室にある「園田海未」と「津島善子」と「天王寺璃奈」を、合計6枚をシャッフルしてデッキの一番下に置く
  - effect: エネルギーを6枚までアクティブにする。
- `PL!HS-bp6-031` ファンファーレ！！！ — **needs_mass_bottom_threshold**
  - effect: 自分の控え室にあるすべてのメンバーカードをシャッフルし、デッキの下に置いてもよい。これにより『みらくらぱーく！』のカードを15枚以上デッキの下に置いた場合、ライブ終了時まで、自分のステージにいる「安養寺姫芽」1人は<(ブレード)><(ブレード)><(ブレード)>を得る。
- `PL!HS-pb1-012` 百生吟子 — **needs_opponent_mass_bottom**
  - effect: 自分と相手はそれぞれ、自身の控え室にあるすべてのメンバーカードをシャッフルし、自身のデッキの下に置く。これにより自分と相手のカードが合計20枚以上デッキの下に置かれた場合、自分の控え室からライブカードを1枚手札に加え、ライブ終了時まで、<(ブレード)><(ブレード)>を得る。
- `PL!N-bp3-009` 天王寺璃奈 — **implemented_green_member2_costsum_bottom**
  - cost: 控え室にあるメンバーカード2枚を好きな順番でデッキの一番下に置いてもよい
  - effect: それらのカードのコストの合計が、6の場合、カードを1枚引く。合計が8の場合、ライブ終了時まで、<ALL>を得る。合計が25の場合、ライブ終了時まで、「<常時>ライブの合計スコアを+1する。」を得る。
- `PL!N-bp3-010` 三船栞子 — **needs_opponent_player_choice**
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるメンバーカードを2枚まで、好きな順番でデッキの一番下に置く。
- `PL!S-PR-041` 黒澤ルビィ — **needs_opponent_player_choice**
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるライブカードを1枚、そのプレイヤーのデッキの一番下に置く。そうした場合、自分はカードを1枚引く。
- `PL!S-bp2-007` 国木田花丸 — **implemented_hand_live_cost_to_bottom**
  - cost: 手札のライブカードを1枚公開し、デッキの一番下に置いてもよい
  - effect: 自分のデッキの上からカードを2枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。
- `PL!S-bp2-008` 小原鞠莉 — **implemented_green_kind_upto_bottom**
  - effect: 自分の控え室からライブカードを1枚までデッキの一番下に置く。
- `PL!S-bp2-021` 未体験HORIZON — **implemented_existing_yell_to_bottom**
  - effect: エールにより公開された自分のカードの中から、ライブカードを1枚までデッキの一番下に置く。
- `PL!S-bp3-007` 国木田花丸 — **needs_opponent_player_choice**
  - cost: <(E)>
  - effect: 自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるライブカードを1枚、そのプレイヤーのデッキの一番下に置く。そうした場合、自分はカードを1枚引く。
- `PL!S-bp5-014` 渡辺曜 — **implemented_draw_then_hand_bottom**
  - effect: カードを1枚引き、手札を1枚デッキの一番下に置く。
- `PL!S-bp6-002` 桜内梨子 — **needs_top_or_bottom_choice**
  - effect: 『Aqours』のライブカードが自分のライブカード置き場から控え室に置かれたとき、そのライブカードをデッキの一番上か一番下に置いてもよい。
- `PL!S-bp6-019` Step! ZERO to ONE — **needs_top_or_bottom_choice**
  - effect: 自分のステージにいるメンバーがすべて『Aqours』の場合、このカードのスコアを+1し、カードを1枚引き、手札からカードを1枚デッキの一番上か一番下に置く。
- `PL!S-sd1-009` 黒澤ルビィ — **needs_top_or_bottom_choice**
  - cost: 手札の『Aqours』のカードを1枚公開してもよい
  - effect: これにより公開したカードをデッキの一番上か一番下に置き、ライブ終了時まで、<(ブレード)>を得る。
- `PL!S-sd1-017` 小原鞠莉 — **implemented_draw_then_hand_bottom**
  - effect: カードを1枚引き、手札を1枚デッキの一番下に置く。
- `PL!S-sd1-018` 黒澤ルビィ — **implemented_draw_then_hand_bottom**
  - effect: カードを1枚引き、手札を1枚デッキの一番下に置く。
