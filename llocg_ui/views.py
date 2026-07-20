# -*- coding: utf-8 -*-
# BUILD_TAG: public_view_back_redaction_audit_20260720a
from __future__ import annotations

"""View-state helpers for Loveca UI.

These helpers intentionally operate on the existing ``App.state_json()`` dict so
that the current manual simulator behavior is not disturbed.

- private view: owner operation screen. Keeps current /state behavior.
- public view: share-window candidate. Redacts hand/deck contents and raw pending.
- debug view: master-app/debug candidate. Currently aliases private with metadata.

This module is a first low-risk step toward the final spec's
PrivateViewState/PublicViewState/DebugViewState split.
"""

from copy import deepcopy
import re
from typing import Any, Dict, Iterable, Set


PUBLIC_BUILD_TAG = "public_view_back_redaction_audit_20260720a"


def _as_list(value: Any) -> list:
    return list(value or []) if isinstance(value, (list, tuple)) else []


def _live_set_cards_are_public(state: Dict[str, Any]) -> bool:
    """Return whether current live card storage contents should be face-up.

    Rule reference: cards are placed face-down during live-card set timing
    (8.2.2 / 8.2.4) and are turned face-up at the performance timing
    (8.3.4).  In the current engine, LIVE_CONFIRM before filtering is the
    last face-down moment.  If live_start_prompted is already true, the reveal
    and non-LIVE cleanup have occurred even when phase still says LIVE_CONFIRM
    because live-start pending prompts are being resolved.
    """
    ph = str(state.get("phase", "") or "").upper()
    if ph in {"LIVE_PERF", "LIVE_ATTEMPT", "LIVE_RESOLVE"}:
        return True
    if ph == "LIVE_CONFIRM" and bool(state.get("live_start_prompted", False)):
        return True
    return False


def _public_pending_revealed_cardnumbers(state: Dict[str, Any]) -> Set[str]:
    """Cards that a pending public-reveal acknowledgement is explicitly showing."""
    out: Set[str] = set()
    pending = state.get("pending")
    if not isinstance(pending, list):
        return out
    for item in pending:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "") or item.get("type", "") or "")
        if kind not in {"show_revealed_cards_ack"}:
            continue
        for key in ("display_cards", "shown", "revealed_cards", "cards", "candidates"):
            v = item.get(key)
            if isinstance(v, list):
                for cn in v:
                    if cn:
                        out.add(str(cn))
    return out


def _public_reveal_event_cardnumbers(state: Dict[str, Any]) -> Set[str]:
    out: Set[str] = set()
    events = state.get("public_reveal_events")
    if not isinstance(events, list):
        return out
    for ev in events:
        if not isinstance(ev, dict):
            continue
        v = ev.get("display_cards")
        if isinstance(v, list):
            for cn in v:
                if cn:
                    out.add(str(cn))
    return out


def _public_cardnumbers(state: Dict[str, Any]) -> Set[str]:
    """Return card numbers that are public in the current single-player UI state."""
    out: Set[str] = set()

    for cn in _as_list(state.get("green_room")):
        if cn:
            out.add(str(cn))

    # Live card storage is a public zone, but set cards can temporarily be
    # face-down.  Do not expose card numbers to public view until the engine has
    # reached the reveal timing.
    if _live_set_cards_are_public(state):
        for cn in _as_list(state.get("set_zone")):
            if cn:
                out.add(str(cn))
        rows = _as_list(state.get("set_zone_score_rows"))
        for row in rows:
            if isinstance(row, dict) and row.get("cardnumber"):
                out.add(str(row.get("cardnumber")))

    for cn in _as_list(state.get("resolve_zone")):
        if cn:
            out.add(str(cn))
    for cn in _as_list(state.get("success_zone")):
        if cn:
            out.add(str(cn))

    stage = state.get("stage") or {}
    if isinstance(stage, dict):
        for slot in stage.values():
            if isinstance(slot, dict) and slot.get("cardnumber"):
                out.add(str(slot.get("cardnumber")))

    stage_detail = state.get("stage_detail") or {}
    if isinstance(stage_detail, dict):
        for detail in stage_detail.values():
            if isinstance(detail, dict) and detail.get("cardnumber"):
                out.add(str(detail.get("cardnumber")))

    out.update(_public_pending_revealed_cardnumbers(state))
    out.update(_public_reveal_event_cardnumbers(state))
    # Turn-scoped cards that were revealed while being added to hand remain
    # public even though the rest of the hand is masked.
    for cn in _as_list(state.get("public_hand_revealed_cards")):
        if cn:
            out.add(str(cn))
    events = state.get("public_hand_reveal_events")
    if isinstance(events, list):
        for ev in events:
            if isinstance(ev, dict):
                for cn in _as_list(ev.get("display_cards")):
                    if cn:
                        out.add(str(cn))

    # BUILD_TAG: refresh_notice_popup_20260630af
    # Refresh moves cards from the public waiting room to hidden deck.  The
    # notice itself is public and may list returned LIVE cards, so preserve card
    # metadata maps for those listed cards.
    notices = state.get("refresh_notices")
    if isinstance(notices, list):
        for ev in notices:
            if not isinstance(ev, dict):
                continue
            for item in _as_list(ev.get("returned_live_cards")):
                if isinstance(item, dict) and item.get("cardnumber"):
                    out.add(str(item.get("cardnumber")))
    return out

