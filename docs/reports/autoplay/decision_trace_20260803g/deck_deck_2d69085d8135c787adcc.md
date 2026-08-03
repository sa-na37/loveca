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
- trials: 200
- mulligan: maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards
- success: turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence
- early policy: 2-2 -> 7-2 -> 13-2
- late policy: 未判定
- target turns: 2-2 / 7-2 / 13-2 / 13-7-2
- accepted targets: 2-2 / 7-2 or 7-2-2 / 13-2 or 13-2-2 / 13-7-2 or 13-20-2

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
- T1: target=2-2 hit_rate=0.98 cumulative=0.98 combined_cumulative=0.58 avg_stage_cost=3.95
- T2: target=7-2 hit_rate=0.92 cumulative=0.915 combined_cumulative=0.14 avg_stage_cost=9.87
- T3: target=13-2 hit_rate=0.88 cumulative=0.88 combined_cumulative=0.045 avg_stage_cost=14.03
- T4: target=13-7-2 hit_rate=0.825 cumulative=0.815 combined_cumulative=0.01 avg_stage_cost=20.36

### Live Score Targets

- T1: target_score=1 accepted=[1, 5] hit_rate=0.59 cumulative=0.59 cards=LL-bp5-001 Live with a smile! score=1 / LL-bp5-001 Live with a smile! score=1
- T2: target_score=5 accepted=[5] hit_rate=0.335 cumulative=0.175 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5
- T3: target_score=5 accepted=[5] hit_rate=0.315 cumulative=0.05 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5
- T4: target_score=5 accepted=[5] hit_rate=0.305 cumulative=0.01 cards=PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp2-024 ビタミンSUMMER！ score=5 / PL!SP-bp5-023 Shooting Voice!! score=5

### Top Routes

- 2-2 / 7-2-2 / 13-2 / 13-7-2: 108 (0.54)
- 2-2 / 7-2 / 13-2 / 13-7-2: 55 (0.275)
- 2-2 / 7-2-2 / 13-2 / 13-2: 12 (0.06)
- 2-2 / 2-2 / 2-2 / 7-2-2: 11 (0.055)
- 2-2 / 7-2-2 / 7-2-2 / 13-2: 4 (0.02)
- 2-2 / 7-2-2 / 7-2-2 / 7-2-2: 2 (0.01)
- 2-2 / 2-2 / 2-2 / 2-2: 2 (0.01)
- 2 / 7-2 / 13 / 13-7-2: 1 (0.005)
- 2-2 / 7-2 / 13-2 / 13-2: 1 (0.005)
- 2 / 7 / 13 / 13-7: 1 (0.005)

### Miss Reasons

- T1: missing 2 3 (0.015), missing 2-2 1 (0.005)
- T2: missing 7 13 (0.065), missing 2 2 (0.01), missing 7-2 1 (0.005)
- T3: missing 13 20 (0.1), missing 2 3 (0.015), missing 13-2 1 (0.005)
- T4: missing 7 17 (0.085), missing 13 14 (0.07), missing 13-7 2 (0.01), missing 2 1 (0.005), missing 13-2 1 (0.005)

### Sample Routes

- T1: 2-2 -> 7-2 -> 13-2 -> 13-7-2
- T2: 2-2 -> 7-2-2 -> 13-2 -> 13-7-2
- T3: 2-2 -> 7-2 -> 13-2 -> 13-7-2
- T4: 2-2 -> 7-2-2 -> 13-2 -> 13-7-2
- T5: 2-2 -> 7-2-2 -> 13-2 -> 13-2

## Decision Trace

