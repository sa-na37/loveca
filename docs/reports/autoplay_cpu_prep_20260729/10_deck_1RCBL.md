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

### コスト軽減
- なし

### 特殊バトンタッチ
- なし

### 15+高コスト
- PL!N-bp1-012 鐘嵐珠 x2 cost=15
- PL!N-pb1-011 ミア・テイラー x2 cost=15

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 800
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 2-2 -> 2-4-2 -> 2-10-2
- late policy: 未判定
- target turns: 2-2 / 2-4-2 / 2-10-2 / 15-4-2
- accepted targets: 2-2 or 4 / 2-4-2 / 2-10-2 or 2-11-2 or 2-13-2 / 15-4-2 or 15-2-2

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
- T1: target=2-2 hit_rate=0.97 cumulative=0.97 combined_cumulative=0.17 avg_stage_cost=7.12
- T2: target=2-4-2 hit_rate=0.6763 cumulative=0.6763 combined_cumulative=0.0525 avg_stage_cost=7.7
- T3: target=2-10-2 hit_rate=0.98 cumulative=0.6575 combined_cumulative=0.0037 avg_stage_cost=24.18
- T4: target=15-4-2 hit_rate=0.5975 cumulative=0.37 combined_cumulative=0.0 avg_stage_cost=32.41

### Live Score Targets

- T1: target_score=1 accepted=[1, 2, 3, 5] hit_rate=0.1737 cumulative=0.1737 cards=PL!N-bp1-026 Poppin' Up! score=1 / PL!N-bp4-029 Rise Up High! score=1 / PL!N-bp4-029 Rise Up High! score=1
- T2: target_score=2 accepted=[2, 3, 5] hit_rate=0.525 cumulative=0.085 cards=PL!N-bp3-032 THE SECRET NiGHT score=2
- T3: target_score=5 accepted=[5] hit_rate=0.0813 cumulative=0.0112 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5
- T4: target_score=5 accepted=[5] hit_rate=0.0725 cumulative=0.0013 cards=PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5 / PL!N-bp1-029 Eutopia score=5

### Top Routes

- 4-2-2 / 4-2-2 / 13-4-2 / 15-13-4: 39 (0.0488)
- 4-2-2 / 4-2-2 / 11-11-4 / 15-11-11: 29 (0.0362)
- 4-2-2 / 4-2-2 / 11-10-4 / 15-11-10: 27 (0.0338)
- 4-2-2 / 4-2-2 / 13-4-2 / 13-11-11: 18 (0.0225)
- 4-4-2 / 4-4-2 / 13-4-4 / 15-13-4: 16 (0.02)
- 4-2-2 / 4-2-2 / 11-4-2 / 15-11-4: 16 (0.02)
- 2-2-2 / 2-2-2 / 13-2-2 / 15-13-2: 16 (0.02)
- 4-2-2 / 4-2-2 / 11-11-10 / 15-11-11: 15 (0.0187)
- 4-4-2 / 4-4-2 / 11-4-4 / 15-11-4: 14 (0.0175)
- 4-2-2 / 4-2-2 / 11-11-10 / 11-11-10: 14 (0.0175)

### Miss Reasons

- T1: missing 2 16 (0.02), missing 4 8 (0.01)
- T2: missing 4 216 (0.27), missing 2 27 (0.0338), missing 4-2 8 (0.01), missing 2-2 6 (0.0075), missing 4-2-2 2 (0.0025)
- T3: missing 10 16 (0.02)
- T4: missing 15 322 (0.4025)

### Sample Routes

- T1: 2-2 -> 2-2-2 -> 11-10-10 -> 15-11-10
- T2: 4-4-2 -> 4-4-2 -> 13-4-4 -> 15-13-4
- T3: 2-2 -> 2-2-2 -> 11-11-11 -> 15-11-11
- T4: 2-2 -> 2-2-2 -> 11-11-10 -> 15-11-11
- T5: 2-2-2 -> 2-2-2 -> 11-11-10 -> 11-11-11
