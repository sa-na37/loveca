# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_topdeck_20260413d
from __future__ import annotations

"""llocg_ui.effects.topdeck

山札上から扱う系の ext apply を分離した正本。
- reorder_from_top{k}
- choose_from_top5 filtered optional
- mill 10 / mill 5
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

    # PL!HS-bp2-003 / PL!HS-bp2-016
    if ext_key in ('reorder_from_top3', 'reorder_from_top2'):
        k = 3 if ext_key == 'reorder_from_top3' else 2
        fn = eng.get('_enqueue_reorder_from_topk_keep_any')
        label = '乙宗梢 bp2-003' if k == 3 else '百生吟子 bp2-016'
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

    if ext_key == "enter_mill5":
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
                for _ in range(5):
                    if not deck:
                        break
                    waiting.append(deck.pop(0))
                    milled += 1
        except Exception:
            pass
        try:
            gs.log.append(f"[AUTO_EXT] mill {milled}/5 cards to waiting_room (村野さやか bp2-011)")
        except Exception:
            pass
        return True

    return False