### Trial 1
- route: 2-2 -> 7-2 -> 13-2 -> 13-7-2
- initial hand: LL-bp5-001 Live with a smile! score=1 | PL!SP-bp2-024 ビタミンSUMMER！ score=5 | PL!SP-bp1-011 鬼塚冬毬 cost=2 | PL!HS-bp1-008 徒町小鈴 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!N-bp4-017 宮下愛 cost=2
- mulligan target: 2-2 / 7-2 / 7-2-2 / 13-2 / 13-2-2
- mulligan score: 41.194 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[5, 7, 9]
- critical focus: T2 bottleneck key focus_costs=[7] turn_access=0.744 key_total=7 all-redraw-p=0.744 two-keep-p=0.644 gap=0.1
- keep: PL!SP-bp1-011 鬼塚冬毬 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- return: LL-bp5-001 Live with a smile! score=1 | PL!SP-bp2-024 ビタミンSUMMER！ score=5 | PL!HS-bp1-008 徒町小鈴 cost=2 | PL!N-bp4-017 宮下愛 cost=2
- redraw: PL!SP-bp5-002 唐可可 cost=13 | PL!N-bp5-021 天王寺璃奈 cost=2 | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!S-bp6-014 渡辺曜 cost=2
- post mulligan hand: PL!SP-bp1-011 鬼塚冬毬 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!SP-bp5-002 唐可可 cost=13 | PL!N-bp5-021 天王寺璃奈 cost=2 | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!S-bp6-014 渡辺曜 cost=2
- hand need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!HS-bp1-008 徒町小鈴 cost=2 need=5.57; PL!N-bp4-017 宮下愛 cost=2 need=5.57; PL!SP-bp1-011 鬼塚冬毬 cost=2 need=5.57; LL-bp5-001 Live with a smile! score=1 need=0.0; PL!SP-bp2-024 ビタミンSUMMER！ score=5 need=0.0
- mulligan candidate comparison:
  - score=41.194 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!SP-bp1-011 鬼塚冬毬 cost=2; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=41.194 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!HS-bp1-008 徒町小鈴 cost=2; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=41.194 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!N-bp4-017 宮下愛 cost=2
  - score=39.02 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp5-001 Live with a smile! score=1; PL!SP-bp1-011 鬼塚冬毬 cost=2; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=39.02 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!SP-bp2-024 ビタミンSUMMER！ score=5; PL!SP-bp1-011 鬼塚冬毬 cost=2; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction

#### T1 target 2-2 accepted 2-2
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!SP-pb2-031 鬼塚夏美 cost=2
- live set selected: PL!HS-bp2-004 夕霧綴理 cost=2 | PL!N-bp5-021 天王寺璃奈 cost=2 | PL!S-bp6-014 渡辺曜 cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!SP-bp5-002 唐可可 cost=13 need=15.75; PL!HS-bp2-004 夕霧綴理 cost=2 need=5.57; PL!N-bp5-021 天王寺璃奈 cost=2 need=5.57; PL!S-bp6-014 渡辺曜 cost=2 need=5.57; PL!SP-bp1-011 鬼塚冬毬 cost=2 need=5.57
- main stage: none -> 2-2
- main played/replaced in: PL!SP-bp1-011 鬼塚冬毬 cost=2 | PL!SP-pb2-031 鬼塚夏美 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 7-2 accepted 7-2 / 7-2-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!SP-pb2-031 鬼塚夏美 cost=2
- live set selected: PL!SP-bp2-024 ビタミンSUMMER！ score=5 | PL!SP-bp1-011 鬼塚冬毬 cost=2 | PL!SP-pb2-031 鬼塚夏美 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!SP-bp2-024 ビタミンSUMMER！ score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=85.0; PL!SP-bp2-009 鬼塚夏美 cost=13 need=19.6; PL!SP-bp5-002 唐可可 cost=13 need=19.6; PL!SP-bp1-011 鬼塚冬毬 cost=2 need=4.53; PL!SP-pb2-031 鬼塚夏美 cost=2 need=4.53; PL!SP-bp2-024 ビタミンSUMMER！ score=5 need=0.0
- main stage: 2-2 -> 7-2
- main played/replaced in: PL!N-bp5-007 優木せつ菜 cost=7
- main replaced out: PL!SP-bp1-011 鬼塚冬毬 cost=2
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=7-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 13-2 accepted 13-2 / 13-2-2
- start stage: 7-2
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: PL!HS-bp1-008 徒町小鈴 cost=2
- live set selected: PL!HS-bp1-008 徒町小鈴 cost=2 | PL!N-bp5-021 天王寺璃奈 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=56.4; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=36.11; PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.0; PL!SP-bp5-002 唐可可 cost=13 need=15.0; PL!HS-bp1-008 徒町小鈴 cost=2 need=2.67; PL!N-bp5-021 天王寺璃奈 cost=2 need=2.67
- main stage: 7-2 -> 13-2
- main played/replaced in: PL!SP-bp5-002 唐可可 cost=13
- main replaced out: PL!N-bp5-007 優木せつ菜 cost=7
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 0, 'wait': 6, 'deck_remaining': 6}
- result: stage=13-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 6, 'deck_remaining': 6}
### Trial 2
- route: 2-2 -> 7-2-2 -> 13-2 -> 13-7-2
- initial hand: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon | PL!SP-bp5-023 Shooting Voice!! score=5 | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!N-bp5-007 優木せつ菜 cost=7 | PL!SP-bp5-002 唐可可 cost=13 | PL!S-sd1-015 津島善子 cost=2
- mulligan target: 2-2 / 7-2 / 7-2-2 / 13-2 / 13-2-2
- mulligan score: 32.56 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[5, 7, 9]
- keep: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon | PL!SP-bp5-002 唐可可 cost=13
- return: PL!SP-bp5-023 Shooting Voice!! score=5 | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!N-bp5-007 優木せつ菜 cost=7 | PL!S-sd1-015 津島善子 cost=2
- redraw: PL!SP-bp5-002 唐可可 cost=13 | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!SP-bp2-009 鬼塚夏美 cost=13 | PL!SP-pb2-031 鬼塚夏美 cost=2
- post mulligan hand: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon | PL!SP-bp5-002 唐可可 cost=13 | PL!SP-bp5-002 唐可可 cost=13 | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!SP-bp2-009 鬼塚夏美 cost=13 | PL!SP-pb2-031 鬼塚夏美 cost=2
- hand need score: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=40.74; PL!N-bp5-007 優木せつ菜 cost=7 need=16.74; PL!SP-bp5-002 唐可可 cost=13 need=15.75; PL!HS-bp2-004 夕霧綴理 cost=2 need=5.57; PL!S-sd1-015 津島善子 cost=2 need=5.57; PL!SP-bp5-023 Shooting Voice!! score=5 need=0.0
- mulligan candidate comparison:
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon; PL!SP-bp5-002 唐可可 cost=13
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!HS-bp2-004 夕霧綴理 cost=2; PL!SP-bp5-002 唐可可 cost=13
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!N-bp5-007 優木せつ菜 cost=7; PL!SP-bp5-002 唐可可 cost=13
  - score=32.56 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!SP-bp5-002 唐可可 cost=13; PL!S-sd1-015 津島善子 cost=2
  - score=32.545 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon; PL!SP-bp5-023 Shooting Voice!! score=5; PL!SP-bp5-002 唐可可 cost=13

