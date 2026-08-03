# Autoplay Policy Report: 10軸青紫

- model: `stage1_policy_template`
- recommended: 2-2 -> 2-4-2 -> 2-10-2

## Cost Bands

- 2-4: 29
- 5-10: 4
- 11-14: 11
- 15+: 4

## Progressions

- 2-2 -> 2-4-2 -> 2-10-2: score=84.0 coverage=1.0 turns=2-2 / 2-4-2 / 2-10-2 missing=なし
- 4 -> 2-4-2 -> 2-10-2: score=74.0 coverage=1.0 turns=4 / 2-4-2 / 2-10-2 missing=なし

## Special Signals

### エネルギー追加ライブ
- PL!N-bp4-030 Daydream Mermaid x4 score=3

### エネルギーアクティブ化
- PL!N-bp1-006 近江彼方 x2 cost=13
- PL!N-pb1-010 三船栞子 x3 cost=10

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
- PL!N-bp1-012 鐘嵐珠 x2 cost=15
- PL!N-pb1-011 ミア・テイラー x2 cost=15

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 200
- seed: base=29 effective=4040449618
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 2-2 -> 2-4-2 -> 2-10-2
- late policy: 未判定
- target turns: 2-2 / 2-4-2 / 2-10-2 / 15-4-2
- accepted targets: 2-2 or 4 / 2-4-2 / 2-10-2 or 2-11-2 or 2-13-2 / 15-4-2 or 15-2-2

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
  - 2-2: PL!-bp3-012 南ことり route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場
  - 4: PL!HS-PR-018 大沢瑠璃乃 route=手札から通常登場
- T2
  - 2-4-2: PL!HS-PR-018 大沢瑠璃乃 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場
- T3
  - 2-10-2: PL!N-bp3-009 天王寺璃奈 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場
  - 2-11-2: PL!-pb1-015 西木野真姫 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場
  - 2-13-2: PL!N-bp1-006 近江彼方 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場
- T4
  - 15-4-2: PL!N-bp1-012 鐘嵐珠 route=手札から通常登場 / PL!HS-PR-018 大沢瑠璃乃 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場
  - 15-2-2: PL!N-bp1-012 鐘嵐珠 route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場 / PL!-bp3-012 南ことり route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=2-2 hit_rate=0.985 cumulative=0.985 combined_cumulative=0.505 avg_stage_cost=3.97
- T2: target=2-4-2 hit_rate=0.8 cumulative=0.8 combined_cumulative=0.3 avg_stage_cost=7.57
- T3: target=2-10-2 hit_rate=0.74 cumulative=0.74 combined_cumulative=0.065 avg_stage_cost=13.12
- T4: target=15-4-2 hit_rate=0.545 cumulative=0.485 combined_cumulative=0.0 avg_stage_cost=15.8

### Live Score Targets

- T1: target_score=1 accepted=[1, 2, 3, 5] hit_rate=0.515 cumulative=0.515 cards=PL!N-bp1-026 Poppin' Up! score=1 / PL!N-bp4-029 Rise Up High! score=1 / PL!N-bp4-029 Rise Up High! score=1
- T2: target_score=2 accepted=[2, 3, 5] hit_rate=0.705 cumulative=0.39 cards=PL!N-bp3-032 THE SECRET NiGHT score=2
- T3: target_score=5 accepted=[5] hit_rate=0.14 cumulative=0.075 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5
- T4: target_score=5 accepted=[5] hit_rate=0.17 cumulative=0.01 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5

### Top Routes

- 2-2 / 4-2-2 / 11-2-2 / 15-2-2: 48 (0.24)
- 2-2 / 4-2-2 / 10-2-2 / 15-2-2: 46 (0.23)
- 2-2 / 4-2-2 / 11-2-2 / 11-2-2: 25 (0.125)
- 2-2 / 4-2-2 / 10-2-2 / 10-2-2: 24 (0.12)
- 2-2 / 2-2 / 2-2 / 2-2: 16 (0.08)
- 2-2 / 4-2-2 / 4-2-2 / 4-2-2: 12 (0.06)
- 4 / 4-4 / 11-4 / 15-4-4: 4 (0.02)
- 4 / 4-4 / 10-4 / 15-4-2: 4 (0.02)
- 4 / 4-2-2 / 11-2-2 / 15-2-2: 3 (0.015)
- 4 / 4-4 / 10-4 / 15-4: 2 (0.01)

### Miss Reasons

