# Pending Residue Before Runtime Fix

- 00_initial.json: phase=MAIN, pending_len=0, pending_kinds=[]
- 01_triggered.json: phase=MAIN, pending_len=1, pending_kinds=['choose_enter_effect_mode']
  - first.kind=choose_enter_effect_mode
  - first.text=PL!-PR-005[登場]: 効果を1つ選ぶ
  - first.source_cn=PL!-PR-005
- 02_pending.json: phase=MAIN, pending_len=1, pending_kinds=['choose_enter_effect_mode']
  - first.kind=choose_enter_effect_mode
  - first.text=PL!-PR-005[登場]: 効果を1つ選ぶ
  - first.source_cn=PL!-PR-005
- 03_after_selection.json: phase=MAIN, pending_len=1, pending_kinds=['choose_enter_effect_mode']
  - first.kind=choose_enter_effect_mode
  - first.text=PL!-PR-005[登場]: 効果を1つ選ぶ
  - first.source_cn=PL!-PR-005
- 04_resolved.json: phase=MAIN, pending_len=1, pending_kinds=['choose_enter_effect_mode']
  - first.kind=choose_enter_effect_mode
  - first.text=PL!-PR-005[登場]: 効果を1つ選ぶ
  - first.source_cn=PL!-PR-005
- 05_after_cleanup.json: phase=MAIN, pending_len=1, pending_kinds=['choose_enter_effect_mode']
  - first.kind=choose_enter_effect_mode
  - first.text=PL!-PR-005[登場]: 効果を1つ選ぶ
  - first.source_cn=PL!-PR-005
- 06_after_undo.json: phase=MAIN, pending_len=0, pending_kinds=[]

Finding: `04_resolved.json` and `05_after_cleanup.json` still contain `choose_enter_effect_mode`, while Phase 3 v2 marked the row as resolved/CLEANUP_PASS/PASS_FULL.
