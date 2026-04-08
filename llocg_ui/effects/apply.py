# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_apply_split_20260407a
from __future__ import annotations

"""llocg_ui.effects.apply

engine_effect の apply dispatcher。
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403

# ---------------------------------------------------------------------------

def try_apply_effect_by_rule_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, str],
    ctx: Dict[str, Any],
) -> bool:
    """Apply extension-owned effect rules.

    Return True only if this module handled the rule completely.
    Return False to fall back to engine.py legacy implementation.
    """
    if str(rule.get("op") or "") != "__ext__":
        return False

    ext_key = str(rule.get("ext_key") or "").strip()

    # confirm_effect helper path from engine.py (no-cost, single-player fallback)
    confirm_op = str((ctx or {}).get("_ext_confirm_op") or "").strip()
    if confirm_op == "draw1":
        drawn = _draw_cards(eng, gs, 1)
        try:
            gs.log.append(f"[AUTO_EXT] confirm -> draw {drawn}")
        except Exception:
            pass
        return True
    if confirm_op == "energy_wait_plus1":
        added = 0
        try:
            put_wait = eng.get("_put_wait_energy_from_deck")
            if callable(put_wait):
                added = int(put_wait(gs, 1, reason="confirm_effect") or 0)
            else:
                rem_fn = eng.get("_energy_remaining_in_deck")
                clamp_fn = eng.get("_clamp_energy_zone")
                rem = int(rem_fn(gs) if callable(rem_fn) else 0)
                if rem > 0:
                    gs.energy_wait = int(getattr(gs, "energy_wait", 0) or 0) + 1
                    if callable(clamp_fn):
                        clamp_fn(gs)
                    added = 1
        except Exception:
            pass
        try:
            gs.log.append(f"[AUTO_EXT] confirm -> energy_wait +{added}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # 既存: position_change_optional
    # ------------------------------------------------------------------
    if ext_key == "position_change_optional":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        if src_pos not in ("L", "C", "R"):
            try:
                gs.log.append(f"[WARN] position_change_optional: invalid src_pos='{src_pos}'")
            except Exception:
                pass
            return True
        options = [p for p in ("L", "C", "R") if p != src_pos] + ["skip"]
        payload = {
            "kind": "position_change",
            "src_pos": src_pos,
            "optional": True,
            "options": options,
            "source_cn": str((ctx or {}).get("source_cn") or ""),
        }
        try:
            getattr(gs, 'pending').append(payload)
            gs.log.append(f"[PENDING] position_change src={src_pos}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 17: PL!-bp3-006 西木野真姫
    # ライブ終了時まで、成功ライブ置き場の枚数 × +2ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_success_zone_count_x2_blade":
        slot = _src_slot(gs, ctx)
        success_cards = _success_zone_cards(gs)
        n = len(success_cards) * 2
        if slot is not None and n > 0:
            _add_temp_blade(eng, slot, n)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_zone={len(success_cards)} -> +{n}blade (西木野真姫)"
                )
            except Exception:
                pass
        elif slot is not None:
            try:
                gs.log.append("[AUTO_EXT] success_zone=0, no blade added (西木野真姫)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 24: PL!-bp4-001 高坂穂乃果
    # 自ステージのコスト合計が相手より低い場合、カードを1枚引く。
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
    if ext_key == "enter_success_score_ge6_activate2":
        success_cards = _success_zone_cards(gs)
        total_score = sum(_card_score(c, cards_db) for c in success_cards)
        if total_score >= 6:
            moved = _activate_energy(gs, 2)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}>=6 -> activate {moved} energy (園田海未)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}<6, no energy (園田海未)"
                )
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 31: PL!-bp4-016 東條希
    # 成功ライブのスコア合計 ≥ 3 → draw 1
    # ------------------------------------------------------------------
    if ext_key == "enter_success_score_ge3_draw1":
        success_cards = _success_zone_cards(gs)
        total_score = sum(_card_score(c, cards_db) for c in success_cards)
        if total_score >= 3:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}>=3 -> draw {drawn} (東條希)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}<3, no draw (東條希)"
                )
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 41: PL!-pb1-003 南ことり
    # ステージの Printemps メンバー数 × energy アクティブ
    # ------------------------------------------------------------------
    if ext_key == "enter_printemps_count_activate_energy":
        count = _stage_unit_count(gs, cards_db, "Printemps")
        if count > 0:
            moved = _activate_energy(gs, count)
            try:
                gs.log.append(
                    f"[AUTO_EXT] Printemps_on_stage={count} -> activate {moved} energy (南ことり)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] no Printemps on stage, no energy (南ことり)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 57: PL!-pb1-032 SENTIMENTAL StepS
    # 成功ライブ置き場に μ's カードがある → draw 1
    # ------------------------------------------------------------------
    if ext_key == "live_success_success_zone_has_mus_draw1":
        success_cards = _success_zone_cards(gs)
        has_mus = any(_card_group(c, cards_db) == "μ's" for c in success_cards)
        if has_mus:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_zone has μ's -> draw {drawn} (SENTIMENTAL StepS)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] no μ's in success_zone, no draw (SENTIMENTAL StepS)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 63: PL!-sd1-008 小泉花陽
    # デッキ上から 10 枚控え室へ (mill 10)
    # ------------------------------------------------------------------
    if ext_key == "body_mill10":
        milled = 0
        try:
            deck = getattr(gs, "deck", None)
            waiting = getattr(gs, "green_room", None)
            if waiting is None:
                waiting = (
                    getattr(gs, "waiting_room", None)
                    or getattr(gs, "graveyard", None)
                    or getattr(gs, "discard", None)
                )
            if deck is not None and waiting is not None:
                for _ in range(10):
                    if not deck:
                        break
                    waiting.append(deck.pop(0))
                    milled += 1
            gs.log.append(f"[AUTO_EXT] mill {milled} cards to waiting_room (小泉花陽)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 67: PL!HS-bp1-004 夕霧綴理
    # ライブ終了時まで、ライブ中のカード 1 枚につき +1ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_live_cards_count_x1_blade":
        slot = _src_slot(gs, ctx)
        live_cards = _live_in_progress_cards(gs)
        n = len(live_cards)
        if slot is not None and n > 0:
            _add_temp_blade(eng, slot, n)
            try:
                gs.log.append(
                    f"[AUTO_EXT] live_cards={n} -> +{n}blade (夕霧綴理)"
                )
            except Exception:
                pass
        elif slot is not None:
            try:
                gs.log.append("[AUTO_EXT] live_cards=0, no blade (夕霧綴理)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 72: PL!HS-bp1-023 ド！ド！ド！
    # ライブ合計スコア > 相手 かつ ステージに蓮ノ空メンバー → energy deck から 1枚 wait
    # ------------------------------------------------------------------
    if ext_key == "live_success_score_gt_opp_and_hasunosora_energy_wait":
        my_score = _live_score_total(gs)
        opp_score = _opp_live_score_total(gs)
        try:
            if (ctx or {}).get("live_score") is not None:
                my_score = int(ctx["live_score"])
            if (ctx or {}).get("opp_live_score") is not None:
                opp_score = int(ctx["opp_live_score"])
        except Exception:
            pass

        has_hasunosora = _stage_has_group(gs, cards_db, "蓮ノ空")
        if not has_hasunosora:
            try:
                gs.log.append("[AUTO_EXT] no 蓮ノ空 on stage, no energy (ド！ド！ド！)")
            except Exception:
                pass
            return True

        opp_exists = _has_opponent_state(gs)
        if opp_exists:
            if my_score > opp_score:
                added = 0
                try:
                    put_wait = eng.get("_put_wait_energy_from_deck")
                    if callable(put_wait):
                        added = int(put_wait(gs, 1, reason="ド！ド！ド！") or 0)
                    else:
                        rem_fn = eng.get("_energy_remaining_in_deck")
                        clamp_fn = eng.get("_clamp_energy_zone")
                        rem = int(rem_fn(gs) if callable(rem_fn) else 0)
                        if rem > 0:
                            gs.energy_wait = int(getattr(gs, "energy_wait", 0) or 0) + 1
                            if callable(clamp_fn):
                                clamp_fn(gs)
                            added = 1
                except Exception:
                    pass
                try:
                    gs.log.append(f"[AUTO_EXT] live_score {my_score}>{opp_score} & 蓮ノ空 on stage -> energy_wait +{added} (ド！ド！ド！)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append(f"[AUTO_EXT] live_score {my_score}<={opp_score}, no energy (ド！ド！ド！)")
                except Exception:
                    pass
            return True

        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "confirm_effect",
            "text": "【ド！ド！ド！】ライブ成功時：自分の合計スコアが相手より高いなら、エネルギーを1枚ウェイトで置く",
            "options": ["使う", "スキップ"],
            "after_effect_template": "ライブの合計スコアが相手より高く、かつ自分のステージに『蓮ノ空』のメンバーがいる場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。",
            "ctx": {"source_cn": src, "_ext_confirm_op": "energy_wait_plus1"},
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] ド！ド！ド！: confirm energy_wait+1 (my_score={my_score}, opp unavailable)")
        except Exception:
            pass
        return True

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

    # ==================================================================
    # group2_single_target_20260402 新規実装
    # ==================================================================

    # ------------------------------------------------------------------
    # Prompt 22: PL!-bp3-026 Oh,Love&Peace! (ライブ開始時)
    # ライブ終了時まで、ステージのメンバー1人（選択）に +3ブレード
    # cost=手札を2枚控え室に置いてもよい → engine 側 pay_or_skip pending が先行
    # effect handler では choose_stage_member_to_activate pending を流用して
    # 対象メンバーを1人選ばせ、解決時に temp_blade +3
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Prompt 35: PL!-bp4-020 Love wing bell (ライブ開始時)
    # ステージが μ's のみ → ステージメンバー1人をポジションチェンジさせてもよい
    # ------------------------------------------------------------------
    if ext_key == "live_start_mus_only_pick_member_position_change":
        if not _stage_all_group(gs, cards_db, "μ's"):
            try:
                gs.log.append("[AUTO_EXT] stage not all μ's, skip (Love wing bell)")
            except Exception:
                pass
            return True
        occupied = _stage_positions_all_occupied(gs)
        src = str((ctx or {}).get("source_cn") or "")
        if not occupied:
            try:
                gs.log.append("[AUTO_EXT] no stage members, skip (Love wing bell)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in occupied]
        # 選択用 pending: choose_stage_member_to_activate でポジションを選ばせ、
        # 解決時に position_change pending を積む
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates + ["skip"],
            "optional": True,
            "after_ext_key": "live_start_mus_only_pick_member_position_change__resolve",
            "source_cn": src,
            "label": "【Love wing bell】ポジションチェンジするメンバーを選んでください（スキップ可）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Love wing bell: choose member for position_change from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_mus_only_pick_member_position_change__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        if chosen_pos == "SKIP" or chosen_pos not in ("L", "C", "R"):
            try:
                gs.log.append("[AUTO_EXT] position_change skipped (Love wing bell)")
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

    # ------------------------------------------------------------------
    # Prompt 48: PL!-pb1-012 南ことり (登場)
    # Printemps のウェイト状態メンバーを1人までアクティブにする
    # ウェイト = active==False のスロット
    # ------------------------------------------------------------------
    if ext_key == "enter_printemps_activate_up_to_1":
        src = str((ctx or {}).get("source_cn") or "")
        wait_printemps = []
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _card_unit(slot, cards_db) != "Printemps":
                        continue
                    if not bool(getattr(slot, "active", True)):
                        wait_printemps.append((pos, slot))
        except Exception:
            pass

        if not wait_printemps:
            try:
                gs.log.append("[AUTO_EXT] no Printemps wait member to activate (南ことり pb1-012)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in wait_printemps] + ["skip"]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": True,
            "after_ext_key": "enter_printemps_activate_up_to_1__resolve",
            "source_cn": src,
            "label": "【南ことり】アクティブにするPrintempsメンバーを選んでください（スキップ可）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 南ことり pb1-012: choose Printemps wait member from {[p for p,_ in wait_printemps]}")
        except Exception:
            pass
        return True

    if ext_key == "enter_printemps_activate_up_to_1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        if chosen_pos == "SKIP" or chosen_pos not in ("L", "C", "R"):
            try:
                gs.log.append("[AUTO_EXT] Printemps activate skipped (南ことり pb1-012)")
            except Exception:
                pass
            return True
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            try:
                slot.active = True
                gs.log.append(f"[AUTO_EXT] activate {chosen_pos} (南ことり pb1-012 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 80: PL!HS-bp2-007 百生吟子 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室に置いたカードがメンバーカードなら、同名ステージメンバーに green+1 blade+1
    # ctx["discarded_cn"] に捨てたカードの cardnumber が渡される想定。
    # 渡されない場合は green_room の最新カードを参照する。
    # ------------------------------------------------------------------
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
    if ext_key == "enter_pick_mus_member_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        candidates = _green_room_members_by_group(gs, cards_db, "μ's")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no μ's MEMBER in green_room (南ことり bp3-003)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} (南ことり bp3-003) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_member_from_green",
            "text": "控え室のメンバーカードを1枚手札に加える",
            "options": cns,
            "want_kind": "MEMBER",
            "want_group": "μ's",
            "remaining_picks": 1,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 南ことり bp3-003: choose μ's MEMBER from green {cns}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 16: PL!-bp3-004 園田海未 (ライブ開始時)
    # 成功置き場にカードがある場合のみ発動可
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 控え室から μ's のライブカードを1枚手札に加える
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_mus_live_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        if not _success_zone_cards(gs):
            try:
                gs.log.append("[AUTO_EXT] success_zone empty, no effect (園田海未 bp3-004)")
            except Exception:
                pass
            return True
        candidates = _green_room_lives_by_group(gs, cards_db, "μ's")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no μ's LIVE in green_room (園田海未 bp3-004)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} LIVE (園田海未 bp3-004) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_live_from_green",
            "text": "控え室のライブカードを1枚手札に加える",
            "options": cns,
            "want_kind": "LIVE",
            "want_group": "μ's",
            "remaining_picks": 1,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 園田海未 bp3-004: choose μ's LIVE from green {cns}")
        except Exception:
            pass
        return True

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
    if ext_key == "body_pick_hasunosora_live_score_le3_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        candidates = _green_room_lives_by_group_score_le(gs, cards_db, "蓮ノ空", 3)
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no 蓮ノ空 LIVE score<=3 in green_room (日野下花帆)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} (日野下花帆) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_card_from_green",
            "candidates": cns,
            "optional": False,
            "after_ext_key": "body_pick_hasunosora_live_score_le3_from_green__resolve",
            "source_cn": src,
            "label": "【日野下花帆】控え室からスコア3以下の蓮ノ空ライブカードを1枚選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 日野下花帆: choose 蓮ノ空 LIVE score<=3 from green {cns}")
        except Exception:
            pass
        return True

    if ext_key == "body_pick_hasunosora_live_score_le3_from_green__resolve":
        chosen_cn = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_cn") or "").strip()
        gr = _green_room_list(gs)
        found = None
        for c in list(gr):
            if str(getattr(c, "cardnumber", None) or c or "").strip() == chosen_cn:
                found = c
                break
        if found is not None:
            ok = _move_card_from_green_to_hand(gs, found)
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {chosen_cn} (日野下花帆 resolve) ok={ok}")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 他メンバーがいる場合、控え室から みらくらぱーく！ のカードを1枚手札へ
    # 注意: Prompt 77（ライブ開始時+2ブレード）は既存実装。壊さない。
    # ------------------------------------------------------------------
    if ext_key == "enter_other_member_exists_pick_mirakupark_from_green":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        if not _stage_has_any_other_member(gs, exclude_pos=src_pos):
            try:
                gs.log.append("[AUTO_EXT] no other member on stage (大沢瑠璃乃 bp2-005 enter)")
            except Exception:
                pass
            return True
        candidates = _green_room_cards_by_group_any_type(gs, cards_db, "みらくらぱーく！")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no みらくらぱーく！ card in green_room (大沢瑠璃乃 bp2-005 enter)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} (大沢瑠璃乃 bp2-005 enter) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_card_from_green",
            "candidates": cns,
            "optional": False,
            "after_ext_key": "enter_other_member_exists_pick_mirakupark_from_green__resolve",
            "source_cn": src,
            "label": "【大沢瑠璃乃】控え室からみらくらぱーく！のカードを1枚選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 大沢瑠璃乃 bp2-005 enter: choose みらくらぱーく！ from green {cns}")
        except Exception:
            pass
        return True

    if ext_key == "enter_other_member_exists_pick_mirakupark_from_green__resolve":
        chosen_cn = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_cn") or "").strip()
        gr = _green_room_list(gs)
        found = None
        for c in list(gr):
            if str(getattr(c, "cardnumber", None) or c or "").strip() == chosen_cn:
                found = c
                break
        if found is not None:
            ok = _move_card_from_green_to_hand(gs, found)
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {chosen_cn} (大沢瑠璃乃 bp2-005 enter resolve) ok={ok}")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 27: PL!-bp4-005 星空凛 (ライブ開始時)
    # ブレード5以上の μ's メンバーがいない場合、このメンバーはセンター以外へポジションチェンジ
    # センター以外 = L / R のみ candidates にする
    # ------------------------------------------------------------------
    if ext_key == "live_start_no_mus_blade5_force_not_center":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        has_heavy_mus = False
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _card_group(slot, cards_db) == "μ's" and _slot_total_blade(slot) >= 5:
                        has_heavy_mus = True
                        break
        except Exception:
            pass

        if has_heavy_mus:
            try:
                gs.log.append("[AUTO_EXT] μ's blade>=5 exists, no position_change (星空凛)")
            except Exception:
                pass
            return True

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
    # Prompt 56: PL!-pb1-030 Cutie Panther (ライブ成功時) — 後半のみ EFFECT_ONLY
    # ステージに名前の異なる BiBi が2人以上 → 控え室から BiBi メンバー1枚手札へ
    # 前半（必要ハート減算）は NEEDS_ENGINE のため未実装。
    # ------------------------------------------------------------------
    if ext_key == "live_success_bibi_2diff_pick_bibi_member_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        diff_count = _stage_unit_count_diff_names(gs, cards_db, "BiBi")
        if diff_count < 2:
            try:
                gs.log.append(f"[AUTO_EXT] BiBi diff_names={diff_count}<2, no effect (Cutie Panther)")
            except Exception:
                pass
            return True
        candidates = _green_room_members_by_group(gs, cards_db, "BiBi")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no BiBi MEMBER in green_room (Cutie Panther)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} BiBi (Cutie Panther) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_member_from_green",
            "text": "控え室のメンバーカードを1枚手札に加える",
            "options": cns,
            "want_kind": "MEMBER",
            "want_group": "BiBi",
            "remaining_picks": 1,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Cutie Panther: choose BiBi MEMBER from green {cns}")
        except Exception:
            pass
        return True

    return False

