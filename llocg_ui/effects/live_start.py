# -*- coding: utf-8 -*-
# BUILD_TAG: live_start_choose_heart_token_text_fix_20260430b
from __future__ import annotations

"""llocg_ui.effects.live_start

ライブ開始時に解決する ext apply の正本。
blade / heart / draw / discard / choose 系のうち、
既存 helper / pending で閉じているものを apply から外出しした完成版。
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def _ctx_src_pos(ctx: Dict[str, Any]) -> str:
    return str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()


def _ctx_source_cn(ctx: Dict[str, Any]) -> str:
    return str((ctx or {}).get("source_cn") or "")


def _stage_slot_at(gs: Any, pos: str) -> Any:
    st = getattr(gs, "stage", None)
    if not isinstance(st, dict):
        return None
    return st.get(str(pos or "").upper())


def _append_pending(gs: Any, payload: Dict[str, Any], log_line: str = "") -> None:
    try:
        getattr(gs, "pending").append(payload)
        if log_line:
            gs.log.append(log_line)
    except Exception:
        pass


def _apply_temp_bonus(
    eng: Dict[str, Any],
    slot: Any,
    *,
    blade: int = 0,
    hearts: Dict[str, int] | None = None,
) -> None:
    if slot is None:
        return
    if blade:
        _add_temp_blade(eng, slot, int(blade))
    if hearts:
        _add_temp_hearts(eng, slot, dict(hearts))


def _queue_choose_stage_member(
    gs: Any,
    *,
    candidates: list[str],
    after_ext_key: str,
    source_cn: str,
    label: str,
    optional: bool = False,
    text: str = "",
    extra_payload: Dict[str, Any] | None = None,
    log_line: str = "",
) -> None:
    payload = {
        "kind": "choose_stage_member_to_activate",
        "candidates": list(candidates),
        "optional": bool(optional),
        "after_ext_key": after_ext_key,
        "source_cn": source_cn,
        "label": label,
    }
    if text:
        payload["text"] = text
    if extra_payload:
        payload.update(dict(extra_payload))
    _append_pending(gs, payload, log_line)


def _heart_token(label: str) -> str:
    m = {
        "桃": "<(桃)>",
        "赤": "<(赤)>",
        "黄": "<(黄)>",
        "緑": "<(緑)>",
        "青": "<(青)>",
        "紫": "<(紫)>",
        "任意": "<(任意)>",
        "虹": "<(虹)>",
    }
    s = str(label or "").strip()
    return m.get(s, s)


def _token_join_options(options: list[str]) -> str:
    vals = [_heart_token(x) for x in list(options or []) if str(x or "").strip()]
    return " / ".join(vals)


def _queue_choose_heart_color(
    gs: Any,
    *,
    pos: str,
    source_cn: str,
    options: list[str],
    text: str,
    log_line: str,
    detail_text: str = "",
) -> None:
    payload = {
        "kind": "choose_heart_color",
        "pos": str(pos or "").upper(),
        "n": 1,
        "text": text,
        "options": list(options),
        "source_cn": source_cn,
        "src_pos": str(pos or "").upper(),
    }
    if str(detail_text or "").strip():
        payload["detail_text"] = str(detail_text)
        payload["effect_text"] = str(detail_text)
    _append_pending(gs, payload, log_line)


def _parse_option_labels_csv(raw: Any, default: list[str] | None = None) -> list[str]:
    vals = [str(x).strip() for x in str(raw or "").split(",") if str(x).strip()]
    return vals or list(default or [])


def _queue_generic_choose_heart(
    gs: Any,
    *,
    src_pos: str,
    source_cn: str,
    options: list[str],
    require_other_member: bool,
) -> bool:
    if require_other_member and not _stage_has_any_other_member(gs, exclude_pos=src_pos):
        try:
            gs.log.append("[AUTO_EXT] no other member on stage, no effect (choose heart)")
        except Exception:
            pass
        return True
    pretty = _token_join_options(options) if options else "好きな色"
    _queue_choose_heart_color(
        gs,
        pos=src_pos,
        source_cn=source_cn,
        options=options,
        text=f"{source_cn}: {pretty}から1つ選ぶ → ライブ終了時まで+1",
        detail_text=f"{pretty}のうち、1つを選ぶ。ライブ終了時まで、選んだハートを1つ得る。",
        log_line=f"[PENDING] {source_cn}: choose heart color",
    )
    return True


def _count_cards_for_heart_bonus(gs: Any, *, count_source: str) -> int:
    src = str(count_source or "").strip()
    if src == "success_zone":
        return len(_success_zone_cards(gs))  # noqa: F405
    return 0


def _queue_choose_heart_then_counted_bonus(
    gs: Any,
    *,
    src_pos: str,
    source_cn: str,
    options: list[str],
    source_name: str,
    count_source: str,
    no_effect_log: str,
) -> bool:
    count = _count_cards_for_heart_bonus(gs, count_source=count_source)
    if count <= 0:
        try:
            gs.log.append(f"[AUTO_EXT] {no_effect_log}")
        except Exception:
            pass
        return True

    # 共通部を二つに分ける:
    # 1. 「＜色A＞か＜色B＞か＜色C＞のうち、1つを選ぶ。」
    # 2. 「成功ライブ置き場のカード1枚につき、選んだハートを1つ得る。」
    pretty = _token_join_options(options) if options else "好きな色"
    label_head = source_name or source_cn or "カード"
    count_label = "自分の成功ライブカード置き場にあるカード"
    _queue_choose_heart_color(
        gs,
        pos=src_pos,
        source_cn=source_cn,
        options=options,
        text=f"【{label_head}】{pretty}から1つ選ぶ",
        detail_text=f"{pretty}のうち、1つを選ぶ。ライブ終了時まで、{count_label}1枚につき、選んだハートを1つ得る。",
        log_line=f"[PENDING] {label_head}: choose heart color then counted bonus x{count}",
    )
    try:
        p = getattr(gs, 'pending', [])[-1]
        if isinstance(p, dict):
            p['n'] = int(count)
            p['count_source'] = str(count_source or '')
            p['counted_bonus_text'] = f"ライブ終了時まで、{count_label}1枚につき、選んだハートを1つ得る。"
    except Exception:
        pass
    return True


def _ctx_choice_pos(ctx: Dict[str, Any]) -> str:
    return str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()


def _activate_slot(slot: Any) -> None:
    if slot is not None:
        try:
            slot.active = True
        except Exception:
            pass


def _queue_activate_wait_member_and_both_temp_bonus(
    gs: Any,
    *,
    candidates: list[str],
    source_cn: str,
    src_pos: str,
    source_name: str,
    select_text: str,
    hearts: Dict[str, int] | None = None,
    blade: int = 0,
    log_line: str = "",
) -> None:
    label_head = source_name or source_cn or "カード"
    _queue_choose_stage_member(
        gs,
        candidates=candidates,
        after_ext_key="live_start_activate_wait_member_and_both_temp_bonus__resolve",
        source_cn=source_cn,
        label=f"【{label_head}】{select_text}",
        text=f"【{label_head}】{select_text}",
        extra_payload={
            "ctx": {
                "src_pos": src_pos,
                "source_cn": source_cn,
                "source_name": label_head,
                "hearts": dict(hearts or {}),
                "blade": int(blade or 0),
            }
        },
        log_line=log_line,
    )


def _apply_activate_wait_member_and_both_temp_bonus(
    eng: Dict[str, Any],
    gs: Any,
    *,
    src_pos: str,
    chosen_pos: str,
    hearts: Dict[str, int] | None = None,
    blade: int = 0,
    source_name: str = "カード",
) -> bool:
    st = getattr(gs, "stage", None)
    if not isinstance(st, dict):
        return True
    src_slot = st.get(str(src_pos or "").upper())
    dst_slot = st.get(str(chosen_pos or "").upper())
    if dst_slot is None:
        try:
            gs.log.append(f"[ERR] {source_name} resolve: empty target {chosen_pos}")
        except Exception:
            pass
        return True
    _activate_slot(dst_slot)
    _apply_temp_bonus(eng, src_slot, blade=blade, hearts=dict(hearts or {}))
    _apply_temp_bonus(eng, dst_slot, blade=blade, hearts=dict(hearts or {}))
    return True


def _card_display_name_with_fallback(eng: Dict[str, Any], cards_db: Dict[str, Any], cn: str) -> str:
    name = _card_name(cn, cards_db)
    if name:
        return name
    try:
        canon_fn = eng.get("_canon_cardno")
        get_card_fn = eng.get("_get_card")
        canon_cn = canon_fn(cn) if callable(canon_fn) else str(cn or "")
        ci = get_card_fn(cards_db, canon_cn) if callable(get_card_fn) else None
        return str(
            getattr(ci, "cardname", "") or
            getattr(ci, "name", "") or
            ((ci if isinstance(ci, dict) else {}).get("cardname")) or
            ((ci if isinstance(ci, dict) else {}).get("name")) or
            ""
        )
    except Exception:
        return ""


def _same_name_or_card_match(eng: Dict[str, Any], cards_db: Dict[str, Any], slot_obj: Any, discarded_cn: str, discarded_name: str) -> bool:
    slot_cn = str(getattr(slot_obj, "cardnumber", "") or "")
    try:
        canon_fn = eng.get("_canon_cardno")
        if callable(canon_fn):
            if canon_fn(slot_cn) == canon_fn(discarded_cn):
                return True
        elif slot_cn == discarded_cn:
            return True
    except Exception:
        if slot_cn == discarded_cn:
            return True
    slot_name = _card_name(slot_obj, cards_db)
    if discarded_name and slot_name and slot_name == discarded_name:
        return True
    slot_name2 = _card_display_name_with_fallback(eng, cards_db, slot_cn)
    return bool(discarded_name and slot_name2 and slot_name2 == discarded_name)


def _matching_stage_members_for_discarded(eng: Dict[str, Any], gs: Any, cards_db: Dict[str, Any], discarded_cn: str, discarded_name: str) -> list[tuple[str, Any]]:
    matched: list[tuple[str, Any]] = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is None or not bool(getattr(slot, "cardnumber", None)):
                    continue
                if _same_name_or_card_match(eng, cards_db, slot, discarded_cn, discarded_name):
                    matched.append((pos, slot))
    except Exception:
        pass
    return matched


def _parse_hearts_csv(raw: Any) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for part in [str(x).strip() for x in str(raw or "").split(",") if str(x).strip()]:
        if ":" in part:
            k, v = part.split(":", 1)
            try:
                n = int(str(v).strip() or "0")
            except Exception:
                n = 0
        else:
            k, n = part, 1
        kk = str(k).strip()
        if kk and n > 0:
            out[kk] = out.get(kk, 0) + int(n)
    return out




def _stage_other_wait_positions(gs: Any, exclude_pos: str = "") -> list[str]:
    out: list[str] = []
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return out
        ex = str(exclude_pos or "").upper()
        for pos in ("L", "C", "R"):
            if pos == ex:
                continue
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, "cardnumber", None)):
                continue
            if not bool(getattr(slot, "active", True)):
                out.append(pos)
    except Exception:
        return []
    return out
def _stage_target_candidates(
    gs: Any,
    cards_db: Dict[str, Any],
    *,
    src_pos: str = "",
    exclude_self: bool = False,
    group_eq: str = "",
) -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    for pos, slot in _stage_positions_all_occupied(gs):
        if exclude_self and pos == str(src_pos or "").upper():
            continue
        if group_eq and _card_group(slot, cards_db) != group_eq:
            continue
        out.append((pos, slot))
    return out


def _queue_generic_pick_stage_member_temp_bonus(
    gs: Any,
    *,
    candidates: list[str],
    source_cn: str,
    source_name: str,
    select_text: str,
    blade: int,
    hearts: Dict[str, int],
    log_line: str,
) -> None:
    label_head = source_name or source_cn or "カード"
    _queue_choose_stage_member(
        gs,
        candidates=candidates,
        after_ext_key="live_start_pick_stage_member_temp_bonus__resolve",
        source_cn=source_cn,
        label=f"【{label_head}】{select_text}",
        text=f"【{label_head}】{select_text}",
        extra_payload={
            "ctx": {
                "blade": int(blade or 0),
                "hearts": dict(hearts or {}),
                "source_name": label_head,
            }
        },
        log_line=log_line,
    )




def _parse_positions_csv(raw: Any) -> list[str]:
    out: list[str] = []
    for x in [str(v).strip().upper() for v in str(raw or "").split(",") if str(v).strip()]:
        if x in ("L", "C", "R") and x not in out:
            out.append(x)
    return out


def _apply_stage_temp_bonus_candidates(
    eng: Dict[str, Any],
    gs: Any,
    cards_db: Dict[str, Any],
    *,
    src_pos: str = "",
    exclude_self: bool = False,
    group_eq: str = "",
    positions: list[str] | None = None,
    blade: int = 0,
    hearts: Dict[str, int] | None = None,
    source_name: str = "カード",
    no_target_log: str = "",
) -> bool:
    posset = set([str(x).strip().upper() for x in (positions or []) if str(x).strip()])
    candidates = _stage_target_candidates(
        gs, cards_db, src_pos=src_pos, exclude_self=exclude_self, group_eq=group_eq
    )
    if posset:
        candidates = [(pos, slot) for pos, slot in candidates if pos in posset]
    if not candidates:
        try:
            gs.log.append(f"[AUTO_EXT] {no_target_log or ('no valid targets (' + str(source_name or 'カード') + ')')}")
        except Exception:
            pass
        return True
    for pos, slot in candidates:
        _apply_temp_bonus(eng, slot, blade=blade, hearts=dict(hearts or {}))
    desc_parts: list[str] = []
    if int(blade or 0) > 0:
        desc_parts.append(f"+{int(blade)}blade")
    for hk, hv in dict(hearts or {}).items():
        try:
            n = int(hv or 0)
        except Exception:
            n = 0
        if n > 0:
            desc_parts.append(f"+{hk}x{n}")
    desc = " ".join(desc_parts) if desc_parts else "+bonus"
    try:
        gs.log.append(f"[AUTO_EXT] {desc} -> {[pos for pos, _ in candidates]} ({source_name})")
    except Exception:
        pass
    return True
def _apply_target_temp_bonus_with_log(
    eng: Dict[str, Any],
    gs: Any,
    *,
    pos: str,
    slot: Any,
    blade: int,
    hearts: Dict[str, int],
    source_name: str,
    resolve: bool = False,
) -> None:
    _apply_temp_bonus(eng, slot, blade=blade, hearts=hearts)
    desc_parts: list[str] = []
    if blade:
        desc_parts.append(f"+{int(blade)}blade")
    for hk, hv in dict(hearts or {}).items():
        if int(hv or 0) > 0:
            desc_parts.append(f"+{hk}x{int(hv)}")
    desc = " ".join(desc_parts) if desc_parts else "+bonus"
    tail = " resolve" if resolve else ""
    try:
        gs.log.append(f"[AUTO_EXT] {desc} -> {pos} ({source_name}{tail})")
    except Exception:
        pass

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

    if ext_key == "live_start_pick_stage_member_temp_bonus":
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        source_name = str((gd or {}).get("source_name") or src or "カード")
        select_text = str((gd or {}).get("select_text") or "対象メンバーを選んでください")
        no_target_log = str((gd or {}).get("no_target_log") or f"no valid targets ({source_name})")
        exclude_self = str((gd or {}).get("exclude_self") or "0") == "1"
        group_eq = str((gd or {}).get("group_eq") or "")
        auto_if_single = str((gd or {}).get("auto_if_single") or "0") == "1"
        blade = int(str((gd or {}).get("blade") or "0") or "0")
        hearts = _parse_hearts_csv((gd or {}).get("hearts"))
        candidates = _stage_target_candidates(
            gs, cards_db, src_pos=src_pos, exclude_self=exclude_self, group_eq=group_eq
        )
        if not candidates:
            try:
                gs.log.append(f"[AUTO_EXT] {no_target_log}")
            except Exception:
                pass
            return True
        if len(candidates) == 1 and auto_if_single:
            pos, slot = candidates[0]
            _apply_target_temp_bonus_with_log(
                eng, gs, pos=pos, slot=slot, blade=blade, hearts=hearts, source_name=source_name, resolve=False
            )
            return True
        _queue_generic_pick_stage_member_temp_bonus(
            gs,
            candidates=[pos for pos, _ in candidates],
            source_cn=src,
            source_name=source_name,
            select_text=select_text,
            blade=blade,
            hearts=hearts,
            log_line=f"[PENDING] {source_name}: choose member from {[pos for pos, _ in candidates]}",
        )
        return True

    if ext_key == "live_start_pick_stage_member_temp_bonus__resolve":
        chosen_pos = _ctx_choice_pos(ctx)
        slot = _stage_slot_at(gs, chosen_pos)
        if slot is not None:
            blade = int((ctx or {}).get("blade") or 0)
            hearts = dict((ctx or {}).get("hearts") or {})
            source_name = str((ctx or {}).get("source_name") or _ctx_source_cn(ctx) or "カード")
            _apply_target_temp_bonus_with_log(
                eng, gs, pos=chosen_pos, slot=slot, blade=blade, hearts=hearts, source_name=source_name, resolve=True
            )
        return True


    # ------------------------------------------------------------------
    # Prompt 32: PL!-bp4-017 小泉花陽 (ライブ開始時)
    # センター(C)の μ's メンバーに +1ブレード（対象固定、選択不要）

    # ------------------------------------------------------------------
    if ext_key == "live_start_apply_stage_temp_bonus":
        src_pos = _ctx_src_pos(ctx)
        source_name = str((gd or {}).get("source_name") or _ctx_source_cn(ctx) or "カード")
        no_target_log = str((gd or {}).get("no_target_log") or f"no valid targets ({source_name})")
        exclude_self = str((gd or {}).get("exclude_self") or "0") == "1"
        group_eq = str((gd or {}).get("group_eq") or "")
        positions = _parse_positions_csv((gd or {}).get("positions"))
        blade = int(str((gd or {}).get("blade") or "0") or "0")
        hearts = _parse_hearts_csv((gd or {}).get("hearts"))
        return _apply_stage_temp_bonus_candidates(
            eng, gs, cards_db,
            src_pos=src_pos,
            exclude_self=exclude_self,
            group_eq=group_eq,
            positions=positions,
            blade=blade,
            hearts=hearts,
            source_name=source_name,
            no_target_log=no_target_log,
        )

    # ------------------------------------------------------------------
    # Prompt 37: PL!-bp4-024 小夜啼鳥恋詩 (ライブ開始時)
    # ステージの μ's メンバー1人（選択）に +1ブレード


    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Prompt 46: PL!-pb1-010 高坂穂乃果 (ライブ開始時)
    # このメンバー以外のステージメンバー全員に +1ブレード（選択なし）



    # ------------------------------------------------------------------

    if ext_key == "live_start_discarded_member_same_name_stage_member_temp_bonus":
        src = _ctx_source_cn(ctx)
        source_name = str((gd or {}).get("source_name") or src or "カード")
        select_text = str((gd or {}).get("select_text") or "と同名のメンバーを選んでください")
        blade = int(str((gd or {}).get("blade") or "0") or "0")
        hearts = _parse_hearts_csv((gd or {}).get("hearts"))
        discarded_cn = str((ctx or {}).get("discarded_cn") or "").strip()
        if not discarded_cn:
            top = _green_room_top(gs)
            if top is not None:
                discarded_cn = str(getattr(top, "cardnumber", None) or top or "").strip()

        if not discarded_cn:
            try:
                gs.log.append(f"[AUTO_EXT] could not identify discarded card ({source_name})")
            except Exception:
                pass
            return True

        discarded_type = _card_type_norm(discarded_cn, cards_db)
        required_type = str((gd or {}).get("discarded_type") or "MEMBER").upper()
        if required_type and discarded_type != required_type:
            try:
                gs.log.append(f"[AUTO_EXT] discarded {discarded_cn} is not {required_type} (type={discarded_type}), no effect ({source_name})")
            except Exception:
                pass
            return True

        discarded_name = _card_display_name_with_fallback(eng, cards_db, discarded_cn)
        if not discarded_name:
            try:
                gs.log.append(f"[AUTO_EXT] name fallback by cardnumber for {discarded_cn} ({source_name})")
            except Exception:
                pass

        matched = _matching_stage_members_for_discarded(eng, gs, cards_db, discarded_cn, discarded_name)
        if not matched:
            try:
                gs.log.append(f"[AUTO_EXT] no stage member named '{discarded_name}', no effect ({source_name})")
            except Exception:
                pass
            return True

        if len(matched) == 1:
            pos, slot = matched[0]
            _apply_target_temp_bonus_with_log(
                eng, gs, pos=pos, slot=slot, blade=blade, hearts=hearts, source_name=source_name, resolve=False
            )
            return True

        _queue_choose_stage_member(
            gs,
            candidates=[pos for pos, _ in matched],
            after_ext_key="live_start_discarded_member_same_name_stage_member_temp_bonus__resolve",
            source_cn=src,
            label=f"【{source_name}】{discarded_name}{select_text}",
            text=f"【{source_name}】{discarded_name}{select_text}",
            extra_payload={
                "ctx": {
                    "discarded_name": discarded_name,
                    "blade": blade,
                    "hearts": dict(hearts or {}),
                    "source_name": source_name,
                }
            },
            log_line=f"[PENDING] {source_name}: choose same-name member from {[pos for pos, _ in matched]}",
        )
        return True

    if ext_key == "live_start_discarded_member_same_name_stage_member_temp_bonus__resolve":
        chosen_pos = _ctx_choice_pos(ctx)
        slot = _stage_slot_at(gs, chosen_pos)
        if slot is not None:
            blade = int((ctx or {}).get("blade") or 0)
            hearts = dict((ctx or {}).get("hearts") or {})
            source_name = str((ctx or {}).get("source_name") or _ctx_source_cn(ctx) or "カード")
            _apply_target_temp_bonus_with_log(
                eng, gs, pos=chosen_pos, slot=slot, blade=blade, hearts=hearts, source_name=source_name, resolve=True
            )
        return True

    # ==================================================================
    # group3_A7B2_20260406a 新規実装
    # ==================================================================

    # ------------------------------------------------------------------
    # Generic choose-heart family
    # - any color
    # - 桃/黄/紫 限定
    # - 他メンバー存在条件付き
    # parameters are supplied from registry.gd
    # ------------------------------------------------------------------
    if ext_key == "live_start_choose_heart":
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        options = _parse_option_labels_csv((gd or {}).get("option_labels"), ["桃", "赤", "黄", "緑", "青", "紫"])
        require_other_member = str((gd or {}).get("require_other_member") or "0") == "1"
        return _queue_generic_choose_heart(
            gs,
            src_pos=src_pos,
            source_cn=src,
            options=options,
            require_other_member=require_other_member,
        )


    if ext_key == "live_start_choose_heart_per_success_count":
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        options = _parse_option_labels_csv((gd or {}).get("option_labels"), ["桃", "赤", "黄", "緑", "青", "紫"])
        source_name = str((gd or {}).get("source_name") or src or "カード")
        count_source = str((gd or {}).get("count_source") or "success_zone")
        no_effect_log = str((gd or {}).get("no_effect_log") or f"{count_source} empty, no effect ({source_name})")
        return _queue_choose_heart_then_counted_bonus(
            gs,
            src_pos=src_pos,
            source_cn=src,
            options=options,
            source_name=source_name,
            count_source=count_source,
            no_effect_log=no_effect_log,
        )


    if ext_key == "live_start_activate_wait_member_and_both_temp_bonus":
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        source_name = str((gd or {}).get("source_name") or src or "カード")
        select_text = str((gd or {}).get("select_text") or "アクティブにするメンバーを選んでください")
        no_target_log = str((gd or {}).get("no_target_log") or f"no other wait member on stage ({source_name})")
        blade = int(str((gd or {}).get("blade") or "0") or "0")
        hearts = _parse_hearts_csv((gd or {}).get("hearts"))
        wait_others = _stage_other_wait_positions(gs, exclude_pos=src_pos)
        if not wait_others:
            try:
                gs.log.append(f"[AUTO_EXT] {no_target_log}")
            except Exception:
                pass
            return True
        if len(wait_others) == 1:
            return _apply_activate_wait_member_and_both_temp_bonus(
                eng, gs, src_pos=src_pos, chosen_pos=wait_others[0], hearts=hearts, blade=blade, source_name=source_name
            )
        _queue_activate_wait_member_and_both_temp_bonus(
            gs,
            candidates=wait_others,
            source_cn=src,
            src_pos=src_pos,
            source_name=source_name,
            select_text=select_text,
            hearts=hearts,
            blade=blade,
            log_line=f"[PENDING] {source_name}: choose wait member from {wait_others}",
        )
        return True

    if ext_key == "live_start_activate_wait_member_and_both_temp_bonus__resolve":
        chosen_pos = _ctx_choice_pos(ctx)
        src_pos = _ctx_src_pos(ctx)
        blade = int((ctx or {}).get("blade") or 0)
        hearts = dict((ctx or {}).get("hearts") or {})
        source_name = str((ctx or {}).get("source_name") or _ctx_source_cn(ctx) or "カード")
        return _apply_activate_wait_member_and_both_temp_bonus(
            eng, gs, src_pos=src_pos, chosen_pos=chosen_pos, hearts=hearts, blade=blade, source_name=source_name
        )

    # ------------------------------------------------------------------
    # Prompt 73: PL!HS-bp2-001 日野下花帆 (起動)
    # コスト <(E)><(E)> → engine 側起動コスト処理
    # 控え室からスコア3以下の 蓮ノ空 ライブカードを1枚手札に加える
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 他メンバーがいる場合、控え室から みらくらぱーく！ のカードを1枚手札へ
    # 注意: Prompt 77（ライブ開始時+2ブレード）は既存実装。壊さない。
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Prompt 80: PL!HS-bp2-018 安養寺姫芽 (登場)
    # MAIN 中に [E][E] を任意支払い → green の LIVE を表向きで set_zone に置き、
    # 次の LIVE_SET で手札から置ける上限を 1 減らす。
    # effect_template only; optional energy cost prompt は engine.py 側。
    return False
