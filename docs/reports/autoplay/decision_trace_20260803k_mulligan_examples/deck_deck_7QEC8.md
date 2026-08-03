# Autoplay Policy Report: 三神

- model: `stage1_policy_template`
- recommended: 未判定

## Cost Bands

- 2-4: 29
- 5-10: 7
- 11-14: 10
- 15+: 2

## Progressions


## Special Signals

### エネルギー追加ライブ
- なし

### エネルギーアクティブ化
- なし

### コスト軽減
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20

### エネルギー支払いなし登場
- なし

### 支払い以上の登場
- なし

### 低コスト追加登場
- なし

### 特殊バトンタッチ
- なし

### 15+高コスト
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 200
- seed: base=29 effective=3472011797
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 未判定
- late policy: 未判定
- target turns: 20 / 20 / 20 / 2-20-2
- accepted targets: 20 / 20 / 20 / 2-20-2

### Effect Assumptions

- up to three cards are live-set exchanged before member planning, and each exchanged card draws one replacement
- the normal draw step is modeled once per turn, including turn 1
- live draw effects are modeled as hand smoothing after each turn
- Daydream-like energy boost live cards count as the 2-4-2 alternative bridge only when selected as the live-set card and succeeding; the added energy becomes usable from the next turn
- low-cost stage summon effects add an extra virtual 2-cost member for progression matching

### Decision Policy

- Initial hand is six cards from the shuffled deck.
- Mulligan scores cards against accepted turn 1-3 targets; scarce target costs such as a 3-copy 10-cost member are kept more strongly.
- Abundant 2-cost members are kept only up to the near-term need because extra copies are comparatively easy to redraw.
- Live cards with energy-boost text are kept when they are needed for a bridge route, but are protected from live-set exchange before that route.
- Cards with low turn 1-3 target value are redrawn back to six cards.
- During live set, up to three cards may be exchanged, including non-live cards.
- Live set exchanges low-priority or replaceable cards to dig toward the nearest target; it does not automatically set every live card.
- Live score targets are inferred from live cards actually present in the deck; the hit check uses the highest-score live card selected during that turn's live-set exchange.
- If the turn has a Daydream-like 2-4-2 bridge, an energy-boost live is preferred as the live-set card for that turn only.
- Member placement tracks active/wait energy, pays active energy for normal plays, applies baton reduction for replacements, then scores feasible lines as higher than target first, exact target second, then the largest available fallback.
- Extra members beyond the accepted target slot count are not played only for occupancy; the persistent stage keeps existing cards unless replacing them improves the current target.
- Each turn performs active, energy, and draw progression before planning, including the first turn draw after setup.
- After live success, draw effects on the live-set card are modeled as hand smoothing for the following turn; energy-boost lives place energy into wait for the next active phase.

### Target Cards And Routes

- T1
  - 20: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補
- T2
  - 20: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補
- T3
  - 20: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補
- T4
  - 2-20-2: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補 / PL!N-PR-009 優木せつ菜 route=手札から通常登場 / PL!N-PR-009 優木せつ菜 route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=20 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=0.0
- T2: target=20 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=0.0
- T3: target=20 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=0.0
- T4: target=2-20-2 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=5.18

### Live Score Targets

- T1: target_score=3 accepted=[3, 5] hit_rate=0.735 cumulative=0.735 cards=PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3
- T2: target_score=5 accepted=[5] hit_rate=0.475 cumulative=0.345 cards=PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- T3: target_score=5 accepted=[5] hit_rate=0.375 cumulative=0.12 cards=PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- T4: target_score=5 accepted=[5] hit_rate=0.365 cumulative=0.02 cards=PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5

### Top Routes

- none / none / none / 4-2: 120 (0.6)
- none / none / none / 2-2: 77 (0.385)
- none / none / none / 2: 2 (0.01)
- none / none / none / 4: 1 (0.005)

### Miss Reasons

