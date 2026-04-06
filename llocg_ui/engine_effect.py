# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_group2_single_target_20260403f
from __future__ import annotations

"""llocg_ui.engine_effect

Claude向けの軽量効果拡張ファイル。

目的
----
- 現 runtime の正本は engine.py のまま維持する。
- 日常の新規効果実装は、できるだけこの小さいファイルだけで完結させる。
- server.py は .engine しか import しないため、engine.py 側 API は壊さない。

運用原則
--------
1. まずこのファイルだけを Claude に渡す。
2. handout / prompt も併せて渡すが、コード変更対象は原則このファイルのみ。
3. engine.py を編集するのは次の場合だけ:
   - 新しい pending kind を engine.py 側で UI/解決対応まで増やす必要がある。
   - 既存 helper / cmd / phase 遷移では表現できない。
   - 新しい dataclass field や state_json 契約の追加が必要。
4. UI の一時ブレード/ハート表示は StageSlot.temp_blade / temp_hearts が基本契約。
5. このファイルは engine.py を import しないこと。循環 import 防止のため、
   engine.py から globals() が渡される。

engine.py 側接続点
------------------
- _match_effect_template() の先頭で try_match_effect_template_ext() を呼ぶ。
- _apply_effect_by_rule() の先頭で try_apply_effect_by_rule_ext() を呼ぶ。
- このファイルは「拡張ルールがヒットした時だけ処理する」。
- 未対応なら None / False を返し、engine.py の既存巨大実装へフォールバックする。

Claude に渡す 3 点
------------------
- engine_effect.py   : このファイル（コード本体）
- handout            : runtime truth / UI 契約 / debug ルール / 対象カード最小DB
- prompt             : 今回の effect_template / 禁止事項 / 出力形式

最小 API 契約
-------------
try_match_effect_template_ext(eng, effect_text) -> Optional[(rule_dict, gd_dict)]
    - eng は engine.py の globals() dict
    - マッチしたら (rule, groupdict) を返す
    - 未対応なら None

try_apply_effect_by_rule_ext(eng, gs, rng, cards_db, rule, gd, ctx) -> bool
    - 自分の拡張ルールなら処理して True
    - 未対応なら False

実装方針
--------
- effect_template は exact match を第一選択にする。
  理由: 既存 regex 群と衝突しにくく、Claude 作業でも安全。
- 必要になった時だけ regex を使う。
- rule dict は最小限のキーだけ持つ:
    {"id": ..., "op": "__ext__", "ext_key": ...}
- helper はこのファイル内に小さく置く。共通化しすぎない。
- engine.py の既存 helper は eng["helper_name"] で使う。

注意
----
- このファイルに handout 相当の要点を残しておくが、長文化しすぎない。
- 対象カードの詳細 DB は handout 側に置く。ここには常設しない。
- 既存 UI 契約:
    slot.temp_blade: int
    slot.temp_hearts: {pink/red/yellow/green/blue/purple/all: int}
  を守る。
"""

