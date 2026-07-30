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

### コスト軽減
- なし

### 特殊バトンタッチ
- なし

### 15+高コスト
- PL!N-bp3-001 上原歩夢 x1 cost=15
- PL!N-pb1-011 ミア・テイラー x4 cost=15

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 800
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 未判定
- late policy: 未判定
- target turns: 15 / 15 / 15 / 15-4-2
- accepted targets: 15 / 15 / 15 / 15-4-2 or 15-2-2

### Effect Assumptions

- up to three cards are live-set exchanged before member planning, and each exchanged card draws one replacement
- live draw effects are modeled as hand smoothing after each turn
- Daydream-like energy boost live cards count as the 2-4-2 alternative bridge only when selected as the live-set card
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
- Member placement then chooses the available hand combination that best covers the turn's accepted target shapes within that turn's target budget: higher than target first, exact target second, then the largest available fallback.
- After live success, draw effects on the live-set card are modeled as hand smoothing for the following turn.

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
- T1: target=15 hit_rate=0.7412 cumulative=0.7412 combined_cumulative=0.5513 avg_stage_cost=33.51
- T2: target=15 hit_rate=0.83 cumulative=0.7412 combined_cumulative=0.3287 avg_stage_cost=34.69
- T3: target=15 hit_rate=0.8712 cumulative=0.7412 combined_cumulative=0.0675 avg_stage_cost=35.13
- T4: target=15-4-2 hit_rate=0.885 cumulative=0.7412 combined_cumulative=0.0063 avg_stage_cost=35.94

### Live Score Targets

- T1: target_score=1 accepted=[1, 3, 4, 5] hit_rate=0.7788 cumulative=0.7788 cards=PL!N-bp1-026 Poppin' Up! score=1 / PL!N-bp1-026 Poppin' Up! score=1 / PL!N-bp1-026 Poppin' Up! score=1
- T2: target_score=3 accepted=[3, 4, 5] hit_rate=0.62 cumulative=0.5038 cards=PL!N-bp3-030 Love U my friends score=3 / PL!N-bp3-030 Love U my friends score=3
- T3: target_score=5 accepted=[5] hit_rate=0.1938 cumulative=0.105 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp3-025 Awakening Promise score=5 / PL!N-bp3-025 Awakening Promise score=5
- T4: target_score=5 accepted=[5] hit_rate=0.0775 cumulative=0.0075 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp3-025 Awakening Promise score=5 / PL!N-bp3-025 Awakening Promise score=5

### Top Routes

- 15-15-13 / 15-15-13 / 15-15-13 / 15-15-13: 109 (0.1363)
- 15-15-15 / 15-15-15 / 15-15-15 / 15-15-15: 71 (0.0887)
- 15-13-13 / 15-13-13 / 15-13-13 / 15-13-13: 48 (0.06)
- 15-13-8 / 15-13-8 / 15-13-8 / 15-13-8: 40 (0.05)
- 15-13-11 / 15-13-11 / 15-13-11 / 15-13-11: 40 (0.05)
- 15-13-4 / 15-13-4 / 15-13-4 / 15-13-4: 36 (0.045)
- 15-15-11 / 15-15-11 / 15-15-11 / 15-15-11: 34 (0.0425)
- 15-8-4 / 15-8-4 / 15-8-4 / 15-8-4: 34 (0.0425)
- 15-15-8 / 15-15-8 / 15-15-8 / 15-15-8: 34 (0.0425)
- 15-4-4 / 15-4-4 / 15-4-4 / 15-4-4: 31 (0.0387)

### Miss Reasons

- T1: missing 15 207 (0.2587)
- T2: missing 15 136 (0.17)
- T3: missing 15 103 (0.1288)
- T4: missing 15 92 (0.115)

### Sample Routes

- T1: 15-15-11 -> 15-15-11 -> 15-15-11 -> 15-15-11
- T2: 15-11-4 -> 15-11-4 -> 15-11-4 -> 15-11-4
- T3: 15-15-13 -> 15-15-13 -> 15-15-13 -> 15-15-13
- T4: 15-15-13 -> 15-15-13 -> 15-15-13 -> 15-15-13
- T5: 13-8-4 -> 13-8-4 -> 13-8-4 -> 13-13-8
