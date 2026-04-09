# -*- coding: utf-8 -*-
# BUILD_TAG: live_set_limit_ui_20260409a
from __future__ import annotations

"""llocg_ui.server

Manual UI web server for LLCG.

Endpoints (kept compatible with the existing "jank" engine API):
- GET  /          : UI HTML
- GET  /state     : JSON state
- POST /cmd       : mutate state (cmd + payload)
- GET  /img?cn=   : card image
- GET  /playmat   : playmat.jpg

This file intentionally keeps the rule/engine logic inside llocg_ui.engine ("jank engine")
unchanged, and only replaces the front-end with a cleaner, more stable UI.

Key goals:
- No "Illegal return statement" (JS is wrapped in an IIFE).
- Card image orientation is consistent:
  * When a zone wants portrait and the card is LIVE (landscape), rotate +90° (CW).
  * When a zone wants landscape and the card is MEMBER (portrait), rotate -90° (CCW).
- Large stacks (resolve / green room) are scrollable and do not overflow the viewport.
- HEAD requests are supported (curl -I works).
"""

import json
import time
import os
import re
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs, unquote

from .db import load_cards_db, is_member_type, is_live_type, _get_card as _db_get_card
from .images import ImageLocator
from .engine import (
    new_game,
    push_undo,
    do_undo,
    cmd_play,
    cmd_set,
    cmd_yell,
    cmd_attempt,
    cmd_ack,
    cmd_end_turn,
    cmd_next,
    cmd_activate_to_green,
    cmd_toggle_stage_active,
    cmd_resolve_pending,
    post_process,
    _get_card,
    _has_sacrifice_ability,
    can_activate_in_state,
    StageSlot,
)

APP_VERSION = "texticon_stack_overlay_20260408f_livequeue_reqicons"


def _write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding=encoding)