- T1: missing 20 200 (1.0)
- T2: missing 20 200 (1.0)
- T3: missing 20 200 (1.0)
- T4: missing 20 197 (0.985), missing 20-2 3 (0.015)

### Sample Routes

- T1: none -> none -> none -> 2-2
- T2: none -> none -> none -> 2-2
- T3: none -> none -> none -> 4-2
- T4: none -> none -> none -> 2-2
- T5: none -> none -> none -> 2-2

## Decision Trace

### Trial 1
- route: none -> none -> none -> 2-2
- initial hand: PL!S-PR-017 渡辺曜 cost=4 | PL!S-PR-029 渡辺曜 cost=9 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-005 渡辺曜 cost=13
- mulligan target: 20 / 20 / 20
- mulligan score: 32.575 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- keep: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- return: PL!S-PR-017 渡辺曜 cost=4 | PL!S-PR-029 渡辺曜 cost=9 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-005 渡辺曜 cost=13
- redraw: PL!SP-pb1-018 米女メイ cost=2 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-005 渡辺曜 cost=13
- post mulligan hand: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!SP-pb1-018 米女メイ cost=2 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-005 渡辺曜 cost=13
- hand need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-PR-017 渡辺曜 cost=4 need=0.0; PL!S-PR-029 渡辺曜 cost=9 need=0.0; PL!S-bp2-005 渡辺曜 cost=13 need=0.0; PL!S-bp2-014 渡辺曜 cost=4 need=0.0; PL!S-bp3-025 SUKI for you, DREAM for you! score=5 need=0.0
- mulligan candidate comparison:
  - score=32.575 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-PR-017 渡辺曜 cost=4; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-PR-029 渡辺曜 cost=9; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!S-bp3-025 SUKI for you, DREAM for you! score=5
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!S-bp2-014 渡辺曜 cost=4

#### T1 target 20 accepted 20
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-014 渡辺曜 cost=4
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!SP-pb1-018 米女メイ cost=2 | PL!S-bp2-014 渡辺曜 cost=4
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp2-023 MY舞☆TONIGHT score=3
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!S-bp2-005 渡辺曜 cost=13 need=0.0; PL!S-bp2-014 渡辺曜 cost=4 need=0.0; PL!S-bp2-023 MY舞☆TONIGHT score=3 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 20 accepted 20
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!SP-pb1-018 米女メイ cost=2
- live set selected: PL!N-bp1-017 宮下愛 cost=4 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!N-PR-009 優木せつ菜 cost=2 need=9.6; PL!SP-pb1-018 米女メイ cost=2 need=9.6; PL!S-bp2-005 渡辺曜 cost=13 need=5.4; PL!S-bp2-001 高海千歌 cost=9 need=4.63; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 20 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 20 accepted 20
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!S-bp2-006 津島善子 cost=11
- live set selected: PL!S-bp2-022 未熟DREAMER score=5 | PL!N-bp3-022 三船栞子 cost=4 | PL!N-bp3-022 三船栞子 cost=4
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp2-022 未熟DREAMER score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=74.0; PL!N-PR-009 優木せつ菜 cost=2 need=7.47; PL!SP-pb1-018 米女メイ cost=2 need=7.47; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-005 渡辺曜 cost=13 need=4.2; PL!S-PR-029 渡辺曜 cost=9 need=3.6
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 2
- route: none -> none -> none -> 2-2
- initial hand: PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-bp2-006 津島善子 cost=11 | PL!S-bp2-001 高海千歌 cost=9 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- mulligan target: 20 / 20 / 20
- mulligan score: 32.575 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- keep: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- return: PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-bp2-006 津島善子 cost=11 | PL!S-bp2-001 高海千歌 cost=9
- redraw: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-022 未熟DREAMER score=5 | PL!S-bp2-006 津島善子 cost=11
- post mulligan hand: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-022 未熟DREAMER score=5 | PL!S-bp2-006 津島善子 cost=11
- hand need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-PR-017 渡辺曜 cost=4 need=0.0; PL!S-bp2-001 高海千歌 cost=9 need=0.0; PL!S-bp2-001 高海千歌 cost=9 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0
- mulligan candidate comparison:
  - score=32.575 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-bp2-006 津島善子 cost=11; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-PR-017 渡辺曜 cost=4; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-bp2-001 高海千歌 cost=9; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-bp2-006 津島善子 cost=11; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction

