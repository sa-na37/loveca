# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_special_20260413l
from __future__ import annotations

"""llocg_ui.effects.special

まだ一般化しきれていない特例寄り ext apply の正本。
現段階では姫芽系の set_zone / face-up live preload / next live set cost reduction をここへ置く。
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def try_apply_special_ext(
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
    if ext_key == "enter_main_pay2_faceup_live_to_set_reduce_next_live_set":
        src = str((ctx or {}).get("source_cn") or "安養寺姫芽")
        phase = str(getattr(gs, "phase", "") or "").upper()
        if phase != 'MAIN':
            try:
                gs.log.append(f"[AUTO_EXT] not MAIN, no effect ({src})")
            except Exception:
                pass
            return True

        chosen_cn = str((ctx or {}).get("chosen_cn") or (ctx or {}).get("choice") or "").strip()
        if chosen_cn:
            ok = _move_live_from_green_to_set_zone(gs, chosen_cn)
            try:
                gs.log.append(f"[AUTO_EXT] green->set_zone {chosen_cn} ({src}) ok={ok}")
            except Exception:
                pass
            if ok:
                _reserve_next_live_set_limit_delta(gs, -1, src)
            return True

        candidates = [c for c in _green_room_list(gs) if _card_type_norm(c, cards_db) == 'LIVE']
        try:
            gs.log.append(f"[AUTO_EXT] {src}: green LIVE candidates={len(candidates)}")
        except Exception:
            pass
        if not candidates:
            try:
                gs.log.append(f"[AUTO_EXT] no LIVE in green_room ({src})")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            ok = _move_live_from_green_to_set_zone(gs, candidates[0])
            try:
                gs.log.append(f"[AUTO_EXT] green->set_zone {cn_str} ({src}) ok={ok}")
            except Exception:
                pass
            if ok:
                _reserve_next_live_set_limit_delta(gs, -1, src)
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_live_from_green",
            "text": "控え室のライブカードを1枚選び、表向きでライブカード置き場に置く",
            "options": cns,
            "want_kind": "LIVE",
            "remaining_picks": 1,
            "after_ext_key": "enter_main_pay2_faceup_live_to_set_reduce_next_live_set",
            "ctx": dict(ctx or {}),
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] {src}: choose LIVE from green for set_zone {cns}")
        except Exception:
            pass
        return True

    return False
