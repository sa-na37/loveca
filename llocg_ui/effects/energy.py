# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_energy_20260413g
from __future__ import annotations

"""llocg_ui.effects.energy

energy active / wait / energy deck に関わる ext apply の正本。
現段階では小さく始め、以後の energy 系実装の受け皿にする。
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def try_apply_energy_ext(
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
    # Prompt 41: PL!-pb1-003 南ことり
    # ステージの Printemps メンバー数 × energy アクティブ
    # ------------------------------------------------------------------
    if ext_key == "enter_printemps_count_activate_energy":
        count = _stage_unit_count(gs, cards_db, "Printemps")
        if count > 0:
            moved = _activate_energy(gs, count)
            try:
                gs.log.append(
                    f"[AUTO_EXT] Printemps_on_stage={count} -> activate {moved} energy (南ことり)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] no Printemps on stage, no energy (南ことり)")
            except Exception:
                pass
        return True

    return False