#### T1 target 2-2 accepted 2-2
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- live set selected: none
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=none
- pre-exchange need score: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=40.74; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=40.74; PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.75; PL!SP-bp5-002 唐可可 cost=13 need=15.75; PL!SP-bp5-002 唐可可 cost=13 need=15.75; PL!HS-bp2-004 夕霧綴理 cost=2 need=5.57
- main stage: none -> 2-2
- main played/replaced in: PL!HS-bp2-004 夕霧綴理 cost=2 | PL!SP-pb2-031 鬼塚夏美 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 7-2 accepted 7-2 / 7-2-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- live set selected: none
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=47.03; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=47.03; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=47.03; PL!SP-bp2-009 鬼塚夏美 cost=13 need=19.6; PL!SP-bp5-002 唐可可 cost=13 need=19.6; PL!SP-bp5-002 唐可可 cost=13 need=19.6
- main stage: 2-2 -> 7-2
- main played/replaced in: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- main replaced out: PL!HS-bp2-004 夕霧綴理 cost=2
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=7-2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 13-2 accepted 13-2 / 13-2-2
- start stage: 7-2
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: PL!HS-bp1-008 徒町小鈴 cost=2
- live set selected: PL!HS-bp1-008 徒町小鈴 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=36.11; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=36.11; PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.0; PL!SP-bp5-002 唐可可 cost=13 need=15.0; PL!SP-bp5-002 唐可可 cost=13 need=15.0; PL!HS-bp1-008 徒町小鈴 cost=2 need=2.67
- main stage: 7-2 -> 13-2
- main played/replaced in: PL!SP-bp5-002 唐可可 cost=13
- main replaced out: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 0, 'wait': 6, 'deck_remaining': 6}
- result: stage=13-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 6, 'deck_remaining': 6}
### Trial 3
- route: 2-2 -> 7-2 -> 13-2 -> 13-7-2
- initial hand: PL!HS-bp1-008 徒町小鈴 cost=2 | PL!N-bp4-017 宮下愛 cost=2 | PL!SP-bp1-011 鬼塚冬毬 cost=2 | PL!S-bp6-014 渡辺曜 cost=2 | PL!SP-bp5-002 唐可可 cost=13 | PL!N-bp4-017 宮下愛 cost=2
- mulligan target: 2-2 / 7-2 / 7-2-2 / 13-2 / 13-2-2
- mulligan score: 34.99 p(T1/T2/T3)=[0.938, 0.743, 0.818] draw_windows=[7, 9, 11]
- critical focus: T2 bottleneck key focus_costs=[7] turn_access=0.743 key_total=7 all-redraw-p=0.743 two-keep-p=0.643 gap=0.101
- keep: none
- return: PL!HS-bp1-008 徒町小鈴 cost=2 | PL!N-bp4-017 宮下愛 cost=2 | PL!SP-bp1-011 鬼塚冬毬 cost=2 | PL!S-bp6-014 渡辺曜 cost=2 | PL!SP-bp5-002 唐可可 cost=13 | PL!N-bp4-017 宮下愛 cost=2
- redraw: PL!S-bp6-014 渡辺曜 cost=2 | PL!N-bp5-007 優木せつ菜 cost=7 | PL!HS-bp1-008 徒町小鈴 cost=2 | PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon | PL!SP-pb2-031 鬼塚夏美 cost=2 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- post mulligan hand: PL!S-bp6-014 渡辺曜 cost=2 | PL!N-bp5-007 優木せつ菜 cost=7 | PL!HS-bp1-008 徒町小鈴 cost=2 | PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon | PL!SP-pb2-031 鬼塚夏美 cost=2 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- hand need score: PL!SP-bp5-002 唐可可 cost=13 need=15.75; PL!HS-bp1-008 徒町小鈴 cost=2 need=5.57; PL!N-bp4-017 宮下愛 cost=2 need=5.57; PL!N-bp4-017 宮下愛 cost=2 need=5.57; PL!S-bp6-014 渡辺曜 cost=2 need=5.57; PL!SP-bp1-011 鬼塚冬毬 cost=2 need=5.57
- mulligan candidate comparison:
  - score=34.99 p(T1/T2/T3)=0.938/0.743/0.818 keep=none
  - score=33.344 p(T1/T2/T3)=1.0/0.645/0.744 keep=PL!HS-bp1-008 徒町小鈴 cost=2; PL!N-bp4-017 宮下愛 cost=2
  - score=33.344 p(T1/T2/T3)=1.0/0.645/0.744 keep=PL!HS-bp1-008 徒町小鈴 cost=2; PL!SP-bp1-011 鬼塚冬毬 cost=2
  - score=33.344 p(T1/T2/T3)=1.0/0.645/0.744 keep=PL!N-bp4-017 宮下愛 cost=2; PL!SP-bp1-011 鬼塚冬毬 cost=2
  - score=33.344 p(T1/T2/T3)=1.0/0.645/0.744 keep=PL!HS-bp1-008 徒町小鈴 cost=2; PL!S-bp6-014 渡辺曜 cost=2

