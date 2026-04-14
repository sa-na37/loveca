# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_position_20260413i
from __future__ import annotations

"""llocg_ui.effects.position

position_change と、配置条件に基づく position_change 誘発の ext apply 正本。
- generic position_change_optional
- Love wing bell
- PL!-bp4-005 星空凛
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def try_apply_position_ext(
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
    # 既存: position_change_optional
    # ------------------------------------------------------------------
    if ext_key == "position_change_optional":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        if src_pos not in ("L", "C", "R"):
            try:
                gs.log.append(f"[WARN] position_change_optional: invalid src_pos='{src_pos}'")
            except Exception:
                pass
            return True
        options = [p for p in ("L", "C", "R") if p != src_pos] + ["skip"]
        payload = {
            "kind": "position_change",
            "src_pos": src_pos,
            "optional": True,
            "options": options,
            "source_cn": str((ctx or {}).get("source_cn") or ""),
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] position_change src={src_pos}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 35: PL!-bp4-020 Love wing bell (ライブ開始時)
    # ステージが μ's のみ → ステージメンバー1人をポジションチェンジさせてもよい
    # ------------------------------------------------------------------
    if ext_key == "live_start_mus_only_pick_member_position_change":
        if not _stage_all_group(gs, cards_db, "μ's"):
            try:
                gs.log.append("[AUTO_EXT] stage not all μ's, skip (Love wing bell)")
            except Exception:
                pass
            return True
        occupied = _stage_positions_all_occupied(gs)
        src = str((ctx or {}).get("source_cn") or "")
        if not occupied:
            try:
                gs.log.append("[AUTO_EXT] no stage members, skip (Love wing bell)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in occupied]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates + ["skip"],
            "optional": True,
            "after_ext_key": "live_start_mus_only_pick_member_position_change__resolve",
            "source_cn": src,
            "label": "【Love wing bell】ポジションチェンジするメンバーを選んでください（スキップ可）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Love wing bell: choose member for position_change from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_mus_only_pick_member_position_change__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        if chosen_pos == "SKIP" or chosen_pos not in ("L", "C", "R"):
            try:
                gs.log.append("[AUTO_EXT] position_change skipped (Love wing bell)")
            except Exception:
                pass
            return True
        options = [p for p in ("L", "C", "R") if p != chosen_pos] + ["skip"]
        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "position_change",
            "src_pos": chosen_pos,
            "optional": True,
            "options": options,
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] position_change src={chosen_pos} (Love wing bell)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 27: PL!-bp4-005 星空凛 (ライブ開始時)
    # ブレード5以上の μ's メンバーがいない場合、このメンバーはセンター以外へポジションチェンジ
    # センター以外 = L / R のみ candidates にする
    # ------------------------------------------------------------------
    if ext_key == "live_start_no_mus_blade5_force_not_center":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        has_heavy_mus = False
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _card_group(slot, cards_db) == "μ's" and _slot_total_blade(slot) >= 5:
                        has_heavy_mus = True
                        break
        except Exception:
            pass

        if has_heavy_mus:
            try:
                gs.log.append("[AUTO_EXT] μ's blade>=5 exists, no position_change (星空凛)")
            except Exception:
                pass
            return True

        # センター以外: src_pos が C なら L/R どちらかへ、L/R なら反対側へ
        if src_pos == "C":
            options = ["L", "R"]
        elif src_pos == "L":
            options = ["R"]
        elif src_pos == "R":
            options = ["L"]
        else:
            options = ["L", "R"]

        payload = {
            "kind": "position_change",
            "src_pos": src_pos,
            "optional": False,
            "options": options,
            "source_cn": src,
            "text": f"{src}: 自分のステージにブレード5以上の『μ's』メンバーがいないため、センターエリア以外にポジションチェンジする",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 星空凛: force position_change to {options} from {src_pos}")
        except Exception:
            pass
        return True

    return False
