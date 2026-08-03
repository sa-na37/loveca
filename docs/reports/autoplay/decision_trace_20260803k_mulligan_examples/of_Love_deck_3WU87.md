# Autoplay Policy Report: サニパ of Love

- model: `stage1_policy_template`
- recommended: 未判定

## Cost Bands

- 2-4: 31
- 5-10: 4
- 11-14: 8
- 15+: 5

## Progressions


## Special Signals

### エネルギー追加ライブ
- なし

### エネルギーアクティブ化
- なし

### コスト軽減
- なし

### エネルギー支払いなし登場
- なし

### 支払い以上の登場
- なし

### 低コスト追加登場
- なし

### 特殊バトンタッチ
- なし

### 15+高コスト
- PL!N-bp3-001 上原歩夢 x1 cost=15
- PL!N-pb1-011 ミア・テイラー x4 cost=15

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 200
- seed: base=29 effective=965692310
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 未判定
- late policy: 未判定
- target turns: 15 / 15 / 15 / 15-4-2
- accepted targets: 15 / 15 / 15 / 15-4-2 or 15-2-2

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
  - 15: PL!N-bp3-001 上原歩夢 route=手札から通常登場
- T2
  - 15: PL!N-bp3-001 上原歩夢 route=手札から通常登場
- T3
  - 15: PL!N-bp3-001 上原歩夢 route=手札から通常登場
- T4
  - 15-4-2: PL!N-bp3-001 上原歩夢 route=手札から通常登場 / PL!N-bp4-013 上原歩夢 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場
  - 15-2-2: PL!N-bp3-001 上原歩夢 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=15 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=0.0
- T2: target=15 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=0.0
- T3: target=15 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=0.0
- T4: target=15-4-2 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=5.61

### Live Score Targets

- T1: target_score=1 accepted=[1, 3, 4, 5] hit_rate=0.74 cumulative=0.74 cards=PL!N-bp1-026 Poppin' Up! score=1 / PL!N-bp1-026 Poppin' Up! score=1 / PL!N-bp1-026 Poppin' Up! score=1
- T2: target_score=3 accepted=[3, 4, 5] hit_rate=0.675 cumulative=0.525 cards=PL!N-bp3-030 Love U my friends score=3 / PL!N-bp3-030 Love U my friends score=3
- T3: target_score=5 accepted=[5] hit_rate=0.265 cumulative=0.155 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp3-025 Awakening Promise score=5 / PL!N-bp3-025 Awakening Promise score=5
- T4: target_score=5 accepted=[5] hit_rate=0.215 cumulative=0.015 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp3-025 Awakening Promise score=5 / PL!N-bp3-025 Awakening Promise score=5

### Top Routes

- none / none / none / 4-2: 161 (0.805)
- none / none / none / 4: 37 (0.185)
- none / none / none / 2-2: 2 (0.01)

### Miss Reasons

- T1: missing 15 200 (1.0)
- T2: missing 15 200 (1.0)
- T3: missing 15 200 (1.0)
- T4: missing 15 163 (0.815), missing 15-2 37 (0.185)

### Sample Routes

- T1: none -> none -> none -> 4-2
- T2: none -> none -> none -> 4-2
- T3: none -> none -> none -> 4-2
- T4: none -> none -> none -> 4-2
- T5: none -> none -> none -> 4-2

## Decision Trace

### Trial 1
- route: none -> none -> none -> 4-2
- initial hand: PL!N-bp1-026 Poppin' Up! score=1 | PL!N-PR-014 鐘嵐珠 cost=2 | PL!-pb1-025 東條希 cost=2 | PL!N-bp4-013 上原歩夢 cost=4 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!SP-bp2-022 鬼塚冬毬 cost=4
- mulligan target: 15 / 15 / 15
- mulligan score: 32.575 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- keep: PL!N-pb1-011 ミア・テイラー cost=15
- return: PL!N-bp1-026 Poppin' Up! score=1 | PL!N-PR-014 鐘嵐珠 cost=2 | PL!-pb1-025 東條希 cost=2 | PL!N-bp4-013 上原歩夢 cost=4 | PL!SP-bp2-022 鬼塚冬毬 cost=4
- redraw: PL!-pb1-025 東條希 cost=2 | PL!SP-bp2-019 若菜四季 cost=4 | PL!SP-bp5-027 HOT PASSION!! score=4 | PL!-bp3-012 南ことり cost=2 | PL!-bp3-012 南ことり cost=2
- post mulligan hand: PL!N-pb1-011 ミア・テイラー cost=15 | PL!-pb1-025 東條希 cost=2 | PL!SP-bp2-019 若菜四季 cost=4 | PL!SP-bp5-027 HOT PASSION!! score=4 | PL!-bp3-012 南ことり cost=2 | PL!-bp3-012 南ことり cost=2
- hand need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!-pb1-025 東條希 cost=2 need=0.0; PL!N-PR-014 鐘嵐珠 cost=2 need=0.0; PL!N-bp1-026 Poppin' Up! score=1 need=0.0; PL!N-bp4-013 上原歩夢 cost=4 need=0.0; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=0.0
- mulligan candidate comparison:
  - score=32.575 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-bp1-026 Poppin' Up! score=1; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-PR-014 鐘嵐珠 cost=2; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!-pb1-025 東條希 cost=2; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-bp4-013 上原歩夢 cost=4; PL!N-pb1-011 ミア・テイラー cost=15

