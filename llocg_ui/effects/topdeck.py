# -*- coding: utf-8 -*-
# BUILD_TAG: topdeck_split_hand_top_green_genericize_20260424f
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
            if len(pool) == 1:
                pick = pool[0]
                gs.hand.append(pick)
                gs.log.append(f'[AUTO_EXT] {label}: only 1 -> hand {pick}')
                return True
            detail_text = str(ctx.get('detail_text') or ctx.get('effect_text') or '')
            gs.pending.append({
                'kind': 'choose_from_topk',
                'text': f'デッキ上から{len(pool)}枚を見る：その中から1枚を手札に加え、残りを控え室に置く',
                'options': list(pool),
                'pool': list(pool),
                'display_cards': list(pool),
                'candidates': list(pool),
                'optional': False,
                'detail_text': detail_text,
                'effect_text': detail_text,
            })
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
        fn = eng.get('_enqueue_look_top_3way_split')
        if callable(fn):
            try:
                fn(gs, k, rng)
                gs.log.append(f"[AUTO_EXT] {label}: enqueue look_top_3way_split top{k}")
            except Exception as e:
                try:
                    gs.log.append(f"[ERR] {label}: _enqueue_look_top_3way_split failed: {e}")
                except Exception:
                    pass
        else:
            try:
                gs.log.append(f"[ERR] {label}: _enqueue_look_top_3way_split not found")
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
                fn(gs, k, rng)
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

    # PL!HS-bp2-010 / 012 / 013 top5 filtered optional
    if ext_key in ('enter_top5_member_optional_pick', 'body_stage_to_green_top5_member_optional', 'body_stage_to_green_top5_live_optional'):
        filter_kind = 'LIVE' if ext_key == 'body_stage_to_green_top5_live_optional' else 'MEMBER'
        label = (
            '日野下花帆 bp2-010' if ext_key == 'enter_top5_member_optional_pick' else
            '乙宗梢 bp2-012' if ext_key == 'body_stage_to_green_top5_member_optional' else
            '夕霧綴理 bp2-013'
        )
        fn = eng.get('_enqueue_choose_from_topk_filtered')
        if callable(fn):
            try:
                fn(gs, 5, rng, cards_db, filter_kind=filter_kind, optional=True)
                gs.log.append(f"[AUTO_EXT] {label}: enqueue choose_from_top5 filter_kind={filter_kind} optional=True")
            except Exception as e:
                try:
                    gs.log.append(f"[ERR] {label}: _enqueue_choose_from_topk_filtered failed: {e}")
                except Exception:
                    pass
        else:
            try:
                gs.log.append(f"[ERR] {label}: _enqueue_choose_from_topk_filtered not found")
            except Exception:
                pass
        return True


    return False