- T1: missing 2 3 (0.015)
- T2: missing 2 21 (0.105), missing 4 18 (0.09), missing 2-2 1 (0.005)
- T3: missing 10 31 (0.155), missing 2 21 (0.105)
- T4: missing 15 87 (0.435), missing 2 4 (0.02)

### Sample Routes

- T1: 2-2 -> 4-2-2 -> 11-2-2 -> 11-2-2
- T2: 2-2 -> 4-2-2 -> 11-2-2 -> 11-2-2
- T3: 2-2 -> 4-2-2 -> 10-2-2 -> 15-2-2
- T4: 2-2 -> 4-2-2 -> 11-2-2 -> 15-2-2
- T5: 2-2 -> 4-2-2 -> 10-2-2 -> 10-2-2

## Decision Trace

### Trial 1
- route: 2-2 -> 4-2-2 -> 11-2-2 -> 11-2-2
- initial hand: PL!N-sd1-006 近江彼方 cost=2 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!HS-PR-026 村野さやか cost=2 | PL!HS-PR-018 大沢瑠璃乃 cost=4 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-pb1-011 ミア・テイラー cost=15
- mulligan target: 2-2 / 4 / 2-4-2 / 2-10-2 / 2-11-2 / 2-13-2
- mulligan score: 54.918 p(T1/T2/T3)=[1.0, 0.958, 0.973] draw_windows=[6, 8, 10]
- critical focus: T2 bottleneck key focus_costs=[] turn_access=0.642 key_total=4 all-redraw-p=0.642 two-keep-p=0.482 gap=0.16
- keep: PL!HS-PR-018 大沢瑠璃乃 cost=4
- return: PL!N-sd1-006 近江彼方 cost=2 | PL!N-pb1-011 ミア・テイラー cost=15 | PL!HS-PR-026 村野さやか cost=2 | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-pb1-011 ミア・テイラー cost=15
- redraw: PL!N-bp1-029 Eutopia score=5 | PL!-pb1-015 西木野真姫 cost=11 | PL!SP-sd1-019 若菜四季 cost=2 | PL!HS-PR-026 村野さやか cost=2 | PL!N-bp1-029 Eutopia score=5
- post mulligan hand: PL!HS-PR-018 大沢瑠璃乃 cost=4 | PL!N-bp1-029 Eutopia score=5 | PL!-pb1-015 西木野真姫 cost=11 | PL!SP-sd1-019 若菜四季 cost=2 | PL!HS-PR-026 村野さやか cost=2 | PL!N-bp1-029 Eutopia score=5
- hand need score: PL!HS-PR-018 大沢瑠璃乃 cost=4 need=21.77; PL!N-pb1-011 ミア・テイラー cost=15 need=21.6; PL!N-pb1-011 ミア・テイラー cost=15 need=21.6; PL!HS-PR-026 村野さやか cost=2 need=7.85; PL!N-sd1-006 近江彼方 cost=2 need=7.85; PL!SP-sd1-019 若菜四季 cost=2 need=7.85
- mulligan candidate comparison:
  - score=54.918 p(T1/T2/T3)=1.0/0.958/0.973 keep=PL!HS-PR-018 大沢瑠璃乃 cost=4
  - score=48.982 p(T1/T2/T3)=1.0/0.991/0.96 keep=PL!N-sd1-006 近江彼方 cost=2; PL!HS-PR-018 大沢瑠璃乃 cost=4
  - score=48.982 p(T1/T2/T3)=1.0/0.991/0.96 keep=PL!HS-PR-026 村野さやか cost=2; PL!HS-PR-018 大沢瑠璃乃 cost=4
  - score=48.982 p(T1/T2/T3)=1.0/0.991/0.96 keep=PL!HS-PR-018 大沢瑠璃乃 cost=4; PL!SP-sd1-019 若菜四季 cost=2
  - score=44.682 p(T1/T2/T3)=1.0/1.0/0.941 keep=PL!N-sd1-006 近江彼方 cost=2; PL!HS-PR-026 村野さやか cost=2; PL!HS-PR-018 大沢瑠璃乃 cost=4

