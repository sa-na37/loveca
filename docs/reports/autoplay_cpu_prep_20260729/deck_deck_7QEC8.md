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

### コスト軽減
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20

### 特殊バトンタッチ
- なし

### 15+高コスト
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 800
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 未判定
- late policy: 未判定
- target turns: 20 / 20 / 20 / 2-20-2
- accepted targets: 20 / 20 / 20 / 2-20-2

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
  - 20: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補
- T2
  - 20: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補
- T3
  - 20: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補
- T4
  - 2-20-2: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補 / PL!N-PR-009 優木せつ菜 route=手札から通常登場 / PL!N-PR-009 優木せつ菜 route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=20 hit_rate=0.4225 cumulative=0.4225 combined_cumulative=0.265 avg_stage_cost=33.6
- T2: target=20 hit_rate=0.5012 cumulative=0.4225 combined_cumulative=0.0975 avg_stage_cost=35.41
- T3: target=20 hit_rate=0.5525 cumulative=0.4225 combined_cumulative=0.0125 avg_stage_cost=36.45
- T4: target=2-20-2 hit_rate=0.5887 cumulative=0.4225 combined_cumulative=0.0025 avg_stage_cost=38.79

### Live Score Targets

- T1: target_score=3 accepted=[3, 5] hit_rate=0.6725 cumulative=0.6725 cards=PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3
- T2: target_score=5 accepted=[5] hit_rate=0.395 cumulative=0.2812 cards=PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- T3: target_score=5 accepted=[5] hit_rate=0.235 cumulative=0.0563 cards=PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- T4: target_score=5 accepted=[5] hit_rate=0.1862 cumulative=0.0075 cards=PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp2-022 未熟DREAMER score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5

### Top Routes

- 20-13-13 / 20-13-13 / 20-13-13 / 20-13-13: 65 (0.0813)
- 20-13-9 / 20-13-9 / 20-13-9 / 20-13-9: 46 (0.0575)
- 20-13-11 / 20-13-11 / 20-13-11 / 20-13-11: 43 (0.0537)
- 20-11-9 / 20-11-9 / 20-11-9 / 20-11-9: 31 (0.0387)
- 20-20-13 / 20-20-13 / 20-20-13 / 20-20-13: 29 (0.0362)
- 20-9-4 / 20-9-4 / 20-9-4 / 20-9-4: 24 (0.03)
- 13-11-9 / 13-11-9 / 13-11-9 / 13-13-11: 21 (0.0262)
- 20-13-4 / 20-13-4 / 20-13-4 / 20-13-4: 19 (0.0238)
- 20-11-4 / 20-11-4 / 20-11-4 / 20-11-4: 15 (0.0187)
- 13-13-13 / 13-13-13 / 13-13-13 / 13-13-13: 13 (0.0163)

### Miss Reasons

- T1: missing 20 462 (0.5775)
- T2: missing 20 399 (0.4988)
- T3: missing 20 358 (0.4475)
- T4: missing 20 329 (0.4113)

### Sample Routes

- T1: 9-4-2 -> 9-4-2 -> 11-9-4 -> 11-11-9
- T2: 20-4-4 -> 20-4-4 -> 20-4-4 -> 20-4-4
- T3: 13-11-11 -> 13-11-11 -> 13-11-11 -> 13-13-11
- T4: 20-13-13 -> 20-13-13 -> 20-13-13 -> 20-13-13
- T5: 13-9-4 -> 13-9-4 -> 13-9-4 -> 13-11-11
