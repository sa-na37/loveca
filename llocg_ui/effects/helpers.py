# -*- coding: utf-8 -*-
# BUILD_TAG: helpers_green_pick_detail_fallback_20260424e
from __future__ import annotations

"""llocg_ui.effects.helpers

engine_effect の共通 helper 群の正本。

注意:
- ここには zone 移動、card 参照、draw、temp bonus 集計などの小部品だけを置く
- matcher や dispatcher 本体は置かない
"""

from typing import Any, Dict

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
    """Return the normalized card type string (MEMBER / LIVE / etc.).

    Conservative rule:
    - Prefer explicit normalized/raw DB type when present.
    - Only fall back to LIVE when the row is obviously LIVE-shaped.
    - Never treat score=0 on MEMBER rows as evidence for LIVE.
    """
    def _infer_live_from_shape(info: Any) -> bool:
        try:
            req = getattr(info, 'required_hearts', None)
            if req is None and isinstance(info, dict):
                req = info.get('required_hearts')
            if isinstance(req, dict) and any(int(v or 0) > 0 for v in req.values()):
                return True
        except Exception:
            pass
        try:
            score = getattr(info, 'score', None)
            if score is None and isinstance(info, dict):
                score = info.get('score')
            score_i = int(score or 0)
        except Exception:
            score_i = 0
        try:
            cost = getattr(info, 'cost', None)
            if cost is None and isinstance(info, dict):
                cost = info.get('cost')
            cost_i = int(cost or 0)
        except Exception:
            cost_i = 0
        try:
            blade = getattr(info, 'blade', None)
            if blade is None and isinstance(info, dict):
                blade = info.get('blade')
            blade_i = int(blade or 0)
        except Exception:
            blade_i = 0
        try:
            base = getattr(info, 'base_hearts', None)
            if base is None and isinstance(info, dict):
                base = info.get('base_hearts')
            has_base = isinstance(base, dict) and any(int(v or 0) > 0 for v in base.values())
        except Exception:
            has_base = False
        return bool(score_i > 0 and cost_i <= 0 and blade_i <= 0 and not has_base)

    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            t = getattr(info, "card_type_norm", None)
            if t is None:
                t = (info if isinstance(info, dict) else {}).get("card_type_norm")
            if t:
                ts = str(t).strip().upper()
                if ts in ("MEMBER", "LIVE", "ENERGY"):
                    if ts == 'MEMBER' and _infer_live_from_shape(info):
                        return 'LIVE'
                    return ts

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
                    if s == 'MEMBER' and _infer_live_from_shape(info):
                        return 'LIVE'
                    return s
                if jp == "メンバー":
                    return 'LIVE' if _infer_live_from_shape(info) else "MEMBER"
                if jp == "ライブ":
                    return "LIVE"
                if jp == "エネルギー":
                    return "ENERGY"

        t = getattr(card, "card_type_norm", None)
        if t:
            return str(t).strip().upper()

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
# group3 helpers
# ---------------------------------------------------------------------------

def _green_room_list(gs: Any) -> list:
    """Return the green_room (控え室) list, trying common field names."""
    try:
        for attr in ("green_room", "waiting_room", "graveyard", "discard"):
            gr = getattr(gs, attr, None)
            if gr is not None and isinstance(gr, list):
                return gr
    except Exception:
        pass
    return []


def _label_matches_group_or_unit(card: Any, cards_db: Dict[str, Any], label: str) -> bool:
    """Best-effort matcher for labels that may live in group or unit.
    Accept exact match or containment in either field.
    """
    try:
        lab = str(label or "").strip()
        if not lab:
            return False
        g = str(_card_group(card, cards_db) or "").strip()
        u = str(_card_unit(card, cards_db) or "").strip()
        return (g == lab) or (u == lab) or (lab in g if g else False) or (lab in u if u else False)
    except Exception:
        return False


def _green_room_members_by_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return list of MEMBER cards in green_room belonging to group_name/unit_name."""
    result = []
    for card in _green_room_list(gs):
        try:
            if _card_type_norm(card, cards_db) == "MEMBER" and _label_matches_group_or_unit(card, cards_db, group_name):
                result.append(card)
        except Exception:
            pass
    return result


def _green_room_lives_by_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return list of LIVE cards in green_room belonging to group_name/unit_name."""
    result = []
    for card in _green_room_list(gs):
        try:
            if _card_type_norm(card, cards_db) == "LIVE" and _label_matches_group_or_unit(card, cards_db, group_name):
                result.append(card)
        except Exception:
            pass
    return result