#### T1 target 2-2 accepted 2-2 / 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!N-pb1-005 宮下愛 cost=2
- live set selected: PL!N-bp1-029 Eutopia score=5 | PL!N-bp1-029 Eutopia score=5 | PL!HS-PR-026 村野さやか cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!N-bp1-029 Eutopia score=5
- pre-exchange need score: PL!HS-PR-018 大沢瑠璃乃 cost=4 need=21.77; PL!-pb1-015 西木野真姫 cost=11 need=14.0; PL!HS-PR-026 村野さやか cost=2 need=7.85; PL!N-pb1-005 宮下愛 cost=2 need=7.85; PL!SP-sd1-019 若菜四季 cost=2 need=7.85; PL!N-bp1-029 Eutopia score=5 need=0.0
- main stage: none -> 2-2
- main played/replaced in: PL!SP-sd1-019 若菜四季 cost=2 | PL!N-pb1-005 宮下愛 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 2-4-2 accepted 2-4-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!HS-PR-018 大沢瑠璃乃 cost=4
- live set selected: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- live set reason: prefer_energy_boost=True target_score=2 live_for_success=PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- pre-exchange need score: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!HS-PR-018 大沢瑠璃乃 cost=4 need=23.03; PL!HS-PR-018 大沢瑠璃乃 cost=4 need=23.03; PL!-pb1-015 西木野真姫 cost=11 need=13.02; PL!-pb1-015 西木野真姫 cost=11 need=13.02
- main stage: 2-2 -> 4-2-2
- main played/replaced in: PL!HS-PR-018 大沢瑠璃乃 cost=4
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 1, 'wait': 4, 'deck_remaining': 7}
- result: stage=4-2-2 stage_hit=True live_score_hit=True miss=none energy_added=1 end_energy={'active': 1, 'wait': 5, 'deck_remaining': 6}

#### T3 target 2-10-2 accepted 2-10-2 / 2-11-2 / 2-13-2
- start stage: 4-2-2
- start energy: {'active': 1, 'wait': 5, 'deck_remaining': 6}
- normal draw: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate
- live set selected: PL!N-bp1-029 Eutopia score=5 | PL!-pb1-015 西木野真姫 cost=11
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!N-bp1-029 Eutopia score=5
- pre-exchange need score: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=35.3; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=18.0; PL!HS-PR-018 大沢瑠璃乃 cost=4 need=12.11; PL!-pb1-015 西木野真姫 cost=11 need=9.91; PL!-pb1-015 西木野真姫 cost=11 need=9.91; PL!N-bp1-029 Eutopia score=5 need=0.0
- main stage: 4-2-2 -> 11-2-2
- main played/replaced in: PL!-pb1-015 西木野真姫 cost=11
- main replaced out: PL!HS-PR-018 大沢瑠璃乃 cost=4
- main energy: {'active': 7, 'wait': 0, 'deck_remaining': 5} -> {'active': 0, 'wait': 7, 'deck_remaining': 5}
- result: stage=11-2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 7, 'deck_remaining': 5}
### Trial 2
- route: 2-2 -> 4-2-2 -> 11-2-2 -> 11-2-2
- initial hand: PL!N-bp1-029 Eutopia score=5 | PL!S-pb1-017 小原鞠莉 cost=4 | PL!-pb1-024 西木野真姫 cost=2 | PL!HS-PR-023 桂城泉 cost=11 | PL!-pb1-015 西木野真姫 cost=11 | PL!N-bp1-006 近江彼方 cost=13 tags=energy_activate
- mulligan target: 2-2 / 4 / 2-4-2 / 2-10-2 / 2-11-2 / 2-13-2
- mulligan score: 54.347 p(T1/T2/T3)=[1.0, 0.975, 0.938] draw_windows=[6, 8, 10]
- critical focus: T2 bottleneck key focus_costs=[] turn_access=0.659 key_total=4 all-redraw-p=0.659 two-keep-p=0.51 gap=0.149
- keep: PL!S-pb1-017 小原鞠莉 cost=4
- return: PL!N-bp1-029 Eutopia score=5 | PL!-pb1-024 西木野真姫 cost=2 | PL!HS-PR-023 桂城泉 cost=11 | PL!-pb1-015 西木野真姫 cost=11 | PL!N-bp1-006 近江彼方 cost=13 tags=energy_activate
- redraw: PL!N-bp3-032 THE SECRET NiGHT score=2 | PL!HS-PR-026 村野さやか cost=2 | PL!N-pb1-005 宮下愛 cost=2 | PL!-pb1-015 西木野真姫 cost=11 | PL!HS-PR-023 桂城泉 cost=11
- post mulligan hand: PL!S-pb1-017 小原鞠莉 cost=4 | PL!N-bp3-032 THE SECRET NiGHT score=2 | PL!HS-PR-026 村野さやか cost=2 | PL!N-pb1-005 宮下愛 cost=2 | PL!-pb1-015 西木野真姫 cost=11 | PL!HS-PR-023 桂城泉 cost=11
- hand need score: PL!N-bp1-006 近江彼方 cost=13 tags=energy_activate need=84.0; PL!S-pb1-017 小原鞠莉 cost=4 need=21.77; PL!-pb1-015 西木野真姫 cost=11 need=14.0; PL!HS-PR-023 桂城泉 cost=11 need=14.0; PL!-pb1-024 西木野真姫 cost=2 need=7.85; PL!N-bp1-029 Eutopia score=5 need=0.0
- mulligan candidate comparison:
  - score=54.347 p(T1/T2/T3)=1.0/0.975/0.938 keep=PL!S-pb1-017 小原鞠莉 cost=4
  - score=51.194 p(T1/T2/T3)=1.0/0.95/0.916 keep=PL!N-bp1-029 Eutopia score=5; PL!S-pb1-017 小原鞠莉 cost=4
  - score=48.313 p(T1/T2/T3)=1.0/0.995/0.916 keep=PL!S-pb1-017 小原鞠莉 cost=4; PL!-pb1-024 西木野真姫 cost=2
  - score=45.378 p(T1/T2/T3)=1.0/0.989/0.887 keep=PL!N-bp1-029 Eutopia score=5; PL!S-pb1-017 小原鞠莉 cost=4; PL!-pb1-024 西木野真姫 cost=2
  - score=44.13 p(T1/T2/T3)=1.0/0.995/1.0 keep=PL!S-pb1-017 小原鞠莉 cost=4; PL!HS-PR-023 桂城泉 cost=11