#### T1 target 2-2 accepted 2-2
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- live set selected: PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!HS-bp1-008 徒町小鈴 cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- pre-exchange need score: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=40.74; PL!N-bp5-007 優木せつ菜 cost=7 need=16.74; PL!HS-bp1-008 徒町小鈴 cost=2 need=5.57; PL!S-bp6-014 渡辺曜 cost=2 need=5.57; PL!SP-pb2-031 鬼塚夏美 cost=2 need=5.57; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5
- main stage: none -> 2-2
- main played/replaced in: PL!S-bp6-014 渡辺曜 cost=2 | PL!SP-pb2-031 鬼塚夏美 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 7-2 accepted 7-2 / 7-2-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!SP-bp2-009 鬼塚夏美 cost=13
- live set selected: PL!SP-bp5-023 Shooting Voice!! score=5 | PL!SP-bp5-023 Shooting Voice!! score=5 | PL!SP-pb2-031 鬼塚夏美 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!SP-bp5-023 Shooting Voice!! score=5
- pre-exchange need score: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=47.03; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=47.03; PL!N-bp5-007 優木せつ菜 cost=7 need=23.03; PL!SP-bp2-009 鬼塚夏美 cost=13 need=19.6; PL!SP-pb2-031 鬼塚夏美 cost=2 need=4.53; PL!SP-bp5-023 Shooting Voice!! score=5 need=0.0
- main stage: 2-2 -> 7-2
- main played/replaced in: PL!N-bp5-007 優木せつ菜 cost=7
- main replaced out: PL!S-bp6-014 渡辺曜 cost=2
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=7-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 13-2 accepted 13-2 / 13-2-2
- start stage: 7-2
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- live set selected: PL!N-bp5-021 天王寺璃奈 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=56.4; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=36.11; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=36.11; PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.0; PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.0; PL!SP-bp5-002 唐可可 cost=13 need=15.0
- main stage: 7-2 -> 13-2
- main played/replaced in: PL!SP-bp2-009 鬼塚夏美 cost=13
- main replaced out: PL!N-bp5-007 優木せつ菜 cost=7
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 0, 'wait': 6, 'deck_remaining': 6}
- result: stage=13-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 6, 'deck_remaining': 6}
### Trial 4
- route: 2-2 -> 7-2-2 -> 13-2 -> 13-7-2
- initial hand: PL!S-sd1-015 津島善子 cost=2 | PL!SP-bp2-009 鬼塚夏美 cost=13 | PL!N-bp5-021 天王寺璃奈 cost=2 | PL!S-bp6-014 渡辺曜 cost=2 | PL!SP-bp2-009 鬼塚夏美 cost=13 | PL!N-bp4-017 宮下愛 cost=2
- mulligan target: 2-2 / 7-2 / 7-2-2 / 13-2 / 13-2-2
- mulligan score: 34.999 p(T1/T2/T3)=[0.95, 0.744, 0.764] draw_windows=[7, 9, 11]
- critical focus: T2 bottleneck key focus_costs=[7] turn_access=0.744 key_total=7 all-redraw-p=0.744 two-keep-p=0.643 gap=0.1
- keep: none
- return: PL!S-sd1-015 津島善子 cost=2 | PL!SP-bp2-009 鬼塚夏美 cost=13 | PL!N-bp5-021 天王寺璃奈 cost=2 | PL!S-bp6-014 渡辺曜 cost=2 | PL!SP-bp2-009 鬼塚夏美 cost=13 | PL!N-bp4-017 宮下愛 cost=2
- redraw: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon | PL!HS-bp1-008 徒町小鈴 cost=2 | PL!SP-bp2-024 ビタミンSUMMER！ score=5 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!S-bp6-014 渡辺曜 cost=2
- post mulligan hand: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon | PL!HS-bp1-008 徒町小鈴 cost=2 | PL!SP-bp2-024 ビタミンSUMMER！ score=5 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!HS-bp2-004 夕霧綴理 cost=2 | PL!S-bp6-014 渡辺曜 cost=2
- hand need score: PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.75; PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.75; PL!N-bp4-017 宮下愛 cost=2 need=5.57; PL!N-bp5-021 天王寺璃奈 cost=2 need=5.57; PL!S-bp6-014 渡辺曜 cost=2 need=5.57; PL!S-sd1-015 津島善子 cost=2 need=5.57
- mulligan candidate comparison:
  - score=34.999 p(T1/T2/T3)=0.95/0.744/0.764 keep=none
  - score=33.111 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-sd1-015 津島善子 cost=2; PL!SP-bp2-009 鬼塚夏美 cost=13
  - score=33.111 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!SP-bp2-009 鬼塚夏美 cost=13; PL!N-bp5-021 天王寺璃奈 cost=2
  - score=33.111 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!SP-bp2-009 鬼塚夏美 cost=13; PL!S-bp6-014 渡辺曜 cost=2
  - score=33.111 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!S-sd1-015 津島善子 cost=2; PL!SP-bp2-009 鬼塚夏美 cost=13

