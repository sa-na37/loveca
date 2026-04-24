# -*- coding: utf-8 -*-
# BUILD_TAG: green_search_filtered_multi_pick_genericize_20260424f
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




def _rule_gd(rule: Dict[str, Any], gd: Dict[str, Any] | None = None) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    base_gd = (rule or {}).get('gd')
    if isinstance(base_gd, dict):
        merged.update(base_gd)
    if isinstance(gd, dict):
        merged.update(gd)
    return merged


def _gd_bool(rule: Dict[str, Any], key: str, default: bool = False, gd: Dict[str, Any] | None = None) -> bool:
    raw = str(_rule_gd(rule, gd).get(key) or ('1' if default else '0')).strip().lower()
    return raw in ('1', 'true', 'yes', 'on')


def _gd_int(rule: Dict[str, Any], key: str, default: int = 0, gd: Dict[str, Any] | None = None) -> int:
    try:
        return int(str(_rule_gd(rule, gd).get(key) or default).strip())
    except Exception:
        return int(default)


def _green_room_filtered_cards(
    gs: Any,
    cards_db: Dict[str, Any],
    *,
    want_kind: str = '',
    want_group: str = '',
    cost_max: int | None = None,
    score_max: int | None = None,
    req_heart_color: str = '',
    req_heart_min: int | None = None,
) -> list:
    kind = str(want_kind or '').strip().upper()
    group = str(want_group or '').strip()
    req_color = str(req_heart_color or '').strip().lower()
    out = []
    for card in _green_room_list(gs):
        try:
            if kind and _card_type_norm(card, cards_db) != kind:
                continue
            if group and not _label_matches_group_or_unit(card, cards_db, group):
                continue
            if cost_max is not None and _card_cost(card, cards_db) > int(cost_max):
                continue
            if score_max is not None and _card_score(card, cards_db) > int(score_max):
                continue
            if req_color and req_heart_min is not None:
                req = _card_required_hearts(card, cards_db)
                if int(req.get(req_color, 0) or 0) < int(req_heart_min):
                    continue
            out.append(card)
        except Exception:
            pass
    return out


def _stage_has_any_other_member_ctx(gs: Any, source_cn: str = '', exclude_pos: str = '') -> bool:
    try:
        st = getattr(gs, 'stage', None)
        if not isinstance(st, dict):
            return False
        skipped_self = False
        source_cn = str(source_cn or '').strip()
        for pos in ('L', 'C', 'R'):
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, 'cardnumber', None)):
                continue
            if exclude_pos and pos == exclude_pos:
                continue
            cn = str(getattr(slot, 'cardnumber', None) or '').strip()
            if source_cn and not exclude_pos and not skipped_self and cn == source_cn:
                skipped_self = True
                continue
            return True
    except Exception:
        pass
    return False


