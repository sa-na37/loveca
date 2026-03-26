# -*- coding: utf-8 -*-
# BUILD_TAG: direct_stage_picker_skip_20260326c
from __future__ import annotations

"""llocg_ui.engine

ゲームフロー・フェイズ遷移・cmd_*・pending handlers。

起動コマンド（プロジェクトルート ~/Desktop/gsim/loveca から）:
  python3 run_llocg_ui_web.py --deck-code 1RCBL

修正時の命名規則:
  engine_{BUILD_TAG}.py として出力し、cp でデプロイする

依存: engine_base, engine_effects
"""

import re
import random
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from .db import (
    CardInfo,
    _safe_int, _read_json, _write_text,
    _hearts_from_counts_json, _parse_tags_json, _count_draw_icons,
    is_member_type, is_live_type,
    _canon_cardno, _cardno_variants, _get_card,
)

# engine_base: 全 helper・dataclass を再エクスポート（既存コードの互換維持）
from .engine_base import *
from .engine_base import (
    ENERGY_TOTAL_DEFAULT,
    GameState, StageSlot,
    draw, pay_energy, stage_blade, owned_base_hearts,
    _grant_temp_heart,
    _enqueue_discard_from_hand, _enqueue_choose_from_green,
    _enqueue_topdeck_from_green, _enqueue_choose_from_topk,
    _enqueue_choose_from_topk_filtered, _enqueue_look_top_3way_split,
    _enqueue_reorder_from_topk_keep_any, _enqueue_topdeck_from_hand,
    _enqueue_choose_top_keep_one, _resolve_choose_top_keep_one,
    _clamp_energy_zone,
    _energy_remaining_in_deck,
    _is_live_ci, _is_member_ci, _is_live,
    _count_blade_icons_from_tagblob, _count_blade_icons,
    _parse_energy_cost, _cost_requires_self_wait, _cost_requires_self_to_green,
    _iter_triggered_abilities, _iter_activated_abilities,
    _has_matchable_activated, _ability_has_supported_clause,
    _has_sacrifice_ability,
    can_activate_in_state, can_activate, activation_moves_self_to_green,
    snapshot_state, restore_state, push_undo, do_undo, begin_turn,
    new_game, refresh, load_simdeck,
    can_satisfy_req, cheer_hearts_from_resolve,
    _rule_refresh_main_deck, _rule_refresh_for_top_access,
)

# engine_effects: エフェクトルールと適用処理
from .engine_effects import (
    _EFFECT_RULES, _EFFECT_RULES_COMPILED, _match_effect_template,
    _HEART_ICON_COLOR_MAP, _HEART_JP_MAP, _parse_heart_icons,
    _apply_effect_by_rule, try_apply_effect_template,
    _enqueue_choose_effects_from_ability,
)