#### T1 target 20 accepted 20
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-023 MY舞☆TONIGHT score=3
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-023 MY舞☆TONIGHT score=3
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-022 未熟DREAMER score=5 need=0.0; PL!S-bp2-023 MY舞☆TONIGHT score=3 need=0.0; PL!S-bp2-023 MY舞☆TONIGHT score=3 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 20 accepted 20
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!S-bp2-001 高海千歌 cost=9
- live set selected: PL!S-bp2-022 未熟DREAMER score=5 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-bp2-014 渡辺曜 cost=4
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp2-022 未熟DREAMER score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-bp2-006 津島善子 cost=11 need=8.1; PL!S-bp2-001 高海千歌 cost=9 need=4.63; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!N-bp3-022 三船栞子 cost=4 need=2.31; PL!S-bp2-014 渡辺曜 cost=4 need=2.31
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 20 accepted 20
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!S-PR-017 渡辺曜 cost=4
- live set selected: PL!S-PR-017 渡辺曜 cost=4 | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-014 渡辺曜 cost=4
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=74.0; PL!SP-pb1-018 米女メイ cost=2 need=7.47; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-001 高海千歌 cost=9 need=3.6; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 20 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 3
- route: none -> none -> none -> 4-2
- initial hand: PL!N-PR-009 優木せつ菜 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-006 津島善子 cost=11 | PL!N-bp1-017 宮下愛 cost=4
- mulligan target: 20 / 20 / 20
- mulligan score: 18.424 p(T1/T2/T3)=[0.245, 0.308, 0.369] draw_windows=[7, 9, 11]
- critical focus: T1 bottleneck key focus_costs=[20] turn_access=0.245 key_total=2 all-redraw-p=0.245 two-keep-p=0.178 gap=0.066
- keep: none
- return: PL!N-PR-009 優木せつ菜 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-006 津島善子 cost=11 | PL!N-bp1-017 宮下愛 cost=4
- redraw: PL!S-bp2-006 津島善子 cost=11 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-PR-025 高海千歌 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!SP-sd1-020 鬼塚夏美 cost=2 | PL!HS-bp2-002 村野さやか cost=13
- post mulligan hand: PL!S-bp2-006 津島善子 cost=11 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-PR-025 高海千歌 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!SP-sd1-020 鬼塚夏美 cost=2 | PL!HS-bp2-002 村野さやか cost=13
- hand need score: PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!N-bp1-017 宮下愛 cost=4 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-014 渡辺曜 cost=4 need=0.0; PL!S-bp3-025 SUKI for you, DREAM for you! score=5 need=0.0
- mulligan candidate comparison:
  - score=18.424 p(T1/T2/T3)=0.245/0.308/0.369 keep=none
  - score=15.477 p(T1/T2/T3)=0.212/0.277/0.339 keep=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
  - score=15.477 p(T1/T2/T3)=0.212/0.277/0.339 keep=PL!S-bp2-006 津島善子 cost=11
  - score=12.539 p(T1/T2/T3)=0.178/0.245/0.308 keep=PL!S-bp3-025 SUKI for you, DREAM for you! score=5; PL!S-bp2-006 津島善子 cost=11
  - score=5.277 p(T1/T2/T3)=0.212/0.277/0.339 keep=PL!N-PR-009 優木せつ菜 cost=2