#### T1 target 15 accepted 15
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!N-bp1-026 Poppin' Up! score=1
- live set selected: PL!SP-bp5-027 HOT PASSION!! score=4 | PL!N-bp1-026 Poppin' Up! score=1 | PL!-bp3-012 南ことり cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!SP-bp5-027 HOT PASSION!! score=4
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!SP-bp5-027 HOT PASSION!! score=4 need=2.5; PL!-bp3-012 南ことり cost=2 need=0.0; PL!-bp3-012 南ことり cost=2 need=0.0; PL!-pb1-025 東條希 cost=2 need=0.0; PL!N-bp1-026 Poppin' Up! score=1 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 15 accepted 15
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!SP-pb1-014 嵐千砂都 cost=2
- live set selected: PL!-bp3-012 南ことり cost=2 | PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=none
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-PR-028 宮下愛 cost=11 need=10.8; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=8.1; PL!N-bp4-013 上原歩夢 cost=4 need=6.55; PL!SP-bp2-019 若菜四季 cost=4 need=6.55; PL!-bp3-012 南ことり cost=2 need=3.24
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!SP-sd1-019 若菜四季 cost=2
- live set selected: PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2 | PL!SP-sd1-019 若菜四季 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=24.0; PL!N-PR-028 宮下愛 cost=11 need=8.4; PL!N-PR-028 宮下愛 cost=11 need=8.4; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=6.3; PL!N-bp4-013 上原歩夢 cost=4 need=5.09; PL!N-bp4-013 上原歩夢 cost=4 need=5.09
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 2
- route: none -> none -> none -> 4-2
- initial hand: PL!N-bp4-013 上原歩夢 cost=4 | PL!N-PR-028 宮下愛 cost=11 | PL!N-PR-009 優木せつ菜 cost=2 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-bp1-026 Poppin' Up! score=1
- mulligan target: 15 / 15 / 15
- mulligan score: 32.575 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- keep: PL!N-pb1-011 ミア・テイラー cost=15
- return: PL!N-bp4-013 上原歩夢 cost=4 | PL!N-PR-028 宮下愛 cost=11 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-bp1-026 Poppin' Up! score=1
- redraw: PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost | PL!SP-bp5-027 HOT PASSION!! score=4 | PL!N-bp4-013 上原歩夢 cost=4 | PL!SP-bp2-019 若菜四季 cost=4 | PL!-pb1-025 東條希 cost=2
- post mulligan hand: PL!N-pb1-011 ミア・テイラー cost=15 | PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost | PL!SP-bp5-027 HOT PASSION!! score=4 | PL!N-bp4-013 上原歩夢 cost=4 | PL!SP-bp2-019 若菜四季 cost=4 | PL!-pb1-025 東條希 cost=2
- hand need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!N-PR-028 宮下愛 cost=11 need=0.0; PL!N-bp1-026 Poppin' Up! score=1 need=0.0; PL!N-bp4-013 上原歩夢 cost=4 need=0.0; PL!SP-sd1-019 若菜四季 cost=2 need=0.0
- mulligan candidate comparison:
  - score=32.575 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-bp4-013 上原歩夢 cost=4; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-PR-028 宮下愛 cost=11; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-PR-009 優木せつ菜 cost=2; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15; PL!SP-sd1-019 若菜四季 cost=2