#### T1 target 2-2 accepted 2-2
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!N-bp5-021 天王寺璃奈 cost=2
- live set selected: PL!SP-bp2-024 ビタミンSUMMER！ score=5 | PL!HS-bp1-008 徒町小鈴 cost=2 | PL!HS-bp2-004 夕霧綴理 cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!SP-bp2-024 ビタミンSUMMER！ score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=40.74; PL!HS-bp1-008 徒町小鈴 cost=2 need=5.57; PL!HS-bp2-004 夕霧綴理 cost=2 need=5.57; PL!N-bp5-021 天王寺璃奈 cost=2 need=5.57; PL!S-bp6-014 渡辺曜 cost=2 need=5.57
- main stage: none -> 2-2
- main played/replaced in: PL!S-bp6-014 渡辺曜 cost=2 | PL!N-bp5-021 天王寺璃奈 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 7-2 accepted 7-2 / 7-2-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- live set selected: PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!N-bp4-017 宮下愛 cost=2 | PL!SP-bp1-011 鬼塚冬毬 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=85.0; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=47.03; PL!N-bp5-007 優木せつ菜 cost=7 need=23.03; PL!N-bp4-017 宮下愛 cost=2 need=4.53; PL!SP-bp1-011 鬼塚冬毬 cost=2 need=4.53; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5
- main stage: 2-2 -> 7-2
- main played/replaced in: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- main replaced out: PL!S-bp6-014 渡辺曜 cost=2
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=7-2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 13-2 accepted 13-2 / 13-2-2
- start stage: 7-2
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: PL!SP-bp1-011 鬼塚冬毬 cost=2
- live set selected: PL!HS-bp2-004 夕霧綴理 cost=2 | PL!S-sd1-015 津島善子 cost=2 | PL!SP-bp1-011 鬼塚冬毬 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=56.4; PL!SP-bp5-002 唐可可 cost=13 need=15.0; PL!N-bp5-007 優木せつ菜 cost=7 need=12.11; PL!HS-bp2-004 夕霧綴理 cost=2 need=2.67; PL!S-sd1-015 津島善子 cost=2 need=2.67; PL!SP-bp1-011 鬼塚冬毬 cost=2 need=2.67
- main stage: 7-2 -> 13-2
- main played/replaced in: PL!SP-bp5-002 唐可可 cost=13
- main replaced out: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 0, 'wait': 6, 'deck_remaining': 6}
- result: stage=13-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 6, 'deck_remaining': 6}
### Trial 5
- route: 2-2 -> 7-2-2 -> 13-2 -> 13-2
- initial hand: PL!HS-bp1-008 徒町小鈴 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!SP-bp5-002 唐可可 cost=13 | PL!SP-pb2-031 鬼塚夏美 cost=2 | PL!SP-bp1-011 鬼塚冬毬 cost=2 | PL!HS-bp2-004 夕霧綴理 cost=2
- mulligan target: 2-2 / 7-2 / 7-2-2 / 13-2 / 13-2-2
- mulligan score: 41.211 p(T1/T2/T3)=[1.0, 1.0, 1.0] draw_windows=[5, 7, 9]
- critical focus: T2 bottleneck key focus_costs=[7] turn_access=0.744 key_total=7 all-redraw-p=0.744 two-keep-p=0.643 gap=0.1
- keep: PL!HS-bp1-008 徒町小鈴 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
- return: PL!SP-bp5-002 唐可可 cost=13 | PL!SP-pb2-031 鬼塚夏美 cost=2 | PL!SP-bp1-011 鬼塚冬毬 cost=2 | PL!HS-bp2-004 夕霧綴理 cost=2
- redraw: PL!N-bp4-017 宮下愛 cost=2 | PL!SP-bp5-023 Shooting Voice!! score=5 | PL!S-sd1-015 津島善子 cost=2 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- post mulligan hand: PL!HS-bp1-008 徒町小鈴 cost=2 | LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction | PL!N-bp4-017 宮下愛 cost=2 | PL!SP-bp5-023 Shooting Voice!! score=5 | PL!S-sd1-015 津島善子 cost=2 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- hand need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!SP-bp5-002 唐可可 cost=13 need=15.75; PL!HS-bp1-008 徒町小鈴 cost=2 need=5.57; PL!HS-bp2-004 夕霧綴理 cost=2 need=5.57; PL!SP-bp1-011 鬼塚冬毬 cost=2 need=5.57; PL!SP-pb2-031 鬼塚夏美 cost=2 need=5.57
- mulligan candidate comparison:
  - score=41.211 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!HS-bp1-008 徒町小鈴 cost=2; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction
  - score=41.211 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!SP-pb2-031 鬼塚夏美 cost=2
  - score=41.211 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!SP-bp1-011 鬼塚冬毬 cost=2
  - score=41.211 p(T1/T2/T3)=1.0/1.0/1.0 keep=LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!HS-bp2-004 夕霧綴理 cost=2
  - score=39.033 p(T1/T2/T3)=1.0/1.0/1.0 keep=PL!HS-bp1-008 徒町小鈴 cost=2; LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction; PL!SP-pb2-031 鬼塚夏美 cost=2

