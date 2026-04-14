# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_success_zone_20260413f
from __future__ import annotations

"""llocg_ui.effects.success_zone

成功ライブ置き場 / ライブ中カード / 相手比較を扱う ext apply の正本。
"""

from typing import Any, Dict
from .helpers import *  # noqa: F403


def try_apply_success_zone_ext(
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
    if ext_key == "live_start_success_zone_count_x2_blade":
        slot = _src_slot(gs, ctx)
        success_cards = _success_zone_cards(gs)
        n = len(success_cards) * 2
        if slot is not None and n > 0:
            _add_temp_blade(eng, slot, n)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_zone={len(success_cards)} -> +{n}blade (西木野真姫)"
                )
            except Exception:
                pass
        elif slot is not None:
            try:
                gs.log.append("[AUTO_EXT] success_zone=0, no blade added (西木野真姫)")
            except Exception:
                pass
        return True
    # ------------------------------------------------------------------
    if ext_key == "enter_success_score_ge6_activate2":
        success_cards = _success_zone_cards(gs)
        total_score = sum(_card_score(c, cards_db) for c in success_cards)
        if total_score >= 6:
            moved = _activate_energy(gs, 2)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}>=6 -> activate {moved} energy (園田海未)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}<6, no energy (園田海未)"
                )
            except Exception:
                pass
        return True
    # ------------------------------------------------------------------
    if ext_key == "enter_success_score_ge3_draw1":
        success_cards = _success_zone_cards(gs)
        total_score = sum(_card_score(c, cards_db) for c in success_cards)
        if total_score >= 3:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}>=3 -> draw {drawn} (東條希)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}<3, no draw (東條希)"
                )
            except Exception:
                pass
        return True
    # ------------------------------------------------------------------
    if ext_key == "live_success_success_zone_has_mus_draw1":
        success_cards = _success_zone_cards(gs)
        has_mus = any(_card_group(c, cards_db) == "μ's" for c in success_cards)
        if has_mus:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_zone has μ's -> draw {drawn} (SENTIMENTAL StepS)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] no μ's in success_zone, no draw (SENTIMENTAL StepS)")
            except Exception:
                pass
        return True
    # ------------------------------------------------------------------
    if ext_key == "live_start_live_cards_count_x1_blade":
        slot = _src_slot(gs, ctx)
        live_cards = _live_in_progress_cards(gs)
        n = len(live_cards)
        if slot is not None and n > 0:
            _add_temp_blade(eng, slot, n)
            try:
                gs.log.append(
                    f"[AUTO_EXT] live_cards={n} -> +{n}blade (夕霧綴理)"
                )
            except Exception:
                pass
        elif slot is not None:
            try:
                gs.log.append("[AUTO_EXT] live_cards=0, no blade (夕霧綴理)")
            except Exception:
                pass
        return True
    # ------------------------------------------------------------------
    if ext_key == "live_success_score_gt_opp_and_hasunosora_energy_wait":
        my_score = _live_score_total(gs)
        opp_score = _opp_live_score_total(gs)
        try:
            if (ctx or {}).get("live_score") is not None:
                my_score = int(ctx["live_score"])
            if (ctx or {}).get("opp_live_score") is not None:
                opp_score = int(ctx["opp_live_score"])
        except Exception:
            pass

        has_hasunosora = _stage_has_group(gs, cards_db, "蓮ノ空")
        if not has_hasunosora:
            try:
                gs.log.append("[AUTO_EXT] no 蓮ノ空 on stage, no energy (ド！ド！ド！)")
            except Exception:
                pass
            return True

        opp_exists = _has_opponent_state(gs)
        if opp_exists:
            if my_score > opp_score:
                added = 0
                try:
                    put_wait = eng.get("_put_wait_energy_from_deck")
                    if callable(put_wait):
                        added = int(put_wait(gs, 1, reason="ド！ド！ド！") or 0)
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
                    gs.log.append(f"[AUTO_EXT] live_score {my_score}>{opp_score} & 蓮ノ空 on stage -> energy_wait +{added} (ド！ド！ド！)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append(f"[AUTO_EXT] live_score {my_score}<={opp_score}, no energy (ド！ド！ド！)")
                except Exception:
                    pass
            return True

        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "confirm_effect",
            "text": "【ド！ド！ド！】ライブ成功時：自分の合計スコアが相手より高いなら、エネルギーを1枚ウェイトで置く",
            "options": ["使う", "スキップ"],
            "after_effect_template": "ライブの合計スコアが相手より高く、かつ自分のステージに『蓮ノ空』のメンバーがいる場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。",
            "ctx": {"source_cn": src, "_ext_confirm_op": "energy_wait_plus1"},
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] ド！ド！ド！: confirm energy_wait+1 (my_score={my_score}, opp unavailable)")
        except Exception:
            pass
        return True

    return False