from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Extension rule table
# ---------------------------------------------------------------------------
# 通常の新規効果実装はここへ追加する。
# 形式:
#   {
#       "id": "human_readable_id",
#       "effect_template": "完全一致で扱う effect_template",
#       "ext_key": "dispatch key",
#   }
EXTRA_EFFECT_RULES = [
    # 既存
    {
        "id": "position_change_optional",
        "effect_template": "このメンバーをポジションチェンジしてもよい。",
        "ext_key": "position_change_optional",
    },
    # Prompt 17: PL!-bp3-006 西木野真姫 (ライブ開始時)
    {
        "id": "live_start_success_zone_count_x2_blade",
        "effect_template": "ライブ終了時まで、自分の成功ライブカード置き場にあるカード1枚につき、<(ブレード)><(ブレード)>を得る。",
        "ext_key": "live_start_success_zone_count_x2_blade",
    },
    # Prompt 24: PL!-bp4-001 高坂穂乃果 (ライブ開始時)
    {
        "id": "live_start_my_cost_lower_draw1",
        "effect_template": "自分ステージにいるメンバーのコストの合計が相手より低い場合、カードを1枚引く。",
        "ext_key": "live_start_my_cost_lower_draw1",
    },
    # Prompt 26: PL!-bp4-004 園田海未 (登場)
    {
        "id": "enter_success_score_ge6_activate2",
        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が6以上の場合、エネルギーを2枚アクティブにする。",
        "ext_key": "enter_success_score_ge6_activate2",
    },
    # Prompt 31: PL!-bp4-016 東條希 (登場)
    {
        "id": "enter_success_score_ge3_draw1",
        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が3以上の場合、カードを1枚引く。",
        "ext_key": "enter_success_score_ge3_draw1",
    },
    # Prompt 41: PL!-pb1-003 南ことり (登場) ※コストはエンジン側が pay_or_skip を積む想定
    {
        "id": "enter_printemps_count_activate_energy",
        "effect_template": "自分のステージにいる『Printemps』のメンバー1人につき、エネルギーを1枚アクティブにする。",
        "ext_key": "enter_printemps_count_activate_energy",
    },
    # Prompt 57: PL!-pb1-032 SENTIMENTAL StepS (ライブ成功時)
    {
        "id": "live_success_success_zone_has_mus_draw1",
        "effect_template": "自分の成功ライブカード置き場に『μ's』のカードがある場合、カードを1枚引く。",
        "ext_key": "live_success_success_zone_has_mus_draw1",
    },
    # Prompt 63: PL!-sd1-008 小泉花陽 (BODY 起動)
    {
        "id": "body_mill10",
        "effect_template": "自分のデッキの上からカードを10枚控え室に置く。",
        "ext_key": "body_mill10",
    },
    # Prompt 67: PL!HS-bp1-004 夕霧綴理 (ライブ開始時)
    {
        "id": "live_start_live_cards_count_x1_blade",
        "effect_template": "ライブ終了時まで、自分のライブ中のカード1枚につき、<(ブレード)>を得る。",
        "ext_key": "live_start_live_cards_count_x1_blade",
    },
    # Prompt 72: PL!HS-bp1-023 ド！ド！ド！ (ライブ成功時)
    {
        "id": "live_success_score_gt_opp_and_hasunosora_energy_wait",
        "effect_template": "ライブの合計スコアが相手より高く、かつ自分のステージに『蓮ノ空』のメンバーがいる場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。",
        "ext_key": "live_success_score_gt_opp_and_hasunosora_energy_wait",
    },
    # Prompt 77: PL!HS-bp2-005 大沢瑠璃乃 (ライブ開始時)
    {
        "id": "live_start_all_stage_filled_x2_blade",
        "effect_template": "自分のステージのエリアすべてにメンバーが登場している場合、ライブ終了時まで、<(ブレード)><(ブレード)>を得る。",
        "ext_key": "live_start_all_stage_filled_x2_blade",
    },
    # -----------------------------------------------------------------------
    # group2_single_target_20260402 新規追加
    # -----------------------------------------------------------------------
    # Prompt 22: PL!-bp3-026 Oh,Love&Peace! (ライブ開始時)
    # cost=手札を2枚控え室に置いてもよい → engine 側 pay_or_skip が積む想定
    {
        "id": "live_start_pick_stage_member_blade3",
        "effect_template": "ライブ終了時まで、自分のステージにいるメンバー1人は<(ブレード)><(ブレード)><(ブレード)>を得る。",
        "ext_key": "live_start_pick_stage_member_blade3",
    },
    # Prompt 30: PL!-bp4-013 園田海未 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    {
        "id": "live_start_pick_other_stage_member_pink1",
        "effect_template": "ライブ終了時まで、自分のステージにいるこのメンバー以外のメンバー1人は、<(桃)>を得る。",
        "ext_key": "live_start_pick_other_stage_member_pink1",
    },
    # Prompt 32: PL!-bp4-017 小泉花陽 (ライブ開始時)
    # cost=このメンバーをウェイトにしてもよい → engine 側 pay_or_skip
    # センターの μ's メンバーにブレード付与（対象が固定なので選択不要）
    {
        "id": "live_start_center_mus_blade1",
        "effect_template": "ライブ終了時まで、自分のセンターエリアにいる『μ's』のメンバーは、<(ブレード)>を得る。",
        "ext_key": "live_start_center_mus_blade1",
    },
    # Prompt 35: PL!-bp4-020 Love wing bell (ライブ開始時)
    # ステージが μ's のみ → メンバー1人をポジションチェンジさせてもよい
    {
        "id": "live_start_mus_only_pick_member_position_change",
        "effect_template": "自分のステージにいるメンバーが『μ's』のみの場合、自分のステージにいるメンバー1人をポジションチェンジさせてもよい。",
        "ext_key": "live_start_mus_only_pick_member_position_change",
    },
    # Prompt 37: PL!-bp4-024 小夜啼鳥恋詩 (ライブ開始時)
    # cost なし → μ's メンバー1人選択してブレード付与
    {
        "id": "live_start_pick_mus_stage_member_blade1",
        "effect_template": "ライブ終了時まで、自分のステージにいる『μ's』のメンバー1人は、<(ブレード)>を得る。",
        "ext_key": "live_start_pick_mus_stage_member_blade1",
    },
    # Prompt 46: PL!-pb1-010 高坂穂乃果 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # このメンバー以外全員に +1ブレード（選択なし、対象が複数固定）
    {
        "id": "live_start_other_stage_members_blade1",
        "effect_template": "ライブ終了時まで、自分のステージにいるほかのメンバーは<(ブレード)>を得る。",
        "ext_key": "live_start_other_stage_members_blade1",
    },
    # Prompt 48: PL!-pb1-012 南ことり (登場)
    # cost なし → Printemps のメンバー1人までアクティブ化（ウェイト状態が対象）
    {
        "id": "enter_printemps_activate_up_to_1",
        "effect_template": "自分のステージにいる『Printemps』のメンバーを1人までアクティブにする。",
        "ext_key": "enter_printemps_activate_up_to_1",
    },
    # Prompt 80: PL!HS-bp2-007 百生吟子 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室に置いたカードがメンバーカードなら、同名ステージメンバーに green+1 blade+1
    {
        "id": "live_start_discard_member_same_name_green1_blade1",
        "effect_template": "これにより控え室に置いたカードがメンバーカードの場合、控え室に置いたカードと同じ名前を持つメンバー1人は、ライブ終了時まで、<(緑)><(ブレード)>を得る。",
        "ext_key": "live_start_discard_member_same_name_green1_blade1",
    },
]