def _enqueue_live_start_prompts(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    """Queue live-start auto effects once per live (until Attempt resolves)."""
    if gs.live_start_prompted:
        return 0

    triggers: List[Dict[str, Any]] = []

    def _append_prompt(prompt: Dict[str, Any], label: str = '') -> None:
        pr = dict(prompt or {})
        txt = str(label or pr.get('text', '') or '')
        cn = str(pr.get('cn', '') or '')
        triggers.append({
            'kind': 'enqueue_pending_prompt',
            'source_cn': cn,
            'label': txt,
            'prompt': pr,
        })

    for pos in ("L", "C", "R"):
        slot = gs.stage.get(pos)
        if not slot:
            continue
        # ウェイト状態でもライブ開始時効果は発火する（ただし後続の能力チェックで
        # コスト「このメンバーをウェイトにする」系はすでにウェイトなのでスキップ）
        ci = _get_card(cards_db, slot.cardnumber)
        if not ci or not ci.abilities:
            continue

        # Special-case: 桜坂しずく bp1-003 live-start
        try:
            if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == _SHIZUKU_BP1_003_CN_CANON:
                if int(getattr(gs, 'energy_active', 0) or 0) >= 1:
                    pr = {
                        'kind': 'live_start_shizuku_bp1_003_pay',
                        'pos': pos,
                        'cn': getattr(ci, 'cardnumber', '') or '',
                        'text': f"{pos}: {getattr(ci, 'cardnumber', '') or ''} ライブ開始時 [E]1 → 好きなハート色を1つ得る (ライブ終了時まで)",
                        'options': ['pay', 'skip'],
                    }
                    _append_prompt(pr, pr['text'])
        except Exception:
            pass

        # Special-case: Emma Verde bp3-008 live-start
        try:
            if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == _EMMA_BP3_008_CN_CANON:
                cands0 = _emma_bp3_008_live_start_candidates(gs, cards_db, pos)
                if cands0 and len(list(getattr(gs, 'hand', []) or [])) >= 2:
                    pr = {
                        'kind': 'emma_bp3_008_live_start_pay',
                        'pos': pos,
                        'cn': getattr(ci, 'cardnumber', '') or '',
                        'text': '【エマ・ヴェルデ】ライブ開始時：手札を2枚控え室に置いてもよい → このメンバー以外のウェイト状態の『虹ヶ咲』メンバー1人をアクティブにする。そうした場合、そのメンバーとこのメンバーはライブ終了時まで緑ハート+1',
                        'options': ['pay', 'skip'],
                        'pos_options': list(cands0),
                    }
                    _append_prompt(pr, f"{pos}: {getattr(ci, 'cardnumber', '') or ''} ライブ開始時")
        except Exception:
            pass

        for ab in ci.abilities:
            if not isinstance(ab, dict):
                continue
            trig = str(ab.get("trigger", "") or "")
            if "ライブ開始時" not in trig:
                continue
            clauses = ab.get("clauses", [])
            if not isinstance(clauses, list):
                continue
            if (not str(getattr(gs, 'success_zone_heart_color', '') or '').strip()):
                try:
                    blob_all = ''.join([str((cl0.get('raw') or cl0.get('effect_template') or '') ) for cl0 in clauses if isinstance(cl0, dict)])
                except Exception:
                    blob_all = ''
                if (
                    ('成功ライブカード置き場' in blob_all) and
                    ('選んだハート' in blob_all) and
                    (('1つを選ぶ' in blob_all) or ('1つ選ぶ' in blob_all))
                ):
                    opts = [c for c in ['桃', '黄', '紫'] if f"<({c})>" in blob_all]
                    if len(opts) >= 2:
                        pr = {
                            'kind': 'live_start_success_heart_by_success',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'text': f"{pos}: {ci.cardnumber} ライブ開始時 → ({'/'.join(opts)})から1つ選ぶ：成功ライブ置き場1枚につき選んだハート+1 (ライブ終了時まで)",
                            'options': opts,
                        }
                        _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                        continue

            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                raw = str(cl.get("raw", "") or "")
                cost = str(cl.get("cost_template", "") or raw)
                eff = str(cl.get("effect_template", "") or raw)
                if "<(E)>" not in cost and "[E]" not in cost and "Ｅ" not in cost and "E" not in cost:
                    blob = str(eff or "")
                    if (not str(getattr(gs, 'success_zone_heart_color', '') or '').strip()) and (
                        ('成功ライブカード置き場' in blob) and ('選んだハート' in blob) and
                        ('<(桃)>' in blob) and ('<(黄)>' in blob) and ('<(紫)>' in blob) and
                        ('1つを選ぶ' in blob)
                    ):
                        pr = {
                            'kind': 'live_start_success_heart_by_success',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'text': f"{pos}: {ci.cardnumber} ライブ開始時 → (桃/黄/紫)を選ぶ：成功ライブ置き場1枚につき選んだハート+1 (ライブ終了時まで)",
                            'options': ['桃', '黄', '紫'],
                        }
                        _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                        continue
                    # ハート変換（元々持つハートは選んだハートになる）
                    if '元々持つハートは選んだハートになる' in blob and '選ぶ' in blob:
                        opts_hr = re.findall(r'<\(([^)]+)\)>', blob)
                        color_opts = []
                        for jp in opts_hr:
                            col = _HEART_JP_MAP.get(jp, '')
                            if col and col not in color_opts:
                                color_opts.append(col)
                        if color_opts:
                            opts_disp = [{'桃':'桃','red':'赤','yellow':'黄','green':'緑','blue':'青','purple':'紫','pink':'桃'}.get(c, c) for c in color_opts]
                            opts_disp_jp = [c for c in re.findall(r'<\(([^)]+)\)>', blob) if c in ('桃','赤','黄','緑','青','紫')]
                            if not opts_disp_jp:
                                opts_disp_jp = opts_disp
                            pr = {
                                'kind': 'live_start_heart_replace',
                                'pos': pos,
                                'cn': ci.cardnumber,
                                'text': f"{pos}: {ci.cardnumber} ライブ開始時 → 元々持つハートを選んだハートに変換 (ライブ終了時まで)",
                                'options': opts_disp_jp,
                                'color_map': {jp: _HEART_JP_MAP.get(jp, jp) for jp in opts_disp_jp},
                            }
                            _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                            continue
                    # Optional hand-discard cost（「手札をN枚控え室に置いてもよい」「手札のXを1枚控え室に置いてもよい」）
                    if '控え室に置いてもよい' in cost and _match_effect_template(eff):
                        # 手札のライブカードを捨てるコスト
                        m_live = re.search(r'手札のライブカードを(\d+)枚控え室に置いてもよい', cost)
                        m_hand = re.search(r'手札を(\d+)枚控え室に置いてもよい', cost)
                        if m_live:
                            cost_kind = 'discard_live_from_hand'
                            cost_n = int(m_live.group(1))
                        elif m_hand:
                            cost_kind = 'discard_from_hand'
                            cost_n = int(m_hand.group(1))
                        else:
                            cost_kind = 'discard_from_hand'
                            cost_n = 1
                        pr = {
                            'kind': 'live_start_pay_effect',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'need_e': 0,
                            'cost_kind': cost_kind,
                            'cost_n': cost_n,
                            'effect': eff,
                            'text': f"{pos}: {ci.cardnumber} ライブ開始時 [{cost}] → {eff}",
                            'options': ['pay', 'skip'],
                        }
                        _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                        continue
                    # コストなし・フリー効果（activate_stage_member等）
                    if not cost.strip() or cost.strip() == eff.strip():
                        m_free = _match_effect_template(eff)
                        if m_free:
                            r_free, gd_free = m_free
                            op_free = r_free.get('op', '')
                            if op_free == 'activate_stage_member':
                                opts_act = [p2 for p2 in ('L','C','R') if gs.stage.get(p2) and not gs.stage[p2].active]
                                if opts_act:
                                    pr = {
                                        'kind': 'choose_stage_member_to_activate',
                                        'pos': pos,
                                        'cn': ci.cardnumber,
                                        'text': f"{pos}: {ci.cardnumber} ライブ開始時 → アクティブにするメンバーを選択",
                                        'options': list(opts_act),
                                        'allow_less': True,
                                    }
                                    _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                    continue
                need_e = _parse_energy_cost(cost)
                if need_e <= 0:
                    need_e = 1

                blades = _count_blade_icons(eff)
                if blades > 0 and need_e == 1:
                    blade_mode = "per_live_card" if ("自分のライブ中のカード1枚につき" in eff or "自分のライブ中のカード１枚につき" in eff) else "fixed"
                    blade_text = (
                        f"{pos}: {ci.cardnumber} ライブ開始時 [E]1 → 自分のライブ中のカード1枚につきブレード+{blades} (ライブ終了時まで)"
                        if blade_mode == "per_live_card"
                        else f"{pos}: {ci.cardnumber} ライブ開始時 [E]1 → ブレード+{blades} (ライブ終了時まで)"
                    )
                    pr = {
                        "kind": "live_start_blade",
                        "pos": pos,
                        "cn": ci.cardnumber,
                        "need_e": 1,
                        "blades": int(blades),
                        "blade_mode": blade_mode,
                        "text": blade_text,
                        "options": ["pay", "skip"],
                    }
                    _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                    continue

                if _match_effect_template(eff):
                    pr = {
                        "kind": "live_start_pay_effect",
                        "pos": pos,
                        "cn": ci.cardnumber,
                        "need_e": int(need_e),
                        "effect": eff,
                        "text": f"{pos}: {ci.cardnumber} ライブ開始時 [E]{need_e} → {eff}",
                        "options": ["pay", "skip"],
                    }
                    _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")

    # LIVE-card live-start: Rise Up High! (PL!N-bp4-029)
    try:
        if int(getattr(gs, 'turn', 0) or 0) == 1:
            for cn_live in list(getattr(gs, 'set_zone', []) or []):
                if _canon_cardno(str(cn_live or '')) != _RISE_UP_HIGH_CN_CANON:
                    continue
                gs.log.append('[AUTO] LIVE: PL!N-bp4-029 live-start: score +1 (turn1)')
                cands = []
                for ppos in ('L','C','R'):
                    slot2 = (gs.stage or {}).get(ppos)
                    if not slot2 or not getattr(slot2, 'active', False):
                        continue
                    ci2 = _get_card(cards_db, getattr(slot2, 'cardnumber', '') or '')
                    if not ci2:
                        continue
                    if '虹ヶ咲' in str(getattr(ci2, 'group', '') or ''):
                        cands.append(ppos)
                if cands:
                    _rise_up_high_opts = []
                    for _pp in list(cands):
                        _sl = (gs.stage or {}).get(_pp)
                        _nm = ''
                        try:
                            _ci = _get_card(cards_db, getattr(_sl, 'cardnumber', '') or '') if _sl else None
                            _nm = str(getattr(_ci, 'name', '') or '') if _ci else ''
                        except Exception:
                            _nm = ''
                        _rise_up_high_opts.append(f"{_pp}: {_nm}" if _nm else str(_pp))
                    pr = {
                        'kind': 'live_start_rise_up_high_pick',
                        'cn': _RISE_UP_HIGH_CN_CANON,
                        'text': '【Rise Up High!】ライブ開始時：『虹ヶ咲』のメンバーを1人選ぶ（このライブ終了時まで、そのメンバーはブレード+1）',
                        'options': list(_rise_up_high_opts),
                        'pos_options': list(cands),
                    }
                    _append_prompt(pr, 'PL!N-bp4-029 ライブ開始時')
                else:
                    gs.log.append('[INFO] Rise Up High: no Nijigasaki member on stage; blade bonus skipped')
                break
    except Exception:
        pass

    try:
        if int(getattr(gs, 'energy_active', 0) or 0) >= 2 and _has_nijigasaki_member_on_stage(gs, cards_db):
            _bf_n = 0
            for _cn0 in list(getattr(gs, 'set_zone', []) or []):
                try:
                    _canon0 = _canon_cardno(_cn0)
                except Exception:
                    _canon0 = str(_cn0 or '')
                if _canon0 == _BUTTERFLY_CN_CANON:
                    _bf_n += 1
            for _i in range(int(_bf_n or 0)):
                pr = {
                    'kind': 'live_start_butterfly_pay',
                    'cn': _BUTTERFLY_CN_CANON,
                    'text': '【Butterfly】ライブ開始時：エネルギー2枚を支払ってもよい。自分のステージに『虹ヶ咲』のメンバーがいる場合、このカードのスコアを+1する。',
                    'options': ['pay', 'skip'],
                }
                _append_prompt(pr, 'PL!N-bp1-028 ライブ開始時')
    except Exception:
        pass

    try:
        if _neo_sky_stage_ready(gs, cards_db):
            _neo_n = 0
            for _cn0 in list(getattr(gs, 'set_zone', []) or []):
                try:
                    _canon0 = _canon_cardno(_cn0)
                except Exception:
                    _canon0 = str(_cn0 or '')
                if _canon0 == _NEO_SKY_CN_CANON:
                    _neo_n += 1
            for _i in range(int(_neo_n or 0)):
                pr = {
                    'kind': 'neo_sky_execute',
                    'cn': _NEO_SKY_CN_CANON,
                    'text': '【NEO SKY, NEO MAP!】ライブ開始時：条件達成 → 3枚引き、手札を3枚好きな順番でデッキの上に置く',
                    'options': ['ok'],
                }
                _append_prompt(pr, 'PL!N-bp4-031 ライブ開始時')
    except Exception:
        pass

    try:
        _niji_n = _count_nijigasaki_members_on_stage(gs, cards_db)
        if _niji_n > 0:
            _tc_n = 0
            for _cn0 in list(getattr(gs, 'set_zone', []) or []):
                try:
                    _canon0 = _canon_cardno(_cn0)
                except Exception:
                    _canon0 = str(_cn0 or '')
                if _canon0 == _TSUNAGARU_CONNECT_CN_CANON:
                    _tc_n += 1
            for _i in range(int(_tc_n or 0)):
                pr = {
                    'kind': 'tsunagaru_connect_execute',
                    'cn': _TSUNAGARU_CONNECT_CN_CANON,
                    'text': '【ツナガルコネクト】ライブ開始時：ステージの『虹ヶ咲』メンバー数ぶんデッキ上を見る → 1枚をデッキ上、残りを控え室。さらにデッキトップを公開し、ライブカードならスコア+1',
                    'options': ['ok'],
                    'k': int(_niji_n),
                }
                _append_prompt(pr, 'PL!N-bp3-028 ライブ開始時')
    except Exception:
        pass

    try:
        _vw_n = 0
        for _cn0 in list(getattr(gs, 'set_zone', []) or []):
            try:
                _canon0 = _canon_cardno(_cn0)
            except Exception:
                _canon0 = str(_cn0 or '')
            if _canon0 == _VIVID_WORLD_CN_CANON:
                _vw_n += 1
        for _i in range(int(_vw_n or 0)):
            triggers.append({
                'kind': 'live_start_vivid_world_auto',
                'source_cn': _VIVID_WORLD_CN_CANON,
                'label': 'PL!N-bp4-025 ライブ開始時',
            })
    except Exception:
        pass

    n = len(triggers)
    if n <= 0:
        return 0

    gs.live_start_prompted = True
    if n >= 2:
        gs.pending.append({
            'kind': 'auto_order',
            'text': 'ライブ開始時効果が複数発生：解決するカードを選択（1つずつ）',
            'options': [_auto_trigger_option_text(t) for t in triggers if _auto_trigger_option_text(t)],
            'queue': list(triggers),
        })
        gs.log.append(f'[PENDING] auto_order triggers={len(triggers)}')
        gs.log.append(f'[PROMPT] live-start abilities queued: {n}')
        return n

    for t in triggers:
        _exec_auto_trigger(gs, cards_db, t)
    gs.log.append(f'[AUTO] live-start triggers queued={n}')
    return n


def _clear_end_of_live_buffs(gs: GameState) -> None:
    for pos in ("L", "C", "R"):
        slot = gs.stage.get(pos)
        if not slot:
            continue
        if getattr(slot, "temp_until", "") == "end_of_live":
            slot.temp_blade = 0
            slot.temp_hearts = {}
            slot.temp_until = ""
        # Always clear heart_replace_color at end of live (it's always "until end of live")
        try:
            slot.heart_replace_color = ""
        except Exception:
            pass

    # clear global end-of-live buffs
    try:
        gs.success_zone_heart_color = ""
    except Exception:
        pass
    try:
        gs.butterfly_paid_this_live = 0
    except Exception:
        pass

def cmd_play(gs: GameState, cards_db: Dict[str, CardInfo], hand_idx: int, pos: str) -> None:
    pos = pos.upper()
    if pos not in ("L", "C", "R"):
        gs.log.append("[ERR] play: pos must be L/C/R")
        return
    if hand_idx < 0 or hand_idx >= len(gs.hand):
        gs.log.append("[ERR] play: invalid hand index")
        return
    existing = gs.stage.get(pos)
    baton_old_cn = None
    baton_old_cost = 0
    if existing is not None:
        # Baton touch (ルール 9.6.2.3.2): you may put your member in that area into green room to reduce the cost.
        baton_old_cn = existing.cardnumber
        old = _get_card(cards_db, baton_old_cn)
        baton_old_cost = int(old.cost) if old else 0
        # If the replaced member had energies under it, they return to the energy deck (not to energy zone).
        old_under = int(getattr(existing, 'energy_under', 0) or 0)
        if old_under > 0:
            try:
                gs.log.append(f"[INFO] {pos}: {baton_old_cn} leaves stage -> return under-energy x{old_under} to energy deck")
            except Exception:
                pass
            try:
                existing.energy_under = 0
            except Exception:
                pass

    cn = gs.hand[hand_idx]
    c = _get_card(cards_db, cn)
    ctype = (c.type if c else "")
    if not c or not is_member_type(ctype):
        gs.log.append(f"[ERR] play: not a MEMBER card: cn={cn} db_type='{ctype}'")
        return

    cost = int(c.cost or 0)
    pay_cost = cost
    if baton_old_cn is not None:
        # Always apply baton touch when the target stage area is occupied.
        # Reduce the cost by the replaced member's cost (min 0), and send the replaced member to green room.
        pay_cost = max(0, cost - int(baton_old_cost or 0))
        gs.green_room.append(baton_old_cn)
        gs.log.append(f"[BATON] {pos}: {baton_old_cn} -> green room; reduce {cost} by {baton_old_cost} => pay {pay_cost}")

    if not pay_energy(gs, pay_cost):
        gs.log.append(f"[ERR] play: insufficient energy (need {pay_cost}, have {gs.energy_active})")
        return

    gs.hand.pop(hand_idx)
    gs.stage[pos] = StageSlot(cardnumber=(c.cardnumber if c else cn), active=True)
    gs.log.append(f"[PLAY] {pos} <- {cn} (pay {pay_cost}; E active={gs.energy_active} wait={gs.energy_wait})")

    # Auto abilities can trigger simultaneously on this "member enters stage" event.
    # If multiple triggers exist, let the user choose the resolution order.
    triggers = _collect_auto_triggers_on_member_enter(gs, cards_db, entered_pos=pos, entered_cn=cn)
    if len(triggers) >= 2:
        opts2: List[str] = []
        for t in triggers:
            scn = _canon_cardno(str((t or {}).get('source_cn', '') or ''))
            if scn:
                # Keep duplicates so that multiple copies (e.g., 2×Ai) can be resolved separately.
                opts2.append(scn)
        gs.pending.append({
            'kind': 'auto_order',
            'text': '自動効果が複数発生：解決するカードを選択（1つずつ）',
            'options': opts2,
            'queue': triggers,
        })
        gs.log.append(f"[PENDING] auto_order triggers={len(triggers)}")
        return

    for t in triggers:
        _exec_auto_trigger(gs, cards_db, t)



def handle_enter_auto(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, cn: str, rng: Optional[random.Random] = None) -> None:
    # Handle [登場] auto abilities for a member that just entered stage.
    canon = _canon_cardno(cn)

    # Hard-coded Shioriko (choice prompt)
    if canon == "PL!N-pb1-010":
        gs.pending.append({
            "kind": "choose_shioriko_enter",
            "cn": canon,
            "pos": pos.upper(),
            "text": "栞子[登場]: 効果を1つ選ぶ（エネルギー+1 / 控え室の虹ヶ咲LIVEを最大2枚デッキ上）",
            "options": ["energy", "topdeck"],
        })
        gs.log.append("[AUTO] 栞子[登場]: choose mode -> pending")
        return

    if rng is None:
        rng = random.Random(gs.seed)

    ci = _get_card(cards_db, canon)
    if not ci or not getattr(ci, 'abilities', None):
        return

    for ab in _iter_triggered_abilities(ci, '登場'):
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            # Cost template handling (limited: optional discard from hand, e.g. "手札を1枚控え室に置いてもよい：...")
            if cost:
                m = re.search(r"手札を(\d+)枚控え室に置いてもよい", cost)
                n = 0
                if m:
                    try:
                        n = int(m.group(1) or 0)
                    except Exception:
                        n = 0
                if n <= 0 and ("手札を1枚控え室に置いてもよい" in cost):
                    n = 1
                if n > 0:
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    gs.pending.append({
                        'kind': 'pay_or_skip',
                        'text': f'{canon}[登場]: {cost}：{eff}',
                        'options': ['pay', 'skip'],
                        'cost_kind': 'discard_from_hand',
                        'cost_n': n,
                        'after_effect_template': eff,
                        'ctx': ctx,
                        'source_cn': canon,
                    })
                    gs.log.append(f"[PENDING] {canon}[登場]: pay/skip -> discard {n} then {eff}")
                    return
                # unsupported cost template for now
                continue

            # costless-only for now
            if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                continue
            ctx = {'pos': pos.upper(), 'source_cn': canon}
            if try_apply_effect_template(gs, rng, cards_db, eff, ctx):
                gs.log.append(f"[AUTO] {canon}[登場]: applied {eff}")
                if gs.pending:
                    return


def handle_stage_cost10_member_enter(gs: GameState, cards_db: Dict[str, CardInfo], entered_pos: str, entered_cn: str, ai_pos: str = '', rng: Optional[random.Random] = None) -> None:
    """Handle auto abilities that trigger when a cost-10 MEMBER enters your stage.

    PL!N-pb1-005 (宮下愛):
      <自動><ターン1回> 自分のステージにコスト10のメンバーが登場したとき、カードを1枚引く。

    NOTE: We resolve *one* Ai instance per trigger so that 2×Ai produces 2 separate triggers
    that can be ordered and resolved independently (rule-consistent).
    """
    try:
        entered_pos = str(entered_pos or '').upper()
    except Exception:
        entered_pos = 'C'
    try:
        ai_pos_u = str(ai_pos or '').upper()
    except Exception:
        ai_pos_u = ''

    canon_enter = _canon_cardno(entered_cn)
    ci_enter = _get_card(cards_db, canon_enter)
    if not ci_enter:
        return
    try:
        cost = int(getattr(ci_enter, 'cost', 0) or 0)
    except Exception:
        cost = 0
    if cost != 10:
        return

    def _resolve_one(p: str) -> None:
        slot = gs.stage.get(p)
        if not slot:
            return
        canon = _canon_cardno(slot.cardnumber)
        if canon != 'PL!N-pb1-005':
            return
        key = f"{p}:{canon}:auto_cost10_enter"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used >= 1:
            return
        drew = draw(gs, 1, rng)
        try:
            gs.used_this_turn[key] = 1
        except Exception:
            gs.used_this_turn = {key: 1}
        gs.log.append(f"[AUTO] {canon}({p}): cost10 member entered ({canon_enter} @ {entered_pos}) -> drew {drew}")

    if ai_pos_u in ('L', 'C', 'R'):
        _resolve_one(ai_pos_u)
        return

    # Fallback: resolve all (legacy behavior)
    for p in ('L', 'C', 'R'):
        _resolve_one(p)

def _has_supported_enter_auto(ci: Optional[CardInfo]) -> bool:
    if not ci or not getattr(ci, 'abilities', None):
        return False
    canon = _canon_cardno(getattr(ci, 'cardnumber', '') or '')
    # Special-cased Shioriko is always supported.
    if canon == 'PL!N-pb1-010':
        return True
    # Any costless, regex-matchable enter ability counts as supported.
    for ab in _iter_triggered_abilities(ci, '登場'):
        if not isinstance(ab, dict):
            continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue

            # allow optional discard-from-hand costs (e.g., "手札を1枚控え室に置いてもよい：...")
            if cost:
                m = re.search(r"手札を(\d+)枚控え室に置いてもよい", cost)
                n = 0
                if m:
                    try:
                        n = int(m.group(1) or 0)
                    except Exception:
                        n = 0
                if n <= 0 and ("手札を1枚控え室に置いてもよい" in cost):
                    n = 1
                if n > 0 and _match_effect_template(eff):
                    return True
                # other cost templates unsupported for enter-auto support detection
                continue

            if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                continue
            if _match_effect_template(eff):
                return True
            # Mode-style (choose) header across clauses
            if ('以下から' in eff) and ('選ぶ' in eff):
                return True
    return False


def _list_active_ai_cost10_positions(gs: GameState, cards_db: Dict[str, CardInfo], entered_cn: str) -> List[str]:
    """Return stage positions of unused 宮下愛(PL!N-pb1-005) that would trigger on cost-10 member enter."""
    canon_enter = _canon_cardno(entered_cn)
    ci_enter = _get_card(cards_db, canon_enter)
    if not ci_enter:
        return []
    try:
        cost = int(getattr(ci_enter, 'cost', 0) or 0)
    except Exception:
        cost = 0
    if cost != 10:
        return []
    out: List[str] = []
    for p in ('L', 'C', 'R'):
        slot = gs.stage.get(p)
        if not slot:
            continue
        canon = _canon_cardno(slot.cardnumber)
        if canon != 'PL!N-pb1-005':
            continue
        key = f"{p}:{canon}:auto_cost10_enter"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used < 1:
            out.append(p)
    return out


def _has_active_ai_cost10_trigger(gs: GameState, cards_db: Dict[str, CardInfo], entered_cn: str) -> bool:
    return bool(_list_active_ai_cost10_positions(gs, cards_db, entered_cn))

def _collect_auto_triggers_on_member_enter(gs: GameState, cards_db: Dict[str, CardInfo], entered_pos: str, entered_cn: str) -> List[Dict[str, Any]]:
    """Collect auto triggers that happen when a MEMBER enters your stage.

    Triggers are collected as individual instances (not de-duplicated), so that
    multiple copies of the same card (e.g., 2× 宮下愛) can be resolved separately
    in the order the player chooses.
    """
    out: List[Dict[str, Any]] = []

    canon_enter = _canon_cardno(entered_cn)
    ci_enter = _get_card(cards_db, canon_enter)
    if ci_enter and _has_supported_enter_auto(ci_enter):
        out.append({
            'kind': 'enter_auto',
            'source_cn': canon_enter,
            'pos': str(entered_pos or 'C').upper(),
            'cn': entered_cn,
        })

    # 宮下愛(PL!N-pb1-005): one trigger per unused copy on stage
    for ai_pos in _list_active_ai_cost10_positions(gs, cards_db, entered_cn):
        out.append({
            'kind': 'ai_cost10_enter',
            'source_cn': 'PL!N-pb1-005',
            'ai_pos': str(ai_pos).upper(),
            'entered_pos': str(entered_pos or 'C').upper(),
            'entered_cn': entered_cn,
        })

    return out

def _auto_trigger_option_text(t: Dict[str, Any]) -> str:
    try:
        lbl = str((t or {}).get('label', '') or '').strip()
    except Exception:
        lbl = ''
    if lbl:
        return lbl
    try:
        cn = str((t or {}).get('source_cn', '') or '').strip()
    except Exception:
        cn = ''
    return cn


def _exec_auto_trigger(gs: GameState, cards_db: Dict[str, CardInfo], trig: Dict[str, Any]) -> None:
    kind = str((trig or {}).get('kind', '') or '')
    if kind == 'enter_auto':
        pos = str(trig.get('pos', 'C') or 'C').upper()
        cn = str(trig.get('cn', '') or '')
        handle_enter_auto(gs, cards_db, pos, cn)
        return
    if kind == 'ai_cost10_enter':
        handle_stage_cost10_member_enter(gs, cards_db, entered_pos=str(trig.get('entered_pos','C') or 'C'), entered_cn=str(trig.get('entered_cn','') or ''), ai_pos=str(trig.get('ai_pos','') or ''), rng=rng)
        return
    if kind == 'enqueue_pending_prompt':
        prm = dict((trig or {}).get('prompt', {}) or {})
        if prm:
            gs.pending.append(prm)
        return
    if kind == 'live_start_vivid_world_auto':
        gs.vivid_world_blue_mode_this_live = True
        gs.log.append('[AUTO] VIVID WORLD live-start: cheer pink/red/yellow/green/purple/all -> blue until end of live')
        return
    # Unknown trigger
    gs.log.append(f"[WARN] auto_trigger: unknown kind={kind}")



def cmd_set(gs: GameState, rng: random.Random, indices: List[int]) -> None:
    if len(indices) > 3:
        gs.log.append("[ERR] set: max 3 cards")
        return
    if any(i < 0 or i >= len(gs.hand) for i in indices):
        gs.log.append("[ERR] set: invalid indices")
        return
    idxs = sorted(set(indices), reverse=True)
    picked = []
    for i in idxs:
        picked.append(gs.hand.pop(i))
    picked.reverse()
    gs.set_zone = picked[:]
    drawn = draw(gs, len(picked), rng)
    gs.log.append(f"[SET] set {len(picked)} cards, drew {drawn}")


def cmd_yell(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo]) -> None:
    # ライブ開始時プロンプトが未処理なら先に処理させる（ブレード変化が確定してからYELL）
    if _enqueue_live_start_prompts(gs, cards_db) > 0:
        gs.log.append("[INFO] yell: live-start prompts queued, resolve them first.")
        return
    n = stage_blade(gs, cards_db)
    if n <= 0:
        gs.log.append("[YELL] 0 (no blade on active stage members)")
        return
    revealed = []
    for i in range(n):
        if not gs.deck:
            _rule_refresh_main_deck(gs, rng, reason=f'yell@{i}')
        if not gs.deck:
            break
        revealed.append(gs.deck.pop(0))
    gs.resolve_zone.extend(revealed)

    # Track cheer reveals for this live (e.g., Poppin' Up!)
    try:
        _lst = list(getattr(gs, '_yell_revealed_this_live', []) or [])
    except Exception:
        _lst = []
    _lst.extend(list(revealed))
    try:
        setattr(gs, '_yell_revealed_this_live', _lst)
    except Exception:
        pass

    try:
        if bool(getattr(gs, 'vivid_world_blue_mode_this_live', False)):
            gs.vivid_world_bonus_this_live = 1 if _vivid_world_revealed_niji_has_all_six(gs, cards_db) else 0
            if int(getattr(gs, 'vivid_world_bonus_this_live', 0) or 0) > 0:
                gs.log.append('[AUTO] VIVID WORLD: revealed Nijigasaki members contain all six colors -> score +1')
            else:
                gs.log.append('[AUTO] VIVID WORLD: revealed Nijigasaki members do not contain all six colors')
        else:
            gs.vivid_world_bonus_this_live = 0
    except Exception:
        gs.vivid_world_bonus_this_live = 0

    draw_n = 0
    for cn in revealed:
        c = _get_card(cards_db, cn)
        if c:
            draw_n += _count_draw_icons(c.blade_heart_tags_json)
    got = draw(gs, draw_n, rng) if draw_n > 0 else 0
    gs.log.append(f"[YELL] revealed {len(revealed)} (blade={n}), draw+{draw_n} -> drew {got}")