def _filter_map_by_public_cards(value: Any, public_cards: Set[str]) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(k): v for k, v in value.items() if str(k) in public_cards}


def _pending_title(kind: str) -> str:
    if kind == "show_revealed_cards_ack":
        return "エール公開カード確認"
    if kind == "live_attempt_summary_ack":
        return "ライブ成功確認"
    if kind == "auto_order":
        return "解決順を選択"
    if kind in {"pay_or_skip", "confirm_effect"}:
        return "効果を使いますか？"
    if kind == "choose_effects":
        return "効果を選択"
    if kind in {"confirm_yell_revealed_all_to_green_then_extra_yell"}:
        return "追加エール確認"
    if kind in {"choose_yell_revealed_to_green_then_extra_yell"}:
        return "公開カードを選択"
    if "heart_color" in kind:
        return "ハートの色を選択"
    if "from_green" in kind or "green" in kind:
        return "控え室から選択"
    if "from_hand" in kind or "hand" in kind:
        return "非公開領域から選択中"
    if kind in {"position_change"}:
        return "移動先を選択"
    if kind.startswith("set_opponent_") or "opponent" in kind:
        return "相手情報を指定"
    if kind in {"message_ack", "effect_notice", "mass_bottom_auto_ack", "mass_bottom_optional_result_ack"}:
        return "効果確認"
    return "効果の選択"


def _pending_is_private_hidden(kind: str, item: Dict[str, Any]) -> bool:
    """Return true only for prompts that would expose hidden owner-only zones.

    Public windows should normally mirror the owner popup.  The exception is
    owner-only look/search/reorder prompts such as “look at the top N cards”,
    hand discard/selection, and deck-top placement choices.
    """
    k = str(kind or "").strip()
    private_exact = {
        "choose_from_topk",
        "view_topk_no_match",
        "reorder_topk_keep_any",
        "choose_top_keep_one",
        "self_top1_to_green_or_keep",
        "discard_from_hand",
        "discard_named_cards_from_hand",
        "hand_to_deck_bottom",
        "hand_to_deck_top_or_bottom",
        "choose_deck_top_or_bottom_for_hand_card",
        "choose_deck_top_or_bottom_for_live_storage_card",
        "choose_player_for_deck_top_action",
        "manual_opponent_deck_top_action_notify",
        "topdeck_from_green",
        "bottomdeck_from_green",
    }
    if k in private_exact:
        return True
    # Deck/hand lookup names are owner-only by default unless they are explicit
    # public reveal acknowledgements.
    if k != "show_revealed_cards_ack" and ("topk" in k or "deck_top" in k or "from_hand" in k or "hand_" in k):
        return True
    return False


def _count_candidates(item: Dict[str, Any]) -> tuple[int, int]:
    cand_n = 0
    opt_n = 0
    for key in ("candidates", "cards", "shown", "display_cards"):
        v = item.get(key)
        if isinstance(v, list):
            cand_n = max(cand_n, len(v))
    v = item.get("options")
    if isinstance(v, list):
        opt_n = len(v)
    return cand_n, opt_n