#### T1 target 2-2 accepted 2-2
- start stage: none
- start energy: {'active': 3, 'wait': 0, 'deck_remaining': 9}
- normal draw: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- live set selected: PL!SP-bp5-023 Shooting Voice!! score=5 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!HS-bp1-008 徒町小鈴 cost=2
- live set reason: prefer_energy_boost=False target_score=1 live_for_success=PL!SP-bp5-023 Shooting Voice!! score=5
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=49.2; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=40.74; PL!HS-bp1-008 徒町小鈴 cost=2 need=5.57; PL!N-bp4-017 宮下愛 cost=2 need=5.57; PL!S-sd1-015 津島善子 cost=2 need=5.57; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5
- main stage: none -> 2-2
- main played/replaced in: PL!N-bp4-017 宮下愛 cost=2 | PL!S-sd1-015 津島善子 cost=2
- main replaced out: none
- main energy: {'active': 4, 'wait': 0, 'deck_remaining': 8} -> {'active': 0, 'wait': 4, 'deck_remaining': 8}
- result: stage=2-2 stage_hit=True live_score_hit=True miss=none energy_added=0 end_energy={'active': 0, 'wait': 4, 'deck_remaining': 8}

#### T2 target 7-2 accepted 7-2 / 7-2-2
- start stage: 2-2
- start energy: {'active': 0, 'wait': 4, 'deck_remaining': 8}
- normal draw: PL!N-bp5-021 天王寺璃奈 cost=2
- live set selected: LL-bp5-001 Live with a smile! score=1 | PL!S-bp2-024 君のこころは輝いてるかい？ score=0 | PL!N-bp5-021 天王寺璃奈 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=PL!S-bp2-024 君のこころは輝いてるかい？ score=0
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=85.0; PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon need=47.03; PL!N-bp5-021 天王寺璃奈 cost=2 need=4.53; PL!S-bp6-014 渡辺曜 cost=2 need=4.53; PL!S-bp2-024 君のこころは輝いてるかい？ score=0 need=2.5; LL-bp5-001 Live with a smile! score=1 need=0.0
- main stage: 2-2 -> 7-2
- main played/replaced in: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- main replaced out: PL!N-bp4-017 宮下愛 cost=2
- main energy: {'active': 5, 'wait': 0, 'deck_remaining': 7} -> {'active': 0, 'wait': 5, 'deck_remaining': 7}
- result: stage=7-2-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 5, 'deck_remaining': 7}

