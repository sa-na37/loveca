# Loveca エール公開参照 family 既実装除外・残件再抽出 2026-06-04a

## 集計
- implemented: 37
- needs_audit_unmatched_live_success: 9
- needs_implementation: 8
- note_only_rule_text: 19

## 既実装 / 今回共通化対象に入れたもの
- `PL!-bp5-004` 園田海未 / body_auto_no_bladeheart_members_gain_icons / 自分がエールしたとき、エールにより公開された自分のカードの中にブレードハートを持たないメンバーカードが3枚以上ある場合、ライブ終了時まで、<ALL>を得る。
- `PL!-pb1-031` 輝夜の城で踊りたい / effect_template:retrieve_yell_group_member / エールにより公開された自分のカードの中から、『μ's』のメンバーカードを1枚手札に加える。
- `PL!HS-PR-027` 徒町小鈴 / effect_template:retrieve_yell_cost2member_or_score2live / エールにより公開された自分のカードの中から、コスト2以下のメンバーカードか、スコア2以下のライブカードを1枚手札に加える。
- `PL!HS-bp1-021` Holiday∞Holiday / effect_template:retrieve_yell_group_live / エールにより公開された自分のカードの中から、『蓮ノ空』のライブカードを1枚手札に加える。
- `PL!HS-bp1-022` AWOKE / live_success:add_live_success_score_bonus_if_revealed_group_member_count_at_least / エールにより公開された自分のカードの中に『蓮ノ空』のメンバーカードが10枚以上ある場合、このカードのスコアを+1する。
- `PL!HS-bp6-001` 日野下花帆 / effect_template:put_yell_revealed_any_to_deck_top_optional / エールで公開された自分のカードの中から、カードを1枚デッキの一番上に置いてもよい。
- `PL!HS-bp6-005` 徒町小鈴 / effect_template:retrieve_yell_group_member / エールにより公開された自分のカードの中から、『DOLLCHESTRA』のメンバーカードを1枚手札に加える。
- `PL!HS-bp6-032` フュージョンクラスト / effect_template:retrieve_yell_cost_member_le / エールにより公開された自分のカードの中から、コスト4以下のメンバーカードを1枚手札に加える。
- `PL!HS-cl1-009` 水彩世界 / effect_template:retrieve_yell_group_cost_member_between / エールにより公開された自分のカードの中から、コスト4以上9以下の『蓮ノ空』のメンバーカードを1枚手札に加える。
- `PL!N-PR-021` 鐘嵐珠 / effect_template:retrieve_yell_cost2member_or_score2live / エールにより公開された自分のカードの中から、コスト2以下のメンバーカードか、スコア2以下のライブカードを1枚手札に加える。
- `PL!N-PR-023` 上原歩夢 / body_auto_same_group_member3_gain_icons / 自分がエールしたとき、エールにより公開された自分のカードの中に同じグループを持つメンバーカードが3枚ある場合、ライブ終了時まで、<桃><緑>を得る。
- `PL!N-bp1-026` Poppin' Up! / live_success:enqueue_success_prompt / ライブの合計スコアが相手より高い場合、エールにより公開された自分のカードの中から、『虹ヶ咲』のカードを1枚手札に加える。
- `PL!N-bp3-030` Love U my friends / live_success:add_live_success_score_bonus_if_revealed_card_tag_count_at_least / エールにより公開された自分のカードの中に<ALL>を持つカードが1枚以上ある場合、このカードのスコアを+1する。
- `PL!N-bp4-025` VIVID WORLD / live_start:live_start_convert_revealed_colors_to_single_color_until_end_of_live / ライブ終了時まで、エールによって公開される自分のカードが持つ<桃>、<赤>、<黄>、<緑>、<紫>、<ALL>は、すべて<青>になる。
- `PL!N-bp4-025` VIVID WORLD / live_success:add_live_success_score_bonus_if_revealed_group_members_have_all_six_colors / エールにより公開された自分の『虹ヶ咲』のメンバーが持つハートの中に<桃>、<赤>、<黄>、<緑>、<青>、<紫>がある場合、このカードのスコアを+1する。
- `PL!N-bp5-001` 上原歩夢 / body_auto_bladeheart_kind_threshold_gain_icons_score / 自分がエールしたとき、エールにより公開された自分のカードが持つブレードハートの中に<桃>、<赤>、<黄>、<緑>、<青>、<紫>、<ALL>のうち、3種類以上ある場合、ライブ終了時まで、<桃>を得る。6種類以上ある場合、さらにライブ終了時まで、『<常時>ライブの合計スコアを+1する。』を得る。
- `PL!N-pb1-012` 鐘嵐珠 / effect_template:retrieve_yell_group_member / エールにより公開された自分のカードの中から、『虹ヶ咲』のメンバーカードを1枚手札に加える。
- `PL!S-PR-040` 国木田花丸 / body_auto_same_group_member3_gain_icons / 自分がエールしたとき、エールにより公開された自分のカードの中に同じグループを持つメンバーカードが3枚ある場合、ライブ終了時まで、<桃><緑>を得る。
- `PL!S-bp2-003` 松浦果南 / body_auto_live_exists_gain_icons / エールにより公開された自分のカードの中にライブカードが1枚以上あるとき、ライブ終了時まで、<緑>を得る。
- `PL!S-bp2-007` 国木田花丸 / body_auto_live_exists_hand_limit_draw1 / エールにより公開された自分のカードの中にライブカードが1枚以上あるとき、自分の手札が7枚以下の場合、カードを1枚引く。
- `PL!S-bp2-021` 未体験HORIZON / effect_template:put_yell_revealed_type_upto_deck_bottom / エールにより公開された自分のカードの中から、ライブカードを1枚までデッキの一番下に置く。
- `PL!S-bp3-005` 渡辺曜 / live_success:enqueue_success_prompt / エールにより公開された自分のカードの枚数が、相手がエールによって公開したカードの枚数より少ない場合、カードを1枚引く。
- `PL!S-bp5-019` not ALONE not HITORI / live_success:enqueue_success_prompt / 自分か相手の成功ライブカード置き場にカードが2枚以上ある場合、エールにより公開された自分のカードの中から、メンバーカードを2枚まで手札に加える。
- `PL!S-bp6-009` 黒澤ルビィ / live_success:add_live_success_score_bonus_if_revealed_group_live_has_tag / エールにより公開された自分のカードの中に、<スコア+1>を持つ『Aqours』のライブカードがある場合、ライブの合計スコアを+1する。
- `PL!S-bp6-023` GALAXY HidE and SeeK / live_success:add_live_success_score_bonus_if_revealed_live_count_at_least / エールにより公開された自分のカードの中にライブカードがある場合、このカードのスコアを+1する。
- `PL!S-pb1-003` 松浦果南 / effect_template:retrieve_yell_live / エールにより公開された自分のカードの中から、ライブカードを1枚手札に加える。
- `PL!S-pb1-007` 国木田花丸 / live_success:put_wait_energy_if_revealed_live_count_at_least / エールにより公開された自分のカードの中にライブカードが1枚以上あるとき、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。
- `PL!S-sd1-001` 高海千歌 / body_auto_per_live_gain_icons_cap / 自分がエールしたとき、ライブ終了時まで、エールにより公開された自分のカードの中のライブカード1枚につき、<赤>を得る。この能力では<赤>は3つまでしか得られない。
- `PL!S-sd1-019` 未来の僕らは知ってるよ / effect_template:retrieve_yell_group_live / エールにより公開された自分のカードの中から、『Aqours』のライブカードを1枚手札に加える。
- `PL!SP-PR-016` 嵐千砂都 / effect_template:retrieve_yell_cost2member_or_score2live / エールにより公開された自分のカードの中から、コスト2以下のメンバーカードか、スコア2以下のライブカードを1枚手札に加える。
- `PL!SP-PR-018` 澁谷かのん / live_success:put_wait_energy_if_revealed_group_card_count_at_least / エールにより公開された自分のカードの中に『Liella!』のカードが7枚以上ある場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。
- `PL!SP-PR-024` 平安名すみれ / body_auto_score_plus_group_live_gain_icons / 自分がエールしたとき、エールにより公開された自分のカードの中に、<スコア+1>を持つ『Liella!』のライブカードが1枚以上ある場合、ライブ終了時まで、<紫>を得る。
- `PL!SP-bp2-015` 平安名すみれ / body_auto_no_bladeheart_cards_gain_icons / エールにより公開された自分のカードの中にブレードハートを持つカードがないとき、ライブ終了時まで、<紫>を得る。
- `PL!SP-bp2-020` 鬼塚夏美 / body_auto_no_bladeheart_cards_gain_icons / エールにより公開された自分のカードの中にブレードハートを持つカードがないとき、ライブ終了時まで、<赤>を得る。
- `PL!SP-bp2-021` ウィーン・マルガレーテ / body_auto_no_bladeheart_cards_gain_icons / エールにより公開された自分のカードの中にブレードハートを持つカードがないとき、ライブ終了時まで、<黄>を得る。
- `PL!SP-bp4-006` 桜小路きな子 / live_success:apply_effect_template_if_revealed_distinct_named_group_member_count_at_least_on_live_success / エールにより公開された自分のカードの中に、名前が異なる『Liella!』のメンバーカードが3枚以上ある場合、エールにより公開された自分のカードの中から『Liella!』のライブカードを1枚手札に加える。
- `PL!SP-bp4-026` Wish Song / live_success:add_live_success_score_bonus_if_revealed_distinct_named_group_member_count_at_least / エールにより公開された自分のカードの中に名前が異なる『Liella!』のメンバーカードが5枚以上ある場合、このカードのスコアを+1する。