def _norm_ws(text: str) -> str:
    """Collapse whitespace for effect_template comparison.

    Steps:
      1. Collapse every run of whitespace (including newlines) to a single space.
      2. Remove spaces that appear immediately before or after icon tokens of the
         form ``<(...)>`` — these spaces are an artefact of the card DB inserting
         newlines around icon tokens and must not prevent matching against the
         one-liner form used in EXTRA_EFFECT_RULES.
    """
    import re as _re
    s = _re.sub(r'\s+', ' ', (text or "").strip())
    # Remove space before icon token: "は、 <(ブレード)>" -> "は、<(ブレード)>"
    s = _re.sub(r' (<\([^)]*\)>)', r'\1', s)
    # Remove space after icon token: "<(ブレード)> を" -> "<(ブレード)>を"
    s = _re.sub(r'(<\([^)]*\)>) ', r'\1', s)
    return s


def try_match_effect_template_ext(
    eng: Dict[str, Any],
    effect_text: str,
) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """Match extension-owned effect templates.

    Matching strategy (in priority order):
      1. Exact match after strip()  -- safest, preserves existing behaviour.
      2. Whitespace-normalized match -- collapses newlines / multi-spaces to a
         single space before comparing.  Needed because some card DB entries
         embed newlines around icon tokens such as <(ブレード)>.

    Returns:
        (rule, gd) if matched, else None.
    """
    s = (effect_text or "").strip()
    if not s:
        return None

    s_norm = _norm_ws(s)

    for r in EXTRA_EFFECT_RULES:
        tpl = str(r.get("effect_template", "") or "").strip()
        if not tpl:
            continue
        # 1. exact match (highest priority, no change to existing behaviour)
        if s == tpl:
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})
        # 2. whitespace-normalised fallback
        if s_norm == _norm_ws(tpl):
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})
    return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _add_temp_blade(eng: Dict[str, Any], slot: Any, n: int) -> None:
    if not slot or n <= 0:
        return
    try:
        slot.temp_blade = int(getattr(slot, "temp_blade", 0) or 0) + int(n)
        slot.temp_until = "end_of_live"
    except Exception:
        pass


def _add_temp_hearts(eng: Dict[str, Any], slot: Any, hearts: Dict[str, int]) -> None:
    if not slot or not hearts:
        return
    try:
        cur = dict(getattr(slot, "temp_hearts", {}) or {})
    except Exception:
        cur = {}
    for k, v in (hearts or {}).items():
        try:
            iv = int(v or 0)
        except Exception:
            iv = 0
        if iv <= 0:
            continue
        cur[str(k)] = int(cur.get(str(k), 0) or 0) + iv
    try:
        slot.temp_hearts = cur
        slot.temp_until = "end_of_live"
    except Exception:
        pass


def _active_stage_slots(gs: Any) -> list:
    """Return list of active (non-None) StageSlots."""
    out = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                v = st.get(pos)
                if v is not None and bool(getattr(v, "active", False)):
                    out.append(v)
    except Exception:
        pass
    return out