def _public_reveal_event_summary(events: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(events, list):
        return out
    for ev in events:
        if not isinstance(ev, dict):
            continue
        cards = []
        v = ev.get("display_cards")
        if isinstance(v, list):
            for cn0 in v:
                cn_s = str(cn0 or "").strip()
                if cn_s and cn_s not in cards:
                    cards.append(cn_s)
        out.append({
            "kind": str(ev.get("kind", "public_reveal_event") or "public_reveal_event"),
            "title": str(ev.get("title", "公開カード") or "公開カード"),
            "source": "",
            "source_public": False,
            "text": str(ev.get("text", "公開されたカードです。") or "公開されたカードです。"),
            "effect_text": "",
            "display_cards": cards,
            "display_card_count": len(cards),
            "candidate_count": 0,
            "option_count": 0,
            "choice_required": False,
            "seq": ev.get("seq", 0),
        })
    return out



CARDNO_TEXT_RE = re.compile(r"\b(?:PL!|LL)[A-Za-z0-9]*-(?:bp\d+|pb\d+|sd\d+|cl\d+|PR|P\d+)-\d{3}\b", re.IGNORECASE)


def _is_exact_cardno(value: str) -> bool:
    return bool(CARDNO_TEXT_RE.fullmatch(str(value or "").strip()))


def _mask_cardnos_in_public_text(value: str, public_cards: Set[str]) -> str:
    """Mask private-zone card numbers in labels while preserving public ones."""
    text = str(value or "")

    def repl(m: re.Match[str]) -> str:
        cn = m.group(0)
        return cn if cn in public_cards else "非公開カード"

    return CARDNO_TEXT_RE.sub(repl, text)


def _public_sanitize_pending_value(value: Any, public_cards: Set[str], key: str = "") -> Any:
    """Preserve the owner popup payload shape, replacing private cards by backs.

    The public window should render the same modal route as the owner window.
    Only cards that are still in opponent-private zones are masked to __BACK__.
    """
    if isinstance(value, str):
        v = value.strip()
        if _is_exact_cardno(v):
            return v if v in public_cards else "__BACK__"
        return _mask_cardnos_in_public_text(value, public_cards)
    if isinstance(value, list):
        return [_public_sanitize_pending_value(v, public_cards, key) for v in value]
    if isinstance(value, tuple):
        return [_public_sanitize_pending_value(v, public_cards, key) for v in value]
    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        for k, v in value.items():
            ks = str(k)
            safe_key = ks
            if _is_exact_cardno(ks) and ks not in public_cards:
                safe_key = "__BACK__"
            else:
                safe_key = _mask_cardnos_in_public_text(ks, public_cards)
            out[safe_key] = _public_sanitize_pending_value(v, public_cards, ks)
        return out
    return value


def _public_pending_mirror(pending: Any, public_cards: Set[str]) -> list[dict[str, Any]]:
    """Return pending payloads for public view without changing popup semantics.

    Unlike the old summary path, this keeps kind/options/queue/display fields so
    server.py can use the same showPending renderer.  Private card identities are
    replaced with __BACK__ placeholders.
    """
    if not isinstance(pending, list):
        return []
    out: list[dict[str, Any]] = []
    for item in pending:
        if not isinstance(item, dict):
            continue
        safe = _public_sanitize_pending_value(item, public_cards)
        if isinstance(safe, dict):
            safe["public_sanitized"] = True
            out.append(safe)
    return out

def _public_pending_summary(pending: Any, public_cards: Set[str]) -> list[dict[str, Any]]:
    """Mirror public-safe pending windows and hide only private-zone prompts."""
    out: list[dict[str, Any]] = []
    if not isinstance(pending, list):
        return out
    for item in pending:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "") or item.get("type", "") or "pending")
        raw_source = str(item.get("source", "") or item.get("cardnumber", "") or item.get("source_card", "") or "")
        source_public = bool(raw_source and raw_source in public_cards)
        source = raw_source if source_public else ""
        hidden = _pending_is_private_hidden(kind, item)

        raw_effect = str(item.get("effect_text", "") or item.get("effect", "") or "")
        raw_text = str(item.get("text", "") or item.get("message", "") or item.get("prompt", "") or item.get("description", "") or item.get("after_effect_template", "") or "")

        if hidden:
            text = "メイン画面で非公開領域のカードを確認・選択しています。"
            effect_text = raw_effect if source_public else ""
        else:
            text = raw_text or raw_effect or "効果を処理しています。"
            effect_text = raw_effect

        public_display_cards: list[str] = []
        if not hidden:
            for key in ("display_cards", "shown", "revealed_cards", "cards"):
                v = item.get(key)
                if isinstance(v, list):
                    for cn0 in v:
                        cn_s = str(cn0 or "").strip()
                        if cn_s and (cn_s in public_cards or kind == "show_revealed_cards_ack"):
                            public_display_cards.append(cn_s)

        seen_display: set[str] = set()
        public_display_cards = [x for x in public_display_cards if not (x in seen_display or seen_display.add(x))]

        public_options: list[str] = []
        if not hidden:
            v = item.get("options")
            if isinstance(v, list):
                for opt in v:
                    opt_s = str(opt or "").strip()
                    if opt_s:
                        public_options.append(opt_s)

        cand_n, opt_n = _count_candidates(item)
        out.append({
            "kind": kind,
            "title": _pending_title(kind),
            "source": source,
            "source_public": source_public,
            "text": text,
            "effect_text": effect_text,
            "display_cards": public_display_cards,
            "display_card_count": len(public_display_cards),
            "candidate_count": 0 if hidden else cand_n,
            "option_count": 0 if hidden else (len(public_options) or opt_n),
            "options": public_options,
            "choice_required": True,
            "public_hidden": bool(hidden),
            "yell_draw_icon_count": item.get("yell_draw_icon_count", 0),
            "yell_draw_drew_count": item.get("yell_draw_drew_count", 0),
            "yell_draw_notice_label": item.get("yell_draw_notice_label", ""),
            "yell_draw_notice_text": item.get("yell_draw_notice_text", ""),
            "condition_status": item.get("condition_status", None),
            "result": item.get("result", ""),
            "live_attempt_summary": deepcopy(item.get("live_attempt_summary", {})) if isinstance(item.get("live_attempt_summary", {}), dict) else {},
        })
    return out