#### T1 target 2-2 accepted 2-2 / 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- live set selected: PL!N-bp3-032 THE SECRET NiGHT score=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!N-bp3-032 THE SECRET NiGHT score=2
- pre-exchange need score: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!S-pb1-017 小原鞠莉 cost=4 need=21.77; PL!-pb1-015 西木野真姫 cost=11 need=14.0; PL!HS-PR-023 桂城泉 cost=11 need=14.0; PL!HS-PR-026 村野さやか cost=2 need=7.85; PL!N-pb1-005 宮下愛 cost=2 need=7.85
- main stage: none -> 2-2
- main played/replaced in: PL!HS-PR-026 村野さやか cost=2 | PL!N-pb1-005 宮下愛 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 2-4-2 accepted 2-4-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!N-sd1-006 近江彼方 cost=2
- live set selected: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost | PL!N-sd1-006 近江彼方 cost=2 | PL!N-sd1-006 近江彼方 cost=2
- live set reason: prefer_energy_boost=True target_score=2 live_for_success=PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- pre-exchange need score: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!S-pb1-017 小原鞠莉 cost=4 need=23.03; PL!-pb1-015 西木野真姫 cost=11 need=13.02; PL!HS-PR-023 桂城泉 cost=11 need=13.02; PL!N-sd1-006 近江彼方 cost=2 need=7.85; PL!N-sd1-006 近江彼方 cost=2 need=7.85
- main stage: 2-2 -> 4-2-2
- main played/replaced in: PL!S-pb1-017 小原鞠莉 cost=4 | PL!SP-sd1-019 若菜四季 cost=2
- main replaced out: PL!HS-PR-026 村野さやか cost=2
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 1, 'wait': 4, 'deck_remaining': 7}
- result: stage=4-2-2 stage_hit=True live_score_hit=True miss=none energy_added=1 end_energy={'active': 1, 'wait': 5, 'deck_remaining': 6}

