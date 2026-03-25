# -*- coding: utf-8 -*-
# BUILD_TAG: yell_retrieve_heart_replace_20260325
from __future__ import annotations

"""llocg_ui.engine_effects

エフェクトルール定義と適用処理。
新しい effect op を追加するときはこのファイルだけ編集すればよい。

依存: engine_base のみ（循環インポートなし）
"""

import re
import random
from typing import Any, Dict, List, Optional

from .db import CardInfo, _get_card
from .engine_base import (
    ENERGY_TOTAL_DEFAULT,
    _canon_cardno, _cardno_variants,
    _parse_energy_cost, _cost_requires_self_to_green,
    _count_blade_icons_from_tagblob,
    _is_live_ci, _is_member_ci,
    _green_candidates,
    draw,
    _energy_remaining_in_deck,
    _enqueue_discard_from_hand,
    _enqueue_choose_from_green,
    _enqueue_topdeck_from_green,
    _enqueue_choose_from_topk,
    _enqueue_choose_from_topk_filtered,
    _enqueue_look_top_3way_split,
    _enqueue_reorder_from_topk_keep_any,
    _grant_temp_heart,
    _clamp_energy_zone,
    GameState, StageSlot,
)

_EFFECT_RULES = [
    {"id": "draw_n", "pattern": r"^カードを(?P<n>\d+)枚引く。$", "op": "draw"},
    {"id": "draw_n_discard_m", "pattern": r"^カードを(?P<n>\d+)枚引き、手札を(?P<m>\d+)枚控え室に置く。$", "op": "draw_then_discard"},
    {"id": "discard_hand_n", "pattern": r"^手札を(?P<n>\d+)枚控え室に置く。$", "op": "discard_from_hand"},
    {"id": "retrieve_waiting_live_n", "pattern": r"^自分の控え室からライブカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "LIVE"},
    {"id": "retrieve_waiting_member_n", "pattern": r"^自分の控え室からメンバーカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "MEMBER"},
    {"id": "retrieve_waiting_live_group_n", "pattern": r"^自分の控え室から『(?P<group>[^』]+)』のライブカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "LIVE"},
    {"id": "look_top_k_choose_1_rest_waiting", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から1枚を手札に加え、残りを控え室に置く。$", "op": "look_top_choose"},
        {"id": "look_top_k_reorder_keep_any_rest_waiting", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。$", "op": "look_top_reorder_keep_any"},
    {"id": "topdeck_green_any_upto1", "pattern": r"^自分の控え室からカードを1枚までデッキの一番上に置く。$", "op": "topdeck_from_green", "card_kind": "ANY", "allow_less": True},
    {"id": "topdeck_green_member_n", "pattern": r"^自分の控え室にあるメンバーカード(?P<n>\d+)枚を好きな順番でデッキの一番上に置く。$", "op": "topdeck_from_green", "card_kind": "MEMBER", "allow_less": False},
    {"id": "topdeck_green_live_group_upto_n", "pattern": r"^自分の控え室にある『(?P<group>[^』]+)』のライブカードを(?P<n>\d+)枚まで好きな順番でデッキの上に置く。$", "op": "topdeck_from_green", "card_kind": "LIVE", "allow_less": True},
    {"id": "energy_put_wait_n", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。$", "op": "energy_put_wait"},
    {"id": "energy_activate_n", "pattern": r"^エネルギーを(?P<n>\d+)枚アクティブにする。$", "op": "energy_activate"},
    {"id": "gain_blade_until_end_live", "pattern": r"^ライブ終了時まで、(?P<blades>(?:<\(ブレード\)>)+)を得る。$", "op": "gain_blade_until_end_live"},
    {"id": "activate_stage_member_upto1", "pattern": r"^自分のステージにいるメンバーを1人までアクティブにする。$", "op": "activate_stage_member"},
    # Fixed-color hearts (and mixed hearts+blades): e.g. "ライブ終了時まで、<(黄)><(黄)>を得る。"
    # Must come AFTER gain_blade_until_end_live so pure-blade still matches first.
    {"id": "gain_icons_until_end_live", "pattern": r"^ライブ終了時まで、(?P<icons>(?:<\([^)]+\)>)+)を得る。$", "op": "gain_icons_until_end_live"},
    # Free heart choice (self): "好きなハートの色を1つ指定する。ライブ終了時まで、そのハートを1つ得る。"
    {"id": "choose_heart_gain_self", "pattern": r"^好きなハートの色を1つ指定する。ライブ終了時まで、そのハートを1つ得る。$", "op": "choose_heart_gain_self"},
    # Free heart choice (other group member)
    {"id": "choose_heart_gain_other_member", "pattern": r"^好きなハートの色を1つ指定する。ライブ終了時まで、自分のステージにいるこのメンバー以外の『(?P<group>[^』]+)』のメンバー1人は、そのハートを1つ得る。$", "op": "choose_heart_gain_other_member"},
    # Activate all stage members
    {"id": "activate_all_stage_members", "pattern": r"^自分のステージにいるすべてのメンバーをアクティブにする。$", "op": "activate_all_stage_members"},
    # Energy activate up to n
    {"id": "energy_activate_upto_n", "pattern": r"^エネルギーを(?P<n>\d+)枚までアクティブにする。$", "op": "energy_activate_upto"},
    # Conditional draw
    {"id": "draw_if_energy_gte", "pattern": r"^自分のエネルギーが(?P<n>\d+)枚以上ある場合、カードを1枚引く。$", "op": "draw_if", "cond": "energy_gte"},
    {"id": "draw_if_stage_cost_gte", "pattern": r"^自分のステージにコスト(?P<n>\d+)以上のメンバーがいる場合、カードを1枚引く。$", "op": "draw_if", "cond": "stage_member_cost_gte"},
    {"id": "draw_if_success_nonempty", "pattern": r"^自分の成功ライブカード置き場にカードがある場合、カードを1枚引く。$", "op": "draw_if", "cond": "success_nonempty"},
    {"id": "draw_if_green_size_gte", "pattern": r"^自分の控え室にカードが(?P<n>\d+)枚以上ある場合、カードを1枚引く。$", "op": "draw_if", "cond": "green_size_gte"},
    # Self-wait (as effect): "このメンバーをウェイトにする。"
    {"id": "set_self_wait_member", "pattern": r"^このメンバーをウェイトにする。$", "op": "set_self_wait"},
    # Opponent wait: "相手のステージにいるコストN以下のメンバーをM人までウェイトにする。"
    {"id": "set_opponent_wait_upto_n", "pattern": r"^相手のステージにいるコスト(?P<cost>\d+)以下のメンバーを(?P<max_n>\d+)人までウェイト(?:状態に)?にする。$", "op": "set_opponent_wait"},
    # Opponent wait all: "相手のステージにいるすべてのコストN以下のメンバーをウェイトにする。"
    {"id": "set_opponent_wait_all_cost", "pattern": r"^相手のステージにいるすべてのコスト(?P<cost>\d+)以下のメンバーをウェイトにする。$", "op": "set_opponent_wait"},
    # Opponent self-choice wait
    {"id": "set_opponent_wait_self_choice", "pattern": r"^相手は、?自身のステージにいるアクティブ状態のメンバー1人をウェイトにする。$", "op": "set_opponent_wait_self_choice"},
    # look_top with optional pick + type/group filter
    # e.g. "デッキ上5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残り控え室"
    {"id": "look_top_k_optional_type", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から(?P<kind>ライブ|メンバー)カードを1枚(?:まで)?公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # with group filter: "その中から『G』のカードを1枚公開して手札に加えてもよい"
    {"id": "look_top_k_optional_group", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から『(?P<group>[^』]+)』のカードを1枚(?:まで)?公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # with group+type: "その中から『G』のライブカードを1枚公開して..."
    {"id": "look_top_k_optional_group_type", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から『(?P<group>[^』]+)』の(?P<kind>ライブ|メンバー)カードを1枚(?:まで)?公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # with name filter: "その中から「名前A」か「名前B」のメンバーカードを1枚公開して..."
    {"id": "look_top_k_optional_names_type", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から(?P<names>(?:「[^」]+」(?:か「[^」]+」)*)の)?(?P<kind>ライブ|メンバー)カードを1枚公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # 3-way split: 1->hand, 1->deck top, 1->green
    {"id": "look_top_3_split", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から1枚を手札に加え、1枚をデッキの上に置き、1枚を控え室に置く。$", "op": "look_top_3way_split"},
    # Retrieve from yell reveals: group-filtered
    {"id": "retrieve_yell_group_any", "pattern": r"^エールにより公開された自分のカードの中から、『(?P<group>[^』]+)』のカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "ANY"},
    # Retrieve from yell reveals: type-filtered (LIVE or MEMBER)
    {"id": "retrieve_yell_live", "pattern": r"^エールにより公開された自分のカードの中から、ライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "LIVE"},
    {"id": "retrieve_yell_member", "pattern": r"^エールにより公開された自分のカードの中から、メンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "MEMBER"},
    # Retrieve from yell reveals: group+type (e.g. 『μ's』のメンバーカード)
    {"id": "retrieve_yell_group_member", "pattern": r"^エールにより公開された自分のカードの中から、『(?P<group>[^』]+)』のメンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "MEMBER"},
    {"id": "retrieve_yell_group_live", "pattern": r"^エールにより公開された自分のカードの中から、『(?P<group>[^』]+)』のライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "LIVE"},
    # Retrieve from yell reveals: cost2-member OR score2-live (e.g. PL!HS-PR-027, PL!N-PR-021, PL!SP-PR-016)
    {"id": "retrieve_yell_cost2member_or_score2live", "pattern": r"^エールにより公開された自分のカードの中から、コスト(?P<cost_lim>\d+)以下のメンバーカードか、スコア(?P<score_lim>\d+)以下のライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "COST_MEMBER_OR_SCORE_LIVE"},
]

_EFFECT_RULES_COMPILED = [{**r, "re": re.compile(r["pattern"])} for r in _EFFECT_RULES]

_HEART_ICON_COLOR_MAP = {
    '桃': 'pink', '赤': 'red', '黄': 'yellow',
    '緑': 'green', '青': 'blue', '紫': 'purple',
}
_HEART_JP_MAP = {
    '桃': 'pink', '赤': 'red', '黄': 'yellow',
    '緑': 'green', '青': 'blue', '紫': 'purple',
    'pink': 'pink', 'red': 'red', 'yellow': 'yellow',
    'green': 'green', 'blue': 'blue', 'purple': 'purple',
}

def _parse_heart_icons(icon_blob: str) -> Dict[str, int]:
    """Parse <(色)> icon string into color -> count dict (excluding blades)."""
    counts: Dict[str, int] = {}
    for m in re.finditer(r'<\(([^)]+)\)>', str(icon_blob or '')):
        jp = m.group(1)
        col = _HEART_ICON_COLOR_MAP.get(jp)
        if col:
            counts[col] = counts.get(col, 0) + 1
    return counts


def _match_effect_template(effect_text: str):
    s = (effect_text or "").strip()
    if not s:
        return None
    for r in _EFFECT_RULES_COMPILED:
        m = r["re"].match(s)
        if m:
            gd = {k: v for k, v in m.groupdict().items() if v is not None}
            return (r, gd)
    return None


def _apply_effect_by_rule(gs: 'GameState', rng: random.Random, cards_db: Dict[str, CardInfo], rule: Dict[str, Any], gd: Dict[str, str], ctx: Dict[str, Any]) -> None:
    op = rule.get('op')

    if op == 'draw':
        n = int(gd.get('n', 0) or 0)
        got = draw(gs, n, rng)
        gs.log.append(f'[AUTO] draw {n} -> drew {got}')
        return

    if op == 'draw_then_discard':
        n = int(gd.get('n', 0) or 0)
        m = int(gd.get('m', 0) or 0)
        got = draw(gs, n, rng)
        gs.log.append(f'[AUTO] draw {n} -> drew {got}; then discard {m}')
        _enqueue_discard_from_hand(gs, m)
        return

    if op == 'discard_from_hand':
        n = int(gd.get('n', 0) or 0)
        _enqueue_discard_from_hand(gs, n)
        return

    if op == 'retrieve_from_waiting_room':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        n = int(gd.get('n', 1) or 1)
        group = str(gd.get('group', '') or '')
        if kind not in ('LIVE','MEMBER'):
            gs.log.append('[WARN] retrieve: unsupported kind')
            return
        _enqueue_choose_from_green(gs, cards_db, kind=kind, n=n, group=group)
        return


    if op == 'topdeck_from_green':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        n = int(gd.get('n', 1) or 1)
        group = str(gd.get('group', '') or '')
        allow_less = bool(rule.get('allow_less', False))
        if kind not in ('LIVE','MEMBER','ANY'):
            gs.log.append('[WARN] topdeck: unsupported kind')
            return
        _enqueue_topdeck_from_green(gs, cards_db, kind=kind, n=n, group=group, allow_less=allow_less)
        return



    if op == 'look_top_choose':
        k = int(gd.get('k', 0) or 0)
        _enqueue_choose_from_topk(gs, k, rng)
        return

    if op == 'look_top_choose_filtered':
        k = int(gd.get('k', 0) or 0)
        kind_jp = str(gd.get('kind', '') or '')
        kind = {'ライブ': 'LIVE', 'メンバー': 'MEMBER'}.get(kind_jp, '')
        group = str(gd.get('group', '') or rule.get('group', '') or '')
        optional = bool(rule.get('optional', False))
        # parse names like 「名前A」か「名前B」
        names_raw = str(gd.get('names', '') or '')
        names = re.findall(r'「([^」]+)」', names_raw) if names_raw else []
        _enqueue_choose_from_topk_filtered(gs, k, rng, cards_db,
                                           filter_kind=kind, filter_group=group,
                                           filter_names=names, optional=optional)
        return

    if op == 'look_top_3way_split':
        k = int(gd.get('k', 0) or 0)
        _enqueue_look_top_3way_split(gs, k, rng)
        return
    if op == 'look_top_reorder_keep_any':
        k = int(gd.get('k', 0) or 0)
        _enqueue_reorder_from_topk_keep_any(gs, k, rng)
        return


    if op == 'energy_put_wait':
        n = int(gd.get('n', 1) or 1)
        n = max(0, n)
        rem = _energy_remaining_in_deck(gs)
        add = min(n, rem)
        if add > 0:
            gs.energy_wait += add
            _clamp_energy_zone(gs)
        gs.log.append(f"[AUTO] energy_put_wait +{add}{' (clipped)' if add<n else ''} (wait={gs.energy_wait})")
        return

    if op == 'energy_activate':
        n = int(gd.get('n', 0) or 0)
        take = min(max(0, n), int(gs.energy_wait or 0))
        gs.energy_wait -= take
        gs.energy_active += take
        gs.log.append(f'[AUTO] energy_activate {n} -> moved {take} (active={gs.energy_active} wait={gs.energy_wait})')
        return

    if op == 'gain_blade_until_end_live':
        blades_blob = gd.get('blades', '')
        b = _count_blade_icons_from_tagblob(blades_blob)
        pos = str(ctx.get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L','C','R') else None
        if not slot:
            gs.log.append('[WARN] gain_blade: no source slot')
            return
        slot.temp_blade += int(b)
        slot.temp_until = 'end_of_live'
        gs.log.append(f'[AUTO] {pos}: gain blade +{b} (until end_of_live)')
        return

    if op == 'activate_stage_member':
        opts = [p for p in ('L','C','R') if gs.stage.get(p)]
        if not opts:
            gs.log.append('[INFO] activate_member: no member on stage')
            return
        gs.pending.append({
            'kind': 'choose_stage_member_to_activate',
            'text': 'ステージのメンバーを1人までアクティブにする（対象を選択）',
            'options': opts,
        })
        gs.log.append('[PENDING] choose stage member to activate')
        return

    if op == 'gain_icons_until_end_live':
        icons_blob = str(gd.get('icons', '') or '')
        pos = str(ctx.get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] gain_icons: no source slot')
            return
        b = _count_blade_icons_from_tagblob(icons_blob)
        if b > 0:
            slot.temp_blade += b
            slot.temp_until = 'end_of_live'
        heart_counts = _parse_heart_icons(icons_blob)
        for col, cnt in heart_counts.items():
            _grant_temp_heart(slot, col, cnt)
        gs.log.append(f'[AUTO] {pos}: gain icons {icons_blob} (until end_of_live; blades={b} hearts={heart_counts})')
        return

    if op == 'choose_heart_gain_self':
        pos = str(ctx.get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] choose_heart_gain_self: no source slot')
            return
        src = str(ctx.get('source_cn', '') or pos)
        gs.pending.append({
            'kind': 'choose_heart_color',
            'target': 'self',
            'pos': pos,
            'n': 1,
            'text': f'{src}: 好きなハートの色を1つ指定する → ライブ終了時まで+1',
            'options': ['桃', '赤', '黄', '緑', '青', '紫'],
        })
        gs.log.append(f'[PENDING] {pos}: choose heart color (self)')
        return

    if op == 'choose_heart_gain_other_member':
        pos = str(ctx.get('pos', '') or '').upper()
        group = str(gd.get('group', '') or '')
        src = str(ctx.get('source_cn', '') or pos)
        cands = []
        for p2 in ('L', 'C', 'R'):
            if p2 == pos:
                continue
            slot2 = gs.stage.get(p2)
            if not slot2:
                continue
            if group:
                ci2 = _get_card(cards_db, slot2.cardnumber)
                if not ci2 or group not in str(getattr(ci2, 'group', '') or ''):
                    continue
            cands.append(p2)
        if not cands:
            gs.log.append(f'[INFO] choose_heart_gain_other_member: no valid {group} target')
            return
        gs.pending.append({
            'kind': 'choose_heart_color_for_other',
            'src_pos': pos,
            'candidates': cands,
            'group': group,
            'n': 1,
            'chosen_color': '',
            'text': f'{src}: 好きなハートの色を1つ指定する → ステージの{group}メンバー1人に+1',
            'options': ['桃', '赤', '黄', '緑', '青', '紫'],
        })
        gs.log.append(f'[PENDING] {pos}: choose heart color for other {group} member')
        return

    if op == 'activate_all_stage_members':
        activated = []
        for p2 in ('L', 'C', 'R'):
            slot2 = gs.stage.get(p2)
            if slot2 and not slot2.active:
                slot2.active = True
                activated.append(p2)
        gs.log.append(f'[AUTO] activate all stage members: {activated if activated else "none (already active)"}')
        return

    if op == 'energy_activate_upto':
        n = int(gd.get('n', 0) or 0)
        actual = min(n, int(gs.energy_wait or 0))
        if actual > 0:
            gs.energy_wait -= actual
            gs.energy_active += actual
        gs.log.append(f'[AUTO] energy activate up to {n}: activated {actual} (wait={gs.energy_wait} active={gs.energy_active})')
        return

    if op == 'set_self_wait':
        pos2 = str((ctx or {}).get('pos', '') or '').upper()
        slot2 = gs.stage.get(pos2) if pos2 in ('L', 'C', 'R') else None
        if slot2:
            slot2.active = False
            gs.log.append(f'[AUTO] {pos2}: {slot2.cardnumber} -> WAIT')
        else:
            gs.log.append(f'[WARN] set_self_wait: no member at pos={pos2}')
        return

    if op == 'set_opponent_wait':
        cost_lim = int(gd.get('cost', 99) or 99)
        max_n = int(gd.get('max_n', gd.get('n', 1)) or 1)
        gs.log.append(f'[MANUAL] 相手のステージにいるコスト{cost_lim}以下のメンバーを{max_n}人までウェイトにする（手動で処理してください）')
        return

    if op == 'set_opponent_wait_self_choice':
        gs.log.append('[MANUAL] 相手は自身のステージのアクティブメンバー1人をウェイトにする（手動で処理してください）')
        return

    if op == 'retrieve_from_yell':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        group = str(gd.get('group', '') or '')
        cost_lim = int(gd.get('cost_lim', 99) or 99)
        score_lim = int(gd.get('score_lim', 99) or 99)
        src = str((ctx or {}).get('source_cn', '') or '')
        pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
        # collect candidates from resolve_zone first, then green_room (already sent there by ack)
        cands: List[str] = []
        seen: set = set()
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if not isinstance(z, list):
                continue
            for cn2 in z:
                canon2 = _canon_cardno(str(cn2 or ''))
                if canon2 in seen:
                    continue
                # only consider cards that were part of yell reveals this live
                if canon2 not in [_canon_cardno(x) for x in pool]:
                    continue
                ci2 = _get_card(cards_db, cn2)
                if not ci2:
                    continue
                if kind == 'LIVE' and not _is_live_ci(ci2):
                    continue
                if kind == 'MEMBER' and not _is_member_ci(ci2):
                    continue
                if kind == 'COST_MEMBER_OR_SCORE_LIVE':
                    ok2 = False
                    if _is_member_ci(ci2) and int(getattr(ci2, 'cost', 0) or 0) <= cost_lim:
                        ok2 = True
                    if _is_live_ci(ci2) and int(getattr(ci2, 'score', 0) or 0) <= score_lim:
                        ok2 = True
                    if not ok2:
                        continue
                if group and (group not in str(getattr(ci2, 'group', '') or '')):
                    continue
                seen.add(canon2)
                cands.append(cn2)
        if not cands:
            gs.log.append(f'[INFO] retrieve_from_yell: no matching card in yell reveals (kind={kind} group={group})')
            return
        label = f'{src}[ライブ成功時]: エールで公開されたカードから1枚手札に加える'
        if kind == 'LIVE':
            label += '（ライブカード）'
        elif kind == 'MEMBER':
            label += '（メンバーカード）'
        elif kind == 'COST_MEMBER_OR_SCORE_LIVE':
            label += f'（コスト{cost_lim}以下のメンバーかスコア{score_lim}以下のライブ）'
        if group:
            label += f'（{group}）'
        gs.pending.append({
            'kind': 'pick_from_yell',
            'text': label,
            'options': list(cands),
            'source_cn': src,
        })
        gs.log.append(f'[PENDING] retrieve_from_yell: {len(cands)} candidates')
        return

    if op == 'draw_if':
        cond = str(rule.get('cond', '') or '')
        n = int(gd.get('n', 0) or 0)
        group = str(gd.get('group', '') or rule.get('group', '') or '')
        name = str(gd.get('name', '') or rule.get('name', '') or '')
        met = False
        if cond == 'energy_gte':
            met = (int(gs.energy_active or 0) + int(gs.energy_wait or 0)) >= n
        elif cond == 'stage_member_cost_gte':
            for slot in gs.stage.values():
                if slot:
                    ci2 = _get_card(cards_db, slot.cardnumber)
                    if ci2 and int(getattr(ci2, 'cost', 0) or 0) >= n:
                        met = True; break
        elif cond == 'success_nonempty':
            met = len(gs.success_pile) > 0
        elif cond == 'green_size_gte':
            met = len(gs.green_room) >= n
        elif cond == 'stage_has_other_group_member':
            trigger_cn = str(getattr(gs, '_trigger_cn', '') or '')
            for slot in gs.stage.values():
                if slot and slot.cardnumber != trigger_cn:
                    ci2 = _get_card(cards_db, slot.cardnumber)
                    if ci2 and group and group in str(getattr(ci2, 'group', '') or ''):
                        met = True; break
        elif cond == 'stage_has_named_member':
            for slot in gs.stage.values():
                if slot:
                    ci2 = _get_card(cards_db, slot.cardnumber)
                    if ci2 and name and name in str(getattr(ci2, 'name', '') or ''):
                        met = True; break
        if met:
            drew = draw(gs, 1, rng)
            gs.log.append(f'[AUTO] draw_if ({cond}): condition met -> drew {drew}')
        else:
            gs.log.append(f'[AUTO] draw_if ({cond}): condition not met -> skip')
        return

    gs.log.append(f"[WARN] effect op not implemented: {op}")


def try_apply_effect_template(gs: 'GameState', rng: random.Random, cards_db: Dict[str, CardInfo], effect_text: str, ctx: Dict[str, Any]) -> bool:
    """Apply an effect_template using the embedded regex rules.

    Also supports a small subset of "mode/choice" wrappers used by key cards.
    """
    text = str(effect_text or '').strip()
    if not text:
        return False

    # Mode wrapper: choose one / choose one or more (Daydream Mermaid etc.)
    # Example:
    #   以下から1つを選ぶ。自分の成功ライブカード置き場に『虹ヶ咲』のカードがある場合、代わりに1つ以上を選ぶ。
    #   ・A...
    #   ・B...
    if ('以下から' in text) and ('選ぶ' in text) and ('・' in text):
        opts: List[str] = []
        for ln in text.splitlines():
            ln = str(ln).strip()
            if ln.startswith('・'):
                opts.append(ln[1:].strip())
        if opts:
            # default: exactly 1
            max_pick = 1
            # conditional: if success live storage has group X, allow 1+ selections
            mcond = re.search(r"成功ライブカード置き場に『(?P<g>[^』]+)』のカードがある場合、代わりに1つ以上を選ぶ。", text)
            if mcond:
                g = str(mcond.group('g') or '').strip()
                if g and _success_has_group(gs, cards_db, g):
                    max_pick = len(opts)

            # Prepare prompt
            src = str((ctx or {}).get('source_cn', '') or '')
            ttl = src if src else '効果'
            if max_pick > 1:
                msg = f'{ttl}: 以下から1つ以上を選ぶ'
            else:
                msg = f'{ttl}: 以下から1つを選ぶ'

            options = list(opts)
            # Add a finish button only when multiple picks are allowed
            if max_pick > 1:
                options.append('Done')

            gs.pending.append({
                'kind': 'choose_effects',
                'text': msg,
                'options': options,
                'remaining': list(opts),
                'picked': [],
                'min': 1,
                'max': int(max_pick),
                'ctx': dict(ctx or {}),
            })
            gs.log.append(f'[PENDING] choose_effects: {ttl} opts={len(opts)} max={max_pick}')
            return True

    # Plain regex rule
    m = _match_effect_template(text)
    if not m:
        return False
    rule, gd = m
    _apply_effect_by_rule(gs, rng, cards_db, rule, gd, ctx)
    return True


def _enqueue_choose_effects_from_ability(gs: 'GameState', cards_db: Dict[str, CardInfo], ab: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    """Handle 'mode' style abilities where the choice header and options are split across clauses.

    Typical pattern (Daydream Mermaid etc.):
      clause0: '以下から1つを選ぶ。...代わりに1つ以上を選ぶ。'
      clause1+: individual option effects (as separate clauses)
    """
    try:
        clauses = ab.get('clauses', [])
    except Exception:
        clauses = []
    if not isinstance(clauses, list) or not clauses:
        return False

    # Find the first 'choose' header clause
    header_i = None
    header_text = ''
    for i, cl in enumerate(clauses):
        if not isinstance(cl, dict):
            continue
        eff0 = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
        if ('以下から' in eff0) and ('選ぶ' in eff0):
            header_i = i
            header_text = eff0
            break
    if header_i is None:
        return False

    # Collect option effect texts from subsequent clauses
    opts: List[str] = []
    for cl in clauses[header_i+1:]:
        if not isinstance(cl, dict):
            continue
        eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
        if not eff:
            continue
        # ignore bullet prefix if any remained
        if eff.startswith('・'):
            eff = eff[1:].strip()
        if eff:
            opts.append(eff)

    if not opts:
        return False

    # Determine selection range
    max_pick = 1
    mcond = re.search(r"成功ライブカード置き場に『(?P<g>[^』]+)』のカードがある場合、代わりに1つ以上を選ぶ。", header_text)
    if mcond:
        g = str(mcond.group('g') or '').strip()
        if g and _success_has_group(gs, cards_db, g):
            max_pick = len(opts)

    src = str((ctx or {}).get('source_cn', '') or '')
    ttl = src if src else '効果'
    msg = f"{ttl}: 以下から{'1つ以上' if max_pick>1 else '1つ'}を選ぶ"

    options = list(opts)
    if max_pick > 1:
        options.append('Done')

    gs.pending.append({
        'kind': 'choose_effects',
        'text': msg,
        'options': options,
        'remaining': list(opts),
        'picked': [],
        'min': 1,
        'max': int(max_pick),
        'ctx': dict(ctx or {}),
    })
    gs.log.append(f"[PENDING] choose_effects: {ttl} opts={len(opts)} max={max_pick}")
    return True


