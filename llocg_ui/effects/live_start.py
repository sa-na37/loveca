# -*- coding: utf-8 -*-
# BUILD_TAG: live_start_wait_and_same_name_helper_cleanup_20260423b
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


def _queue_choose_heart_color(
    gs: Any,
    *,
    pos: str,
    source_cn: str,
    options: list[str],
    text: str,
    log_line: str,
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
    _append_pending(gs, payload, log_line)



def _ctx_choice_pos(ctx: Dict[str, Any]) -> str:
    return str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()


def _activate_slot(slot: Any) -> None:
    if slot is not None:
        try:
            slot.active = True
        except Exception:
            pass


def _queue_other_wait_member_choice(
    gs: Any,
    *,
    candidates: list[str],
    source_cn: str,
    src_pos: str,
    log_line: str,
) -> None:
    _queue_choose_stage_member(
        gs,
        candidates=candidates,
        after_ext_key="live_start_activate_other_wait_member_both_green1__resolve",
        source_cn=source_cn,
        label="【エマ・ヴェルデ】アクティブにするメンバーを選んでください",
        text="【エマ・ヴェルデ】アクティブにするメンバーをクリックしてください",
        extra_payload={"ctx": {"src_pos": src_pos, "source_cn": source_cn}},
        log_line=log_line,
    )


def _apply_activate_other_wait_member_both_green1(eng: Dict[str, Any], gs: Any, *, src_pos: str, chosen_pos: str) -> bool:
    st = getattr(gs, "stage", None)
    if not isinstance(st, dict):
        return True
    src_slot = st.get(str(src_pos or "").upper())
    dst_slot = st.get(str(chosen_pos or "").upper())
    if dst_slot is None:
        try:
            gs.log.append(f"[ERR] Emma bp3-008 resolve: empty target {chosen_pos}")
        except Exception:
            pass
        return True
    _activate_slot(dst_slot)
    _apply_temp_bonus(eng, src_slot, hearts={"green": 1})
    _apply_temp_bonus(eng, dst_slot, hearts={"green": 1})
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
        src = _ctx_source_cn(ctx)
        if not occupied:
            try:
                gs.log.append("[AUTO_EXT] no stage members, no blade (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        if len(occupied) == 1:
            pos, slot = occupied[0]
            _apply_temp_bonus(eng, slot, blade=3)
            try:
                gs.log.append(f"[AUTO_EXT] only 1 member -> +3blade to {pos} (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        _queue_choose_stage_member(
            gs,
            candidates=[pos for pos, _ in occupied],
            after_ext_key="live_start_pick_stage_member_blade3__resolve",
            source_cn=src,
            label="【Oh,Love&Peace!】ブレード+3を与えるメンバーを選んでください",
            log_line=f"[PENDING] Oh,Love&Peace!: choose member for +3blade from {[pos for pos, _ in occupied]}",
        )
        return True

    if ext_key == "live_start_pick_stage_member_blade3__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        slot = _stage_slot_at(gs, chosen_pos)
        if slot is not None:
            _apply_temp_bonus(eng, slot, blade=3)
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
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append("[AUTO_EXT] no other members on stage (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        if len(others) == 1:
            pos, slot = others[0]
            _apply_temp_bonus(eng, slot, hearts={"pink": 1})
            try:
                gs.log.append(f"[AUTO_EXT] +pink to {pos} (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        _queue_choose_stage_member(
            gs,
            candidates=[pos for pos, _ in others],
            after_ext_key="live_start_pick_other_stage_member_pink1__resolve",
            source_cn=src,
            label="【園田海未】桃ハート+1を与えるメンバーを選んでください（このメンバー以外）",
            log_line=f"[PENDING] 園田海未 bp4-013: choose other member for +pink from {[pos for pos, _ in others]}",
        )
        return True

    if ext_key == "live_start_pick_other_stage_member_pink1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        slot = _stage_slot_at(gs, chosen_pos)
        if slot is not None:
            _apply_temp_bonus(eng, slot, hearts={"pink": 1})
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
        center_slot = _stage_slot_at(gs, "C")
        if center_slot is not None and bool(getattr(center_slot, "cardnumber", None)):
            if _card_group(center_slot, cards_db) == "μ's":
                _apply_temp_bonus(eng, center_slot, blade=1)
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
    # Prompt 37: PL!-bp4-024 小夜啼鳥恋詩 (ライブ開始時)
    # ステージの μ's メンバー1人（選択）に +1ブレード


    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_mus_stage_member_blade1":
        mus_members = _stage_positions_with_group(gs, cards_db, "μ's")
        src = _ctx_source_cn(ctx)
        if not mus_members:
            try:
                gs.log.append("[AUTO_EXT] no μ's on stage (小夜啼鳥恋詩)")
            except Exception:
                pass
            return True
        _queue_choose_stage_member(
            gs,
            candidates=[pos for pos, _ in mus_members],
            after_ext_key="live_start_pick_mus_stage_member_blade1__resolve",
            source_cn=src,
            label="【小夜啼鳥恋詩】ブレード+1を与えるμ'sメンバーを選んでください",
            log_line=f"[PENDING] 小夜啼鳥恋詩: choose μ's member for +blade from {[pos for pos, _ in mus_members]}",
        )
        return True

    if ext_key == "live_start_pick_mus_stage_member_blade1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        slot = _stage_slot_at(gs, chosen_pos)
        if slot is not None:
            _apply_temp_bonus(eng, slot, blade=1)
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
        src_pos = _ctx_src_pos(ctx)
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append("[AUTO_EXT] no other members on stage (高坂穂乃果 pb1-010)")
            except Exception:
                pass
            return True
        for _, slot in others:
            _apply_temp_bonus(eng, slot, blade=1)
        try:
            gs.log.append(f"[AUTO_EXT] +1blade to {[p for p, _ in others]} (高坂穂乃果 pb1-010)")
        except Exception:
            pass
        return True

    if ext_key == "live_start_discard_member_same_name_green1_blade1":
        src = _ctx_source_cn(ctx)
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

        discarded_type = _card_type_norm(discarded_cn, cards_db)
        if discarded_type != "MEMBER":
            try:
                gs.log.append(f"[AUTO_EXT] discarded {discarded_cn} is not MEMBER (type={discarded_type}), no effect (百生吟子)")
            except Exception:
                pass
            return True

        discarded_name = _card_display_name_with_fallback(eng, cards_db, discarded_cn)
        if not discarded_name:
            try:
                gs.log.append(f"[AUTO_EXT] name fallback by cardnumber for {discarded_cn} (百生吟子)")
            except Exception:
                pass

        matched = _matching_stage_members_for_discarded(eng, gs, cards_db, discarded_cn, discarded_name)
        if not matched:
            try:
                gs.log.append(f"[AUTO_EXT] no stage member named '{discarded_name}', no effect (百生吟子)")
            except Exception:
                pass
            return True

        if len(matched) == 1:
            pos, slot = matched[0]
            _apply_temp_bonus(eng, slot, blade=1, hearts={"green": 1})
            try:
                gs.log.append(f"[AUTO_EXT] discarded MEMBER '{discarded_name}' -> +green+blade to {pos} (百生吟子)")
            except Exception:
                pass
            return True

        _queue_choose_stage_member(
            gs,
            candidates=[pos for pos, _ in matched],
            after_ext_key="live_start_discard_member_same_name_green1_blade1__resolve",
            source_cn=src,
            label=f"【百生吟子】{discarded_name}と同名のメンバーを選んでください",
            extra_payload={"discarded_name": discarded_name},
            log_line=f"[PENDING] 百生吟子: choose same-name member from {[pos for pos, _ in matched]}",
        )
        return True

    if ext_key == "live_start_discard_member_same_name_green1_blade1__resolve":
        chosen_pos = _ctx_choice_pos(ctx)
        slot = _stage_slot_at(gs, chosen_pos)
        if slot is not None:
            _apply_temp_bonus(eng, slot, blade=1, hearts={"green": 1})
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
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        if not _stage_has_any_other_member(gs, exclude_pos=src_pos):
            try:
                gs.log.append("[AUTO_EXT] no other member on stage, no effect (藤島慈)")
            except Exception:
                pass
            return True
        _queue_choose_heart_color(
            gs,
            pos=src_pos,
            source_cn=src,
            options=["桃", "赤", "黄", "緑", "青", "紫"],
            text=f"{src}: 好きなハートの色を1つ指定する → ライブ終了時まで+1",
            log_line="[PENDING] 藤島慈: choose heart color (self)",
        )
        return True

    # ------------------------------------------------------------------
    # Prompt 14: PL!-bp3-003 南ことり (登場)
    # cost=このメンバーをウェイトにしてもよい → engine 側 self_wait pay_or_skip
    # 控え室から μ's のメンバーカードを1枚手札に加える
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Generalized from engine special-case: PL!N-bp3-008 エマ・ヴェルデ (ライブ開始時)
    # 手札を2枚控え室に置いてもよい：
    # このメンバー以外のウェイト状態のメンバー1人をアクティブにする。
    # そうした場合、そのメンバーとこのメンバーはそれぞれ緑+1（ライブ終了時まで）
    # ------------------------------------------------------------------
    if ext_key == "live_start_activate_other_wait_member_both_green1":
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return True
        cands = []
        for pos, slot in st.items():
            p = str(pos or "").upper()
            if p not in ("L", "C", "R") or p == src_pos:
                continue
            if slot is None or bool(getattr(slot, "active", False)):
                continue
            info = _lookup_cardinfo(cards_db, getattr(slot, "cardnumber", "") or "")
            ctype = ""
            try:
                ctype = str(getattr(info, "card_type", None) or (info if isinstance(info, dict) else {}).get("card_type") or "").upper()
            except Exception:
                ctype = ""
            if ctype == "LIVE":
                continue
            cands.append(p)
        if not cands:
            try:
                gs.log.append("[AUTO_EXT] Emma bp3-008: no other WAIT members")
            except Exception:
                pass
            return True
        if len(cands) == 1:
            chosen = cands[0]
            _apply_activate_other_wait_member_both_green1(eng, gs, src_pos=src_pos, chosen_pos=chosen)
            try:
                gs.log.append(f"[AUTO_EXT] Emma bp3-008: {chosen} ACTIVE; {src_pos} and {chosen} gain green +1")
            except Exception:
                pass
            return True
        _queue_other_wait_member_choice(
            gs,
            candidates=list(cands),
            source_cn=src,
            src_pos=src_pos,
            log_line=f"[PENDING] Emma bp3-008: choose WAIT member to activate from {cands}",
        )
        return True

    if ext_key == "live_start_activate_other_wait_member_both_green1__resolve":
        src_pos = str((ctx or {}).get("src_pos") or "").upper()
        chosen = _ctx_choice_pos(ctx)
        _apply_activate_other_wait_member_both_green1(eng, gs, src_pos=src_pos, chosen_pos=chosen)
        try:
            gs.log.append(f"[AUTO_EXT] Emma bp3-008 resolve: {chosen} ACTIVE; {src_pos} and {chosen} gain green +1")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Generalized from engine special-case: PL!N-bp1-003 桜坂しずく (ライブ開始時)
    # cost=<(E)> は engine 側 live_start_pay_effect
    # 好きなハート色を1つ指定する。ライブ終了時まで、そのハートを1つ得る。
    # ------------------------------------------------------------------
    if ext_key == "live_start_choose_any_heart":
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        _queue_choose_heart_color(
            gs,
            pos=src_pos,
            source_cn=src,
            options=["桃", "赤", "黄", "緑", "青", "紫"],
            text=f"{src}: 好きなハートの色を1つ指定する → ライブ終了時まで+1",
            log_line="[PENDING] 桜坂しずく bp1-003: choose any heart color",
        )
        return True

    # ------------------------------------------------------------------
    # Prompt 60: PL!-sd1-003 南ことり (ライブ開始時)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 桃/黄/紫 のうち1つ選んでライブ終了時まで得る

    # ------------------------------------------------------------------
    if ext_key == "live_start_choose_pinkYellowPurple_heart":
        src_pos = _ctx_src_pos(ctx)
        src = _ctx_source_cn(ctx)
        _queue_choose_heart_color(
            gs,
            pos=src_pos,
            source_cn=src,
            options=["桃", "黄", "紫"],
            text=f"{src}: 桃/黄/紫から1つ選ぶ → ライブ終了時まで+1",
            log_line="[PENDING] 南ことり sd1-003: choose pink/yellow/purple heart",
        )
        return True

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