#### T3 target 2-10-2 accepted 2-10-2 / 2-11-2 / 2-13-2
- start stage: 4-2-2
- start energy: {'active': 1, 'wait': 5, 'deck_remaining': 6}
- normal draw: PL!HS-PR-018 大沢瑠璃乃 cost=4
- live set selected: PL!-pb1-015 西木野真姫 cost=11 | PL!HS-PR-023 桂城泉 cost=11
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!HS-PR-018 大沢瑠璃乃 cost=4 need=12.11; PL!S-pb1-017 小原鞠莉 cost=4 need=12.11; PL!-pb1-015 西木野真姫 cost=11 need=9.91; PL!HS-PR-023 桂城泉 cost=11 need=9.91; PL!HS-PR-023 桂城泉 cost=11 need=9.91
- main stage: 4-2-2 -> 11-2-2
- main played/replaced in: PL!HS-PR-023 桂城泉 cost=11
- main replaced out: PL!S-pb1-017 小原鞠莉 cost=4
- main energy: {'active': 7, 'wait': 0, 'deck_remaining': 5} -> {'active': 0, 'wait': 7, 'deck_remaining': 5}
- result: stage=11-2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 7, 'deck_remaining': 5}
### Trial 3
- route: 2-2 -> 4-2-2 -> 10-2-2 -> 15-2-2
- initial hand: PL!N-bp3-030 Love U my friends score=3 | PL!HS-PR-018 大沢瑠璃乃 cost=4 | PL!S-pb1-017 小原鞠莉 cost=4 | PL!HS-PR-018 大沢瑠璃乃 cost=4 | PL!N-bp4-029 Rise Up High! score=1 | PL!-bp3-012 南ことり cost=2
- mulligan target: 2-2 / 4 / 2-4-2 / 2-10-2 / 2-11-2 / 2-13-2
- mulligan score: 53.516 p(T1/T2/T3)=[1.0, 0.958, 0.973] draw_windows=[6, 8, 10]
- critical focus: T2 bottleneck key focus_costs=[] turn_access=0.499 key_total=4 all-redraw-p=0.499 two-keep-p=0.365 gap=0.134
- keep: PL!HS-PR-018 大沢瑠璃乃 cost=4
- return: PL!N-bp3-030 Love U my friends score=3 | PL!S-pb1-017 小原鞠莉 cost=4 | PL!HS-PR-018 大沢瑠璃乃 cost=4 | PL!N-bp4-029 Rise Up High! score=1 | PL!-bp3-012 南ことり cost=2
- redraw: PL!SP-sd1-019 若菜四季 cost=2 | PL!HS-PR-026 村野さやか cost=2 | PL!N-bp4-017 宮下愛 cost=2 | PL!N-bp1-026 Poppin' Up! score=1 | PL!N-bp1-029 Eutopia score=5
- post mulligan hand: PL!HS-PR-018 大沢瑠璃乃 cost=4 | PL!SP-sd1-019 若菜四季 cost=2 | PL!HS-PR-026 村野さやか cost=2 | PL!N-bp4-017 宮下愛 cost=2 | PL!N-bp1-026 Poppin' Up! score=1 | PL!N-bp1-029 Eutopia score=5
- hand need score: PL!HS-PR-018 大沢瑠璃乃 cost=4 need=21.77; PL!HS-PR-018 大沢瑠璃乃 cost=4 need=21.77; PL!S-pb1-017 小原鞠莉 cost=4 need=21.77; PL!-bp3-012 南ことり cost=2 need=7.85; PL!N-bp3-030 Love U my friends score=3 need=0.0; PL!N-bp4-029 Rise Up High! score=1 need=0.0
- mulligan candidate comparison:
  - score=53.516 p(T1/T2/T3)=1.0/0.958/0.973 keep=PL!HS-PR-018 大沢瑠璃乃 cost=4
  - score=53.516 p(T1/T2/T3)=1.0/0.958/0.973 keep=PL!S-pb1-017 小原鞠莉 cost=4
  - score=53.516 p(T1/T2/T3)=1.0/0.958/0.973 keep=PL!HS-PR-018 大沢瑠璃乃 cost=4
  - score=50.432 p(T1/T2/T3)=1.0/0.924/0.96 keep=PL!N-bp3-030 Love U my friends score=3; PL!HS-PR-018 大沢瑠璃乃 cost=4
  - score=50.432 p(T1/T2/T3)=1.0/0.924/0.96 keep=PL!N-bp3-030 Love U my friends score=3; PL!S-pb1-017 小原鞠莉 cost=4

#### T1 target 2-2 accepted 2-2 / 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!N-sd1-004 朝香果林 cost=11
- live set selected: PL!N-bp1-029 Eutopia score=5 | PL!N-bp1-026 Poppin' Up! score=1 | PL!HS-PR-026 村野さやか cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!N-bp1-029 Eutopia score=5
- pre-exchange need score: PL!HS-PR-018 大沢瑠璃乃 cost=4 need=21.77; PL!N-sd1-004 朝香果林 cost=11 need=14.0; PL!HS-PR-026 村野さやか cost=2 need=7.85; PL!N-bp4-017 宮下愛 cost=2 need=7.85; PL!SP-sd1-019 若菜四季 cost=2 need=7.85; PL!N-bp1-026 Poppin' Up! score=1 need=0.0
- main stage: none -> 2-2
- main played/replaced in: PL!SP-sd1-019 若菜四季 cost=2 | PL!N-bp4-017 宮下愛 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 2-4-2 accepted 2-4-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!-pb1-024 西木野真姫 cost=2
- live set selected: PL!-pb1-024 西木野真姫 cost=2 | PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=True target_score=2 live_for_success=none
- pre-exchange need score: PL!N-bp1-006 近江彼方 cost=13 tags=energy_activate need=71.6; PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=42.3; PL!HS-PR-018 大沢瑠璃乃 cost=4 need=23.03; PL!N-sd1-004 朝香果林 cost=11 need=13.02; PL!-pb1-024 西木野真姫 cost=2 need=7.85; PL!SP-pb1-014 嵐千砂都 cost=2 need=7.85
- main stage: 2-2 -> 4-2-2
- main played/replaced in: PL!HS-PR-018 大沢瑠璃乃 cost=4
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 1, 'wait': 4, 'deck_remaining': 7}
- result: stage=4-2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 1, 'wait': 4, 'deck_remaining': 7}