def _enqueue_green_pick_filtered_to_hand(
    gs: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, Any],
    ctx: Dict[str, Any],
) -> bool:
    gd = _rule_gd(rule, gd)
    src = str((ctx or {}).get('source_cn') or '')
    src_pos = str((ctx or {}).get('src_pos') or (ctx or {}).get('pos') or '').upper()
    source_name = str(gd.get('source_name') or src or 'カード')
    want_kind = str(gd.get('want_kind') or '').strip().upper()
    want_group = str(gd.get('want_group') or '').strip()
    score_max = gd.get('score_max')
    try:
        score_max = int(str(score_max).strip()) if str(score_max).strip() else None
    except Exception:
        score_max = None
    req_heart_color = str(gd.get('req_heart_color') or '').strip().lower()
    req_heart_min = gd.get('req_heart_min')
    try:
        req_heart_min = int(str(req_heart_min).strip()) if str(req_heart_min).strip() else None
    except Exception:
        req_heart_min = None

    detail_text = str((ctx or {}).get('detail_text') or (ctx or {}).get('effect_text') or gd.get('detail_text') or '')

    if _gd_bool(rule, 'require_success_zone', False, gd) and not _success_zone_cards(gs):
        msg = str(gd.get('no_effect_popup_text') or '成功ライブカード置き場にカードがないため、この効果は解決されませんでした。')
        try:
            gs.log.append(str(gd.get('no_effect_log') or f'[AUTO_EXT] success_zone empty, no effect ({source_name})'))
        except Exception:
            pass
        _append_ack_confirm(gs, src, msg, detail_text or msg)
        return True

    if _gd_bool(rule, 'require_other_member', False, gd) and not _stage_has_any_other_member_ctx(gs, source_cn=src, exclude_pos=src_pos):
        msg = str(gd.get('no_effect_popup_text') or 'ほかのメンバーがいないため、この効果は解決されませんでした。')
        try:
            gs.log.append(str(gd.get('no_effect_log') or f'[AUTO_EXT] no other member on stage ({source_name})'))
        except Exception:
            pass
        _append_ack_confirm(gs, src, msg, detail_text or msg)
        return True

    diff_unit = str(gd.get('require_unit_diff_names_label') or '').strip()
    diff_n = _gd_int(rule, 'require_unit_diff_names_ge', 0, gd)
    if diff_unit and diff_n > 0:
        diff_count = _stage_unit_count_diff_names(gs, cards_db, diff_unit)
        if diff_count < diff_n:
            msg = str(gd.get('no_effect_popup_text') or f'{diff_unit}の名前の異なるメンバーが{diff_n}人以上いないため、この効果は解決されませんでした。')
            try:
                gs.log.append(str(gd.get('no_effect_log') or f'[AUTO_EXT] {diff_unit} diff_names={diff_count}<{diff_n}, no effect ({source_name})'))
            except Exception:
                pass
            _append_ack_confirm(gs, src, msg, detail_text or msg)
            return True

    candidates = _green_room_filtered_cards(
        gs,
        cards_db,
        want_kind=want_kind,
        want_group=want_group,
        cost_max=None,
        score_max=score_max,
        req_heart_color=req_heart_color,
        req_heart_min=req_heart_min,
    )
    if not candidates:
        kind_txt = want_kind or 'CARD'
        group_txt = want_group or 'any'
        extra = f' score<={score_max}' if score_max is not None else ''
        if req_heart_color and req_heart_min is not None:
            extra += f' req[{req_heart_color}]>={req_heart_min}'
        msg = str(gd.get('no_candidates_popup_text') or '条件を満たすカードが控え室にないため、この効果は解決されませんでした。')
        try:
            gs.log.append(str(gd.get('no_candidates_log') or f'[AUTO_EXT] no {group_txt} {kind_txt}{extra} in green_room ({source_name})'))
        except Exception:
            pass
        _append_ack_confirm(gs, src, msg, detail_text or msg)
        return True

    label = str(gd.get('pending_label') or f'【{source_name}】控え室からカードを1枚選んでください')
    _enqueue_choose_card_from_green_pending(
        gs,
        candidates=candidates,
        source_cn=src,
        source_name=source_name,
        after_ext_key='green_pick_filtered_to_hand__resolve',
        label=label,
        detail_text=detail_text,
        optional=False,
        allow_skip=False,
        ctx={'source_name': source_name, 'detail_text': detail_text},
    )
    return True



