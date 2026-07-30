# Autoplay Policy Report: 推し活

- model: `stage1_policy_template`
- recommended: 4 -> 9 -> 15単騎

## Cost Bands

- 2-4: 23
- 5-10: 7
- 11-14: 9
- 15+: 9

## Progressions

- 4 -> 9 -> 15単騎: score=89.5 coverage=1.0 turns=4 / 9 / 15 missing=なし
- 4ターン目以降 15+単騎軸: score=77.5 coverage=0.833 turns=4 / 9 / 15 / 15 missing=なし

## Special Signals

### コスト軽減
- なし

### 特殊バトンタッチ
- なし

### 15+高コスト
- PL!-PR-015 西木野真姫 x3 cost=17
- PL!-bp4-002 絢瀬絵里 x1 cost=15
- PL!-bp6-003 南ことり x2 cost=15
- PL!-bp6-006 西木野真姫 x3 cost=17

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 800
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 4 -> 9 -> 15単騎
- late policy: 4ターン目以降 15+単騎軸
- target turns: 4 / 9 / 15 / 2-17-2
- accepted targets: 4 / 9 / 15 / 2-17-2

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
  - 4: PL!-bp3-015 西木野真姫 route=手札から通常登場
- T2
  - 9: PL!-PR-006 西木野真姫 route=手札から通常登場
- T3
  - 15: PL!-bp4-002 絢瀬絵里 route=手札から通常登場
- T4
  - 2-17-2: PL!-PR-015 西木野真姫 route=手札から通常登場 / PL!-bp3-009 矢澤にこ route=手札から通常登場 / PL!-bp5-006 西木野真姫 route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=4 hit_rate=0.675 cumulative=0.675 combined_cumulative=0.3638 avg_stage_cost=4.42
- T2: target=9 hit_rate=0.835 cumulative=0.54 combined_cumulative=0.1025 avg_stage_cost=16.21
- T3: target=15 hit_rate=0.5663 cumulative=0.2787 combined_cumulative=0.0013 avg_stage_cost=28.09
- T4: target=2-17-2 hit_rate=0.8588 cumulative=0.215 combined_cumulative=0.0 avg_stage_cost=39.01

### Live Score Targets

- T1: target_score=2 accepted=[2, 3, 6, 7, 9] hit_rate=0.5025 cumulative=0.5025 cards=PL!-bp6-019 Music S.T.A.R.T!! score=2 / PL!-bp6-019 Music S.T.A.R.T!! score=2 / PL!-bp6-019 Music S.T.A.R.T!! score=2 / PL!-bp6-019 Music S.T.A.R.T!! score=2
- T2: target_score=3 accepted=[3, 6, 7, 9] hit_rate=0.3038 cumulative=0.1825 cards=PL!-bp6-024 錯覚CROSSROADS score=3 / PL!-bp6-024 錯覚CROSSROADS score=3 / PL!-bp6-024 錯覚CROSSROADS score=3
- T3: target_score=9 accepted=[9] hit_rate=0.0338 cumulative=0.0063 cards=PL!-bp6-022 Dreamin' Go! Go!! score=9
- T4: target_score=9 accepted=[9] hit_rate=0.025 cumulative=0.0 cards=PL!-bp6-022 Dreamin' Go! Go!! score=9

### Top Routes

- 4 / 9-9-4 / 15-9-9 / 17-15-9: 46 (0.0575)
- 4-4 / 9-4-4 / 15-9-4 / 17-15-9: 35 (0.0437)
- 4-4 / 9-4-4 / 11-9-4 / 17-11-9: 34 (0.0425)
- none / 9-9 / 15-9-9 / 17-15-9: 32 (0.04)
- 4 / 9-9-4 / 11-9-9 / 17-11-9: 31 (0.0387)
- 4 / 9-4 / 15-9-4 / 17-15-9: 26 (0.0325)
- 4 / 9-9-4 / 13-9-9 / 17-13-9: 24 (0.03)
- none / 9-9-9 / 15-9-9 / 17-15-9: 22 (0.0275)
- 4-2 / 9-4-2 / 15-9-4 / 17-15-9: 20 (0.025)
- 2 / 9-9-2 / 15-9-9 / 17-15-9: 17 (0.0213)

### Miss Reasons

- T1: missing 4 260 (0.325)
- T2: missing 9 132 (0.165)
- T3: missing 15 347 (0.4338)
- T4: missing 17 113 (0.1412)

### Sample Routes

- T1: 4 -> 9-4-2 -> 13-9-4 -> 17-13-9
- T2: 4-4 -> 9-4-4 -> 13-9-4 -> 17-13-9
- T3: 4 -> 9-9-4 -> 15-9-9 -> 17-15-9
- T4: none -> 9-9 -> 15-9-9 -> 17-15-9
- T5: 2 -> 9-2 -> 15-9-2 -> 17-15-9
