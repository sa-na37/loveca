# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_group1_lowest_risk_20260402
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
]


def try_match_effect_template_ext(
    eng: Dict[str, Any],
    effect_text: str,
) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """Match extension-owned effect templates.

    Returns:
        (rule, gd) if matched, else None.
    """
    s = (effect_text or "").strip()
    if not s:
        return None

    for r in EXTRA_EFFECT_RULES:
        tpl = str(r.get("effect_template", "") or "").strip()
        if tpl and s == tpl:
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


def _card_group(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the group string of a card."""
    try:
        cn = str(getattr(card, "cardnumber", None) or card or "")
        info = cards_db.get(cn)
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
        cn = str(getattr(card, "cardnumber", None) or card or "")
        info = cards_db.get(cn)
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


def _activate_energy(gs: Any, n: int) -> int:
    """Move up to n cards from energy_wait to energy_active. Returns count moved."""
    moved = 0
    try:
        wait = getattr(gs, "energy_wait", None)
        active = getattr(gs, "energy_active", None)
        if wait is None or active is None:
            return 0
        for _ in range(n):
            if not wait:
                break
            card = wait.pop(0)
            active.append(card)
            moved += 1
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
    # 自分ステージのコスト合計 < 相手 → draw 1
    # ------------------------------------------------------------------
    if ext_key == "live_start_my_cost_lower_draw1":
        my_cost = _stage_member_cost_sum(gs, cards_db)
        opp_cost = _opp_stage_member_cost_sum(gs, cards_db)
        if my_cost < opp_cost:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(
                    f"[AUTO_EXT] my_cost={my_cost} < opp_cost={opp_cost} -> draw {drawn} (高坂穂乃果)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] my_cost={my_cost} >= opp_cost={opp_cost}, no draw (高坂穂乃果)"
                )
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
    # コスト (このメンバーをウェイトにしてもよい) は engine 側が pay_or_skip pending を積む。
    # この handler は effect 部分のみを担当する。
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
        # ctx に live_score / opp_live_score があれば優先
        try:
            if (ctx or {}).get("live_score") is not None:
                my_score = int(ctx["live_score"])
            if (ctx or {}).get("opp_live_score") is not None:
                opp_score = int(ctx["opp_live_score"])
        except Exception:
            pass

        has_hasunosora = _stage_has_group(gs, cards_db, "蓮ノ空")
        if my_score > opp_score and has_hasunosora:
            added = 0
            try:
                energy_deck = (
                    getattr(gs, "energy_deck", None)
                    or getattr(gs, "energy_pile", None)
                )
                energy_wait = getattr(gs, "energy_wait", None)
                if energy_deck and energy_wait is not None:
                    card = energy_deck.pop(0)
                    energy_wait.append(card)
                    added = 1
            except Exception:
                pass
            try:
                gs.log.append(
                    f"[AUTO_EXT] live_score {my_score}>{opp_score} & 蓮ノ空 on stage "
                    f"-> energy_wait +{added} (ド！ド！ド！)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] cond not met (score {my_score} vs {opp_score}, "
                    f"hasunosora={has_hasunosora}), no energy (ド！ド！ド！)"
                )
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

    return False