#### T1 target 15 accepted 15
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!SP-pb1-014 嵐千砂都 cost=2
- live set selected: PL!SP-bp5-027 HOT PASSION!! score=4 | PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!SP-bp5-027 HOT PASSION!! score=4
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!SP-bp5-027 HOT PASSION!! score=4 need=2.5; PL!-pb1-025 東條希 cost=2 need=0.0; PL!N-bp4-013 上原歩夢 cost=4 need=0.0; PL!SP-bp2-019 若菜四季 cost=4 need=0.0; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 15 accepted 15
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!SP-bp2-022 鬼塚冬毬 cost=4
- live set selected: PL!N-bp1-029 Eutopia score=5 | PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!N-bp1-029 Eutopia score=5
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=8.1; PL!N-bp4-013 上原歩夢 cost=4 need=6.55; PL!SP-bp2-019 若菜四季 cost=4 need=6.55; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=6.55; PL!-pb1-025 東條希 cost=2 need=3.24
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!-pb1-025 東條希 cost=2
- live set selected: PL!N-bp1-026 Poppin' Up! score=1 | PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=24.0; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=6.3; PL!N-bp4-013 上原歩夢 cost=4 need=5.09; PL!SP-bp2-019 若菜四季 cost=4 need=5.09; PL!SP-bp2-019 若菜四季 cost=4 need=5.09; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=5.09
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 3
- route: none -> none -> none -> 4-2
- initial hand: PL!N-PR-009 優木せつ菜 cost=2 | PL!-bp3-012 南ことり cost=2 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!N-bp5-012 鐘嵐珠 cost=13
- mulligan target: 15 / 15 / 15
- mulligan score: 11.857 p(T1/T2/T3)=[0.515, 0.614, 0.696] draw_windows=[7, 9, 11]
- keep: none
- return: PL!N-PR-009 優木せつ菜 cost=2 | PL!-bp3-012 南ことり cost=2 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!N-bp5-012 鐘嵐珠 cost=13
- redraw: PL!SP-bp2-022 鬼塚冬毬 cost=4 | PL!SP-pb1-014 嵐千砂都 cost=2 | PL!SP-bp2-022 鬼塚冬毬 cost=4 | PL!SP-bp5-027 HOT PASSION!! score=4 | PL!-bp3-012 南ことり cost=2 | PL!N-bp3-001 上原歩夢 cost=15
- post mulligan hand: PL!SP-bp2-022 鬼塚冬毬 cost=4 | PL!SP-pb1-014 嵐千砂都 cost=2 | PL!SP-bp2-022 鬼塚冬毬 cost=4 | PL!SP-bp5-027 HOT PASSION!! score=4 | PL!-bp3-012 南ことり cost=2 | PL!N-bp3-001 上原歩夢 cost=15
- hand need score: PL!-bp3-012 南ことり cost=2 need=0.0; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!N-PR-028 宮下愛 cost=11 need=0.0; PL!N-bp5-012 鐘嵐珠 cost=13 need=0.0; PL!SP-sd1-019 若菜四季 cost=2 need=0.0
- mulligan candidate comparison:
  - score=11.857 p(T1/T2/T3)=0.515/0.614/0.696 keep=none
  - score=10.358 p(T1/T2/T3)=0.459/0.567/0.657 keep=PL!N-PR-009 優木せつ菜 cost=2
  - score=10.358 p(T1/T2/T3)=0.459/0.567/0.657 keep=PL!-bp3-012 南ことり cost=2
  - score=10.358 p(T1/T2/T3)=0.459/0.567/0.657 keep=PL!SP-sd1-019 若菜四季 cost=2
  - score=10.358 p(T1/T2/T3)=0.459/0.567/0.657 keep=PL!N-PR-009 優木せつ菜 cost=2

