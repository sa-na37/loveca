# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_stage_triggers_20260413k
from __future__ import annotations

"""llocg_ui.effects.stage_triggers

登場・BODY・leave-stage 近辺の ext apply 正本。
ここでは live_start / energy / position 以外で、
既存 helper / pending で閉じている残りの汎用寄り処理を受け持つ。
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def try_apply_stage_triggers_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, str],
    ctx: Dict[str, Any],
    ext_key: str,
) -> bool:

    # ==================================================================
    # bp2_batch2_20260410b Claude merge (GPT debugged)
    # ==================================================================

    # PL!HS-bp2-002 村野さやか (登場)
    # PL!HS-bp2-002 村野さやか (BODY)
    if ext_key == "body_higher_cost_member_exists_blade3":
        slot = _src_slot(gs, ctx)
        src = str((ctx or {}).get('source_cn') or '')
        if slot is None:
            return True
        my_cost = _card_cost(slot, cards_db)
        src_pos = str((ctx or {}).get('src_pos') or (ctx or {}).get('pos') or '').upper()
        found_higher = False
        try:
            st = getattr(gs, 'stage', None)
            if isinstance(st, dict):
                for pos in ('L','C','R'):
                    if pos == src_pos:
                        continue
                    other = st.get(pos)
                    if other is None or not bool(getattr(other, 'cardnumber', None)):
                        continue
                    if _card_type_norm(other, cards_db) == 'MEMBER' and _card_cost(other, cards_db) > my_cost:
                        found_higher = True
                        break
        except Exception:
            pass
        try:
            gs.log.append(f"[AUTO_EXT] 村野さやか BODY: my_cost={my_cost} found_higher={found_higher} ({src})")
        except Exception:
            pass
        if found_higher:
            _add_temp_blade(eng, slot, 3)
        return True

    # PL!HS-bp2-006 藤島慈 (BODY)
    if ext_key == 'body_mirakupark_others_count_blade':
        slot = _src_slot(gs, ctx)
        src_pos = str((ctx or {}).get('src_pos') or (ctx or {}).get('pos') or '').upper()
        if slot is None:
            return True
        count = 0
        try:
            st = getattr(gs, 'stage', None)
            if isinstance(st, dict):
                for pos in ('L','C','R'):
                    if pos == src_pos:
                        continue
                    other = st.get(pos)
                    if other is None or not bool(getattr(other, 'cardnumber', None)):
                        continue
                    if _card_type_norm(other, cards_db) == 'MEMBER' and _label_matches_group_or_unit(other, cards_db, 'みらくらぱーく！'):
                        count += 1
        except Exception:
            pass
        if count > 0:
            _add_temp_blade(eng, slot, count)
        try:
            gs.log.append(f"[AUTO_EXT] 藤島慈 BODY: みらくらぱーく！ others={count}")
        except Exception:
            pass
        return True

    # PL!HS-bp2-017 徒町小鈴 (登場)
    if ext_key == 'enter_green_ge10_draw1':
        green_count = len(_green_room_list(gs))
        if green_count >= 10:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(f"[AUTO_EXT] 徒町小鈴: green>=10 -> draw {drawn}")
            except Exception:
                pass
        else:
            try:
                gs.log.append(f"[AUTO_EXT] 徒町小鈴: green_room={green_count}<10, no draw")
            except Exception:
                pass
        return True

    # PL!HS-bp2-014 大沢瑠璃乃 (登場)
    if ext_key == 'enter_draw1_and_cannot_live_until_end_of_live':
        drawn = _draw_cards(eng, gs, 1)
        try:
            gs.cannot_live_until_end_of_live = True
        except Exception:
            setattr(gs, 'cannot_live_until_end_of_live', True)
        try:
            gs.log.append(f"[AUTO_EXT] 大沢瑠璃乃 bp2-014: draw {drawn}; cannot live until end of live")
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
    # bp2_batch3_local_20260413f
    {
        "id": "enter_sayaka_bp2011_mill5",
        "effect_template": "デッキの上からカードを5枚控え室に置く。",
        "ext_key": "enter_mill5",
    },
    {
        "id": "body_megumi_bp2015_leave_stage_draw2_discard1",
        "effect_template": "このメンバーがステージから控え室に置かれたとき、カードを2枚引き、手札を1枚控え室に置く。",
        "ext_key": "body_leave_stage_draw2_discard1",
    },

    # Prompt 80: PL!HS-bp2-007 百生吟子 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室に置いたカードがメンバーカードなら、同名ステージメンバーに green+1 blade+1
    # ctx["discarded_cn"] に捨てたカードの cardnumber が渡される想定。
    # 渡されない場合は green_room の最新カードを参照する。
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Prompt 56: PL!-pb1-030 Cutie Panther (ライブ成功時) — 後半のみ EFFECT_ONLY
    # ステージに名前の異なる BiBi が2人以上 → 控え室から BiBi メンバー1枚手札へ
    # 前半（必要ハート減算）は NEEDS_ENGINE のため未実装。
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # bp2_batch3_local_20260413f: PL!HS-bp2-011 村野さやか (登場)
    # デッキ上からカードを5枚控え室に置く。
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # bp2_batch3_local_20260413f: PL!HS-bp2-015 藤島慈 (自動/BODY)
    # leave-stage -> draw2, discard1
    # ------------------------------------------------------------------
    if ext_key == "body_leave_stage_draw2_discard1":
        trigger = str((ctx or {}).get("trigger") or "").lower()
        if trigger and trigger not in ("leave_stage", "stage_to_green", "stage_leave"):
            try:
                gs.log.append(f"[AUTO_EXT] 藤島慈 bp2-015: trigger={trigger!r} not leave-stage, skip")
            except Exception:
                pass
            return True
        drawn = _draw_cards(eng, gs, 2)
        try:
            gs.log.append(f"[AUTO_EXT] 藤島慈 bp2-015: draw {drawn} (leave-stage)")
        except Exception:
            pass
        enqueue_discard = eng.get("_enqueue_discard_from_hand")
        if callable(enqueue_discard):
            try:
                enqueue_discard(gs, 1, label="【藤島慈】手札を1枚控え室に置く")
            except Exception as e:
                try:
                    gs.log.append(f"[ERR] 藤島慈 bp2-015: enqueue_discard_from_hand failed: {e}")
                except Exception:
                    pass
        else:
            try:
                gs.log.append("[ERR] 藤島慈 bp2-015: _enqueue_discard_from_hand not found")
            except Exception:
                pass
        return True

    return False
