# -*- coding: utf-8 -*-
# BUILD_TAG: green_search_required_heart_filter_genericize_20260424d
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

    if ext_key == "green_pick_filtered_to_hand":
        return _enqueue_green_pick_filtered_to_hand(gs, cards_db, rule, gd or {}, ctx)


    if ext_key == "green_pick_filtered_to_hand__resolve":
        chosen_cn = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_cn") or "").strip()
        src_label = str((ctx or {}).get("source_name") or "green_pick_filtered_to_hand")
        return _resolve_green_choice_to_hand(gs, chosen_cn, src_label)

    if ext_key == "body_pick_live_req_yellow_ge3_from_green":
        src = str((ctx or {}).get("source_cn") or "PL!-PR-003")
        return _enqueue_pick_live_req_heart_from_green(gs, cards_db, 'yellow', 3, src)

    if ext_key == "body_pick_live_req_pink_ge3_from_green":
        src = str((ctx or {}).get("source_cn") or "PL!-PR-004")
        return _enqueue_pick_live_req_heart_from_green(gs, cards_db, 'pink', 3, src)

    return False
