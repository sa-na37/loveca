# Autoplay Policy Report: 三神 のコピー

- model: `stage1_policy_template`
- recommended: 4 -> 9 -> 15単騎

## Cost Bands

- 2-4: 28
- 5-10: 7
- 11-14: 10
- 15+: 3

## Progressions

- 4 -> 9 -> 15単騎: score=67.75 coverage=0.778 turns=4 / 9 / 15 missing=なし
- 4ターン目以降 15+単騎軸: score=63.75 coverage=0.722 turns=4 / 9 / 15 / 15 missing=15コストx1

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
- PL!S-bp7-005 渡辺曜 x1 cost=15

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 200
- seed: base=29 effective=799776334
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 4 -> 9 -> 15単騎
- late policy: 4ターン目以降 15+単騎軸
- target turns: 4 / 9 / 15 / 2-20-2
- accepted targets: 4 / 9 / 15 / 2-20-2

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
  - 4: PL!N-bp1-017 宮下愛 route=手札から通常登場
- T2
  - 9: PL!S-PR-029 渡辺曜 route=手札から通常登場
- T3
  - 15: PL!S-bp7-005 渡辺曜 route=手札から通常登場
- T4
  - 2-20-2: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補 / PL!N-PR-009 優木せつ菜 route=手札から通常登場 / PL!N-PR-009 優木せつ菜 route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=4 hit_rate=0.965 cumulative=0.965 combined_cumulative=0.715 avg_stage_cost=3.86
- T2: target=9 hit_rate=0.755 cumulative=0.755 combined_cumulative=0.155 avg_stage_cost=7.63
- T3: target=15 hit_rate=0.23 cumulative=0.23 combined_cumulative=0.0 avg_stage_cost=9.02
- T4: target=2-20-2 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=12.77

### Live Score Targets

- T1: target_score=3 accepted=[3, 5, 8] hit_rate=0.74 cumulative=0.74 cards=PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3
- T2: target_score=5 accepted=[5, 8] hit_rate=0.325 cumulative=0.23 cards=PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- T3: target_score=8 accepted=[8] hit_rate=0.12 cumulative=0.035 cards=PL!S-bp7-022 恋になりたいAQUARIUM score=8 / PL!S-bp7-022 恋になりたいAQUARIUM score=8
- T4: target_score=8 accepted=[8] hit_rate=0.155 cumulative=0.005 cards=PL!S-bp7-022 恋になりたいAQUARIUM score=8 / PL!S-bp7-022 恋になりたいAQUARIUM score=8

### Top Routes

- 4 / 9 / 9 / 9-4: 56 (0.28)
- 4 / 9 / 9 / 9-2: 48 (0.24)
- 4 / 9 / 15 / 20-2: 29 (0.145)
- 4 / 4 / 4 / 4-4: 27 (0.135)
- 4 / 4 / 4 / 4-2: 15 (0.075)
- 4 / 9 / 15 / 15-2: 8 (0.04)
- 4 / 9 / 15 / 15-4: 7 (0.035)
- none / none / none / 4-2: 6 (0.03)
- 4 / 9 / 15 / 15: 1 (0.005)
- 4 / 9 / 15 / 20: 1 (0.005)

### Miss Reasons

- T1: missing 4 7 (0.035)
- T2: missing 9 49 (0.245)
- T3: missing 15 154 (0.77)
- T4: missing 20 168 (0.84), missing 2 29 (0.145), missing 20-2 2 (0.01), missing 2-2 1 (0.005)

### Sample Routes

- T1: 4 -> 4 -> 4 -> 4-2
- T2: 4 -> 9 -> 9 -> 9-2
- T3: 4 -> 9 -> 9 -> 9-2
- T4: 4 -> 9 -> 9 -> 9-4
- T5: none -> none -> none -> 4-2

## Decision Trace

