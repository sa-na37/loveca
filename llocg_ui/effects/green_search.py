# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_green_search_20260413c
from __future__ import annotations

"""llocg_ui.effects.green_search

控え室(green_room)からカードを回収する ext handler 群の正本。

方針:
- green→hand 系だけを apply.py から切り出す
- runtime の挙動は変えない
- ext_key に該当しない場合だけ False を返し、apply.py の残りへ委譲する
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def _resolve_green_choice_to_hand(gs: Any, chosen_cn: str, src_label: str) -> bool:
    chosen_cn = str(chosen_cn or '').strip()
    if not chosen_cn:
        return True
    gr = _green_room_list(gs)
    found = None
    for c in list(gr):
        if str(getattr(c, 'cardnumber', None) or c or '').strip() == chosen_cn:
            found = c
            break
    if found is not None:
        ok = _move_card_from_green_to_hand(gs, found)
        try:
            gs.log.append(f"[AUTO_EXT] green->hand {chosen_cn} ({src_label}) ok={ok}")
        except Exception:
            pass
    return True


def try_apply_green_search_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    ctx: Dict[str, Any] | None = None,
) -> bool:
    ctx = ctx or {}
    ext_key = str((rule or {}).get('ext_key') or '').strip()

    if ext_key == "enter_pick_cost_le2_member_from_green_up_to_2":
        src = str((ctx or {}).get("source_cn") or "")
        candidates = [
            c for c in _green_room_list(gs)
            if _card_type_norm(c, cards_db) == 'MEMBER' and _card_cost(c, cards_db) <= 2
        ]
        try:
            gs.log.append(f"[AUTO_EXT] 村野さやか: candidates={len(candidates)} (multi-pick) ({src})")
        except Exception:
            pass
        if not candidates:
            return True
        cns = [str(getattr(c, 'cardnumber', None) or c or '') for c in candidates]
        payload = {
            'kind': 'choose_member_from_green_multi_up_to',
            'text': '【村野さやか】控え室からコスト2以下のメンバーカードを0〜2枚選んで手札に加える',
            'options': cns,
            'min_picks': 0,
            'max_picks': min(2, len(cns)),
            'want_kind': 'MEMBER',
            'source_cn': src,
        }
        try:
            getattr(gs, 'pending').append(payload)
            gs.log.append(f"[PENDING] 村野さやか: multi-pick cost<=2 MEMBER opts={cns}")
        except Exception:
            pass
        return True

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

    if ext_key == "body_pick_live_req_yellow_ge3_from_green":
        src = str((ctx or {}).get("source_cn") or "PL!-PR-003")
        return _enqueue_pick_live_req_heart_from_green(gs, cards_db, 'yellow', 3, src)

    if ext_key == "body_pick_live_req_pink_ge3_from_green":
        src = str((ctx or {}).get("source_cn") or "PL!-PR-004")
        return _enqueue_pick_live_req_heart_from_green(gs, cards_db, 'pink', 3, src)

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
