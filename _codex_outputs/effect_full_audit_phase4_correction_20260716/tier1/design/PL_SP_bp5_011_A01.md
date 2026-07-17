# PL!SP-bp5-011#A01 design

- audit_id: PL!SP-bp5-011#A01
- cardnumber: PL!SP-bp5-011
- cardname: 鬼塚冬毬
- card_type: MEMBER
- effect_text: を得る。
- canonical_trigger: 常時
- activation_timing: 常時
- required_zone: none
- required_phase: MAIN for 起動; none for 常時; trigger-specific otherwise
- required_cost: provided by debug energy/hand/deck setup where applicable
- required_targets: stage members/hand cards/deck top according to effect text
- required_prior_state: avoid unrelated trigger noise; provide other member when effect requires another stage member
- forbidden_noise: DECK_CODE wrapper, success zone >=3 initial state, unrelated live triggers
- expected_pending_kind: none for 常時; effect-specific for 起動
- expected_state_change: excluded from implementation backlog
- expected_cleanup: count only when effect actually resolves
- expected_undo: count exact undo only after effect actually resolves
- manual_steps: No runtime trigger: parser fragment/duplicate row; verify exclusion only.