### Trial 1
- route: 4 -> 4 -> 4 -> 4-2
- initial hand: PL!S-PR-017 渡辺曜 cost=4 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-029 渡辺曜 cost=9
- mulligan target: 4 / 9 / 15
- mulligan score: 28.087 p(T1/T2/T3)=[1.0, 0.637, 0.185] draw_windows=[6, 8, 10]
- critical focus: T3 bottleneck key focus_costs=[15] turn_access=0.204 key_total=1 all-redraw-p=0.204 two-keep-p=0.167 gap=0.037
- keep: PL!S-PR-017 渡辺曜 cost=4
- return: PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-029 渡辺曜 cost=9
- redraw: PL!S-bp2-014 渡辺曜 cost=4 | PL!SP-pb1-018 米女メイ cost=2 | PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-025 高海千歌 cost=2 | PL!N-bp3-022 三船栞子 cost=4
- post mulligan hand: PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-014 渡辺曜 cost=4 | PL!SP-pb1-018 米女メイ cost=2 | PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-025 高海千歌 cost=2 | PL!N-bp3-022 三船栞子 cost=4
- hand need score: PL!S-PR-029 渡辺曜 cost=9 need=12.11; PL!N-bp3-022 三船栞子 cost=4 need=4.57; PL!N-bp3-022 三船栞子 cost=4 need=4.57; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!S-bp3-025 SUKI for you, DREAM for you! score=5 need=0.0
- mulligan candidate comparison:
  - score=28.087 p(T1/T2/T3)=1.0/0.637/0.185 keep=PL!S-PR-017 渡辺曜 cost=4
  - score=28.087 p(T1/T2/T3)=1.0/0.637/0.185 keep=PL!N-bp3-022 三船栞子 cost=4
  - score=28.087 p(T1/T2/T3)=1.0/0.637/0.185 keep=PL!S-PR-017 渡辺曜 cost=4
  - score=28.087 p(T1/T2/T3)=1.0/0.637/0.185 keep=PL!N-bp3-022 三船栞子 cost=4
  - score=27.982 p(T1/T2/T3)=1.0/1.0/0.185 keep=PL!S-PR-029 渡辺曜 cost=9

