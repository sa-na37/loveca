# -*- coding: utf-8 -*-
# BUILD_TAG: topdeck_filtered_optional_pick_genericize_20260424a
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

    # topk filtered optional pick family
    if ext_key == 'topk_filtered_optional_pick':
        merged_gd = dict(gd or {})
        try:
            topk = int(str(merged_gd.get('topk') or '5').strip())
        except Exception:
            topk = 5
        filter_kind = str(merged_gd.get('filter_kind') or 'MEMBER').strip().upper() or 'MEMBER'
        optional = str(merged_gd.get('optional') or '1').strip().lower() not in ('0', 'false', 'no', 'off')
        label = str(merged_gd.get('source_name') or 'topk filtered optional pick')
        fn = eng.get('_enqueue_choose_from_topk_filtered')
        if callable(fn):
            try:
                fn(gs, topk, rng, cards_db, filter_kind=filter_kind, optional=optional)
                gs.log.append(f"[AUTO_EXT] {label}: enqueue choose_from_top{topk} filter_kind={filter_kind} optional={optional}")
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