#### T1 target 15 accepted 15
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost
- live set selected: PL!SP-bp5-027 HOT PASSION!! score=4 | PL!-bp3-012 南ことり cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!SP-bp5-027 HOT PASSION!! score=4
- pre-exchange need score: PL!N-bp3-001 上原歩夢 cost=15 need=38.4; PL!SP-bp5-027 HOT PASSION!! score=4 need=2.5; PL!-bp3-012 南ことり cost=2 need=0.0; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=0.0; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=0.0; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 15 accepted 15
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!N-bp5-012 鐘嵐珠 cost=13
- live set selected: PL!-pb1-025 東條希 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!N-PR-009 優木せつ菜 cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=none
- pre-exchange need score: PL!N-bp3-001 上原歩夢 cost=15 need=38.4; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=8.1; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=6.55; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=6.55; PL!N-bp5-012 鐘嵐珠 cost=13 need=6.48; PL!-pb1-025 東條希 cost=2 need=3.24
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!SP-bp2-019 若菜四季 cost=4
- live set selected: PL!SP-pb1-014 嵐千砂都 cost=2 | PL!SP-bp5-027 HOT PASSION!! score=4 | PL!N-bp5-012 鐘嵐珠 cost=13
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!SP-bp5-027 HOT PASSION!! score=4
- pre-exchange need score: PL!N-bp3-001 上原歩夢 cost=15 need=24.0; PL!N-pb1-011 ミア・テイラー cost=15 need=24.0; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=6.3; PL!SP-bp2-019 若菜四季 cost=4 need=5.09; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=5.09; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=5.09
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 4
- route: none -> none -> none -> 4-2
- initial hand: PL!-pb1-025 東條希 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!-pb1-025 東條希 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-sd1-019 若菜四季 cost=2
- mulligan target: 15 / 15 / 15
- mulligan score: 32.575 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- keep: PL!N-pb1-011 ミア・テイラー cost=15
- return: PL!-pb1-025 東條希 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!-pb1-025 東條希 cost=2 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-sd1-019 若菜四季 cost=2
- redraw: PL!N-bp4-013 上原歩夢 cost=4 | PL!SP-sd1-019 若菜四季 cost=2 | PL!-pb1-025 東條希 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!SP-bp5-027 HOT PASSION!! score=4
- post mulligan hand: PL!N-pb1-011 ミア・テイラー cost=15 | PL!N-bp4-013 上原歩夢 cost=4 | PL!SP-sd1-019 若菜四季 cost=2 | PL!-pb1-025 東條希 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!SP-bp5-027 HOT PASSION!! score=4
- hand need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!-pb1-025 東條希 cost=2 need=0.0; PL!-pb1-025 東條希 cost=2 need=0.0; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!N-PR-028 宮下愛 cost=11 need=0.0; PL!SP-sd1-019 若菜四季 cost=2 need=0.0
- mulligan candidate comparison:
  - score=32.575 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!-pb1-025 東條希 cost=2; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-PR-028 宮下愛 cost=11; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15; PL!-pb1-025 東條希 cost=2
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15; PL!N-PR-009 優木せつ菜 cost=2

#### T1 target 15 accepted 15
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!SP-pb1-014 嵐千砂都 cost=2
- live set selected: PL!SP-bp5-027 HOT PASSION!! score=4 | PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!SP-bp5-027 HOT PASSION!! score=4
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!SP-bp5-027 HOT PASSION!! score=4 need=2.5; PL!-pb1-025 東條希 cost=2 need=0.0; PL!N-PR-028 宮下愛 cost=11 need=0.0; PL!N-bp4-013 上原歩夢 cost=4 need=0.0; PL!SP-pb1-014 嵐千砂都 cost=2 need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 15 accepted 15
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!N-pb1-011 ミア・テイラー cost=15
- live set selected: PL!N-bp3-030 Love U my friends score=3 | PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-sd1-019 若菜四季 cost=2
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!N-bp3-030 Love U my friends score=3
- pre-exchange need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-PR-028 宮下愛 cost=11 need=10.8; PL!N-bp4-013 上原歩夢 cost=4 need=6.55; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=6.55; PL!N-bp5-012 鐘嵐珠 cost=13 need=6.48
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!-bp3-012 南ことり cost=2
- live set selected: PL!N-bp1-029 Eutopia score=5 | PL!-bp3-012 南ことり cost=2 | PL!SP-sd1-019 若菜四季 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!N-bp1-029 Eutopia score=5
- pre-exchange need score: PL!N-bp3-001 上原歩夢 cost=15 need=24.0; PL!N-pb1-011 ミア・テイラー cost=15 need=24.0; PL!N-pb1-011 ミア・テイラー cost=15 need=24.0; PL!N-PR-028 宮下愛 cost=11 need=8.4; PL!N-bp4-013 上原歩夢 cost=4 need=5.09; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=5.09
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
### Trial 5
- route: none -> none -> none -> 4-2
- initial hand: PL!SP-bp2-019 若菜四季 cost=4 | PL!-bp3-012 南ことり cost=2 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2 | PL!SP-bp5-027 HOT PASSION!! score=4
- mulligan target: 15 / 15 / 15
- mulligan score: 32.575 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[6, 8, 10]
- keep: PL!N-pb1-011 ミア・テイラー cost=15
- return: PL!SP-bp2-019 若菜四季 cost=4 | PL!-bp3-012 南ことり cost=2 | PL!-pb1-025 東條希 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2 | PL!SP-bp5-027 HOT PASSION!! score=4
- redraw: PL!N-PR-009 優木せつ菜 cost=2 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!N-bp3-001 上原歩夢 cost=15
- post mulligan hand: PL!N-pb1-011 ミア・テイラー cost=15 | PL!N-PR-009 優木せつ菜 cost=2 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-PR-028 宮下愛 cost=11 | PL!N-bp3-001 上原歩夢 cost=15
- hand need score: PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!SP-bp5-027 HOT PASSION!! score=4 need=2.5; PL!-bp3-012 南ことり cost=2 need=0.0; PL!-pb1-025 東條希 cost=2 need=0.0; PL!SP-bp2-019 若菜四季 cost=4 need=0.0; PL!SP-pb1-014 嵐千砂都 cost=2 need=0.0
- mulligan candidate comparison:
  - score=32.575 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!SP-bp2-019 若菜四季 cost=4; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!-bp3-012 南ことり cost=2; PL!N-pb1-011 ミア・テイラー cost=15
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15; PL!-pb1-025 東條希 cost=2
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-pb1-011 ミア・テイラー cost=15; PL!SP-pb1-014 嵐千砂都 cost=2

