# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_apply_pass_gd_to_green_search_20260424c
# BUILD_TAG: apply_unreachable_position_change_removed_20260629ae
from __future__ import annotations

"""llocg_ui.effects.apply

engine_effect の apply dispatcher の正本。

注意:
- ext_key ベースの effect 処理をここで受ける
- helper は effects.helpers から参照する
- 未対応時は False を返し、engine.py 側既存実装へフォールバックさせる
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403
from .green_search import try_apply_green_search_ext
from .topdeck import try_apply_topdeck_ext
from .success_zone import try_apply_success_zone_ext
from .energy import try_apply_energy_ext
from .position import try_apply_position_ext
from .stage_triggers import try_apply_stage_triggers_ext
from .live_start import try_apply_live_start_ext
from .special import try_apply_special_ext

def try_apply_effect_by_rule_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, str],
    ctx: Dict[str, Any],
) -> bool:
    """Apply extension-owned effect rules.

    Return True only if this module handled the rule completely.
    Return False to fall back to engine.py legacy implementation.
    """
    if str(rule.get("op") or "") != "__ext__":
        return False

    ext_key = str(rule.get("ext_key") or "").strip()

    if try_apply_green_search_ext(eng, gs, rng, cards_db, rule, gd, ctx):
        return True

    if try_apply_topdeck_ext(eng, gs, rng, cards_db, rule, gd, ctx, ext_key):
        return True

    if try_apply_success_zone_ext(eng, gs, rng, cards_db, rule, gd, ctx, ext_key):
        return True

    if try_apply_energy_ext(eng, gs, rng, cards_db, rule, gd, ctx, ext_key):
        return True

    if try_apply_position_ext(eng, gs, rng, cards_db, rule, gd, ctx, ext_key):
        return True

    if try_apply_stage_triggers_ext(eng, gs, rng, cards_db, rule, gd, ctx, ext_key):
        return True

    if try_apply_live_start_ext(eng, gs, rng, cards_db, rule, gd, ctx, ext_key):
        return True

    if try_apply_special_ext(eng, gs, rng, cards_db, rule, gd, ctx, ext_key):
        return True

    # confirm_effect helper path from engine.py (no-cost, single-player fallback)
    confirm_op = str((ctx or {}).get("_ext_confirm_op") or "").strip()
    if confirm_op == "draw1":
        drawn = _draw_cards(eng, gs, 1)
        try:
            gs.log.append(f"[AUTO_EXT] confirm -> draw {drawn}")
        except Exception:
            pass
        return True
    if confirm_op == "energy_wait_plus1":
        added = 0
        try:
            put_wait = eng.get("_put_wait_energy_from_deck")
            if callable(put_wait):
                added = int(put_wait(gs, 1, reason="confirm_effect") or 0)
            else:
                rem_fn = eng.get("_energy_remaining_in_deck")
                clamp_fn = eng.get("_clamp_energy_zone")
                rem = int(rem_fn(gs) if callable(rem_fn) else 0)
                if rem > 0:
                    gs.energy_wait = int(getattr(gs, "energy_wait", 0) or 0) + 1
                    if callable(clamp_fn):
                        clamp_fn(gs)
                    added = 1
        except Exception:
            pass
        try:
            gs.log.append(f"[AUTO_EXT] confirm -> energy_wait +{added}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 17: PL!-bp3-006 西木野真姫
    # ライブ終了時まで、成功ライブ置き場の枚数 × +2ブレード
    # ------------------------------------------------------------------
    # Prompt 24: PL!-bp4-001 高坂穂乃果
    # 自ステージのコスト合計が相手より低い場合、カードを1枚引く。