## 注釈のみ
- `PL!-PR-007` 東條希 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp3-001` 高坂穂乃果 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp3-002` 絢瀬絵里 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp3-003` 南ことり / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp3-008` 小泉花陽 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp3-014` 星空凛 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp3-017` 小泉花陽 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp3-018` 矢澤にこ / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!-bp6-010` 高坂穂乃果 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!HS-bp5-016` 桂城泉 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!N-bp3-006` 近江彼方 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!N-bp3-022` 三船栞子 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!N-bp3-023` ミア・テイラー / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!N-bp4-016` 朝香果林 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!N-bp5-004` 朝香果林 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!S-bp3-012` 松浦果南 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!S-bp3-017` 小原鞠莉 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!S-bp6-018` 黒澤ルビィ / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）
- `PL!SP-pb2-009` 鬼塚夏美 / （ウェイト状態のメンバーが持つ<(ブレード)>は、エールで公開する枚数を増やさない。）

## 残件
- `LL-bp5-001` Live with a smile! / needs_audit_unmatched_live_success / エールにより公開された自分のカードの中にライブカードが2枚以上あるか、自分のステージにいるメンバーが持つハートの中に<桃>、<赤>、<黄>、<緑>、<青>、<紫>のうち合計5種類以上あるか、このターンに自分のステージにいるメンバーがエリアを移動している場合、このカードのスコアを+1する。
- `PL!-bp6-001` 高坂穂乃果 / needs_audit_unmatched_live_success / エールにより公開された自分のカードの中に、ブレードハートを持たない『μ's』のメンバーカードがある場合、カードを1枚引き、手札を1枚控え室に置く。
- `PL!HS-bp6-027` 月夜見海月 / needs_implementation / 自分がエールしたとき、エールにより公開された自分のブレードハートを持たない『蓮ノ空』のカードを3枚まで控え室に置いてもよい。そうした場合、これにより控え室に置いた数に等しい枚数のエールを追加で行う。
- `PL!HS-cl1-012` Edelied / needs_audit_unmatched_live_success / 自分と相手のライブの合計スコアが同じ場合、エールにより公開された自分のカードの中から、コスト9以上のメンバーカードを1枚手札に加える。
- `PL!S-bp2-004` 黒澤ダイヤ / needs_implementation / エールにより公開された自分のカードの中にライブカードがないとき、それらのカードをすべて控え室に置いてもよい。これにより1枚以上のカードが控え室に置かれた場合、そのエールで得たブレードハートを失い、もう一度エールを行う。
- `PL!S-bp2-008` 小原鞠莉 / needs_implementation / 自分のステージのエリアすべてに『Aqours』のメンバーが登場しており、かつ名前が異なる場合、「<ライブ成功時>エールにより公開された自分のカードの中にライブカードが1枚以上ある場合、ライブの合計スコアを+1する。ライブカードが3枚以上ある場合、代わりに合計スコアを+2する。」を得る。
- `PL!S-bp3-002` 桜内梨子 / needs_audit_unmatched_live_success / ライブの合計スコアが相手より高い場合、このカードを手札に加えてもよい。この能力は、このカードが自分のエールによって公開されている場合のみ発動する。
- `PL!S-bp3-019` MIRACLE WAVE / needs_audit_unmatched_live_success / このターン、エールにより公開された自分のカードの中にブレードハートを持たないカードが0枚の場合か、または自分の余剰ハートを2つ以上持っている場合、このカードのスコアは4になる。
- `PL!S-bp3-020` ダイスキだったらダイジョウブ！ / needs_implementation / エールにより自分のカードを1枚以上公開したとき、それらのカードの中にブレードハートを持つカードが2枚以下の場合、それらのカードをすべて控え室に置いてもよい。そのエールで得たブレードハートを失い、もう一度エールを行う。
- `PL!S-bp5-022` SELF CONTROL!! / needs_audit_unmatched_live_success / エールにより公開されている自分のライブカードの枚数が、エールにより公開されている相手のライブカードの枚数より多い場合、このカードのスコアを+1する。
- `PL!S-bp6-021` MIRAI TICKET / needs_implementation / 自分がエールした時、エールにより公開された自分のカードの中からブレードハートを持たない『Aqours』のメンバーカードを1枚まで控え室に置いてもよい。そうした場合、これにより控え室に置いたカードのコスト5につき、追加で1枚エールを行う。この能力では4枚までしか追加でエールできない。
- `PL!SP-bp2-010` ウィーン・マルガレーテ / needs_implementation / 自分のステージにこのメンバー以外のメンバーが1人以上いる場合、ライブ終了時まで、エールによって公開される自分のカードの枚数が8枚減る。
- `PL!SP-bp2-025` Bubble Rise / needs_audit_unmatched_live_success / 自分のステージに「澁谷かのん」、「ウィーン・マルガレーテ」、「鬼塚冬毬」のうち、名前の異なるメンバーが2枚以上いる場合、エールにより公開された自分のカードの中から、カードを1枚手札に加える。
- `PL!SP-bp4-023` Dazzling Game / needs_implementation / ライブ終了時まで、エールによって公開される自分のカードが持つ<桃>、<赤>、<黄>、<緑>、<青>、<ALL>は、すべて<紫>になる。
- `PL!SP-bp5-023` Shooting Voice!! / needs_audit_unmatched_live_success / 自分か相手の成功ライブカード置き場にカードが2枚以上あり、かつエールによって公開された自分のカードの中に<(スコア)+1>を持つライブカードが1枚以上ある場合、このカードのスコアを+2する。
- `PL!SP-pb2-004` 平安名すみれ / needs_audit_unmatched_live_success / 自分のライブカード置き場の中に元々のスコアより高いスコアのライブカードがあるか、エールにより公開された自分のカードの中に<スコア+1>を持つライブカードがある場合、カードを1枚引く。
- `PL!SP-pb2-008` 若菜四季 / needs_implementation / エールにより公開された自分のカードの中にあるブレードハートを持たない『Liella!』のメンバーカード2枚につき、ライブの合計スコアを+1する。この能力では合計スコアは2までしか増えない。