#### T3 target 13-2 accepted 13-2 / 13-2-2
- start stage: 7-2
- start energy: {'active': 0, 'wait': 5, 'deck_remaining': 7}
- normal draw: PL!S-bp6-014 渡辺曜 cost=2
- live set selected: PL!N-bp4-017 宮下愛 cost=2 | PL!S-bp6-014 渡辺曜 cost=2 | PL!S-bp6-014 渡辺曜 cost=2
- live set reason: prefer_energy_boost=False target_score=5 live_for_success=none
- pre-exchange need score: LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 cost=20 tags=cost_reduction need=56.4; PL!SP-bp2-009 鬼塚夏美 cost=13 need=15.0; PL!SP-bp5-002 唐可可 cost=13 need=15.0; PL!N-bp4-017 宮下愛 cost=2 need=2.67; PL!S-bp6-014 渡辺曜 cost=2 need=2.67; PL!S-bp6-014 渡辺曜 cost=2 need=2.67
- main stage: 7-2 -> 13-2
- main played/replaced in: PL!SP-bp5-002 唐可可 cost=13
- main replaced out: PL!-pb1-018 矢澤にこ cost=7 tags=overcost_member_play,low_cost_summon
- main energy: {'active': 6, 'wait': 0, 'deck_remaining': 6} -> {'active': 0, 'wait': 6, 'deck_remaining': 6}
- result: stage=13-2 stage_hit=True live_score_hit=False miss=none energy_added=0 end_energy={'active': 0, 'wait': 6, 'deck_remaining': 6}