def _has_nijigasaki_member_on_stage(gs: GameState, cards_db: Dict[str, CardInfo]) -> bool:
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        if '虹ヶ咲' in str(getattr(ci, 'group', '') or ''):
            return True
    return False


def _put_wait_energy_from_deck(gs: GameState, n: int, reason: str = '') -> int:
    n = int(n or 0)
    if n <= 0:
        return 0
    rem = int(_energy_remaining_in_deck(gs))
    if rem <= 0:
        gs.log.append("[INFO] energy deck empty" + (f" ({reason})" if reason else ""))
        return 0
    add = min(rem, n)
    gs.energy_wait += add
    _clamp_energy_zone(gs)
    gs.log.append(f"[AUTO] energy deck -> WAIT +{add}" + (f" ({reason})" if reason else ""))
    return int(add)


def _la_bella_patria_green_excess(gs: GameState) -> int:
    try:
        pool = dict(getattr(gs, 'last_attempt_excess_hearts', {}) or {})
    except Exception:
        pool = {}
    return int(pool.get('green', 0) or 0)


def _la_bella_patria_can_trigger(gs: GameState, cards_db: Dict[str, CardInfo]) -> bool:
    # IMPORTANT: only real green excess counts here. ALL does not satisfy this condition.
    if int(_la_bella_patria_green_excess(gs)) <= 0:
        return False
    return bool(_has_nijigasaki_member_on_stage(gs, cards_db))


def _enqueue_success_auto_order(gs: GameState, triggers: List[Dict[str, Any]]) -> int:
    triggers = list(triggers or [])
    n = len(triggers)
    if n <= 0:
        return 0
    if n == 1:
        return 1
    gs.pending.append({
        'kind': 'auto_order',
        'text': 'ライブ成功時効果が複数発生：解決するカードを選択（1つずつ）',
        'options': [_auto_trigger_option_text(t) for t in triggers if _auto_trigger_option_text(t)],
        'queue': list(triggers),
    })
    gs.log.append(f"[PROMPT] live-success abilities queued: {n}")
    return n


def _run_live_success_triggers(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], lives: List[str]) -> None:
    try:
        setattr(gs, '_poppin_pending_queue', [])
    except Exception:
        pass
    success_triggers: List[Dict[str, Any]] = []
    """Run <ライブ成功時> triggers at LIVE_RESOLVE timing (before winner-based success storage).

    Some LIVE success effects conditionally depend on 成功ライブカード置き場 (e.g., Daydream Mermaid),
    and the current successful LIVE may be placed there. Therefore we execute these triggers after the
    optional 'store one successful LIVE card' prompt has been resolved.
    """
    # Stage-member success triggers (costless, regex-supported subset)
    for pos in ('L','C','R'):
        slot = gs.stage.get(pos)
        if not slot or not slot.active:
            continue
        ci_src = _get_card(cards_db, slot.cardnumber)
        if not ci_src or not getattr(ci_src, 'abilities', None):
            continue
        for ab in _iter_triggered_abilities(ci_src, 'ライブ成功時'):
            ctx = {'pos': pos, 'source_cn': ci_src.cardnumber}
            if isinstance(ab, dict) and _enqueue_choose_effects_from_ability(gs, cards_db, ab, ctx):
                return
            clauses = ab.get('clauses', [])
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                cost = str(cl.get('cost_template', '') or '')
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                    continue
                # Optional hand-discard cost for retrieve_from_yell effects
                m_opt = re.search(r'手札を(\d+)枚控え室に置いてもよい', cost)
                if m_opt and _match_effect_template(eff) and 'retrieve_from_yell' == (_match_effect_template(eff) or [{}])[0].get('op', ''):
                    cost_n = int(m_opt.group(1))
                    gs.pending.append({
                        'kind': 'live_success_pay_effect',
                        'pos': pos,
                        'cn': ci_src.cardnumber,
                        'cost_kind': 'discard_from_hand',
                        'cost_n': cost_n,
                        'effect': eff,
                        'text': f"{pos}: {ci_src.cardnumber}[ライブ成功時] 手札を{cost_n}枚控え室に置いてもよい → {eff}",
                        'options': ['pay', 'skip'],
                        'source_cn': ci_src.cardnumber,
                        'ctx': {'pos': pos, 'source_cn': ci_src.cardnumber},
                    })
                    gs.log.append(f"[PENDING] {pos}: {ci_src.cardnumber}[ライブ成功時] pay_or_skip -> {eff}")
                    return
                ctx = {'pos': pos, 'source_cn': ci_src.cardnumber}
                if try_apply_effect_template(gs, rng, cards_db, eff, ctx):
                    gs.log.append(f"[AUTO] {pos}: {ci_src.cardnumber}[ライブ成功時] applied {eff}")
                    if gs.pending:
                        return
            if gs.pending:
                return
        if gs.pending:
            return

    # Live-card success triggers (costless, regex-supported subset)
    for cn_live in list(lives or []):
        ci_live = _get_card(cards_db, cn_live)

        # Special: La Bella Patria (PL!N-bp3-027)
        try:
            if _canon_cardno(str(cn_live or '')) == _LA_BELLA_PATRIA_CN_CANON:
                if _la_bella_patria_can_trigger(gs, cards_db):
                    success_triggers.append({
                        'kind': 'success_auto_labella',
                        'source_cn': str(cn_live or ''),
                        'label': 'PL!N-bp3-027 ライブ成功時',
                    })
                else:
                    gs.log.append('[INFO] La Bella Patria: condition not met')
        except Exception:
            pass

        # Special: Poppin' Up! (PL!N-bp1-026)
        try:
            if _canon_cardno(str(cn_live or '')) == _POPPIN_UP_CN_CANON:
                pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
                cands = []
                for cn2 in pool:
                    ci2 = _get_card(cards_db, cn2)
                    if ci2 and ('虹ヶ咲' in str(getattr(ci2, 'group', '') or '')):
                        cands.append(cn2)
                if cands:
                    _pp_q = list(getattr(gs, '_poppin_pending_queue', []) or [])
                    _pp_q.append({
                        'kind': 'pick_poppinup_from_yell',
                        'text': "【Poppin' Up!】ライブ成功時：相手より合計スコアが高い場合、エールで公開された自分の『虹ヶ咲』カードを1枚手札に加える（条件を満たさない場合はSkip可）",
                        'options': list(cands),
                        'source_cn': str(cn_live or ''),
                    })
                    setattr(gs, '_poppin_pending_queue', _pp_q)
                    success_triggers.append({
                        'kind': 'success_auto_poppin',
                        'source_cn': str(cn_live or ''),
                        'label': "PL!N-bp1-026 ライブ成功時",
                    })
                    gs.log.append(f"[QUEUE] PoppinUp pick from yell ({len(cands)} candidates)")
                else:
                    gs.log.append("[INFO] PoppinUp: no Nijigasaki cards among yell reveals")
        except Exception:
            pass
        if not ci_live or not getattr(ci_live, 'abilities', None):
            continue
        for ab in _iter_triggered_abilities(ci_live, 'ライブ成功時'):
            ctx2 = {'source_cn': cn_live}
            if isinstance(ab, dict) and _enqueue_choose_effects_from_ability(gs, cards_db, ab, ctx2):
                return
            clauses = ab.get('clauses', [])
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                cost = str(cl.get('cost_template', '') or '')
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                    continue
                ctx2 = {'source_cn': cn_live}
                if try_apply_effect_template(gs, rng, cards_db, eff, ctx2):
                    gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時] applied {eff}")
                    if gs.pending:
                        return
            if gs.pending:
                return
        if gs.pending:
            return

    # Execute success triggers (Poppin / La Bella).
    # If multiple triggers exist, show auto_order prompt for ordering.
    if success_triggers:
        if len(success_triggers) == 1:
            trig = success_triggers[0]
            k = str((trig or {}).get('kind', '') or '')
            if k == 'success_auto_labella':
                _put_wait_energy_from_deck(gs, 1, reason='La Bella Patria')
            elif k == 'success_auto_poppin':
                _pp_q = list(getattr(gs, '_poppin_pending_queue', []) or [])
                if _pp_q:
                    gs.pending.append(_pp_q[0])
                    setattr(gs, '_poppin_pending_queue', _pp_q[1:])
        else:
            _enqueue_success_auto_order(gs, success_triggers)


# ----------------------------
# Step21: LIVE scoring helpers (UI)
# ----------------------------
_EUTOPIA_CN_CANON = 'PL!N-bp1-029'
_RISE_UP_HIGH_CN_CANON = 'PL!N-bp4-029'

_POPPIN_UP_CN_CANON = 'PL!N-bp1-026'
_SOLITUDE_RAIN_CN_CANON = 'PL!N-bp1-027'
_PSYCHO_HEART_CN_CANON = 'PL!N-bp3-026'
_STARS_WE_CHASE_CN_CANON = 'PL!N-bp4-028'
_LOVE_U_MY_FRIENDS_CN_CANON = 'PL!N-bp3-030'
_MONSTER_GIRLS_CN_CANON = 'PL!N-bp3-031'
_EMOTION_CN_CANON = 'PL!N-bp4-027'
_LA_BELLA_PATRIA_CN_CANON = 'PL!N-bp3-027'
_BUTTERFLY_CN_CANON = 'PL!N-bp1-028'
_TSUNAGARU_CONNECT_CN_CANON = 'PL!N-bp3-028'
_VIVID_WORLD_CN_CANON = 'PL!N-bp4-025'
_SHIZUKU_BP1_003_CN_CANON = 'PL!N-bp1-003'
_NEO_SKY_CN_CANON = 'PL!N-bp4-031'
_EMMA_BP3_008_CN_CANON = 'PL!N-bp3-008'
def _live_score_delta_for_attempt(cn_live, lives_count, gs_turn):
    # Eutopia: if 3+ LIVE cards are set in this attempt, score +2 for Eutopia
    # Rise Up High!: if turn==1 live phase, score +1 for this card
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon == _EUTOPIA_CN_CANON and int(lives_count) >= 3:
        return 2
    if canon == _RISE_UP_HIGH_CN_CANON and int(gs_turn or 0) == 1:
        return 1
    return 0

def _compute_attempt_score_breakdown(lives, cards_db, gs_turn, gs=None):
    lives_count = len(lives or [])
    total = 0
    rows = []
    _butterfly_paid_remaining = int(getattr(gs, 'butterfly_paid_this_live', 0) or 0) if gs is not None else 0
    for cn in (lives or []):
        ci = _get_card(cards_db, cn)
        base = int(getattr(ci, 'score', 0) or 0) if ci else 0
        delta = int(_live_score_delta_for_attempt(cn, lives_count, gs_turn))
        if gs is not None:
            delta += int(_extra_live_score_delta_for_attempt(cn, gs, cards_db))
        try:
            canon = _canon_cardno(cn)
        except Exception:
            canon = str(cn or '')
        if canon == _BUTTERFLY_CN_CANON and _butterfly_paid_remaining > 0:
            delta += 1
            _butterfly_paid_remaining -= 1
        eff = base + delta
        total += eff
        rows.append({'cn': cn, 'base': base, 'delta': delta, 'score': eff})
    return total, rows




def _solitude_rain_stage_color_kinds(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    cols = set()
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'active', False):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if '虹ヶ咲' not in str(getattr(ci, 'group', '') or ''):
            continue
        for k, v in ((getattr(ci, 'base_hearts', None) or {}) or {}).items():
            if k in ('pink', 'red', 'yellow', 'green', 'blue', 'purple') and int(v or 0) > 0:
                cols.add(k)
    return int(len(cols))