#### T3 target 2-10-2 accepted 2-10-2 / 2-11-2 / 2-13-2
- start stage: 4-2-2
- start energy: {'active': 1, 'wait': 4, 'deck_remaining': 7}
- normal draw: PL!SP-pb1-014 嵐千砂都 cost=2
- live set selected: PL!SP-pb1-014 嵐千砂都 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!N-bp1-006 近江彼方 cost=13 tags=energy_activate need=57.6; PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=35.3; PL!N-bp1-012 鐘嵐珠 cost=15 need=21.2; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=18.0; PL!N-sd1-004 朝香果林 cost=11 need=9.91; PL!SP-pb1-014 嵐千砂都 cost=2 need=4.91
- main stage: 4-2-2 -> 10-2-2
- main played/replaced in: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate
- main replaced out: PL!HS-PR-018 大沢瑠璃乃 cost=4
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 0, 'wait': 6, 'deck_remaining': 6}
- result: stage=10-2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 6, 'deck_remaining': 6}
### Trial 4
- route: 2-2 -> 4-2-2 -> 11-2-2 -> 15-2-2
- initial hand: PL!N-pb1-005 宮下愛 cost=2 | PL!HS-PR-023 桂城泉 cost=11 | PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost | PL!N-bp1-012 鐘嵐珠 cost=15 | PL!N-bp1-029 Eutopia score=5 | PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- mulligan target: 2-2 / 4 / 2-4-2 / 2-10-2 / 2-11-2 / 2-13-2
- mulligan score: 32.179 p(T1/T2/T3)=[1.0, 0.96, 0.999] draw_windows=[5, 7, 9]
- critical focus: T3 bottleneck key focus_costs=[10, 13] turn_access=0.975 key_total=6 all-redraw-p=0.975 two-keep-p=0.945 gap=0.031
- keep: PL!HS-PR-023 桂城泉 cost=11 | PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- return: PL!N-pb1-005 宮下愛 cost=2 | PL!N-bp1-012 鐘嵐珠 cost=15 | PL!N-bp1-029 Eutopia score=5 | PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- redraw: PL!N-bp1-012 鐘嵐珠 cost=15 | PL!N-pb1-005 宮下愛 cost=2 | PL!N-bp3-030 Love U my friends score=3 | PL!HS-PR-023 桂城泉 cost=11
- post mulligan hand: PL!HS-PR-023 桂城泉 cost=11 | PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost | PL!N-bp1-012 鐘嵐珠 cost=15 | PL!N-pb1-005 宮下愛 cost=2 | PL!N-bp3-030 Love U my friends score=3 | PL!HS-PR-023 桂城泉 cost=11
- hand need score: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!N-bp1-012 鐘嵐珠 cost=15 need=21.6; PL!HS-PR-023 桂城泉 cost=11 need=14.0; PL!N-pb1-005 宮下愛 cost=2 need=7.85; PL!N-bp1-029 Eutopia score=5 need=0.0
- mulligan candidate comparison:
  - score=32.179 p(T1/T2/T3)=1.0/0.96/0.999 keep=PL!HS-PR-023 桂城泉 cost=11; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
  - score=32.179 p(T1/T2/T3)=1.0/0.96/0.999 keep=PL!HS-PR-023 桂城泉 cost=11; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
  - score=30.592 p(T1/T2/T3)=0.938/0.656/0.963 keep=PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
  - score=30.592 p(T1/T2/T3)=0.938/0.656/0.963 keep=PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
  - score=30.551 p(T1/T2/T3)=1.0/0.92/0.998 keep=PL!HS-PR-023 桂城泉 cost=11; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost; PL!N-bp1-029 Eutopia score=5