#### T1 target 15 accepted 15
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost
- live set selected: PL!N-PR-009 優木せつ菜 cost=2 | PL!SP-sd1-019 若菜四季 cost=2 | PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=none
- pre-exchange need score: PL!N-bp3-001 上原歩夢 cost=15 need=38.4; PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-PR-009 優木せつ菜 cost=2 need=0.0; PL!N-PR-028 宮下愛 cost=11 need=0.0; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=0.0
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 4, 'wait': 0, 'deck_remaining': 8}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 4, 'wait': 0, 'deck_remaining': 8}

#### T2 target 15 accepted 15
- start stage: none
- start energy: {'active': 4, 'wait': 0, 'deck_remaining': 8}
- normal draw: PL!N-bp1-026 Poppin' Up! score=1
- live set selected: PL!N-bp3-025 Awakening Promise score=5 | PL!N-bp1-026 Poppin' Up! score=1 | PL!SP-bp2-022 鬼塚冬毬 cost=4
- live set reason: prefer_energy_boost=False target_score=3 live_for_success=PL!N-bp3-025 Awakening Promise score=5
- pre-exchange need score: PL!N-bp3-001 上原歩夢 cost=15 need=38.4; PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-pb1-011 ミア・テイラー cost=15 need=38.4; PL!N-PR-028 宮下愛 cost=11 need=10.8; PL!N-PR-028 宮下愛 cost=11 need=10.8; PL!SP-bp2-022 鬼塚冬毬 cost=4 need=6.55
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 5, 'wait': 0, 'deck_remaining': 7}
- result: stage=none stage_hit=False live_score_hit=True miss=missing 15 energy_added=0 end_energy={'active': 5, 'wait': 0, 'deck_remaining': 7}

#### T3 target 15 accepted 15
- start stage: none
- start energy: {'active': 5, 'wait': 0, 'deck_remaining': 7}
- normal draw: PL!-bp3-012 南ことり cost=2
- live set selected: PL!N-bp1-026 Poppin' Up! score=1 | PL!N-bp3-030 Love U my friends score=3 | PL!-bp3-012 南ことり cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!N-bp3-001 上原歩夢 cost=15 need=24.0; PL!N-pb1-011 ミア・テイラー cost=15 need=24.0; PL!N-pb1-011 ミア・テイラー cost=15 need=24.0; PL!N-PR-028 宮下愛 cost=11 need=8.4; PL!N-PR-028 宮下愛 cost=11 need=8.4; PL!SP-bp5-222 聖澤悠奈 cost=8 tags=energy_boost need=6.3
- main stage: none -> none
- main played/replaced in: none
- main replaced out: none
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 6, 'wait': 0, 'deck_remaining': 6}
- result: stage=none stage_hit=False live_score_hit=False miss=missing 15 energy_added=0 end_energy={'active': 6, 'wait': 0, 'deck_remaining': 6}