def _green_room_lives_by_group_score_le(
    gs: Any, cards_db: Dict[str, Any], group_name: str, score_max: int
) -> list:
    """Return LIVE cards in green_room with group_name and score <= score_max."""
    result = []
    for card in _green_room_lives_by_group(gs, cards_db, group_name):
        try:
            if _card_score(card, cards_db) <= score_max:
                result.append(card)
        except Exception:
            pass
    return result


def _green_room_cards_by_group_any_type(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return cards of any type in green_room belonging to group_name/unit_name."""
    result = []
    for card in _green_room_list(gs):
        try:
            if _label_matches_group_or_unit(card, cards_db, group_name):
                result.append(card)
        except Exception:
            pass
    return result

def _card_required_hearts(card: Any, cards_db: Dict[str, Any]) -> Dict[str, int]:
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            d = getattr(info, 'required_hearts', None)
            if d is None and isinstance(info, dict):
                d = info.get('required_hearts')
            if isinstance(d, dict):
                return {str(k): int(v or 0) for k, v in d.items()}
    except Exception:
        pass
    return {}


def _green_room_lives_with_required_heart_ge(gs: Any, cards_db: Dict[str, Any], color: str, n: int) -> list:
    result = []
    key = str(color or '').strip().lower()
    for card in _green_room_list(gs):
        try:
            if _card_type_norm(card, cards_db) != 'LIVE':
                continue
            req = _card_required_hearts(card, cards_db)
            if int(req.get(key, 0) or 0) >= int(n or 0):
                result.append(card)
        except Exception:
            pass
    return result


def _enqueue_pick_live_req_heart_from_green(gs: Any, cards_db: Dict[str, Any], color: str, n: int, src: str) -> bool:
    cands = _green_room_lives_with_required_heart_ge(gs, cards_db, color, n)
    if not cands:
        try:
            gs.log.append(f"[AUTO_EXT] no LIVE in green_room with required {color}>={n} ({src})")
        except Exception:
            pass
        return True
    if len(cands) == 1:
        ok = _move_card_from_green_to_hand(gs, cands[0])
        cn_str = str(getattr(cands[0], 'cardnumber', None) or cands[0] or '')
        try:
            gs.log.append(f"[AUTO_EXT] green->hand {cn_str} ({src}) ok={ok}")
        except Exception:
            pass
        return True
    cns = [str(getattr(c, 'cardnumber', None) or c or '') for c in cands]
    payload = {
        'kind': 'pick_live_from_green',
        'text': f"控え室の必要ハートに<{color}>を{n}以上含むライブカードを1枚手札に加える",
        'options': cns,
    }
    try:
        getattr(gs, 'pending').append(payload)
        gs.log.append(f"[PENDING] pick req-heart live from green color={color} n={n} opts={cns}")
    except Exception:
        pass
    return True


def _move_card_from_green_to_hand(gs: Any, card: Any) -> bool:
    """Remove card from green_room and add to hand. Returns True on success."""
    try:
        gr = _green_room_list(gs)
        if card in gr:
            gr.remove(card)
        else:
            # fallback: try to find by cardnumber
            cn = str(getattr(card, "cardnumber", None) or card or "")
            found = None
            for c in list(gr):
                if str(getattr(c, "cardnumber", None) or c or "") == cn:
                    found = c
                    break
            if found is None:
                return False
            gr.remove(found)
            card = found
        hand = getattr(gs, "hand", None)
        if hand is None:
            return False
        hand.append(card)
        return True
    except Exception:
        return False


def _move_live_from_green_to_set_zone(gs: Any, card: Any) -> bool:
    """Remove LIVE card from green_room and append to set_zone (face-up by current UI contract)."""
    try:
        gr = _green_room_list(gs)
        found = None
        if card in gr:
            found = card
        else:
            cn = str(getattr(card, "cardnumber", None) or card or "")
            for c in list(gr):
                if str(getattr(c, "cardnumber", None) or c or "") == cn:
                    found = c
                    break
        if found is None:
            return False
        gr.remove(found)
        sz = getattr(gs, "set_zone", None)
        if sz is None:
            setattr(gs, "set_zone", [])
            sz = getattr(gs, "set_zone")
        sz.append(found)
        return True
    except Exception:
        return False


def _reserve_next_live_set_limit_delta(gs: Any, delta: int, src: str = "") -> int:
    try:
        cur = int(getattr(gs, "next_live_set_limit_delta", 0) or 0)
    except Exception:
        cur = 0
    new_val = cur + int(delta or 0)
    try:
        setattr(gs, "next_live_set_limit_delta", new_val)
    except Exception:
        pass
    try:
        gs.log.append(f"[AUTO_EXT] reserved next live-set limit delta {new_val:+d} ({src})")
    except Exception:
        pass
    return new_val


def _opp_stage_has_wait_member(gs: Any) -> bool:
    """Return True if opponent stage has any member in wait (active==False) state."""
    try:
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is None:
            return False
        st = getattr(opp, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, "cardnumber", None)):
                continue
            if not bool(getattr(slot, "active", True)):
                return True
    except Exception:
        pass
    return False


def _stage_other_member_exists(gs: Any, src_pos: str) -> bool:
    """Return True if any stage position OTHER than src_pos has a member."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            if pos == src_pos:
                continue
            slot = st.get(pos)
            if slot is not None and bool(getattr(slot, "cardnumber", None)):
                return True
    except Exception:
        pass
    return False


def _stage_has_any_other_member(gs: Any, exclude_pos: str = "") -> bool:
    """Return True if any member is on stage (optionally excluding exclude_pos)."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            if pos == exclude_pos:
                continue
            slot = st.get(pos)
            if slot is not None and bool(getattr(slot, "cardnumber", None)):
                return True
    except Exception:
        pass
    return False


def _slot_total_blade(slot: Any) -> int:
    """Return total blade count of a slot (base + temp)."""
    try:
        base = int(getattr(slot, "blade", 0) or 0)
        temp = int(getattr(slot, "temp_blade", 0) or 0)
        return base + temp
    except Exception:
        return 0


def _stage_unit_count_diff_names(gs: Any, cards_db: Dict[str, Any], unit_name: str) -> int:
    """Count stage members with unit_name having DISTINCT cardnames."""
    names_seen = set()
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return 0
        for pos in ("L", "C", "R"):
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, "cardnumber", None)):
                continue
            if not _label_matches_group_or_unit(slot, cards_db, unit_name):
                continue
            name = _card_name(slot, cards_db) or str(getattr(slot, "cardnumber", pos))
            names_seen.add(name)
    except Exception:
        pass
    return len(names_seen)


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------




def _append_ack_confirm(gs: Any, source_cn: str, text: str, detail_text: str = "") -> None:
    try:
        getattr(gs, "pending").append({
            "kind": "confirm_effect",
            "text": str(text or detail_text or "効果を確認してください。"),
            "detail_text": str(detail_text or text or ""),
            "options": ["ok"],
            "ctx": {"source_cn": str(source_cn or ""), "_ack_only": True},
            "source_cn": str(source_cn or ""),
        })
    except Exception:
        pass


def _enqueue_choose_card_from_green_pending(
    gs: Any,
    *,
    candidates: list,
    source_cn: str,
    source_name: str,
    after_ext_key: str,
    label: str,
    detail_text: str = "",
    optional: bool = False,
    allow_skip: bool = False,
    ctx: Dict[str, Any] | None = None,
) -> bool:
    try:
        cns = [str(getattr(c, 'cardnumber', None) or c or '') for c in list(candidates or [])]
        ctx0 = dict(ctx or {})
        detail = str(detail_text or ctx0.get('detail_text') or ctx0.get('effect_text') or '')
        payload = {
            'kind': 'choose_card_from_green',
            'candidates': cns,
            'optional': bool(optional),
            'allow_skip': bool(allow_skip),
            'after_ext_key': str(after_ext_key or '').strip(),
            'source_cn': str(source_cn or ''),
            'label': str(label or f'【{source_name}】控え室からカードを1枚選んでください'),
            'detail_text': detail,
            'ctx': ctx0,
        }
        payload['ctx'].setdefault('source_name', str(source_name or 'カード'))
        if detail:
            payload['ctx'].setdefault('detail_text', detail)
        getattr(gs, 'pending').append(payload)
        try:
            gs.log.append(f"[PENDING] {source_name}: choose from green {cns}")
        except Exception:
            pass
        return True
    except Exception:
        return False


# export underscore helpers explicitly so apply.py can use `from .helpers import *`
__all__ = [name for name, obj in globals().items() if callable(obj) and name.startswith('_')]