#### T1 target 20 accepted 20
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-022 未熟DREAMER score=5
- live set selected: PL!S-bp2-022 未熟DREAMER score=5 | PL!S-PR-025 高海千歌 cost=2 | PL!SP-sd1-020 鬼塚夏美 cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp2-022 未熟DREAMER score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!HS-bp2-002 村野さやか cost=13 need=0.0; PL!S-PR-025 高海千歌 cost=2 need=0.0; PL!S-bp2-001 高海千歌 cost=9 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-022 未熟DREAMER score=5 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 20 accepted 20
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!S-bp2-014 渡辺曜 cost=4
- live set selected: PL!N-bp3-022 三船栞子 cost=4 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-bp2-006 津島善子 cost=11 need=8.1; PL!HS-bp2-002 村野さやか cost=13 need=5.4; PL!S-bp2-005 渡辺曜 cost=13 need=5.4; PL!S-bp2-001 高海千歌 cost=9 need=4.63; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 20 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 20 accepted 20
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!HS-bp2-002 村野さやか cost=13
- live set selected: PL!N-bp3-022 三船栞子 cost=4 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-bp2-001 高海千歌 cost=9
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=74.0; PL!SP-pb1-018 米女メイ cost=2 need=7.47; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!HS-bp2-002 村野さやか cost=13 need=4.2; PL!HS-bp2-002 村野さやか cost=13 need=4.2; PL!S-bp2-005 渡辺曜 cost=13 need=4.2
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 20 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 4
- route: none -> none -> none -> 2-2
- initial hand: PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-014 渡辺曜 cost=4 | PL!HS-bp2-002 村野さやか cost=13 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!SP-pb1-018 米女メイ cost=2 | PL!SP-pb1-018 米女メイ cost=2
- mulligan target: 20 / 20 / 20
- mulligan score: 32.575 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- keep: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- return: PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-014 渡辺曜 cost=4 | PL!HS-bp2-002 村野さやか cost=13 | PL!SP-pb1-018 米女メイ cost=2 | PL!SP-pb1-018 米女メイ cost=2
- redraw: PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-022 未熟DREAMER score=5 | PL!S-PR-029 渡辺曜 cost=9 | PL!S-bp2-006 津島善子 cost=11 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- post mulligan hand: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-022 未熟DREAMER score=5 | PL!S-PR-029 渡辺曜 cost=9 | PL!S-bp2-006 津島善子 cost=11 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- hand need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!HS-bp2-002 村野さやか cost=13 need=0.0; PL!S-bp2-014 渡辺曜 cost=4 need=0.0; PL!SP-pb1-018 米女メイ cost=2 need=0.0; PL!SP-pb1-018 米女メイ cost=2 need=0.0
- mulligan candidate comparison:
  - score=32.575 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-bp2-024 君のこころは輝いてるかい？ score=0; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-bp2-014 渡辺曜 cost=4; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!HS-bp2-002 村野さやか cost=13; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!SP-pb1-018 米女メイ cost=2

