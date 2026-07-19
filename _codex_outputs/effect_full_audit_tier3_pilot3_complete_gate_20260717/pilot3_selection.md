# Pilot3 Selection

## PL!S-bp3-016#A01
- canonical_id: PL!S-bp3-016#A01
- cardnumber: PL!S-bp3-016
- cardname: 黒澤ダイヤ
- trigger: 常時
- effect_text: 自分の成功ライブカード置き場にあるカード1枚につき、ステージにいるこのメンバーのコストを+1する。
- family: success zone continuous cost bonus
- selection_reason: 成功置き場枚数だけで条件を作れ、effective_costで数値検証できる。
- why_rule_is_clear: 自分の成功ライブカード置き場の枚数に等しいコスト増加で、閾値や任意処理がない。
- why_runtime_can_represent_it: success_zoneを初期状態で0から2枚にでき、state_jsonのeffective_costで確認できる。
- why_positive_negative_is_possible: positiveは成功置き場2枚、negativeは成功置き場1枚で、差は成功置き場1枚だけ。
- expected_ui: NOT_APPLICABLE

## PL!N-bp4-008#A01
- canonical_id: PL!N-bp4-008#A01
- cardnumber: PL!N-bp4-008
- cardname: 高咲侑
- trigger: 起動
- effect_text: 手札を1枚控え室に置く：エネルギー1枚か『虹ヶ咲』のメンバー1人をアクティブにする。
- family: activated discard then active target
- selection_reason: 正規の起動ボタン、手札コスト、解決不能な効果本体を切り分けて証拠化できる。
- why_rule_is_clear: 起動コストは手札1枚で、効果はエネルギーまたは虹ヶ咲メンバー1対象のアクティブ化。
- why_runtime_can_represent_it: stage C、手札1枚、wait energy=1を初期状態で表現できる。
- why_positive_negative_is_possible: negativeは手札コスト1枚だけを除去する。
- expected_ui: stage detail action button and discard pending

## PL!SP-bp7-025#A01
- canonical_id: PL!SP-bp7-025#A01
- cardnumber: PL!SP-bp7-025
- cardname: 唐可可
- trigger: ライブ開始時
- effect_text: ライブ終了時まで、自分のステージにいる「嵐千砂都」1人は<(ブレード)>を得る。
- family: live start target member blade
- selection_reason: ライブ開始時、対象名、temp bladeという3点が明確で、UI/pending識別の検証対象にできる。
- why_rule_is_clear: ライブ開始時に嵐千砂都1人へブレード1個をライブ終了時まで付与するだけの効果。
- why_runtime_can_represent_it: sourceをstage C、嵐千砂都をstage L、live cardを手札に置ける。
- why_positive_negative_is_possible: negativeは対象の嵐千砂都を別メンバーへ置換する。
- expected_ui: live set button, live-start auto order, target selection
