# Loveca named-hand discard cost / cost-result family audit (2026-06-04a)

compiled: `./llocg_db_out_full/cards_compiled_v7h.json`
candidates: 3

## Summary

- implemented_count_to_blade_bonus: 1
- implemented_discarded_heart_colors: 1
- implemented_exact3_live_total_score_bonus: 1

## Candidates

### LL-bp1-001 上原歩夢＆澁谷かのん＆日野下花帆
- status: `implemented_exact3_live_total_score_bonus`
- trigger: `自動 / ライブ開始時`
- cost: 手札の「上原歩夢」と「澁谷かのん」と「日野下花帆」を、好きな組み合わせで合計3枚、控え室に置いてもよい
- effect: ライブ終了時まで、「<常時>ライブの合計スコアを+3する。」を得る。

### LL-bp2-001 渡辺曜＆鬼塚夏美＆大沢瑠璃乃
- status: `implemented_count_to_blade_bonus`
- trigger: `自動 / ライブ開始時`
- cost: 手札の「渡辺曜」と「鬼塚夏美」と「大沢瑠璃乃」を好きな枚数控え室に置いてもよい
- effect: ライブ終了時まで、これによって控え室に置いた枚数1枚につき<(ブレード)>を得る。

### LL-bp6-001 南ことり＆黒澤ダイヤ＆徒町小鈴
- status: `implemented_discarded_heart_colors`
- trigger: `自動 / ライブ開始時`
- cost: 手札の「南ことり」と「黒澤ダイヤ」と「徒町小鈴」を好きな枚数控え室に置いてもよい
- effect: ライブ終了時まで、これにより控え室に置いたそれらのカードが持つハートの色1つにつき、その色のハートを1つずつ得る。