def _all_stage_slots_filled(gs: Any) -> bool:
    """Return True if all 3 stage positions (L/C/R) have an active member."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            v = st.get(pos)
            if v is None or not bool(getattr(v, "cardnumber", None)):
                return False
        return True
    except Exception:
        return False


def _src_slot(gs: Any, ctx: Dict[str, Any]) -> Any:
    """Return the StageSlot for the source member, or None."""
    try:
        src_pos = str(
            (ctx or {}).get("src_pos") or (ctx or {}).get("pos") or ""
        ).upper()
        if src_pos not in ("L", "C", "R"):
            return None
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            return st.get(src_pos)
    except Exception:
        pass
    return None


def _success_zone_cards(gs: Any) -> list:
    """Return list of cards in the success live zone."""
    try:
        z = getattr(gs, "success_zone", None) or []
        if not isinstance(z, list):
            z = list(z)
        return z
    except Exception:
        return []


def _card_score(card: Any, cards_db: Dict[str, Any]) -> int:
    """Return the score of a card (from cards_db or card attribute)."""
    try:
        cn = str(getattr(card, "cardnumber", None) or card or "")
        info = cards_db.get(cn)
        if info is not None:
            s = getattr(info, "score", None)
            if s is None:
                s = (info if isinstance(info, dict) else {}). get("score")
            if s is not None and str(s).strip() not in ("", "None"):
                return int(str(s).strip())
        # fallback: card itself may have score attr
        sv = getattr(card, "score", None)
        if sv is not None and str(sv).strip() not in ("", "None"):
            return int(str(sv).strip())
    except Exception:
        pass
    return 0


def _lookup_cardinfo(cards_db: Dict[str, Any], card: Any) -> Any:
    try:
        cn = str(getattr(card, "cardnumber", None) or card or "").strip()
        if not cn:
            return None
        info = cards_db.get(cn)
        if info is not None:
            return info
        low = cn.lower()
        for k, v in (cards_db or {}).items():
            try:
                if str(k).strip().lower() == low:
                    return v
            except Exception:
                continue
    except Exception:
        pass
    return None

def _card_group(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the group string of a card."""
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            g = getattr(info, "group", None)
            if g is None:
                g = (info if isinstance(info, dict) else {}).get("group")
            if g:
                return str(g)
        g = getattr(card, "group", None)
        if g:
            return str(g)
    except Exception:
        pass
    return ""