#### T1 target 4 accepted 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-005 渡辺曜 cost=13
- live set selected: PL!S-PR-025 高海千歌 cost=2 | PL!SP-pb1-018 米女メイ cost=2 | PL!N-bp3-022 三船栞子 cost=4
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=none
- pre-exchange need score: PL!S-bp2-006 津島善子 cost=11 need=13.5; PL!S-bp2-005 渡辺曜 cost=13 need=9.0; PL!N-bp3-022 三船栞子 cost=4 need=4.57; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!S-bp2-014 渡辺曜 cost=4 need=4.57; PL!S-PR-025 高海千歌 cost=2 need=0.0
- main stage: none -> 4
- main played/replaced in: PL!S-PR-017 渡辺曜 cost=4
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=4 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 9 accepted 9
- start stage: 4
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-014 渡辺曜 cost=4
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!N-PR-009 優木せつ菜 cost=2 need=10.29; PL!S-bp2-005 渡辺曜 cost=13 need=10.2; PL!S-bp2-014 渡辺曜 cost=4 need=2.31; PL!S-bp2-014 渡辺曜 cost=4 need=2.31; PL!S-bp2-014 渡辺曜 cost=4 need=2.31
- main stage: 4 -> 4
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=4 stage_hit=False live_score_hit=True miss=missing 9 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: 4
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!S-bp2-023 MY舞☆TONIGHT score=3
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-005 渡辺曜 cost=13
- live set reason: prefer_energy_boost=False target_score=8 live_for_success=none
- pre-exchange need score: PL!N-PR-009 優木せつ菜 cost=2 need=8.0; PL!S-PR-025 高海千歌 cost=2 need=8.0; PL!SP-pb1-018 米女メイ cost=2 need=8.0; PL!SP-pb1-018 米女メイ cost=2 need=8.0; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-005 渡辺曜 cost=13 need=4.2
- main stage: 4 -> 4
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=4 stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 2
- route: 4 -> 9 -> 9 -> 9-2
- initial hand: PL!HS-bp2-002 村野さやか cost=13 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-001 高海千歌 cost=9 | PL!SP-sd1-020 鬼塚夏美 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-pb1-018 米女メイ cost=2
- mulligan target: 4 / 9 / 15
- mulligan score: 27.982 p(T1/T2/T3)=[1.0, 1.0, 0.185] draw_windows=[6, 8, 10]
- critical focus: T3 bottleneck key focus_costs=[15] turn_access=0.204 key_total=1 all-redraw-p=0.204 two-keep-p=0.167 gap=0.037
- keep: PL!S-bp2-001 高海千歌 cost=9
- return: PL!HS-bp2-002 村野さやか cost=13 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!SP-sd1-020 鬼塚夏美 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-pb1-018 米女メイ cost=2
- redraw: PL!N-bp3-022 三船栞子 cost=4 | PL!S-bp2-014 渡辺曜 cost=4 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-pb1-018 米女メイ cost=2 | PL!S-PR-017 渡辺曜 cost=4
- post mulligan hand: PL!S-bp2-001 高海千歌 cost=9 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-bp2-014 渡辺曜 cost=4 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-pb1-018 米女メイ cost=2 | PL!S-PR-017 渡辺曜 cost=4
- hand need score: PL!S-bp2-001 高海千歌 cost=9 need=12.11; PL!HS-bp2-002 村野さやか cost=13 need=9.0; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!SP-pb1-018 米女メイ cost=2 need=0.0; PL!SP-sd1-020 鬼塚夏美 cost=2 need=0.0
- mulligan candidate comparison:
  - score=27.982 p(T1/T2/T3)=1.0/1.0/0.185 keep=PL!HS-bp2-002 村野さやか cost=13
  - score=27.982 p(T1/T2/T3)=1.0/1.0/0.185 keep=PL!S-bp2-001 高海千歌 cost=9
  - score=26.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!HS-bp2-002 村野さやか cost=13; PL!S-bp2-024 君のこころは輝いてるかい？ score=0
  - score=26.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!S-bp2-024 君のこころは輝いてるかい？ score=0; PL!S-bp2-001 高海千歌 cost=9
  - score=24.824 p(T1/T2/T3)=0.895/0.685/0.204 keep=none

