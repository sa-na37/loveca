# -*- coding: utf-8 -*-
# BUILD_TAG: topdeck_public_reveal_pool_20260723a
from __future__ import annotations

"""llocg_ui.effects.topdeck

山札上から扱う系の ext apply を分離した正本。
- reorder_from_top{k}
- choose_from_top5 filtered optional
- mill top{k} -> green_room
- look top{k}, choose 1 to hand, rest to green
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403




def _topdeck_modal_common(gd: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Common payload for effect-resolution modals.

    Topdeck extension effects must not create a bespoke card picker that loses
    source/effect context.  Every pending created here carries source_cn and the
    currently resolving effect text so the shared modal lead/card-text panels are
    rendered by server.py.
    """
    gd = gd or {}
    ctx = ctx or {}
    src = str(ctx.get('source_cn') or gd.get('source_cn') or '').strip()
    detail = str(
        ctx.get('detail_text')
        or ctx.get('effect_text')
        or gd.get('detail_text')
        or gd.get('effect_text')
        or ''
    ).strip()
    if not detail:
        auto_detail = str(ctx.get('auto_effect_detail') or '').strip()
        if '効果：' in auto_detail:
            detail = auto_detail.split('効果：', 1)[1].strip()
        elif auto_detail:
            detail = auto_detail
    trigger = str(ctx.get('trigger') or ctx.get('timing') or gd.get('trigger') or gd.get('timing') or '').strip()
    if not trigger:
        auto_detail = str(ctx.get('auto_effect_detail') or '')
        if '登場' in auto_detail:
            trigger = '登場時'
        elif 'ライブ開始' in auto_detail:
            trigger = 'ライブ開始時'
        elif 'ライブ成功' in auto_detail:
            trigger = 'ライブ成功時'
    payload: Dict[str, Any] = {'ctx': dict(ctx)}
    if src:
        payload['source_cn'] = src
        payload['ctx'].setdefault('source_cn', src)
    if detail:
        payload['detail_text'] = detail
        payload['effect_text'] = detail
        payload['ctx'].setdefault('detail_text', detail)
        payload['ctx'].setdefault('effect_text', detail)
    if trigger:
        payload['trigger'] = trigger
        payload['ctx'].setdefault('trigger', trigger)
    return payload


