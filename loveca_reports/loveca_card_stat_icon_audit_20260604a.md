# Loveca card stat icon audit 20260604a

tokv1: `llocg_db_out_full/cards_min_tokv1.json`

## Summary

- `cards_total`: 993
- `defect_base_counts_blank`: 787
- `defect_blade_heart_counts_blank`: 600
- `defect_blade_heart_tags_blank`: 196
- `defect_required_counts_blank`: 196
- `raw_base_rows`: 787
- `raw_blade_heart_rows`: 600
- `raw_required_rows`: 196
- `runtime_base_still_blank`: 0
- `runtime_blade_heart_still_blank`: 0
- `runtime_blade_heart_tags_still_blank`: 0
- `runtime_required_still_blank`: 0

## Interpretation

- `stored_*_blank` means the DB's normalized columns are blank despite parseable raw icon text.
- `runtime_*_still_blank` should be 0 after `db_parse_raw_heart_icons_20260604a`.
- This audit checks required hearts, member base hearts, blade-heart colors, and blade-heart non-color tags such as `<ドロー+1>` / `<スコア+1>`.

## First rows

| cardnumber | cardname | field | raw | runtime_blank_after_patch |
|---|---|---|---|---:|
| LL-PR-004 | 愛♡スクリ～ム！ | required | <桃> 3 <赤> 3 <緑> 3 (合計9) | 0 |
| LL-PR-004 | 愛♡スクリ～ム！ | blade_heart | <ALL> | 0 |
| LL-PR-004 | 愛♡スクリ～ム！ | blade_heart_tags | <ALL> | 0 |
| LL-bp1-001 | 上原歩夢＆澁谷かのん＆日野下花帆 | base | <桃> 3 <緑> 3 <紫> 3 | 0 |
| LL-bp2-001 | 渡辺曜＆鬼塚夏美＆大沢瑠璃乃 | base | <桃> 2 <黄> 2 <緑> 2 | 0 |
| LL-bp3-001 | 園田海未＆津島善子＆天王寺璃奈 | base | <桃> 2 <青> 2 <紫> 2 | 0 |
| LL-bp4-001 | 絢瀬絵里＆朝香果林＆葉月恋 | base | <赤> 2 <青> 2 <紫> 2 | 0 |
| LL-bp5-001 | Live with a smile! | required | <赤> 1 <任意> 3 (合計4) | 0 |
| LL-bp5-001 | Live with a smile! | blade_heart_tags | <スコア+1> | 0 |
| LL-bp5-002 | Bring the LOVE！ | required | <桃> 2 <赤> 2 <黄> 1 <任意> 5 (合計10) | 0 |
| LL-bp5-002 | Bring the LOVE！ | blade_heart | <ALL> | 0 |
| LL-bp5-002 | Bring the LOVE！ | blade_heart_tags | <ALL> | 0 |
| LL-bp6-001 | 南ことり＆黒澤ダイヤ＆徒町小鈴 | base | <赤> 2 <黄> 2 <青> 2 | 0 |
| PL!-PR-001 | 高坂穂乃果 | base | <黄> 2 | 0 |
| PL!-PR-002 | 絢瀬絵里 | base | <紫> 2 | 0 |
| PL!-PR-003 | 南ことり | base | <桃> 2 <黄> 3 <紫> 1 | 0 |
| PL!-PR-003 | 南ことり | blade_heart | <黄> | 0 |
| PL!-PR-004 | 園田海未 | base | <桃> 3 <黄> 1 <紫> 2 | 0 |
| PL!-PR-004 | 園田海未 | blade_heart | <桃> | 0 |
| PL!-PR-005 | 星空凛 | base | <桃> 1 <黄> 1 <紫> 1 | 0 |
| PL!-PR-006 | 西木野真姫 | base | <桃> 1 <黄> 1 <紫> 1 | 0 |
| PL!-PR-007 | 東條希 | base | <桃> 1 | 0 |
| PL!-PR-008 | 小泉花陽 | base | <桃> 1 <黄> 1 <紫> 1 | 0 |
| PL!-PR-009 | 矢澤にこ | base | <紫> 1 | 0 |
| PL!-PR-012 | 小泉花陽 | base | <黄> 1 | 0 |
| PL!-PR-012 | 小泉花陽 | blade_heart | <黄> | 0 |
| PL!-PR-014 | 園田海未 | base | <桃> 1 | 0 |
| PL!-PR-014 | 園田海未 | blade_heart | <桃> | 0 |
| PL!-PR-015 | 西木野真姫 | base | <黄> 3 <紫> 3 | 0 |
| PL!-PR-015 | 西木野真姫 | blade_heart | <紫> | 0 |
| PL!-PR-017 | 矢澤にこ | base | <紫> 1 | 0 |
| PL!-PR-017 | 矢澤にこ | blade_heart | <紫> | 0 |
| PL!-PR-018 | 東條希 | base | <桃> 3 <紫> 3 | 0 |
| PL!-PR-018 | 東條希 | blade_heart | <桃> | 0 |
| PL!-bp3-001 | 高坂穂乃果 | base | <桃> 2 <黄> 2 <紫> 2 | 0 |
| PL!-bp3-001 | 高坂穂乃果 | blade_heart | <黄> | 0 |
| PL!-bp3-002 | 絢瀬絵里 | base | <桃> 1 <黄> 1 <紫> 2 | 0 |
| PL!-bp3-003 | 南ことり | base | <桃> 1 <黄> 1 <紫> 1 | 0 |
| PL!-bp3-003 | 南ことり | blade_heart | <黄> | 0 |
| PL!-bp3-004 | 園田海未 | base | <桃> 2 <黄> 1 <紫> 1 | 0 |