#### T1 target 4 accepted 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp7-022 恋になりたいAQUARIUM score=8
- live set selected: PL!S-bp7-022 恋になりたいAQUARIUM score=8 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-pb1-018 米女メイ cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp7-022 恋になりたいAQUARIUM score=8
- pre-exchange need score: PL!S-bp2-001 高海千歌 cost=9 need=12.11; PL!N-bp3-022 三船栞子 cost=4 need=4.57; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!S-bp2-014 渡辺曜 cost=4 need=4.57; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!S-bp7-022 恋になりたいAQUARIUM score=8 need=0.0
- main stage: none -> 4
- main played/replaced in: PL!N-bp3-022 三船栞子 cost=4
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=4 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 9 accepted 9
- start stage: 4
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!N-bp3-022 三船栞子 cost=4
- live set selected: PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-014 渡辺曜 cost=4
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!S-bp2-001 高海千歌 cost=9 need=13.77; PL!SP-sd1-020 鬼塚夏美 cost=2 need=10.29; PL!N-bp3-022 三船栞子 cost=4 need=2.31; PL!S-PR-017 渡辺曜 cost=4 need=2.31
- main stage: 4 -> 9
- main played/replaced in: PL!S-bp2-001 高海千歌 cost=9
- main replaced out: PL!N-bp3-022 三船栞子 cost=4
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=9 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: 9
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: PL!SP-pb1-018 米女メイ cost=2
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-PR-025 高海千歌 cost=2
- live set reason: prefer_energy_boost=False target_score=8 live_for_success=none
- pre-exchange need score: PL!S-PR-025 高海千歌 cost=2 need=8.0; PL!SP-pb1-018 米女メイ cost=2 need=8.0; PL!SP-sd1-020 鬼塚夏美 cost=2 need=8.0; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-001 高海千歌 cost=9 need=3.6
- main stage: 9 -> 9
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=9 stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 3
- route: 4 -> 9 -> 9 -> 9-2
- initial hand: PL!S-PR-029 渡辺曜 cost=9 | PL!S-PR-017 渡辺曜 cost=4 | PL!SP-pb1-018 米女メイ cost=2 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-bp1-017 宮下愛 cost=4 | PL!S-bp2-006 津島善子 cost=11
- mulligan target: 4 / 9 / 15
- mulligan score: 33.982 p(T1/T2/T3)=[1.0, 1.0, 0.185] draw_windows=[6, 8, 10]
- critical focus: T3 bottleneck key focus_costs=[15] turn_access=0.204 key_total=1 all-redraw-p=0.204 two-keep-p=0.167 gap=0.037
- keep: PL!S-bp2-006 津島善子 cost=11
- return: PL!S-PR-029 渡辺曜 cost=9 | PL!S-PR-017 渡辺曜 cost=4 | PL!SP-pb1-018 米女メイ cost=2 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-bp1-017 宮下愛 cost=4
- redraw: PL!S-PR-017 渡辺曜 cost=4 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-PR-029 渡辺曜 cost=9
- post mulligan hand: PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-017 渡辺曜 cost=4 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-PR-029 渡辺曜 cost=9
- hand need score: PL!S-bp2-006 津島善子 cost=11 need=13.5; PL!S-PR-029 渡辺曜 cost=9 need=12.11; PL!N-bp1-017 宮下愛 cost=4 need=4.57; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!S-bp3-025 SUKI for you, DREAM for you! score=5 need=0.0; PL!SP-pb1-018 米女メイ cost=2 need=0.0
- mulligan candidate comparison:
  - score=33.982 p(T1/T2/T3)=1.0/1.0/0.185 keep=PL!S-bp2-006 津島善子 cost=11
  - score=32.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!S-PR-017 渡辺曜 cost=4; PL!S-bp2-006 津島善子 cost=11
  - score=32.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!S-bp3-025 SUKI for you, DREAM for you! score=5; PL!S-bp2-006 津島善子 cost=11
  - score=32.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!N-bp1-017 宮下愛 cost=4; PL!S-bp2-006 津島善子 cost=11
  - score=31.575 p(T1/T2/T3)=1.0/1.0/0.148 keep=PL!S-PR-017 渡辺曜 cost=4; PL!S-bp3-025 SUKI for you, DREAM for you! score=5; PL!S-bp2-006 津島善子 cost=11