def _psycho_heart_success_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    has1 = False
    has5 = False
    for cn in list(getattr(gs, 'success_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        sc = int(getattr(ci, 'score', 0) or 0)
        if sc == 1:
            has1 = True
        elif sc == 5:
            has5 = True
    if has1 and has5:
        return 2
    if has1 or has5:
        return 1
    return 0



def _stars_we_chase_waiting_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    names = set()
    for cn in list(getattr(gs, 'green_room', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if not _is_live_ci(ci):
            continue
        if '虹ヶ咲' not in str(getattr(ci, 'group', '') or ''):
            continue
        nm = str(
            getattr(ci, 'name', '') or
            getattr(ci, 'cardname', '') or
            getattr(ci, 'title', '') or
            cn
        )
        if nm:
            names.add(nm)
    n = len(names)
    if n >= 6:
        return 2
    if n >= 4:
        return 1
    return 0



def _love_u_my_friends_success_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        txt = str(getattr(ci, 'blade_heart_tags_json', '') or '')
        if '(ALL)' in txt:
            return 1
    return 0



def _monster_girls_wait_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    n = 0
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot:
            continue
        cn = str(getattr(slot, 'cardnumber', '') or '')
        if not cn:
            continue
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        if bool(getattr(slot, 'active', False)):
            continue
        n += 1
    return int(n)



def _emotion_success_count(gs: GameState) -> int:
    if gs is None:
        return 0
    n = 0
    for cn in list(getattr(gs, 'success_zone', []) or []):
        try:
            canon = _canon_cardno(cn)
        except Exception:
            canon = str(cn or '')
        if canon == _EMOTION_CN_CANON:
            n += 1
    return int(n)


def _emotion_required_any_bonus(cn_live, gs: GameState) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon != _EMOTION_CN_CANON:
        return 0
    return 3 * int(_emotion_success_count(gs))


def _effective_live_required_hearts(cn_live, ci, gs: GameState) -> Dict[str, int]:
    req = dict((getattr(ci, 'required_hearts', {}) if ci else {}) or {})
    try:
        extra_any = int(_emotion_required_any_bonus(cn_live, gs))
    except Exception:
        extra_any = 0
    if extra_any > 0:
        req['any'] = int(req.get('any', 0) or 0) + extra_any
    return req


def _extra_live_score_delta_for_attempt(cn_live, gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon == _SOLITUDE_RAIN_CN_CANON:
        return int(_solitude_rain_stage_color_kinds(gs, cards_db))
    if canon == _PSYCHO_HEART_CN_CANON:
        return int(_psycho_heart_success_bonus(gs, cards_db))
    if canon == _STARS_WE_CHASE_CN_CANON:
        return int(_stars_we_chase_waiting_bonus(gs, cards_db))
    if canon == _LOVE_U_MY_FRIENDS_CN_CANON:
        return int(_love_u_my_friends_success_bonus(gs, cards_db))
    if canon == _MONSTER_GIRLS_CN_CANON:
        return int(_monster_girls_wait_bonus(gs, cards_db))
    if canon == _EMOTION_CN_CANON:
        return 2 * int(_emotion_success_count(gs))
    if canon == _TSUNAGARU_CONNECT_CN_CANON:
        return int(getattr(gs, 'tsunagaru_connect_bonus_this_live', 0) or 0)
    if canon == _VIVID_WORLD_CN_CANON:
        return int(getattr(gs, 'vivid_world_bonus_this_live', 0) or 0)
    return 0


def _enqueue_next_poppin_prompt(gs: GameState) -> bool:
    if list(getattr(gs, 'pending', []) or []):
        return False
    q = list(getattr(gs, '_poppin_pending_queue', []) or [])
    while q:
        p0 = dict(q.pop(0))
        pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
        raw_opts = list(p0.get('options', []) or [])
        counts: Dict[str, int] = {}
        for x in pool:
            cx = _canon_cardno(x)
            counts[cx] = counts.get(cx, 0) + 1
        filtered: List[str] = []
        for x in raw_opts:
            cx = _canon_cardno(x)
            if counts.get(cx, 0) > 0:
                filtered.append(x)
                counts[cx] -= 1
        if filtered:
            p0['options'] = list(filtered)
            gs.pending.append(p0)
            setattr(gs, '_poppin_pending_queue', q)
            gs.log.append(f"[PENDING] PoppinUp queued prompt ({len(filtered)} candidates)")
            return True
    setattr(gs, '_poppin_pending_queue', [])
    return False

def cmd_attempt(gs: GameState, cards_db: Dict[str, CardInfo]) -> None:
    if not gs.set_zone:
        gs.last_attempt_excess_hearts = {}
        gs.butterfly_paid_this_live = 0
        gs.tsunagaru_connect_bonus_this_live = 0
        gs.vivid_world_blue_mode_this_live = False
        gs.vivid_world_bonus_this_live = 0
        gs.log.append("[ATTEMPT] no set cards")
        # clear end-of-live state defensively
        gs.last_attempt_lives = []
        gs.last_attempt_ok = False
        gs.need_live_success_triggers = False
        gs.need_success_store_choice = False
        _clear_end_of_live_buffs(gs)
        gs.live_start_prompted = False
        return

    if gs.pending:
        gs.log.append("[WARN] attempt: pending prompts exist; resolve them first.")
        return

    if _enqueue_live_start_prompts(gs, cards_db) > 0:
        gs.log.append("[INFO] attempt: resolve live-start prompts, then click Attempt again.")
        return

    lives = []
    nonlives = []
    for cn in gs.set_zone:
        c = _get_card(cards_db, cn)
        if c and is_live_type(c.type):
            lives.append(cn)
        else:
            nonlives.append(cn)

    if nonlives:
        gs.green_room.extend(nonlives)

    base = owned_base_hearts(gs, cards_db)
    cheer = cheer_hearts_from_resolve(gs, cards_db)
    owned = dict(base)
    for k, v in cheer.items():
        owned[k] = owned.get(k, 0) + int(v)

    gs.log.append(f"[ATTEMPT] LIVE={len(lives)} base={base} cheer={cheer} owned={owned}")
    globals()['_CURRENT_GS_FOR_ATTEMPT'] = gs
    ok_all, alloc_map = _solve_multi_live_allocations(lives, cards_db, owned)
    globals()['_CURRENT_GS_FOR_ATTEMPT'] = None

    if ok_all:
        try:
            _excess_pool = {str(k).lower(): int(v or 0) for k, v in (owned or {}).items()}
            for _cn0 in lives:
                _apply_alloc_to_pool(alloc_map.get(_cn0, {}) or {}, _excess_pool)
            gs.last_attempt_excess_hearts = dict(_excess_pool)
        except Exception:
            gs.last_attempt_excess_hearts = {}
        for cn in lives:
            c = _get_card(cards_db, cn)
            req = _effective_live_required_hearts(cn, c, gs)
            alloc = alloc_map.get(cn, {}) or {}
            gs.log.append(f"  live: OK {cn} req={req} alloc={alloc}")
    else:
        gs.last_attempt_excess_hearts = {}
        # Failure trace (deterministic): consume hearts in current LIVE list order using the same reduction rule (8.3.15.1.2).
        pool_trace: Dict[str, int] = {str(k).lower(): int(v or 0) for k, v in (owned or {}).items()}
        pool_trace.setdefault("all", 0)
        failed_at = None
        for cn in lives:
            c = _get_card(cards_db, cn)
            req = _effective_live_required_hearts(cn, c, gs)
            ok, alloc = can_satisfy_req(req, pool_trace)
            gs.log.append(f"  live: {'OK' if ok else 'NG'} {cn} req={req} alloc={alloc}")
            if ok:
                _apply_alloc_to_pool(alloc, pool_trace)
            else:
                failed_at = cn
                break
        # Mark remaining lives (if any) as not attempted in trace
        if failed_at is not None:
            seen_fail = False
            for cn in lives:
                if cn == failed_at:
                    seen_fail = True
                    continue
                if seen_fail:
                    c = _get_card(cards_db, cn)
                    req = _effective_live_required_hearts(cn, c, gs)
                    gs.log.append(f"  live: NG {cn} req={req} alloc={{'reason': 'not reached'}}")


    # clear set zone (attempted)
    gs.set_zone = []

    # Result & UI banner
    if ok_all:
        total_score, score_rows = _compute_attempt_score_breakdown(lives, cards_db, int(getattr(gs, 'turn', 0) or 0), gs)
        for r in score_rows:
            cn = r.get('cn', '')
            base_s = int(r.get('base', 0) or 0)
            delta_s = int(r.get('delta', 0) or 0)
            eff_s = int(r.get('score', 0) or 0)
            if delta_s:
                gs.log.append(f"  score: {cn} = {eff_s} ({base_s}+{delta_s})")
            else:
                gs.log.append(f"  score: {cn} = {eff_s}")
        gs.log.append(f"[ATTEMPT] result=SUCCESS total_score={total_score}")
        result_txt = f"SUCCESS (Score{total_score})"
    else:
        gs.log.append("[ATTEMPT] result=FAIL")
        result_txt = "FAIL"

    # UI banner (transient)
    gs.banner_text = result_txt
    gs.banner_ts = time.time()
    gs.banner_ttl = 4.0

    # Move attempted LIVE cards: by default they go to waiting room (green_room).
    if lives:
        gs.green_room.extend(lives)
        if ok_all:
            gs.log.append(f"[ZONE] waiting +{len(lives)} (success live)")
            # IMPORTANT (rules timing):
            # - Do NOT move a successful LIVE to success storage here.
            # - Do NOT run <ライブ成功時> triggers here.
            # These are handled in LIVE_RESOLVE (8.4 timing) so the just-succeeded LIVE
            # does NOT count as being in success storage during its own success-effect resolution.
            gs.last_attempt_lives = list(lives)
            gs.last_attempt_ok = True
            gs.need_live_success_triggers = True
            gs.need_success_store_choice = True
        else:
            gs.log.append(f"[ZONE] waiting +{len(lives)} (failed live)")
            gs.last_attempt_lives = []
            gs.last_attempt_ok = False
            gs.need_live_success_triggers = False
            gs.need_success_store_choice = False
            _clear_end_of_live_buffs(gs)
            gs.live_start_prompted = False
    else:
        gs.last_attempt_lives = []
        gs.last_attempt_ok = False
        gs.need_live_success_triggers = False
        gs.need_success_store_choice = False
        _clear_end_of_live_buffs(gs)
        gs.live_start_prompted = False


def cmd_ack(gs: GameState, rng: Optional[random.Random] = None) -> None:
    if not gs.resolve_zone:
        gs.log.append("[ACK] resolve zone empty")
        return
    n = len(gs.resolve_zone)
    gs.green_room.extend(gs.resolve_zone)
    gs.resolve_zone = []
    gs.log.append(f"[ACK] moved {n} revealed cards -> green room")
    _rule_refresh_main_deck(gs, rng, reason='ack')




def cmd_toggle_stage_active(gs: GameState, cards_db: Dict[str, CardInfo], pos: str) -> None:
    pos = str(pos or '').upper()
    if pos not in ('L', 'C', 'R'):
        gs.log.append(f"[ERR] toggle_stage_active: invalid pos={pos}")
        return
    slot = (gs.stage or {}).get(pos)
    if not slot or not getattr(slot, 'cardnumber', ''):
        gs.log.append(f"[ERR] toggle_stage_active: empty stage {pos}")
        return
    ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
    if ci and _is_live_ci(ci):
        gs.log.append(f"[ERR] toggle_stage_active: not a member at {pos}")
        return
    slot.active = (not bool(getattr(slot, 'active', False)))
    state = 'ACTIVE' if bool(slot.active) else 'WAIT'
    gs.log.append(f"[STATE] {pos} -> {state} ({getattr(slot, 'cardnumber', '')})")


def cmd_activate_to_green(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, rng: Optional[random.Random] = None) -> None:
    # Activate ability on stage member at pos.
    pos = str(pos or "").upper()
    if pos not in ("L", "C", "R"):
        gs.log.append("[ERR] activate: pos must be L/C/R")
        return
    slot = gs.stage.get(pos)
    if not slot:
        gs.log.append(f"[ERR] activate: empty stage {pos}")
        return
    ci = _get_card(cards_db, slot.cardnumber)
    if not ci:
        gs.log.append(f"[ERR] activate: card not in DB: {slot.cardnumber}")
        return

    if rng is None:
        rng = random.Random(gs.seed)

    # Special-case: Emma Verde bp3-008
    if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == _EMMA_BP3_008_CN_CANON:
        key = f"{pos}:{_EMMA_BP3_008_CN_CANON}:emma_bp3_008_activate"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used >= 1:
            gs.log.append(f"[INFO] activate: already used this turn ({key})")
            return
        cands = _emma_bp3_008_wait_candidates(gs, cards_db, pos)
        if not cands:
            gs.log.append("[INFO] エマ・ヴェルデ: ウェイトにできる『虹ヶ咲』メンバーがいない")
            return
        opts = [_stage_pos_label(gs, cards_db, pp) for pp in cands]
        gs.pending.append({
            'kind': 'emma_bp3_008_wait_pick',
            'text': '【エマ・ヴェルデ】起動：このメンバー以外の『虹ヶ咲』メンバー1人をウェイト状態にする → カードを1枚引く',
            'options': list(opts),
            'pos_options': list(cands),
            'source_pos': pos,
            'source_cn': getattr(ci, 'cardnumber', '') or '',
            'ability_key': key,
        })
        gs.log.append(f"[PENDING] Emma bp3-008: choose 1 Nijigasaki member to set WAIT ({len(cands)} candidates)")
        return

    # 1) Generic activated abilities
    for ab in _iter_activated_abilities(ci):
        flags = _ability_usage_flags(ab if isinstance(ab, dict) else {})
        akey = _ability_key(ci, ab if isinstance(ab, dict) else {}, pos)
        if flags.get('turn_only') is not None and int(gs.turn or 0) != int(flags['turn_only']):
            continue
        if flags.get('once_per_turn'):
            used = int((getattr(gs, 'used_this_turn', {}) or {}).get(akey, 0) or 0)
            if used >= 1:
                gs.log.append(f"[INFO] activate: already used this turn ({akey})")
                return

        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list) or not clauses:
            continue

        gs.log.append(f"[ACT] {pos}: {ci.cardnumber} activated")
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            # コストのみのclause（effect_templateが空）も処理する
            # 例：「このメンバーをウェイトにする：カードを1枚引き、手札を1枚控え室に置く。」
            # の場合、cost_template="このメンバーをウェイトにする" / effect_template="" のclauseが
            # 先に来ることがあるため、コストだけ適用してcontinueする
            if not eff:
                # effが空でもコスト（self-wait）だけ処理してcontinue
                if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost):
                    if slot and slot.active:
                        slot.active = False
                        gs.log.append(f"[COST] {pos}: {getattr(slot,'cardnumber','?')} -> WAIT (self-wait cost, eff-empty clause)")
                continue

            need_e = _parse_energy_cost(cost)
            if need_e > 0:
                if not pay_energy(gs, need_e):
                    gs.log.append(f"[ERR] activate: insufficient energy for [E]{need_e} (have {gs.energy_active})")
                    return
                gs.log.append(f"[COST] paid [E]{need_e} (E active={gs.energy_active} wait={gs.energy_wait})")

            # Special cost: move 1 energy from energy zone under this member
            # Prefer WAIT energy first, then ACTIVE (Mia etc.).
            if _cost_move_active_energy_to_under(cost):
                a_act = int(gs.energy_active or 0)
                a_wait = int(gs.energy_wait or 0)
                if (a_act + a_wait) < 1:
                    gs.log.append(f"[ERR] activate: insufficient energy to place under (active={gs.energy_active} wait={gs.energy_wait})")
                    return
                src = 'active'
                try:
                    if a_wait >= 1:
                        gs.energy_wait -= 1
                        src = 'wait'
                    else:
                        gs.energy_active -= 1
                        src = 'active'
                except Exception:
                    pass
                try:
                    slot.energy_under = int(getattr(slot, 'energy_under', 0) or 0) + 1
                except Exception:
                    pass
                gs.log.append(f"[COST] moved 1 energy under {pos} from {src} (under={int(getattr(slot,'energy_under',0) or 0)}; E active={gs.energy_active} wait={gs.energy_wait})")

            if _cost_requires_self_to_green(cost):
                gs.green_room.append(slot.cardnumber)
                gs.stage[pos] = None
                gs.log.append(f"[COST] {pos}: {slot.cardnumber} -> waiting room")

            # Cost: self-wait (member stays on stage but becomes WAIT)
            if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost):
                slot.active = False
                gs.log.append(f"[COST] {pos}: {slot.cardnumber} -> WAIT (self-wait cost)")

            # Cost: pick named cards from green room, shuffle to deck bottom
            named_cost = _cost_named_cards_to_deck_bottom(cost)
            if named_cost:
                names = named_cost['names']
                total = named_cost['total']
                # candidates: cards in green room whose name contains any target name
                cands = []
                for gcn in list(gs.green_room):
                    gci = _get_card(cards_db, gcn)
                    gname = str(getattr(gci, 'name', '') or getattr(gci, 'cardname', '') or gcn)
                    if any(n in gname for n in names):
                        cands.append(gcn)
                if len(cands) < total:
                    gs.log.append(f"[ERR] named_cards_cost: コスト支払い不可。必要{total}枚、控え室に{len(cands)}枚（{names}）")
                    # 消費済みコスト（エネルギー・自己控え室）を巻き戻す余裕はないので警告のみ
                    return
                else:
                    # Mark once-per-turn before suspending
                    if flags.get('once_per_turn'):
                        try:
                            gs.used_this_turn[akey] = 1
                        except Exception:
                            try:
                                gs.used_this_turn = {akey: 1}
                            except Exception:
                                pass
                    gs.pending.append({
                        'kind': 'named_cards_cost_multi',
                        'text': f'控え室から合計{total}枚を選択してデッキの一番下へ（{"・".join(names)}）',
                        'options': cands,
                        'total': total,
                        'resume_effect': eff,
                        'resume_pos': pos,
                        'resume_source_cn': ci.cardnumber,
                    })
                    gs.log.append(f"[PENDING] named_cards_cost_multi: total={total} cands={cands}")
                    return

            # Mark once-per-turn usage after costs are paid (even if effect creates pending)
            if flags.get('once_per_turn'):
                try:
                    gs.used_this_turn[akey] = 1
                except Exception:
                    try:
                        gs.used_this_turn = {akey: 1}
                    except Exception:
                        pass

            ctx = {'pos': pos, 'source_cn': ci.cardnumber}
            matched = try_apply_effect_template(gs, rng, cards_db, eff, ctx)
            if not matched:
                gs.log.append(f"[WARN] activate: unsupported effect_template: {eff}")

            if gs.pending:
                return

        return

    # If this card has matchable activated templates, do NOT fall back to legacy heuristics.
    if _has_matchable_activated(ci):
        gs.log.append(f"[ERR] activate: no usable activated ability on {ci.cardnumber} (conditions/cost/limit)")
        return

    # 2) Legacy fallback (kept)
    if not (_has_green_live_take_ability(ci) or _has_green_member_take_ability(ci) or _has_sacrifice_ability(ci)):
        gs.log.append(f"[ERR] activate: no supported activated ability on {ci.cardnumber}")
        return

    if _has_sacrifice_ability(ci):
        gs.green_room.append(slot.cardnumber)
        gs.stage[pos] = None
        gs.log.append(f"[ACT] {pos}: {ci.cardnumber} -> waiting room (cost)")

    if _has_green_live_take_ability(ci):
        cands = _green_live_candidates(gs, cards_db)
        if not cands:
            gs.log.append("[ACT] no LIVE in waiting room to take")
        elif len(cands) == 1:
            take_cn = cands[0]
            gs.green_room.remove(take_cn)
            gs.hand.append(take_cn)
            gs.log.append(f"[ACT] took LIVE {take_cn} from waiting room -> hand")
        else:
            gs.pending.append({
                "kind": "pick_live_from_green",
                "text": "控え室のライブカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 LIVE from waiting room ({len(cands)} candidates)")

    if _has_green_member_take_ability(ci):
        def _card_type_upper(x: Any) -> str:
            if x is None:
                return ""
            t = getattr(x, "type", None)
            if t is None:
                t = getattr(x, "cardtype", None)
            return str(t or "").upper()

        cands = [cn for cn in gs.green_room if (_get_card(cards_db, cn) and _card_type_upper(_get_card(cards_db, cn)) == "MEMBER")]
        if not cands:
            gs.log.append("[ACT] no MEMBER in waiting room to take")
        elif len(cands) == 1:
            take_cn = cands[0]
            gs.green_room.remove(take_cn)
            gs.hand.append(take_cn)
            gs.log.append(f"[ACT] took MEMBER {take_cn} from waiting room -> hand")
        else:
            gs.pending.append({
                "kind": "pick_member_from_green",
                "text": "控え室のメンバーカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 MEMBER from waiting room ({len(cands)} candidates)")



def cmd_resolve_pending(gs: GameState, cards_db: Dict[str, CardInfo], idx: int, choice: str, rng: Optional[random.Random] = None) -> None:
    if idx < 0 or idx >= len(gs.pending):
        gs.log.append("[ERR] resolve_pending: invalid idx")
        return
    if rng is None:
        rng = random.Random(gs.seed)
    p = gs.pending.pop(idx)
    kind = str(p.get("kind", "") or "")
    choice_str = str(choice or "").strip()

    def _auto_queue_to_options(q: List[Dict[str, Any]]) -> List[str]:
        out: List[str] = []
        for t in (q or []):
            txt = _auto_trigger_option_text(t)
            if txt:
                out.append(txt)
        return out

    def _enqueue_auto_order_from_deferred() -> None:
        """Enqueue deferred auto-order prompt only when nothing else is pending.

        This prevents interleaving multiple auto triggers in the middle of a multi-step
        resolution chain (e.g., mode choice -> target pick).
        """
        q = getattr(gs, '_deferred_auto_queue', None)
        if not q:
            return
        if gs.pending:
            return
        # Avoid duplication
        if any((str(pp.get('kind','') or '') == 'auto_order') for pp in (gs.pending or [])):
            return
        opts2 = _auto_queue_to_options(list(q))
        if not opts2:
            setattr(gs, '_deferred_auto_queue', [])
            return
        gs.pending.append({
            'kind': 'auto_order',
            'text': str(getattr(gs, '_deferred_auto_text', '') or '自動効果が複数発生：解決するカードを選択（1つずつ）'),
            'options': opts2,
            'queue': list(q),
        })
        setattr(gs, '_deferred_auto_queue', [])

    if kind == 'auto_order':
        queue = list(p.get('queue', []) or [])
        if not queue:
            gs.log.append('[INFO] auto_order: empty queue')
            return
        cn_choice = _canon_cardno(choice_str)
        pick_i = None
        for i, t in enumerate(queue):
            txt = _auto_trigger_option_text(t)
            if txt and txt == choice_str:
                pick_i = i
                break
            if _canon_cardno(str(t.get('source_cn', '') or '')) == cn_choice:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f"[ERR] auto_order: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        trig = queue.pop(pick_i)
        if str(trig.get('kind','')) == 'success_auto_labella':
            _put_wait_energy_from_deck(gs, 1, reason='La Bella Patria')
        elif str(trig.get('kind','')) == 'success_auto_poppin':
            _pp_q = list(getattr(gs, '_poppin_pending_queue', []) or [])
            if _pp_q:
                gs.pending.append(_pp_q[0])
                setattr(gs, '_poppin_pending_queue', _pp_q[1:])
            else:
                gs.log.append('[INFO] PoppinUp: no pending queue')
        else:
            _exec_auto_trigger(gs, cards_db, trig)

        # Defer remaining triggers until the current trigger (and any nested pending prompts) finishes.
        if queue:
            setattr(gs, '_deferred_auto_queue', list(queue))
            setattr(gs, '_deferred_auto_text', str(p.get('text', '') or '自動効果が複数発生：解決するカードを選択（1つずつ）'))
            _enqueue_auto_order_from_deferred()
        return

    # --- Generic effect-engine prompts ---

    if kind == 'pay_or_skip':
        # Generic optional-cost prompt (e.g., "...してもよい：<effect>")
        cost_kind = str(p.get('cost_kind', '') or '')
        cost_n = _safe_int(p.get('cost_n', 0), 0)
        after_eff = str(p.get('after_effect_template', '') or '').strip()
        ctx0 = dict(p.get('ctx', {}) or {})
        src = str(p.get('source_cn', '') or '')
        low = choice_str.lower()

        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append(f"[SKIP] {src}: skipped optional cost")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return

        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f"[ERR] pay_or_skip: invalid choice {choice_str}")
            gs.pending.append(p)
            return

        if cost_kind == 'discard_from_hand':
            if cost_n <= 0:
                gs.log.append("[ERR] pay_or_skip: invalid cost_n")
                return
            if len(gs.hand) < cost_n:
                gs.log.append(f"[ERR] pay_or_skip: not enough cards in hand (need {cost_n})")
                return
            gs.pending.append({
                'kind': 'discard_from_hand',
                'remaining': cost_n,
                'text': f'手札を{cost_n}枚控え室に置く',
                'options': list(gs.hand),
                'after_effect_template': after_eff,
                'after_ctx': ctx0,
                'after_source_cn': src,
            })
            return

        gs.log.append(f"[ERR] pay_or_skip: unsupported cost_kind={cost_kind}")
        return


    if kind == 'discard_from_hand':
        rem = _safe_int(p.get('remaining', 0), 0)
        after_eff = str(p.get('after_effect_template', '') or '').strip()
        after_ctx = dict(p.get('after_ctx', {}) or {})
        after_src = str(p.get('after_source_cn', '') or '')
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, x in enumerate(list(gs.hand)):
            if _canon_cardno(x) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f"[ERR] discard: chosen not in hand {cn}")
            return
        moved = gs.hand.pop(pick_i)
        gs.green_room.append(moved)
        rem -= 1
        gs.log.append(f"[ACT] discard 1 -> {moved} (remaining={rem})")
        if rem > 0:
            gs.pending.append({
                'kind': 'discard_from_hand',
                'remaining': rem,
                'text': f'手札を{rem}枚控え室に置く',
                'options': list(gs.hand),
                'after_effect_template': after_eff,
                'after_ctx': after_ctx,
                'after_source_cn': after_src,
            })
            return

        # After-cost effect (if any)
        if after_eff:
            rng2 = random.Random(getattr(gs, 'seed', 1) or 1)
            ok = try_apply_effect_template(gs, rng2, cards_db, after_eff, after_ctx)
            if ok:
                gs.log.append(f"[ACT] {after_src}: applied {after_eff}")
            else:
                gs.log.append(f"[WARN] {after_src}: after-cost effect not matchable {after_eff}")
        # resume parent prompt if provided
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return




    if kind == 'pick_success_to_store':
        lives = list(p.get('lives', []) or [])
        if not lives:
            gs.log.append('[INFO] success_store: no successful live cards')
            return
        c0 = str(choice_str or '').strip()
        if c0.lower() == 'skip':
            gs.log.append('[ACT] success_store: skipped')
            _clear_end_of_live_buffs(gs)
            gs.live_start_prompted = False
            return

        cn = _canon_cardno(c0)
        pick = None
        for x in lives:
            if _canon_cardno(x) == cn:
                pick = x
                break
        if not pick:
            gs.log.append(f"[ERR] success_store: invalid choice {cn}")
            gs.pending.insert(idx, p)
            return
        # move the chosen card from waiting room to success storage
        pick_cn = None
        if pick in gs.green_room:
            pick_cn = pick
        else:
            for v in _cardno_variants(pick):
                if v in gs.green_room:
                    pick_cn = v
                    break
        if not pick_cn:
            # it should exist, but don't crash
            pick_cn = pick
        try:
            if pick_cn in gs.green_room:
                gs.green_room.remove(pick_cn)
        except Exception:
            pass
        try:
            gs.success_zone.append(pick_cn)
        except Exception:
            gs.success_zone = list(getattr(gs, 'success_zone', []) or []) + [pick_cn]
        gs.log.append(f"[ACT] success_store: moved {pick_cn} -> success storage")
        _clear_end_of_live_buffs(gs)
        gs.live_start_prompted = False
        return

    if kind == 'live_start_success_heart_by_success':
        ch = str(choice_str or '').strip()
        m = {
            '桃': 'pink',
            '黄': 'yellow',
            '紫': 'purple',
            'pink': 'pink',
            'yellow': 'yellow',
            'purple': 'purple',
        }
        col = m.get(ch, '')
        if not col:
            gs.log.append(f"[ERR] live_start_success_heart: invalid choice '{ch}'")
            gs.pending.append(p)
            return
        try:
            gs.success_zone_heart_color = col
        except Exception:
            pass
        gs.log.append(f"[ACT] live_start_success_heart: choose={col} (per success card, until end_of_live)")
        return

    if kind == 'live_start_heart_replace':
        pos2 = str(p.get('pos', '') or '').upper()
        cn2 = str(p.get('cn', '') or '')
        ch = str(choice_str or '').strip()
        color_map = dict(p.get('color_map', {}) or {})
        # ch may be Japanese color name
        col = _HEART_JP_MAP.get(ch, '') or color_map.get(ch, '') or ''
        if not col:
            gs.log.append(f"[ERR] live_start_heart_replace: invalid choice '{ch}' for {cn2}")
            gs.pending.append(p)
            return
        slot2 = gs.stage.get(pos2)
        if not slot2:
            gs.log.append(f"[SKIP] live_start_heart_replace: {pos2} empty")
            return
        slot2.heart_replace_color = col
        gs.log.append(f"[ACT] {pos2}: {cn2} 元々持つハートを'{col}'に変換 (ライブ終了時まで)")
        return

    if kind == 'choose_effects':
        remaining = list(p.get('remaining', []) or [])
        picked = list(p.get('picked', []) or [])
        min_pick = int(p.get('min', 1) or 1)
        max_pick = int(p.get('max', 1) or 1)
        ctx0 = dict(p.get('ctx', {}) or {})
        choice0 = str(choice_str or '').strip()

        if choice0.lower() in ('done', '__done__', 'finish', 'end', '終了', '完了'):
            if len(picked) < min_pick:
                # still need at least one selection
                gs.log.append(f"[ERR] choose_effects: select >= {min_pick} before Done")
                gs.pending.append(p)
                return
            gs.log.append(f"[ACT] choose_effects: done (picked={len(picked)})")
            return

        if choice0 not in remaining:
            gs.log.append(f"[ERR] choose_effects: invalid choice '{choice0}'")
            gs.pending.append(p)
            return

        # remove one occurrence
        rem2 = list(remaining)
        try:
            rem2.remove(choice0)
        except Exception:
            rem2 = [x for x in remaining if x != choice0]
        picked2 = picked + [choice0]

        # Apply the chosen effect (may enqueue another pending)
        rng2 = random.Random(getattr(gs, 'seed', 1) or 1)
        ok = try_apply_effect_template(gs, rng2, cards_db, choice0, ctx0)
        if ok:
            gs.log.append(f"[ACT] choose_effects: applied {choice0}")
        else:
            gs.log.append(f"[WARN] choose_effects: not matchable {choice0}")

        # Need more selections?
        need_more = (len(picked2) < max_pick) and bool(rem2)
        if need_more:
            opts = list(rem2)
            if len(picked2) >= min_pick:
                opts.append('Done')
            resume = {
                'kind': 'choose_effects',
                'text': str(p.get('text', '') or '選択'),
                'options': opts,
                'remaining': list(rem2),
                'picked': list(picked2),
                'min': min_pick,
                'max': max_pick,
                'ctx': ctx0,
            }
            if gs.pending:
                # Attach resume to the next pending (e.g., choose_member_from_green)
                try:
                    gs.pending[-1]['_resume'] = resume
                except Exception:
                    gs.pending.append(resume)
            else:
                gs.pending.append(resume)
        return


    if kind in ('choose_live_from_green','choose_member_from_green'):
        want_kind = 'LIVE' if kind=='choose_live_from_green' else 'MEMBER'
        cn = _canon_cardno(choice_str)
        pick_cn = None
        if cn in gs.green_room:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gs.green_room:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] retrieve: not in waiting room {cn}")
            return
        ci2 = _get_card(cards_db, pick_cn)
        if want_kind=='LIVE' and not _is_live_ci(ci2):
            gs.log.append(f"[ERR] retrieve: not LIVE {pick_cn}")
            return
        if want_kind=='MEMBER' and not _is_member_ci(ci2):
            gs.log.append(f"[ERR] retrieve: not MEMBER {pick_cn}")
            return
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] retrieved {want_kind} {pick_cn} -> hand")
        # n>1 連続回収
        remaining_picks = int(p.get('remaining_picks', 1) or 1) - 1
        if remaining_picks > 0:
            _enqueue_choose_from_green(gs, cards_db, kind=want_kind, n=remaining_picks,
                                       group=str(p.get('want_group', '') or ''))
            return
        # resume parent prompt if provided (e.g., choose_effects)
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return

    if kind == 'view_topk_no_match':
        # User confirmed viewing the pool; send all to green room
        pool = list(p.get('pool', []) or [])
        gs.green_room.extend(pool)
        gs.log.append(f'[ACT] view_topk_no_match: confirmed -> {len(pool)} cards to waiting room')
        return

    if kind == 'choose_from_topk':
        pool = list(p.get('pool', []) or [])
        if not pool:
            gs.log.append('[ERR] topk: pool missing')
            return
        optional = bool(p.get('optional', False))
        # skip: put all pool cards to waiting room
        if choice_str.strip().lower() in ('skip', 'スキップ', '__skip__'):
            if optional:
                gs.green_room.extend(pool)
                gs.log.append(f'[ACT] topk: skip chosen -> {len(pool)} cards to waiting room')
            else:
                gs.log.append('[ERR] topk: skip not allowed (not optional)')
                gs.deck = pool + gs.deck
            return
        cn = _canon_cardno(choice_str)
        pick_idx = None
        candidates = list(p.get('candidates', pool) or pool)
        for i, x in enumerate(pool):
            if _canon_cardno(x) == cn:
                # validate against candidates if filtered
                if candidates and cn not in [_canon_cardno(c) for c in candidates]:
                    gs.log.append(f'[ERR] topk: {cn} not in filtered candidates')
                    gs.deck = pool + gs.deck
                    return
                pick_idx = i
                break
        if pick_idx is None:
            gs.log.append(f"[ERR] topk: invalid choice {cn}")
            gs.deck = pool + gs.deck
            return
        pick_cn = pool.pop(pick_idx)
        gs.hand.append(pick_cn)
        gs.green_room.extend(pool)
        gs.log.append(f"[ACT] topk chose {pick_cn} -> hand; rest {len(pool)} -> waiting room")
        return

    if kind == 'look_top_3way_step':
        pool = list(p.get('pool', []) or [])
        step = str(p.get('step', 'hand') or 'hand')
        if not pool:
            gs.log.append('[ERR] look_top_3way: pool missing')
            return
        cn = _canon_cardno(choice_str)
        match_idx = None
        for i, x in enumerate(pool):
            if _canon_cardno(x) == cn:
                match_idx = i
                break
        if match_idx is None:
            gs.log.append(f'[ERR] look_top_3way: {cn} not in pool {pool}')
            gs.deck = pool + gs.deck
            return
        picked = pool.pop(match_idx)
        if step == 'hand':
            gs.hand.append(picked)
            gs.log.append(f'[ACT] look_top_3way: {picked} -> hand')
            if len(pool) >= 2:
                remaining = list(pool)
                gs.pending.append({
                    'kind': 'look_top_3way_step',
                    'text': f'残り{len(remaining)}枚からデッキ上に置く1枚を選ぶ（残りは控え室）',
                    'options': remaining,
                    'pool': remaining,
                    'step': 'topdeck',
                    'picked_hand': picked,
                    'picked_top': '',
                })
            else:
                # only 1 left -> goes to deck top, none to green
                if pool:
                    gs.deck.insert(0, pool[0])
                    gs.log.append(f'[AUTO] look_top_3way: {pool[0]} -> deck top (only card left)')
        elif step == 'topdeck':
            gs.deck.insert(0, picked)
            gs.log.append(f'[ACT] look_top_3way: {picked} -> deck top')
            gs.green_room.extend(pool)
            gs.log.append(f'[AUTO] look_top_3way: {pool} -> waiting room')
        return




    if kind == 'named_cards_cost_multi':
        total = int(p.get('total', 0) or 0)
        options = list(p.get('options', []) or [])
        resume_eff = str(p.get('resume_effect', '') or '')
        resume_pos = str(p.get('resume_pos', '') or '')
        resume_src = str(p.get('resume_source_cn', '') or '')

        # choice_str はカンマ区切りの cardnumber リスト（server.py から送信）
        raw_picks = [s.strip() for s in choice_str.split(',')
                     if s.strip() and s.strip().lower() not in ('__done__', 'done', 'skip')]

        if len(raw_picks) != total:
            gs.log.append(f"[ERR] named_cards_cost_multi: 枚数不一致（必要{total}枚、選択{len(raw_picks)}枚）")
            gs.pending.insert(0, p)  # 再度選択させる
            return

        picks_canon = [_canon_cardno(x) for x in raw_picks]
        green_copy = list(gs.green_room)
        picked = []
        ok = True
        for cn in picks_canon:
            found = False
            for i, gcn in enumerate(green_copy):
                if _canon_cardno(gcn) == cn and gcn in options:
                    picked.append(green_copy.pop(i))
                    found = True
                    break
            if not found:
                gs.log.append(f"[ERR] named_cards_cost_multi: {cn} が控え室/選択肢に見つからない")
                ok = False
                break

        if not ok:
            return

        gs.green_room = green_copy
        rng_local = random.Random(gs.seed)
        rng_local.shuffle(picked)
        gs.deck = gs.deck + picked
        gs.log.append(f"[COST] named_cards_cost_multi: {picked} → デッキ下（シャッフル済）")

        if resume_eff:
            ctx = {'pos': resume_pos, 'source_cn': resume_src}
            matched = try_apply_effect_template(gs, rng, cards_db, resume_eff, ctx)
            if not matched:
                gs.log.append(f"[WARN] named_cards_cost_multi: 効果テンプレート非対応: {resume_eff}")
        return

    if kind == 'topdeck_from_green':
        rem = _safe_int(p.get('remaining', 0), 0)
        picked = list(p.get('picked', []) or [])
        want_kind = str(p.get('want_kind', '') or '').upper()
        want_group = str(p.get('want_group', '') or '')
        allow_less = bool(p.get('allow_less', False))

        low = choice_str.lower()
        if allow_less and low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            if picked:
                # picked list is already in desired top order
                gs.deck = picked + gs.deck
                gs.log.append(f"[ACT] topdeck_from_green: placed {len(picked)} on top (early finish)")
            else:
                gs.log.append("[SKIP] topdeck_from_green: picked 0")
            return

        # pick card in waiting room (allow variants)
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, x in enumerate(list(gs.green_room)):
            if _canon_cardno(x) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f"[ERR] topdeck_from_green: chosen not in waiting room {cn}")
            # restore picked back to waiting room (best effort)
            if picked:
                gs.green_room.extend(picked)
            return

        pick_cn = gs.green_room.pop(pick_i)
        ci2 = _get_card(cards_db, pick_cn)
        if want_kind == 'LIVE' and not _is_live_ci(ci2):
            gs.log.append(f"[ERR] topdeck_from_green: not LIVE {pick_cn}")
            gs.green_room.append(pick_cn)
            if picked:
                gs.green_room.extend(picked)
            return
        if want_kind == 'MEMBER' and not _is_member_ci(ci2):
            gs.log.append(f"[ERR] topdeck_from_green: not MEMBER {pick_cn}")
            gs.green_room.append(pick_cn)
            if picked:
                gs.green_room.extend(picked)
            return
        # want_kind == 'ANY': no type check
        if want_group and (want_group not in str(getattr(ci2, 'group', '') or '')):
            gs.log.append(f"[ERR] topdeck_from_green: group mismatch {pick_cn}")
            gs.green_room.append(pick_cn)
            if picked:
                gs.green_room.extend(picked)
            return

        picked.append(pick_cn)
        rem -= 1

        if rem <= 0:
            gs.deck = picked + gs.deck
            gs.log.append(f"[ACT] topdeck_from_green: placed {len(picked)} on top")
            return

        # rebuild candidates
        cands: List[str] = []
        for x in list(gs.green_room):
            ci = _get_card(cards_db, x)
            if not ci:
                continue
            if want_kind == 'LIVE' and not _is_live_ci(ci):
                continue
            if want_kind == 'MEMBER' and not _is_member_ci(ci):
                continue
            # want_kind == 'ANY': no type filter
            if want_group and (want_group not in str(getattr(ci, 'group', '') or '')):
                continue
            cands.append(x)

        if not cands:
            # no more candidates; finalize with what we have
            gs.deck = picked + gs.deck
            gs.log.append(f"[ACT] topdeck_from_green: candidates exhausted; placed {len(picked)} on top")
            return

        opts = list(cands) + (['skip'] if allow_less else [])
        gs.pending.append({
            'kind': 'topdeck_from_green',
            'text': f'控え室の{want_kind}をデッキ上に置く（残り{rem}枚）/ skipで終了' if allow_less else f'控え室の{want_kind}をデッキ上に置く（残り{rem}枚）',
            'options': opts,
            'remaining': rem,
            'picked': picked,
            'want_kind': want_kind,
            'want_group': want_group,
            'allow_less': allow_less,
        })
        gs.log.append(f"[PENDING] topdeck_from_green: picked {pick_cn}; remaining {rem}")
        return

    if kind == 'reorder_topk_keep_any':
        pool = list(p.get('pool', []) or [])
        kept = list(p.get('kept', []) or [])
        if not pool and not kept:
            gs.log.append('[ERR] reorder_topk: state missing')
            return

        low = choice_str.lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            # finalize early
            if pool:
                gs.green_room.extend(pool)
            if kept:
                gs.deck = kept + gs.deck
            gs.log.append(f"[ACT] reorder_topk: kept {len(kept)} on top; rest {len(pool)} -> waiting room")
            return

        cn = _canon_cardno(choice_str)
        pick_idx = None
        for i, x in enumerate(pool):
            if _canon_cardno(x) == cn:
                pick_idx = i
                break
        if pick_idx is None:
            gs.log.append(f"[ERR] reorder_topk: invalid choice {cn}")
            # best-effort restore
            gs.deck = kept + pool + gs.deck
            return

        pick_cn = pool.pop(pick_idx)
        kept.append(pick_cn)

        if not pool:
            # done
            gs.deck = kept + gs.deck
            gs.log.append(f"[ACT] reorder_topk: kept {len(kept)} on top; rest 0 -> waiting room")
            return

        # queue next pick
        opts = list(pool) + ['skip']
        gs.pending.append({
            'kind': 'reorder_topk_keep_any',
            'text': f'次にデッキ上に置くカードを選択（残り{len(pool)}枚）/ skipで終了',
            'options': opts,
            'pool': list(pool),
            'kept': list(kept),
            'allow_less': True,
        })
        gs.log.append(f"[PENDING] reorder_topk: picked {pick_cn}; remaining {len(pool)}")
        return

    if kind == 'live_start_butterfly_pay':
        low = str(choice_str or '').strip().lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] Butterfly live-start skipped')
            return
        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f'[ERR] Butterfly live-start: invalid choice {choice_str}')
            return
        if int(getattr(gs, 'energy_active', 0) or 0) < 2:
            gs.log.append('[ERR] Butterfly live-start: not enough active energy')
            return
        if not _has_nijigasaki_member_on_stage(gs, cards_db):
            gs.log.append('[INFO] Butterfly live-start: no Nijigasaki member on stage')
            return
        gs.energy_active = max(0, int(getattr(gs, 'energy_active', 0) or 0) - 2)
        gs.butterfly_paid_this_live = int(getattr(gs, 'butterfly_paid_this_live', 0) or 0) + 1
        gs.log.append('[AUTO] Butterfly live-start: paid E2 -> score +1')
        return

    if kind == 'neo_sky_execute':
        drew = draw(gs, 3, None)
        gs.log.append(f'[AUTO] NEO SKY, NEO MAP!: drew {drew}')
        _enqueue_topdeck_from_hand(gs, 3, 'NEO SKY, NEO MAP!')
        return

    if kind == 'topdeck_from_hand':
        rem = int(p.get('remaining', 0) or 0)
        picked = list(p.get('picked', []) or [])
        label = str(p.get('label', '') or '')
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, x in enumerate(list(gs.hand)):
            if _canon_cardno(x) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f'[ERR] topdeck_from_hand: chosen not in hand {cn}')
            return
        pick_cn = gs.hand.pop(pick_i)
        picked.append(pick_cn)
        rem -= 1

        if rem <= 0:
            gs.deck = picked + gs.deck
            gs.log.append(f'[ACT] topdeck_from_hand: placed {len(picked)} on top ({label})')
            return

        opts = list(gs.hand)
        if not opts:
            gs.deck = picked + gs.deck
            gs.log.append(f'[ACT] topdeck_from_hand: hand exhausted; placed {len(picked)} on top ({label})')
            return

        prompt = {
            'kind': 'topdeck_from_hand',
            'text': f'{label} 次にデッキ上に置くカードを選択（残り{rem}枚）',
            'options': opts,
            'remaining': rem,
            'picked': picked,
            'label': label,
        }
        try:
            gs.pending.insert(0, prompt)
        except Exception:
            gs.pending.append(prompt)
        gs.log.append(f'[PENDING] topdeck_from_hand picked {pick_cn}; remaining {rem} ({label})')
        return

    if kind == 'tsunagaru_connect_execute':
        k = int(p.get('k', 0) or 0)
        _enqueue_choose_top_keep_one(gs, k, 'ツナガルコネクト')
        return

    if kind == 'choose_top_keep_one':
        ok = _resolve_choose_top_keep_one(gs, p, choice_str, cards_db)
        if not ok:
            return
        return

    if kind == 'live_start_shizuku_bp1_003_pay':
        pos = str(p.get('pos', '') or '').upper()
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        low = str(choice_str or '').strip().lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append(f"[SKIP] {pos}: Shizuku bp1-003 live-start skipped")
            return
        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f"[ERR] Shizuku bp1-003 live-start: invalid choice {choice_str}")
            return
        if not pay_energy(gs, 1):
            gs.log.append(f"[ERR] ability: insufficient energy for [E]1 (have {gs.energy_active})")
            return
        gs.pending.insert(0, {
            'kind': 'live_start_shizuku_bp1_003_choose_color',
            'pos': pos,
            'cn': str(p.get('cn', '') or ''),
            'text': f"{pos}: 桜坂しずく ライブ開始時 → 好きなハート色を選ぶ",
            'options': ['桃', '赤', '黄', '緑', '青', '紫'],
        })
        gs.log.append(f"[PENDING] {pos}: Shizuku bp1-003 choose heart color")
        return

    if kind == 'live_start_shizuku_bp1_003_choose_color':
        pos = str(p.get('pos', '') or '').upper()
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        ch = str(choice_str or '').strip()
        m = {
            '桃': 'pink',
            '赤': 'red',
            '黄': 'yellow',
            '緑': 'green',
            '青': 'blue',
            '紫': 'purple',
            'pink': 'pink',
            'red': 'red',
            'yellow': 'yellow',
            'green': 'green',
            'blue': 'blue',
            'purple': 'purple',
        }
        col = m.get(ch, '')
        if not col:
            gs.log.append(f"[ERR] Shizuku bp1-003 choose color: invalid choice '{ch}'")
            return
        _grant_temp_heart(slot, col, 1)
        gs.log.append(f"[AUTO] {pos}: Shizuku bp1-003 -> temp heart +1 {col} (until end of live)")
        return

    if kind == 'choose_stage_member_to_activate':
        raw = str(choice_str or '').strip()
        low = raw.lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] choose_stage_member_to_activate skipped')
            return
        pos2 = raw[:1].upper() if raw else ''
        if pos2 not in ('L','C','R'):
            gs.log.append(f"[ERR] activate_member: invalid pos {choice_str}")
            return
        slot2 = gs.stage.get(pos2)
        if not slot2:
            gs.log.append(f"[ERR] activate_member: empty {pos2}")
            return
        if slot2.active:
            gs.log.append(f"[INFO] stage {pos2} already ACTIVE")
            return
        slot2.active = True
        gs.log.append(f"[ACT] stage {pos2} set ACTIVE")
        return

    if kind == 'emma_bp3_008_wait_pick':
        raw = str(choice_str or '').strip()
        pos2 = (raw[:1].upper() if raw else '')
        pos_opts = list(p.get('pos_options', []) or [])
        src_pos = str(p.get('source_pos', '') or '').upper()
        key = str(p.get('ability_key', '') or '')
        if pos2 not in ('L','C','R') or (pos_opts and pos2 not in pos_opts):
            gs.log.append(f"[ERR] Emma bp3-008: invalid target {choice_str}")
            return
        slot2 = (gs.stage or {}).get(pos2)
        if not slot2:
            gs.log.append(f"[ERR] Emma bp3-008: empty stage {pos2}")
            return
        slot2.active = False
        rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
        drew = draw(gs, 1, rng2)
        if key:
            try:
                gs.used_this_turn[key] = 1
            except Exception:
                gs.used_this_turn = {key: 1}
        gs.log.append(f"[ACT] Emma bp3-008: {pos2} set WAIT -> drew {drew}")
        return

    if kind == 'emma_bp3_008_live_start_pay':
        src_pos = str(p.get('pos', '') or '').upper()
        pos_opts = list(p.get('pos_options', []) or [])
        if choice_str.lower() not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append('[SKIP] Emma bp3-008 live-start skipped')
            return
        if len(list(getattr(gs, 'hand', []) or [])) < 2:
            gs.log.append('[ERR] Emma bp3-008 live-start: not enough cards in hand for discard 2')
            return
        opts = [_stage_pos_label(gs, cards_db, pp) for pp in pos_opts]
        resume = {
            'kind': 'emma_bp3_008_live_start_pick',
            'text': '【エマ・ヴェルデ】ライブ開始時：アクティブにする『虹ヶ咲』メンバーを選ぶ',
            'options': list(opts),
            'pos_options': list(pos_opts),
            'source_pos': src_pos,
        }
        gs.pending.append({
            'kind': 'discard_from_hand',
            'remaining': 2,
            'text': '手札を2枚控え室に置く',
            'options': list(gs.hand),
            '_resume': resume,
        })
        return

    if kind == 'emma_bp3_008_live_start_pick':
        raw = str(choice_str or '').strip()
        pos2 = (raw[:1].upper() if raw else '')
        pos_opts = list(p.get('pos_options', []) or [])
        src_pos = str(p.get('source_pos', '') or '').upper()
        if pos2 not in ('L','C','R') or (pos_opts and pos2 not in pos_opts):
            gs.log.append(f"[ERR] Emma bp3-008 live-start: invalid target {choice_str}")
            return
        src_slot = (gs.stage or {}).get(src_pos)
        slot2 = (gs.stage or {}).get(pos2)
        if not src_slot or not slot2:
            gs.log.append('[ERR] Emma bp3-008 live-start: source/target missing')
            return
        slot2.active = True
        _grant_temp_heart(src_slot, 'green', 1)
        _grant_temp_heart(slot2, 'green', 1)
        gs.log.append(f"[AUTO] Emma bp3-008 live-start: {pos2} set ACTIVE; {src_pos} and {pos2} gain green +1 until end of live")
        return


    # Generic "skip / finish early" for prompts that allow fewer picks than the max.
    # The UI can send __SKIP__ to stop selecting additional cards.
    if str(choice_str or '').strip().lower() in ("__skip__", "skip") and p.get("allow_less"):
        gs.log.append(f"[SKIP] prompt {kind}: user skipped remaining selections")
        return

    # 1) Live-start optional payment -> temp blade
    if kind == "live_start_free_effect":
        pos = str(p.get("pos", "") or "").upper()
        op_free = str(p.get("op", "") or "")
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] live_start_free_effect: stage {pos} empty")
            return
        if choice_str.lower() in ("do", "yes", "y", "1", "true"):
            if op_free == "activate_stage_member":
                wait_opts = [p2 for p2 in ('L','C','R') if gs.stage.get(p2) and not gs.stage[p2].active]
                if not wait_opts:
                    gs.log.append(f"[INFO] live_start_free_effect: no wait member to activate")
                    return
                gs.pending.append({
                    'kind': 'choose_stage_member_to_activate',
                    'text': f'{pos}: ステージのメンバーを1人までアクティブにする（対象を選択）',
                    'options': list(wait_opts),
                    'allow_less': True,
                })
                gs.log.append(f"[PENDING] {pos}: live_start activate member choice")
        else:
            gs.log.append(f"[SKIP] {pos}: live_start_free_effect ({op_free}) skipped")
        return

    if kind == "live_start_blade":
        pos = str(p.get("pos", "") or "").upper()
        need_e = _safe_int(p.get("need_e", 1), 1)
        blades = _safe_int(p.get("blades", 0), 0)
        blade_mode = str(p.get("blade_mode", "fixed") or "fixed")
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        if choice_str.lower() in ("pay", "yes", "y", "1", "true"):
            if not pay_energy(gs, need_e):
                gs.log.append(f"[ERR] ability: insufficient energy for [E]{need_e} (have {gs.energy_active})")
                return
            gain = int(blades)
            if blade_mode == "per_live_card":
                gain = int(blades) * int(len(getattr(gs, 'set_zone', []) or []))
            slot.temp_blade += gain
            slot.temp_until = "end_of_live"
            if blade_mode == "per_live_card":
                gs.log.append(f"[AUTO] {pos}: paid [E]{need_e} -> temp blade +{gain} ({blades}×LIVE{len(getattr(gs, 'set_zone', []) or [])}) (until end of live)")
            else:
                gs.log.append(f"[AUTO] {pos}: paid [E]{need_e} -> temp blade +{gain} (until end of live)")
        else:
            gs.log.append(f"[SKIP] {pos}: live-start blade ability skipped")
        return

    
    # 1b) Live-start optional payment -> generic effect template (regex engine)
    if kind == "live_start_pay_effect":
        pos = str(p.get("pos", "") or "").upper()
        need_e = _safe_int(p.get("need_e", 0), 0)
        cost_kind = str(p.get("cost_kind", "") or "")
        cost_n = _safe_int(p.get("cost_n", 0), 0)
        eff = str(p.get("effect", "") or "").strip()
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        if choice_str.lower() in ("pay", "yes", "y", "1", "true"):
            # エネルギーコスト（即時支払い）
            if need_e > 0:
                if not pay_energy(gs, need_e):
                    gs.log.append(f"[ERR] ability: insufficient energy for [E]{need_e} (have {gs.energy_active})")
                    return
            src_cn = str(p.get("cn", "") or "")
            after_ctx = {"pos": pos, "source_cn": src_cn}
            # 手札のライブカードを捨てるコスト → ユーザーに選ばせる
            if cost_kind == 'discard_live_from_hand' and cost_n > 0:
                live_in_hand = [c for c in list(gs.hand) if _is_live(_get_card(cards_db, c))]
                if len(live_in_hand) < cost_n:
                    gs.log.append(f"[ERR] live_start_pay_effect: not enough live cards in hand (need {cost_n}, have {len(live_in_hand)})")
                    return
                gs.pending.append({
                    'kind': 'discard_from_hand',
                    'remaining': cost_n,
                    'text': f'手札のライブカードを{cost_n}枚控え室に置く',
                    'options': live_in_hand,
                    'after_effect_template': eff,
                    'after_ctx': after_ctx,
                    'after_source_cn': src_cn,
                })
                return
            # 手札を捨てるコスト（汎用）→ ユーザーに選ばせる
            if cost_kind == 'discard_from_hand' and cost_n > 0:
                if len(gs.hand) < cost_n:
                    gs.log.append(f"[ERR] live_start_pay_effect: not enough cards in hand (need {cost_n})")
                    return
                gs.pending.append({
                    'kind': 'discard_from_hand',
                    'remaining': cost_n,
                    'text': f'手札を{cost_n}枚控え室に置く',
                    'options': list(gs.hand),
                    'after_effect_template': eff,
                    'after_ctx': after_ctx,
                    'after_source_cn': src_cn,
                })
                return
            # コストなし（エネルギーのみ or コストなし）→ 即時効果適用
            rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            ok = try_apply_effect_template(gs, rng, cards_db, eff, after_ctx)
            if ok:
                gs.log.append(f"[AUTO] {pos}: paid cost -> applied {eff}")
            else:
                gs.log.append(f"[WARN] {pos}: paid cost but effect not matchable: {eff}")
        else:
            gs.log.append(f"[SKIP] {pos}: live-start ability skipped")
        return


    # 1c) Live-start Rise Up High: choose 1 Nijigasaki member -> temp blade +1
    if kind == 'live_start_rise_up_high_pick':
        raw = str(choice_str or '').strip()
        pos = (raw[:1].upper() if raw else '')
        pos_opts = p.get('pos_options', None)
        if (not isinstance(pos_opts, list)) or (not pos_opts):
            pos_opts = p.get('options', []) or []
        if pos not in ('L','C','R') or (isinstance(pos_opts, list) and pos_opts and pos not in pos_opts):
            gs.log.append(f'[ERR] RiseUpHigh: invalid choice {choice_str}')
            return
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'active', False):
            gs.log.append(f'[ERR] RiseUpHigh: stage {pos} empty')
            return
        slot.temp_blade += 1
        slot.temp_until = 'end_of_live'
        gs.log.append(f'[AUTO] RiseUpHigh: {pos} temp blade +1 (until end of live)')
        return
    # 1d) Live-success Poppin' Up!: pick 1 Nijigasaki card among yell reveals -> hand (Skip allowed)
    if kind == 'pick_poppinup_from_yell':
        if choice_str.lower() == 'skip':
            gs.log.append("[SKIP] PoppinUp: skipped")
            _enqueue_next_poppin_prompt(gs)
            return
        cn = _canon_cardno(choice_str)
        opts = list(p.get('options', []) or [])
        if opts and (not any(_canon_cardno(x) == cn for x in opts)):
            gs.log.append(f"[ERR] PoppinUp: invalid choice {choice_str}")
            return
        moved = None
        # remove from resolve_zone first, then green_room
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if not isinstance(z, list):
                continue
            for i, x in enumerate(list(z)):
                if _canon_cardno(x) == cn:
                    moved = z.pop(i)
                    break
            if moved:
                break
        if not moved:
            gs.log.append(f"[ERR] PoppinUp: chosen card not found in zones {cn}")
            _enqueue_next_poppin_prompt(gs)
            return
        gs.hand.append(moved)
        # remove one occurrence from tracker
        try:
            pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
            for i, x in enumerate(list(pool)):
                if _canon_cardno(x) == cn:
                    pool.pop(i)
                    break
            setattr(gs, '_yell_revealed_this_live', pool)
        except Exception:
            pass
        gs.log.append(f"[ACT] PoppinUp: took {moved} -> hand")
        _enqueue_next_poppin_prompt(gs)
        return

    # 1e) Generic yell-retrieve: pick 1 card from yell reveals -> hand
    if kind == 'pick_from_yell':
        opts = list(p.get('options', []) or [])
        if choice_str.lower() in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] pick_from_yell: skipped')
            return
        cn = _canon_cardno(choice_str)
        if opts and not any(_canon_cardno(x) == cn for x in opts):
            gs.log.append(f'[ERR] pick_from_yell: invalid choice {choice_str}')
            return
        moved = None
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if not isinstance(z, list):
                continue
            for i, x in enumerate(list(z)):
                if _canon_cardno(x) == cn:
                    moved = z.pop(i)
                    break
            if moved:
                break
        if not moved:
            gs.log.append(f'[ERR] pick_from_yell: chosen card not found in zones {cn}')
            return
        gs.hand.append(moved)
        # remove from tracker
        try:
            pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
            for i, x in enumerate(list(pool)):
                if _canon_cardno(x) == cn:
                    pool.pop(i)
                    break
            setattr(gs, '_yell_revealed_this_live', pool)
        except Exception:
            pass
        gs.log.append(f'[ACT] pick_from_yell: took {moved} -> hand')
        return

    # 1f) live-success optional-cost pay/skip (hand discard -> retrieve_from_yell)
    if kind == 'live_success_pay_effect':
        low = str(choice_str or '').strip().lower()
        pos2 = str(p.get('pos', '') or '').upper()
        src_cn = str(p.get('source_cn', '') or '')
        eff = str(p.get('effect', '') or '')
        cost_kind = str(p.get('cost_kind', '') or '')
        cost_n = int(p.get('cost_n', 0) or 0)
        ctx2 = dict(p.get('ctx', {}) or {})
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append(f'[SKIP] {src_cn}[ライブ成功時] optional cost skipped')
            return
        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f'[ERR] live_success_pay_effect: invalid choice {choice_str}')
            return
        if cost_kind == 'discard_from_hand':
            if len(gs.hand) < cost_n:
                gs.log.append(f'[ERR] live_success_pay_effect: not enough hand cards to discard')
                return
            # enqueue discard first; after_effect_template fires when discard completes
            gs.pending.append({
                'kind': 'discard_from_hand',
                'remaining': cost_n,
                'text': f'{src_cn}[ライブ成功時] 手札を{cost_n}枚控え室に置く',
                'options': list(gs.hand),
                'after_effect_template': eff,
                'after_ctx': ctx2,
                'after_source_cn': src_cn,
            })
            gs.log.append(f'[PENDING] {src_cn}[ライブ成功時] discard {cost_n} then {eff}')
        return