#### T1 target 2-2 accepted 2-2 / 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!HS-PR-026 村野さやか cost=2
- live set selected: PL!N-bp3-030 Love U my friends score=3
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!N-bp3-030 Love U my friends score=3
- pre-exchange need score: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!N-bp1-012 鐘嵐珠 cost=15 need=21.6; PL!HS-PR-023 桂城泉 cost=11 need=14.0; PL!HS-PR-023 桂城泉 cost=11 need=14.0; PL!HS-PR-026 村野さやか cost=2 need=7.85; PL!N-pb1-005 宮下愛 cost=2 need=7.85
- main stage: none -> 2-2
- main played/replaced in: PL!N-pb1-005 宮下愛 cost=2 | PL!HS-PR-026 村野さやか cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 2-4-2 accepted 2-4-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!N-bp3-032 THE SECRET NiGHT score=2
- live set selected: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost | PL!N-bp3-032 THE SECRET NiGHT score=2
- live set reason: prefer_energy_boost=True target_score=2 live_for_success=PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- pre-exchange need score: PL!N-bp1-012 鐘嵐珠 cost=15 need=39.5; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=30.0; PL!S-pb1-017 小原鞠莉 cost=4 need=23.03; PL!HS-PR-023 桂城泉 cost=11 need=13.02; PL!HS-PR-023 桂城泉 cost=11 need=13.02; PL!N-bp3-032 THE SECRET NiGHT score=2 need=0.0
- main stage: 2-2 -> 4-2-2
- main played/replaced in: PL!S-pb1-017 小原鞠莉 cost=4
- main replaced out: none
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 1, 'wait': 4, 'deck_remaining': 7}
- result: stage=4-2-2 stage_hit=True live_score_hit=True miss=none energy_added=1 end_energy={'active': 1, 'wait': 5, 'deck_remaining': 6}

#### T3 target 2-10-2 accepted 2-10-2 / 2-11-2 / 2-13-2
- start stage: 4-2-2
- start energy: {'active': 1, 'wait': 5, 'deck_remaining': 6}
- normal draw: PL!N-bp1-029 Eutopia score=5
- live set selected: PL!N-bp1-029 Eutopia score=5 | PL!N-bp4-029 Rise Up High! score=1 | PL!HS-PR-023 桂城泉 cost=11
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!N-bp1-029 Eutopia score=5
- pre-exchange need score: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=35.3; PL!N-bp1-012 鐘嵐珠 cost=15 need=21.2; PL!HS-PR-023 桂城泉 cost=11 need=9.91; PL!HS-PR-023 桂城泉 cost=11 need=9.91; PL!N-bp1-029 Eutopia score=5 need=0.0; PL!N-bp4-029 Rise Up High! score=1 need=0.0
- main stage: 4-2-2 -> 11-2-2
- main played/replaced in: PL!HS-PR-023 桂城泉 cost=11
- main replaced out: PL!S-pb1-017 小原鞠莉 cost=4
- main energy: {'active': 7, 'wait': 0, 'deck_remaining': 5} -> {'active': 0, 'wait': 7, 'deck_remaining': 5}
- result: stage=11-2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 7, 'deck_remaining': 5}
### Trial 5
- route: 2-2 -> 4-2-2 -> 10-2-2 -> 10-2-2
- initial hand: PL!HS-PR-026 村野さやか cost=2 | PL!-pb1-015 西木野真姫 cost=11 | PL!N-bp3-009 天王寺璃奈 cost=10 | PL!N-bp1-012 鐘嵐珠 cost=15 | PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate | PL!N-pb1-011 ミア・テイラー cost=15
- mulligan target: 2-2 / 4 / 2-4-2 / 2-10-2 / 2-11-2 / 2-13-2
- mulligan score: 66.202 p(T1/T2/T3)=[1.0, 0.996, 1.0] draw_windows=[5, 7, 9]
- critical focus: T2 bottleneck key focus_costs=[] turn_access=0.721 key_total=4 all-redraw-p=0.721 two-keep-p=0.573 gap=0.148
- keep: PL!HS-PR-026 村野さやか cost=2 | PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate
- return: PL!-pb1-015 西木野真姫 cost=11 | PL!N-bp3-009 天王寺璃奈 cost=10 | PL!N-bp1-012 鐘嵐珠 cost=15 | PL!N-pb1-011 ミア・テイラー cost=15
- redraw: PL!SP-sd1-019 若菜四季 cost=2 | PL!N-sd1-006 近江彼方 cost=2 | PL!N-bp1-029 Eutopia score=5 | PL!S-pb1-017 小原鞠莉 cost=4
- post mulligan hand: PL!HS-PR-026 村野さやか cost=2 | PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate | PL!SP-sd1-019 若菜四季 cost=2 | PL!N-sd1-006 近江彼方 cost=2 | PL!N-bp1-029 Eutopia score=5 | PL!S-pb1-017 小原鞠莉 cost=4
- hand need score: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=52.5; PL!N-bp3-009 天王寺璃奈 cost=10 need=39.5; PL!N-bp1-012 鐘嵐珠 cost=15 need=21.6; PL!N-pb1-011 ミア・テイラー cost=15 need=21.6; PL!-pb1-015 西木野真姫 cost=11 need=14.0; PL!HS-PR-026 村野さやか cost=2 need=7.85
- mulligan candidate comparison:
  - score=66.202 p(T1/T2/T3)=1.0/0.996/1.0 keep=PL!HS-PR-026 村野さやか cost=2; PL!N-bp3-009 天王寺璃奈 cost=10
  - score=66.202 p(T1/T2/T3)=1.0/0.996/1.0 keep=PL!HS-PR-026 村野さやか cost=2; PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate
  - score=62.671 p(T1/T2/T3)=1.0/0.981/1.0 keep=PL!N-bp3-009 天王寺璃奈 cost=10
  - score=62.671 p(T1/T2/T3)=1.0/0.981/1.0 keep=PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate
  - score=57.315 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!HS-PR-026 村野さやか cost=2; PL!N-bp3-009 天王寺璃奈 cost=10; PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate

