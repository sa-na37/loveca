# PL!HS-bp6-014#A01 design

- audit_id: PL!HS-bp6-014#A01
- cardnumber: PL!HS-bp6-014
- cardname: 安養寺姫芽
- card_type: MEMBER
- effect_text: このカードを手札から控え室に置く：カードを1枚引き、ライブ終了時まで、自分のステージにいる「藤島慈」か「大沢瑠璃乃」のうち1人は<(ブレード)>を得る。この能力は、このカードが手札にある場合のみ起動できる。
- canonical_trigger: 起動
- activation_timing: 起動
- required_zone: hand
- required_phase: MAIN for 起動; none for 常時; trigger-specific otherwise
- required_cost: provided by debug energy/hand/deck setup where applicable
- required_targets: stage members/hand cards/deck top according to effect text
- required_prior_state: avoid unrelated trigger noise; provide other member when effect requires another stage member
- forbidden_noise: DECK_CODE wrapper, success zone >=3 initial state, unrelated live triggers
- expected_pending_kind: none for 常時; effect-specific for 起動
- expected_state_change: hand activation UI/command should exist before resolver
- expected_cleanup: count only when effect actually resolves
- expected_undo: count exact undo only after effect actually resolves
- manual_steps: Keep card in hand and look for a legal hand-activation route; stage activation is not legal.