#### T1 target 4 accepted 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-001 高海千歌 cost=9
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-PR-009 優木せつ菜 cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!S-bp2-006 津島善子 cost=11 need=13.5; PL!S-PR-029 渡辺曜 cost=9 need=12.11; PL!S-bp2-001 高海千歌 cost=9 need=12.11; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!N-PR-009 優木せつ菜 cost=2 need=0.0
- main stage: none -> 4
- main played/replaced in: PL!S-PR-017 渡辺曜 cost=4
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=4 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 9 accepted 9
- start stage: 4
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!S-bp2-001 高海千歌 cost=9
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=85.0; PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!S-PR-029 渡辺曜 cost=9 need=13.77; PL!S-bp2-001 高海千歌 cost=9 need=13.77; PL!S-bp2-001 高海千歌 cost=9 need=13.77; PL!S-bp2-001 高海千歌 cost=9 need=13.77
- main stage: 4 -> 9
- main played/replaced in: PL!S-PR-029 渡辺曜 cost=9
- main replaced out: PL!S-PR-017 渡辺曜 cost=4
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=9 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: 9
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: PL!S-bp2-014 渡辺曜 cost=4
- live set selected: PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-001 高海千歌 cost=9 | PL!S-bp2-001 高海千歌 cost=9
- live set reason: prefer_energy_boost=False target_score=8 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=56.4; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-001 高海千歌 cost=9 need=3.6; PL!S-bp2-001 高海千歌 cost=9 need=3.6; PL!S-bp2-001 高海千歌 cost=9 need=3.6
- main stage: 9 -> 9
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=9 stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 4
- route: 4 -> 9 -> 9 -> 9-4
- initial hand: PL!S-PR-017 渡辺曜 cost=4 | PL!S-bp2-006 津島善子 cost=11 | PL!N-bp1-017 宮下愛 cost=4 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- mulligan target: 4 / 9 / 15
- mulligan score: 33.982 p(T1/T2/T3)=[1.0, 1.0, 0.185] draw_windows=[6, 8, 10]
- critical focus: T3 bottleneck key focus_costs=[15] turn_access=0.204 key_total=1 all-redraw-p=0.204 two-keep-p=0.167 gap=0.037
- keep: PL!S-bp2-006 津島善子 cost=11
- return: PL!S-PR-017 渡辺曜 cost=4 | PL!N-bp1-017 宮下愛 cost=4 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- redraw: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-017 渡辺曜 cost=4 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-029 渡辺曜 cost=9
- post mulligan hand: PL!S-bp2-006 津島善子 cost=11 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-006 津島善子 cost=11 | PL!S-PR-017 渡辺曜 cost=4 | PL!N-bp3-022 三船栞子 cost=4 | PL!S-PR-029 渡辺曜 cost=9
- hand need score: PL!S-bp2-006 津島善子 cost=11 need=13.5; PL!N-bp1-017 宮下愛 cost=4 need=4.57; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!S-bp2-023 MY舞☆TONIGHT score=3 need=0.0
- mulligan candidate comparison:
  - score=33.982 p(T1/T2/T3)=1.0/1.0/0.185 keep=PL!S-bp2-006 津島善子 cost=11
  - score=32.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!S-PR-017 渡辺曜 cost=4; PL!S-bp2-006 津島善子 cost=11
  - score=32.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!S-bp2-006 津島善子 cost=11; PL!N-bp1-017 宮下愛 cost=4
  - score=32.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!S-bp2-006 津島善子 cost=11; PL!S-bp2-023 MY舞☆TONIGHT score=3
  - score=32.779 p(T1/T2/T3)=1.0/1.0/0.167 keep=PL!S-bp2-006 津島善子 cost=11; PL!S-bp2-024 君のこころは輝いてるかい？ score=0