def _enqueue_green_pick_filtered_to_hand_multi(
    gs: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, Any],
    ctx: Dict[str, Any],
) -> bool:
    gd = _rule_gd(rule, gd)
    src = str((ctx or {}).get('source_cn') or '')
    src_pos = str((ctx or {}).get('src_pos') or (ctx or {}).get('pos') or '').upper()
    source_name = str(gd.get('source_name') or src or 'カード')
    want_kind = str(gd.get('want_kind') or '').strip().upper()
    want_group = str(gd.get('want_group') or '').strip()
    cost_max = gd.get('cost_max')
    try:
        cost_max = int(str(cost_max).strip()) if str(cost_max).strip() else None
    except Exception:
        cost_max = None
    score_max = gd.get('score_max')
    try:
        score_max = int(str(score_max).strip()) if str(score_max).strip() else None
    except Exception:
        score_max = None
    req_heart_color = str(gd.get('req_heart_color') or '').strip().lower()
    req_heart_min = gd.get('req_heart_min')
    try:
        req_heart_min = int(str(req_heart_min).strip()) if str(req_heart_min).strip() else None
    except Exception:
        req_heart_min = None
    min_picks = _gd_int(rule, 'min_picks', 0, gd)
    max_picks = max(_gd_int(rule, 'max_picks', 1, gd), 0)

    detail_text = str((ctx or {}).get('detail_text') or (ctx or {}).get('effect_text') or gd.get('detail_text') or '')

    if _gd_bool(rule, 'require_success_zone', False, gd) and not _success_zone_cards(gs):
        msg = str(gd.get('no_effect_popup_text') or '成功ライブカード置き場にカードがないため、この効果は解決されませんでした。')
        try:
            gs.log.append(str(gd.get('no_effect_log') or f'[AUTO_EXT] success_zone empty, no effect ({source_name})'))
        except Exception:
            pass
        _append_ack_confirm(gs, src, msg, detail_text or msg)
        return True

    if _gd_bool(rule, 'require_other_member', False, gd) and not _stage_has_any_other_member_ctx(gs, source_cn=src, exclude_pos=src_pos):
        msg = str(gd.get('no_effect_popup_text') or 'ほかのメンバーがいないため、この効果は解決されませんでした。')
        try:
            gs.log.append(str(gd.get('no_effect_log') or f'[AUTO_EXT] no other member on stage ({source_name})'))
        except Exception:
            pass
        _append_ack_confirm(gs, src, msg, detail_text or msg)
        return True

    diff_unit = str(gd.get('require_unit_diff_names_label') or '').strip()
    diff_n = _gd_int(rule, 'require_unit_diff_names_ge', 0, gd)
    if diff_unit and diff_n > 0:
        diff_count = _stage_unit_count_diff_names(gs, cards_db, diff_unit)
        if diff_count < diff_n:
            msg = str(gd.get('no_effect_popup_text') or f'{diff_unit}の名前の異なるメンバーが{diff_n}人以上いないため、この効果は解決されませんでした。')
            try:
                gs.log.append(str(gd.get('no_effect_log') or f'[AUTO_EXT] {diff_unit} diff_names={diff_count}<{diff_n}, no effect ({source_name})'))
            except Exception:
                pass
            _append_ack_confirm(gs, src, msg, detail_text or msg)
            return True

    candidates = _green_room_filtered_cards(
        gs,
        cards_db,
        want_kind=want_kind,
        want_group=want_group,
        cost_max=cost_max,
        score_max=score_max,
        req_heart_color=req_heart_color,
        req_heart_min=req_heart_min,
    )
    if not candidates:
        kind_txt = want_kind or 'CARD'
        group_txt = want_group or 'any'
        extra = f' cost<={cost_max}' if cost_max is not None else ''
        if score_max is not None:
            extra += f' score<={score_max}'
        if req_heart_color and req_heart_min is not None:
            extra += f' req[{req_heart_color}]>={req_heart_min}'
        msg = str(gd.get('no_candidates_popup_text') or '条件を満たすカードが控え室にないため、この効果は解決されませんでした。')
        try:
            gs.log.append(str(gd.get('no_candidates_log') or f'[AUTO_EXT] no {group_txt} {kind_txt}{extra} in green_room ({source_name})'))
        except Exception:
            pass
        _append_ack_confirm(gs, src, msg, detail_text or msg)
        return True

    cns = [str(getattr(c, 'cardnumber', None) or c or '') for c in candidates]
    label = str(gd.get('pending_label') or f'【{source_name}】控え室からカードを0〜{max_picks}枚選んでください')
    payload = {
        'kind': 'choose_member_from_green_multi_up_to',
        'text': label,
        'options': cns,
        'min_picks': min_picks,
        'max_picks': min(max_picks, len(cns)),
        'want_kind': want_kind,
        'source_cn': src,
        'source_name': source_name,
        'detail_text': detail_text,
        'current_text': detail_text,
    }
    try:
        getattr(gs, 'pending').append(payload)
        gs.log.append(f"[PENDING] {source_name}: green multi-pick opts={cns} min={min_picks} max={payload['max_picks']}")
    except Exception:
        pass
    return True


def try_apply_green_search_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, Any] | None = None,
    ctx: Dict[str, Any] | None = None,
) -> bool:
    ctx = ctx or {}
    ext_key = str((rule or {}).get('ext_key') or '').strip()

    if ext_key == "green_pick_filtered_to_hand_multi":
        return _enqueue_green_pick_filtered_to_hand_multi(gs, cards_db, rule, gd or {}, ctx)

    if ext_key == "green_pick_filtered_to_hand":
        return _enqueue_green_pick_filtered_to_hand(gs, cards_db, rule, gd or {}, ctx)


    if ext_key == "green_pick_filtered_to_hand__resolve":
        chosen_cn = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_cn") or "").strip()
        src_label = str((ctx or {}).get("source_name") or "green_pick_filtered_to_hand")
        return _resolve_green_choice_to_hand(gs, chosen_cn, src_label)

    return False