def try_apply_topdeck_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, str],
    ctx: Dict[str, Any],
    ext_key: str,
 ) -> bool:
    common_modal = _topdeck_modal_common(gd, ctx)

    # mill top{k} -> green_room
    if ext_key == "mill_topk_to_green":
        try:
            k = int(gd.get('topk') or 0)
        except Exception:
            k = 0
        if k <= 0:
            k = 5
        label = gd.get('source_name') or f'top{k} mill'
        milled = 0
        try:
            deck = getattr(gs, 'deck', None)
            waiting = getattr(gs, 'green_room', None)
            if waiting is None:
                waiting = (
                    getattr(gs, 'waiting_room', None)
                    or getattr(gs, 'graveyard', None)
                    or getattr(gs, 'discard', None)
                )
            if deck is not None and waiting is not None:
                for _ in range(k):
                    if not deck:
                        break
                    waiting.append(deck.pop(0))
                    milled += 1
            gs.log.append(f"[AUTO_EXT] {label}: milled {milled}/{k} to waiting_room")
        except Exception as e:
            try:
                gs.log.append(f"[ERR] {label}: mill_topk_to_green failed: {e}")
            except Exception:
                pass
        return True


    # look top{k}, choose N to hand, rest to green (generic non-public reveal path)
    # BUILD_TAG: topdeck_generic_choose_n_to_hand_rest_green_20260629aa
    if ext_key == 'topk_choose_n_to_hand_rest_green':
        try:
            k = int(gd.get('topk') or 0)
        except Exception:
            k = 0
        try:
            pick_n = int(gd.get('pick_count') or gd.get('pick_n') or 1)
        except Exception:
            pick_n = 1
        try:
            min_pick = int(gd.get('min_pick_count') or pick_n)
        except Exception:
            min_pick = pick_n
        try:
            max_pick = int(gd.get('max_pick_count') or pick_n)
        except Exception:
            max_pick = pick_n
        if k <= 0:
            k = max(1, pick_n)
        if pick_n <= 0:
            pick_n = 1
        label = gd.get('source_name') or f'top{k} choose{pick_n}'
        try:
            refresh = eng.get('_rule_refresh_for_top_access')
            if callable(refresh):
                refresh(gs, rng, k, reason='look_top_choose_n_rest_green')
            deck = getattr(gs, 'deck', None)
            if not deck:
                gs.log.append(f'[INFO] {label}: deck empty')
                return True
            pool = []
            for _ in range(min(k, len(deck))):
                pool.append(deck.pop(0))
            if not pool:
                gs.log.append(f'[INFO] {label}: no cards after refresh')
                return True
            detail_text = str(ctx.get('detail_text') or ctx.get('effect_text') or gd.get('effect_text') or common_modal.get('detail_text') or '')
            # Even when the pool is small, keep the shared effect popup route.
            # One-candidate effects still need source/effect context and user confirmation.
            optional_raw = str(gd.get('optional') or '0').strip().lower()
            optional = optional_raw in ('1', 'true', 'yes', 'on')
            opts = list(pool)
            if optional and min_pick <= 0:
                opts = list(pool) + ['done', 'skip']
            pending = {
                **common_modal,
                'kind': 'choose_from_topk',
                'text': str(gd.get('pending_label') or f'デッキ上から{len(pool)}枚を見る：その中から{min_pick if min_pick == max_pick else str(min_pick)+"〜"+str(max_pick)}枚を手札に加え、残りを控え室に置く'),
                'options': opts,
                'pool': list(pool),
                'display_cards': list(pool),
                'candidates': list(pool),
                'optional': optional,
                'pick_count': max_pick,
                'min_pick_count': min_pick,
                'max_pick_count': max_pick,
            }
            if detail_text:
                pending['detail_text'] = detail_text
                pending['effect_text'] = detail_text
            gs.pending.append(pending)
            gs.log.append(f"[AUTO_EXT] {label}: inline choose_from_top{len(pool)} pick {min_pick}..{max_pick} pending")
        except Exception as e:
            try:
                gs.log.append(f"[ERR] {label}: inline topk_choose_n_to_hand_rest_green failed: {e}")
            except Exception:
                pass
        return True

    # look top{k}, choose 1 to hand, rest to green
    if ext_key == 'topk_choose_one_to_hand_rest_green':
        try:
            k = int(gd.get('topk') or 0)
        except Exception:
            k = 0
        if k <= 0:
            k = 3
        label = gd.get('source_name') or f'top{k} choose1'
        try:
            refresh = eng.get('_rule_refresh_for_top_access')
            if callable(refresh):
                refresh(gs, rng, k, reason='look_top_choose_one_rest_green')
            deck = getattr(gs, 'deck', None)
            if not deck:
                gs.log.append(f'[INFO] {label}: deck empty')
                return True
            pool = []
            for _ in range(min(k, len(deck))):
                pool.append(deck.pop(0))
            if not pool:
                gs.log.append(f'[INFO] {label}: no cards after refresh')
                return True
            # One-candidate effects still use the shared popup route.
            detail_text = str(ctx.get('detail_text') or ctx.get('effect_text') or gd.get('detail_text') or gd.get('effect_text') or common_modal.get('detail_text') or '')
            pending = {
                **common_modal,
                'kind': 'choose_from_topk',
                'text': f'デッキ上から{len(pool)}枚を見る：その中から1枚を手札に加え、残りを控え室に置く',
                'options': list(pool),
                'pool': list(pool),
                'display_cards': list(pool),
                'candidates': list(pool),
                'optional': False,
            }
            if detail_text:
                pending['detail_text'] = detail_text
                pending['effect_text'] = detail_text
            gs.pending.append(pending)
            gs.log.append(f"[AUTO_EXT] {label}: inline choose_from_top{len(pool)} pending")
        except Exception as e:
            try:
                gs.log.append(f"[ERR] {label}: inline topk_choose_one_to_hand_rest_green failed: {e}")
            except Exception:
                pass
        return True

    # look top{k}, choose 1 to hand, 1 to deck top, rest to green
    if ext_key == 'topk_split_one_hand_one_top_rest_green':
        try:
            k = int(gd.get('topk') or 0)
        except Exception:
            k = 0
        if k <= 0:
            k = 3
        label = gd.get('source_name') or f'top{k} split1/1/rest'
        try:
            refresh = eng.get('_rule_refresh_for_top_access')
            if callable(refresh):
                refresh(gs, rng, k, reason='look_top_3way')
            if not getattr(gs, 'deck', None):
                try:
                    gs.log.append('[INFO] look_top_3way: deck empty')
                except Exception:
                    pass
                return True
            pool = [gs.deck.pop(0) for _ in range(min(k, len(gs.deck)))]
            detail_text = str(ctx.get('detail_text') or ctx.get('effect_text') or gd.get('detail_text') or gd.get('effect_text') or common_modal.get('detail_text') or '')
            pending = {
                **common_modal,
                'kind': 'look_top_3way_step',
                'text': f'手札に加えるカードを選ぶ（デッキ上{len(pool)}枚から1枚）',
                'options': list(pool),
                'pool': list(pool),
                'display_cards': list(pool),
                'step': 'hand',
                'picked_hand': '',
                'picked_top': '',
            }
            if detail_text:
                pending['detail_text'] = detail_text
                pending['effect_text'] = detail_text
            gs.pending.append(pending)
            try:
                gs.log.append(f"[AUTO_EXT] {label}: enqueue look_top_3way_split top{k} (legacy step UI + clearer labels)")
                gs.log.append(f'[PENDING] look_top_3way: pool={pool}')
            except Exception:
                pass
        except Exception as e:
            try:
                gs.log.append(f"[ERR] {label}: topk_split_one_hand_one_top_rest_green failed: {e}")
            except Exception:
                pass
        return True


    # reorder top{k} keep any
    if ext_key == 'reorder_from_topk':
        try:
            k = int(gd.get('topk') or 0)
        except Exception:
            k = 0
        if k <= 0:
            k = 3
        fn = eng.get('_enqueue_reorder_from_topk_keep_any')
        label = gd.get('source_name') or f'top{k} reorder'
        if callable(fn):
            try:
                fn(gs, k, rng, ctx=ctx)
                gs.log.append(f"[AUTO_EXT] {label}: enqueue reorder_from_top{k}")
            except Exception as e:
                try:
                    gs.log.append(f"[ERR] {label}: _enqueue_reorder_from_topk_keep_any failed: {e}")
                except Exception:
                    pass
        else:
            try:
                gs.log.append(f"[ERR] {label}: _enqueue_reorder_from_topk_keep_any not found")
            except Exception:
                pass
        return True

    # look top{k}, optionally pick 1 filtered card to hand, rest to green
    if ext_key in ('topk_filtered_optional_pick', 'enter_top5_member_optional_pick', 'body_stage_to_green_top5_member_optional', 'body_stage_to_green_top5_live_optional'):
        try:
            k = int(gd.get('topk') or 0)
        except Exception:
            k = 0
        if k <= 0:
            k = 5

        filter_kind = str(gd.get('filter_kind') or '').strip().upper()
        if not filter_kind and ext_key in (
            'enter_top5_member_optional_pick',
            'body_stage_to_green_top5_member_optional',
        ):
            filter_kind = 'MEMBER'
        elif not filter_kind and ext_key == 'body_stage_to_green_top5_live_optional':
            filter_kind = 'LIVE'
        if filter_kind in ('ANY', 'CARD', 'カード'):
            filter_kind = ''

        filter_group = str(gd.get('filter_group') or '').strip()
        raw_names = str(gd.get('filter_names') or '').strip()
        filter_names = [s.strip() for s in raw_names.split(',') if s.strip()]
        try:
            cost_min = int(gd.get('cost_min') or 0)
        except Exception:
            cost_min = 0
        try:
            cost_max = int(gd.get('cost_max') or 0)
        except Exception:
            cost_max = 0

        optional_raw = str(gd.get('optional') if gd.get('optional') is not None else '1').strip().lower()
        optional = optional_raw not in ('0', 'false', 'no', 'off')

        label = gd.get('source_name') or (
            '日野下花帆 bp2-010' if ext_key == 'enter_top5_member_optional_pick' else
            '乙宗梢 bp2-012' if ext_key == 'body_stage_to_green_top5_member_optional' else
            '夕霧綴理 bp2-013' if ext_key == 'body_stage_to_green_top5_live_optional' else
            f'top{k} filtered optional pick'
        )

        detail_text = str(ctx.get('detail_text') or ctx.get('effect_text') or gd.get('detail_text') or gd.get('effect_text') or common_modal.get('detail_text') or '')
        try:
            refresh = eng.get('_rule_refresh_for_top_access')
            if callable(refresh):
                refresh(gs, rng, k, reason='look_top_filtered')
            deck = getattr(gs, 'deck', None)
            if not deck:
                gs.log.append(f'[INFO] {label}: deck empty')
                return True
            pool = [deck.pop(0) for _ in range(min(k, len(deck)))]
            if not pool:
                gs.log.append(f'[INFO] {label}: no cards after refresh')
                return True

            # These helper names live in engine.py, not this extension module.
            # Resolve them from the `eng` globals passed into the extension so
            # stage->green/top-k effects do not depend on accidental module globals.
            get_card_fn = eng.get('_get_card')
            is_live_fn = eng.get('_is_live_ci') or eng.get('_is_live')
            is_member_fn = eng.get('_is_member_ci') or eng.get('_is_member')
            canon_fn = eng.get('_canon_cardno')

            def _card_from_db(cn: str):
                if callable(get_card_fn):
                    return get_card_fn(cards_db, cn)
                key = str(cn or '')
                if key in cards_db:
                    return cards_db.get(key)
                if callable(canon_fn):
                    key2 = canon_fn(key)
                    if key2 in cards_db:
                        return cards_db.get(key2)
                return None

            def _is_live_local(ci) -> bool:
                if callable(is_live_fn):
                    return bool(is_live_fn(ci))
                typ = str(getattr(ci, 'type', '') or getattr(ci, 'card_type', '') or '').upper()
                return 'LIVE' in typ or 'ライブ' in typ

            def _is_member_local(ci) -> bool:
                if callable(is_member_fn):
                    return bool(is_member_fn(ci))
                typ = str(getattr(ci, 'type', '') or getattr(ci, 'card_type', '') or '').upper()
                return 'MEMBER' in typ or 'メンバー' in typ

            def _matches(cn: str) -> bool:
                ci = _card_from_db(cn)
                if not ci:
                    return False
                if filter_kind == 'LIVE' and not _is_live_local(ci):
                    return False
                if filter_kind == 'MEMBER' and not _is_member_local(ci):
                    return False
                if filter_group:
                    group = str(getattr(ci, 'group', '') or '')
                    if filter_group not in group:
                        return False
                if filter_names:
                    name = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or cn)
                    if not any(n in name for n in filter_names):
                        return False
                if cost_min or cost_max:
                    try:
                        cost_val = int(getattr(ci, 'cost', 0) or 0)
                    except Exception:
                        cost_val = 0
                    if cost_min and cost_val < cost_min:
                        return False
                    if cost_max and cost_val > cost_max:
                        return False
                return True

            candidates = [cn for cn in pool if _matches(cn)]

            label_parts = []
            if cost_min and cost_max:
                label_parts.append(f'コスト{cost_min}〜{cost_max}')
            elif cost_min:
                label_parts.append(f'コスト{cost_min}以上')
            elif cost_max:
                label_parts.append(f'コスト{cost_max}以下')
            if filter_group:
                label_parts.append(f'『{filter_group}』')
            if filter_names:
                label_parts.append('か'.join(f'「{n}」' for n in filter_names))
            if filter_kind:
                label_parts.append({'LIVE': 'ライブカード', 'MEMBER': 'メンバーカード'}.get(filter_kind, filter_kind))
            label_text = ''.join(label_parts) if label_parts else 'カード'

            if not candidates:
                pending = {
                    **common_modal,
                    'kind': 'view_topk_no_match',
                    'text': f'デッキ上{len(pool)}枚を公開（{label_text}なし）→ 全て控え室へ',
                    'options': ['確認'],
                    'pool': list(pool),
                    'display_cards': list(pool),
                }
                if detail_text:
                    pending['detail_text'] = detail_text
                    pending['effect_text'] = detail_text
                gs.pending.append(pending)
                gs.log.append(f'[PENDING] {label}: no match in top{len(pool)}')
                return True

            opts = list(candidates)
            if optional:
                opts.append('skip')
            pending = {
                **common_modal,
                'kind': 'choose_from_topk',
                'text': f'デッキ上{len(pool)}枚から{label_text}を1枚公開して手札へ' + ('（スキップ可）' if optional else ''),
                'options': opts,
                'pool': list(pool),
                'display_cards': list(pool),
                'display_pool_all': list(pool),
                'public_reveal_pool': True,
                'candidates': list(candidates),
                'optional': optional,
            }
            if detail_text:
                pending['detail_text'] = detail_text
                pending['effect_text'] = detail_text
            gs.pending.append(pending)
            gs.log.append(f"[AUTO_EXT] {label}: enqueue choose_from_top{k} kind={filter_kind or '-'} group={filter_group or '-'} names={filter_names or '-'} cost_min={cost_min} cost_max={cost_max} optional={optional}")
        except Exception as e:
            try:
                gs.log.append(f"[ERR] {label}: topk_filtered_optional_pick failed: {e}")
            except Exception:
                pass
        return True


    return False
