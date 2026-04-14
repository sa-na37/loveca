# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_live_start_20260413l
from __future__ import annotations

"""llocg_ui.effects.live_start

ライブ開始時に解決する ext apply の正本。
blade / heart / draw / discard / choose 系のうち、
既存 helper / pending で閉じているものを apply から外出しした完成版。
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def try_apply_live_start_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, str],
    ctx: Dict[str, Any],
    ext_key: str,
) -> bool:

    # ------------------------------------------------------------------
    if ext_key == "live_start_my_cost_lower_draw1":
        my_cost = _stage_member_cost_sum(gs, cards_db)
        opp_exists = _has_opponent_state(gs)
        opp_cost = _opp_stage_member_cost_sum(gs, cards_db) if opp_exists else 0
        src = str((ctx or {}).get("source_cn") or "")
        if opp_exists:
            if my_cost < opp_cost:
                drawn = _draw_cards(eng, gs, 1)
                try:
                    gs.log.append(f"[AUTO_EXT] stage_cost {my_cost}<{opp_cost} -> draw {drawn} (高坂穂乃果)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append(f"[AUTO_EXT] stage_cost {my_cost}>={opp_cost}, no draw (高坂穂乃果)")
                except Exception:
                    pass
            return True
        payload = {
            "kind": "confirm_effect",
            "text": "【高坂穂乃果】ライブ開始時：自分ステージのコスト合計が相手より低いなら、カードを1枚引く",
            "options": ["使う", "スキップ"],
            "after_effect_template": "自分ステージにいるメンバーのコストの合計が相手より低い場合、カードを1枚引く。",
            "ctx": {"source_cn": src, "_ext_confirm_op": "draw1"},
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 高坂穂乃果: confirm draw1 (my_cost={my_cost}, opp unavailable)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 26: PL!-bp4-004 園田海未
    # 成功ライブのスコア合計 ≥ 6 → energy 2枚アクティブ
    # ------------------------------------------------------------------
    # Prompt 31: PL!-bp4-016 東條希
    # 成功ライブのスコア合計 ≥ 3 → draw 1

    # ------------------------------------------------------------------
    # Prompt 57: PL!-pb1-032 SENTIMENTAL StepS
    # 成功ライブ置き場に μ's カードがある → draw 1
    # ------------------------------------------------------------------
    # Prompt 67: PL!HS-bp1-004 夕霧綴理
    # ライブ終了時まで、ライブ中のカード 1 枚につき +1ブレード
    # ------------------------------------------------------------------
    # Prompt 72: PL!HS-bp1-023 ド！ド！ド！
    # ライブ合計スコア > 相手 かつ ステージに蓮ノ空メンバー → energy deck から 1枚 wait
    # ------------------------------------------------------------------
    # Prompt 77: PL!HS-bp2-005 大沢瑠璃乃
    # ステージ全 3 エリアにメンバーがいる → ライブ終了時まで +2ブレード



    # ------------------------------------------------------------------
    if ext_key == "live_start_all_stage_filled_x2_blade":
        slot = _src_slot(gs, ctx)
        if _all_stage_slots_filled(gs):
            if slot is not None:
                _add_temp_blade(eng, slot, 2)
            try:
                gs.log.append("[AUTO_EXT] all stage filled -> +2blade (大沢瑠璃乃)")
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] stage not full, no blade (大沢瑠璃乃)")
            except Exception:
                pass
        return True

    if ext_key == "live_start_pick_stage_member_blade3":
        occupied = _stage_positions_all_occupied(gs)
        src = str((ctx or {}).get("source_cn") or "")
        if not occupied:
            try:
                gs.log.append("[AUTO_EXT] no stage members, no blade (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        if len(occupied) == 1:
            # 対象が1人のみなら選択不要で即付与
            _, slot = occupied[0]
            _add_temp_blade(eng, slot, 3)
            try:
                gs.log.append(f"[AUTO_EXT] only 1 member -> +3blade to {occupied[0][0]} (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        # 複数いる場合は choose_stage_member_to_activate pending で選択
        candidates = [pos for pos, _ in occupied]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_stage_member_blade3__resolve",
            "source_cn": src,
            "label": "【Oh,Love&Peace!】ブレード+3を与えるメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Oh,Love&Peace!: choose member for +3blade from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_stage_member_blade3__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_blade(eng, slot, 3)
            try:
                gs.log.append(f"[AUTO_EXT] +3blade -> {chosen_pos} (Oh,Love&Peace! resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 30: PL!-bp4-013 園田海未 (ライブ開始時)
    # このメンバー以外のステージメンバー1人（選択）に pink+1
    # src_pos から「このメンバー」を特定して除外候補を絞る


    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_other_stage_member_pink1":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append(f"[AUTO_EXT] no other members on stage (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        if len(others) == 1:
            _, slot = others[0]
            _add_temp_hearts(eng, slot, {"pink": 1})
            try:
                gs.log.append(f"[AUTO_EXT] +pink to {others[0][0]} (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in others]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_other_stage_member_pink1__resolve",
            "source_cn": src,
            "label": "【園田海未】桃ハート+1を与えるメンバーを選んでください（このメンバー以外）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 園田海未 bp4-013: choose other member for +pink from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_other_stage_member_pink1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_hearts(eng, slot, {"pink": 1})
            try:
                gs.log.append(f"[AUTO_EXT] +pink -> {chosen_pos} (園田海未 bp4-013 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 32: PL!-bp4-017 小泉花陽 (ライブ開始時)
    # センター(C)の μ's メンバーに +1ブレード（対象固定、選択不要）

    # ------------------------------------------------------------------
    if ext_key == "live_start_center_mus_blade1":
        st = getattr(gs, "stage", None)
        center_slot = (st or {}).get("C") if isinstance(st, dict) else None
        if center_slot is not None and bool(getattr(center_slot, "cardnumber", None)):
            if _card_group(center_slot, cards_db) == "μ's":
                _add_temp_blade(eng, center_slot, 1)
                try:
                    gs.log.append("[AUTO_EXT] center μ's -> +1blade (小泉花陽 bp4-017)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append("[AUTO_EXT] center member is not μ's, no blade (小泉花陽 bp4-017)")
                except Exception:
                    pass
        else:
            try:
                gs.log.append("[AUTO_EXT] center empty, no blade (小泉花陽 bp4-017)")
            except Exception:
                pass
        return True

        options = [p for p in ("L", "C", "R") if p != chosen_pos] + ["skip"]
        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "position_change",
            "src_pos": chosen_pos,
            "optional": True,
            "options": options,
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] position_change src={chosen_pos} (Love wing bell)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 37: PL!-bp4-024 小夜啼鳥恋詩 (ライブ開始時)
    # ステージの μ's メンバー1人（選択）に +1ブレード


    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_mus_stage_member_blade1":
        mus_members = _stage_positions_with_group(gs, cards_db, "μ's")
        src = str((ctx or {}).get("source_cn") or "")
        if not mus_members:
            try:
                gs.log.append("[AUTO_EXT] no μ's on stage (小夜啼鳥恋詩)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in mus_members]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_mus_stage_member_blade1__resolve",
            "source_cn": src,
            "label": "【小夜啼鳥恋詩】ブレード+1を与えるμ'sメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 小夜啼鳥恋詩: choose μ's member for +blade from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_mus_stage_member_blade1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] +1blade -> {chosen_pos} (小夜啼鳥恋詩 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 46: PL!-pb1-010 高坂穂乃果 (ライブ開始時)
    # このメンバー以外のステージメンバー全員に +1ブレード（選択なし）



    # ------------------------------------------------------------------
    if ext_key == "live_start_other_stage_members_blade1":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append(f"[AUTO_EXT] no other members on stage (高坂穂乃果 pb1-010)")
            except Exception:
                pass
            return True
        for pos, slot in others:
            _add_temp_blade(eng, slot, 1)
        try:
            gs.log.append(f"[AUTO_EXT] +1blade to {[p for p,_ in others]} (高坂穂乃果 pb1-010)")
        except Exception:
            pass
        return True

    if ext_key == "live_start_discard_member_same_name_green1_blade1":
        src = str((ctx or {}).get("source_cn") or "")
        # 捨てたカードを特定
        discarded_cn = str((ctx or {}).get("discarded_cn") or "").strip()
        if not discarded_cn:
            top = _green_room_top(gs)
            if top is not None:
                discarded_cn = str(getattr(top, "cardnumber", None) or top or "").strip()

        if not discarded_cn:
            try:
                gs.log.append("[AUTO_EXT] could not identify discarded card (百生吟子)")
            except Exception:
                pass
            return True

        # カードタイプ確認（MEMBER でなければ効果なし）
        discarded_type = _card_type_norm(discarded_cn, cards_db)
        if discarded_type != "MEMBER":
            try:
                gs.log.append(f"[AUTO_EXT] discarded {discarded_cn} is not MEMBER (type={discarded_type}), no effect (百生吟子)")
            except Exception:
                pass
            return True

        # 同名のステージメンバーを探す
        discarded_name = _card_name(discarded_cn, cards_db)
        if not discarded_name:
            try:
                canon_fn = eng.get("_canon_cardno")
                get_card_fn = eng.get("_get_card")
                canon_cn = canon_fn(discarded_cn) if callable(canon_fn) else str(discarded_cn or "")
                ci_dis = get_card_fn(cards_db, canon_cn) if callable(get_card_fn) else None
                if ci_dis is not None:
                    discarded_name = str(
                        getattr(ci_dis, "cardname", "") or
                        getattr(ci_dis, "name", "") or
                        ((ci_dis if isinstance(ci_dis, dict) else {}).get("cardname")) or
                        ((ci_dis if isinstance(ci_dis, dict) else {}).get("name")) or
                        ""
                    )
            except Exception:
                pass

        def _same_name_or_card(slot_obj: Any, discarded_cn_val: str, discarded_name_val: str) -> bool:
            slot_cn = str(getattr(slot_obj, "cardnumber", "") or "")
            # まず cardnumber 一致を強く見る
            try:
                canon_fn = eng.get("_canon_cardno")
                if callable(canon_fn):
                    if canon_fn(slot_cn) == canon_fn(discarded_cn_val):
                        return True
                elif slot_cn == discarded_cn_val:
                    return True
            except Exception:
                if slot_cn == discarded_cn_val:
                    return True

            # 次に cardname 一致
            slot_name = _card_name(slot_obj, cards_db)
            if discarded_name_val and slot_name and slot_name == discarded_name_val:
                return True

            # 最後に engine の _get_card でもう一度引き直す
            try:
                canon_fn = eng.get("_canon_cardno")
                get_card_fn = eng.get("_get_card")
                canon_slot = canon_fn(slot_cn) if callable(canon_fn) else slot_cn
                ci_slot = get_card_fn(cards_db, canon_slot) if callable(get_card_fn) else None
                slot_name2 = str(
                    getattr(ci_slot, "cardname", "") or
                    getattr(ci_slot, "name", "") or
                    ((ci_slot if isinstance(ci_slot, dict) else {}).get("cardname")) or
                    ((ci_slot if isinstance(ci_slot, dict) else {}).get("name")) or
                    ""
                )
                if discarded_name_val and slot_name2 and slot_name2 == discarded_name_val:
                    return True
            except Exception:
                pass
            return False

        if not discarded_name:
            # 名前が取れなくても cardnumber 一致だけで通せるようにする
            try:
                gs.log.append(f"[AUTO_EXT] name fallback by cardnumber for {discarded_cn} (百生吟子)")
            except Exception:
                pass

        matched = []
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _same_name_or_card(slot, discarded_cn, discarded_name):
                        matched.append((pos, slot))
        except Exception:
            pass

        if not matched:
            try:
                gs.log.append(f"[AUTO_EXT] no stage member named '{discarded_name}', no effect (百生吟子)")
            except Exception:
                pass
            return True

        if len(matched) == 1:
            _, slot = matched[0]
            _add_temp_hearts(eng, slot, {"green": 1})
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] discarded MEMBER '{discarded_name}' -> +green+blade to {matched[0][0]} (百生吟子)")
            except Exception:
                pass
            return True

        # 同名が複数いる場合は選択（通常は起きないが安全のため）
        candidates = [pos for pos, _ in matched]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_discard_member_same_name_green1_blade1__resolve",
            "source_cn": src,
            "discarded_name": discarded_name,
            "label": f"【百生吟子】{discarded_name}と同名のメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 百生吟子: choose same-name member from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_discard_member_same_name_green1_blade1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_hearts(eng, slot, {"green": 1})
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] +green+blade -> {chosen_pos} (百生吟子 resolve)")
            except Exception:
                pass
        return True

    # ==================================================================
    # group3_A7B2_20260406a 新規実装
    # ==================================================================

    # ------------------------------------------------------------------
    # Prompt 69: PL!HS-bp1-006 藤島慈 (ライブ開始時)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 他メンバーがいる場合: ハートの色を1つ選んで ライブ終了時まで得る

    # ------------------------------------------------------------------
    if ext_key == "live_start_other_member_exists_choose_heart":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        if not _stage_has_any_other_member(gs, exclude_pos=src_pos):
            try:
                gs.log.append("[AUTO_EXT] no other member on stage, no effect (藤島慈)")
            except Exception:
                pass
            return True
        payload = {
            "kind": "choose_heart_color",
            "pos": src_pos,
            "n": 1,
            "text": f"{src}: 好きなハートの色を1つ指定する → ライブ終了時まで+1",
            "options": ["桃", "赤", "黄", "緑", "青", "紫"],
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append("[PENDING] 藤島慈: choose heart color (self)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 14: PL!-bp3-003 南ことり (登場)
    # cost=このメンバーをウェイトにしてもよい → engine 側 self_wait pay_or_skip
    # 控え室から μ's のメンバーカードを1枚手札に加える
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Prompt 60: PL!-sd1-003 南ことり (ライブ開始時)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 桃/黄/紫 のうち1つ選んでライブ終了時まで得る

    # ------------------------------------------------------------------
    if ext_key == "live_start_choose_pinkYellowPurple_heart":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "choose_heart_color",
            "pos": src_pos,
            "n": 1,
            "text": f"{src}: 桃/黄/紫から1つ選ぶ → ライブ終了時まで+1",
            "options": ["桃", "黄", "紫"],
            "source_cn": src,
            "src_pos": src_pos,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append("[PENDING] 南ことり sd1-003: choose pink/yellow/purple heart")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 73: PL!HS-bp2-001 日野下花帆 (起動)
    # コスト <(E)><(E)> → engine 側起動コスト処理
    # 控え室からスコア3以下の 蓮ノ空 ライブカードを1枚手札に加える
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)

    # ------------------------------------------------------------------
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 他メンバーがいる場合、控え室から みらくらぱーく！ のカードを1枚手札へ
    # 注意: Prompt 77（ライブ開始時+2ブレード）は既存実装。壊さない。
    # ------------------------------------------------------------------

        # センター以外: src_pos が C なら L/R どちらかへ、L/R なら反対側へ
        if src_pos == "C":
            options = ["L", "R"]
        elif src_pos == "L":
            options = ["R"]
        elif src_pos == "R":
            options = ["L"]
        else:
            options = ["L", "R"]

        payload = {
            "kind": "position_change",
            "src_pos": src_pos,
            "optional": False,
            "options": options,
            "source_cn": src,
            "text": f"{src}: 自分のステージにブレード5以上の『μ's』メンバーがいないため、センターエリア以外にポジションチェンジする",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 星空凛: force position_change to {options} from {src_pos}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 80: PL!HS-bp2-018 安養寺姫芽 (登場)
    # MAIN 中に [E][E] を任意支払い → green の LIVE を表向きで set_zone に置き、
    # 次の LIVE_SET で手札から置ける上限を 1 減らす。
    # effect_template only; optional energy cost prompt は engine.py 側。

    return False

    return False