#### T1 target 2-2 accepted 2-2 / 4
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!HS-PR-026 村野さやか cost=2
- live set selected: PL!N-bp1-029 Eutopia score=5 | PL!HS-PR-026 村野さやか cost=2 | PL!HS-PR-026 村野さやか cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!N-bp1-029 Eutopia score=5
- pre-exchange need score: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=52.5; PL!S-pb1-017 小原鞠莉 cost=4 need=21.77; PL!HS-PR-026 村野さやか cost=2 need=7.85; PL!HS-PR-026 村野さやか cost=2 need=7.85; PL!N-sd1-006 近江彼方 cost=2 need=7.85; PL!SP-sd1-019 若菜四季 cost=2 need=7.85
- main stage: none -> 2-2
- main played/replaced in: PL!SP-sd1-019 若菜四季 cost=2 | PL!N-sd1-006 近江彼方 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 2-4-2 accepted 2-4-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!HS-PR-018 大沢瑠璃乃 cost=4
- live set selected: PL!N-bp3-032 THE SECRET NiGHT score=2 | PL!N-sd1-006 近江彼方 cost=2
- live set reason: prefer_energy_boost=True target_score=2 live_for_success=PL!N-bp3-032 THE SECRET NiGHT score=2
- pre-exchange need score: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=42.3; PL!HS-PR-018 大沢瑠璃乃 cost=4 need=23.03; PL!S-pb1-017 小原鞠莉 cost=4 need=23.03; PL!-pb1-015 西木野真姫 cost=11 need=13.02; PL!N-sd1-006 近江彼方 cost=2 need=7.85; PL!N-bp3-032 THE SECRET NiGHT score=2 need=0.0
- main stage: 2-2 -> 4-2-2
- main played/replaced in: PL!S-pb1-017 小原鞠莉 cost=4 | PL!N-pb1-005 宮下愛 cost=2
- main replaced out: PL!SP-sd1-019 若菜四季 cost=2
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 1, 'wait': 4, 'deck_remaining': 7}
- result: stage=4-2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 1, 'wait': 4, 'deck_remaining': 7}

#### T3 target 2-10-2 accepted 2-10-2 / 2-11-2 / 2-13-2
- start stage: 4-2-2
- start energy: {'active': 1, 'wait': 4, 'deck_remaining': 7}
- normal draw: PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost
- live set selected: PL!N-bp3-030 Love U my friends score=3
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate need=35.3; PL!N-bp4-030 Daydream Mermaid score=3 tags=energy_boost need=18.0; PL!HS-PR-018 大沢瑠璃乃 cost=4 need=12.11; PL!-pb1-015 西木野真姫 cost=11 need=9.91; PL!N-bp3-030 Love U my friends score=3 need=0.0
- main stage: 4-2-2 -> 10-2-2
- main played/replaced in: PL!N-pb1-010 三船栞子 cost=10 tags=energy_activate
- main replaced out: PL!S-pb1-017 小原鞠莉 cost=4
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 0, 'wait': 6, 'deck_remaining': 6}
- result: stage=10-2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 6, 'deck_remaining': 6}