# 2) Pick 1 LIVE from green room to hand
    if kind == "pick_live_from_green":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] pick live from green room")
            return
        opts = p.get("options", [])
        cn = _canon_cardno(choice_str)
        if isinstance(opts, list) and opts and cn not in opts:
            gs.log.append(f"[ERR] pick live: invalid choice {cn}")
            return
        # allow variants in green room list
        # exact match first; else try variant hit
        gr = list(gs.green_room)
        pick_cn = None
        if cn in gr:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gr:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] pick live: not in green room {cn}")
            return
        ci2 = _get_card(cards_db, pick_cn)
        if not _is_live(ci2):
            gs.log.append(f"[ERR] pick live: not a LIVE card {pick_cn}")
            return
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] took LIVE {pick_cn} from green room -> hand")
        return

    # 2b) Pick 1 MEMBER from green room to hand (sd1-006)
    if kind == "pick_member_from_green":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] pick member from green room")
            return
        opts = p.get("options", [])
        cn = _canon_cardno(choice_str)
        if isinstance(opts, list) and opts and cn not in opts:
            gs.log.append(f"[ERR] pick member: invalid choice {cn}")
            return
        gr = list(gs.green_room)
        pick_cn = None
        if cn in gr:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gr:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] pick member: not in green room {cn}")
            return
        ci2 = _get_card(cards_db, pick_cn)
        if _is_live(ci2):
            gs.log.append(f"[ERR] pick member: LIVE is not allowed {pick_cn}")
            return
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] took MEMBER {pick_cn} from green room -> hand")
        return

    # 3) Shioriko enter (PL!N-pb1-010): choose mode
    #    - energy: move 1 energy from wait -> active automatically
    #    - topdeck: choose up to 2 Nijigasaki LIVE from green room and place on deck top (order selectable)
    if kind == "choose_shioriko_enter":
        mode = choice_str.lower()
        if mode in ("energy", "e", "0", "a"):
            if gs.energy_wait > 0:
                gs.energy_wait -= 1
                gs.energy_active += 1
                gs.log.append("[AUTO] 栞子[登場]: chose ENERGY -> moved 1 (wait->active)")
            else:
                gs.log.append("[AUTO] 栞子[登場]: chose ENERGY but no wait energy")
            return
        if mode in ("topdeck", "deck", "b", "1"):
            cands: List[str] = []
            for x in list(gs.green_room):
                ci = _get_card(cards_db, x)
                if not ci:
                    continue
                if not _is_live(ci):
                    continue
                g = str(getattr(ci, "group", "") or "")
                if "虹ヶ咲" not in g:
                    continue
                cands.append(x)
            if not cands:
                gs.log.append("[AUTO] 栞子[登場]: chose TOPDECK but no Nijigasaki LIVE in green room")
                return
            gs.pending.append({
                "kind": "shioriko_topdeck_pick1",
                "text": "栞子[登場]: 控え室の『虹ヶ咲』LIVEを最大2枚デッキ上。まず1枚目（=一番上）を選ぶ / Skip可",
                "options": cands,
            })
            gs.log.append(f"[PENDING] 栞子[登場]: pick topdeck #1 from {len(cands)} candidates")
            return
        gs.log.append(f"[ERR] 栞子[登場]: invalid mode '{choice_str}'")
        return

    # 4) Shioriko topdeck pick #1
    if kind == "shioriko_topdeck_pick1":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] 栞子[登場]: topdeck 0 cards")
            return
        opts = p.get("options", [])
        cn = _canon_cardno(choice_str)
        # find actual card in green room (allow variants)
        pick_cn = None
        if cn in gs.green_room:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gs.green_room:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] 栞子[登場]: pick1 not in green room {cn}")
            return
        ci = _get_card(cards_db, pick_cn)
        if not ci or (not _is_live(ci)) or ("虹ヶ咲" not in str(ci.group or "")):
            gs.log.append(f"[ERR] 栞子[登場]: pick1 invalid (need Nijigasaki LIVE) {pick_cn}")
            return
        # remove from green and put on deck top
        gs.green_room.remove(pick_cn)
        gs.deck.insert(0, pick_cn)
        gs.log.append(f"[AUTO] 栞子[登場]: topdeck #1 -> {pick_cn}")

        # second pick (optional) from remaining candidates
        cands2: List[str] = []
        for x in list(gs.green_room):
            ci2 = _get_card(cards_db, x)
            if not ci2:
                continue
            if not _is_live(ci2):
                continue
            if "虹ヶ咲" not in str(ci2.group or ""):
                continue
            cands2.append(x)
        if not cands2:
            gs.log.append("[AUTO] 栞子[登場]: topdeck #2 none")
            return
        gs.pending.append({
            "kind": "shioriko_topdeck_pick2",
            "text": "栞子[登場]: 2枚目（=上から2枚目）を選ぶ / Skip可",
            "options": cands2,
        })
        gs.log.append(f"[PENDING] 栞子[登場]: pick topdeck #2 from {len(cands2)} candidates")
        return

    # 5) Shioriko topdeck pick #2
    if kind == "shioriko_topdeck_pick2":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] 栞子[登場]: topdeck only 1 card")
            return
        cn = _canon_cardno(choice_str)
        pick_cn = None
        if cn in gs.green_room:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gs.green_room:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] 栞子[登場]: pick2 not in green room {cn}")
            return
        ci = _get_card(cards_db, pick_cn)
        if not ci or (not _is_live(ci)) or ("虹ヶ咲" not in str(ci.group or "")):
            gs.log.append(f"[ERR] 栞子[登場]: pick2 invalid (need Nijigasaki LIVE) {pick_cn}")
            return
        gs.green_room.remove(pick_cn)
        # place as 2nd card on top: insert at index 1
        gs.deck.insert(1 if len(gs.deck) >= 1 else 0, pick_cn)
        gs.log.append(f"[AUTO] 栞子[登場]: topdeck #2 -> {pick_cn}")
        return

    if kind == 'choose_heart_color':
        pos = str(p.get('pos', '') or '').upper()
        n = int(p.get('n', 1) or 1)
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f'[SKIP] choose_heart_color: stage {pos} empty')
            return
        col = _HEART_JP_MAP.get(str(choice_str or '').strip(), '')
        if not col:
            gs.log.append(f'[ERR] choose_heart_color: invalid color {choice_str!r}')
            gs.pending.append(p)
            return
        _grant_temp_heart(slot, col, n)
        gs.log.append(f'[AUTO] {pos}: temp heart +{n} {col} (until end_of_live)')
        return

    if kind == 'choose_heart_color_for_other':
        src_pos = str(p.get('src_pos', '') or '').upper()
        cands = list(p.get('candidates', []) or [])
        n = int(p.get('n', 1) or 1)
        chosen_color = str(p.get('chosen_color', '') or '')
        if not chosen_color:
            # Step 1: choose color
            col = _HEART_JP_MAP.get(str(choice_str or '').strip(), '')
            if not col:
                gs.log.append(f'[ERR] choose_heart_color_for_other: invalid color {choice_str!r}')
                gs.pending.append(p)
                return
            if len(cands) == 1:
                slot2 = gs.stage.get(cands[0])
                if slot2:
                    _grant_temp_heart(slot2, col, n)
                    gs.log.append(f'[AUTO] {cands[0]}: temp heart +{n} {col} from {src_pos}')
                return
            # Need to pick target member next
            gs.pending.append({**p, 'chosen_color': col,
                'text': f'ハートを与えるメンバーの位置を選ぶ（{col}×{n}）',
                'options': cands})
            return
        else:
            # Step 2: choose target position
            tgt = str(choice_str or '').upper()
            if tgt not in cands:
                gs.log.append(f'[ERR] choose_heart_color_for_other: invalid target {tgt!r}')
                gs.pending.append(p)
                return
            slot2 = gs.stage.get(tgt)
            if slot2:
                _grant_temp_heart(slot2, chosen_color, n)
                gs.log.append(f'[AUTO] {tgt}: temp heart +{n} {chosen_color} from {src_pos}')
            return

    gs.log.append(f"[WARN] resolve_pending: unknown kind='{kind}' (ignored)")

    # If a deferred auto-order exists and we are now free of other prompts, resume it.
    _enqueue_auto_order_from_deferred()

