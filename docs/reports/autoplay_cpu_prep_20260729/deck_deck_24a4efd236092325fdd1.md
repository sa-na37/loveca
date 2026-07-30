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

### コスト軽減
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20

### 特殊バトンタッチ
- なし

### 15+高コスト
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20
- PL!S-bp7-005 渡辺曜 x1 cost=15

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 800
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 4 -> 9 -> 15単騎
- late policy: 4ターン目以降 15+単騎軸
- target turns: 4 / 9 / 15 / 2-20-2
- accepted targets: 4 / 9 / 15 / 2-20-2

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
  - 4: PL!N-bp1-017 宮下愛 route=手札から通常登場
- T2
  - 9: PL!S-PR-029 渡辺曜 route=手札から通常登場
- T3
  - 15: PL!S-bp7-005 渡辺曜 route=手札から通常登場
- T4
  - 2-20-2: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補 / PL!N-PR-009 優木せつ菜 route=手札から通常登場 / PL!N-PR-009 優木せつ菜 route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=4 hit_rate=0.7975 cumulative=0.7975 combined_cumulative=0.42 avg_stage_cost=5.78
- T2: target=9 hit_rate=0.8588 cumulative=0.6725 combined_cumulative=0.0762 avg_stage_cost=16.51
- T3: target=15 hit_rate=0.235 cumulative=0.145 combined_cumulative=0.0013 avg_stage_cost=27.16
- T4: target=2-20-2 hit_rate=0.49 cumulative=0.055 combined_cumulative=0.0 avg_stage_cost=39.16

### Live Score Targets

- T1: target_score=3 accepted=[3, 5, 8] hit_rate=0.5138 cumulative=0.5138 cards=PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3 / PL!S-bp2-023 MY舞☆TONIGHT score=3
- T2: target_score=5 accepted=[5, 8] hit_rate=0.2263 cumulative=0.13 cards=PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5 / PL!S-bp3-025 SUKI for you, DREAM for you! score=5
- T3: target_score=8 accepted=[8] hit_rate=0.0413 cumulative=0.0075 cards=PL!S-bp7-022 恋になりたいAQUARIUM score=8 / PL!S-bp7-022 恋になりたいAQUARIUM score=8
- T4: target_score=8 accepted=[8] hit_rate=0.0537 cumulative=0.0013 cards=PL!S-bp7-022 恋になりたいAQUARIUM score=8 / PL!S-bp7-022 恋になりたいAQUARIUM score=8

### Top Routes

- 4 / 9-9-4 / 13-9-9 / 20-13-9: 59 (0.0737)
- 4-4 / 9-4-4 / 13-9-4 / 20-13-9: 36 (0.045)
- 4-2 / 9-4-2 / 13-9-4 / 20-13-9: 20 (0.025)
- 4 / 9-9-4 / 13-9-9 / 13-13-11: 18 (0.0225)
- 4 / 9-4-2 / 13-9-4 / 20-13-9: 17 (0.0213)
- 4 / 9-9-4 / 13-9-9 / 13-13-13: 16 (0.02)
- 4 / 9-4 / 13-9-4 / 20-13-9: 14 (0.0175)
- 4 / 9-9-4 / 15-9-9 / 20-15-9: 13 (0.0163)
- 4-4 / 9-4-4 / 13-9-4 / 13-13-11: 13 (0.0163)
- 4-4-4 / 9-4-4 / 13-9-4 / 13-13-11: 12 (0.015)

### Miss Reasons

- T1: missing 4 162 (0.2025)
- T2: missing 9 113 (0.1412)
- T3: missing 15 612 (0.765)
- T4: missing 20 408 (0.51)

### Sample Routes

- T1: 4-2 -> 9-4-2 -> 13-9-4 -> 13-13-9
- T2: 4-4-4 -> 9-4-4 -> 13-9-4 -> 20-13-9
- T3: 4 -> 9-4 -> 13-9-4 -> 13-13-13
- T4: 4 -> 4 -> 13-13-4 -> 20-13-13
- T5: 4 -> 9-9-4 -> 15-9-9 -> 15-13-13