#### T1 target 4 accepted 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-023 MY舞☆TONIGHT score=3
- live set selected: PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!N-bp3-022 三船栞子 cost=4
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp2-023 MY舞☆TONIGHT score=3
- pre-exchange need score: PL!S-bp2-006 津島善子 cost=11 need=13.5; PL!S-bp2-006 津島善子 cost=11 need=13.5; PL!S-PR-029 渡辺曜 cost=9 need=12.11; PL!N-bp3-022 三船栞子 cost=4 need=4.57; PL!S-PR-017 渡辺曜 cost=4 need=4.57; PL!S-bp2-023 MY舞☆TONIGHT score=3 need=0.0
- main stage: none -> 4
- main played/replaced in: PL!S-PR-017 渡辺曜 cost=4
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=4 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 9 accepted 9
- start stage: 4
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!S-bp2-006 津島善子 cost=11
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-PR-009 優木せつ菜 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!S-PR-029 渡辺曜 cost=9 need=13.77; PL!N-PR-009 優木せつ菜 cost=2 need=10.29; PL!HS-bp2-002 村野さやか cost=13 need=10.2
- main stage: 4 -> 9
- main played/replaced in: PL!S-PR-029 渡辺曜 cost=9
- main replaced out: PL!S-PR-017 渡辺曜 cost=4
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=9 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: 9
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: PL!S-PR-017 渡辺曜 cost=4
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-PR-017 渡辺曜 cost=4 | PL!HS-bp2-002 村野さやか cost=13
- live set reason: prefer_energy_boost=False target_score=8 live_for_success=none
- pre-exchange need score: PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!HS-bp2-002 村野さやか cost=13 need=4.2; PL!S-bp2-005 渡辺曜 cost=13 need=4.2; PL!S-PR-017 渡辺曜 cost=4 need=1.8
- main stage: 9 -> 9
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=9 stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 5
- route: none -> none -> none -> 4-2
- initial hand: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp2-005 渡辺曜 cost=13 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!HS-bp2-002 村野さやか cost=13 | PL!N-bp3-022 三船栞子 cost=4
- mulligan target: 4 / 9 / 15
- mulligan score: 38.056 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- critical focus: T3 bottleneck key focus_costs=[15] turn_access=0.204 key_total=1 all-redraw-p=0.204 two-keep-p=0.167 gap=0.037
- keep: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- return: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp2-005 渡辺曜 cost=13 | PL!HS-bp2-002 村野さやか cost=13 | PL!N-bp3-022 三船栞子 cost=4
- redraw: PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!SP-sd1-020 鬼塚夏美 cost=2 | PL!S-PR-029 渡辺曜 cost=9
- post mulligan hand: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!N-PR-009 優木せつ菜 cost=2 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!SP-sd1-020 鬼塚夏美 cost=2 | PL!S-PR-029 渡辺曜 cost=9
- hand need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!HS-bp2-002 村野さやか cost=13 need=9.0; PL!S-bp2-005 渡辺曜 cost=13 need=9.0; PL!N-bp3-022 三船栞子 cost=4 need=4.57; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!S-bp3-025 SUKI for you, DREAM for you! score=5 need=0.0
- mulligan candidate comparison:
  - score=38.056 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=36.945 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-bp3-025 SUKI for you, DREAM for you! score=5; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=36.945 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!N-bp3-022 三船栞子 cost=4
  - score=35.834 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-bp3-025 SUKI for you, DREAM for you! score=5; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!N-bp3-022 三船栞子 cost=4
  - score=30.945 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-PR-009 優木せつ菜 cost=2; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction

#### T1 target 4 accepted 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-023 MY舞☆TONIGHT score=3
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-sd1-020 鬼塚夏美 cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!S-PR-029 渡辺曜 cost=9 need=12.11; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!S-bp2-023 MY舞☆TONIGHT score=3 need=0.0; PL!S-bp3-025 SUKI for you, DREAM for you! score=5 need=0.0; PL!S-bp3-025 SUKI for you, DREAM for you! score=5 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 4 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 9 accepted 9
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!HS-bp2-002 村野さやか cost=13
- live set selected: PL!S-bp3-025 SUKI for you, DREAM for you! score=5 | PL!S-bp2-023 MY舞☆TONIGHT score=3 | PL!S-PR-025 高海千歌 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=85.0; PL!S-bp2-006 津島善子 cost=11 need=15.3; PL!S-PR-029 渡辺曜 cost=9 need=13.77; PL!S-bp2-001 高海千歌 cost=9 need=13.77; PL!S-PR-025 高海千歌 cost=2 need=10.29; PL!HS-bp2-002 村野さやか cost=13 need=10.2
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 9 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!HS-bp2-002 村野さやか cost=13
- live set selected: PL!S-bp2-014 渡辺曜 cost=4 | PL!S-bp2-014 渡辺曜 cost=4 | PL!S-PR-029 渡辺曜 cost=9
- live set reason: prefer_energy_boost=False target_score=8 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=56.4; PL!S-bp2-006 津島善子 cost=11 need=6.3; PL!HS-bp2-002 村野さやか cost=13 need=4.2; PL!HS-bp2-002 村野さやか cost=13 need=4.2; PL!S-PR-029 渡辺曜 cost=9 need=3.6; PL!S-PR-029 渡辺曜 cost=9 need=3.6
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