def _card_unit(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the unit string of a card."""
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            u = getattr(info, "unit", None)
            if u is None:
                u = (info if isinstance(info, dict) else {}).get("unit")
            if u:
                return str(u)
        u = getattr(card, "unit", None)
        if u:
            return str(u)
    except Exception:
        pass
    return ""


def _card_cost(card: Any, cards_db: Dict[str, Any]) -> int:
    """Return the cost of a card as int."""
    try:
        cn = str(getattr(card, "cardnumber", None) or card or "")
        info = cards_db.get(cn)
        if info is not None:
            c = getattr(info, "cost", None)
            if c is None:
                c = (info if isinstance(info, dict) else {}).get("cost")
            if c is not None and str(c).strip() not in ("", "None"):
                return int(str(c).strip())
        cv = getattr(card, "cost", None)
        if cv is not None and str(cv).strip() not in ("", "None"):
            return int(str(cv).strip())
    except Exception:
        pass
    return 0


def _card_type_norm(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the normalized card type string (MEMBER / LIVE / etc.)."""
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            t = getattr(info, "card_type_norm", None)
            if t is None:
                t = (info if isinstance(info, dict) else {}).get("card_type_norm")
            if t:
                return str(t)

            raw = getattr(info, "card_type_raw", None)
            if raw is None:
                raw = (info if isinstance(info, dict) else {}).get("card_type_raw")
            if raw is None:
                raw = getattr(info, "type", None)
            if raw is None:
                raw = (info if isinstance(info, dict) else {}).get("type")
            if raw:
                s = str(raw).strip().upper()
                jp = str(raw).strip()
                if s in ("MEMBER", "LIVE", "ENERGY"):
                    return s
                if jp == "メンバー":
                    return "MEMBER"
                if jp == "ライブ":
                    return "LIVE"
                if jp == "エネルギー":
                    return "ENERGY"

        t = getattr(card, "card_type_norm", None)
        if t:
            return str(t)

        raw = getattr(card, "card_type_raw", None) or getattr(card, "type", None)
        if raw:
            s = str(raw).strip().upper()
            jp = str(raw).strip()
            if s in ("MEMBER", "LIVE", "ENERGY"):
                return s
            if jp == "メンバー":
                return "MEMBER"
            if jp == "ライブ":
                return "LIVE"
            if jp == "エネルギー":
                return "ENERGY"
    except Exception:
        pass
    return ""


def _card_name(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the cardname string of a card."""
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            n = getattr(info, "cardname", None)
            if n is None:
                n = (info if isinstance(info, dict) else {}).get("cardname")
            if n:
                return str(n)
        n = getattr(card, "cardname", None) or getattr(card, "name", None)
        if n:
            return str(n)
    except Exception:
        pass
    return ""


def _stage_member_cost_sum(gs: Any, cards_db: Dict[str, Any]) -> int:
    """Sum of costs of all active stage members."""
    total = 0
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    total += _card_cost(slot, cards_db)
    except Exception:
        pass
    return total


def _opp_stage_member_cost_sum(gs: Any, cards_db: Dict[str, Any]) -> int:
    """Sum of costs of all opponent active stage members."""
    total = 0
    try:
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is None:
            return 0
        st = getattr(opp, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    total += _card_cost(slot, cards_db)
    except Exception:
        pass
    return total


def _has_opponent_state(gs: Any) -> bool:
    """Best-effort check whether opponent state exists in this runtime."""
    try:
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is None:
            return False
        return True
    except Exception:
        return False


def _activate_energy(gs: Any, n: int) -> int:
    """Move up to n energy from energy_wait to energy_active. Returns count moved.
    energy_active / energy_wait are int fields in GameState (not lists).
    """
    moved = 0
    try:
        wait = int(getattr(gs, "energy_wait", 0) or 0)
        take = min(max(0, n), wait)
        if take > 0:
            gs.energy_wait -= take
            gs.energy_active += take
            moved = take
    except Exception:
        pass
    return moved


def _draw_cards(eng: Dict[str, Any], gs: Any, n: int) -> int:
    """Draw n cards from deck to hand. Returns count drawn."""
    drawn = 0
    try:
        # Try using engine helper if available
        draw_fn = eng.get("_draw") or eng.get("draw_cards")
        if callable(draw_fn):
            draw_fn(gs, n)
            return n
        # Fallback: direct list manipulation
        deck = getattr(gs, "deck", None)
        hand = getattr(gs, "hand", None)
        if deck is None or hand is None:
            return 0
        for _ in range(n):
            if not deck:
                break
            hand.append(deck.pop(0))
            drawn += 1
    except Exception:
        pass
    return drawn


def _live_in_progress_cards(gs: Any) -> list:
    """Return list of cards currently in the live zone (ライブ中のカード)."""
    try:
        # Try common field names
        for attr in ("live_zone", "live_cards", "current_live_cards", "live_area"):
            z = getattr(gs, attr, None)
            if z is not None:
                return list(z) if not isinstance(z, list) else z
        # Fallback: try live dict
        live = getattr(gs, "live", None)
        if live is not None:
            cards = getattr(live, "cards", None) or (live if isinstance(live, dict) else {}).get("cards")
            if cards is not None:
                return list(cards)
    except Exception:
        pass
    return []


def _live_score_total(gs: Any) -> int:
    """Return current live total score (自分)."""
    try:
        for attr in ("live_score", "score", "current_score"):
            v = getattr(gs, attr, None)
            if v is not None:
                return int(v)
        live = getattr(gs, "live", None)
        if live is not None:
            v = getattr(live, "score", None) or (live if isinstance(live, dict) else {}).get("score")
            if v is not None:
                return int(v)
    except Exception:
        pass
    return 0


def _opp_live_score_total(gs: Any) -> int:
    """Return opponent live total score."""
    try:
        for attr in ("opp_live_score", "opp_score"):
            v = getattr(gs, attr, None)
            if v is not None:
                return int(v)
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is not None:
            for attr in ("live_score", "score", "current_score"):
                v = getattr(opp, attr, None)
                if v is not None:
                    return int(v)
    except Exception:
        pass
    return 0


def _stage_has_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> bool:
    """Return True if any active stage member belongs to group_name."""
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_group(slot, cards_db) == group_name:
                        return True
    except Exception:
        pass
    return False


def _stage_all_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> bool:
    """Return True if ALL occupied stage positions belong to group_name."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        found_any = False
        for pos in ("L", "C", "R"):
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, "cardnumber", None)):
                continue
            found_any = True
            if _card_group(slot, cards_db) != group_name:
                return False
        return found_any
    except Exception:
        return False


def _stage_unit_count(gs: Any, cards_db: Dict[str, Any], unit_name: str) -> int:
    """Count active stage members belonging to unit_name."""
    count = 0
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_unit(slot, cards_db) == unit_name:
                        count += 1
    except Exception:
        pass
    return count