class App:
    def __init__(
        self,
        root: Path,
        code: str,
        deck_code: str,
        seed: int,
        debug: bool,
        compiled: Optional[Path] = None,
        tokv1: Optional[Path] = None,
    ):
        self.root = Path(root)
        self.outdir = self.root / "sim_out"
        self.cards_db = load_cards_db(self.root, compiled_path=compiled, tokv1_path=tokv1)
        self.img = ImageLocator(self.root)
        self.ui_code = str(code)
        self.deck_code = str(deck_code)
        self.gs, self.rng = new_game(self.root, self.deck_code, seed=seed, debug=debug)
        self._force_mulligan_start()
        self._apply_start_overrides_from_env()
        self.save_trace()

    def save_trace(self) -> None:
        self.outdir.mkdir(parents=True, exist_ok=True)
        _write_text(self.outdir / "ui_trace.txt", "\n".join(self.gs.log) + ("\n" if self.gs.log else ""))


    def _force_mulligan_start(self) -> None:
        """Force MULLIGAN state at boot (spec).

        - Deal opening 6 cards.
        - Phase becomes 'MULLIGAN' (user selects any number to redraw).
        - After decision, UI calls cmd 'mulligan_next' which redraws and auto-starts Turn 1.
        """
        gs = self.gs
        try:
            if str(getattr(gs, 'phase', '')).upper() == 'MULLIGAN':
                return
        except Exception:
            pass

        # Return any existing hand to deck, then shuffle and draw 6
        try:
            deck = list(getattr(gs, 'deck', []) or [])
        except Exception:
            deck = []
        try:
            hand = list(getattr(gs, 'hand', []) or [])
        except Exception:
            hand = []
        deck.extend(hand)
        try:
            self.rng.shuffle(deck)
        except Exception:
            pass

        new_hand = []
        for _ in range(6):
            if not deck:
                break
            new_hand.append(deck.pop(0))

        try:
            gs.deck = deck
            gs.hand = new_hand
        except Exception:
            pass

        # Reset baseline before Turn 1
        try:
            gs.turn = 0
            gs.phase = 'MULLIGAN'
            gs.energy_active = 3
            gs.energy_wait = 0
        except Exception:
            pass

        # Clear any leftover stacks/pending defensively
        for k in ('set_zone','resolve_zone','pending'):
            try:
                v = getattr(gs, k, None)
                if isinstance(v, list):
                    v.clear()
                elif v is not None:
                    setattr(gs, k, [])
            except Exception:
                pass

        try:
            gs.log.append('[PHASE] MULLIGAN (choose cards to redraw)')
        except Exception:
            pass

    def _apply_start_overrides_from_env(self) -> None:
        """Apply debug start overrides from environment variables.

        Supported env vars:
          - LLOCG_START_HAND: comma/space separated cardnumbers to force into opening hand
          - LLOCG_START_HAND_SIZE: target hand size after forcing (0 = do not fill)
          - LLOCG_START_ENERGY_ACTIVE / LLOCG_START_ENERGY_WAIT
          - LLOCG_START_TURN (int), LLOCG_START_PHASE (e.g. MAIN/MULLIGAN)
          - LLOCG_START_SHUFFLE: '1' to shuffle deck after removing forced hand
          - LLOCG_START_DEBUG: '1' to enable gs.debug

        Notes:
          - Debug-only: mutates GameState directly.
          - Energy is capped by gs.energy_total (default 12) minus stage under-energy.
        """
        env = os.environ
        gs = self.gs

        preset_s = (env.get('LLOCG_DEBUG_PRESET') or '').strip().lower()
        effect_card_s = (env.get('LLOCG_DEBUG_EFFECT_CARD') or '').strip()
        debug_energy_cap_s = (env.get('LLOCG_DEBUG_ENERGY_CAP') or '').strip()

        hand_spec = (env.get('LLOCG_START_HAND') or '').strip()
        e_active_s = (env.get('LLOCG_START_ENERGY_ACTIVE') or '').strip()
        e_wait_s = (env.get('LLOCG_START_ENERGY_WAIT') or '').strip()
        turn_s = (env.get('LLOCG_START_TURN') or '').strip()
        phase_s = (env.get('LLOCG_START_PHASE') or '').strip()
        hand_size_s = (env.get('LLOCG_START_HAND_SIZE') or '').strip()
        shuffle_s = (env.get('LLOCG_START_SHUFFLE') or '').strip()
        debug_s = (env.get('LLOCG_START_DEBUG') or '').strip()

        # Optional richer injections for faster effect testing
        green_spec = (env.get('LLOCG_START_GREEN') or '').strip()        # waiting room
        success_spec = (env.get('LLOCG_START_SUCCESS') or '').strip()    # success live storage
        decktop_spec = (env.get('LLOCG_START_DECK_TOP') or '').strip()   # put these on top of deck (leftmost = top)
        deckexact_spec = (env.get('LLOCG_START_DECK_EXACT') or '').strip() # replace deck exactly (leftmost = top)
        resolve_spec = (env.get('LLOCG_START_RESOLVE') or '').strip()    # resolve zone (cheer)
        stage_spec = (env.get('LLOCG_START_STAGE') or '').strip()        # e.g., "C=CN,L=CN2" or "C:CN"
        stage_l = (env.get('LLOCG_START_STAGE_L') or '').strip()
        stage_c = (env.get('LLOCG_START_STAGE_C') or '').strip()
        stage_r = (env.get('LLOCG_START_STAGE_R') or '').strip()

        if (not hand_spec) and effect_card_s:
            # Convenience: single card effect test
            hand_spec = effect_card_s

        any_override = any([
            preset_s,
            hand_spec, e_active_s, e_wait_s, turn_s, phase_s, hand_size_s, shuffle_s, debug_s,
            green_spec, decktop_spec, deckexact_spec, resolve_spec,
            stage_spec, stage_l, stage_c, stage_r,
        ])
        if not any_override:
            return

        def _as_int(s: str, default: int) -> int:
            try:
                return int(str(s).strip())
            except Exception:
                return default

        # Debug energy_total override (safe: only affects debug preset / explicit env var)
        if preset_s == 'effect' or debug_energy_cap_s:
            cap_v = _as_int(debug_energy_cap_s, 0) if debug_energy_cap_s else 0
            if cap_v > 0:
                try:
                    gs.energy_total = cap_v
                except Exception:
                    pass

        # Presets (safe defaults for effect implementation/testing)
        if preset_s == 'effect':
            # Start directly in MAIN with ample energy, and auto-provide cards needed to test the effect quickly.
            # - Default energy cap is 99 (debug only). Normal rule cap (12) is kept unless preset/evar overrides it.
            # - Do NOT add random cards to zones; only add what is required / explicitly requested.
            if not debug_s:
                try:
                    gs.debug = True
                except Exception:
                    pass
            if not phase_s:
                try:
                    gs.phase = 'MAIN'
                except Exception:
                    pass
            if not turn_s:
                try:
                    gs.turn = 1
                except Exception:
                    pass

            # Debug energy cap (default 99) and starting energy
            if not debug_energy_cap_s:
                debug_energy_cap_s = '99'
            if (not e_active_s) and (not e_wait_s):
                e_active_s = debug_energy_cap_s
                e_wait_s = '0'

            # Keep only forced cards by default; we'll append required extras later.
            if not hand_size_s:
                hand_size_s = '0'

            # Clear zones unless explicitly provided by env (avoid confusing random contents).
            if not green_spec:
                try:
                    gs.green_room = []
                except Exception:
                    pass
            if not success_spec:
                try:
                    gs.success_zone = []
                except Exception:
                    pass
            if not resolve_spec:
                try:
                    gs.resolve_zone = []
                except Exception:
                    pass
            if not decktop_spec:
                # no-op; keep deck order
                pass
        # Phase / turn
        if turn_s:
            try:
                gs.turn = _as_int(turn_s, int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                pass

        target_phase = ''
        if phase_s:
            target_phase = str(phase_s).strip().upper()
            try:
                gs.phase = target_phase
            except Exception:
                pass
        else:
            try:
                target_phase = str(getattr(gs, 'phase', '') or '').upper()
            except Exception:
                target_phase = ''

        # Hand target size defaults
        if hand_size_s:
            target_hand_size = _as_int(hand_size_s, 7)
        else:
            target_hand_size = 6 if target_phase == 'MULLIGAN' else 7
        if target_hand_size < 0:
            target_hand_size = 0

        # Debug flag
        if debug_s:
            try:
                gs.debug = str(debug_s).strip() in ('1','true','TRUE','yes','YES')
            except Exception:
                pass

        def _split_cards(spec: str) -> list[str]:
            if not spec:
                return []
            return [t for t in re.split(r'[\s,]+', spec) if t]

        # Forced hand
        forced = []
        if hand_spec:
            forced = _split_cards(hand_spec)

        if forced:
            try:
                deck = list(getattr(gs, 'deck', []) or [])
            except Exception:
                deck = []
            new_hand = []
            for cn in forced:
                try:
                    deck.remove(cn)
                except ValueError:
                    pass
                new_hand.append(cn)

            if shuffle_s.strip() in ('1','true','TRUE','yes','YES'):
                try:
                    self.rng.shuffle(deck)
                except Exception:
                    pass

            if target_hand_size > 0:
                while len(new_hand) < target_hand_size and deck:
                    new_hand.append(deck.pop(0))

            try:
                gs.deck = deck
                gs.hand = new_hand
            except Exception:
                pass
        elif hand_size_s:
            # size change only
            try:
                deck = list(getattr(gs, 'deck', []) or [])
            except Exception:
                deck = []
            try:
                hand = list(getattr(gs, 'hand', []) or [])
            except Exception:
                hand = []
            if target_hand_size > 0:
                if len(hand) > target_hand_size:
                    extras = hand[target_hand_size:]
                    hand = hand[:target_hand_size]
                    deck = list(extras) + deck
                while len(hand) < target_hand_size and deck:
                    hand.append(deck.pop(0))
                try:
                    gs.deck = deck
                    gs.hand = hand
                except Exception:
                    pass


        # If using the "effect" preset, auto-provide cards needed to reach/trigger the effect quickly.
        if preset_s == 'effect':
            # Helpers to classify cards
            def _ci(cn: str):
                try:
                    return _db_get_card(self.cards_db, cn)
                except Exception:
                    return None

            def _is_live(cn: str) -> bool:
                ci = _ci(cn)
                try:
                    return bool(ci) and is_live_type(getattr(ci, 'type', '') or '')
                except Exception:
                    return False

            def _is_member(cn: str) -> bool:
                ci = _ci(cn)
                try:
                    return bool(ci) and is_member_type(getattr(ci, 'type', '') or '')
                except Exception:
                    return False

            def _pick_from_deck(deck_list: list[str], pred, n: int) -> list[str]:
                out = []
                if n <= 0:
                    return out
                i = 0
                # deterministic: keep deck order
                while i < len(deck_list) and len(out) < n:
                    cn = deck_list[i]
                    if pred(cn):
                        out.append(cn)
                        deck_list.pop(i)
                        continue
                    i += 1
                return out

            # Extract effect templates from the target effect card to infer required green-room candidates.
            need_green_members = 0
            need_green_live = []  # list of (group, n)
            tgt = effect_card_s.strip()
            if tgt:
                ci_t = _ci(tgt)
                abilities = getattr(ci_t, 'abilities', []) if ci_t else []
                tpls = []
                for ab in abilities or []:
                    if not isinstance(ab, dict):
                        continue
                    ar = ab.get('ability_raw')
                    if isinstance(ar, dict):
                        clauses = ar.get('clauses')
                        if isinstance(clauses, list):
                            for cl in clauses:
                                if isinstance(cl, dict):
                                    et = cl.get('effect_template')
                                    if et:
                                        tpls.append(str(et))
                    # fallback: sometimes effect_template sits directly on ability dict
                    if ab.get('effect_template'):
                        tpls.append(str(ab.get('effect_template')))
                for tpl in tpls:
                    m = re.search(r'控え室にあるメンバーカード(\d+)枚', tpl)
                    if m:
                        try:
                            need_green_members = max(need_green_members, int(m.group(1)))
                        except Exception:
                            pass
                    m0 = re.search(r'控え室からメンバーカードを(\d+)枚手札に加える', tpl)
                    if m0:
                        try:
                            need_green_members = max(need_green_members, int(m0.group(1)))
                        except Exception:
                            pass
                    m2 = re.search(r'控え室にある『([^』]+)』のライブカード(\d+)枚', tpl)
                    if m2:
                        g = str(m2.group(1)).strip()
                        try:
                            n = int(m2.group(2))
                        except Exception:
                            n = 0
                        if g and n > 0:
                            need_green_live.append((g, n))

            # Mutate deck/hand/green deterministically.
            try:
                deck = list(getattr(gs, 'deck', []) or [])
            except Exception:
                deck = []
            try:
                hand = list(getattr(gs, 'hand', []) or [])
            except Exception:
                hand = []
            try:
                green = list(getattr(gs, 'green_room', []) or [])
            except Exception:
                green = []

            # Ensure the target effect card is present (if specified but not in hand yet)
            if tgt and (tgt not in hand) and (tgt in deck):
                try:
                    deck.remove(tgt)
                except Exception:
                    pass
                hand.append(tgt)

            # Always give enough LIVE cards to reach live-start abilities quickly.
            live_min = _as_int(os.environ.get('LLOCG_DEBUG_LIVE_IN_HAND') or '', 3)
            if live_min <= 0:
                live_min = 0
            have_live = sum(1 for cn in hand if _is_live(cn))
            if have_live < live_min:
                hand.extend(_pick_from_deck(deck, _is_live, live_min - have_live))

            # Provide extra MEMBER cards to populate stage easily (default 2).
            mem_min = _as_int(os.environ.get('LLOCG_DEBUG_MEMBER_IN_HAND') or '', 2)
            if mem_min <= 0:
                mem_min = 0
            have_mem = sum(1 for cn in hand if _is_member(cn))
            if have_mem < mem_min:
                hand.extend(_pick_from_deck(deck, _is_member, mem_min - have_mem))

            # Green room candidates inferred from effect template (only if user didn't specify LLOCG_START_GREEN)
            if (not green_spec) and need_green_members > 0:
                green.extend(_pick_from_deck(deck, _is_member, need_green_members))

            if (not green_spec) and need_green_live:
                for g, n in need_green_live:
                    def _pred_live_group(cn: str) -> bool:
                        ci = _ci(cn)
                        if not ci:
                            return False
                        try:
                            if not is_live_type(getattr(ci, 'type', '') or ''):
                                return False
                            grp = str(getattr(ci, 'group', '') or '')
                            return grp == g
                        except Exception:
                            return False
                    green.extend(_pick_from_deck(deck, _pred_live_group, n))

            try:
                gs.deck = deck
                gs.hand = hand
                gs.green_room = green
            except Exception:
                pass

        # Energy overrides with cap
        if e_active_s or e_wait_s:
            try:
                active0 = int(getattr(gs, 'energy_active', 0) or 0)
            except Exception:
                active0 = 0
            try:
                wait0 = int(getattr(gs, 'energy_wait', 0) or 0)
            except Exception:
                wait0 = 0
            active = _as_int(e_active_s, active0) if e_active_s else active0
            wait = _as_int(e_wait_s, wait0) if e_wait_s else wait0
            if active < 0: active = 0
            if wait < 0: wait = 0

            under = 0
            try:
                st = getattr(gs, 'stage', None)
                if isinstance(st, dict):
                    for v in st.values():
                        if v is None:
                            continue
                        try:
                            under += int(getattr(v, 'energy_under', 0) or 0)
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                total_cap = int(getattr(gs, 'energy_total', 12) or 12)
            except Exception:
                total_cap = 12
            cap = max(0, total_cap - under)
            total = active + wait
            if total > cap:
                overflow = total - cap
                if wait >= overflow:
                    wait -= overflow
                else:
                    overflow -= wait
                    wait = 0
                    active = max(0, active - overflow)
            try:
                gs.energy_active = active
                gs.energy_wait = wait
            except Exception:
                pass

        # Stage injection (L/C/R)
        # Priority: explicit per-slot env > stage_spec
        st_map: Dict[str, str] = {}
        if stage_spec:
            for part in re.split(r'[;,]+', stage_spec):
                p = part.strip()
                if not p:
                    continue
                if '=' in p:
                    k, v = p.split('=', 1)
                elif ':' in p:
                    k, v = p.split(':', 1)
                else:
                    continue
                kk = str(k).strip().upper()
                vv = str(v).strip()
                if kk in ('L','C','R') and vv:
                    st_map[kk] = vv
        if stage_l:
            st_map['L'] = stage_l
        if stage_c:
            st_map['C'] = stage_c
        if stage_r:
            st_map['R'] = stage_r

        if st_map:
            # Remove injected cards from zones/deck to avoid accidental duplicates
            try:
                deck = list(getattr(gs, 'deck', []) or [])
            except Exception:
                deck = []
            try:
                hand = list(getattr(gs, 'hand', []) or [])
            except Exception:
                hand = []
            try:
                gr = list(getattr(gs, 'green_room', []) or [])
            except Exception:
                gr = []
            for pos, cn in st_map.items():
                # strip one occurrence
                try:
                    if cn in deck:
                        deck.remove(cn)
                except Exception:
                    pass
                try:
                    if cn in hand:
                        hand.remove(cn)
                except Exception:
                    pass
                try:
                    if cn in gr:
                        gr.remove(cn)
                except Exception:
                    pass

                try:
                    gs.stage[pos] = StageSlot(cardnumber=cn, active=True)
                except Exception:
                    pass

            try:
                gs.deck = deck
                gs.hand = hand
                gs.green_room = gr
            except Exception:
                pass

        # Green room injection (append)
        if green_spec:
            add = _split_cards(green_spec)
            if add:
                try:
                    deck = list(getattr(gs, 'deck', []) or [])
                except Exception:
                    deck = []
                for cn in add:
                    try:
                        if cn in deck:
                            deck.remove(cn)
                    except Exception:
                        pass
                try:
                    gs.deck = deck
                except Exception:
                    pass
                try:
                    gs.green_room.extend(add)
                except Exception:
                    pass

        # Success live storage injection (append)
        if success_spec:
            add = _split_cards(success_spec)
            if add:
                try:
                    deck = list(getattr(gs, 'deck', []) or [])
                except Exception:
                    deck = []
                try:
                    sz = list(getattr(gs, 'success_zone', []) or [])
                except Exception:
                    sz = []
                for cn in add:
                    try:
                        if cn in deck:
                            deck.remove(cn)
                    except Exception:
                        pass
                    sz.append(cn)
                try:
                    gs.deck = deck
                    gs.success_zone = sz
                except Exception:
                    pass


        # Resolve zone injection (overwrite)
        if resolve_spec:
            add = _split_cards(resolve_spec)
            if add:
                try:
                    deck = list(getattr(gs, 'deck', []) or [])
                except Exception:
                    deck = []
                for cn in add:
                    try:
                        if cn in deck:
                            deck.remove(cn)
                    except Exception:
                        pass
                try:
                    gs.deck = deck
                except Exception:
                    pass
                try:
                    gs.resolve_zone = list(add)
                except Exception:
                    pass

        # Replace deck exactly (leftmost = top). Debug-only convenience.
        # Cards removed from the original deck are moved to waiting room,
        # so total card count is preserved for refresh tests.
        if deckexact_spec:
            exact_cards = _split_cards(deckexact_spec)
            try:
                cur_deck = list(getattr(gs, 'deck', []) or [])
            except Exception:
                cur_deck = []
            try:
                cur_green = list(getattr(gs, 'green_room', []) or [])
            except Exception:
                cur_green = []

            rest = list(cur_deck)
            for cn in exact_cards:
                try:
                    rest.remove(cn)
                except Exception:
                    pass

            try:
                gs.deck = list(exact_cards)
            except Exception:
                pass
            try:
                gs.green_room = list(cur_green) + list(rest)
            except Exception:
                pass

        # Put specified cards on TOP of deck (leftmost = top)
        if decktop_spec:
            top_cards = _split_cards(decktop_spec)
            if top_cards:
                try:
                    deck = list(getattr(gs, 'deck', []) or [])
                except Exception:
                    deck = []
                for cn in top_cards:
                    try:
                        if cn in deck:
                            deck.remove(cn)
                    except Exception:
                        pass
                deck = list(top_cards) + deck
                try:
                    gs.deck = deck
                except Exception:
                    pass

        # Log summary
        try:
            e_total = int(getattr(gs, 'energy_total', 12) or 12)
        except Exception:
            e_total = 12
        try:
            e_a = int(getattr(gs, 'energy_active', 0) or 0)
        except Exception:
            e_a = 0
        try:
            e_w = int(getattr(gs, 'energy_wait', 0) or 0)
        except Exception:
            e_w = 0
        try:
            h = list(getattr(gs, 'hand', []) or [])
        except Exception:
            h = []
        try:
            ph = str(getattr(gs, 'phase', '') or '')
        except Exception:
            ph = ''
        try:
            tr = int(getattr(gs, 'turn', 0) or 0)
        except Exception:
            tr = 0
        try:
            gs.log.append(f'[DEBUG_START] phase={ph} turn={tr} hand={len(h)} E={e_a}/{e_total} wait={e_w}')
        except Exception:
            pass

    def _cmd_mulligan_next(self, indices: list[int]) -> None:
        """Apply mulligan redraw, then auto-start Turn 1 per spec."""
        gs = self.gs
        try:
            n = len(gs.hand)
        except Exception:
            n = 0
        idxs = []
        for x in indices:
            try:
                i = int(x)
            except Exception:
                continue
            if 0 <= i < n:
                idxs.append(i)
        idxs = sorted(set(idxs))
        idxset = set(idxs)

        try:
            removed = [gs.hand[i] for i in idxs]
            keep = [c for j,c in enumerate(gs.hand) if j not in idxset]
        except Exception:
            removed = []
            keep = list(getattr(gs, 'hand', []) or [])

        draw_n = len(removed)
        drawn = []
        try:
            for _ in range(draw_n):
                if not gs.deck:
                    break
                drawn.append(gs.deck.pop(0))
        except Exception:
            pass

        try:
            gs.hand = keep + drawn
        except Exception:
            pass

        try:
            gs.deck.extend(removed)
        except Exception:
            pass
        try:
            self.rng.shuffle(gs.deck)
        except Exception:
            pass

        try:
            gs.log.append(f'[MULLIGAN] redraw={draw_n}')
        except Exception:
            pass

        # Auto-start Turn 1: energy 4/4, draw 1, enter MAIN
        try:
            gs.turn = 1
            gs.energy_active = 4
            gs.energy_wait = 0
        except Exception:
            pass
        try:
            if gs.deck:
                gs.hand.append(gs.deck.pop(0))
        except Exception:
            pass
        try:
            gs.phase = 'MAIN'
            gs.log.append('[PHASE] MAIN turn=1 (auto after mulligan)')
        except Exception:
            pass

    def _all_cardnumbers_in_state(self) -> list[str]:
        gs = getattr(self, "gs", None)
        if gs is None:
            return []
        cns: set[str] = set()

        def _add(items: Any) -> None:
            if not items:
                return
            try:
                for it in items:
                    if it is None:
                        continue
                    if isinstance(it, str):
                        cns.add(it)
                    else:
                        cn = getattr(it, "cardnumber", None) or getattr(it, "cn", None)
                        if isinstance(cn, str) and cn:
                            cns.add(cn)
            except Exception:
                return

        _add(getattr(gs, "hand", None))
        _add(getattr(gs, "green_room", None))
        _add(getattr(gs, "set_zone", None))
        _add(getattr(gs, "resolve_zone", None))
        _add(getattr(gs, "deck", None))

        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                _add(st.values())
        except Exception:
            pass

        try:
            for item in getattr(gs, "pending", []) or []:
                if not isinstance(item, dict):
                    continue
                _add(item.get("candidates"))
                _add(item.get("cards"))
                _add(item.get("shown"))
                _add(item.get("display_cards"))
        except Exception:
            pass

        return sorted(cns)

    def _cn2type(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci and getattr(ci, "type", None):
                out[cn] = str(ci.type)
        return out

    def _cn2name(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci and getattr(ci, "name", None):
                out[cn] = str(ci.name)
        return out

    def _cn2label(self) -> Dict[str, str]:
        def _exp_token(cardnumber: str) -> str:
            try:
                s = cardnumber.split("!", 1)[1]
                return s.split("-", 1)[0]
            except Exception:
                return ""

        cn2type = self._cn2type()
        out: Dict[str, str] = {}

        cns: set[str] = set(self._all_cardnumbers_in_state())
        for p in getattr(self.gs, "pending", []) or []:
            if not isinstance(p, dict):
                continue
            for opt in (p.get("options") or []):
                if isinstance(opt, str) and "PL!" in opt:
                    cns.add(opt)

        for cn in sorted(cns):
            ci = _get_card(self.cards_db, cn)
            if not ci or not getattr(ci, "name", None):
                continue
            t = cn2type.get(cn, "")
            if t == "LIVE":
                out[cn] = str(ci.name)
            else:
                exp = _exp_token(cn)
                cost = getattr(ci, "cost", None)
                try:
                    cost_s = str(int(cost)) if cost is not None else "?"
                except Exception:
                    cost_s = "?"
                out[cn] = f"{exp}/{cost_s}/{ci.name}" if exp else f"{cost_s}/{ci.name}"
        return out

    def state_json(self) -> Dict[str, Any]:
        now = time.time()
        banner = None
        if getattr(self.gs, "banner_text", "") and (
            now - getattr(self.gs, "banner_ts", 0.0) <= getattr(self.gs, "banner_ttl", 0.0)
        ):
            banner = {"text": self.gs.banner_text}

        return {
            "root": str(self.gs.root),
            "code": self.ui_code,
            "deck_code": self.deck_code,
            "seed": self.gs.seed,
            "debug": self.gs.debug,
            "turn": self.gs.turn,
            "phase": self.gs.phase,
            "deck": self.gs.deck if self.gs.debug else ["?"] * len(self.gs.deck),
            "hand": list(self.gs.hand),
            "energy_active": int(self.gs.energy_active),
            "energy_wait": int(self.gs.energy_wait),
            "stage": {k: (asdict(v) if v else None) for k, v in self.gs.stage.items()},
            "green_room": list(self.gs.green_room),
            "set_zone": list(self.gs.set_zone),
            "live_set_limit": int(getattr(self.gs, "current_live_set_limit", 3) or 3),
            "set_zone_score_rows": self._set_zone_score_rows_for_ui(),
            "resolve_zone": list(self.gs.resolve_zone),
            "success_zone": list(getattr(self.gs, "success_zone", []) or []),
            "pending": list(self.gs.pending),
            "cn2name": self._cn2name(),
            "cn2label": self._cn2label(),
            "cn2type": self._cn2type(),
            "stage_detail": {
                k: (
                    {
                        "cardnumber": v.cardnumber,
                        "name": (_get_card(self.cards_db, v.cardnumber).name if _get_card(self.cards_db, v.cardnumber) else ""),
                        "type": (_get_card(self.cards_db, v.cardnumber).type if _get_card(self.cards_db, v.cardnumber) else ""),
                        "has_sac": _has_sacrifice_ability(_get_card(self.cards_db, v.cardnumber)),
                        "energy_under": int(getattr(v, "energy_under", 0) or 0),
                        "can_activate": can_activate_in_state(self.gs, self.cards_db, k),
                        # 一時的なブレード/ハート増加（UIアイコン表示用）
                        "temp_blade": int(getattr(v, "temp_blade", 0) or 0),
                        "temp_hearts": dict(getattr(v, "temp_hearts", {}) or {}),
                        "always_hearts_bonus": dict(self._always_hearts_bonus_for(k, v) or {}),
                        # 常時BODYブレード加算（コスト13以上条件）
                        "always_blade_bonus": self._always_blade_bonus_for(k, v),
                        "always_score_bonus": self._always_score_bonus_for(k, v),
                        # PL!N-bp1-012 ランジュのライブ中ボーナス（UIアイコン表示用）
                        "lanzhu_blade_bonus": self._lanzhu_blade_bonus_for(k, v),
                        "lanzhu_heart_bonus": self._lanzhu_heart_bonus_for(k, v),
                    }
                    if v
                    else None
                )
                for k, v in self.gs.stage.items()
            },
            "log": list(self.gs.log),
            "banner": banner,
            "ui_version": APP_VERSION,
        }
    def _set_zone_score_rows_for_ui(self):
        """Return per-card score breakdown rows parallel to set_zone for UI/debug display.

        Each element is either None or a dict: {cardnumber, base, delta, score}.
        Only LIVE cards in set_zone receive rows; non-LIVE entries stay None.
        """
        from .engine import _compute_attempt_score_breakdown, _effective_live_required_hearts
        try:
            items = list(getattr(self.gs, 'set_zone', []) or [])
            rows_out = [None] * len(items)
            live_cns = []
            live_idxs = []
            for i, cn in enumerate(items):
                ci = _get_card(self.cards_db, cn)
                t = str(getattr(ci, 'type', '') or '').upper() if ci else ''
                if 'LIVE' in t:
                    live_cns.append(cn)
                    live_idxs.append(i)
            if not live_cns:
                return rows_out
            _total, rows = _compute_attempt_score_breakdown(live_cns, self.cards_db, int(getattr(self.gs, 'turn', 0) or 0), self.gs, live_set_indices=live_idxs)
            for idx, r in zip(live_idxs, rows):
                if not isinstance(r, dict):
                    continue

                req_delta = {}
                try:
                    ci0 = _get_card(self.cards_db, str(r.get('cn', '') or ''))
                    base_req = dict((getattr(ci0, 'required_hearts', {}) if ci0 else {}) or {})
                    eff_req = _effective_live_required_hearts(str(r.get('cn', '') or ''), ci0, self.gs, self.cards_db, set_idx=idx)
                    keys = set(base_req.keys()) | set(eff_req.keys())
                    for kk in keys:
                        b0 = int(base_req.get(kk, 0) or 0)
                        e0 = int(eff_req.get(kk, 0) or 0)
                        d0 = e0 - b0
                        if d0:
                            req_delta[str(kk)] = int(d0)
                except Exception:
                    req_delta = {}
                rows_out[idx] = {
                    'cardnumber': str(r.get('cn', '') or ''),
                    'base': int(r.get('base', 0) or 0),
                    'delta': int(r.get('delta', 0) or 0),
                    'score': int(r.get('score', 0) or 0),
                    'req_delta': req_delta,
                }
            return rows_out
        except Exception:
            return []

    def _always_blade_bonus_for(self, pos: str, slot) -> int:
        """常時ブレードボーナスを返す（UI表示専用）。

        含むもの:
        - 常時BODY: コスト13以上条件の +2
        - Love wing bell (PL!-bp4-020): success_zone にある間、センターの μ's に +1/copy
        """
        from .engine import (
            _has_body_always_cost13_blade_bonus,
            _stage_has_cost13_plus_member,
            _stage_has_other_higher_cost_member,
            _love_wing_bell_success_bonus_count,
            _canon_cardno,
        )
        bonus = 0
        try:
            if not slot or not getattr(slot, 'active', False):
                return 0
            ci = _get_card(self.cards_db, slot.cardnumber)
            if not ci:
                return 0

            # 常時BODY: コスト13以上条件
            try:
                if _has_body_always_cost13_blade_bonus(ci) and _stage_has_cost13_plus_member(self.gs, self.cards_db):
                    bonus += 2
            except Exception:
                pass

            # Love wing bell: success_zone にある間、センターの μ's メンバーに +1/copy
            try:
                if pos == 'C' and ("μ's" in str(getattr(ci, 'group', '') or '')):
                    bonus += int(_love_wing_bell_success_bonus_count(self.gs) or 0)
            except Exception:
                pass

            # PL!-sd1-001 高坂穂乃果: 成功ライブカード置き場1枚につき +1 blade
            try:
                if _canon_cardno(getattr(slot, 'cardnumber', '') or '') == 'PL!-sd1-001':
                    bonus += len(list(getattr(self.gs, 'success_zone', []) or []))
            except Exception:
                pass

            # PL!HS-bp2-002 村野さやか: 自分より高コストのメンバーがいる場合 +3 blade
            try:
                if _canon_cardno(getattr(slot, 'cardnumber', '') or '') == 'PL!HS-bp2-002':
                    self_cost = int(getattr(ci, 'cost', 0) or 0)
                    if _stage_has_other_higher_cost_member(self.gs, self.cards_db, pos, self_cost):
                        bonus += 3
            except Exception:
                pass
        except Exception:
            return 0
        return int(bonus)


    def _always_hearts_bonus_for(self, pos: str, slot) -> dict:
        """常時のハート加算を返す（UI表示専用）。"""
        from .engine import _slot_always_hearts_bonus
        try:
            return dict(_slot_always_hearts_bonus(self.gs, self.cards_db, pos, slot) or {})
        except Exception:
            return {}

    def _always_score_bonus_for(self, pos: str, slot) -> int:
        """常時のライブ合計スコア加算を返す（UI表示専用）。"""
        from .engine import _slot_always_score_bonus
        try:
            return int(_slot_always_score_bonus(self.gs, self.cards_db, pos, slot) or 0)
        except Exception:
            return 0

    def _lanzhu_blade_bonus_for(self, pos: str, slot) -> int:
        """PL!N-bp1-012 ランジュのライブ中ブレードボーナスをUI表示用に返す。"""
        from .engine import _lanzhu_bp1_012_live_bonus_count, _canon_cardno
        try:
            if not slot or not getattr(slot, 'active', False):
                return 0
            if _canon_cardno(getattr(slot, 'cardnumber', '') or '') != 'PL!N-bp1-012':
                return 0
            n = _lanzhu_bp1_012_live_bonus_count(self.gs, self.cards_db)
            return 2 if n > 0 else 0
        except Exception:
            return 0

    def _lanzhu_heart_bonus_for(self, pos: str, slot) -> int:
        """PL!N-bp1-012 ランジュのライブ中ALLハートボーナスをUI表示用に返す。"""
        from .engine import _lanzhu_bp1_012_live_bonus_count, _canon_cardno
        try:
            if not slot or not getattr(slot, 'active', False):
                return 0
            if _canon_cardno(getattr(slot, 'cardnumber', '') or '') != 'PL!N-bp1-012':
                return 0
            n = _lanzhu_bp1_012_live_bonus_count(self.gs, self.cards_db)
            return 2 if n > 0 else 0
        except Exception:
            return 0

# PATCH_V2_10_LIVE_GUARD_MAIN_ONLY_APPCMD
    def _live_set_split(self):
        # returns (live_cns, other_cns)
        live = []
        other = []
        try:
            items = list(getattr(self.gs, 'set_zone', []) or [])
        except Exception:
            items = []
        for cn in items:
            try:
                ci = _get_card(self.cards_db, cn)
                t = str(getattr(ci, 'type', '') or '').upper() if ci else ''
            except Exception:
                t = ''
            if 'LIVE' in t:
                live.append(cn)
            else:
                other.append(cn)
        return live, other

    def _end_turn_skip_cheer(self, reason: str = '') -> None:
        # clear resolve zone (avoid popup), then end turn
        try:
            if hasattr(self.gs, 'resolve_zone'):
                self.gs.resolve_zone = []
        except Exception:
            pass
        try:
            if reason:
                self.gs.log.append(f'[UI] {reason}')
        except Exception:
            pass
        cmd_end_turn(self.gs, self.rng)


    def cmd(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:        # PATCH_V2_10_GUARD_MAIN_ONLY
        try:
            ph0 = str(getattr(self.gs, 'phase', '') or '')
        except Exception:
            ph0 = ''
        if name in {'play', 'activate_to_green'} and ph0 != 'MAIN':
            try:
                self.gs.log.append('[UI] メインフェイズのみ実行できます')
            except Exception:
                pass
            self.save_trace()
            return self.state_json()

        mutating = name in {
            "play",
            "set",
            "yell",
            "attempt",
            "ack",
            "end_turn",
            "toggle_debug",
            "activate_to_green",
            "resolve_pending",
            "next",
            "mulligan_next",
        }
        if mutating and name != "toggle_debug":
            push_undo(self.gs, self.rng)

        if name == "play":
            cmd_play(self.gs, self.cards_db, int(payload.get("hand_idx", -1)), str(payload.get("pos", "")))
        elif name == "set":
            idxs = payload.get("indices", [])
            if not isinstance(idxs, list):
                idxs = []
            cmd_set(self.gs, self.rng, [int(x) for x in idxs])
        elif name == "yell":
            cmd_yell(self.gs, self.rng, self.cards_db)
        elif name == "attempt":
            cmd_attempt(self.gs, self.cards_db)
        elif name == "ack":
            cmd_ack(self.gs)
        elif name == "activate_to_green":
            cmd_activate_to_green(self.gs, self.cards_db, str(payload.get("pos", "")))
        elif name == "toggle_stage_active":
            push_undo(self.gs, self.rng)
            cmd_toggle_stage_active(self.gs, self.cards_db, str(payload.get("pos", "")))
        elif name == "resolve_pending":
            cmd_resolve_pending(
                self.gs,
                self.cards_db,
                int(payload.get("idx", -1)),
                str(payload.get("choice", "")),
            )
        elif name == "next":
            idxs = payload.get("indices", [])
            if not isinstance(idxs, list):
                idxs = []
            # Convenience: if the only pending is a simple pay/skip (or yes/no) confirm,
            # allow NEXT to select the default (PAY/YES) without clicking the popup.
            try:
                pend = list(getattr(self.gs, 'pending', []) or [])
            except Exception:
                pend = []
            if pend:
                p0 = pend[0] if isinstance(pend[0], dict) else None
                opts = []
                if isinstance(p0, dict):
                    o = p0.get('options', None)
                    if isinstance(o, list):
                        opts = [str(x).strip().lower() for x in o if str(x).strip()]
                if opts:
                    s = set(opts)
                    if s.issubset({'pay','skip','yes','no'}) and len(s) <= 2:
                        if 'pay' in s:
                            choice = 'pay'
                        elif 'yes' in s:
                            choice = 'yes'
                        else:
                            choice = opts[0]
                        cmd_resolve_pending(self.gs, self.cards_db, 0, choice)
                        post_process(self.gs)
                        self.save_trace()
                        return self.state_json()

            cmd_next(self.gs, self.rng, self.cards_db, [int(x) for x in idxs])
        elif name == "mulligan_next":
            idxs = payload.get("indices", [])
            if not isinstance(idxs, list):
                idxs = []
            if str(getattr(self.gs, "phase", "")).upper() == "MULLIGAN":
                self._cmd_mulligan_next([int(x) for x in idxs])
            else:
                self.gs.log.append("[WARN] mulligan_next ignored (phase mismatch)")
        elif name == "end_turn":
            cmd_end_turn(self.gs, self.rng)
        elif name == "undo":
            do_undo(self.gs, self.rng)
        elif name == "toggle_debug":
            self.gs.debug = not self.gs.debug
            self.gs.log.append(f"[DEBUG] debug={self.gs.debug}")
        else:
            self.gs.log.append(f"[ERR] unknown cmd: {name}")

        # Post-process to resume deferred prompts (e.g., auto trigger order).
        post_process(self.gs)

        self.save_trace()
        return self.state_json()


class Handler(BaseHTTPRequestHandler):
    """HTTP router."""

    app: App = None  # type: ignore
    _head_only: bool = False

    def log_message(self, fmt: str, *args: Any) -> None:
        # keep logs small
        try:
            msg = fmt % args
        except Exception:
            msg = fmt
        print(f"[UI] {msg}")

    def _send(self, code: int, content: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if not self._head_only and content:
            self.wfile.write(content)

    def do_HEAD(self) -> None:
        # Reuse GET routing; just suppress body.
        self._head_only = True
        try:
            self.do_GET()
        finally:
            self._head_only = False

    def do_GET(self) -> None:
        u = urlparse(self.path)

        if u.path == "/":
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return

        if u.path == "/favicon.ico":
            self._send(204, b"", "image/x-icon")
            return

        if u.path == "/playmat":
            candidates: list[Path] = []
            try:
                here = Path(__file__).resolve()
                candidates.append(here.parents[1] / "playmat.jpg")
            except Exception:
                pass
            candidates.append(Path.cwd() / "playmat.jpg")
            for p in candidates:
                if p and p.exists():
                    self._send(200, p.read_bytes(), "image/jpeg")
                    return
            self._send(404, b"", "text/plain; charset=utf-8")
            return

        if u.path == "/state":
            data = json.dumps(self.app.state_json(), ensure_ascii=False).encode("utf-8")
            self._send(200, data, "application/json; charset=utf-8")
            return

        if u.path == "/cardinfo":
            qs = parse_qs(u.query)
            cn = unquote((qs.get("cn", [""])[0] or "").strip())
            ci = _db_get_card(self.app.cards_db, cn) if cn else None
            if not ci:
                self._send(404, json.dumps({"error": "not found"}).encode(), "application/json")
                return
            abilities_text = []
            for ab in (getattr(ci, 'abilities', None) or []):
                if not isinstance(ab, dict):
                    continue
                trig      = str(ab.get('trigger', '')       or '')
                ab_type   = str(ab.get('ability_type', '')  or '')
                cond      = str(ab.get('conditions', '')     or '')
                clauses   = ab.get('clauses', []) or []
                # BODY trigger with empty clauses = DBの断片エントリ → スキップ
                if trig == 'BODY' and not clauses:
                    continue
                # BODY trigger with clauses: ability_typeをヘッダに使う（例：常時）
                header = trig if trig and trig != 'BODY' else (ab_type if ab_type and ab_type != 'UNKNOWN' else '')
                parts = []
                if header:
                    parts.append(f'<{header}>')
                if cond:
                    parts.append(f'【{cond}】')
                clause_texts = []
                for cl in clauses:
                    if not isinstance(cl, dict):
                        continue
                    cost = str(cl.get('cost_template', '') or '')
                    eff  = str(cl.get('effect_template', '') or cl.get('raw', '') or '')
                    # cost と eff を "コスト：効果" 形式で結合
                    if cost and eff:
                        clause_texts.append(f'{cost}：{eff}')
                    elif eff:
                        clause_texts.append(eff)
                    elif cost:
                        clause_texts.append(cost)
                if not clause_texts:
                    continue  # 内容のない断片エントリはスキップ
                parts.extend(clause_texts)
                abilities_text.append('\n'.join(parts))
            # base hearts (MEMBER)
            hearts = {}
            try:
                bh = getattr(ci, 'base_hearts', None) or {}
                hearts = {k: v for k, v in bh.items() if v and int(v) > 0}
            except Exception:
                pass
            # required hearts + score (LIVE)
            required_hearts = {}
            try:
                rh = getattr(ci, 'required_hearts', None) or {}
                required_hearts = {k: v for k, v in rh.items() if v and int(v) > 0}
            except Exception:
                pass
            score = ''
            try:
                sv = getattr(ci, 'score', None)
                if sv is not None:
                    score = str(int(sv))
            except Exception:
                pass
            info = {
                "cn": cn,
                "name":            str(getattr(ci, 'name',  '') or ''),
                "type":            str(getattr(ci, 'type',  '') or ''),
                "group":           str(getattr(ci, 'group', '') or ''),
                "cost":            str(getattr(ci, 'cost',  '') or ''),
                "blade":           str(getattr(ci, 'blade', '') or ''),
                "hearts":          hearts,
                "required_hearts": required_hearts,
                "score":           score,
                "abilities":       abilities_text,
            }
            self._send(200, json.dumps(info, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return

        if u.path == "/img":
            qs = parse_qs(u.query)
            cn = unquote((qs.get("cn", [""])[0] or "").strip())
            # special: energy card back image
            if cn == "__ENERGY__":
                cand = []
                try:
                    cand.append(Path.cwd() / "energy.jpg")
                    cand.append(Path.cwd() / "energy.png")
                    cand.append(Path.cwd() / "energy.jpeg")
                    cand.append(self.app.root / "energy.jpg")
                    cand.append(self.app.root / "energy.png")
                    cand.append(self.app.root / "llocg_db_out_full" / "energy.jpg")
                except Exception:
                    pass
                for p2 in cand:
                    try:
                        if p2 and p2.exists():
                            ctype = "image/jpeg" if str(p2).lower().endswith((".jpg",".jpeg")) else "image/png"
                            self._send(200, p2.read_bytes(), ctype)
                            return
                    except Exception:
                        pass
                # fallback: 1x1 transparent PNG
                self._send(200, bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a49444154789c6360000002000154a24f5d0000000049454e44ae426082'), "image/png")
                return
            p = self.app.img.find(cn)
            if p and p.exists():
                ctype = "image/png"
                if str(p).lower().endswith((".jpg", ".jpeg")):
                    ctype = "image/jpeg"
                self._send(200, p.read_bytes(), ctype)
            else:
                self._send(404, b"", "text/plain")
            return

        # texticon static files: /llocg_db_out_full/card_images/texticons/<filename>
        if u.path.startswith("/llocg_db_out_full/card_images/texticons/"):
            fname = u.path[len("/llocg_db_out_full/card_images/texticons/"):]
            fname = unquote(fname).lstrip("/")
            if fname and "/" not in fname:
                # self.app.root が llocg_db_out_full を指している場合があるため
                # __file__ (llocg_ui/server.py) の親の親 (loveca/) を正規のルートとして使う
                _loveca_root = Path(__file__).resolve().parents[1]
                _cands = [
                    _loveca_root / "llocg_db_out_full" / "card_images" / "texticons" / fname,
                    self.app.root / "llocg_db_out_full" / "card_images" / "texticons" / fname,
                    self.app.root / "card_images" / "texticons" / fname,
                ]
                for _p in _cands:
                    if _p.exists():
                        ctype = "image/png" if fname.lower().endswith(".png") else "image/jpeg"
                        self._send(200, _p.read_bytes(), ctype)
                        return
            self._send(404, b"", "text/plain")
            return

        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        u = urlparse(self.path)
        if u.path != "/cmd":
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        n = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(n) if n > 0 else b"{}"
        try:
            obj = json.loads(body.decode("utf-8"))
        except Exception:
            obj = {}

        cmd = str(obj.get("cmd", "")).strip()
        payload = obj.get("payload", {}) or {}
        if not isinstance(payload, dict):
            payload = {}

        out = self.app.cmd(cmd, payload)
        data = json.dumps(out, ensure_ascii=False).encode("utf-8")
        self._send(200, data, "application/json; charset=utf-8")


def serve(
    host: str,
    port: int,
    root: Path,
    code: str,
    deck_code: str,
    seed: int,
    debug: bool,
    compiled: Optional[Path] = None,
    tokv1: Optional[Path] = None,
) -> None:
    """Start the HTTP server."""
    app = App(root=root, code=code, deck_code=deck_code, seed=seed, debug=debug, compiled=compiled, tokv1=tokv1)
    Handler.app = app
    httpd = ThreadingHTTPServer((host, int(port)), Handler)
    print(f"[LLCG UI] serving on http://{host}:{port} (ui={APP_VERSION}, deck={deck_code})")
    httpd.serve_forever()


# NOTE: Keep this as a raw string; no %-formatting.
HTML = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>LLCG Manual UI</title>
<style>
  :root{
    --pmW: 1200px;
    --pmH: 654px;
    --scale: 0.77;
    --cardW: 347px;
    --cardH: 485px;
    --gap: 8px;
    --sideW: 0px;
  }
  html,body{height:100%;margin:0;background:#111;color:#eee;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;}
  #root{height:100%;display:flex;align-items:center;justify-content:center;}
  #pmWrap{position:relative;width:var(--pmW);height:var(--pmH);background:#222;box-shadow:0 10px 40px rgba(0,0,0,.6);overflow:hidden;border-radius:10px;}
  #playmat{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;user-select:none;pointer-events:none;}
  #zones{position:absolute;inset:0;}

  /* zone */
  .zone{position:absolute;box-sizing:border-box;}
  .zone.debug{outline:2px dashed rgba(0,0,0,.35);}
  .label{position:absolute;left:6px;top:6px;padding:2px 6px;font-size:12px;background:rgba(0,0,0,.55);border-radius:6px;pointer-events:none;}
  .countBadge{position:absolute;right:6px;bottom:6px;padding:2px 6px;font-size:12px;background:rgba(0,0,0,.75);border-radius:6px;pointer-events:none;}
  .zoneInner{position:absolute;inset:0;overflow:hidden;}

  /* cards */
  .cardWrap{position:absolute;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,.55);user-select:none;cursor:pointer;background:#000;}
  .cardWrap img{position:absolute;left:0;top:0;border-radius:8px;display:block;width:100%;height:100%;pointer-events:none;}
  .cardWrap.selected{box-shadow:0 0 0 5px rgba(0,0,0,.92) inset, 0 0 0 5px rgba(0,0,0,.92); border-radius:12px;}
  .cap{position:absolute;left:6px;right:6px;bottom:-18px;font-size:11px;line-height:1.1;color:#eee;text-shadow:0 1px 2px rgba(0,0,0,.8);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none;}

  /* rotation wrappers */
  .rot{position:absolute;left:50%;top:50%;transform-origin:center;}

  /* top bar */
  #topBar{position:absolute;left:10px;top:10px;display:flex;gap:8px;align-items:center;z-index:6000;flex-wrap:wrap;}
  #topBar .pill{background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:6px 10px;font-size:12px;}
  #topBar .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:10px;cursor:pointer;}
  #topBar .miniBtn:hover{background:rgba(255,255,255,.18);}

  /* banner */
  #banner{position:absolute;left:50%;top:54px;transform:translateX(-50%);padding:10px 16px;border-radius:999px;background:rgba(0,0,0,.72);border:1px solid rgba(255,255,255,.22);z-index:9900;display:none;font-size:18px;font-weight:800;letter-spacing:.5px;pointer-events:none;max-width:85%;text-align:center;}
  #banner[data-kind="fail"]{background:rgba(160,20,20,.78);}
  #banner[data-kind="success"]{background:rgba(20,140,60,.78);}
  #banner[data-kind="info"]{background:rgba(0,0,0,.72);}


  /* log */
  #logBox{position:absolute;inset:0;overflow:auto;font-size:12px;line-height:1.3;padding:8px;background:rgba(0,0,0,.45);border-radius:10px;white-space:pre-wrap;}

  /* energy UI */
  .energyUI{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-start;gap:8px;padding:26px 10px 10px 10px;}
  .energyUI .energyText{font-size:14px;line-height:1.2;background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:8px 10px;color:#eee;}
  .energyUI .btn{background:rgba(0,0,0,.65);color:#eee;border:1px solid rgba(255,255,255,.14);padding:10px 10px;border-radius:12px;cursor:pointer;font-size:13px;text-align:center;}
  .energyUI .btn.primary{background:#ffd54a;color:#111;border-color:rgba(0,0,0,.3);}
  .cardWrap.underEnergy{pointer-events:none;}

  /* small activation button on stage card */
  .actBtn{position:absolute;left:6px;right:6px;bottom:6px;padding:6px 6px;border-radius:10px;border:1px solid rgba(255,255,255,.18);
          background:rgba(0,0,0,.6);color:#fff;font-size:12px;cursor:pointer;}
  .actBtn:hover{background:rgba(0,0,0,.74);}
  .toggleActiveBtn{position:absolute;top:4px;left:4px;width:24px;height:24px;border-radius:50%;border:1px solid rgba(255,255,255,.4);
                   background:rgba(0,0,0,.55);color:#fff;font-size:14px;line-height:22px;text-align:center;cursor:pointer;padding:0;z-index:10;}
  .toggleActiveBtn:hover{background:rgba(80,180,255,.7);}

  /* popups */
  #mask{position:absolute;left:0;top:0;bottom:0;right:var(--sideW);background:rgba(0,0,0,.55);display:none;z-index:9000;}
  #modal{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(92%, calc(var(--pmW) - var(--sideW) - 140px));max-height:min(64%, calc(var(--pmH) - 160px));overflow:hidden;background:#1b1b1b;border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:12px;box-shadow:0 14px 60px rgba(0,0,0,.7);display:flex;flex-direction:column;}
  #modalTitle{font-weight:700;flex:0 0 auto;}
  #modalMain{display:flex;gap:16px;flex:1 1 auto;min-height:0;overflow:hidden;margin-top:10px;}
  #modalLead{display:none;flex:0 0 160px;max-width:160px;min-width:160px;flex-direction:column;gap:8px;align-items:flex-start;}
  #modalLead.visible{display:flex;}
  #modalSourceCard{width:150px;min-width:150px;}
  #modalSourceCard img{display:block;width:150px;height:auto;max-height:220px;object-fit:cover;border-radius:12px;border:1px solid rgba(255,255,255,.14);box-shadow:0 8px 24px rgba(0,0,0,.35);}
  #modalSourceName{width:150px;font-weight:700;color:#fff;font-size:13px;line-height:1.35;white-space:normal;word-break:break-word;}
  #modalSourceMeta{width:150px;font-size:11px;color:#aaa;line-height:1.35;white-space:pre-wrap;}
  #modalContent{display:flex;flex-direction:column;flex:1 1 auto;min-width:0;min-height:0;overflow:hidden;}
  #modalText{white-space:pre-wrap;line-height:1.45;color:#ddd;font-size:13px;margin-top:0;flex:0 0 auto;}
  #modalCards{margin-top:10px;overflow-x:auto;overflow-y:auto;padding-bottom:6px;flex:1 1 auto;min-height:0;} 
  #modalCards .surf{position:relative;height:1px;}
  #modalActions{display:flex;gap:8px;justify-content:flex-end;margin-top:10px;flex-wrap:wrap;flex:0 0 auto;}
  #modalActions .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:10px;cursor:pointer;}
/* UI_FIX_PENDING_CARD_CHOICES */
  /* pending card choice list (image buttons) */
  .choiceRow{display:inline-flex;gap:8px;align-items:flex-start;overflow-x:auto;overflow-y:hidden;max-width:min(72vw, 1060px);padding:6px 2px 10px 2px;}
  .choiceBtn{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);border-radius:12px;padding:0;cursor:pointer;position:relative;flex:0 0 auto;box-shadow:0 6px 16px rgba(0,0,0,.35);}
  .choiceBtn:hover{outline:3px solid rgba(255,255,255,.22);outline-offset:-3px;}
  .choiceBtn img{width:100%;height:100%;object-fit:cover;display:block;border-radius:12px;}
  .choiceCap{position:absolute;left:0;right:0;bottom:0;font-size:11px;padding:4px 6px;background:linear-gradient(to top, rgba(0,0,0,.65), rgba(0,0,0,.05));color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6);border-bottom-left-radius:12px;border-bottom-right-radius:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  /* reorder drag-and-drop */
  .reorderHint{font-size:12px;color:#aaa;margin-bottom:6px;display:flex;align-items:center;gap:6px;}
  .reorderHint .arrow{font-size:16px;color:#f9a;}
  .reorderRow{display:inline-flex;gap:10px;align-items:flex-end;overflow-x:auto;padding:8px 4px 12px 4px;min-height:60px;}
  .reorderCard{position:relative;flex:0 0 auto;cursor:grab;border-radius:12px;border:2px solid rgba(255,255,255,.18);box-shadow:0 6px 18px rgba(0,0,0,.4);transition:transform .1s,opacity .1s;}
  .reorderCard:hover{outline:3px solid rgba(249,170,200,.6);outline-offset:-3px;}
  .reorderCard.dragging{opacity:.35;cursor:grabbing;}
  .reorderCard.dragover{outline:3px solid #f9a;outline-offset:-3px;transform:scale(1.05);}
  .reorderCard img{width:100%;height:100%;object-fit:cover;display:block;border-radius:10px;}
  .reorderCard .idxBadge{position:absolute;top:4px;left:4px;background:rgba(0,0,0,.7);color:#f9a;font-size:11px;font-weight:700;padding:2px 6px;border-radius:6px;pointer-events:none;}
  .reorderCard .cnCap{position:absolute;left:0;right:0;bottom:0;font-size:10px;padding:3px 5px;background:linear-gradient(to top,rgba(0,0,0,.65),rgba(0,0,0,.0));color:#fff;border-bottom-left-radius:10px;border-bottom-right-radius:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none;}
  /* card detail panel */
  #cardDetail{position:fixed;z-index:19000;background:#1a1a1a;border:1px solid rgba(255,255,255,.18);border-radius:14px;padding:0;box-shadow:0 16px 60px rgba(0,0,0,.75);display:none;width:340px;max-height:80vh;overflow:hidden;flex-direction:row;}
  #cardDetail.visible{display:flex;}
  #cdImg{width:140px;min-width:140px;flex-shrink:0;position:relative;}
  #cdImg img{width:100%;height:100%;object-fit:cover;border-radius:14px 0 0 14px;display:block;}
  #cdBody{flex:1;overflow-y:auto;padding:12px 14px;display:flex;flex-direction:column;gap:8px;}
  #cdName{font-size:14px;font-weight:700;color:#fff;line-height:1.3;}
  #cdMeta{font-size:11px;color:#aaa;display:flex;flex-wrap:wrap;gap:4px;}
  #cdMeta span{background:rgba(255,255,255,.08);padding:2px 7px;border-radius:6px;}
  #cdAbilities{font-size:11px;color:#ddd;line-height:1.55;white-space:pre-wrap;}
  #cdClose{position:absolute;top:6px;right:8px;background:rgba(0,0,0,.5);color:#fff;border:none;border-radius:50%;width:22px;height:22px;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:1;}
</style>
</head>
<body>
<div id="root">
  <div id="pmWrap">
    <img id="playmat" src="/playmat" alt="playmat"/>

    <div id="topBar">
      <div class="pill">Turn: <b id="turn">?</b> | Phase: <b id="phase">?</b> | Energy: <b id="energy">?</b></div>
      <div class="pill">Selected(hand): <b id="selected">0</b></div>
      <button class="miniBtn" id="btnDbg">枠表示</button>
    </div>

    <div id="banner"></div>

    <div id="zones"></div>

    <div id="mask">
      <div id="modal">
        <div id="modalTitle">Popup</div>
        <div id="modalMain">
          <div id="modalLead">
            <div id="modalSourceCard"></div>
            <div id="modalSourceName"></div>
            <div id="modalSourceMeta"></div>
          </div>
          <div id="modalContent">
            <div id="modalText"></div>
            <div id="modalCards"></div>
            <div id="modalActions"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div id="cardDetail">
  <div id="cdImg"><img id="cdImgEl" src="" alt=""/></div>
  <div id="cdBody">
    <div id="cdName"></div>
    <div id="cdMeta"></div>
    <div id="cdAbilities"></div>
  </div>
  <button id="cdClose">×</button>
</div>

<script>
(()=>{
  const BASE_W = 1560;
  const BASE_H = 851;

  // Base coordinates, aligned to playmat.jpg
  // Right side contains: DECK (top), Waiting room (middle), Energy+UNDO+NEXT (bottom)
  const layout = {
    zones: {
      deck:    {x: 1235, y:  60, w: 270, h: 180, kind:"deck",    orient:"portrait", label:"DECK"},
      green:   {x: 1235, y: 255, w: 270, h: 260, kind:"green",   orient:"portrait", label:"Waiting room"},
      energy:  {x: 1235, y: 545, w: 270, h: 280, kind:"energy",  orient:"portrait", label:"ENERGY"},
      // 成功ライブカード置き場（playmat枠に合わせて左側へ）
      success: {x:   20, y: 210, w: 240, h: 320, kind:"success", orient:"landscape", label:"Success"},

      liveset: {x: 300, y: 55, w: 910, h: 210, kind:"fan",     orient:"landscape", label:"LIVE SET"},
      stageL:  {x:  352, y: 280, w: 181, h: 252, kind:"stage",   orient:"portrait",  label:"L", slot:"L"},
      stageC:  {x:  683, y: 280, w: 180, h: 251, kind:"stage",   orient:"portrait",  label:"C", slot:"C"},
      stageR:  {x:  995, y: 280, w: 180, h: 251, kind:"stage",   orient:"portrait",  label:"R", slot:"R"},

      hand:    {x:  420, y: 600, w: 805, h: 235, kind:"hand",    orient:"portrait",  label:"HAND"},
      log:     {x:   40, y: 585, w: 360, h: 235, kind:"log",     orient:"portrait",  label:"LOG"},
    }
  };

  const elZones = document.getElementById('zones');
  const elTurn = document.getElementById('turn');
  const elPhase = document.getElementById('phase');
  const elEnergy = document.getElementById('energy');
  const elSelected = document.getElementById('selected');
  const elBanner = document.getElementById('banner');

  const elMask = document.getElementById('mask');
  const elModal = document.getElementById('modal');
  const elModalTitle = document.getElementById('modalTitle');
  const elModalLead = document.getElementById('modalLead');
  const elModalSourceCard = document.getElementById('modalSourceCard');
  const elModalSourceName = document.getElementById('modalSourceName');
  const elModalSourceMeta = document.getElementById('modalSourceMeta');
  const elModalText = document.getElementById('modalText');
  const elModalCards = document.getElementById('modalCards');
  const elModalActions = document.getElementById('modalActions');

  const btnDbg = document.getElementById('btnDbg');

  let debug = false;
  let st = null;
  let selHand = []; // indices
  let popup = {type:null};
  let bannerTimer = null;
  let stdPortrait = null;
  let stdLandscape = null;

  // ── Card detail panel ──
  const elCardDetail  = document.getElementById('cardDetail');
  const elCdImg       = document.getElementById('cdImgEl');
  const elCdName      = document.getElementById('cdName');
  const elCdMeta      = document.getElementById('cdMeta');
  const elCdAbilities = document.getElementById('cdAbilities');
  const elCdClose     = document.getElementById('cdClose');

  elCdClose.addEventListener('click', ()=>{ elCardDetail.classList.remove('visible'); });
  document.addEventListener('keydown', ev=>{ if(ev.key==='Escape') elCardDetail.classList.remove('visible'); });
  document.addEventListener('click', ev=>{
    if(elCardDetail.classList.contains('visible') && !elCardDetail.contains(ev.target)){
      elCardDetail.classList.remove('visible');
    }
  });

  async function showCardDetail(cn, anchorEl){
    if(!cn) return;
    elCdImg.src = imgUrl(cn);
    elCdName.textContent = cn;
    elCdMeta.innerHTML = '';
    elCdAbilities.textContent = '読み込み中…';
    elCardDetail.classList.add('visible');

    // Position near the anchor element
    if(anchorEl){
      const rect = anchorEl.getBoundingClientRect();
      let left = rect.right + 8;
      let top  = rect.top;
      // keep inside viewport
      if(left + 350 > window.innerWidth)  left = rect.left - 350;
      if(top  + 400 > window.innerHeight) top  = window.innerHeight - 410;
      elCardDetail.style.left = Math.max(4, left) + 'px';
      elCardDetail.style.top  = Math.max(4, top)  + 'px';
    } else {
      elCardDetail.style.left = '50%';
      elCardDetail.style.top  = '50%';
      elCardDetail.style.transform = 'translate(-50%,-50%)';
    }

    try {
      const r = await fetch(`/cardinfo?cn=${encodeURIComponent(cn)}`, {cache:'no-store'});
      if(!r.ok){ elCdAbilities.textContent = '（情報なし）'; return; }
      const info = await r.json();
      elCdName.textContent = info.name ? `${info.name}（${cn}）` : cn;

      // meta chips
      elCdMeta.innerHTML = '';
      const chips = [];
      if(info.type)  chips.push(info.type);
      if(info.group) chips.push(info.group);
      if(info.cost)  chips.push(`コスト${info.cost}`);
      if(info.blade) chips.push(`ブレード${info.blade}`);
      if(info.score) chips.push(`スコア${info.score}`);
      if(info.hearts && Object.keys(info.hearts).length){
        const jpMap = {pink:'桃',red:'赤',yellow:'黄',green:'緑',blue:'青',purple:'紫'};
        const hStr = Object.entries(info.hearts).map(([k,v])=>`${jpMap[k]||k}×${v}`).join(' ');
        chips.push(hStr);
      }
      if(info.required_hearts && Object.keys(info.required_hearts).length){
        const jpMap = {pink:'桃',red:'赤',yellow:'黄',green:'緑',blue:'青',purple:'紫',any:'無色'};
        const rStr = '必要: ' + Object.entries(info.required_hearts).map(([k,v])=>`${jpMap[k]||k}×${v}`).join(' ');
        chips.push(rStr);
      }
      chips.forEach(c=>{ const s=document.createElement('span'); s.textContent=c; elCdMeta.appendChild(s); });

      // abilities
      if(info.abilities && info.abilities.length){
        elCdAbilities.textContent = info.abilities.join('\n\n');
      } else {
        elCdAbilities.textContent = '（効果なし）';
      }
    } catch(e) {
      elCdAbilities.textContent = '（取得失敗）';
    }
  }

  function cssScale(){
    const pad = 12;
    const vw = window.innerWidth - pad*2;
    const vh = window.innerHeight - pad*2;
    const s = Math.min(vw / BASE_W, vh / BASE_H);
    const pmW = Math.floor(BASE_W * s);
    const pmH = Math.floor(BASE_H * s);
    document.documentElement.style.setProperty('--pmW', pmW + 'px');
    document.documentElement.style.setProperty('--pmH', pmH + 'px');
    document.documentElement.style.setProperty('--scale', s.toFixed(6));
    document.documentElement.style.setProperty('--cardW', (451*s).toFixed(2) + 'px');
    document.documentElement.style.setProperty('--cardH', (630*s).toFixed(2) + 'px');
    // right-side panel width in pixels (scaled)
    document.documentElement.style.setProperty('--sideW', (270*s).toFixed(2) + 'px');
  }

  function scale(){
    return parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--scale')) || 1.0;
  }
  function px(v){ return v * scale(); }

  window.addEventListener('resize', ()=>{ cssScale(); render(); });

  async function apiState(){
    const r = await fetch('/state', {cache:'no-store'});
    return await r.json();
  }
  async function apiCmd(cmd, payload={}){
    const r = await fetch('/cmd', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({cmd, payload})
    });
    return await r.json();
  }

  function cnType(cn){
    try{ return String((st && st.cn2type && st.cn2type[cn]) || ''); }catch(e){ return ''; }
  }
  function intrinsicOrient(cn){
    const t = cnType(cn).toUpperCase();
    if(t.includes('LIVE')) return 'landscape';
    return 'portrait';
  }
  function imgUrl(cn){
    return `/img?cn=${encodeURIComponent(cn)}`;
  }
  function labelFor(cn){
    const m = (st && st.cn2label) ? st.cn2label : null;
    return (m && m[cn]) ? String(m[cn]) : String(cn);
  }
  function cardNameFor(cn){
    const m = (st && st.cn2name) ? st.cn2name : null;
    const name = (m && m[cn]) ? String(m[cn]).trim() : '';
    return name || String(cn || '');
  }
  function choiceTextLabel(raw){
    const s = String(raw || '').trim();
    const low = s.toLowerCase();
    if(!s) return '';
    if(looksLikeCardNo(s)) return cardNameFor(s);
    if(low === 'skip' || low === '__skip__') return 'スキップ';
    if(low === 'pay' || low === 'yes' || low === 'y' || low === '1' || low === 'true' || low === 'apply' || low === 'use') return '使う';
    if(low === 'no' || low === 'n' || low === '0' || low === 'false') return '使わない';
    if(low === 'ok') return '確認';
    return s;
  }
  function cardChoiceCaption(cn, nth, tot){
    const name = cardNameFor(cn);
    if(tot && tot > 1) return `${name} (${nth}/${tot})`;
    return name;
  }
  function pendingTitleFor(p){
    const kind = String((p && p.kind) || '').trim();
    if(kind === 'pay_or_skip' || kind === 'confirm_effect') return '効果を使いますか？';
    if(kind === 'choose_effects') return '効果を選択';
    if(kind === 'choose_stage_member_to_activate') return '対象メンバーを選択';
    if(kind === 'choose_heart_color' || kind === 'choose_heart_color_for_other') return 'ハートの色を選択';
    if(kind === 'discard_from_hand' || kind === 'discard_named_cards_from_hand') return '手札から選択';
    if(kind === 'position_change') return '移動先を選択';
    if(kind === 'choose_from_topk' || kind === 'choose_top_keep_one' || kind === 'topdeck_from_green') return 'カードを選択';
    if(kind === 'auto_order') return '解決順を選択';
    return '効果の選択';
  }
  function summarizeEffectText(raw){
    const s = String(raw || '').trim();
    if(!s) return '';
    if(s === 'この効果を解決するか選んでください。') return s;
    if(s.includes('カードを1枚引く')) return 'カードを1枚引きます。';
    if(s.includes('エネルギーカードを1枚ウェイト状態で置く')) return 'エネルギーを1枚ウェイトで置きます。';
    if(s.includes('付与するハートの色')) return '付与するハートの色を選んでください。';
    if(s.includes('手札から') && s.includes('選')) return '手札から選ぶカードを選択してください。';
    return s;
  }
  function pendingTextFor(p){
    const explicitRaw = (p && (p.text || p.prompt || p.message || p.description || p.after_effect_template)) ? (p.text || p.prompt || p.message || p.description || p.after_effect_template) : '';
    const explicit = summarizeEffectText(explicitRaw);
    if(explicit) return explicit;
    const kind = String((p && p.kind) || '').trim();
    if(kind === 'pay_or_skip' || kind === 'confirm_effect') return 'この効果を使うか、スキップするかを選んでください。';
    if(kind === 'choose_stage_member_to_activate') return '対象にするメンバーを選んでください。';
    if(kind === 'choose_heart_color' || kind === 'choose_heart_color_for_other') return '付与するハートの色を選んでください。';
    if(kind === 'discard_from_hand' || kind === 'discard_named_cards_from_hand') return '手札から選ぶカードを選択してください。';
    if(kind === 'choose_effects') return '解決する効果を選んでください。';
    if(kind === 'auto_order') return '解決順を選んでください。';
    if(kind === 'position_change') return '移動先のエリアを選んでください。';
    return pendingSourceCn(p) ? '効果を解決するため、対象または選択肢を選んでください。' : '';
  }
  function setRichText(el, raw){
    const s = String(raw || '');
    el.innerHTML = '';
    if(!s) return;
    const ICON_BASE = '/llocg_db_out_full/card_images/texticons/';
    const tokenMap = {
      '<(ブレード)>':'icon_blade.png',
      '<(桃)>':'heart_01.png',
      '<(赤)>':'heart_02.png',
      '<(黄)>':'heart_03.png',
      '<(緑)>':'heart_04.png',
      '<(青)>':'heart_05.png',
      '<(紫)>':'heart_06.png',
      '<(任意)>':'heart_00.png',
      '<(虹)>':'icon_all.png',
      '<(すべて)>':'icon_all.png',
    };
    const reTok = /<\((ブレード|桃|赤|黄|緑|青|紫|任意|虹|すべて)\)>/g;
    let last = 0;
    let m;
    while((m = reTok.exec(s)) !== null){
      if(m.index > last){
        el.appendChild(document.createTextNode(s.slice(last, m.index)));
      }
      const tok = m[0];
      const srcFile = tokenMap[tok];
      if(srcFile){
        const img = document.createElement('img');
        img.src = ICON_BASE + srcFile;
        img.alt = m[1];
        img.style.width = '1em';
        img.style.height = '1em';
        img.style.objectFit = 'contain';
        img.style.verticalAlign = '-0.12em';
        img.style.margin = '0 0.05em';
        el.appendChild(img);
      }else{
        el.appendChild(document.createTextNode(tok));
      }
      last = reTok.lastIndex;
    }
    if(last < s.length){
      el.appendChild(document.createTextNode(s.slice(last)));
    }
  }

  function clearModalLead(){
    elModalLead.classList.remove('visible');
    elModalSourceCard.innerHTML = '';
    elModalSourceName.textContent = '';
    elModalSourceMeta.textContent = '';
  }
  function pendingSourceCn(p){
    const tries = [
      p && p.source_cn,
      p && p.cn,
      p && p.after_source_cn,
      p && p.resume_source_cn,
      p && p.ctx && p.ctx.source_cn,
      p && p.ctx && p.ctx.cn,
      p && p.prompt && p.prompt.source_cn,
      p && p.prompt && p.prompt.cn,
      p && Array.isArray(p.queue) && p.queue[0] && p.queue[0].source_cn,
      p && Array.isArray(p.queue) && p.queue[0] && p.queue[0].cn,
      p && Array.isArray(p.remaining) && p.remaining[0] && p.remaining[0].source_cn,
      p && Array.isArray(p.remaining) && p.remaining[0] && p.remaining[0].cn,
    ];
    for(const v of tries){
      const s = String(v || '').trim();
      if(s && looksLikeCardNo(s)) return s;
    }
    return '';
  }
  function pendingTriggerLabel(p){
    const direct = String((p && (p.trigger || p.timing || p.when)) || '').trim();
    if(direct) return direct;
    const kind = String((p && p.kind) || '').trim();
    if(kind.startsWith('live_start') || kind === 'enqueue_pending_prompt') return 'ライブ開始時';
    if(kind.includes('success')) return 'ライブ成功時';
    if(kind.includes('enter') || kind.includes('on_enter')) return '登場時';
    if(kind.includes('activate') || kind.includes('body')) return '起動/能力';
    return '';
  }
  function setModalLeadFromPending(p){
    const cn = pendingSourceCn(p);
    if(!cn){ clearModalLead(); return; }
    const nameMap = (st && st.cn2name) ? st.cn2name : null;
    const displayName = (nameMap && nameMap[cn]) ? String(nameMap[cn]) : String(cn);
    const trigger = pendingTriggerLabel(p);
    elModalSourceCard.innerHTML = '';
    const img = document.createElement('img');
    img.src = imgUrl(cn);
    img.alt = cn;
    elModalSourceCard.appendChild(img);
    elModalSourceName.textContent = displayName;
    elModalSourceMeta.textContent = trigger ? `${cn}\n発生源 / ${trigger}` : `${cn}\n発生源`;
    elModalLead.classList.add('visible');
  }

  function selLimit(){
    if(!st) return 1;
    if(String(st.phase||'').toUpperCase()==='MULLIGAN') return (st.hand? st.hand.length : 6) || 6;
    if(st.phase === 'LIVE_SET') return Math.max(0, Number(st.live_set_limit || 3));
    return 1;
  }
  function toggleSel(i){
    const idx = selHand.indexOf(i);
    if(idx >= 0) selHand.splice(idx,1);
    else{
      selHand.push(i);
      const lim = selLimit();
      while(selHand.length > lim) selHand.shift();
    }
    updateTop();
    render();
  }
  function clearSel(){ selHand = []; updateTop(); render(); }

  function setBanner(text){
    if(bannerTimer){ clearTimeout(bannerTimer); bannerTimer = null; }
    if(text){
      const t = String(text);
      elBanner.textContent = t;
      const u = t.toUpperCase();
      if(u.includes('FAIL')) elBanner.dataset.kind = 'fail';
      else if(u.includes('SUCCESS') || u.includes('OK')) elBanner.dataset.kind = 'success';
      else elBanner.dataset.kind = 'info';
      elBanner.style.display = 'block';
      bannerTimer = setTimeout(()=>{ elBanner.style.display = 'none'; }, 1600);
    }else{
      elBanner.style.display = 'none';
      elBanner.textContent = '';
      elBanner.dataset.kind = 'info';
    }
  }

  function computeDispSize(wantOrient, zoneW, zoneH){
    const cw = px(451), ch = px(630);
    const baseW = (wantOrient==='portrait') ? cw : ch;
    const baseH = (wantOrient==='portrait') ? ch : cw;
    const s = Math.min(1.0, zoneW / baseW, zoneH / baseH);
    return {w: baseW*s, h: baseH*s};
  }


  function standardSize(orient){
    // Prefer the hand card size as the global standard (spec: unify card sizes)
    if(orient==='portrait' && stdPortrait) return stdPortrait;
    if(orient==='landscape' && stdLandscape) return stdLandscape;
    const cw = px(451) * 0.38;
    const ch = px(630) * 0.38;
    if(orient==='landscape') return {w: ch, h: cw};
    return {w: cw, h: ch};
  }
  function makeCard(cn, wantOrient, x, y, w, h, capText, onClick, isSelected=false, z=100, noHover=false, forceIntrinsicOrient=null){
    const wrap = document.createElement('div');
    wrap.className = 'cardWrap';
    wrap.style.left = x + 'px';
    wrap.style.top = y + 'px';
    wrap.style.width = w + 'px';
    wrap.style.height = h + 'px';
    wrap.style.zIndex = String(z);
    wrap.dataset.baseZ = String(z);
    if(isSelected){ wrap.classList.add('selected'); wrap.style.zIndex='18000'; wrap.dataset.baseZ='18000'; }

    const intr = forceIntrinsicOrient || intrinsicOrient(cn);
    const needsRotate = (intr !== wantOrient);

    if(!needsRotate){
      const img = document.createElement('img');
      img.src = imgUrl(cn);
      img.alt = cn;
      wrap.appendChild(img);
    }else{
      // portrait<-landscape : rotate +90 (CW)
      // landscape<-portrait : rotate -90 (CCW)
      const inner = document.createElement('div');
      inner.className = 'rot';
      const rotDeg = (wantOrient==='portrait') ? 90 : -90;
      inner.style.transform = `translate(-50%,-50%) rotate(${rotDeg}deg)`;
      inner.style.width = h + 'px';
      inner.style.height = w + 'px';
      inner.style.left = '50%';
      inner.style.top = '50%';

      const img = document.createElement('img');
      img.src = imgUrl(cn);
      img.alt = cn;
      img.style.position = 'absolute';
      img.style.left = '0';
      img.style.top = '0';
      img.style.width = '100%';
      img.style.height = '100%';
      img.style.borderRadius = '8px';
      img.style.objectFit = 'contain';
      inner.appendChild(img);
      wrap.appendChild(inner);
    }

    if(capText){
      const cap = document.createElement('div');
      cap.className = 'cap';
      cap.textContent = capText;
      wrap.appendChild(cap);
    }

    // hover: lift + bring front (disabled for under-energy cards etc.)
    if(!noHover){
      wrap.addEventListener('mouseenter', ()=>{
        const lift = Math.max(4, Math.floor(w * 0.05));
        wrap.style.transform = `translateY(${-lift}px)`;
        wrap.style.zIndex = '20000';
      });
      wrap.addEventListener('mouseleave', ()=>{
        wrap.style.transform = '';
        wrap.style.zIndex = wrap.dataset.baseZ || '100';
      });
    }else{
      wrap.style.pointerEvents = 'none';
    }

    if(onClick){
      wrap.addEventListener('click', (ev)=>{ ev.stopPropagation(); onClick(); });
    }else{
      wrap.addEventListener('click', (ev)=>{ ev.stopPropagation(); });
    }

    // 右クリックでカード詳細
    const detailCn = (cn && cn !== '__BACK__' && cn !== '__ENERGY__') ? cn : null;
    if(detailCn){
      wrap.addEventListener('contextmenu', ev=>{
        ev.preventDefault();
        ev.stopPropagation();
        showCardDetail(detailCn, wrap);
      });
    }

    return wrap;
  }

  function zoneDiv(z){
    const d = document.createElement('div');
    d.className = 'zone' + (debug ? ' debug' : '');
    d.style.left = px(z.x) + 'px';
    d.style.top = px(z.y) + 'px';
    d.style.width = px(z.w) + 'px';
    d.style.height = px(z.h) + 'px';

    const lab = document.createElement('div');
    lab.className = 'label';
    lab.textContent = z.label || '';
    d.appendChild(lab);

    const inner = document.createElement('div');
    inner.className = 'zoneInner';
    d.appendChild(inner);

    return d;
  }

  function renderLog(zoneEl, lines){
    const inner = zoneEl.querySelector('.zoneInner');
    const box = document.createElement('div');
    box.id = 'logBox';
    const tail = (lines||[]).slice(-28).join('\n');
    box.textContent = tail;
    inner.appendChild(box);
  }

  // 空ゾーン：カードなし・バッジだけ表示（クリックがあれば登録）
  function renderEmptyZone(zoneEl, countText, onClick){
    const inner = zoneEl.querySelector('.zoneInner');
    inner.style.cursor = onClick ? 'pointer' : 'default';
    if(onClick){
      zoneEl.onclick = (ev)=>{ ev.stopPropagation(); onClick(); };
    }else{
      zoneEl.onclick = null;
    }
    if(countText !== undefined && countText !== null){
      const badge = document.createElement('div');
      badge.className = 'countBadge';
      badge.textContent = String(countText);
      zoneEl.appendChild(badge);
    }
  }

  function renderTopCard(zoneEl, cn, wantOrient, countText, onClick){
    const inner = zoneEl.querySelector('.zoneInner');
    inner.style.cursor = onClick ? 'pointer' : 'default';
    if(onClick){
      zoneEl.onclick = (ev)=>{ ev.stopPropagation(); onClick(); };
    }else{
      zoneEl.onclick = null;
    }

    const zoneW = zoneEl.clientWidth;
    const zoneH = zoneEl.clientHeight;
    const padTop = 22;
    const padX = 8;
    const availW = zoneW - padX*2;
    const availH = zoneH - padTop - 10;
    const sz = computeDispSize(wantOrient, availW, availH);
    const x = (zoneW - sz.w)/2;
    const y = padTop + (availH - sz.h)/2;

    const card = makeCard(cn, wantOrient, x, y, sz.w, sz.h, '', (onClick?()=>onClick():null), false, 200);
    inner.appendChild(card);

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(countText);
    zoneEl.appendChild(badge);
  }

  function renderVertStack(zoneEl, cards, wantOrient, countText, onClick, {overlap=0.70, maxShow=4, forceIntrinsicOrient=null} = {}){
    // Stack cards vertically with overlap (e.g., 70% overlap => step=30% height).
    const inner = zoneEl.querySelector('.zoneInner');
    inner.style.cursor = onClick ? 'pointer' : 'default';
    if(onClick){
      zoneEl.onclick = (ev)=>{ ev.stopPropagation(); onClick(); };
    }else{
      zoneEl.onclick = null;
    }

    const list = Array.isArray(cards) ? cards.slice() : [];
    const nAll = list.length;
    const nShow = Math.min(nAll, maxShow);
    const show = (nShow>0) ? list.slice(-nShow) : [];

    const zoneW = zoneEl.clientWidth;
    const zoneH = zoneEl.clientHeight;
    const padTop = 22;
    const padX = 8;
    const availW = zoneW - padX*2;
    const availH = zoneH - padTop - 10;

    if(nShow<=0){
      renderEmptyZone(zoneEl, 0, onClick);
      return;
    }

    const stepFrac = Math.max(0.0, Math.min(0.95, 1.0 - overlap));
    const denom = 1.0 + stepFrac * (nShow - 1);
    const cardAvailH = availH / denom;
    const sz = computeDispSize(wantOrient, availW, cardAvailH);
    const stepY = sz.h * stepFrac;
    const totalH = sz.h + stepY*(nShow-1);
    const x = (zoneW - sz.w)/2;
    const y0 = padTop + Math.max(0, (availH - totalH)/2);

    show.forEach((cn, i)=>{
      const y = y0 + stepY*i;
      const card = makeCard(String(cn), wantOrient, x, y, sz.w, sz.h, '', null, false, 200+i, false, forceIntrinsicOrient);
      inner.appendChild(card);
    });

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(countText);
    zoneEl.appendChild(badge);
  }

  function renderHand(zoneEl, cards){
    const inner = zoneEl.querySelector('.zoneInner');
    const zoneW = zoneEl.clientWidth;
    const zoneH = zoneEl.clientHeight;
    const padTop = 22;
    const padX = 10;
    const availW = zoneW - padX*2;
    const availH = zoneH - padTop - 10;

    const sz = computeDispSize('portrait', availW, availH);
    // cache standard card size from hand area
    stdPortrait = {w: sz.w, h: sz.h};
    stdLandscape = {w: sz.h, h: sz.w};
    const n = cards.length;

    let step = 0;
    if(n <= 1){
      step = 0;
    }else{
      const maxStep = sz.w + px(8);
      const fitStep = (availW - sz.w) / (n - 1);
      step = Math.min(maxStep, fitStep);
      if(!isFinite(step) || step < 0) step = 0;
    }

    const totalW = (n===0) ? 0 : (sz.w + step*(n-1));
    const startX = (availW > totalW) ? (availW - totalW)/2 : 0;
    const baseY = padTop + Math.max(0, (availH - sz.h)/2);

    cards.forEach((cn, i)=>{
      const x = padX + startX + step*i;
      const y = baseY;
      const cap = labelFor(cn);
      const isSel = selHand.includes(i);
      const card = makeCard(cn, 'portrait', x, y, sz.w, sz.h, cap, ()=>toggleSel(i), isSel, 100+i);
      inner.appendChild(card);
    });

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(cards.length);
    zoneEl.appendChild(badge);
  }

  function renderFan(zoneEl, cards, wantOrient){
    const inner = zoneEl.querySelector('.zoneInner');
    const zoneW = zoneEl.clientWidth;
    const zoneH = zoneEl.clientHeight;
    const padTop = 22;
    const padX = 10;
    const availW = zoneW - padX*2;
    const availH = zoneH - padTop - 10;
    const sz = computeDispSize(wantOrient, availW, availH);
    const n = cards.length;

    let step = 0;
    if(n <= 1){
      step = 0;
    }else{
      const maxStep = sz.w + px(10);
      const fitStep = (availW - sz.w) / (n - 1);
      step = Math.min(maxStep, fitStep);
      if(!isFinite(step) || step < 0) step = 0;
    }

    const totalW = (n===0) ? 0 : (sz.w + step*(n-1));
    const startX = (availW > totalW) ? (availW - totalW)/2 : 0;
    const baseY = padTop + Math.max(0, (availH - sz.h)/2);

    cards.forEach((cn, i)=>{
      const x = padX + startX + step*i;
      const y = baseY;
      const card = makeCard(cn, wantOrient, x, y, sz.w, sz.h, '', null, false, 100+i);
      inner.appendChild(card);
    });

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(cards.length);
    zoneEl.appendChild(badge);
  }


  function renderLiveSet(zoneEl, cards){
    const inner = zoneEl.querySelector('.zoneInner');
    const zoneW = zoneEl.clientWidth;
    const zoneH = zoneEl.clientHeight;
    const padTop = 22;
    const padX = 10;
    const availW = zoneW - padX*2;
    const availH = zoneH - padTop - 10;
    const gap = Math.max(6, px(14));
    const slotW = (availW - gap*2) / 3;
    const slotsX = [0, slotW + gap, 2*(slotW + gap)];
    const scoreRows = Array.isArray(st && st.set_zone_score_rows) ? st.set_zone_score_rows : [];
    for(let i=0;i<3;i++){
      const cn = (Array.isArray(cards) && i < cards.length) ? String(cards[i]) : null;
      if(!cn) continue;
      const sz = computeDispSize('landscape', slotW, availH);
      const x = padX + slotsX[i] + (slotW - sz.w)/2;
      const y = padTop + Math.max(0, (availH - sz.h)/2);
      const card = makeCard(cn, 'landscape', x, y, sz.w, sz.h, '', null, false, 100+i);
      try{
        const row = (i < scoreRows.length) ? scoreRows[i] : null;
        const delta = Number(row && row.delta || 0);
        if(delta !== 0){
          const sb = document.createElement('div');
          const sign = delta > 0 ? '+' : '';
          const base = Number(row && row.base || 0);
          const eff = Number(row && row.score || 0);
          sb.title = `スコア ${eff} (${base}${sign}${delta})`;
          sb.textContent = `SCORE${sign}${delta}`;
          sb.style.cssText = [
            'position:absolute',
            'top:-8px',
            'left:50%',
            'transform:translateX(-50%)',
            'background:rgba(30,30,30,.88)',
            'color:#fff',
            'font-size:10px',
            'font-weight:700',
            'line-height:1',
            'padding:3px 5px',
            'border-radius:999px',
            'pointer-events:none',
            'z-index:55',
            'box-shadow:0 1px 4px rgba(0,0,0,.35)',
            'letter-spacing:0',
            'white-space:nowrap',
          ].join(';');

    card.appendChild(sb);
  }
  const reqDelta = Object.assign({}, row && row.req_delta || {});
  if(Object.keys(reqDelta).some(k => Number(reqDelta[k] || 0) !== 0)){
    const ICON_BASE2 = '/llocg_db_out_full/card_images/texticons/';
    const heartIconFile2 = {
      pink:'heart_01.png', red:'heart_02.png', yellow:'heart_03.png',
      green:'heart_04.png', blue:'heart_05.png', purple:'heart_06.png',
      any:'heart_00.png', all:'icon_all.png',
    };
    const heartFallback2 = {
      pink:'桃', red:'赤', yellow:'黄', green:'緑', blue:'青', purple:'紫', any:'無', all:'ALL',
    };
    const heartColor2 = {
      pink:'#ff88cc', red:'#ff5555', yellow:'#ffe566', green:'#44dd88',
      blue:'#55aaff', purple:'#cc77ff', any:'#ddd', all:'#fff',
    };
    const ICO2 = 16, STEP2 = 10;
    const makeIconStack2 = (icons, titleAll)=>{
      const n = icons.length;
      const totalW = ICO2 + STEP2 * (n - 1);
      const wrap = document.createElement('div');
      wrap.title = titleAll;
      wrap.style.cssText = ['position:relative', `width:${totalW}px`, `height:${ICO2}px`, 'flex-shrink:0'].join(';');
      icons.forEach((ico, i)=>{
        const img = document.createElement('img');
        img.src = ico.src; img.alt = ico.alt;
        img.style.cssText = ['position:absolute', `left:${STEP2*i}px`, 'top:0', `width:${ICO2}px`, `height:${ICO2}px`, 'object-fit:contain', `z-index:${10+i}`].join(';');
        img.onerror = ()=>{
          const sp = document.createElement('span');
          sp.textContent = ico.fallbackText;
          sp.style.cssText = ['position:absolute', `left:${STEP2*i}px`, 'top:0', `width:${ICO2}px`, `height:${ICO2}px`, 'display:flex','align-items:center','justify-content:center',`font-size:${ICO2-2}px`, `color:${ico.fallbackColor}`, `z-index:${10+i}`].join(';');
          img.replaceWith(sp);
        };
        wrap.appendChild(img);
      });
      return wrap;
    };
    const makeIconRow2 = (signText, stack, titleAll)=>{
      const row2 = document.createElement('div');
      row2.title = titleAll;
      row2.style.cssText = 'display:flex;align-items:center;gap:2px;';
      const sgn = document.createElement('span');
      sgn.textContent = signText;
      sgn.style.cssText = ['color:#fff','font-size:11px','font-weight:700','line-height:1','flex-shrink:0'].join(';');
      row2.appendChild(sgn);
      row2.appendChild(stack);
      return row2;
    };
    const ov2 = document.createElement('div');
    ov2.style.cssText = ['position:absolute','right:0','top:14px','display:flex','flex-direction:column','align-items:flex-end','gap:3px','padding:3px 4px','background:rgba(0,0,0,0.62)','border-radius:6px 0 0 6px','pointer-events:none','z-index:50'].join(';');
    for(const [col, cnt] of Object.entries(reqDelta)){
      const n = Number(cnt || 0);
      if(!n) continue;
      const absn = Math.abs(n);
      const file = heartIconFile2[col] || 'heart_00.png';
      const fb   = heartFallback2[col] || col;
      const fc   = heartColor2[col] || '#fff';
      const icons = Array.from({length: absn}, ()=>({src: ICON_BASE2 + file, alt: fb, fallbackText: fb, fallbackColor: fc}));
      const signText = n > 0 ? '＋' : '－';
      const desc = `${fb}必要ハート ${n > 0 ? '+' : ''}${n}`;
      ov2.appendChild(makeIconRow2(signText, makeIconStack2(icons, ''), desc));
    }
    card.appendChild(ov2);
  }
}catch(e){}
inner.appendChild(card);
    }
    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String((Array.isArray(cards)?cards.length:0));
    zoneEl.appendChild(badge);
  }
  function renderStage(zoneEl, slotKey, slotObj){
    // clicking the zone plays a selected hand card into this slot (card itself is also clickable)
    const doPlayHere = async ()=>{
      if(selHand.length !== 1){
        setBanner('手札を1枚選択して、置きたい枠をクリック');
        return;
      }
      const idx = selHand[0];
      st = await apiCmd('play', {hand_idx: idx, pos: slotKey});
      selHand = [];
      updateTop();
      render();
    };

    zoneEl.onclick = (ev)=>{ ev.stopPropagation(); doPlayHere(); };


    if(!slotObj || !slotObj.cardnumber) return;
    const cn = String(slotObj.cardnumber);

    const inner = zoneEl.querySelector('.zoneInner');
    const zoneW = zoneEl.clientWidth;
    const zoneH = zoneEl.clientHeight;
    const padTop = 22;
    const availW = zoneW - 10;
    const availH = zoneH - padTop - 10;
    const isWait = slotObj && (slotObj.active === false);
    // spec: same scale for all cards; portrait is reference scale
    const szPortrait = computeDispSize('portrait', availW, availH);
    stdPortrait = {w: szPortrait.w, h: szPortrait.h};
    stdLandscape = {w: szPortrait.h, h: szPortrait.w};
    // wait → rotate in place at same scale (swap w/h, render as landscape)
    const sz = isWait ? {w: szPortrait.h, h: szPortrait.w} : szPortrait;
    const dispOrient = isWait ? 'landscape' : 'portrait';
    // wait card is wider than zone → allow overflow so it's not clipped
    inner.style.overflow = isWait ? 'visible' : 'hidden';
    const x = (zoneW - sz.w)/2;
    const y = padTop + Math.max(0, (availH - sz.h)/2);

    // energies under this member (render behind)
    try{
      const underN = Number(slotObj.energy_under||0);
      if(underN > 0){
        const dx = sz.w * 0.05;
        const dy = sz.w * 0.05;
        for(let i=0;i<underN;i++){
          const ex = x + dx*(i+1);
          const ey = y + dy*(i+1);
          const ecard = makeCard('__ENERGY__', 'portrait', ex, ey, sz.w, sz.h, '', null, false, 350+i, true);
          ecard.classList.add('underEnergy');
          inner.appendChild(ecard);
        }
      }
    }catch(e){}
    const card = makeCard(cn, dispOrient, x, y, sz.w, sz.h, labelFor(cn), ()=>doPlayHere(), false, 400);

    // activation button (if possible)
    try{
      const sd = (st && st.stage_detail) ? st.stage_detail : null;
      const det = sd ? sd[slotKey] : null;
      const canAct = det && det.can_activate;
      if(canAct){
        const b = document.createElement('button');
        b.className = 'actBtn';
        b.textContent = '起動';
        b.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('activate_to_green', {pos: slotKey});
          updateTop();
          render();
        });
        card.appendChild(b);
      }
    }catch(e){}

    // manual active/wait toggle button (top-left ↻)
    try{
      const isActive = slotObj && slotObj.active;
      const tb = document.createElement('button');
      tb.className = 'toggleActiveBtn';
      tb.title = isActive ? 'ウェイトにする' : 'アクティブにする';
      tb.textContent = '↻';
      tb.addEventListener('click', async (ev)=>{
        ev.stopPropagation();
        st = await apiCmd('toggle_stage_active', {pos: slotKey});
        updateTop();
        render();
      });
      card.appendChild(tb);
    }catch(e){}

    inner.appendChild(card);

    // ── 一時ブレード/ハート増加アイコンオーバーレイ（カード右上） ──────────
    try{
      const sd  = (st && st.stage_detail) ? st.stage_detail : null;
      const det = sd ? sd[slotKey] : null;
      if(det){
        const tmpBlade  = Number(det.temp_blade      || 0);
        const alwBlade0 = Number(det.always_blade_bonus || 0);
        const alwScore  = Number(det.always_score_bonus || 0);
        const lzBlade   = Number(det.lanzhu_blade_bonus || 0);
        const lzHeart   = Number(det.lanzhu_heart_bonus || 0);
        const tmpHearts = Object.assign({}, det.temp_hearts || {});
        const alwHearts = Object.assign({}, det.always_hearts_bonus || {});
        if(lzHeart > 0) alwHearts['all'] = (Number(alwHearts['all'] || 0)) + lzHeart;

        // Love wing bell の常時ブレードは、state_detail に乗らない環境でも
        // success_zone から再計算して可視バッジへ反映する
        let alwBlade = alwBlade0;
        try{
          if(alwBlade <= 0 && slotKey === 'C'){
            const sz = Array.isArray(st && st.success_zone) ? st.success_zone : [];
            const cnSelf = String(cn || '');
            // μ's カードは cardnumber が PL!- で始まる前提
            if(cnSelf.startsWith('PL!-')){
              const lwCount = sz.filter(x => String(x||'') === 'PL!-bp4-020').length;
              if(lwCount > 0) alwBlade += lwCount;
            }
          }
        }catch(e){}
        const totalBlade = tmpBlade + alwBlade + lzBlade;

        const hasBonus = totalBlade !== 0 || alwScore !== 0 || Object.keys(alwHearts).some(k=>Number(alwHearts[k])!==0) || Object.keys(tmpHearts).some(k=>Number(tmpHearts[k])!==0);
        if(hasBonus){
          const ICON_BASE = '/llocg_db_out_full/card_images/texticons/';
          const heartIconFile = {
            pink:'heart_01.png', red:'heart_02.png', yellow:'heart_03.png',
            green:'heart_04.png', blue:'heart_05.png', purple:'heart_06.png',
            any:'heart_00.png', all:'icon_all.png',
          };
          const heartFallback = {
            pink:'桃', red:'赤', yellow:'黄', green:'緑', blue:'青', purple:'紫', any:'無', all:'ALL',
          };
          const heartColor = {
            pink:'#ff88cc', red:'#ff5555', yellow:'#ffe566',
            green:'#44dd88', blue:'#55aaff', purple:'#cc77ff', any:'#ddd', all:'#fff',
          };

          // アイコンサイズと重なり量
          const ICO  = 16;   // アイコン1枚の幅・高さ (px)
          const STEP = 10;   // 右が前面になる重なりオフセット (px)

          // アイコンスタックを作る関数
          // icons: [{src, alt, fallbackText, fallbackColor, title}...]
          // 右が前面 = index大ほど z-index高
          const makeIconStack = (icons, titleAll)=>{
            const n = icons.length;
            const totalW = ICO + STEP * (n - 1);
            const wrap = document.createElement('div');
            wrap.title = titleAll;
            wrap.style.cssText = [
              'position:relative',
              `width:${totalW}px`,
              `height:${ICO}px`,
              'flex-shrink:0',
            ].join(';');
            icons.forEach((ico, i)=>{
              const img = document.createElement('img');
              img.src = ico.src;
              img.alt = ico.alt;
              img.style.cssText = [
                'position:absolute',
                `left:${STEP * i}px`,
                'top:0',
                `width:${ICO}px`,
                `height:${ICO}px`,
                'object-fit:contain',
                `z-index:${10 + i}`,
              ].join(';');
              img.onerror = ()=>{
                const sp = document.createElement('span');
                sp.textContent = ico.fallbackText;
                sp.style.cssText = [
                  'position:absolute',
                  `left:${STEP * i}px`,
                  'top:0',
                  `width:${ICO}px`,
                  `height:${ICO}px`,
                  'display:flex',
                  'align-items:center',
                  'justify-content:center',
                  `font-size:${ICO - 2}px`,
                  `color:${ico.fallbackColor}`,
                  `z-index:${10 + i}`,
                ].join(';');
                img.replaceWith(sp);
              };
              wrap.appendChild(img);
            });
            return wrap;
          };

          // オーバーレイ本体（縦並び、カード右上）
          // card(.cardWrap) の子にすることでホバー時の z-index 上昇に追従する
          const ov = document.createElement('div');
          ov.style.cssText = [
            'position:absolute',
            'right:0',
            'top:2px',
            'display:flex',
            'flex-direction:column',
            'align-items:flex-end',
            'gap:3px',
            'padding:3px 4px',
            'background:rgba(0,0,0,0.62)',
            'border-radius:6px 0 0 6px',
            'pointer-events:none',
            'z-index:50',
          ].join(';');

          // アイコン行（＋ラベル + スタック）を作る関数
          const makeIconRow = (signText, stack, titleAll)=>{
            const row = document.createElement('div');
            row.title = titleAll;
            row.style.cssText = 'display:flex;align-items:center;gap:2px;';
            const plus = document.createElement('span');
            plus.textContent = signText;
            plus.style.cssText = [
              'color:#fff',
              'font-size:11px',
              'font-weight:700',
              'line-height:1',
              'flex-shrink:0',
            ].join(';');
            row.appendChild(plus);
            row.appendChild(stack);
            return row;
          };

          // ブレードスタック
          if(totalBlade !== 0){
            const absBlade = Math.abs(totalBlade);
            const icons = Array.from({length: absBlade}, ()=>({
              src: ICON_BASE + 'icon_blade.png',
              alt: '▲',
              fallbackText: '▲',
              fallbackColor: '#ffe566',
            }));
            const titleStr = `ブレード ${totalBlade > 0 ? '+' : ''}${totalBlade}`;
            ov.appendChild(makeIconRow(totalBlade > 0 ? '＋' : '－', makeIconStack(icons, ''), titleStr));
          }

          // 常時ハート（色別）
          for(const [col, cnt] of Object.entries(alwHearts)){
            const n = Number(cnt);
            if(!n) continue;
            const file = heartIconFile[col] || `heart_${col}.png`;
            const fb   = heartFallback[col] || col;
            const fc   = heartColor[col] || '#fff';
            const absn = Math.abs(n);
            const icons = Array.from({length: absn}, ()=>({
              src: ICON_BASE + file,
              alt: fb,
              fallbackText: '♥',
              fallbackColor: fc,
            }));
            ov.appendChild(makeIconRow(n > 0 ? '＋' : '－', makeIconStack(icons, ''), `${fb}ハート ${n > 0 ? '+' : ''}${n}`));
          }

          // 一時ハート（色別）
          for(const [col, cnt] of Object.entries(tmpHearts)){
            const n = Number(cnt);
            if(!n) continue;
            const file = heartIconFile[col] || `heart_${col}.png`;
            const fb   = heartFallback[col] || col;
            const fc   = heartColor[col] || '#fff';
            const absn = Math.abs(n);
            const icons = Array.from({length: absn}, ()=>({
              src: ICON_BASE + file,
              alt: fb,
              fallbackText: '♥',
              fallbackColor: fc,
            }));
            ov.appendChild(makeIconRow(n > 0 ? '＋' : '－', makeIconStack(icons, ''), `${fb}ハート ${n > 0 ? '+' : ''}${n}（一時）`));
          }

          if(alwScore !== 0){
            const sb = document.createElement('div');
            const signScore = alwScore > 0 ? '+' : '';
            sb.title = `ライブ合計スコア ${signScore}${alwScore}`;
            sb.textContent = `SCORE${signScore}${alwScore}`;
            sb.style.cssText = [
              'position:absolute',
              'top:-8px',
              'left:50%',
              'transform:translateX(-50%)',
              'background:rgba(30,30,30,.88)',
              'color:#fff',
              'font-size:10px',
              'font-weight:700',
              'line-height:1',
              'padding:3px 5px',
              'border-radius:999px',
              'pointer-events:none',
              'z-index:55',
              'box-shadow:0 1px 4px rgba(0,0,0,.35)',
              'letter-spacing:0',
              'white-space:nowrap',
            ].join(';');
            card.appendChild(sb);
          }

          card.appendChild(ov);
        }
      }
    }catch(e){}
  }

  function renderEnergy(zoneEl){
    const inner = zoneEl.querySelector('.zoneInner');
    const wrap = document.createElement('div');
    wrap.className = 'energyUI';

    const active = st ? Number(st.energy_active||0) : 0;
    const wait = st ? Number(st.energy_wait||0) : 0;
    const total = active + wait;

    const t = document.createElement('div');
    t.className = 'energyText';
    t.innerHTML = `Energy: <b>${active}</b> / <b>${total}</b><div style="opacity:.8;font-size:12px;margin-top:2px;">wait: ${wait}</div>`;
    wrap.appendChild(t);

    const btnUndo = document.createElement('button');
    btnUndo.className = 'btn';
    btnUndo.textContent = 'UNDO';
    btnUndo.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      st = await apiCmd('undo', {});
      selHand = [];
      updateTop();
      render();
    });

    const btnNext = document.createElement('button');
    btnNext.className = 'btn primary';
    const ph = String(st && st.phase ? st.phase : '').toUpperCase();
    btnNext.textContent = (ph==='MULLIGAN') ? 'マリガン決定' : 'NEXT';
    btnNext.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      const ph2 = String(st && st.phase ? st.phase : '').toUpperCase();
      if(ph2==='MULLIGAN') st = await apiCmd('mulligan_next', {indices: selHand.slice()});
      else st = await apiCmd('next', {indices: selHand.slice()});
      selHand = [];
      updateTop();
      render();
    });

    wrap.appendChild(btnUndo);
    wrap.appendChild(btnNext);
    inner.appendChild(wrap);
  }

  function openCardListPopup(title, cards, {closable=true, helperText='', forcePortrait=false, forceLandscape=false } = {}){
    let cardsList = cards.slice();
    // sort waiting room cards (spec update): by cardnumber asc, then card type
    try{
      const t = String(title||'');
      if(t.includes('控え室') || t.toLowerCase().includes('waiting')){
        const typeOrder = (tp)=>{ const u=String(tp||'').toUpperCase(); if(u.includes('MEMBER')) return 0; if(u.includes('LIVE')) return 1; return 2; };
        cardsList.sort((a,b)=>{
          const sa=String(a||'');
          const sb=String(b||'');
          const c = sa.localeCompare(sb, 'en', {numeric:true});
          if(c!==0) return c;
          const ta = typeOrder(cnType(sa));
          const tb = typeOrder(cnType(sb));
          return ta - tb;
        });
      }
    }catch(e){ cardsList = cards.slice(); }

    popup = {type:'cardlist', title, cards: cardsList.slice(), closable, helperText};

    elModalTitle.textContent = title;
    setRichText(elModalText, helperText || '');
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    // layout card list with overlap + horizontal scroll
    // Use the standard (hand-based) card size in popups
    const dimsP = standardSize('portrait');
    const dimsL = standardSize('landscape');
    const maxW = Math.max(dimsP.w, dimsL.w);
    const maxH = Math.max(dimsP.h, dimsL.h);

    const surf = document.createElement('div');
    surf.className = 'surf';
    surf.style.height = (maxH + 12) + 'px';
    const step = maxW * 0.45; // overlap ~55% (spec: 1/2~2/3)
    const minW = (cardsList.length<=1) ? (maxW + 24) : (maxW + step*(cardsList.length-1) + 24);
    surf.style.minWidth = minW + 'px';

    cardsList.forEach((cn, i)=>{
      const orient = forceLandscape ? 'landscape' : (forcePortrait ? 'portrait' : intrinsicOrient(cn));
      const d = (orient==='landscape') ? dimsL : dimsP;
      const x = 12 + step*i + (maxW - d.w)/2;
      const y = 6 + (maxH - d.h)/2;
      const c = makeCard(cn, orient, x, y, d.w, d.h, '', null, false, 100+i);
      surf.appendChild(c);
    });

    elModalCards.appendChild(surf);

    if(closable){
      const close = document.createElement('button');
      close.className = 'miniBtn';
      close.textContent = 'Close';
      close.addEventListener('click', ()=>{ closePopup(); });
      elModalActions.appendChild(close);
    }

    elMask.style.display = 'block';
  }

  function openCardPickPopup(title, cards, {helperText='', forcePortrait=false, forceLandscape=false, allowSkip=true } = {}){
    // Like openCardListPopup, but each card is clickable to resolve pending (idx=0).
    let cardsList = (Array.isArray(cards) ? cards.slice() : []).filter(c=>!!c);
    popup = {type:'pending', title, cards: cardsList.slice(), closable:false, helperText};

    elModalTitle.textContent = title;
    setRichText(elModalText, helperText || '');
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const dimsP = standardSize('portrait');
    const dimsL = standardSize('landscape');
    const maxW = Math.max(dimsP.w, dimsL.w);
    const maxH = Math.max(dimsP.h, dimsL.h);

    const surf = document.createElement('div');
    surf.className = 'surf';
    surf.style.height = (maxH + 12) + 'px';
    const step = maxW * 0.45; // overlap ~55%
    const minW = (cardsList.length<=1) ? (maxW + 24) : (maxW + step*(cardsList.length-1) + 24);
    surf.style.minWidth = minW + 'px';

    cardsList.forEach((cn, i)=>{
      const s = String(cn);
      const orient = forceLandscape ? 'landscape' : (forcePortrait ? 'portrait' : intrinsicOrient(s));
      const d = (orient==='landscape') ? dimsL : dimsP;
      const x = 12 + step*i + (maxW - d.w)/2;
      const y = 6 + (maxH - d.h)/2;
      const c = makeCard(s, orient, x, y, d.w, d.h, '', async ()=>{
        st = await apiCmd('resolve_pending', {idx:0, choice: s});
        selHand = [];
        updateTop();
        render();
      }, false, 100+i);
      surf.appendChild(c);
    });

    elModalCards.appendChild(surf);

    if(allowSkip){
      const bSkip = document.createElement('button');
      bSkip.className = 'miniBtn';
      bSkip.textContent = 'Skip';
      bSkip.addEventListener('click', async (ev)=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
        selHand = [];
        updateTop();
        render();
      });
      elModalActions.appendChild(bSkip);
    }

    elMask.style.display = 'block';
  }

  function closePopup(){
    popup = {type:null};
    elMask.style.display = 'none';
    clearModalLead();
    elModalCards.innerHTML = '';
    elModalText.textContent = '';
    elModalActions.innerHTML = '';
  }

  function showReorderPopup(p){
    const pool = Array.isArray(p.pool) ? p.pool.slice() : [];
    const kept = Array.isArray(p.kept) ? p.kept.slice() : [];

    popup = {type:'pending', closable:false};
    elModalTitle.textContent = 'カード順番を決める';
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';
    elModalText.innerHTML = '';

    const dimsP = standardSize('portrait');
    const dimsL = standardSize('landscape');

    let deckList    = pool.slice();
    let discardList = [];
    let dragSrc = null; // {list:'deck'|'discard', idx:number}

    // ── DOM ──
    const cols = document.createElement('div');
    cols.style.cssText = 'display:flex;gap:12px;align-items:stretch;overflow:hidden;';

    const leftWrap = document.createElement('div');
    leftWrap.style.cssText = 'flex:1;min-width:0;display:flex;flex-direction:column;gap:6px;';
    const leftLabel = document.createElement('div');
    leftLabel.style.cssText = 'font-size:12px;color:#f9a;font-weight:700;padding:2px 0;';
    leftLabel.textContent = '← 山札に残す（左が一番上）';
    const leftRow = document.createElement('div');
    leftRow.className = 'reorderRow';
    leftRow.style.cssText = 'flex-wrap:wrap;min-height:80px;border:1px dashed rgba(249,170,200,.3);border-radius:10px;padding:8px;';
    leftWrap.appendChild(leftLabel);
    leftWrap.appendChild(leftRow);

    const rightWrap = document.createElement('div');
    rightWrap.style.cssText = 'flex:1;min-width:0;display:flex;flex-direction:column;gap:6px;';
    const rightLabel = document.createElement('div');
    rightLabel.style.cssText = 'font-size:12px;color:#aaa;font-weight:700;padding:2px 0;';
    rightLabel.textContent = '控え室へ送る';
    const rightRow = document.createElement('div');
    rightRow.className = 'reorderRow';
    rightRow.style.cssText = 'flex-wrap:wrap;min-height:80px;border:1px dashed rgba(180,180,180,.25);border-radius:10px;padding:8px;';
    rightWrap.appendChild(rightLabel);
    rightWrap.appendChild(rightRow);

    cols.appendChild(leftWrap);
    cols.appendChild(rightWrap);
    elModalCards.appendChild(cols);

    function getList(listName){ return listName === 'deck' ? deckList : discardList; }

    // ── 中央化されたドロップ処理（インデックスずれを正しく補正）──
    function handleDrop(dstListName, dstIdx){
      if(!dragSrc) return;
      const {list: srcListName, idx: srcIdx} = dragSrc;
      dragSrc = null;

      const srcList = getList(srcListName);
      const dstList = getList(dstListName);

      // srcListから取り出す
      if(srcIdx < 0 || srcIdx >= srcList.length) return; // 安全チェック
      const [moved] = srcList.splice(srcIdx, 1);

      if(srcListName === dstListName){
        // 同一リスト内並び替え：splice後にインデックスがずれるので補正
        const adjustedDst = (srcIdx < dstIdx) ? dstIdx - 1 : dstIdx;
        const clampedDst  = Math.max(0, Math.min(adjustedDst, dstList.length));
        dstList.splice(clampedDst, 0, moved);
      } else {
        // 別リストへ移動
        const clampedDst = Math.max(0, Math.min(dstIdx, dstList.length));
        dstList.splice(clampedDst, 0, moved);
      }
      rebuild();
    }

    function makeCard(cn, listName, idx){
      const intr = intrinsicOrient(cn);
      const d = intr==='landscape' ? dimsL : dimsP;
      const wrap = document.createElement('div');
      wrap.className = 'reorderCard';
      wrap.style.width  = d.w+'px';
      wrap.style.height = d.h+'px';
      wrap.draggable = true;

      const img = document.createElement('img');
      img.src = imgUrl(cn); img.alt = cn; img.draggable = false;

      const badge = document.createElement('div');
      badge.className = 'idxBadge';
      if(listName === 'deck'){
        badge.textContent = (kept.length + idx + 1)+'番目';
        badge.style.background = 'rgba(249,100,160,.8)';
      } else {
        badge.textContent = '控え室';
        badge.style.background = 'rgba(100,100,100,.8)';
      }
      const cap = document.createElement('div');
      cap.className = 'cnCap'; cap.textContent = cn;

      wrap.appendChild(img); wrap.appendChild(badge); wrap.appendChild(cap);

      wrap.addEventListener('dragstart', ev=>{
        dragSrc = {list: listName, idx};
        wrap.classList.add('dragging');
        ev.stopPropagation();
      });
      wrap.addEventListener('dragend', ()=>{
        wrap.classList.remove('dragging');
      });
      wrap.addEventListener('dragover', ev=>{
        ev.preventDefault();
        ev.stopPropagation();
        wrap.classList.add('dragover');
      });
      wrap.addEventListener('dragleave', ()=> wrap.classList.remove('dragover'));
      wrap.addEventListener('drop', ev=>{
        ev.preventDefault();
        ev.stopPropagation();
        wrap.classList.remove('dragover');
        handleDrop(listName, idx);
      });

      return wrap;
    }

    function rebuild(){
      leftRow.innerHTML  = '';
      rightRow.innerHTML = '';

      // 確定済みカード（ロック表示、左列）
      kept.forEach((cn, ki)=>{
        const intr = intrinsicOrient(cn);
        const d = intr==='landscape' ? dimsL : dimsP;
        const wrap = document.createElement('div');
        wrap.className = 'reorderCard';
        wrap.style.cssText = `width:${d.w}px;height:${d.h}px;opacity:.45;cursor:default;`;
        const img = document.createElement('img');
        img.src = imgUrl(cn); img.alt = cn; img.draggable = false;
        const badge = document.createElement('div');
        badge.className = 'idxBadge';
        badge.textContent = (ki+1)+'番目（確定）';
        const cap = document.createElement('div');
        cap.className = 'cnCap'; cap.textContent = cn;
        wrap.appendChild(img); wrap.appendChild(badge); wrap.appendChild(cap);
        leftRow.appendChild(wrap);
      });

      deckList.forEach((cn, i)=>{
        leftRow.appendChild(makeCard(cn, 'deck', i));
      });
      discardList.forEach((cn, i)=>{
        rightRow.appendChild(makeCard(cn, 'discard', i));
      });
    }

    // ── 行エリアのドロップゾーン（末尾追加）──1回だけ設定 ──
    function setupRowDrop(row, listName){
      row.addEventListener('dragover', ev=>{
        // カード上でのdragoverはカード側で処理済み（stopPropagation）
        // ここに来るのは行の空白部分のみ
        ev.preventDefault();
        row.style.outline = '2px solid rgba(255,255,255,.15)';
      });
      row.addEventListener('dragleave', ev=>{
        if(!row.contains(ev.relatedTarget)) row.style.outline = '';
      });
      row.addEventListener('drop', ev=>{
        ev.preventDefault();
        row.style.outline = '';
        // カードへのドロップはstopPropagationで止められているのでここは空白部分のみ
        handleDrop(listName, getList(listName).length);
      });
    }

    // ★ setupRowDrop は rebuild() の外で1回だけ呼ぶ
    setupRowDrop(leftRow,  'deck');
    setupRowDrop(rightRow, 'discard');

    rebuild();

    // ── ボタン ──
    const bConfirm = document.createElement('button');
    bConfirm.className = 'miniBtn';
    bConfirm.style.cssText = 'background:rgba(249,170,200,.25);font-weight:700;';
    bConfirm.textContent = '確定';
    bConfirm.addEventListener('click', async ()=>{
      bConfirm.disabled = true;
      for(const cn of deckList){
        st = await apiCmd('resolve_pending', {idx:0, choice: cn});
      }
      st = await apiCmd('resolve_pending', {idx:0, choice: 'skip'});
      selHand = []; updateTop(); render();
    });

    const bSkipAll = document.createElement('button');
    bSkipAll.className = 'miniBtn';
    bSkipAll.textContent = '全て控え室へ';
    bSkipAll.addEventListener('click', async ()=>{
      bSkipAll.disabled = true;
      st = await apiCmd('resolve_pending', {idx:0, choice: 'skip'});
      selHand = []; updateTop(); render();
    });

    elModalActions.appendChild(bConfirm);
    elModalActions.appendChild(bSkipAll);
    elMask.style.display = 'block';
  }


  
  function looksLikeCardNo(x){
    if(x==null) return false;
    const s = String(x).trim();
    if(!s) return false;
    // Exact cardnumber only. Labels like "C: PL!N-bp1-003 ライブ開始時" must NOT match.
    // Prefixes: PL!, PL!N, PL!S, PL!SP, PL!HS, LL (series suffix optional after !)
    return /^(?:PL!|LL)[A-Za-z0-9]*-(?:bp\d+|pb\d+|sd\d+|PR|P\d+)-\d{3}$/i.test(s);
  }

  function showPending(p){
    const kind = (p && p.kind) ? String(p.kind) : '';
    setModalLeadFromPending(p);

    // Drag-and-drop reorder UI
    if(kind === 'reorder_topk_keep_any'){
      showReorderPopup(p);
      return;
    }

    // デッキ上K枚公開 → フィルタ不一致（全カード控え室へ）確認ポップアップ
    if(kind === 'view_topk_no_match'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards : [];
      // openCardListPopup のレンダリングロジックをそのまま利用
      openCardListPopup('デッキ公開', displayCards, {
        closable: false,
        helperText: '条件に一致するカードがありません。全カードを控え室へ送ります。'
      });
      // popup種別を pending に上書き（resolve_pending を送るため）
      popup = {type:'pending', closable:false};
      const btnOk = document.createElement('button');
      btnOk.className = 'miniBtn';
      btnOk.textContent = '確認';
      let _vtSubmitting = false;
      btnOk.addEventListener('click', async ev => {
        ev.stopPropagation();
        if(_vtSubmitting) return;
        _vtSubmitting = true;
        st = await apiCmd('resolve_pending', {idx:0, choice:'ok'});
        selHand = [];
        updateTop();
        render();
      });
      elModalActions.appendChild(btnOk);
      return;
    }

    // デッキ上K枚公開 → 候補(左)／その他(右) の左右分割選択UI
    if(kind === 'choose_from_topk'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards
                         : (Array.isArray(p.options) ? p.options : []);
      const candidates = Array.isArray(p.candidates) ? p.candidates : [];
      const optional   = (p.optional === true || p.optional === 'true' || candidates.length === 0);
      const helperText = String((p && (p.text || p.prompt || p.message))
                         ? (p.text || p.prompt || p.message)
                         : (candidates.length > 0 ? '候補カードをクリックして選択' : '該当カードなし'));

      popup = {type:'pending', closable:false};
      elModalTitle.textContent = 'デッキ公開';
      setRichText(elModalText, helperText);
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';

      const candidateSet = new Set(candidates.map(c => String(c).trim()));
      const leftCards  = displayCards.filter(c => candidateSet.has(String(c).trim()));
      const rightCards = displayCards.filter(c => !candidateSet.has(String(c).trim()));

      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      const maxW  = Math.max(dimsP.w, dimsL.w);
      const maxH  = Math.max(dimsP.h, dimsL.h);

      // surf（カード列）を生成するヘルパー
      function makeSplitSurf(cards, clickable){
        const surf = document.createElement('div');
        surf.className = 'surf';
        surf.style.height = (maxH + 12) + 'px';
        const step = maxW * 0.45;
        const minW = (cards.length <= 1) ? (maxW + 24) : (maxW + step*(cards.length-1) + 24);
        surf.style.minWidth = minW + 'px';
        cards.forEach((cn, i) => {
          const s = String(cn).trim();
          const orient = intrinsicOrient(s);
          const d = (orient === 'landscape') ? dimsL : dimsP;
          const x = 12 + step*i + (maxW - d.w)/2;
          const y = 6  + (maxH - d.h)/2;
          let clickFn = null;
          if(clickable){
            clickFn = async () => {
              st = await apiCmd('resolve_pending', {idx:0, choice: s});
              selHand = [];
              updateTop();
              render();
            };
          }
          const c = makeCard(s, orient, x, y, d.w, d.h, '', clickFn, false, 100+i);
          if(!clickable){
            c.style.opacity = '0.35';
            c.style.filter  = 'grayscale(80%)';
            c.style.cursor  = 'default';
          }
          surf.appendChild(c);
        });
        return surf;
      }

      // 左右分割ラッパー
      const splitWrap = document.createElement('div');
      splitWrap.style.cssText = 'display:flex;gap:0;align-items:flex-start;';

      if(leftCards.length > 0){
        const col = document.createElement('div');
        col.style.cssText = 'flex:0 0 auto;';
        const lbl = document.createElement('div');
        lbl.style.cssText = 'color:#ffe066;font-size:11px;margin-bottom:3px;text-align:center;padding:0 12px;';
        lbl.textContent = '▼ 候補（クリックで選択）';
        col.appendChild(lbl);
        col.appendChild(makeSplitSurf(leftCards, true));
        splitWrap.appendChild(col);
      }

      if(leftCards.length > 0 && rightCards.length > 0){
        const sep = document.createElement('div');
        sep.style.cssText = 'width:2px;background:#444;align-self:stretch;flex-shrink:0;margin:0 8px;';
        splitWrap.appendChild(sep);
      }

      if(rightCards.length > 0){
        const col = document.createElement('div');
        col.style.cssText = 'flex:0 0 auto;';
        const lbl = document.createElement('div');
        lbl.style.cssText = 'color:#777;font-size:11px;margin-bottom:3px;text-align:center;padding:0 12px;';
        lbl.textContent = 'その他（選択不可）';
        col.appendChild(lbl);
        col.appendChild(makeSplitSurf(rightCards, false));
        splitWrap.appendChild(col);
      }

      elModalCards.appendChild(splitWrap);

      if(optional){
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn';
        bSkip.textContent = 'スキップ';
        let _cfSubmitting = false;
        bSkip.addEventListener('click', async ev => {
          ev.stopPropagation();
          if(_cfSubmitting) return;
          _cfSubmitting = true;
          st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
          selHand = [];
          updateTop();
          render();
        });
        elModalActions.appendChild(bSkip);
      }

      elMask.style.display = 'block';
      return;
    }

    // BODY起動: デッキ上5枚からライブカードを1枚選択（choose_from_topkと同じ左右分割UI）
    if(kind === 'body_reveal_pick_live'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards
                         : (Array.isArray(p.pool) ? p.pool : []);
      const candidates = Array.isArray(p.candidates) ? p.candidates
                       : (Array.isArray(p.live_cands) ? p.live_cands : []);
      const helperText = String((p && (p.text || p.prompt || p.message))
                         ? (p.text || p.prompt || p.message)
                         : 'ライブカードをクリックして選択（スキップ可）');

      popup = {type:'pending', closable:false};
      elModalTitle.textContent = 'デッキ公開';
      setRichText(elModalText, helperText);
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';

      const candidateSet = new Set(candidates.map(c => String(c).trim()));
      const leftCards  = displayCards.filter(c => candidateSet.has(String(c).trim()));
      const rightCards = displayCards.filter(c => !candidateSet.has(String(c).trim()));

      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      const maxW  = Math.max(dimsP.w, dimsL.w);
      const maxH  = Math.max(dimsP.h, dimsL.h);

      function makeBodySurf(cards, clickable){
        const surf = document.createElement('div');
        surf.className = 'surf';
        surf.style.height = (maxH + 12) + 'px';
        const step = maxW * 0.45;
        const minW = (cards.length <= 1) ? (maxW + 24) : (maxW + step*(cards.length-1) + 24);
        surf.style.minWidth = minW + 'px';
        cards.forEach((cn, i) => {
          const s = String(cn).trim();
          const orient = intrinsicOrient(s);
          const d = (orient === 'landscape') ? dimsL : dimsP;
          const x = 12 + step*i + (maxW - d.w)/2;
          const y = 6  + (maxH - d.h)/2;
          let clickFn = null;
          if(clickable){
            clickFn = async () => {
              st = await apiCmd('resolve_pending', {idx:0, choice: s});
              selHand = [];
              updateTop();
              render();
            };
          }
          const c = makeCard(s, orient, x, y, d.w, d.h, '', clickFn, false, 100+i);
          if(!clickable){
            c.style.opacity = '0.35';
            c.style.filter  = 'grayscale(80%)';
            c.style.cursor  = 'default';
          }
          surf.appendChild(c);
        });
        return surf;
      }

      const splitWrap = document.createElement('div');
      splitWrap.style.cssText = 'display:flex;gap:0;align-items:flex-start;';

      if(leftCards.length > 0){
        const col = document.createElement('div');
        col.style.cssText = 'flex:0 0 auto;';
        const lbl = document.createElement('div');
        lbl.style.cssText = 'color:#ffe066;font-size:11px;margin-bottom:3px;text-align:center;padding:0 12px;';
        lbl.textContent = '▼ ライブカード（クリックで選択）';
        col.appendChild(lbl);
        col.appendChild(makeBodySurf(leftCards, true));
        splitWrap.appendChild(col);
      }

      if(leftCards.length > 0 && rightCards.length > 0){
        const sep = document.createElement('div');
        sep.style.cssText = 'width:2px;background:#444;align-self:stretch;flex-shrink:0;margin:0 8px;';
        splitWrap.appendChild(sep);
      }

      if(rightCards.length > 0){
        const col = document.createElement('div');
        col.style.cssText = 'flex:0 0 auto;';
        const lbl = document.createElement('div');
        lbl.style.cssText = 'color:#777;font-size:11px;margin-bottom:3px;text-align:center;padding:0 12px;';
        lbl.textContent = 'その他（選択不可）';
        col.appendChild(lbl);
        col.appendChild(makeBodySurf(rightCards, false));
        splitWrap.appendChild(col);
      }

      elModalCards.appendChild(splitWrap);

      const bSkip = document.createElement('button');
      bSkip.className = 'miniBtn';
      bSkip.textContent = 'Skip';
      let _brSubmitting = false;
      bSkip.addEventListener('click', async ev => {
        ev.stopPropagation();
        if(_brSubmitting) return;
        _brSubmitting = true;
        st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
        selHand = [];
        updateTop();
        render();
      });
      elModalActions.appendChild(bSkip);

      elMask.style.display = 'block';
      return;
    }

    // Multi-select: named_cards_cost_multi（控え室からN枚選択→デッキ下へ）
    if(kind === 'named_cards_cost_multi'){
      const total = (p && p.total) ? parseInt(p.total) : 0;
      const opts = (p && Array.isArray(p.options)) ? p.options : [];
      const title = String((p && (p.text || p.prompt || p.message)) ? (p.text || p.prompt || p.message) : `控え室から${total}枚選択`);

      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '選択';
      setRichText(elModalText, title);
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';

      // Track selected card indices (allow duplicates by index)
      const selected = [];  // array of indices into opts

      const dimsP = standardSize('portrait');
      const row = document.createElement('div');
      row.className = 'choiceRow';

      // Counter display
      const counter = document.createElement('div');
      counter.style.cssText = 'width:100%;text-align:center;color:#fff;font-size:13px;margin-bottom:4px;padding:2px 0;';
      counter.textContent = `選択: 0 / ${total}`;

      const doneBtn = document.createElement('button');
      doneBtn.className = 'miniBtn';
      doneBtn.textContent = `確定 (0/${total})`;
      doneBtn.disabled = true;
      doneBtn.style.opacity = '0.5';

      // Track highlight per button (may need to pick same card twice)
      const btnMap = {};  // index -> button element
      const pickCount = {};  // cardnumber -> how many times picked

      function updateCounter(){
        const n = selected.length;
        counter.textContent = `選択: ${n} / ${total}`;
        doneBtn.textContent = `確定 (${n}/${total})`;
        doneBtn.disabled = (n !== total);
        doneBtn.style.opacity = (n === total) ? '1' : '0.5';

        // Update all button highlights
        const seen = {};
        opts.forEach((cn, i) => {
          const k = String(cn).trim();
          seen[k] = (seen[k]||0);
        });
        const selCount = {};
        selected.forEach(idx => {
          const k = String(opts[idx]).trim();
          selCount[k] = (selCount[k]||0) + 1;
        });

        opts.forEach((cn, i) => {
          const b = btnMap[i];
          if(!b) return;
          const k = String(cn).trim();
          // How many times is this specific index selected?
          const timesThisIdx = selected.filter(x => x === i).length;
          if(timesThisIdx > 0){
            b.style.outline = `3px solid #ffe066`;
            b.style.outlineOffset = '-3px';
            const cap = b.querySelector('.choiceCap');
            if(cap) cap.textContent = k + (timesThisIdx > 1 ? ` ×${timesThisIdx}` : ' ✓');
          } else {
            b.style.outline = '';
            b.style.outlineOffset = '';
            // restore original caption with dup count
            const dup = opts.filter(x => String(x).trim() === k).length;
            const nth = opts.slice(0, i).filter(x => String(x).trim() === k).length + 1;
            const cap = b.querySelector('.choiceCap');
            if(cap) cap.textContent = (dup > 1) ? `${k} (${nth}/${dup})` : k;
          }
        });
      }

      const dupCount = {};
      opts.forEach(o => { const k=String(o).trim(); dupCount[k]=(dupCount[k]||0)+1; });
      const dupSeen = {};

      opts.forEach((opt, i) => {
        const cn = String(opt).trim();
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = dimsP.w + 'px';
        b.style.height = dimsP.h + 'px';

        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;
        b.appendChild(img);

        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        dupSeen[cn] = (dupSeen[cn]||0) + 1;
        cap.textContent = cardChoiceCaption(cn, dupSeen[cn], dupCount[cn]);
        b.appendChild(cap);

        btnMap[i] = b;

        b.addEventListener('click', ev => {
          ev.stopPropagation();
          const alreadyIdx = selected.lastIndexOf(i);
          if(alreadyIdx >= 0){
            // deselect one instance
            selected.splice(alreadyIdx, 1);
          } else if(selected.length < total){
            selected.push(i);
          }
          updateCounter();
        });

        row.appendChild(b);
      });

      let submitting = false;
      doneBtn.addEventListener('click', async ev => {
        ev.stopPropagation();
        if(selected.length !== total) return;
        if(submitting) return;
        submitting = true;
        const choiceStr = selected.map(i => String(opts[i]).trim()).join(',');
        st = await apiCmd('resolve_pending', {idx:0, choice: choiceStr});
        selHand = [];
        updateTop();
        render();
      });

      elModalCards.appendChild(counter);
      elModalCards.appendChild(row);
      elModalActions.appendChild(doneBtn);
      elMask.style.display = 'block';
      return;
    }

    popup = {type:'pending', closable:false};
    elModalTitle.textContent = pendingTitleFor(p);
    const pendText = pendingTextFor(p);
    setRichText(elModalText, pendText);
    const allowSkip = !!((p && (p.allow_less || p.allow_skip)) || /Skip可/i.test(pendText) || /\bskip\b/i.test(pendText) || (kind && /pick/i.test(kind)));
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const opts = (p && (Array.isArray(p.options)?p.options: (Array.isArray(p.candidates)?p.candidates:(Array.isArray(p.cards)?p.cards:(Array.isArray(p.shown)?p.shown:[]))))) || [];

    // Special: 成功ライブカード置き場へ置くカード選択（Skip可）
    if(kind === 'pick_success_to_store'){
      const cards = opts.filter(o=>looksLikeCardNo(o));
      openCardPickPopup('成功ライブ', cards, {helperText: pendText || '成功ライブカード置き場に置くカードを選択（Skip可）', forceLandscape:true, allowSkip:true});
      return;
    }

    if(kind === 'auto_order' && Array.isArray(p.queue) && p.queue.length){
      const row = document.createElement('div');
      row.className = 'choiceRow';

      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      const queue = Array.isArray(p.queue) ? p.queue : [];

      const items = opts.map((opt, i)=>{
        const trig = queue[i] || {};
        const cn = String((trig && trig.source_cn) ? trig.source_cn : '').trim();
        const label = String(opt || '').trim();
        return {label, cn};
      }).filter(it=>it.label);

      items.forEach(it=>{
        const b = document.createElement('button');
        b.className = 'choiceBtn';

        if(looksLikeCardNo(it.cn)){
          const intr = intrinsicOrient(it.cn);
          const d = (intr==='landscape') ? dimsL : dimsP;
          b.style.width = d.w + 'px';
          b.style.height = d.h + 'px';

          const img = document.createElement('img');
          img.src = imgUrl(it.cn);
          img.alt = it.cn;
          b.appendChild(img);
        }else{
          const d = dimsP;
          b.style.width = d.w + 'px';
          b.style.height = d.h + 'px';
        }

        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = it.label;
        b.appendChild(cap);

        b.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: it.label});
          selHand = [];
          updateTop();
          render();
        });

        row.appendChild(b);
      });

      elModalCards.appendChild(row);
      elMask.style.display = 'block';
      return;
    }

    const allCardNo = opts.length && opts.every(o=>looksLikeCardNo(o));

    // position_change: show stage position choices as image buttons (same style as stage-choice UI)
    if(kind === 'position_change'){
      const stagePosHasSkipPC = opts.some(o => String(o).toLowerCase() === 'skip');
      const stageEntriesPC = opts
        .filter(o => String(o).toLowerCase() !== 'skip')
        .map(o=>{
          const raw = String(o || '').trim();
          const pos = raw ? raw[0].toUpperCase() : '';
          return { raw, pos };
        });
      const allStagePosPC = stageEntriesPC.length && stageEntriesPC.every(e=>['L','C','R'].includes(e.pos));
      if(allStagePosPC){
        const stage = (st && st.stage) ? st.stage : {};
        const srcPos = String((p && (p.src_pos || p.pos || '')) || '').trim().toUpperCase();
        const srcSlot = srcPos && stage[srcPos] ? stage[srcPos] : null;
        const srcCn = srcSlot ? String(srcSlot.cardnumber || '') : '';
        const srcName = srcSlot ? String(srcSlot.cardname || srcSlot.name || srcCn || '') : '';
        elModalTitle.textContent = 'ポジションチェンジ';
        const explicitPcText = pendingTextFor(p);
        setRichText(elModalText, explicitPcText || (srcName
          ? `${srcName}${srcPos ? `（現在 ${srcPos}）` : ''} の移動先を選んでください。移動先にメンバーがいる場合は入れ替わります。`
          : `移動先を選んでください。移動先にメンバーがいる場合は入れ替わります。`));
        const row = document.createElement('div');
        row.className = 'choiceRow';
        const dimsP = standardSize('portrait');
        const dimsL = standardSize('landscape');
        stageEntriesPC.forEach(({raw, pos})=>{
          const posU = pos;
          const slotData = stage[posU];
          const cn = slotData ? String(slotData.cardnumber || '') : '';
          const cardname = slotData ? String(slotData.cardname || slotData.name || '') : '';
          const isWait = !!(slotData && slotData.active === false);
          const btnDims = isWait ? dimsL : dimsP;
          const b = document.createElement('button');
          b.className = 'choiceBtn';
          b.style.width    = btnDims.w + 'px';
          b.style.height   = btnDims.h + 'px';
          b.style.position = 'relative';
          b.style.overflow = 'hidden';
          if(cn && looksLikeCardNo(cn)){
            const img = document.createElement('img');
            img.src = imgUrl(cn); img.alt = cn;
            if(isWait){
              img.style.width           = btnDims.h + 'px';
              img.style.height          = btnDims.w + 'px';
              img.style.position        = 'absolute';
              img.style.top             = '50%';
              img.style.left            = '50%';
              img.style.transform       = 'translate(-50%, -50%) rotate(-90deg)';
              img.style.transformOrigin = 'center center';
            }
            b.appendChild(img);
          }
          if(isWait){
            const badge = document.createElement('div');
            badge.style.cssText = 'position:absolute;top:6px;right:6px;background:rgba(220,120,0,.92);color:#fff;font-size:11px;font-weight:bold;padding:3px 7px;border-radius:5px;pointer-events:none;z-index:10;letter-spacing:0.05em;box-shadow:0 1px 4px rgba(0,0,0,.4);';
            badge.textContent = 'WAIT';
            b.appendChild(badge);
          }
          const cap = document.createElement('div');
          cap.className = 'choiceCap';
          cap.textContent = cn
            ? `${posU}${cardname ? `: ${cardname}` : `: ${cn}`}${isWait ? ' [WAIT]' : ''}`
            : `${posU}（空）`;
          b.appendChild(cap);
          b.addEventListener('click', async ev=>{
            ev.stopPropagation();
            st = await apiCmd('resolve_pending', {idx:0, choice: raw || posU});
            selHand=[]; updateTop(); render();
          });
          row.appendChild(b);
        });
        elModalCards.appendChild(row);
        if(stagePosHasSkipPC){
          const bSkip = document.createElement('button');
          bSkip.className = 'miniBtn'; bSkip.textContent = 'スキップ';
          bSkip.addEventListener('click', async ev=>{
            ev.stopPropagation();
            st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
            selHand=[]; updateTop(); render();
          });
          elModalActions.appendChild(bSkip);
        }
        elMask.style.display = 'block';
        return;
      }
    }

    // Stage position options (plain L/C/R or labels like 'L: ...') → ステージカード画像で表示
    // Stage position options (plain L/C/R or labels like 'L: ...') → ステージカード画像で表示
    // skip を除外してからL/C/R判定する（choose_stage_member_to_activate など skip混入ケース対応）
    const stagePosHasSkip = opts.some(o => String(o).toLowerCase() === 'skip');
    const stageEntries = opts
      .filter(o => String(o).toLowerCase() !== 'skip')
      .map(o=>{
        const raw = String(o || '').trim();
        const pos = raw ? raw[0].toUpperCase() : '';
        return { raw, pos };
      });
    const allStagePos = stageEntries.length && stageEntries.every(e=>['L','C','R'].includes(e.pos));
    if(allStagePos){
      const row = document.createElement('div');
      row.className = 'choiceRow';
      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      stageEntries.forEach(({raw, pos})=>{
        const posU = pos;
        const stage = (st && st.stage) ? st.stage : {};
        const slotData = stage[posU];
        const cn = slotData ? String(slotData.cardnumber || '') : '';
        const isWait = !!(slotData && slotData.active === false);
        const btnDims = isWait ? dimsL : dimsP;
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width    = btnDims.w + 'px';
        b.style.height   = btnDims.h + 'px';
        b.style.position = 'relative';
        b.style.overflow = 'hidden';
        if(cn && looksLikeCardNo(cn)){
          const img = document.createElement('img');
          img.src = imgUrl(cn); img.alt = cn;
          if(isWait){
            img.style.width           = btnDims.h + 'px';
            img.style.height          = btnDims.w + 'px';
            img.style.position        = 'absolute';
            img.style.top             = '50%';
            img.style.left            = '50%';
            img.style.transform       = 'translate(-50%, -50%) rotate(-90deg)';
            img.style.transformOrigin = 'center center';
          }
          b.appendChild(img);
        }
        if(isWait){
          const badge = document.createElement('div');
          badge.style.cssText = 'position:absolute;top:6px;right:6px;background:rgba(220,120,0,.92);color:#fff;font-size:11px;font-weight:bold;padding:3px 7px;border-radius:5px;pointer-events:none;z-index:10;letter-spacing:0.05em;box-shadow:0 1px 4px rgba(0,0,0,.4);';
          badge.textContent = 'WAIT';
          b.appendChild(badge);
        }
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = raw || (posU + (cn ? `: ${cn}` : '（空）') + (isWait ? ' [WAIT]' : ''));
        b.appendChild(cap);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: raw || posU});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      elModalCards.appendChild(row);
      if(allowSkip || stagePosHasSkip){
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn'; bSkip.textContent = 'スキップ';
        bSkip.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
          selHand=[]; updateTop(); render();
        });
        elModalActions.appendChild(bSkip);
      }
      elMask.style.display = 'block';
      return;
    }

    // topdeck_from_green: card images + optional Skip button
    if(kind === 'topdeck_from_green'){
      const cardOpts = opts.filter(o => looksLikeCardNo(String(o)));
      const hasSkip  = opts.some(o => String(o).toLowerCase() === 'skip');
      const row = document.createElement('div');
      row.className = 'choiceRow';
      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      const dupCount = {};
      cardOpts.forEach(o=>{ const k=String(o).trim(); dupCount[k]=(dupCount[k]||0)+1; });
      const dupSeen = {};
      cardOpts.forEach(cn=>{
        cn = String(cn).trim();
        const intr = intrinsicOrient(cn);
        const d = (intr==='landscape') ? dimsL : dimsP;
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = d.w + 'px';
        b.style.height = d.h + 'px';
        const img = document.createElement('img');
        img.src = imgUrl(cn); img.alt = cn;
        dupSeen[cn] = (dupSeen[cn]||0)+1;
        const nth = dupSeen[cn]; const tot = dupCount[cn]||0;
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = cardChoiceCaption(cn, nth, tot);
        b.appendChild(img); b.appendChild(cap);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: cn});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      elModalCards.appendChild(row);
      if(hasSkip){
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn'; bSkip.textContent = 'スキップ';
        bSkip.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
          selHand=[]; updateTop(); render();
        });
        elModalActions.appendChild(bSkip);
      }
      elMask.style.display = 'block';
      return;
    }

    if(allCardNo){
      // Render as image list (clickable) in modalCards; keep card size unified
      const row = document.createElement('div');
      row.className = 'choiceRow';

      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');

      const dupCount = {};
      opts.forEach(o=>{
        const k = String(o).trim();
        if(!k) return;
        dupCount[k] = (dupCount[k]||0) + 1;
      });
      const dupSeen = {};

      opts.forEach(opt=>{
        const cn = String(opt).trim();
        const intr = intrinsicOrient(cn);
        const d = (intr==='landscape') ? dimsL : dimsP;

        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = d.w + 'px';
        b.style.height = d.h + 'px';

        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;

        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        dupSeen[cn] = (dupSeen[cn]||0)+1;
        const nth = dupSeen[cn];
        const tot = dupCount[cn]||0;
        cap.textContent = cardChoiceCaption(cn, nth, tot);

        b.appendChild(img);
        b.appendChild(cap);

        b.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: cn});
          selHand = [];
          updateTop();
          render();
        });

        row.appendChild(b);
      });

      elModalCards.appendChild(row);

      if(allowSkip){
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn';
        bSkip.textContent = 'スキップ';
        bSkip.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
          selHand = [];
          updateTop();
          render();
        });
        elModalActions.appendChild(bSkip);
      }

    }else if(opts.length){
      // Fallback: text buttons
      opts.forEach(opt=>{
        const b = document.createElement('button');
        b.className = 'miniBtn';
        b.textContent = choiceTextLabel(opt);
        b.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:String(opt)});
          selHand = [];
          updateTop();
          render();
        });
        elModalActions.appendChild(b);
      });
    }

    elMask.style.display = 'block';
  }

  function maybeShowPending(){
    const p = (st && Array.isArray(st.pending) && st.pending.length) ? st.pending[0] : null;
    if(p){
      showPending(p);
      return true;
    }
    if(popup && popup.type==='pending'){
      closePopup();
    }
    return false;
  }

  function maybeShowResolvePopup(){
    const rz = (st && Array.isArray(st.resolve_zone)) ? st.resolve_zone : [];
    if(rz.length > 0){
      // confirm-only popup; user proceeds with NEXT.
      openCardListPopup('解決領域', rz, {closable:false, helperText:'NEXTで次へ進みます', forcePortrait:true});
    }else{
      // if the current popup is resolve, close it
      if(popup && popup.type==='cardlist' && !popup.closable){
        closePopup();
      }
    }
  }

  function updateTop(){
    elTurn.textContent = st ? String(st.turn) : '?';
    elPhase.textContent = st ? String(st.phase) : '?';
    const active = st ? Number(st.energy_active||0) : 0;
    const wait = st ? Number(st.energy_wait||0) : 0;
    elEnergy.textContent = st ? `${active}/${active+wait}` : '?';
    elSelected.textContent = String(selHand.length);
    setBanner(st && st.banner && st.banner.text ? String(st.banner.text) : '');
  }

  function render(){
    if(!st) return;
    elZones.innerHTML = '';

    // build zones
    const zels = {};
    for(const [k,z] of Object.entries(layout.zones)){
      const zd = zoneDiv(z);
      zels[k] = zd;
      elZones.appendChild(zd);
      if(z.kind==='log') renderLog(zd, st.log || []);
    }

    // DECK: 山札あり→裏面表示、なし→何も表示しない
    const deckCount = (st.deck||[]).length;
    if(deckCount > 0){
      renderTopCard(zels.deck, '__BACK__', 'portrait', deckCount, null);
    }else{
      renderEmptyZone(zels.deck, 0, null);
    }

    // Waiting room: カードあり→最後尾を表示、なし→何も表示しない
    const gr = Array.isArray(st.green_room) ? st.green_room : [];
    if(gr.length){
      renderTopCard(zels.green, String(gr[gr.length-1]), 'portrait', gr.length, ()=>{
        openCardListPopup('控え室', gr, {closable:true, helperText:''});
      });
    }else{
      renderEmptyZone(zels.green, 0, null);
    }

    // Success live storage: カードあり→縦スタック表示、なし→何も表示しない
    const sz = Array.isArray(st.success_zone) ? st.success_zone : [];
    if(sz.length){
      renderVertStack(zels.success, sz, 'landscape', sz.length, ()=>{
        openCardListPopup('成功ライブ', sz, {closable:true, helperText:'', forceLandscape:true});
      }, {overlap:0.70, maxShow:4, forceIntrinsicOrient:'landscape'});
    }else{
      renderEmptyZone(zels.success, null, null);
    }


    // Energy + UNDO/NEXT
    renderEnergy(zels.energy);

    // Live set (fixed 3 slots; cards do not shift when count changes)
    renderLiveSet(zels.liveset, Array.isArray(st.set_zone)?st.set_zone:[]);

    // Stage
    const stage = st.stage || {};
    renderStage(zels.stageL, 'L', stage.L);
    renderStage(zels.stageC, 'C', stage.C);
    renderStage(zels.stageR, 'R', stage.R);

    // Hand
    renderHand(zels.hand, Array.isArray(st.hand)?st.hand:[]);

    // Pending (choice) takes precedence; otherwise show resolve popup
    if(!maybeShowPending()){
      maybeShowResolvePopup();
    }
  }

  btnDbg.addEventListener('click', ()=>{ debug = !debug; render(); });
  elMask.addEventListener('click', (ev)=>{ if(popup && popup.type==='cardlist' && popup.closable){ closePopup(); } });

  // init
  cssScale();
  apiState().then(s=>{ st = s; updateTop(); render(); }).catch(err=>{
    console.error(err);
    alert('Failed to load /state. Is the server running?');
  });
})();
</script>
</body>
</html>'''
