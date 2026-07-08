# -*- coding: utf-8 -*-
# BUILD_TAG: public_reveal_metadata_gate_ext_20260625n
# BUILD_TAG: public_reveal_after_cmd_refresh_seq_compat_20260701ao
"""Public-view reveal policy extension.

Rules implemented here:
- A card that is explicitly revealed and then added to hand remains face-up in
  the public hand display only until MAIN ends.
- ``choose_from_topk`` is NOT public merely because it has ``candidates``.
- Filtered top-k effects generated from text that says "公開して手札に加える"
  are marked with structured metadata at pending-generation time.
- Non-public "look at top N and add to hand" effects such as 優木あんじゅ must
  not become public.

This module monkey-patches narrow hook points instead of replacing core files.
"""
from __future__ import annotations

import importlib
import json
import time
import types
from typing import Any, Dict, List

WRAP_ATTR = "__loveca_public_reveal_ext_wrapped__"
AUTO_REVEAL_ATTR = "_public_hand_auto_reveal_candidates"


def _cn_list(val: Any) -> list[str]:
    out: list[str] = []
    if isinstance(val, list):
        for cn0 in val:
            cn = str(cn0 or "").strip()
            if cn and cn not in out and cn.lower() not in {"skip", "__skip__", "スキップ"}:
                out.append(cn)
    return out


def _inc_counts(cards: list[str]) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for cn in cards:
        d[str(cn)] = d.get(str(cn), 0) + 1
    return d


def _hand_added(before: list[str], after: list[str]) -> list[str]:
    b = _inc_counts(before)
    out: list[str] = []
    for cn in after:
        c = str(cn)
        if after.count(c) > int(b.get(c, 0) or 0) and c not in out:
            out.append(c)
    return out


def _remember_auto_reveals(gs: Any, cards: list[str]) -> None:
    clean = _cn_list(cards)
    if not clean:
        return
    cur = _cn_list(getattr(gs, AUTO_REVEAL_ATTR, []))
    for cn in clean:
        if cn not in cur:
            cur.append(cn)
    try:
        setattr(gs, AUTO_REVEAL_ATTR, cur)
    except Exception:
        pass


def _mark_pending_item_public(item: Any, reason: str) -> None:
    if not isinstance(item, dict) or item.get("kind") != "choose_from_topk":
        return
    item["public_reveal_selected_to_hand"] = True
    item["public_reveal_selected_only"] = True
    item["public_reveal_source_zone"] = "deck_top"
    item["public_reveal_reason"] = reason


def _wrap_filtered_enqueue(fn):
    if getattr(fn, WRAP_ATTR, False):
        return fn

    def wrapped(*args, **kwargs):
        gs = args[0] if args else kwargs.get("gs")
        before_len = len(getattr(gs, "pending", []) or []) if gs is not None else 0
        before_hand = [str(cn) for cn in list(getattr(gs, "hand", []) or [])] if gs is not None else []
        result = fn(*args, **kwargs)
        if gs is None:
            return result
        pending = list(getattr(gs, "pending", []) or [])
        for item in pending[before_len:]:
            _mark_pending_item_public(item, "filtered_topk_public_to_hand")
        # Some filtered top-k effects auto-resolve when exactly one candidate is
        # available.  Preserve that chosen card as public if it was added to hand.
        after_hand = [str(cn) for cn in list(getattr(gs, "hand", []) or [])]
        added = _hand_added(before_hand, after_hand)
        if added:
            _remember_auto_reveals(gs, added)
        return result

    setattr(wrapped, WRAP_ATTR, True)
    setattr(wrapped, "__wrapped__", fn)
    return wrapped


def _patch_filtered_enqueue_symbols() -> None:
    # engine.py is the main path.  engine_effects.py and engine_base.py may hold
    # imported aliases or legacy copies; patch them too if present.
    for mod_name in ("llocg_ui.engine", "llocg_ui.engine_effects", "llocg_ui.engine_base"):
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        fn = getattr(mod, "_enqueue_choose_from_topk_filtered", None)
        if callable(fn):
            setattr(mod, "_enqueue_choose_from_topk_filtered", _wrap_filtered_enqueue(fn))


def _replacement_reveal_candidates(app: Any) -> list[str]:
    """Metadata-gated replacement for App._reveal_candidate_cards_from_pending."""
    out: list[str] = []

    def add_cards(val: Any) -> None:
        for cn in _cn_list(val):
            if cn not in out:
                out.append(cn)

    try:
        pending = list(getattr(app.gs, "pending", []) or [])
    except Exception:
        pending = []

    for item in pending:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "") or item.get("type", "") or "")
        if kind == "show_revealed_cards_ack":
            for key in ("display_cards", "shown", "revealed_cards", "cards", "candidates"):
                add_cards(item.get(key))
            continue

        public_text = "\n".join([
            str(item.get("text", "") or ""),
            str(item.get("effect_text", "") or ""),
            str(item.get("detail_text", "") or ""),
        ])

        if kind == "choose_from_topk":
            metadata_public = bool(item.get("public_reveal_selected_to_hand"))
            explicit_public_to_hand = ("公開" in public_text and "手札" in public_text)
            if not (metadata_public or explicit_public_to_hand):
                continue
            add_cards(item.get("candidates"))
            if not out:
                add_cards(item.get("options"))
            continue

        if kind == "look_top_3way_step":
            # 3-way look effects are private unless explicitly text-marked.
            if not ("公開" in public_text and "手札" in public_text):
                continue
            add_cards(item.get("candidates"))
            if not out:
                add_cards(item.get("options"))
            continue

    return out


def _patch_app_methods(app: Any) -> None:
    # Replace the broad candidates-based detection from older patches.
    app._reveal_candidate_cards_from_pending = types.MethodType(lambda self: _replacement_reveal_candidates(self), app)

    orig_after = getattr(app, "_remember_public_hand_reveals_after_cmd", None)
    if not callable(orig_after) or getattr(orig_after, WRAP_ATTR, False):
        return

    def after_wrapper(
        self,
        before_hand: List[str],
        reveal_candidates: List[str],
        reason: str = "",
        before_refresh_seq: int = 0,
        *args,
        **kwargs,
    ) -> None:
        # BUILD_TAG: public_reveal_after_cmd_refresh_seq_compat_20260701ao
        # Core server.py now passes before_refresh_seq as the 4th explicit
        # argument to suppress false public reveals across refresh.  Older ext
        # hooks accepted only (before_hand, reveal_candidates, reason), causing
        # TypeError on play/next.  Keep auto-reveal merging, but forward the new
        # argument to the bound core method.
        auto = _cn_list(getattr(self.gs, AUTO_REVEAL_ATTR, []))
        try:
            setattr(self.gs, AUTO_REVEAL_ATTR, [])
        except Exception:
            pass
        merged = []
        for cn in list(reveal_candidates or []) + auto:
            if cn not in merged:
                merged.append(cn)
        return orig_after(before_hand, merged, reason, before_refresh_seq, *args, **kwargs)

    setattr(after_wrapper, WRAP_ATTR, True)
    app._remember_public_hand_reveals_after_cmd = types.MethodType(after_wrapper, app)


def apply_app_hook(app: Any) -> None:
    _patch_filtered_enqueue_symbols()
    _patch_app_methods(app)
    try:
        app.gs.log.append("[EXT] public reveal metadata gate active")
    except Exception:
        pass
