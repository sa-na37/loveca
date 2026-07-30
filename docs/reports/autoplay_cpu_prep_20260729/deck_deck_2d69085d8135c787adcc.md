# Autoplay Policy Report: 君ここ

- model: `stage1_policy_template`
- recommended: 2-2 -> 7-2 -> 13-2

## Cost Bands

- 2-4: 31
- 5-10: 7
- 11-14: 8
- 15+: 2

## Progressions

- 2-2 -> 7-2 -> 13-2: score=88.5 coverage=1.0 turns=2-2 / 7-2 / 13-2 missing=なし

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
- early policy: 2-2 -> 7-2 -> 13-2
- late policy: 未判定
- target turns: 2-2 / 7-2 / 13-2 / 13-7-2
- accepted targets: 2-2 / 7-2 or 7-2-2 / 13-2 or 13-2-2 / 13-7-2 or 13-20-2

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
  - 2-2: PL!HS-bp1-008 徒町小鈴 route=手札から通常登場 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場
- T2
  - 7-2: PL!-pb1-018 矢澤にこ route=手札から通常登場 / 登場時に追加2コスト登場候補 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場
  - 7-2-2: PL!-pb1-018 矢澤にこ route=手札から通常登場 / 登場時に追加2コスト登場候補 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場
- T3
  - 13-2: PL!SP-bp2-009 鬼塚夏美 route=手札から通常登場 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場
  - 13-2-2: PL!SP-bp2-009 鬼塚夏美 route=手札から通常登場 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場
- T4
  - 13-7-2: PL!SP-bp2-009 鬼塚夏美 route=手札から通常登場 / PL!-pb1-018 矢澤にこ route=手札から通常登場 / 登場時に追加2コスト登場候補 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場
  - 13-20-2: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 route=手札から通常登場 / 自身のコスト軽減で到達候補 / PL!SP-bp2-009 鬼塚夏美 route=手札から通常登場 / PL!HS-bp1-008 徒町小鈴 route=手札から通常登場

### Turn Summary

- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。
- T1: target=2-2 hit_rate=0.9862 cumulative=0.9862 combined_cumulative=0.2775 avg_stage_cost=5.59
- T2: target=7-2 hit_rate=0.7662 cumulative=0.7538 combined_cumulative=0.03 avg_stage_cost=10.35
- T3: target=13-2 hit_rate=0.8462 cumulative=0.6225 combined_cumulative=0.0025 avg_stage_cost=20.19
- T4: target=13-7-2 hit_rate=0.965 cumulative=0.6225 combined_cumulative=0.0 avg_stage_cost=25.57

### Live Score Targets

- T1: target_score=1 accepted=[1, 5] hit_rate=0.2787 cumulative=0.2787 cards=LL-bp5-001 Live with a smile! score=1 / LL-bp5-001 Live with a smile! score=1
- T2: target_score=5 accepted=[5] hit_rate=0.1212 cumulative=0.0425 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5
- T3: target_score=5 accepted=[5] hit_rate=0.0988 cumulative=0.005 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5
- T4: target_score=5 accepted=[5] hit_rate=0.0938 cumulative=0.0025 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5

### Top Routes

- 2-2-2 / 7-2-2 / 13-7-2 / 13-7-2: 378 (0.4725)
- 2-2-2 / 2-2-2 / 13-2-2 / 13-13-2: 73 (0.0912)
- 2-2-2 / 2-2-2 / 13-2-2 / 20-13-2: 72 (0.09)
- 2-2 / 7-7-2 / 13-7-7 / 13-7-7: 63 (0.0788)
- 2-2 / 7-2-2 / 13-7-2 / 13-7-2: 57 (0.0712)
- 2-2-2 / 7-2-2 / 7-7-2 / 20-7-7: 24 (0.03)
- 2-2-2 / 7-2-2 / 7-2-2 / 20-13-7: 13 (0.0163)
- 2-2-2 / 7-2-2 / 7-7-2 / 13-7-7: 11 (0.0138)
- 2-2-2 / 2-2-2 / 13-2-2 / 13-7-2: 11 (0.0138)
- 2-2-2 / 7-2-2 / 7-7-7 / 7-7-7: 8 (0.01)

### Miss Reasons

- T1: missing 2 7 (0.0088), missing 2-2 4 (0.005)
- T2: missing 7 187 (0.2338)
- T3: missing 13 123 (0.1537)
- T4: missing 13 23 (0.0288), missing 7 5 (0.0063)

### Sample Routes

- T1: 2-2-2 -> 7-2-2 -> 7-7-2 -> 13-7-7
- T2: 2-2-2 -> 7-2-2 -> 7-2-2 -> 20-13-7
- T3: 2-2-2 -> 7-2-2 -> 13-7-2 -> 13-7-2
- T4: 2-2-2 -> 7-2-2 -> 13-7-2 -> 13-7-2
- T5: 2-2-2 -> 7-2-2 -> 13-7-2 -> 13-7-2