def make_private_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return owner/private view.  Currently the existing state with metadata."""
    out = deepcopy(state)
    out["view_mode"] = "private"
    out["view_build_tag"] = PUBLIC_BUILD_TAG
    return out


def make_public_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a share-window-safe state candidate.

    This is intentionally conservative: it removes hand/deck contents, hand-only
    cost details, raw pending payloads, and card-name maps for non-public cards.
    """
    src = deepcopy(state)
    public_cards = _public_cardnumbers(src)

    deck_count = len(_as_list(src.get("deck")))
    hand_count = len(_as_list(src.get("hand")))

    src["view_mode"] = "public"
    src["view_build_tag"] = PUBLIC_BUILD_TAG

    # Redact owner-only / secret zones.
    src["deck_count"] = deck_count
    src["hand_count"] = hand_count
    src["deck"] = []
    src["hand"] = []
    src["hand_detail"] = []

    # Preserve public board zones.  green_room contents are public by current spec.
    src["green_room_count"] = len(_as_list(src.get("green_room")))
    live_set_count = len(_as_list(src.get("set_zone")))
    live_set_public = _live_set_cards_are_public(src)
    src["set_zone_count"] = live_set_count
    src["set_zone_public"] = bool(live_set_public)
    if not live_set_public:
        # Face-down live storage: expose only count and placeholder backs.
        src["set_zone"] = ["__BACK__" for _ in range(live_set_count)]
        src["set_zone_score_rows"] = [None for _ in range(live_set_count)]
    src["resolve_zone_count"] = len(_as_list(src.get("resolve_zone")))
    src["success_zone_count"] = len(_as_list(src.get("success_zone")))

    # Preserve the actual pending payload shape so the public window can use the
    # same modal renderer as the owner window.  Only private-zone card identities
    # are replaced with card backs.
    src["pending"] = _public_pending_mirror(src.get("pending"), public_cards)
    src["public_pending"] = []
    src["public_reveal_events"] = _public_reveal_event_summary(src.get("public_reveal_events"))

    # Card-number maps are useful for rendering but must not expose hand/deck.
    for key in ["cn2name", "cn2label", "cn2type", "cn2is_live", "cn2yell_hearts", "cn2yell_draw_icons", "cn2yell_score_icons", "cn2group", "cn2unit", "cn2cost", "cn2score"]:
        src[key] = _filter_map_by_public_cards(src.get(key), public_cards)

    # Debug internals should not be part of share view.
    src["debug"] = False
    src.pop("root", None)

    return src


def make_master_debug_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return master/debug view.  Placeholder for future richer debug shaping."""
    out = deepcopy(state)
    out["view_mode"] = "debug"
    out["view_build_tag"] = PUBLIC_BUILD_TAG
    return out


def make_view_state(state: Dict[str, Any], mode: str = "private") -> Dict[str, Any]:
    m = str(mode or "private").strip().lower()
    if m in {"public", "share", "shared"}:
        return make_public_state(state)
    if m in {"debug", "master"}:
        return make_master_debug_state(state)
    return make_private_state(state)