def cmd_end_turn(gs: GameState, rng: random.Random) -> None:
    """End MAIN and enter the Live phase (same turn).

    Note: We do NOT advance to the next turn here. The next turn begins after
    the Live phase is fully resolved (ACK done, resolve zone empty).
    """
    if gs.pending:
        gs.log.append("[WARN] end_turn: pending prompt exists; resolve it first.")
        return
    if gs.resolve_zone:
        gs.log.append("[WARN] end_turn: resolve_zone not empty; please ACK before ending.")
        return
    if gs.phase != "MAIN":
        gs.log.append(f"[WARN] end_turn: only allowed in MAIN (phase={gs.phase})")
        return

    # Enter Live phase (set step)
    gs.phase = "LIVE_SET"
    gs.set_zone = []
    gs.live_start_prompted = False
    gs.turn_blade_bonus = 0
    gs.log.append(f"[PHASE] LIVE_SET (choose up to 3 from hand) turn={gs.turn}")


def _advance_to_next_turn(gs: GameState, rng: random.Random) -> None:
    gs.turn += 1
    begin_turn(gs, rng)


def cmd_next(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], indices: Optional[List[int]] = None) -> None:
    """Automatic progression for the current phase.

    The intended flow is:
      MAIN -> (Next/End Turn) -> LIVE_SET -> (Next) -> LIVE_CONFIRM -> (resolve live-start prompts)
      -> LIVE_PERF -> (Next) -> LIVE_ATTEMPT -> (Next) -> LIVE_RESOLVE -> (Next) -> next turn.
    """
    if indices is None:
        indices = []

    if gs.pending:
        gs.log.append("[WARN] next: pending prompt exists; resolve it first.")
        return

    if gs.phase == "MAIN":
        cmd_end_turn(gs, rng)
        return

    if gs.phase == "LIVE_SET":
        cmd_set(gs, rng, indices)
        gs.phase = "LIVE_CONFIRM"
        gs.log.append(f"[PHASE] LIVE_CONFIRM (filter set cards) turn={gs.turn}")
        return

    if gs.phase == "LIVE_CONFIRM":
        if not gs.set_zone:
            gs.log.append("[INFO] confirm: set_zone empty; skipping live.")
            gs.phase = "LIVE_RESOLVE"
            gs.log.append(f"[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}")
            return

        lives: List[str] = []
        nonlives: List[str] = []
        for cn in gs.set_zone:
            c = _get_card(cards_db, cn)
            if c and c.type == "LIVE":
                lives.append(cn)
            else:
                nonlives.append(cn)

        if nonlives:
            gs.green_room.extend(nonlives)
            gs.log.append(f"[SET] non-live {len(nonlives)} -> green room")
        gs.set_zone = lives
        # FIX_V2_17_CONFIRM_NO_LIVE_AFTER_FILTER
        # If no LIVE cards remain after filtering, skip live (no cheer/attempt).
        if not gs.set_zone:
            gs.log.append('[INFO] confirm: no LIVE after filtering; skipping live.')
            gs.phase = 'LIVE_RESOLVE'
            gs.log.append(f'[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}')
            return


        n = _enqueue_live_start_prompts(gs, cards_db)
        if n > 0:
            gs.log.append(f"[AUTO] live-start triggers queued={n}")
            return

        gs.phase = "LIVE_PERF"
        gs.log.append(f"[PHASE] LIVE_PERF (YELL) turn={gs.turn}")
        return

    if gs.phase == "LIVE_PERF":
        # FIX_V2_17_PERF_NO_LIVE_GUARD
        if not gs.set_zone:
            gs.log.append('[INFO] perf: no LIVE in set_zone; skipping cheer/attempt.')
            gs.phase = 'LIVE_RESOLVE'
            gs.log.append(f'[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}')
            return

        cmd_yell(gs, rng, cards_db)
        gs.phase = "LIVE_ATTEMPT"
        gs.log.append(f"[PHASE] LIVE_ATTEMPT (attempt) turn={gs.turn}")
        return

    if gs.phase == "LIVE_ATTEMPT":
        cmd_attempt(gs, cards_db)
        gs.phase = "LIVE_RESOLVE"
        gs.log.append(f"[PHASE] LIVE_RESOLVE (ACK + next turn) turn={gs.turn}")
        return

    if gs.phase == "LIVE_RESOLVE":
        # Treat Next as the confirm/cleanup step (8.4 timing).
        # 1) Run <ライブ成功時> triggers (8.4.4)
        if bool(getattr(gs, 'need_live_success_triggers', False)):
            gs.need_live_success_triggers = False
            if bool(getattr(gs, 'last_attempt_ok', False)) and list(getattr(gs, 'last_attempt_lives', []) or []):
                lives = list(getattr(gs, 'last_attempt_lives', []) or [])
                _run_live_success_triggers(gs, rng, cards_db, lives)
                if (not gs.pending) and _enqueue_next_poppin_prompt(gs):
                    return
                if gs.pending:
                    return

        # 2) Winner-based success storage decision (8.4.7).
        #    Since this simulator has no opponent, we let the user decide whether to store
        #    a successful LIVE into 成功ライブカード置き場 (skip allowed).
        if bool(getattr(gs, 'need_success_store_choice', False)):
            if bool(getattr(gs, 'last_attempt_ok', False)) and list(getattr(gs, 'last_attempt_lives', []) or []):
                lives = list(getattr(gs, 'last_attempt_lives', []) or [])
                gs.pending.append({
                    'kind': 'pick_success_to_store',
                    'text': '成功ライブカード置き場に置くカードを選択（Skip可）',
                    # candidates are LIVE cardnumbers (skip is a separate action)
                    'options': list(lives),
                    'lives': list(lives),
                })
                gs.need_success_store_choice = False
                gs.log.append(f"[PENDING] success store choice ({len(lives)} lives)")
                return
            gs.need_success_store_choice = False

        # 3) ACK revealed cards (resolve zone)
        if gs.resolve_zone:
            cmd_ack(gs, rng)
        if gs.resolve_zone:
            gs.log.append("[WARN] next: resolve_zone still not empty after ACK; abort.")
            return

        # Defensive cleanup if success-store prompt was skipped by older saves
        if bool(getattr(gs, 'last_attempt_ok', False)) and list(getattr(gs, 'last_attempt_lives', []) or []):
            _clear_end_of_live_buffs(gs)
            gs.live_start_prompted = False

        # Clear per-live cheer reveal tracker
        try:
            setattr(gs, '_yell_revealed_this_live', [])
        except Exception:
            pass

        # Clear last-attempt helpers
        gs.last_attempt_lives = []
        gs.last_attempt_ok = False

        _advance_to_next_turn(gs, rng)
        return

    gs.log.append(f"[WARN] next: unknown phase={gs.phase}")