#### T1 target 20 accepted 20
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-006 津島善子 cost=11
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-022 未熟DREAMER score=5
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!S-PR-017 渡辺曜 cost=4 need=0.0; PL!S-PR-029 渡辺曜 cost=9 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-022 未熟DREAMER score=5 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 20 accepted 20
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!SP-pb1-018 米女メイ cost=2
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-PR-029 渡辺曜 cost=9 | PL!S-PR-029 渡辺曜 cost=9
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=118.0; PL!SP-pb1-018 米女メイ cost=2 need=9.6; PL!S-bp2-006 津島善子 cost=11 need=8.1; PL!S-bp2-006 津島善子 cost=11 need=8.1; PL!HS-bp2-002 村野さやか cost=13 need=5.4; PL!S-PR-029 渡辺曜 cost=9 need=4.63
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 20 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 20 accepted 20
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!HS-bp2-002 村野さやか cost=13
- live set selected: PL!N-bp1-017 宮下愛 cost=4 | PL!HS-bp2-002 村野さやか cost=13 | PL!HS-bp2-002 村野さやか cost=13
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=74.0; PL!S-PR-025 高海千歌 cost=2 need=7.47; PL!SP-pb1-018 米女メイ cost=2 need=7.47; PL!SP-sd1-020 鬼塚夏美 cost=2 need=7.47; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-006 津島善子 cost=11 need=6.3
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 20 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 5
- route: none -> none -> none -> 2-2
- initial hand: PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-025 高海千歌 cost=2 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-006 津島善子 cost=11 | PL!S-bp2-022 未熟DREAMER score=5
- mulligan target: 20 / 20 / 20
- mulligan score: 18.424 p(T1/T2/T3)=[0.245, 0.308, 0.369] draw_windows=[7, 9, 11]
- critical focus: T1 bottleneck key focus_costs=[20] turn_access=0.245 key_total=2 all-redraw-p=0.245 two-keep-p=0.178 gap=0.066
- keep: none
- return: PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-025 高海千歌 cost=2 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-006 津島善子 cost=11 | PL!S-bp2-022 未熟DREAMER score=5
- redraw: PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-PR-025 高海千歌 cost=2 | PL!N-bp3-022 三船栞子 cost=4
- post mulligan hand: PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-PR-025 高海千歌 cost=2 | PL!N-bp3-022 三船栞子 cost=4
- hand need score: PL!S-PR-025 高海千歌 cost=2 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-006 津島善子 cost=11 need=0.0; PL!S-bp2-014 渡辺曜 cost=4 need=0.0; PL!S-bp2-022 未熟DREAMER score=5 need=0.0; PL!S-bp2-023 MY舞☆TONIGHT score=3 need=0.0
- mulligan candidate comparison:
  - score=18.424 p(T1/T2/T3)=0.245/0.308/0.369 keep=none
  - score=15.477 p(T1/T2/T3)=0.212/0.277/0.339 keep=PL!S-bp2-006 津島善子 cost=11
  - score=15.477 p(T1/T2/T3)=0.212/0.277/0.339 keep=PL!S-bp2-023 MY舞☆TONIGHT score=3
  - score=15.477 p(T1/T2/T3)=0.212/0.277/0.339 keep=PL!S-bp2-006 津島善子 cost=11
  - score=15.477 p(T1/T2/T3)=0.212/0.277/0.339 keep=PL!S-bp2-022 未熟DREAMER score=5

#### T1 target 20 accepted 20
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-005 渡辺曜 cost=13
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-PR-025 高海千歌 cost=2 | PL!N-bp3-022 三船栞子 cost=4
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp2-023 MY舞☆TONIGHT score=3
- pre-exchange need score: PL!N-bp3-022 三船栞子 cost=4 need=0.0; PL!S-PR-025 高海千歌 cost=2 need=0.0; PL!S-bp2-001 高海千歌 cost=9 need=0.0; PL!S-bp2-005 渡辺曜 cost=13 need=0.0; PL!S-bp2-014 渡辺曜 cost=4 need=0.0; PL!S-bp2-014 渡辺曜 cost=4 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 20 accepted 20
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!N-PR-009 優木せつ菜 cost=2
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-017 渡辺曜 cost=4
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: PL!N-PR-009 優木せつ菜 cost=2 need=9.6; PL!S-bp2-005 渡辺曜 cost=13 need=5.4; PL!S-bp2-001 高海千歌 cost=9 need=4.63; PL!N-bp3-022 三船栞子 cost=4 need=2.31; PL!S-PR-017 渡辺曜 cost=4 need=2.31; PL!S-bp2-014 渡辺曜 cost=4 need=2.31
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 20 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 20 accepted 20
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-014 渡辺曜 cost=4
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!N-PR-009 優木せつ菜 cost=2 need=7.47; PL!HS-bp2-002 村野さやか cost=13 need=4.2; PL!S-bp2-005 渡辺曜 cost=13 need=4.2; PL!S-bp2-001 高海千歌 cost=9 need=3.6; PL!S-bp2-001 高海千歌 cost=9 need=3.6; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 20 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
