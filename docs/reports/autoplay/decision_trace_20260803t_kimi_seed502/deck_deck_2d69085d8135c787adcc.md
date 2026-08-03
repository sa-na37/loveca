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

### エネルギー追加ライブ
- なし

### エネルギーアクティブ化
- なし

### コスト軽減
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20

### エネルギー支払いなし登場
- なし

### 支払い以上の登場
- PL!-pb1-018 矢澤にこ x4 cost=7

### 低コスト追加登場
- PL!-pb1-018 矢澤にこ x4 cost=7

### 特殊バトンタッチ
- なし

### 15+高コスト
- LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 x2 cost=20

## Trial Result

- model: `max_target_probability_heuristic`
- trials: 300
- seed: base=502 effective=591657975
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 2-2 -> 7-2 -> 13-2
- late policy: 未判定
- target turns: 2-2 / 7-2 / 13-2 / 13-7-2
- accepted targets: 2-2 / 7-2 or 7-2-2 / 13-2 or 13-2-2 / 13-7-2 or 13-20-2

### Effect Assumptions

- up to three cards are live-set exchanged after member planning, and each exchanged card draws one replacement
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
- Each turn performs active, energy, normal draw, member placement, then live-set exchange in that order.
- During live set, up to three cards may be exchanged, including non-live cards.
- Live set exchanges low-priority or replaceable cards to dig toward the nearest target; it does not automatically set every live card.
- Live score targets are inferred from live cards actually present in the deck; the hit check uses the highest-score live card selected during that turn's live-set exchange.
- If the turn has a Daydream-like 2-4-2 bridge, an energy-boost live is preferred as the live-set card for that turn only.
- Member placement tracks active/wait energy, pays active energy for normal plays, applies baton reduction for replacements, then scores feasible lines as higher than target first, exact target second, then the largest available fallback.
- Extra members beyond the accepted target slot count are not played only for occupancy; the persistent stage keeps existing cards unless replacing them improves the current target.
- After live success, draw effects on the live-set card are modeled as hand smoothing for the following turn; energy-boost lives place energy into wait for the next active phase.

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
- T1: target=2-2 hit_rate=0.9833 cumulative=0.9833 combined_cumulative=0.0633 avg_stage_cost=3.96
- T2: target=7-2 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=3.96
- T3: target=13-2 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=3.96
- T4: target=13-7-2 hit_rate=0.0 cumulative=0.0 combined_cumulative=0.0 avg_stage_cost=10.89

### Live Score Targets

- T1: target_score=1 accepted=[1, 5] hit_rate=0.0633 cumulative=0.0633 cards=LL-bp5-001 Live with a smile! score=1 / LL-bp5-001 Live with a smile! score=1
- T2: target_score=5 accepted=[5] hit_rate=0.0467 cumulative=0.0167 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5
- T3: target_score=5 accepted=[5] hit_rate=0.4067 cumulative=0.0133 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5
- T4: target_score=5 accepted=[5] hit_rate=0.4067 cumulative=0.0 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5

### Top Routes

- 2-2 / 2-2 / 2-2 / 7-2-2: 291 (0.97)
- 2-2 / 2-2 / 2-2 / 2-2: 4 (0.0133)
- 2 / 2 / 2 / 7-2-2: 4 (0.0133)
- none / none / none / 7: 1 (0.0033)

### Miss Reasons

- T1: missing 2 4 (0.0133), missing 2-2 1 (0.0033)
- T2: missing 7 299 (0.9967), missing 7-2 1 (0.0033)
- T3: missing 13 299 (0.9967), missing 13-2 1 (0.0033)
- T4: missing 13 295 (0.9833), missing 13-7 4 (0.0133), missing 13-2 1 (0.0033)

### Sample Routes

- T1: 2-2 -> 2-2 -> 2-2 -> 7-2-2
- T2: 2-2 -> 2-2 -> 2-2 -> 7-2-2
- T3: 2-2 -> 2-2 -> 2-2 -> 7-2-2
- T4: 2-2 -> 2-2 -> 2-2 -> 2-2
- T5: 2-2 -> 2-2 -> 2-2 -> 7-2-2