def _stage_positions_with_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return list of (pos, slot) tuples for stage members matching group_name."""
    result = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_group(slot, cards_db) == group_name:
                        result.append((pos, slot))
    except Exception:
        pass
    return result


def _stage_positions_with_unit(gs: Any, cards_db: Dict[str, Any], unit_name: str) -> list:
    """Return list of (pos, slot) tuples for stage members matching unit_name."""
    result = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_unit(slot, cards_db) == unit_name:
                        result.append((pos, slot))
    except Exception:
        pass
    return result


def _stage_positions_all_occupied(gs: Any) -> list:
    """Return list of (pos, slot) tuples for all occupied stage positions."""
    result = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    result.append((pos, slot))
    except Exception:
        pass
    return result


def _green_room_top(gs: Any) -> Any:
    """Return the most recently added card in green_room (控え室の最上位), or None."""
    try:
        gr = getattr(gs, "green_room", None)
        if gr is None:
            gr = (
                getattr(gs, "waiting_room", None)
                or getattr(gs, "graveyard", None)
                or getattr(gs, "discard", None)
            )
        if gr and isinstance(gr, list) and len(gr) > 0:
            return gr[-1]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

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
            getattr(gs, 'pending').append(payload)
            gs.log.append(f"[PENDING] position_change src={src_pos}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 17: PL!-bp3-006 西木野真姫
    # ライブ終了時まで、成功ライブ置き場の枚数 × +2ブレード
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
    # Prompt 24: PL!-bp4-001 高坂穂乃果
    # 自ステージのコスト合計が相手より低い場合、カードを1枚引く。
    # ------------------------------------------------------------------
    if ext_key == "live_start_my_cost_lower_draw1":
        my_cost = _stage_member_cost_sum(gs, cards_db)
        opp_exists = _has_opponent_state(gs)
        opp_cost = _opp_stage_member_cost_sum(gs, cards_db) if opp_exists else 0
        src = str((ctx or {}).get("source_cn") or "")
        if opp_exists:
            if my_cost < opp_cost:
                drawn = _draw_cards(eng, gs, 1)
                try:
                    gs.log.append(f"[AUTO_EXT] stage_cost {my_cost}<{opp_cost} -> draw {drawn} (高坂穂乃果)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append(f"[AUTO_EXT] stage_cost {my_cost}>={opp_cost}, no draw (高坂穂乃果)")
                except Exception:
                    pass
            return True
        payload = {
            "kind": "confirm_effect",
            "text": "【高坂穂乃果】ライブ開始時：自分ステージのコスト合計が相手より低いなら、カードを1枚引く",
            "options": ["使う", "スキップ"],
            "after_effect_template": "自分ステージにいるメンバーのコストの合計が相手より低い場合、カードを1枚引く。",
            "ctx": {"source_cn": src, "_ext_confirm_op": "draw1"},
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 高坂穂乃果: confirm draw1 (my_cost={my_cost}, opp unavailable)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 26: PL!-bp4-004 園田海未
    # 成功ライブのスコア合計 ≥ 6 → energy 2枚アクティブ
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
    # Prompt 31: PL!-bp4-016 東條希
    # 成功ライブのスコア合計 ≥ 3 → draw 1
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

    # ------------------------------------------------------------------
    # Prompt 57: PL!-pb1-032 SENTIMENTAL StepS
    # 成功ライブ置き場に μ's カードがある → draw 1
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

    # ------------------------------------------------------------------
    # Prompt 67: PL!HS-bp1-004 夕霧綴理
    # ライブ終了時まで、ライブ中のカード 1 枚につき +1ブレード
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
    # Prompt 72: PL!HS-bp1-023 ド！ド！ド！
    # ライブ合計スコア > 相手 かつ ステージに蓮ノ空メンバー → energy deck から 1枚 wait
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

    # ------------------------------------------------------------------
    # Prompt 77: PL!HS-bp2-005 大沢瑠璃乃
    # ステージ全 3 エリアにメンバーがいる → ライブ終了時まで +2ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_all_stage_filled_x2_blade":
        slot = _src_slot(gs, ctx)
        if _all_stage_slots_filled(gs):
            if slot is not None:
                _add_temp_blade(eng, slot, 2)
            try:
                gs.log.append("[AUTO_EXT] all stage filled -> +2blade (大沢瑠璃乃)")
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] stage not full, no blade (大沢瑠璃乃)")
            except Exception:
                pass
        return True

    # ==================================================================
    # group2_single_target_20260402 新規実装
    # ==================================================================

    # ------------------------------------------------------------------
    # Prompt 22: PL!-bp3-026 Oh,Love&Peace! (ライブ開始時)
    # ライブ終了時まで、ステージのメンバー1人（選択）に +3ブレード
    # cost=手札を2枚控え室に置いてもよい → engine 側 pay_or_skip pending が先行
    # effect handler では choose_stage_member_to_activate pending を流用して
    # 対象メンバーを1人選ばせ、解決時に temp_blade +3
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_stage_member_blade3":
        occupied = _stage_positions_all_occupied(gs)
        src = str((ctx or {}).get("source_cn") or "")
        if not occupied:
            try:
                gs.log.append("[AUTO_EXT] no stage members, no blade (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        if len(occupied) == 1:
            # 対象が1人のみなら選択不要で即付与
            _, slot = occupied[0]
            _add_temp_blade(eng, slot, 3)
            try:
                gs.log.append(f"[AUTO_EXT] only 1 member -> +3blade to {occupied[0][0]} (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        # 複数いる場合は choose_stage_member_to_activate pending で選択
        candidates = [pos for pos, _ in occupied]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_stage_member_blade3__resolve",
            "source_cn": src,
            "label": "【Oh,Love&Peace!】ブレード+3を与えるメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Oh,Love&Peace!: choose member for +3blade from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_stage_member_blade3__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_blade(eng, slot, 3)
            try:
                gs.log.append(f"[AUTO_EXT] +3blade -> {chosen_pos} (Oh,Love&Peace! resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 30: PL!-bp4-013 園田海未 (ライブ開始時)
    # このメンバー以外のステージメンバー1人（選択）に pink+1
    # src_pos から「このメンバー」を特定して除外候補を絞る
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_other_stage_member_pink1":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append(f"[AUTO_EXT] no other members on stage (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        if len(others) == 1:
            _, slot = others[0]
            _add_temp_hearts(eng, slot, {"pink": 1})
            try:
                gs.log.append(f"[AUTO_EXT] +pink to {others[0][0]} (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in others]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_other_stage_member_pink1__resolve",
            "source_cn": src,
            "label": "【園田海未】桃ハート+1を与えるメンバーを選んでください（このメンバー以外）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 園田海未 bp4-013: choose other member for +pink from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_other_stage_member_pink1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_hearts(eng, slot, {"pink": 1})
            try:
                gs.log.append(f"[AUTO_EXT] +pink -> {chosen_pos} (園田海未 bp4-013 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 32: PL!-bp4-017 小泉花陽 (ライブ開始時)
    # センター(C)の μ's メンバーに +1ブレード（対象固定、選択不要）
    # ------------------------------------------------------------------
    if ext_key == "live_start_center_mus_blade1":
        st = getattr(gs, "stage", None)
        center_slot = (st or {}).get("C") if isinstance(st, dict) else None
        if center_slot is not None and bool(getattr(center_slot, "cardnumber", None)):
            if _card_group(center_slot, cards_db) == "μ's":
                _add_temp_blade(eng, center_slot, 1)
                try:
                    gs.log.append("[AUTO_EXT] center μ's -> +1blade (小泉花陽 bp4-017)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append("[AUTO_EXT] center member is not μ's, no blade (小泉花陽 bp4-017)")
                except Exception:
                    pass
        else:
            try:
                gs.log.append("[AUTO_EXT] center empty, no blade (小泉花陽 bp4-017)")
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
        # 選択用 pending: choose_stage_member_to_activate でポジションを選ばせ、
        # 解決時に position_change pending を積む
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
    # Prompt 37: PL!-bp4-024 小夜啼鳥恋詩 (ライブ開始時)
    # ステージの μ's メンバー1人（選択）に +1ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_mus_stage_member_blade1":
        mus_members = _stage_positions_with_group(gs, cards_db, "μ's")
        src = str((ctx or {}).get("source_cn") or "")
        if not mus_members:
            try:
                gs.log.append("[AUTO_EXT] no μ's on stage (小夜啼鳥恋詩)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in mus_members]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_mus_stage_member_blade1__resolve",
            "source_cn": src,
            "label": "【小夜啼鳥恋詩】ブレード+1を与えるμ'sメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 小夜啼鳥恋詩: choose μ's member for +blade from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_mus_stage_member_blade1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] +1blade -> {chosen_pos} (小夜啼鳥恋詩 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 46: PL!-pb1-010 高坂穂乃果 (ライブ開始時)
    # このメンバー以外のステージメンバー全員に +1ブレード（選択なし）
    # ------------------------------------------------------------------
    if ext_key == "live_start_other_stage_members_blade1":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append(f"[AUTO_EXT] no other members on stage (高坂穂乃果 pb1-010)")
            except Exception:
                pass
            return True
        for pos, slot in others:
            _add_temp_blade(eng, slot, 1)
        try:
            gs.log.append(f"[AUTO_EXT] +1blade to {[p for p,_ in others]} (高坂穂乃果 pb1-010)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 48: PL!-pb1-012 南ことり (登場)
    # Printemps のウェイト状態メンバーを1人までアクティブにする
    # ウェイト = active==False のスロット
    # ------------------------------------------------------------------
    if ext_key == "enter_printemps_activate_up_to_1":
        src = str((ctx or {}).get("source_cn") or "")
        wait_printemps = []
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _card_unit(slot, cards_db) != "Printemps":
                        continue
                    if not bool(getattr(slot, "active", True)):
                        wait_printemps.append((pos, slot))
        except Exception:
            pass

        if not wait_printemps:
            try:
                gs.log.append("[AUTO_EXT] no Printemps wait member to activate (南ことり pb1-012)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in wait_printemps] + ["skip"]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": True,
            "after_ext_key": "enter_printemps_activate_up_to_1__resolve",
            "source_cn": src,
            "label": "【南ことり】アクティブにするPrintempsメンバーを選んでください（スキップ可）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 南ことり pb1-012: choose Printemps wait member from {[p for p,_ in wait_printemps]}")
        except Exception:
            pass
        return True

    if ext_key == "enter_printemps_activate_up_to_1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        if chosen_pos == "SKIP" or chosen_pos not in ("L", "C", "R"):
            try:
                gs.log.append("[AUTO_EXT] Printemps activate skipped (南ことり pb1-012)")
            except Exception:
                pass
            return True
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            try:
                slot.active = True
                gs.log.append(f"[AUTO_EXT] activate {chosen_pos} (南ことり pb1-012 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 80: PL!HS-bp2-007 百生吟子 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室に置いたカードがメンバーカードなら、同名ステージメンバーに green+1 blade+1
    # ctx["discarded_cn"] に捨てたカードの cardnumber が渡される想定。
    # 渡されない場合は green_room の最新カードを参照する。
    # ------------------------------------------------------------------
    if ext_key == "live_start_discard_member_same_name_green1_blade1":
        src = str((ctx or {}).get("source_cn") or "")
        # 捨てたカードを特定
        discarded_cn = str((ctx or {}).get("discarded_cn") or "").strip()
        if not discarded_cn:
            top = _green_room_top(gs)
            if top is not None:
                discarded_cn = str(getattr(top, "cardnumber", None) or top or "").strip()

        if not discarded_cn:
            try:
                gs.log.append("[AUTO_EXT] could not identify discarded card (百生吟子)")
            except Exception:
                pass
            return True

        # カードタイプ確認（MEMBER でなければ効果なし）
        discarded_type = _card_type_norm(discarded_cn, cards_db)
        if discarded_type != "MEMBER":
            try:
                gs.log.append(f"[AUTO_EXT] discarded {discarded_cn} is not MEMBER (type={discarded_type}), no effect (百生吟子)")
            except Exception:
                pass
            return True

        # 同名のステージメンバーを探す
        discarded_name = _card_name(discarded_cn, cards_db)
        if not discarded_name:
            try:
                canon_fn = eng.get("_canon_cardno")
                get_card_fn = eng.get("_get_card")
                canon_cn = canon_fn(discarded_cn) if callable(canon_fn) else str(discarded_cn or "")
                ci_dis = get_card_fn(cards_db, canon_cn) if callable(get_card_fn) else None
                if ci_dis is not None:
                    discarded_name = str(getattr(ci_dis, "cardname", "") or getattr(ci_dis, "name", "") or "")
            except Exception:
                pass
        if not discarded_name:
            try:
                gs.log.append(f"[AUTO_EXT] could not get name for {discarded_cn} (百生吟子)")
            except Exception:
                pass
            return True

        matched = []
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    slot_name = _card_name(slot, cards_db)
                    slot_cn = str(getattr(slot, "cardnumber", "") or "")
                    same_name = bool(slot_name and slot_name == discarded_name)
                    same_cn = False
                    try:
                        canon_fn = eng.get("_canon_cardno")
                        if callable(canon_fn):
                            same_cn = canon_fn(slot_cn) == canon_fn(discarded_cn)
                        else:
                            same_cn = slot_cn == discarded_cn
                    except Exception:
                        same_cn = slot_cn == discarded_cn
                    if same_name or same_cn:
                        matched.append((pos, slot))
        except Exception:
            pass

        if not matched:
            try:
                gs.log.append(f"[AUTO_EXT] no stage member named '{discarded_name}', no effect (百生吟子)")
            except Exception:
                pass
            return True

        if len(matched) == 1:
            _, slot = matched[0]
            _add_temp_hearts(eng, slot, {"green": 1})
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] discarded MEMBER '{discarded_name}' -> +green+blade to {matched[0][0]} (百生吟子)")
            except Exception:
                pass
            return True

        # 同名が複数いる場合は選択（通常は起きないが安全のため）
        candidates = [pos for pos, _ in matched]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_discard_member_same_name_green1_blade1__resolve",
            "source_cn": src,
            "discarded_name": discarded_name,
            "label": f"【百生吟子】{discarded_name}と同名のメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 百生吟子: choose same-name member from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_discard_member_same_name_green1_blade1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_hearts(eng, slot, {"green": 1})
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] +green+blade -> {chosen_pos} (百生吟子 resolve)")
            except Exception:
                pass
        return True

    return False
