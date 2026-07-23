# -*- coding: utf-8 -*-
# BUILD_TAG: manual_debug_move_stats_patch_20260723a
from __future__ import annotations

"""llocg_ui.server

Manual UI web server for LLCG.

Endpoints (kept compatible with the existing "jank" engine API):
- GET  /          : UI HTML
- GET  /public    : read-only public UI HTML
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

import base64
import copy
import datetime as _dt
import json
import time
import os
import pickle
import re
import threading
import random
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs, unquote

from .db import load_cards_db, is_member_type, is_live_type, _get_card as _db_get_card, _count_draw_icons
from .images import ImageLocator
from .views import make_view_state
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
    cmd_activate_from_hand,
    cmd_toggle_stage_active,
    cmd_resolve_pending,
    post_process,
    _get_card,
    _has_sacrifice_ability,
    can_activate_in_state,
    can_activate_from_hand_in_state,
    StageSlot,
    _slot_effective_cost,
    _card_effective_play_cost_from_hand,
    _success_zone_score_sum,
    _ordered_heart_counts,
    _rule_refresh_main_deck,
)

APP_VERSION = "reset_seed_record_flow_view_cache_20260723a"


def _write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding=encoding)


_YELL_HEART_TOKEN_TO_COLOR = {
    '桃': 'pink', '赤': 'red', '黄': 'yellow', '緑': 'green', '青': 'blue', '紫': 'purple',
    '任意': 'any', '無色': 'any', 'ALL': 'all', '虹': 'all', 'すべて': 'all',
}


def _parse_yell_heart_counts_from_raw(raw_text: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    txt = str(raw_text or '').strip()
    if not txt or txt in {'なし', '-', '0'}:
        return {}
    for m in re.finditer(r'<(?:\(([^)]+)\)|([^<>]+))>', txt):
        inner = str((m.group(1) or m.group(2) or '')).strip()
        key = inner.replace('＋', '+').replace(' ', '')
        m_colorless = re.match(r'^(?:無色|任意)[×xX](\d+)$', key)
        if m_colorless:
            try:
                counts['any'] = int(counts.get('any', 0) or 0) + max(0, int(m_colorless.group(1) or 0))
            except Exception:
                pass
            continue
        color = _YELL_HEART_TOKEN_TO_COLOR.get(key)
        if not color:
            continue
        counts[color] = int(counts.get(color, 0) or 0) + 1
    return _ordered_heart_counts(counts)


def _ci_yell_double_colorless_icon_count(ci: Optional[Any]) -> int:
    if not ci:
        return 0
    txt = str(getattr(ci, 'blade_heart_raw', '') or '')
    total = 0
    for m in re.finditer(r'<(?:\(([^)]+)\)|([^<>]+))>', txt):
        inner = str((m.group(1) or m.group(2) or '')).strip()
        key = inner.replace('＋', '+').replace(' ', '')
        mm = re.match(r'^(?:無色|任意)[×xX](\d+)$', key)
        if not mm:
            continue
        try:
            if int(mm.group(1) or 0) >= 2:
                total += 1
        except Exception:
            pass
    return int(total)


def _sum_named_icon_bonus_from_raw(raw_text: str, label: str) -> int:
    txt = str(raw_text or '').strip()
    if not txt or txt in {'なし', '-', '0'}:
        return 0
    total = 0
    for m in re.finditer(r'<(?:\(([^)]+)\)|([^<>]+))>', txt):
        inner = str((m.group(1) or m.group(2) or '')).strip()
        key = inner.replace('＋', '+').replace(' ', '')
        mm = re.match(r'^' + re.escape(label) + r'([+\-]\d+)$', key)
        if mm:
            try:
                total += int(mm.group(1))
            except Exception:
                pass
    return int(total)


def _ci_yell_heart_counts(ci: Optional[Any]) -> Dict[str, int]:
    if not ci:
        return {}
    return _parse_yell_heart_counts_from_raw(getattr(ci, 'blade_heart_raw', '') or '')


def _ci_yell_draw_icon_count(ci: Optional[Any]) -> int:
    if not ci:
        return 0
    tags = str(getattr(ci, 'blade_heart_tags_json', '') or '').strip()
    try:
        tag_n = int(_count_draw_icons(tags) or 0)
    except Exception:
        tag_n = 0
    try:
        raw_n = int(_sum_named_icon_bonus_from_raw(getattr(ci, 'blade_heart_raw', '') or '', 'ドロー') or 0)
    except Exception:
        raw_n = 0
    return max(int(tag_n or 0), int(raw_n or 0))


def _ci_yell_score_icon_count(ci: Optional[Any]) -> int:
    if not ci:
        return 0
    return _sum_named_icon_bonus_from_raw(getattr(ci, 'blade_heart_raw', '') or '', 'スコア')


def _ci_has_yell_blade_heart_payload(ci: Optional[Any]) -> bool:
    if not ci:
        return False
    if _ci_yell_heart_counts(ci):
        return True
    if _ci_yell_draw_icon_count(ci) or _ci_yell_score_icon_count(ci) or _ci_yell_double_colorless_icon_count(ci):
        return True
    txt = " ".join([
        str(getattr(ci, 'blade_heart_raw', '') or ''),
        str(getattr(ci, 'blade_heart_tags_json', '') or ''),
    ]).strip()
    if not txt or txt in {'なし', '-', '0', '[]'}:
        return False
    return bool(re.search(r'<(?:\([^)]+\)|[^<>]+)>', txt))


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
        self.deck_image_prefs = self._load_deck_image_prefs_from_env()
        self.ui_code = str(code)
        self.deck_code = str(deck_code)
        self.remote_mode = str(os.environ.get("LLOCG_APP_REMOTE_MODE", "") or "").strip().lower() not in ("", "0", "false", "no")
        self.remote_session_key = str(os.environ.get("LLOCG_APP_REMOTE_SESSION_KEY", "") or "")
        self.remote_session_uid = str(os.environ.get("LLOCG_APP_REMOTE_SESSION_UID", "") or "")
        self.gs, self.rng = new_game(self.root, self.deck_code, seed=seed, debug=debug)
        # BUILD_TAG: refresh_notice_popup_20260630af
        # Engine refresh notices need DB metadata for no-bladeheart/live summaries.
        try:
            setattr(self.gs, "_cards_db", self.cards_db)
        except Exception:
            pass
        self._force_mulligan_start()
        self._apply_start_overrides_from_env()
        self.card_instance_zones: Dict[str, List[str]] = {}
        self.card_instance_meta: Dict[str, Dict[str, str]] = {}
        self.card_instance_seq: int = 0
        self._init_card_instance_tracking()
        # Public-window reveal ledger.  This is intentionally independent from
        # gs.pending because owner-side acknowledgement can clear a reveal popup
        # before the public window's next poll sees it.
        self._public_reveal_events: List[Dict[str, Any]] = []
        self._public_reveal_seq: int = 0
        self._public_reveal_seen: Dict[str, float] = {}
        # Cards that became known while being added to hand remain public until
        # MAIN ends.  This is the public-window source of truth for
        # "private zone -> revealed -> hand" and "public zone -> hand" effects,
        # independent of transient owner-side popups.
        self._public_hand_revealed_turn: int = int(getattr(self.gs, "turn", 0) or 0)
        self._public_hand_revealed_cards: List[str] = []
        self._public_hand_revealed_instance_ids: List[str] = []
        self._public_hand_reveal_events: List[Dict[str, Any]] = []
        self._public_hand_reveal_seq: int = 0
        self._view_cache_lock = threading.RLock()
        self._view_cache_revision: int = 0
        self._view_cache_ttl_sec: float = 0.25
        self._poll_state_cache: Dict[str, Any] = {}
        self._view_bytes_cache: Dict[str, Dict[str, Any]] = {}
        self._apply_optional_extensions()
        self.save_trace()

    def _fresh_reset_seed(self) -> int:
        return int(time.time() * 1000) & 0x7FFFFFFF

    def _reshuffle_app_normal_match_from_env(self, seed: int) -> bool:
        if str(os.environ.get("LLOCG_APP_NORMAL_MATCH_SETUP", "") or "").strip().lower() in ("", "0", "false", "no"):
            return False
        raw = os.environ.get("LLOCG_APP_DECK_VARIANTS_JSON", "")
        try:
            variants = json.loads(raw) if raw else []
        except Exception:
            variants = []
        if not isinstance(variants, list):
            return False
        entries: List[Dict[str, str]] = []
        seq = 0
        for row in variants:
            if not isinstance(row, dict):
                continue
            cn = str(row.get("card_no") or row.get("cardnumber") or "").strip()
            if not cn:
                continue
            try:
                count = max(0, int(row.get("count", 0) or 0))
            except Exception:
                count = 0
            for _ in range(count):
                seq += 1
                entries.append({
                    "instance_id": f"dc{seq:03d}",
                    "cardnumber": cn,
                    "rarity": str(row.get("rarity", "") or ""),
                    "variant_id": str(row.get("variant_id", "") or ""),
                })
        if len(entries) != 60:
            return False
        rng = random.Random(int(seed or 0))
        rng.shuffle(entries)
        opening_entries = entries[:6]
        remaining_entries = entries[6:]
        try:
            self.gs.hand = [str(x.get("cardnumber") or "") for x in opening_entries]
            self.gs.deck = [str(x.get("cardnumber") or "") for x in remaining_entries]
            self.gs.phase = "MULLIGAN"
            self.gs.turn = 0
            self.gs.green_room = []
            self.gs.resolve_zone = []
            self.gs.set_zone = []
            self.gs.success_zone = []
            self.gs.energy_active = 0
            self.gs.energy_wait = 0
            self.gs.live_start_prompted = False
            self.gs.log.append(f"[RESET] normal match reshuffled from selected deck seed={seed}")
        except Exception:
            return False
        os.environ["LLOCG_APP_INITIAL_INSTANCES_JSON"] = json.dumps(
            {"hand": opening_entries, "deck": remaining_entries},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return True

    def reset_match(self) -> None:
        debug = bool(getattr(self.gs, "debug", False))
        new_seed = self._fresh_reset_seed()
        self.gs, self.rng = new_game(self.root, self.deck_code, seed=new_seed, debug=debug)
        try:
            setattr(self.gs, "_cards_db", self.cards_db)
        except Exception:
            pass
        self._force_mulligan_start()
        self._apply_start_overrides_from_env()
        self._reshuffle_app_normal_match_from_env(new_seed)
        self.card_instance_zones = {}
        self.card_instance_meta = {}
        self.card_instance_seq = 0
        self._init_card_instance_tracking()
        self._public_reveal_events = []
        self._public_reveal_seq = 0
        self._public_reveal_seen = {}
        self._public_hand_revealed_turn = int(getattr(self.gs, "turn", 0) or 0)
        self._public_hand_revealed_cards = []
        self._public_hand_revealed_instance_ids = []
        self._public_hand_reveal_events = []
        self._public_hand_reveal_seq = 0
        self._refresh_notice_ack_seq = 0
        self._apply_optional_extensions()
        try:
            self.gs.log.append(f"[RESET] new match seed={new_seed}")
        except Exception:
            pass
        self.save_trace()

    def _normalize_record_result(self, value: Any) -> str:
        raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "win": "win",
            "lose": "lose",
            "loss": "lose",
            "no": "no_game",
            "ng": "no_game",
            "nogame": "no_game",
            "no_game": "no_game",
            "draw": "no_game",
        }
        if raw not in aliases:
            raise ValueError("記録結果が不正です。")
        return aliases[raw]

    def _append_match_result_record(self, result: str) -> Dict[str, Any]:
        result = self._normalize_record_result(result)
        record = {
            "schema_version": 1,
            "recorded_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "simulator": "remote" if self.remote_mode else "single",
            "result": result,
            "deck_code": self.deck_code,
            "seed": int(getattr(self.gs, "seed", 0) or 0),
            "turn": int(getattr(self.gs, "turn", 0) or 0),
            "phase": str(getattr(self.gs, "phase", "") or ""),
            "remote_session_key": self.remote_session_key,
            "remote_session_uid": self.remote_session_uid,
            "build_tag": "match_record_reset_buttons_20260722a",
        }
        log_dir = self.root / "user_data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "loveca_match_results.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record

    def record_result_and_reset(self, result: Any) -> Dict[str, Any]:
        record = self._append_match_result_record(str(result or ""))
        self.reset_match()
        try:
            self.gs.log.append(f"[MATCH-RECORD] result={record['result']} saved=user_data/logs/loveca_match_results.jsonl")
        except Exception:
            pass
        self.save_trace()
        return record

    def record_result_only(self, result: Any) -> Dict[str, Any]:
        record = self._append_match_result_record(str(result or ""))
        try:
            self.gs.log.append(f"[MATCH-RECORD] result={record['result']} saved=user_data/logs/loveca_match_results.jsonl")
        except Exception:
            pass
        self.save_trace()
        return record

    def _normalize_image_rarity(self, value: Any) -> str:
        text = str(value or "").strip().upper()
        return text.replace("＋", "+").replace("+", "2")

    def _rarity_from_variant_id(self, variant_id: Any) -> str:
        parts = str(variant_id or "").split("|")
        if len(parts) >= 2:
            return parts[1]
        return ""

    def _load_deck_image_prefs_from_env(self) -> Dict[str, Dict[str, str]]:
        raw = os.environ.get("LLOCG_APP_DECK_VARIANTS_JSON", "")
        if not raw:
            return {}
        try:
            rows = json.loads(raw)
        except Exception:
            return {}
        if not isinstance(rows, list):
            return {}
        prefs: Dict[str, Dict[str, str]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            cn = str(row.get("card_no") or row.get("cardnumber") or "").strip()
            if not cn:
                continue
            variant_id = str(row.get("variant_id") or "").strip()
            rarity = str(row.get("rarity") or "").strip() or self._rarity_from_variant_id(variant_id)
            if not variant_id and not rarity:
                continue
            current = prefs.get(cn)
            # Prefer a row with an explicit variant id; otherwise keep the
            # first deck-list rarity for this card number.  Game state currently
            # stores card numbers, not per-copy variant ids.
            if current and (current.get("variant_id") or not variant_id):
                continue
            prefs[cn] = {
                "variant_id": variant_id,
                "rarity": self._normalize_image_rarity(rarity),
            }
        return prefs

    def _cn2image_rarity(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for cn in self._all_cardnumbers_in_state():
            pref = self.deck_image_prefs.get(cn, {})
            rarity = str(pref.get("rarity") or "").strip()
            if rarity:
                out[cn] = rarity
        return out

    def _cn2image_variant_id(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for cn in self._all_cardnumbers_in_state():
            pref = self.deck_image_prefs.get(cn, {})
            variant_id = str(pref.get("variant_id") or "").strip()
            if variant_id:
                out[cn] = variant_id
        return out

    def _normalize_instance_entry(self, row: Any, fallback_cn: str = "") -> Dict[str, str]:
        data = row if isinstance(row, dict) else {}
        cn = str(
            data.get("cardnumber")
            or data.get("card_no")
            or data.get("cn")
            or fallback_cn
            or ""
        ).strip()
        variant_id = str(data.get("variant_id") or "").strip()
        rarity = str(data.get("rarity") or "").strip() or self._rarity_from_variant_id(variant_id)
        return {
            "instance_id": str(data.get("instance_id") or "").strip(),
            "cardnumber": cn,
            "rarity": self._normalize_image_rarity(rarity),
            "variant_id": variant_id,
        }

    def _next_card_instance_id(self) -> str:
        self.card_instance_seq = int(getattr(self, "card_instance_seq", 0) or 0) + 1
        return f"ci{self.card_instance_seq:05d}"

    def _register_card_instance(self, row: Any, fallback_cn: str = "") -> str:
        item = self._normalize_instance_entry(row, fallback_cn=fallback_cn)
        cn = item.get("cardnumber", "")
        iid = item.get("instance_id", "") or self._next_card_instance_id()
        if iid in self.card_instance_meta:
            iid = self._next_card_instance_id()
        if not cn:
            cn = str(fallback_cn or "").strip()
        pref = self.deck_image_prefs.get(cn, {})
        rarity = item.get("rarity", "") or str(pref.get("rarity") or "")
        variant_id = item.get("variant_id", "") or str(pref.get("variant_id") or "")
        self.card_instance_meta[iid] = {
            "id": iid,
            "cardnumber": cn,
            "rarity": self._normalize_image_rarity(rarity),
            "variant_id": variant_id,
        }
        return iid

    def _load_initial_instance_rows(self) -> Dict[str, List[Dict[str, str]]]:
        raw = os.environ.get("LLOCG_APP_INITIAL_INSTANCES_JSON", "")
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except Exception:
            return {}
        if not isinstance(data, dict):
            return {}
        out: Dict[str, List[Dict[str, str]]] = {}
        for zone in ("hand", "deck"):
            rows = data.get(zone)
            if not isinstance(rows, list):
                continue
            out[zone] = [self._normalize_instance_entry(row) for row in rows if isinstance(row, dict)]
        return out

    def _fallback_instance_rows_by_cardnumber(self) -> Dict[str, List[Dict[str, str]]]:
        rows: Dict[str, List[Dict[str, str]]] = {}
        raw = os.environ.get("LLOCG_APP_DECK_VARIANTS_JSON", "")
        try:
            data = json.loads(raw) if raw else []
        except Exception:
            data = []
        if isinstance(data, list):
            for row in data:
                if not isinstance(row, dict):
                    continue
                cn = str(row.get("card_no") or row.get("cardnumber") or "").strip()
                if not cn:
                    continue
                try:
                    count = max(0, int(row.get("count", 0) or 0))
                except Exception:
                    count = 0
                item = self._normalize_instance_entry(row, fallback_cn=cn)
                for _ in range(count):
                    rows.setdefault(cn, []).append(dict(item))
        return rows

    def _zone_cardnumbers_for_instance_tracking(self) -> Dict[str, List[str]]:
        gs = self.gs
        zones: Dict[str, List[str]] = {
            "deck": [str(cn) for cn in list(getattr(gs, "deck", []) or [])],
            "hand": [str(cn) for cn in list(getattr(gs, "hand", []) or [])],
            "green_room": [str(cn) for cn in list(getattr(gs, "green_room", []) or [])],
            "set_zone": [str(cn) for cn in list(getattr(gs, "set_zone", []) or [])],
            "resolve_zone": [str(cn) for cn in list(getattr(gs, "resolve_zone", []) or [])],
            "success_zone": [str(cn) for cn in list(getattr(gs, "success_zone", []) or [])],
        }
        stage = getattr(gs, "stage", {}) or {}
        if isinstance(stage, dict):
            for pos in ("L", "C", "R"):
                slot = stage.get(pos)
                cn = ""
                if slot is not None:
                    cn = str(slot.get("cardnumber") if isinstance(slot, dict) else getattr(slot, "cardnumber", "") or "").strip()
                zones[f"stage:{pos}"] = [cn] if cn else []
        return zones

    def _make_unknown_card_instance(self, cn: str) -> str:
        return self._register_card_instance({"cardnumber": str(cn or "")}, fallback_cn=str(cn or ""))

    def _init_card_instance_tracking(self) -> None:
        self.card_instance_zones = {}
        self.card_instance_meta = {}
        self.card_instance_seq = 0
        current = self._zone_cardnumbers_for_instance_tracking()
        initial = self._load_initial_instance_rows()
        fallback_by_cn = self._fallback_instance_rows_by_cardnumber()

        for zone, cards in current.items():
            ids: List[str] = []
            explicit_rows = list(initial.get(zone, []) or [])
            for idx, cn in enumerate(cards):
                row = explicit_rows[idx] if idx < len(explicit_rows) else None
                if not row:
                    pool = fallback_by_cn.get(str(cn), [])
                    row = pool.pop(0) if pool else {"cardnumber": cn}
                ids.append(self._register_card_instance(row, fallback_cn=str(cn)))
            self.card_instance_zones[zone] = ids

    def _remove_instance_from_pool(self, pool: List[str], iid: str) -> None:
        try:
            pool.remove(iid)
        except ValueError:
            pass

    def _pop_matching_instance(self, pool: List[str], cn: str, used: set[str]) -> str:
        for iid in list(pool):
            if iid in used:
                continue
            meta = self.card_instance_meta.get(iid, {})
            if str(meta.get("cardnumber") or "") == str(cn):
                pool.remove(iid)
                return iid
        return ""

    def _sync_card_instances_from_state(self) -> None:
        if not isinstance(getattr(self, "card_instance_zones", None), dict):
            self._init_card_instance_tracking()
            return
        current = self._zone_cardnumbers_for_instance_tracking()
        old_zones = {zone: list(ids or []) for zone, ids in self.card_instance_zones.items()}
        global_pool: Dict[str, List[str]] = {}
        for ids in old_zones.values():
            for iid in ids:
                meta = self.card_instance_meta.get(iid, {})
                cn = str(meta.get("cardnumber") or "")
                if cn:
                    global_pool.setdefault(cn, []).append(iid)

        new_zones: Dict[str, List[str]] = {}
        used: set[str] = set()
        for zone, cards in current.items():
            same_pool = list(old_zones.get(zone, []) or [])
            ids: List[str] = []
            for cn in cards:
                cn_s = str(cn or "")
                iid = self._pop_matching_instance(same_pool, cn_s, used)
                if iid:
                    self._remove_instance_from_pool(global_pool.get(cn_s, []), iid)
                else:
                    pool = global_pool.get(cn_s, [])
                    iid = ""
                    while pool:
                        cand = pool.pop(0)
                        if cand not in used:
                            iid = cand
                            break
                if not iid:
                    iid = self._make_unknown_card_instance(cn_s)
                used.add(iid)
                ids.append(iid)
            new_zones[zone] = ids
        self.card_instance_zones = new_zones

    def _zone_instance_state_for_ui(self) -> Dict[str, Any]:
        self._sync_card_instances_from_state()
        stage = {
            pos: (list(self.card_instance_zones.get(f"stage:{pos}", []) or [None])[0])
            if self.card_instance_zones.get(f"stage:{pos}") else None
            for pos in ("L", "C", "R")
        }
        return {
            "deck": list(self.card_instance_zones.get("deck", []) or []),
            "hand": list(self.card_instance_zones.get("hand", []) or []),
            "green_room": list(self.card_instance_zones.get("green_room", []) or []),
            "set_zone": list(self.card_instance_zones.get("set_zone", []) or []),
            "resolve_zone": list(self.card_instance_zones.get("resolve_zone", []) or []),
            "success_zone": list(self.card_instance_zones.get("success_zone", []) or []),
            "stage": stage,
        }

    def _instance_meta_state_for_ui(self) -> Dict[str, Dict[str, str]]:
        self._sync_card_instances_from_state()
        active_ids: set[str] = set()
        for value in self._zone_instance_state_for_ui().values():
            if isinstance(value, list):
                active_ids.update(str(x) for x in value if x)
            elif isinstance(value, dict):
                active_ids.update(str(x) for x in value.values() if x)
        return {iid: dict(meta) for iid, meta in self.card_instance_meta.items() if iid in active_ids}

    def _apply_optional_extensions(self) -> None:
        """Load optional out-of-tree extensions.

        This hook is intentionally small: future ChatGPT/Codex changes should
        prefer adding files under ``llocg_ext/`` and registering behavior via
        ``llocg_ext.apply_extensions(app)`` rather than replacing core files.
        Extension failures are logged but do not prevent the base UI from
        starting.
        """
        try:
            from llocg_ext import apply_extensions  # type: ignore
        except Exception as e:
            try:
                print(f"[EXT] no external extension loaded: {e}")
            except Exception:
                pass
            return
        try:
            apply_extensions(self)
            try:
                self.gs.log.append("[EXT] loaded llocg_ext extensions")
            except Exception:
                pass
        except Exception as e:
            try:
                print(f"[EXT][ERR] extension load failed: {e}")
                self.gs.log.append(f"[EXT][ERR] extension load failed: {e}")
            except Exception:
                pass

    def _public_reveal_event_from_pending_item(self, item: Any, reason: str = "") -> Optional[Dict[str, Any]]:
        if not isinstance(item, dict):
            return None
        kind = str(item.get("kind", "") or item.get("type", "") or "")
        if kind != "show_revealed_cards_ack":
            return None
        cards: List[str] = []
        for key in ("display_cards", "shown", "revealed_cards", "cards", "candidates"):
            val = item.get(key)
            if isinstance(val, list):
                for cn in val:
                    cn_s = str(cn or "").strip()
                    if cn_s and cn_s not in cards:
                        cards.append(cn_s)
        # Even an empty reveal ack is useful as a public note, but cards are the
        # part that must persist after owner-side popup dismissal.
        text = str(item.get("text", "") or item.get("message", "") or item.get("prompt", "") or "公開カードを確認しました。")
        return {
            "kind": "public_reveal_event",
            "source_kind": kind,
            "title": "公開カード",
            "text": text,
            "display_cards": cards,
            "display_card_count": len(cards),
            "reason": str(reason or ""),
        }

    def _remember_public_reveals_from_pending(self, reason: str = "") -> None:
        now = time.time()
        # Prune old seen keys and expired events first.
        self._public_reveal_seen = {k: t for k, t in getattr(self, "_public_reveal_seen", {}).items() if now - float(t or 0) <= 30.0}
        self._public_reveal_events = [ev for ev in getattr(self, "_public_reveal_events", []) if float(ev.get("expires_at", 0.0) or 0.0) > now]
        try:
            pending = list(getattr(self.gs, "pending", []) or [])
        except Exception:
            pending = []
        for item in pending:
            ev = self._public_reveal_event_from_pending_item(item, reason)
            if not ev:
                continue
            key = json.dumps({"text": ev.get("text", ""), "cards": ev.get("display_cards", [])}, ensure_ascii=False, sort_keys=True)
            if key in self._public_reveal_seen:
                # Refresh expiry rather than duplicating.
                for old_ev in self._public_reveal_events:
                    old_key = json.dumps({"text": old_ev.get("text", ""), "cards": old_ev.get("display_cards", [])}, ensure_ascii=False, sort_keys=True)
                    if old_key == key:
                        old_ev["expires_at"] = now + 10.0
                continue
            self._public_reveal_seen[key] = now
            self._public_reveal_seq += 1
            ev["seq"] = self._public_reveal_seq
            ev["created_at"] = now
            ev["expires_at"] = now + 10.0
            self._public_reveal_events.append(ev)

    def _public_reveal_events_snapshot(self) -> List[Dict[str, Any]]:
        now = time.time()
        self._public_reveal_events = [ev for ev in getattr(self, "_public_reveal_events", []) if float(ev.get("expires_at", 0.0) or 0.0) > now]
        return [dict(ev) for ev in self._public_reveal_events]

    def _current_turn_int(self) -> int:
        try:
            return int(getattr(self.gs, "turn", 0) or 0)
        except Exception:
            return 0

    def _sync_public_hand_reveals_turn(self) -> None:
        """Clear public-in-hand reveal state as soon as its legal window ends.

        These cards are public only while they remain relevant to main-phase
        private-zone lookup effects.  Keeping them public until turn change leaks
        whether a revealed hand card was set face-down as a live card.  Therefore
        clear the ledger immediately after leaving MAIN, and also on turn change.
        """
        cur_turn = self._current_turn_int()
        try:
            phase = str(getattr(self.gs, "phase", "") or "").upper()
        except Exception:
            phase = ""
        turn_changed = int(getattr(self, "_public_hand_revealed_turn", cur_turn) or 0) != cur_turn
        phase_closed = phase != "MAIN"
        if turn_changed or phase_closed:
            self._public_hand_revealed_turn = cur_turn
            self._public_hand_revealed_cards = []
            self._public_hand_revealed_instance_ids = []
            self._public_hand_reveal_events = []

    def _live_set_cards_are_public_for_public_source(self) -> bool:
        """Mirror public-view live set visibility for source-count tracking."""
        try:
            phase = str(getattr(self.gs, "phase", "") or "").upper()
        except Exception:
            phase = ""
        if phase in {"LIVE_PERF", "LIVE_ATTEMPT", "LIVE_RESOLVE"}:
            return True
        if phase == "LIVE_CONFIRM" and bool(getattr(self.gs, "live_start_prompted", False)):
            return True
        return False

    def _public_source_counts_for_hand_reveal(self) -> Dict[str, int]:
        """Count cards that are publicly known and can later move to hand.

        This is intentionally about *source visibility*, not about all cards the
        owner can see.  It is used with hand-count deltas after a command:
        if a card's count in public sources decreases and its count in hand
        increases, the public window keeps that card face-up in hand until MAIN
        ends.
        """
        counts: Dict[str, int] = {}

        def add_cn(cn0: Any) -> None:
            cn = str(cn0 or "").strip()
            if cn and cn != "__BACK__":
                counts[cn] = counts.get(cn, 0) + 1

        def add_list(v: Any) -> None:
            if isinstance(v, list):
                for cn0 in v:
                    add_cn(cn0)

        # Public zones in the current simulator surface.
        add_list(getattr(self.gs, "green_room", None))
        add_list(getattr(self.gs, "resolve_zone", None))
        add_list(getattr(self.gs, "success_zone", None))
        if self._live_set_cards_are_public_for_public_source():
            add_list(getattr(self.gs, "set_zone", None))

        stage = getattr(self.gs, "stage", None)
        try:
            items = stage.items() if isinstance(stage, dict) else []
        except Exception:
            items = []
        for _pos, slot in items:
            try:
                cn = slot.get("cardnumber") if isinstance(slot, dict) else getattr(slot, "cardnumber", "")
            except Exception:
                cn = ""
            add_cn(cn)

        # Explicit reveal acknowledgements are public even if the revealed cards
        # are not yet in a normal public zone.  This covers effects whose owner
        # popup is acknowledged immediately.
        try:
            pending = list(getattr(self.gs, "pending", []) or [])
        except Exception:
            pending = []
        for item in pending:
            if not isinstance(item, dict):
                continue
            kind = str(item.get("kind", "") or item.get("type", "") or "")
            if kind != "show_revealed_cards_ack":
                continue
            for key in ("display_cards", "shown", "revealed_cards", "cards", "candidates"):
                add_list(item.get(key))

        return counts

    def _reveal_candidate_cards_from_pending(self) -> List[str]:
        """Return card numbers that may become public if added to hand.

        Public-window rule used here:
        - Explicit reveal ACKs are public.
        - For private-zone lookup effects, do NOT reveal the whole pool.
          If the pending text/effect text says a card is revealed/publicly shown
          and added to hand, keep only the card that actually reaches hand public
          until MAIN ends.

        Main regression target: PL!-bp6-002.  Its pending is
        ``choose_from_topk`` rather than ``show_revealed_cards_ack``; the chosen
        matching card must become public after resolve_pending adds it to hand.
        """
        out: List[str] = []

        def _add_cards(val: Any) -> None:
            if not isinstance(val, list):
                return
            for cn0 in val:
                cn = str(cn0 or "").strip()
                if cn and cn not in out:
                    out.append(cn)

        try:
            pending = list(getattr(self.gs, "pending", []) or [])
        except Exception:
            pending = []

        for item in pending:
            if not isinstance(item, dict):
                continue
            kind = str(item.get("kind", "") or item.get("type", "") or "")

            if kind == "show_revealed_cards_ack":
                for key in ("display_cards", "shown", "revealed_cards", "cards", "candidates"):
                    _add_cards(item.get(key))
                continue

            # Private-zone lookup -> hand effects.  Do not reveal the whole
            # owner-only pool.  We keep only the selected card public after it
            # actually reaches hand.
            #
            # Important: filtered top-k effects generated by the engine do not
            # necessarily contain the word "公開" in pending.text.  Example
            # PL!-bp6-002 currently produces:
            #   kind=choose_from_topk
            #   text="デッキ上2枚から『μ's』・能力なし/常時能力ありを1枚手札へ..."
            #   candidates=[...]
            # The presence of candidates means the owner is choosing from a
            # condition-checked subset.  The chosen card needs to be public so
            # the public window can verify the condition, but the unchosen pool
            # stays private.
            public_text = "\n".join([
                str(item.get("text", "") or ""),
                str(item.get("effect_text", "") or ""),
                str(item.get("detail_text", "") or ""),
            ])

            if kind == "choose_from_topk":
                # BUILD_TAG: public_hand_reveal_strict_metadata_20260701an
                # A private top-deck lookup may expose candidates to the owner
                # without making them public.  Do not treat mere candidates as a
                # public reveal.  Only explicit metadata, or effect text that says
                # the selected card is revealed/public and added to hand, can keep
                # the selected card face-up in the public hand row.
                explicit_metadata = any(bool(item.get(k)) for k in (
                    "public_reveal_selected_to_hand",
                    "public_reveal_to_hand",
                    "reveal_selected_to_public_hand",
                ))
                explicit_public_to_hand = ("公開" in public_text and "手札" in public_text)
                if not (explicit_metadata or explicit_public_to_hand):
                    continue
                _add_cards(item.get("candidates"))
                if not out:
                    opts = item.get("options")
                    if isinstance(opts, list):
                        _add_cards([x for x in opts if str(x).strip().lower() not in {"skip", "__skip__", "スキップ"}])
                continue

            if kind == "look_top_3way_step":
                # 3-way look effects are not necessarily public.  Keep the
                # stricter explicit-text rule here until a dedicated metadata
                # flag is added at pending generation time.
                if not ("公開" in public_text and "手札" in public_text):
                    continue
                _add_cards(item.get("candidates"))
                if not out:
                    opts = item.get("options")
                    if isinstance(opts, list):
                        _add_cards([x for x in opts if str(x).strip().lower() not in {"skip", "__skip__", "スキップ"}])
                continue

        return out

    def _remember_public_hand_reveals_after_cmd(
        self,
        before_hand: List[str],
        reveal_candidates: List[str],
        reason: str = "",
        before_refresh_seq: int = 0,
        before_hand_instance_ids: Optional[List[str]] = None,
    ) -> None:
        """Keep known cards that reached hand public until MAIN ends.

        Cases covered:
        - private-zone lookup effects that reveal/condition-check selected card(s)
          before adding them to hand;
        - cards moved from public zones such as green room/resolve/success to hand.

        The owner-side popup can close immediately, so the public window needs a
        short scoped ledger independent from pending.
        """
        self._sync_public_hand_reveals_turn()
        try:
            phase = str(getattr(self.gs, "phase", "") or "").upper()
        except Exception:
            phase = ""
        if phase != "MAIN":
            return
        try:
            after_hand = [str(cn) for cn in list(getattr(self.gs, "hand", []) or [])]
        except Exception:
            after_hand = []
        before_counts: Dict[str, int] = {}
        for cn in before_hand or []:
            before_counts[str(cn)] = before_counts.get(str(cn), 0) + 1
        added: List[str] = []
        added_ids: List[str] = []
        before_iids = set(str(x) for x in list(before_hand_instance_ids or []) if str(x or "").strip())
        try:
            self._sync_card_instances_from_state()
            after_hand_iids = [str(x or "") for x in list(self.card_instance_zones.get("hand", []) or [])]
        except Exception:
            after_hand_iids = []
        used_iids = set(str(x) for x in list(getattr(self, "_public_hand_revealed_instance_ids", []) or []) if str(x or "").strip())

        def find_added_instance_id(cn: str) -> str:
            for idx, hand_cn in enumerate(after_hand):
                if hand_cn != cn or idx >= len(after_hand_iids):
                    continue
                iid = str(after_hand_iids[idx] or "")
                if iid and iid not in before_iids and iid not in used_iids:
                    return iid
            for idx, hand_cn in enumerate(after_hand):
                if hand_cn != cn or idx >= len(after_hand_iids):
                    continue
                iid = str(after_hand_iids[idx] or "")
                if iid and iid not in used_iids:
                    return iid
            return ""

        def add_if_hand_increased(cn0: Any) -> None:
            cn = str(cn0 or "").strip()
            if not cn or cn == "__BACK__":
                return
            after_n = sum(1 for x in after_hand if x == cn)
            before_n = int(before_counts.get(cn, 0) or 0)
            already_added_n = sum(1 for x in added if x == cn)
            if after_n > before_n + already_added_n:
                added.append(cn)
                iid = find_added_instance_id(cn)
                if iid:
                    added_ids.append(iid)
                    used_iids.add(iid)

        for cn in reveal_candidates or []:
            # Mark only cards that are in hand after resolution and whose count
            # in hand increased.  This avoids keeping merely-viewed/bottomed cards
            # public and avoids ordinary non-reveal draws.
            add_if_hand_increased(cn)

        # Generic public-zone -> hand rule.  If a card was in a public source
        # before the command, that public-source count decreased, and the same
        # card's hand count increased, keep it visible in the public hand row
        # until MAIN ends.
        #
        # BUILD_TAG: public_hand_reveal_skip_refresh_source_loss_20260701an
        # Refresh moves the public green room into a hidden deck.  If the same
        # command then draws a card with the same card number, that is not a
        # direct public-zone -> hand move and must not become public in hand.
        try:
            after_refresh_seq = int(getattr(self.gs, "refresh_notice_seq", 0) or 0)
        except Exception:
            after_refresh_seq = 0
        refresh_happened_during_cmd = bool(before_refresh_seq and after_refresh_seq > int(before_refresh_seq or 0))
        before_src: Dict[str, int] = {} if refresh_happened_during_cmd else (getattr(self, "_public_hand_before_source_counts", {}) or {})
        after_src = self._public_source_counts_for_hand_reveal()
        for cn, before_src_n in before_src.items():
            try:
                bsn = int(before_src_n or 0)
            except Exception:
                bsn = 0
            if bsn <= 0:
                continue
            asn = int(after_src.get(cn, 0) or 0)
            if asn < bsn:
                add_if_hand_increased(cn)

        if not added:
            return
        cards = list(getattr(self, "_public_hand_revealed_cards", []) or [])
        for cn in added:
            cards.append(cn)
        self._public_hand_revealed_cards = cards
        if added_ids:
            ids = list(getattr(self, "_public_hand_revealed_instance_ids", []) or [])
            for iid in added_ids:
                if iid not in ids:
                    ids.append(iid)
            self._public_hand_revealed_instance_ids = ids
        self._public_hand_reveal_seq += 1
        ev = {
            "kind": "public_hand_reveal",
            "title": "公開して手札に加えたカード",
            "text": "公開情報として手札に加わったカードです。メインフェイズ終了まで公開情報として扱います。",
            "display_cards": added,
            "display_instance_ids": added_ids,
            "display_card_count": len(added),
            "turn": self._current_turn_int(),
            "seq": self._public_hand_reveal_seq,
            "created_at": time.time(),
            "reason": str(reason or ""),
        }
        self._public_hand_reveal_events.append(ev)
        # Keep the short animation ledger small; the persistent public cards are
        # stored separately in _public_hand_revealed_cards.
        self._public_hand_reveal_events = self._public_hand_reveal_events[-8:]
        try:
            self.gs.log.append(f"[PUBLIC_REVEAL] hand public until MAIN end: {', '.join(added)}")
        except Exception:
            pass

    def _public_hand_revealed_cards_snapshot(self) -> List[str]:
        self._sync_public_hand_reveals_turn()
        ids = self._public_hand_revealed_instance_ids_snapshot()
        if ids:
            cards: List[str] = []
            for iid in ids:
                meta = self.card_instance_meta.get(str(iid), {}) if isinstance(getattr(self, "card_instance_meta", None), dict) else {}
                cn = str(meta.get("cardnumber") or "")
                if cn:
                    cards.append(cn)
            self._public_hand_revealed_cards = cards
            return list(cards)
        hand = [str(cn) for cn in list(getattr(self.gs, "hand", []) or [])]
        cards: List[str] = []
        for cn in list(getattr(self, "_public_hand_revealed_cards", []) or []):
            if cn in hand:
                cards.append(cn)
        self._public_hand_revealed_cards = cards
        return list(cards)

    def _public_hand_revealed_instance_ids_snapshot(self) -> List[str]:
        self._sync_public_hand_reveals_turn()
        try:
            self._sync_card_instances_from_state()
            hand_ids = set(str(x) for x in list(self.card_instance_zones.get("hand", []) or []) if str(x or "").strip())
        except Exception:
            hand_ids = set()
        ids: List[str] = []
        for iid0 in list(getattr(self, "_public_hand_revealed_instance_ids", []) or []):
            iid = str(iid0 or "").strip()
            if iid and iid in hand_ids and iid not in ids:
                ids.append(iid)
        self._public_hand_revealed_instance_ids = ids
        return list(ids)

    def _card_intrinsic_orient_for_public(self, cn: str) -> str:
        """Return UI intrinsic orientation for a known public hand card.

        Public hand rendering cannot always rely on ``cn2type`` surviving view
        redaction at the exact repaint timing.  Compute the orientation on the
        server side from the DB and expose it only for cards already registered
        as public-in-hand.  LIVE cards should be rotated in the portrait hand
        row just like they are in the owner hand.
        """
        try:
            ci = _get_card(self.cards_db, str(cn or ""))
            typ = str(getattr(ci, "type", "") or "").upper() if ci else ""
            if "LIVE" in typ:
                return "landscape"
            score = int(getattr(ci, "score", 0) or 0) if ci else 0
            if score > 0:
                return "landscape"
        except Exception:
            pass
        return "portrait"

    def _public_hand_revealed_orient_snapshot(self) -> Dict[str, str]:
        return {cn: self._card_intrinsic_orient_for_public(cn) for cn in self._public_hand_revealed_cards_snapshot()}

    def _public_hand_reveal_events_snapshot(self) -> List[Dict[str, Any]]:
        self._sync_public_hand_reveals_turn()
        cur_turn = self._current_turn_int()
        events = []
        now = time.time()
        for ev in list(getattr(self, "_public_hand_reveal_events", []) or []):
            if int(ev.get("turn", cur_turn) or cur_turn) == cur_turn and now - float(ev.get("created_at", 0.0) or 0.0) <= 20.0:
                events.append(dict(ev))
        self._public_hand_reveal_events = events
        return [dict(ev) for ev in events]

    def _ack_refresh_notice(self, seq: int) -> None:
        """Acknowledge refresh notices for synchronized owner/public UI only."""
        # BUILD_TAG: refresh_notice_owner_public_ack_and_deck_empty_check_20260701ap
        try:
            seq_i = int(seq or 0)
        except Exception:
            seq_i = 0
        if seq_i <= 0:
            return
        try:
            cur = int(getattr(self, "_refresh_notice_ack_seq", 0) or 0)
        except Exception:
            cur = 0
        try:
            self._refresh_notice_ack_seq = max(cur, seq_i)
        except Exception:
            pass
        # BUILD_TAG: refresh_notice_undo_owner_resync_20260701aq
        # Do not remove notices from the GameState ledger on acknowledgement.
        # The owner/public UI suppresses acknowledged notices via ack seq.  Keeping
        # the ledger intact lets undo restore and replay the same notice correctly.

    def _latest_unacked_refresh_notice_seq(self) -> int:
        try:
            notices = [x for x in (getattr(self.gs, "refresh_notices", []) or []) if isinstance(x, dict)]
        except Exception:
            notices = []
        latest = 0
        for ev in notices:
            try:
                latest = max(latest, int(ev.get("seq", 0) or 0))
            except Exception:
                pass
        try:
            ack = int(getattr(self, "_refresh_notice_ack_seq", 0) or 0)
        except Exception:
            ack = 0
        return latest if latest > ack else 0

    def _auto_refresh_if_deck_empty_after_cmd(self, reason: str = "post_cmd") -> None:
        """Apply the rule refresh immediately when command resolution empties the deck."""
        # BUILD_TAG: refresh_notice_owner_public_ack_and_deck_empty_check_20260701ap
        try:
            deck_empty = len(list(getattr(self.gs, "deck", []) or [])) == 0
            has_green = len(list(getattr(self.gs, "green_room", []) or [])) > 0
        except Exception:
            deck_empty = False
            has_green = False
        if not (deck_empty and has_green):
            return
        try:
            _rule_refresh_main_deck(self.gs, self.rng, reason=reason)
        except Exception as e:
            try:
                self.gs.log.append(f"[WARN] post-command refresh failed: {e}")
            except Exception:
                pass

    def save_trace(self) -> None:
        self._invalidate_view_cache()
        self.outdir.mkdir(parents=True, exist_ok=True)
        _write_text(self.outdir / "ui_trace.txt", "\n".join(self.gs.log) + ("\n" if self.gs.log else ""))

    def _invalidate_view_cache(self) -> None:
        try:
            lock = getattr(self, "_view_cache_lock", None)
            if lock is None:
                return
            with lock:
                self._view_cache_revision = int(getattr(self, "_view_cache_revision", 0) or 0) + 1
                self._poll_state_cache = {}
                self._view_bytes_cache = {}
        except Exception:
            pass

    def view_state_bytes(self, mode: str = "private") -> bytes:
        """Return serialized view state, sharing short-lived polling work.

        The owner and public windows poll the same simulator.  Building the full
        state and then redacting it for the public view is expensive, so GET
        requests share a tiny cache.  Mutating commands call save_trace(), which
        invalidates this cache before their fresh response is built.
        """
        view_mode = str(mode or "private").strip().lower() or "private"
        if view_mode in {"share", "shared"}:
            view_mode = "public"
        now = time.time()
        ttl = float(getattr(self, "_view_cache_ttl_sec", 0.25) or 0.25)
        with self._view_cache_lock:
            rev = int(getattr(self, "_view_cache_revision", 0) or 0)
            cached = self._view_bytes_cache.get(view_mode)
            if (
                isinstance(cached, dict)
                and int(cached.get("revision", -1)) == rev
                and now - float(cached.get("ts", 0.0) or 0.0) <= ttl
            ):
                data = cached.get("data")
                if isinstance(data, (bytes, bytearray)):
                    return bytes(data)

            base_entry = self._poll_state_cache
            base_state = None
            if (
                isinstance(base_entry, dict)
                and int(base_entry.get("revision", -1)) == rev
                and now - float(base_entry.get("ts", 0.0) or 0.0) <= ttl
            ):
                candidate = base_entry.get("state")
                if isinstance(candidate, dict):
                    base_state = candidate
            if base_state is None:
                base_state = self.state_json()
                self._poll_state_cache = {"revision": rev, "ts": now, "state": base_state}

            data = json.dumps(make_view_state(base_state, view_mode), ensure_ascii=False).encode("utf-8")
            self._view_bytes_cache[view_mode] = {"revision": rev, "ts": now, "data": data}
            return data

    def _capture_suspend_snapshot(self) -> Dict[str, Any]:
        return {
            "gs": copy.deepcopy(self.gs),
            "rng_state": self.rng.getstate(),
            "app_state": {
                "public_reveal_events": copy.deepcopy(self._public_reveal_events),
                "public_reveal_seq": int(self._public_reveal_seq or 0),
                "public_reveal_seen": copy.deepcopy(self._public_reveal_seen),
                "public_hand_revealed_turn": int(self._public_hand_revealed_turn or 0),
                "public_hand_revealed_cards": copy.deepcopy(self._public_hand_revealed_cards),
                "public_hand_revealed_instance_ids": copy.deepcopy(getattr(self, "_public_hand_revealed_instance_ids", []) or []),
                "public_hand_reveal_events": copy.deepcopy(self._public_hand_reveal_events),
                "public_hand_reveal_seq": int(self._public_hand_reveal_seq or 0),
                "refresh_notice_ack_seq": int(getattr(self, "_refresh_notice_ack_seq", 0) or 0),
                "card_instance_zones": copy.deepcopy(getattr(self, "card_instance_zones", {}) or {}),
                "card_instance_meta": copy.deepcopy(getattr(self, "card_instance_meta", {}) or {}),
                "card_instance_seq": int(getattr(self, "card_instance_seq", 0) or 0),
            },
        }

    def _restore_suspend_snapshot(self, snap: Dict[str, Any]) -> None:
        self.gs = copy.deepcopy(snap["gs"])
        try:
            setattr(self.gs, "_cards_db", self.cards_db)
        except Exception:
            pass
        self.rng.setstate(snap["rng_state"])
        app_state = dict(snap.get("app_state", {}) or {})
        self._public_reveal_events = list(app_state.get("public_reveal_events", []) or [])
        self._public_reveal_seq = int(app_state.get("public_reveal_seq", 0) or 0)
        self._public_reveal_seen = dict(app_state.get("public_reveal_seen", {}) or {})
        self._public_hand_revealed_turn = int(app_state.get("public_hand_revealed_turn", 0) or 0)
        self._public_hand_revealed_cards = list(app_state.get("public_hand_revealed_cards", []) or [])
        self._public_hand_revealed_instance_ids = list(app_state.get("public_hand_revealed_instance_ids", []) or [])
        self._public_hand_reveal_events = list(app_state.get("public_hand_reveal_events", []) or [])
        self._public_hand_reveal_seq = int(app_state.get("public_hand_reveal_seq", 0) or 0)
        self._refresh_notice_ack_seq = int(app_state.get("refresh_notice_ack_seq", 0) or 0)
        self.card_instance_zones = copy.deepcopy(app_state.get("card_instance_zones", {}) or {})
        self.card_instance_meta = copy.deepcopy(app_state.get("card_instance_meta", {}) or {})
        self.card_instance_seq = int(app_state.get("card_instance_seq", 0) or 0)
        if not self.card_instance_zones:
            self._init_card_instance_tracking()

    def export_suspend_data(self, label: str = "") -> Dict[str, Any]:
        state = self.state_json()
        payload = base64.b64encode(
            pickle.dumps(self._capture_suspend_snapshot(), protocol=pickle.HIGHEST_PROTOCOL)
        ).decode("ascii")
        return {
            "format": "llocg_ui_suspend_state",
            "format_version": 1,
                "build_tag": "match_record_reset_buttons_20260722a",
            "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "label": str(label or ""),
            "summary": {
                "turn": state.get("turn"),
                "phase": state.get("phase"),
                "deck_code": state.get("deck_code"),
                "hand_count": len(list(state.get("hand", []) or [])),
                "deck_count": len(list(state.get("deck", []) or [])),
                "success_zone": list(state.get("success_zone", []) or []),
                "set_zone": list(state.get("set_zone", []) or []),
            },
            "log": list(state.get("log", []) or []),
            "snapshot_b64": payload,
        }

    def import_suspend_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("中断データの形式が不正です")
        if data.get("format") != "llocg_ui_suspend_state":
            raise ValueError("1デッキ用シミュレーターの中断データではありません")
        raw = str(data.get("snapshot_b64", "") or "")
        if not raw:
            raise ValueError("中断データに復元用スナップショットがありません")
        try:
            snap = pickle.loads(base64.b64decode(raw.encode("ascii"), validate=True))
        except Exception as exc:
            raise ValueError(f"中断データを読み込めません: {exc}") from exc
        self._restore_suspend_snapshot(snap)
        try:
            self.gs.undo_stack = []
        except Exception:
            pass
        try:
            self.gs.log.append(
                f"[RESUME] 中断データから再開 label={str(data.get('label', '') or '')}"
            )
        except Exception:
            pass
        self.save_trace()
        return self.state_json()


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

    def _push_undo_with_app_state(self) -> None:
        push_undo(self.gs, self.rng)
        try:
            if self.gs.undo_stack:
                self.gs.undo_stack[-1]["app_state"] = {
                    "refresh_notice_ack_seq": int(getattr(self, "_refresh_notice_ack_seq", 0) or 0),
                }
        except Exception:
            pass

    def _do_undo_with_app_state(self) -> None:
        app_state: Dict[str, Any] = {}
        try:
            if self.gs.undo_stack:
                app_state = dict(self.gs.undo_stack[-1].get("app_state") or {})
        except Exception:
            app_state = {}
        do_undo(self.gs, self.rng)
        if "refresh_notice_ack_seq" in app_state:
            try:
                self._refresh_notice_ack_seq = int(app_state.get("refresh_notice_ack_seq", 0) or 0)
                return
            except Exception:
                pass
        try:
            cur_seq = int(getattr(self.gs, "refresh_notice_seq", 0) or 0)
            cur_ack = int(getattr(self, "_refresh_notice_ack_seq", 0) or 0)
            self._refresh_notice_ack_seq = max(0, min(cur_ack, cur_seq))
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
        opponent_wait_s = (env.get('LLOCG_START_OPPONENT_WAIT') or '').strip()
        opponent_success_s = (env.get('LLOCG_START_OPPONENT_SUCCESS') or '').strip()
        opponent_success_score_s = (env.get('LLOCG_START_OPPONENT_SUCCESS_SCORE') or env.get('LLOCG_START_OPPONENT_SUCCESS_SCORE_SUM') or '').strip()
        opponent_excess_s = (env.get('LLOCG_START_OPPONENT_EXCESS') or env.get('LLOCG_START_OPPONENT_EXCESS_HEARTS') or '').strip()
        turn_order_s = (env.get('LLOCG_START_TURN_ORDER') or '').strip()
        turn_s = (env.get('LLOCG_START_TURN') or '').strip()
        phase_s = (env.get('LLOCG_START_PHASE') or '').strip()
        hand_size_s = (env.get('LLOCG_START_HAND_SIZE') or '').strip()
        shuffle_s = (env.get('LLOCG_START_SHUFFLE') or '').strip()
        debug_s = (env.get('LLOCG_START_DEBUG') or '').strip()
        stage_moved_s = (env.get('LLOCG_START_STAGE_MOVED_THIS_TURN') or '').strip()
        stage_moved_cards_s = (env.get('LLOCG_START_STAGE_MOVED_CARDS') or env.get('LLOCG_START_STAGE_MOVED_CARDNUMBERS') or '').strip()

        # Optional richer injections for faster effect testing
        green_spec = (env.get('LLOCG_START_GREEN') or '').strip()        # waiting room
        success_spec = (env.get('LLOCG_START_SUCCESS') or '').strip()    # success live storage
        decktop_spec = (env.get('LLOCG_START_DECK_TOP') or '').strip()   # put these on top of deck (leftmost = top)
        # BUILD_TAG: debug_start_empty_deck_exact_and_energy_cap_20260701ai
        # Treat an explicitly present empty LLOCG_START_DECK_EXACT as an exact empty deck.
        # Also support a non-empty sentinel/flag because some shells and launchers make
        # empty-string env debugging ambiguous.
        deckempty_s = (env.get('LLOCG_START_DECK_EMPTY') or '').strip()
        deckexact_present = ('LLOCG_START_DECK_EXACT' in env) or (deckempty_s in ('1','true','TRUE','yes','YES'))
        deckexact_spec = (env.get('LLOCG_START_DECK_EXACT') or '').strip() # replace deck exactly (leftmost = top)
        if deckempty_s in ('1','true','TRUE','yes','YES') or deckexact_spec.upper() in ('__EMPTY__','EMPTY','NONE','NULL'):
            deckexact_spec = ''
            deckexact_present = True
        deckexact_strict_s = (env.get('LLOCG_START_DECK_EXACT_STRICT') or env.get('LLOCG_START_DECK_EXACT_DROP_REST') or '').strip()
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
            hand_spec, e_active_s, e_wait_s, opponent_wait_s, opponent_success_s, opponent_success_score_s, opponent_excess_s, turn_order_s, turn_s, phase_s, hand_size_s, shuffle_s, debug_s,
            green_spec, decktop_spec, deckexact_present, deckexact_spec, deckexact_strict_s, deckempty_s, resolve_spec,
            stage_spec, stage_l, stage_c, stage_r, stage_moved_s, stage_moved_cards_s,
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

            # Debug energy cap (default 99) and starting energy.
            # BUILD_TAG: debug_start_empty_deck_exact_and_energy_cap_20260630ag_rebased0630
            if not debug_energy_cap_s:
                debug_energy_cap_s = '99'
            try:
                cap_v = _as_int(debug_energy_cap_s, 0)
                if cap_v > 0:
                    gs.energy_total = cap_v
            except Exception:
                pass
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

        # Opponent manual counters / turn-order overrides (debug/manual state seed)
        if opponent_wait_s:
            try:
                ow = max(0, min(3, _as_int(opponent_wait_s, 0)))
                gs.opponent_wait_count = ow
                gs.log.append(f'[DEBUG_START] opponent_wait_count={ow}')
            except Exception:
                pass
        if opponent_success_s:
            try:
                osn = max(0, min(2, _as_int(opponent_success_s, 0)))
                gs.opponent_success_count = osn
                gs.log.append(f'[DEBUG_START] opponent_success_count={osn}')
            except Exception:
                pass
        if opponent_success_score_s:
            try:
                oss = max(0, min(20, _as_int(opponent_success_score_s, 0)))
                gs.opponent_success_score_sum = oss
                gs.log.append(f'[DEBUG_START] opponent_success_score_sum={oss}')
            except Exception:
                pass
        if opponent_excess_s:
            try:
                oex = max(0, min(9, _as_int(opponent_excess_s, 0)))
                gs.opponent_excess_heart_count = oex
                gs.log.append(f'[DEBUG_START] opponent_excess_heart_count={oex}')
            except Exception:
                pass
        if turn_order_s:
            try:
                tos = str(turn_order_s).strip().lower()
                if tos in ('second', 'gote', '後手', '2'):
                    gs.turn_order = 'second'
                else:
                    gs.turn_order = 'first'
                gs.log.append(f'[DEBUG_START] turn_order={getattr(gs, "turn_order", "first")}')
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

        # Debug-only movement-state seed for testing hand-cost reductions that
        # depend on a member having moved this turn.
        if stage_moved_s or stage_moved_cards_s:
            try:
                moved = str(stage_moved_s).strip().lower() in ('1','true','yes','y','on','moved')
                cards = _split_cards(stage_moved_cards_s) if stage_moved_cards_s else []
                if cards:
                    moved = True
                setattr(gs, 'stage_moved_this_turn', bool(moved))
                if cards:
                    try:
                        cur = set(getattr(gs, 'stage_moved_cardnumbers_this_turn', set()) or set())
                    except Exception:
                        cur = set()
                    cur.update(cards)
                    setattr(gs, 'stage_moved_cardnumbers_this_turn', cur)
                try:
                    log = list(getattr(gs, 'stage_movement_log_this_turn', []) or [])
                    log.append({'debug_start': True, 'cards': list(cards), 'moved': bool(moved)})
                    setattr(gs, 'stage_movement_log_this_turn', log)
                except Exception:
                    pass
                gs.log.append(f'[DEBUG_START] stage_moved_this_turn={bool(moved)} cards={cards}')
            except Exception as e:
                try:
                    gs.log.append(f'[WARN] DEBUG_START stage_moved failed: {e}')
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
        if deckexact_present:
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

            strict_exact = str(deckexact_strict_s or '').strip() in ('1','true','TRUE','yes','YES')
            try:
                gs.deck = list(exact_cards)
            except Exception:
                pass
            try:
                if strict_exact:
                    gs.green_room = list(cur_green)
                    gs.log.append('[DEBUG_START] deck_exact strict: dropped original deck remainder')
                else:
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
                _add(item.get("pool"))
                _add(item.get("kept"))
                for key in ("card", "source_cn", "picked_card", "after_source_cn", "resume_source_cn"):
                    v = item.get(key)
                    if isinstance(v, str) and v:
                        cns.add(v)
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

    def _cn2is_live(self) -> Dict[str, bool]:
        out: Dict[str, bool] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            try:
                out[cn] = bool(is_live_type(getattr(ci, "type", "") or ""))
            except Exception:
                try:
                    out[cn] = int(getattr(ci, "score", 0) or 0) > 0
                except Exception:
                    out[cn] = False
        return out

    def _cn2yell_hearts(self) -> Dict[str, Dict[str, int]]:
        out: Dict[str, Dict[str, int]] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            counts = _ci_yell_heart_counts(ci)
            if counts:
                out[cn] = counts
        return out

    def _cn2yell_draw_icons(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            n = int(_ci_yell_draw_icon_count(ci) or 0)
            if n:
                out[cn] = n
        return out

    def _cn2yell_score_icons(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            n = int(_ci_yell_score_icon_count(ci) or 0)
            if n:
                out[cn] = n
        return out

    def _cn2yell_double_colorless_icons(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            n = int(_ci_yell_double_colorless_icon_count(ci) or 0)
            if n:
                out[cn] = n
        return out

    def _cn2yell_has_blade_heart(self) -> Dict[str, bool]:
        out: Dict[str, bool] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            out[cn] = bool(_ci_has_yell_blade_heart_payload(ci))
        return out

    def _cn2blade(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            try:
                n = int(getattr(ci, "blade", 0) or 0)
            except Exception:
                n = 0
            if n:
                out[cn] = n
        return out

    def _cn2base_hearts(self) -> Dict[str, Dict[str, int]]:
        out: Dict[str, Dict[str, int]] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            try:
                hearts = getattr(ci, "base_hearts", None) or {}
                counts = _ordered_heart_counts({str(k): int(v) for k, v in dict(hearts).items() if int(v or 0) > 0})
            except Exception:
                counts = {}
            if counts:
                out[cn] = counts
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

    def _cn2group(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci and getattr(ci, "group", None):
                out[cn] = str(ci.group)
        return out

    def _cn2unit(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci and getattr(ci, "unit", None):
                out[cn] = str(ci.unit)
        return out

    def _cn2cost(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            try:
                out[cn] = int(getattr(ci, "cost", 0) or 0)
            except Exception:
                pass
        return out

    def _hand_detail_for_ui(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for cn in list(getattr(self.gs, "hand", []) or []):
            ci = _get_card(self.cards_db, cn)
            try:
                base_cost = int(getattr(ci, "cost", 0) or 0) if ci else 0
            except Exception:
                base_cost = 0
            try:
                effective_cost = int(_card_effective_play_cost_from_hand(self.gs, self.cards_db, cn) or base_cost)
            except Exception:
                effective_cost = base_cost
            out.append({
                "cardnumber": cn,
                "base_cost": int(base_cost or 0),
                "effective_cost": int(effective_cost or 0),
                "can_activate_from_hand": bool(can_activate_from_hand_in_state(self.gs, self.cards_db, len(out))),
            })
        return out

    def _cn2score(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for cn in self._all_cardnumbers_in_state():
            ci = _get_card(self.cards_db, cn)
            if ci is None:
                continue
            try:
                out[cn] = int(getattr(ci, "score", 0) or 0)
            except Exception:
                pass
        return out

    def state_json(self) -> Dict[str, Any]:
        # Capture reveal acknowledgements while they are still pending, so the
        # public window can show them even if the owner resolves immediately.
        self._remember_public_reveals_from_pending("state_json")
        now = time.time()
        banner = None
        if getattr(self.gs, "banner_text", "") and (
            now - getattr(self.gs, "banner_ts", 0.0) <= getattr(self.gs, "banner_ttl", 0.0)
        ):
            banner = {"text": self.gs.banner_text}
        card_instances = self._zone_instance_state_for_ui()
        card_instance_meta = self._instance_meta_state_for_ui()

        return {
            "root": str(self.gs.root),
            "code": self.ui_code,
            "deck_code": self.deck_code,
            "seed": self.gs.seed,
            "debug": self.gs.debug,
            "remote_mode": bool(getattr(self, "remote_mode", False)),
            "turn": self.gs.turn,
            "phase": self.gs.phase,
            "live_start_prompted": bool(getattr(self.gs, "live_start_prompted", False)),
            "deck": self.gs.deck if self.gs.debug else ["?"] * len(self.gs.deck),
            "hand": list(self.gs.hand),
            "hand_detail": self._hand_detail_for_ui(),
            "energy_active": int(self.gs.energy_active),
            "energy_wait": int(self.gs.energy_wait),
            "opponent_wait_count": max(0, min(3, int(getattr(self.gs, "opponent_wait_count", 0) or 0))),
            "opponent_success_count": max(0, min(2, int(getattr(self.gs, "opponent_success_count", 0) or 0))),
            "opponent_excess_heart_count": max(0, min(9, int(getattr(self.gs, "opponent_excess_heart_count", 0) or 0))),
            "turn_order": str(getattr(self.gs, "turn_order", "first") or "first"),
            "next_turn_order": str(getattr(self.gs, "next_turn_order", "") or ""),
            "stage": {k: (asdict(v) if v else None) for k, v in self.gs.stage.items()},
            "green_room": list(self.gs.green_room),
            "set_zone": list(self.gs.set_zone),
            "live_set_limit": int(getattr(self.gs, "live_set_limit", 3) or 3),
            "set_zone_score_rows": self._set_zone_score_rows_for_ui(),
            "resolve_zone": list(self.gs.resolve_zone),
            "yell_reveal_acknowledged_this_live": bool(getattr(self.gs, "yell_reveal_acknowledged_this_live", False)),
            "yell_flow_completed_this_live": bool(getattr(self.gs, "yell_flow_completed_this_live", False)),
            "success_zone": list(getattr(self.gs, "success_zone", []) or []),
            "success_zone_score_sum": int(_success_zone_score_sum(self.gs, self.cards_db) or 0),
            "success_zone_heart_color": str(getattr(self.gs, "success_zone_heart_color", "") or ""),
            "success_zone_heart_pos": str(getattr(self.gs, "success_zone_heart_pos", "") or ""),
            "pending": list(self.gs.pending),
            "deck_refreshed_this_turn": bool(getattr(self.gs, "deck_refreshed_this_turn", False)),
            "refresh_notice_seq": int(getattr(self.gs, "refresh_notice_seq", 0) or 0),
            "refresh_notice_ack_seq": int(min(int(getattr(self.gs, "refresh_notice_seq", 0) or 0), int(getattr(self, "_refresh_notice_ack_seq", 0) or 0))),
            "refresh_notices": [dict(x) for x in (getattr(self.gs, "refresh_notices", []) or []) if isinstance(x, dict)],
            "effect_events": [dict(x) for x in (getattr(self.gs, "effect_events", []) or []) if isinstance(x, dict)][-80:],
            "public_reveal_events": self._public_reveal_events_snapshot(),
            "public_hand_revealed_cards": self._public_hand_revealed_cards_snapshot(),
            "public_hand_revealed_instance_ids": self._public_hand_revealed_instance_ids_snapshot(),
            "public_hand_revealed_orient": self._public_hand_revealed_orient_snapshot(),
            "public_hand_reveal_events": self._public_hand_reveal_events_snapshot(),
            "cn2name": self._cn2name(),
            "cn2label": self._cn2label(),
            "cn2type": self._cn2type(),
            "cn2is_live": self._cn2is_live(),
            "cn2yell_hearts": self._cn2yell_hearts(),
            "cn2yell_draw_icons": self._cn2yell_draw_icons(),
            "cn2yell_score_icons": self._cn2yell_score_icons(),
            "cn2yell_double_colorless_icons": self._cn2yell_double_colorless_icons(),
            "cn2yell_has_blade_heart": self._cn2yell_has_blade_heart(),
            "cn2image_rarity": self._cn2image_rarity(),
            "cn2image_variant_id": self._cn2image_variant_id(),
            "card_instances": card_instances,
            "card_instance_meta": card_instance_meta,
            "cn2group": self._cn2group(),
            "cn2unit": self._cn2unit(),
            "cn2cost": self._cn2cost(),
            "cn2score": self._cn2score(),
            "cn2blade": self._cn2blade(),
            "cn2base_hearts": self._cn2base_hearts(),
            "stage_detail": {
                k: (
                    {
                        "cardnumber": v.cardnumber,
                        "name": (_get_card(self.cards_db, v.cardnumber).name if _get_card(self.cards_db, v.cardnumber) else ""),
                        "type": (_get_card(self.cards_db, v.cardnumber).type if _get_card(self.cards_db, v.cardnumber) else ""),
                        "has_sac": _has_sacrifice_ability(_get_card(self.cards_db, v.cardnumber)),
                        "energy_under": int(getattr(v, "energy_under", 0) or 0),
                        "under_cards": [str(x) for x in list(getattr(v, "under_cards", []) or []) if str(x or "").strip()],
                        "base_cost": int(getattr(_get_card(self.cards_db, v.cardnumber), "cost", 0) or 0) if _get_card(self.cards_db, v.cardnumber) else 0,
                        "effective_cost": int(_slot_effective_cost(self.gs, self.cards_db, k, v) or 0),
                        "can_activate": can_activate_in_state(self.gs, self.cards_db, k),
                        # 一時的なブレード/ハート増加（UIアイコン表示用）
                        "temp_blade": int(getattr(v, "temp_blade", 0) or 0),
                        "temp_hearts": dict(getattr(v, "temp_hearts", {}) or {}),
                        "success_zone_hearts_bonus": dict(self._success_zone_hearts_bonus_for(k) or {}),
                        "always_hearts_bonus": dict(self._always_hearts_bonus_for(k, v) or {}),
                        # 常時BODYブレード加算（コスト13以上条件）
                        "always_blade_bonus": self._always_blade_bonus_for(k, v),
                        "always_score_bonus": self._always_score_bonus_for(k, v),
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
        from .engine import _compute_attempt_score_breakdown, _effective_live_required_hearts, _ordered_heart_counts
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
                    'req_delta': _ordered_heart_counts(req_delta),
                }
            return rows_out
        except Exception:
            return []

    def _always_blade_bonus_for(self, pos: str, slot) -> int:
        """常時ブレードボーナスを返す（UI表示専用）。"""
        from .engine import _slot_always_blade_bonus
        try:
            return int(_slot_always_blade_bonus(self.gs, self.cards_db, pos, slot) or 0)
        except Exception:
            return 0


    def _always_hearts_bonus_for(self, pos: str, slot) -> dict:
        """常時のハート加算を返す（UI表示専用）。"""
        from .engine import _slot_always_hearts_bonus
        try:
            return dict(_slot_always_hearts_bonus(self.gs, self.cards_db, pos, slot) or {})
        except Exception:
            return {}

    def _success_zone_hearts_bonus_for(self, pos: str) -> dict:
        """成功置き場枚数参照型のハート加算を overlay 用に返す。"""
        try:
            src_pos = str(getattr(self.gs, "success_zone_heart_pos", "") or "").upper()
            col = str(getattr(self.gs, "success_zone_heart_color", "") or "").lower().strip()
            if not src_pos or src_pos != str(pos or "").upper() or not col:
                return {}
            n = len(list(getattr(self.gs, "success_zone", []) or []))
            return {col: int(n)} if n > 0 else {}
        except Exception:
            return {}

    def _always_score_bonus_for(self, pos: str, slot) -> int:
        """常時のライブ合計スコア加算を返す（UI表示専用）。"""
        from .engine import _slot_always_score_bonus
        try:
            return int(_slot_always_score_bonus(self.gs, self.cards_db, pos, slot) or 0)
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


    def _auto_advance_live_attempt_after_yell_flow(self, reason: str = '') -> bool:
        """Advance directly from a fully acknowledged YELL flow to attempt summary.

        YELL cards intentionally remain in ``resolve_zone`` until live cleanup.
        Once the one-time YELL reveal acknowledgement and any resumed YELL auto
        prompts are finished, leaving the UI on an empty LIVE_ATTEMPT board adds an
        unnecessary NEXT-only pause.  Advance exactly that gap here; choice prompts
        still block because ``pending`` must be empty.
        """
        try:
            if str(getattr(self.gs, 'phase', '') or '') != 'LIVE_ATTEMPT':
                return False
            if list(getattr(self.gs, 'pending', []) or []):
                return False
            if not bool(getattr(self.gs, 'yell_reveal_acknowledged_this_live', False)):
                return False
            cmd_next(self.gs, self.rng, self.cards_db, [])
            post_process(self.gs)
            try:
                self.gs.log.append(f'[AUTO] YELL flow -> live attempt summary ({reason or "auto"})')
            except Exception:
                pass
            return True
        except Exception as e:
            try:
                self.gs.log.append(f'[WARN] auto live-attempt advance failed: {e}')
            except Exception:
                pass
            return False

    def _debug_list_zone(self, zone: str) -> Optional[List[str]]:
        key = str(zone or "").strip().lower()
        if key == "hand":
            return self.gs.hand
        if key == "deck":
            return self.gs.deck
        if key in {"green", "green_room", "waiting"}:
            return self.gs.green_room
        if key in {"success", "success_zone"}:
            return self.gs.success_zone
        return None

    def _debug_stage_pos(self, zone: str, pos: str = "") -> str:
        text = str(pos or "").strip().upper()
        if text in {"L", "C", "R"}:
            return text
        z = str(zone or "").strip().upper()
        if z.startswith("STAGE:"):
            cand = z.split(":", 1)[1].strip().upper()
            if cand in {"L", "C", "R"}:
                return cand
        if z in {"L", "C", "R"}:
            return z
        return ""

    def _debug_take_card(self, zone: str, index: Any = None, pos: str = "") -> str:
        stage_pos = self._debug_stage_pos(zone, pos)
        if stage_pos:
            slot = (getattr(self.gs, "stage", {}) or {}).get(stage_pos)
            if not slot or not getattr(slot, "cardnumber", ""):
                raise ValueError("移動元ステージにカードがありません。")
            cn = str(getattr(slot, "cardnumber", "") or "")
            under_cards = [str(x) for x in list(getattr(slot, "under_cards", []) or []) if str(x or "").strip()]
            energy_under = int(getattr(slot, "energy_under", 0) or 0)
            self.gs.stage[stage_pos] = None
            if under_cards:
                self.gs.green_room.extend(under_cards)
                self.gs.log.append(f"[DEBUG-MOVE] stage:{stage_pos} under_cards -> green_room count={len(under_cards)}")
            if energy_under:
                self.gs.log.append(f"[DEBUG-MOVE] stage:{stage_pos} energy_under cleared count={energy_under}")
            return cn

        lst = self._debug_list_zone(zone)
        if lst is None:
            raise ValueError("移動元領域が不正です。")
        try:
            idx = int(index)
        except Exception:
            idx = -1
        if idx < 0 or idx >= len(lst):
            raise ValueError("移動元カード位置が不正です。")
        return str(lst.pop(idx) or "")

    def _debug_put_card(self, cn: str, zone: str, index: Any = None, pos: str = "") -> None:
        cardnumber = str(cn or "").strip()
        if not cardnumber:
            raise ValueError("移動カードが空です。")
        stage_pos = self._debug_stage_pos(zone, pos)
        if stage_pos:
            old = (getattr(self.gs, "stage", {}) or {}).get(stage_pos)
            if old and getattr(old, "cardnumber", ""):
                old_cn = str(getattr(old, "cardnumber", "") or "")
                self.gs.green_room.append(old_cn)
                under_cards = [str(x) for x in list(getattr(old, "under_cards", []) or []) if str(x or "").strip()]
                if under_cards:
                    self.gs.green_room.extend(under_cards)
                self.gs.log.append(f"[DEBUG-MOVE] replaced stage:{stage_pos} -> green_room {old_cn}")
            self.gs.stage[stage_pos] = StageSlot(cardnumber=cardnumber, active=True)
            return

        lst = self._debug_list_zone(zone)
        if lst is None:
            raise ValueError("移動先領域が不正です。")
        try:
            idx = int(index)
        except Exception:
            idx = len(lst)
        idx = max(0, min(len(lst), idx))
        lst.insert(idx, cardnumber)

    def _cmd_debug_move_card(self, payload: Dict[str, Any]) -> None:
        from_zone = str(payload.get("from_zone", "") or "")
        to_zone = str(payload.get("to_zone", "") or "")
        from_pos = str(payload.get("from_pos", "") or "")
        to_pos = str(payload.get("to_pos", "") or "")
        cn = self._debug_take_card(from_zone, payload.get("from_index", -1), from_pos)
        try:
            self._debug_put_card(cn, to_zone, payload.get("to_index", None), to_pos)
        except Exception:
            self._debug_put_card(cn, from_zone, payload.get("from_index", None), from_pos)
            raise
        self._sync_card_instances_from_state()
        self.gs.log.append(f"[DEBUG-MOVE] {cn}: {from_zone}{(':'+from_pos) if from_pos else ''} -> {to_zone}{(':'+to_pos) if to_pos else ''}")

    def _cmd_debug_reorder_zone(self, payload: Dict[str, Any]) -> None:
        zone = str(payload.get("zone", "") or "")
        lst = self._debug_list_zone(zone)
        if lst is None:
            raise ValueError("並び替え対象領域が不正です。")
        new_cards = [str(x) for x in list(payload.get("cards", []) or [])]
        if sorted(new_cards) != sorted([str(x) for x in lst]):
            raise ValueError("並び替え前後のカード集合が一致しません。")
        lst[:] = new_cards
        self._sync_card_instances_from_state()
        self.gs.log.append(f"[DEBUG-MOVE] reorder {zone} count={len(lst)}")

    def cmd(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:        # PATCH_V2_10_GUARD_MAIN_ONLY
        try:
            ph0 = str(getattr(self.gs, 'phase', '') or '')
        except Exception:
            ph0 = ''
        if name in {'play', 'activate_to_green', 'activate_from_hand'} and ph0 != 'MAIN':
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
            "activate_from_hand",
            "resolve_pending",
            "next",
            "mulligan_next",
            "opponent_wait_delta",
            "opponent_success_delta",
            "turn_order_set",
            "ack_yell_reveal",
            "ack_refresh_notice",
            "record_result",
            "debug_move_card",
            "debug_reorder_zone",
        }
        unacked_refresh_seq = self._latest_unacked_refresh_notice_seq()
        if mutating and unacked_refresh_seq and name not in {"ack_refresh_notice", "undo", "reset", "record_reset", "record_result", "toggle_debug", "debug_move_card", "debug_reorder_zone"}:
            if name == "next":
                self._push_undo_with_app_state()
                self._ack_refresh_notice(unacked_refresh_seq)
                try:
                    self.gs.log.append(f"[ACK] refresh notice seq={unacked_refresh_seq} acknowledged by NEXT")
                except Exception:
                    pass
            else:
                try:
                    self.gs.log.append(f"[BLOCK] {name}: refresh notice seq={unacked_refresh_seq} requires confirmation first")
                except Exception:
                    pass
            self.save_trace()
            return self.state_json()

        before_hand_for_public_reveal: List[str] = []
        before_hand_instance_ids_for_public_reveal: List[str] = []
        reveal_candidates_for_public_hand: List[str] = []
        before_refresh_notice_seq_for_public_hand: int = 0
        if mutating and name != "toggle_debug":
            # Owner commands can clear a reveal ACK before the public window's
            # next poll.  Preserve it in a short-lived public ledger first.
            self._remember_public_reveals_from_pending(f"before_cmd:{name}")
            try:
                before_hand_for_public_reveal = [str(cn) for cn in list(getattr(self.gs, "hand", []) or [])]
            except Exception:
                before_hand_for_public_reveal = []
            try:
                before_hand_instance_ids_for_public_reveal = [str(x) for x in list((self._zone_instance_state_for_ui().get("hand") or []))]
            except Exception:
                before_hand_instance_ids_for_public_reveal = []
            reveal_candidates_for_public_hand = self._reveal_candidate_cards_from_pending()
            self._public_hand_before_source_counts = self._public_source_counts_for_hand_reveal()
            try:
                before_refresh_notice_seq_for_public_hand = int(getattr(self.gs, "refresh_notice_seq", 0) or 0)
            except Exception:
                before_refresh_notice_seq_for_public_hand = 0
            self._push_undo_with_app_state()

        if name == "play":
            cmd_play(self.gs, self.cards_db, int(payload.get("hand_idx", -1)), str(payload.get("pos", "")))
        elif name == "debug_move_card":
            try:
                self._cmd_debug_move_card(payload)
            except Exception as e:
                self.gs.log.append(f"[DEBUG-MOVE-ERR] {e}")
                self.gs.banner_text = str(e)
                self.gs.banner_ts = time.time()
                self.gs.banner_ttl = 2.5
            self.save_trace()
            return self.state_json()
        elif name == "debug_reorder_zone":
            try:
                self._cmd_debug_reorder_zone(payload)
            except Exception as e:
                self.gs.log.append(f"[DEBUG-MOVE-ERR] {e}")
                self.gs.banner_text = str(e)
                self.gs.banner_ts = time.time()
                self.gs.banner_ttl = 2.5
            self.save_trace()
            return self.state_json()
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
        elif name == "activate_from_hand":
            cmd_activate_from_hand(self.gs, self.cards_db, int(payload.get("hand_idx", -1)), self.rng)
        elif name == "toggle_stage_active":
            self._push_undo_with_app_state()
            cmd_toggle_stage_active(self.gs, self.cards_db, str(payload.get("pos", "")))
        elif name == "opponent_wait_delta":
            try:
                delta = int(payload.get("delta", 0) or 0)
            except Exception:
                delta = 0
            cur = max(0, min(3, int(getattr(self.gs, "opponent_wait_count", 0) or 0)))
            newv = max(0, min(3, cur + delta))
            try:
                self.gs.opponent_wait_count = newv
                self.gs.log.append(f"[UI] opponent_wait_count {cur} -> {newv}")
            except Exception:
                pass
        elif name == "opponent_success_delta":
            try:
                delta = int(payload.get("delta", 0) or 0)
            except Exception:
                delta = 0
            cur = max(0, min(2, int(getattr(self.gs, "opponent_success_count", 0) or 0)))
            newv = max(0, min(2, cur + delta))
            try:
                self.gs.opponent_success_count = newv
                self.gs.log.append(f"[UI] opponent_success_count {cur} -> {newv}")
            except Exception:
                pass
        elif name == "ack_yell_reveal":
            try:
                self.gs.yell_reveal_acknowledged_this_live = True
                self.gs.log.append('[ACK] yell reveal fallback acknowledged')
            except Exception:
                pass
        elif name == "reset":
            self.reset_match()
            return self.state_json()
        elif name == "record_reset":
            self.record_result_and_reset(payload.get("result", ""))
            return self.state_json()
        elif name == "record_result":
            self.record_result_only(payload.get("result", ""))
            return self.state_json()
        elif name == "turn_order_set":
            raw = str(payload.get("value", "") or "").strip().lower()
            val = "second" if raw in ("second", "gote", "後手", "2") else "first"
            try:
                oldv = str(getattr(self.gs, "turn_order", "first") or "first")
                self.gs.turn_order = val
                self.gs.next_turn_order = ""
                self.gs.log.append(f"[UI] turn_order {oldv} -> {val}")
            except Exception:
                pass
        elif name == "resolve_pending":
            cmd_resolve_pending(
                self.gs,
                self.cards_db,
                int(payload.get("idx", -1)),
                str(payload.get("choice", "")),
                self.rng,
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
                if isinstance(p0, dict):
                    k0 = str(p0.get('kind','') or '')
                    ack_kinds = {
                        'show_revealed_cards_ack', 'message_ack', 'effect_notice', 'live_attempt_summary_ack',
                        'live_start_success_count_distinct_names_score_ack',
                        'mass_bottom_auto_ack', 'mass_bottom_optional_result_ack',
                    }
                    if k0 == 'choose_enter_effect_mode' and not (bool(p0.get('optional', False)) or bool(p0.get('allow_skip', False))):
                        msg = '必須選択です。いずれかの効果を選んでください。'
                        txt = str(p0.get('text', '') or '')
                        if msg not in txt:
                            p0['text'] = (txt + '\n' + msg).strip()
                        p0['last_error'] = msg
                        p0['mandatory'] = True
                        p0['allow_skip'] = False
                        self.gs.pending[0] = p0
                        self.gs.log.append('[BLOCK] next: choose_enter_effect_mode requires a choice')
                        post_process(self.gs)
                        self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                        self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
                        self.save_trace()
                        return self.state_json()
                    if k0 in ack_kinds:
                        cmd_resolve_pending(self.gs, self.cards_db, 0, 'ok')
                        post_process(self.gs)
                        self._auto_advance_live_attempt_after_yell_flow(f'next_ack:{k0}')
                        self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                        self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
                        self.save_trace()
                        return self.state_json()
                    if k0 == 'set_opponent_excess_for_live_success':
                        cur_ex = str(max(0, min(9, int(getattr(self.gs, 'opponent_excess_heart_count', 0) or 0))))
                        cmd_resolve_pending(self.gs, self.cards_db, 0, cur_ex)
                        post_process(self.gs)
                        self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                        self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
                        self.save_trace()
                        return self.state_json()
                    if k0 == 'set_opponent_success_score_for_live_attempt':
                        cur_oss_i = int(getattr(self.gs, 'opponent_success_score_sum', -1) or -1)
                        if cur_oss_i < 0:
                            cur_oss_i = 0
                        cmd_resolve_pending(self.gs, self.cards_db, 0, str(max(0, min(20, cur_oss_i))), self.rng)
                        post_process(self.gs)
                        self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                        self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
                        self.save_trace()
                        return self.state_json()
                    if k0 == 'auto_order':
                        auto_opts = [str(x) for x in list(p0.get('options', []) or []) if str(x).strip()]
                        if auto_opts:
                            cmd_resolve_pending(self.gs, self.cards_db, 0, auto_opts[0], self.rng)
                            post_process(self.gs)
                            self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                            self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
                            self.save_trace()
                            return self.state_json()
                    if k0 == 'pick_success_to_store':
                        cmd_resolve_pending(self.gs, self.cards_db, 0, 'skip')
                        post_process(self.gs)
                        self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                        self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
                        self.save_trace()
                        return self.state_json()
                    if ('skip' in opts or '__skip__' in opts) and (bool(p0.get('optional', False)) or bool(p0.get('allow_skip', False)) or k0 in ('pay_or_skip', 'confirm_effect', 'discard_from_hand')):
                        cmd_resolve_pending(self.gs, self.cards_db, 0, 'skip')
                        post_process(self.gs)
                        self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                        self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
                        self.save_trace()
                        return self.state_json()
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
                        self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
                        self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, f"next:{k0}", before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)
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
            self._do_undo_with_app_state()
        elif name == "ack_refresh_notice":
            try:
                self._ack_refresh_notice(int(payload.get("seq", 0) or 0))
            except Exception:
                pass
        elif name == "toggle_debug":
            self.gs.debug = not self.gs.debug
            self.gs.log.append(f"[DEBUG] debug={self.gs.debug}")
        else:
            self.gs.log.append(f"[ERR] unknown cmd: {name}")

        # Post-process to resume deferred prompts (e.g., auto trigger order).
        post_process(self.gs)
        if mutating and name not in {"toggle_debug", "undo", "ack_refresh_notice"}:
            self._auto_advance_live_attempt_after_yell_flow(f'post_cmd:{name}')
        if mutating and name not in {"toggle_debug", "undo", "ack_refresh_notice"}:
            self._auto_refresh_if_deck_empty_after_cmd(f"post_cmd:{name}")
        if mutating and name != "toggle_debug":
            self._remember_public_hand_reveals_after_cmd(before_hand_for_public_reveal, reveal_candidates_for_public_hand, name, before_refresh_notice_seq_for_public_hand, before_hand_instance_ids_for_public_reveal)

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
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(content)))
            # BUILD_TAG: public_refresh_notice_reload_nocache_20260701ar
            # The public window is often kept open while code is patched.  Do not let
            # the browser reuse an old HTML/JS bundle; stale public JS can render the
            # legacy refresh popup and miss owner-OK acknowledgement handling.
            if "text/html" in str(ctype).lower() or "application/json" in str(ctype).lower():
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
            self.end_headers()
            if not self._head_only and content:
                self.wfile.write(content)
        except (BrokenPipeError, ConnectionResetError):
            # Browsers often cancel image requests when cards are re-rendered.
            # Treat that as a completed client-side cancellation, not a server
            # error worth flooding the app log with.
            return

    def do_HEAD(self) -> None:
        # Reuse GET routing; just suppress body.
        self._head_only = True
        try:
            self.do_GET()
        finally:
            self._head_only = False

    def do_GET(self) -> None:
        u = urlparse(self.path)

        if u.path == "/" or u.path == "/public":
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
            qs = parse_qs(u.query)
            view_mode = (qs.get("view", [""])[0] or qs.get("mode", [""])[0] or "private").strip().lower()
            data = self.app.view_state_bytes(view_mode)
            self._send(200, data, "application/json; charset=utf-8")
            return

        if u.path == "/public_state":
            data = self.app.view_state_bytes("public")
            self._send(200, data, "application/json; charset=utf-8")
            return

        if u.path == "/suspend_state":
            data = json.dumps(self.app.export_suspend_data(), ensure_ascii=False).encode("utf-8")
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
                hearts = _ordered_heart_counts({k: v for k, v in bh.items() if v and int(v) > 0})
            except Exception:
                pass
            # required hearts + score (LIVE)
            required_hearts = {}
            try:
                rh = getattr(ci, 'required_hearts', None) or {}
                required_hearts = _ordered_heart_counts({k: v for k, v in rh.items() if v and int(v) > 0})
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
            # special: public/private card back image.
            # Use the official local back image under llocg_db_out_full/card_images/back.png.
            if cn == "__BACK__":
                cand = []
                try:
                    loveca_root = Path(__file__).resolve().parents[1]
                    cand.extend([
                        loveca_root / "llocg_db_out_full" / "card_images" / "back.png",
                        self.app.root / "llocg_db_out_full" / "card_images" / "back.png",
                        self.app.root / "card_images" / "back.png",
                        Path.cwd() / "llocg_db_out_full" / "card_images" / "back.png",
                        Path.cwd() / "card_images" / "back.png",
                    ])
                except Exception:
                    pass
                for p2 in cand:
                    try:
                        if p2 and p2.exists():
                            self._send(200, p2.read_bytes(), "image/png")
                            return
                    except Exception:
                        pass
                self._send(404, b"", "text/plain")
                return

            # special: energy card back image
            if cn == "__ENERGY__":
                cand = []
                try:
                    cand.append(Path.cwd() / "energy.png")
                    cand.append(Path.cwd() / "energy.jpg")
                    cand.append(Path.cwd() / "energy.jpeg")
                    cand.append(Path.cwd() / "energy.webp")
                    cand.append(self.app.root / "energy.png")
                    cand.append(self.app.root / "energy.jpg")
                    cand.append(self.app.root / "energy.jpeg")
                    cand.append(self.app.root / "energy.webp")
                    cand.append(self.app.root / "llocg_db_out_full" / "card_images" / "energy.png")
                    cand.append(self.app.root / "llocg_db_out_full" / "card_images" / "energy.jpg")
                    cand.append(self.app.root / "llocg_db_out_full" / "card_images" / "energy.jpeg")
                    cand.append(self.app.root / "llocg_db_out_full" / "card_images" / "energy.webp")
                    cand.append(self.app.root / "card_images" / "energy.png")
                    cand.append(self.app.root / "card_images" / "energy.jpg")
                    cand.append(self.app.root / "card_images" / "energy.jpeg")
                    cand.append(self.app.root / "card_images" / "energy.webp")
                    cand.append(Path.cwd() / "llocg_db_out_full" / "card_images" / "energy.png")
                    cand.append(Path.cwd() / "llocg_db_out_full" / "card_images" / "energy.jpg")
                    cand.append(Path.cwd() / "llocg_db_out_full" / "card_images" / "energy.jpeg")
                    cand.append(Path.cwd() / "llocg_db_out_full" / "card_images" / "energy.webp")
                    cand.append(self.app.root / "llocg_db_out_full" / "energy.jpg")
                except Exception:
                    pass
                for p2 in cand:
                    try:
                        if p2 and p2.exists():
                            ctype = "image/webp" if str(p2).lower().endswith(".webp") else "image/jpeg" if str(p2).lower().endswith((".jpg",".jpeg")) else "image/png"
                            self._send(200, p2.read_bytes(), ctype)
                            return
                    except Exception:
                        pass
                # fallback: 1x1 transparent PNG
                self._send(200, bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a49444154789c6360000002000154a24f5d0000000049454e44ae426082'), "image/png")
                return
            # BUILD_TAG: image_preview_fallback_canonical_priority_20260708a
            rarity = unquote((qs.get("rarity", [""])[0] or "").strip())
            variant_id = unquote((qs.get("variant_id", [""])[0] or "").strip())
            if not rarity and variant_id:
                rarity = self.app._rarity_from_variant_id(variant_id)
            p = self.app.img.find(cn, rarity=rarity)
            if p and p.exists():
                ctype = "image/png"
                p_lower = str(p).lower()
                if p_lower.endswith((".jpg", ".jpeg")):
                    ctype = "image/jpeg"
                elif p_lower.endswith(".webp"):
                    ctype = "image/webp"
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
        if u.path not in {"/cmd", "/resume_state"}:
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        n = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(n) if n > 0 else b"{}"
        try:
            obj = json.loads(body.decode("utf-8"))
        except Exception:
            obj = {}

        if u.path == "/resume_state":
            try:
                state = self.app.import_suspend_data(obj)
                data = json.dumps({"ok": True, "state": state}, ensure_ascii=False).encode("utf-8")
                self._send(200, data, "application/json; charset=utf-8")
                return
            except Exception as exc:
                data = json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False).encode("utf-8")
                self._send(400, data, "application/json; charset=utf-8")
                return

        cmd = str(obj.get("cmd", "")).strip()
        payload = obj.get("payload", {}) or {}
        if not isinstance(payload, dict):
            payload = {}

        if cmd == "shutdown":
            data = json.dumps({"ok": True, "message": "シミュレータを終了します。"}, ensure_ascii=False).encode("utf-8")
            self._send(200, data, "application/json; charset=utf-8")
            try:
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            except Exception:
                pass
            return

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
    --uiScale: 0.77;
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
  .label{position:absolute;left:calc(6px * var(--uiScale));top:calc(6px * var(--uiScale));padding:calc(2px * var(--uiScale)) calc(6px * var(--uiScale));font-size:calc(12px * var(--uiScale));background:rgba(0,0,0,.55);border-radius:calc(6px * var(--uiScale));pointer-events:none;}
  .countBadge{position:absolute;right:calc(6px * var(--uiScale));bottom:calc(6px * var(--uiScale));padding:calc(2px * var(--uiScale)) calc(6px * var(--uiScale));font-size:calc(12px * var(--uiScale));background:rgba(0,0,0,.75);border-radius:calc(6px * var(--uiScale));pointer-events:none;}
  .underEnergyBadge{position:absolute;min-width:calc(32px * var(--uiScale));height:calc(23px * var(--uiScale));padding:0 calc(7px * var(--uiScale));box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;gap:calc(4px * var(--uiScale));font-size:calc(11px * var(--uiScale));font-weight:900;line-height:1;color:#fff;background:rgba(0,0,0,.82);border:1px solid rgba(255,255,255,.58);border-radius:999px;box-shadow:0 2px 7px rgba(0,0,0,.48);pointer-events:none;z-index:470;transform:translate(-100%,-100%);}
  .underEnergyBadgeIcon{position:relative;width:calc(11px * var(--uiScale));height:calc(15px * var(--uiScale));border:1px solid rgba(255,255,255,.86);border-radius:calc(2px * var(--uiScale));box-sizing:border-box;background:linear-gradient(180deg,rgba(255,255,255,.30),rgba(120,180,255,.30));}
  .underEnergyBadgeIcon::before{content:'';position:absolute;left:calc(-4px * var(--uiScale));top:calc(3px * var(--uiScale));width:calc(11px * var(--uiScale));height:calc(15px * var(--uiScale));border:1px solid rgba(255,255,255,.62);border-radius:calc(2px * var(--uiScale));box-sizing:border-box;background:rgba(80,120,190,.32);z-index:-1;}
  .underEnergyBadgeCount{display:inline-block;min-width:calc(10px * var(--uiScale));text-align:left;}
  .zoneInner{position:absolute;inset:0;overflow:hidden;}

  /* cards */
  .cardWrap{position:absolute;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,.55);user-select:none;cursor:pointer;background:#000;}
  .cardWrap img{position:absolute;left:0;top:0;border-radius:8px;display:block;width:100%;height:100%;pointer-events:none;}
  .cardWrap.selected{box-shadow:0 0 0 5px rgba(0,0,0,.92) inset, 0 0 0 5px rgba(0,0,0,.92); border-radius:12px;}
  .cap{position:absolute;left:calc(6px * var(--uiScale));right:calc(6px * var(--uiScale));bottom:calc(-18px * var(--uiScale));font-size:calc(11px * var(--uiScale));line-height:1.1;color:#eee;text-shadow:0 1px 2px rgba(0,0,0,.8);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none;}

  /* rotation wrappers */
  .rot{position:absolute;left:50%;top:50%;transform-origin:center;}

  /* top bar */
  #topBar{position:absolute;left:calc(10px * var(--uiScale));top:calc(10px * var(--uiScale));display:flex;gap:calc(8px * var(--uiScale));align-items:center;z-index:6000;flex-wrap:wrap;}
  #topBar .pill{background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:calc(6px * var(--uiScale)) calc(10px * var(--uiScale));font-size:calc(12px * var(--uiScale));}
  #topBar .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:calc(6px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:calc(10px * var(--uiScale));font-size:calc(12px * var(--uiScale));cursor:pointer;}
  #topBar .miniBtn:hover{background:rgba(255,255,255,.18);}
  #topBar .debugMoveBtn{background:rgba(140,60,70,.82);border-color:rgba(255,185,195,.32);}
  #topBar .debugMoveBtn.active{background:#ffda62;color:#15100a;border-color:rgba(0,0,0,.32);box-shadow:0 0 0 2px rgba(0,0,0,.28),0 0 14px rgba(255,218,98,.42);}
  body.publicView #topBar .miniBtn, body.publicView #topBar .oppWaitBtn{opacity:.35;cursor:not-allowed;pointer-events:none;}
  #publicViewBadge{display:none;background:#66d9ef;color:#071014;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:6px 10px;font-size:12px;font-weight:900;letter-spacing:.04em;}
  body.publicView #publicViewBadge{display:inline-flex;}
  .publicPendingNote{margin-top:10px;padding:10px 12px;border-radius:10px;background:rgba(102,217,239,.10);border:1px solid rgba(102,217,239,.28);color:#dff9ff;font-size:13px;line-height:1.45;}
  .publicKnownHandPanel{position:absolute;right:calc(var(--sideW) + 14px);bottom:18px;z-index:8200;display:none;gap:8px;align-items:flex-end;padding:9px 10px 10px;border-radius:12px;background:rgba(0,0,0,.68);border:1px solid rgba(255,216,77,.42);box-shadow:0 8px 26px rgba(0,0,0,.55);}
  .publicKnownHandPanel .publicKnownTitle{font-size:12px;font-weight:900;color:#ffe985;writing-mode:vertical-rl;letter-spacing:.08em;line-height:1.1;}
  .cardWrap.publicRevealFlash{animation:publicRevealBlink .55s ease-in-out 0s 4;box-shadow:0 0 0 4px rgba(255,216,77,.95),0 0 24px rgba(255,216,77,.95),0 8px 22px rgba(0,0,0,.70) !important;}
  .cardWrap.publicKnownHandCard{box-shadow:0 0 0 2px rgba(255,216,77,.75),0 8px 22px rgba(0,0,0,.70) !important;}
    .publicRevealFloat{position:absolute;left:50%;top:18%;transform:translateX(-50%);z-index:20000;padding:12px 16px;border-radius:16px;background:rgba(0,0,0,.78);border:1px solid rgba(255,216,77,.72);box-shadow:0 10px 30px rgba(0,0,0,.62),0 0 28px rgba(255,216,77,.38);display:flex;align-items:center;gap:12px;pointer-events:none;animation:publicRevealFloat 2.8s ease-out forwards;}
  .publicRevealFloatTitle{font-size:16px;font-weight:900;color:#ffe985;white-space:nowrap;text-shadow:0 2px 3px rgba(0,0,0,.9);}
  @keyframes publicRevealBlink{0%,100%{filter:none;transform:translateY(0);}50%{filter:brightness(1.35);transform:translateY(-4px);}}
  @keyframes publicRevealFloat{0%{opacity:0;transform:translate(-50%,12px) scale(.96);}12%{opacity:1;transform:translate(-50%,0) scale(1);}82%{opacity:1;transform:translate(-50%,0) scale(1);}100%{opacity:0;transform:translate(-50%,-14px) scale(1.02);}}
  #topBar .oppWaitPill{display:flex;align-items:center;gap:6px;}
  #topBar .oppWaitBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.16);border-radius:999px;min-width:24px;height:22px;padding:0 7px;line-height:18px;font-size:13px;font-weight:800;cursor:pointer;}
  #topBar .turnOrderBtn{min-width:42px;}
  #topBar .oppWaitBtn:hover{background:rgba(255,255,255,.20);}
  #topBar .oppWaitBtn.orderSelected{background:#ffd84d;color:#111;border-color:#ffd84d;box-shadow:0 0 0 2px rgba(0,0,0,.35),0 0 12px rgba(255,216,77,.55);}
  #resetPanel{position:absolute;right:calc(var(--sideW) + calc(12px * var(--uiScale)));top:calc(10px * var(--uiScale));z-index:7600;display:none;align-items:center;gap:calc(6px * var(--uiScale));padding:calc(7px * var(--uiScale)) calc(8px * var(--uiScale));border-radius:calc(13px * var(--uiScale));background:rgba(15,18,24,.82);border:1px solid rgba(255,255,255,.20);box-shadow:0 calc(8px * var(--uiScale)) calc(26px * var(--uiScale)) rgba(0,0,0,.48);backdrop-filter:blur(6px);}
  #resetPanel.visible{display:flex;}
  #resetPanel .resetPanelTitle{font-size:calc(10px * var(--uiScale));font-weight:900;color:#d6deea;letter-spacing:.06em;white-space:nowrap;opacity:.88;}
  #resetPanel button{border:1px solid rgba(255,255,255,.20);border-radius:calc(9px * var(--uiScale));padding:calc(6px * var(--uiScale)) calc(9px * var(--uiScale));background:#7a3f52;color:#fff;font-size:calc(12px * var(--uiScale));font-weight:900;line-height:1.1;cursor:pointer;white-space:nowrap;}
  #resetPanel button:hover{background:#934c64;}
  #resetPanel button:disabled{opacity:.45;cursor:wait;}
  body.publicView #resetPanel{display:none !important;}

  /* banner */
  #banner{position:absolute;left:50%;top:calc(54px * var(--uiScale));transform:translateX(-50%);padding:calc(10px * var(--uiScale)) calc(16px * var(--uiScale));border-radius:999px;background:rgba(0,0,0,.72);border:1px solid rgba(255,255,255,.22);z-index:9900;display:none;font-size:calc(18px * var(--uiScale));font-weight:800;letter-spacing:.5px;pointer-events:none;max-width:85%;text-align:center;}
  #banner[data-kind="fail"]{background:rgba(160,20,20,.78);}
  #banner[data-kind="success"]{background:rgba(20,140,60,.78);}
  #banner[data-kind="info"]{background:rgba(0,0,0,.72);}


  /* log */
  #logBox{position:absolute;inset:0;overflow:hidden;font-size:12px;line-height:1.3;padding:8px;background:rgba(0,0,0,.45);border-radius:10px;display:flex;flex-direction:column;gap:6px;}
  #effectLogPanel{flex:0 0 auto;max-height:92px;overflow:auto;border-radius:8px;background:rgba(102,217,239,.08);border:1px solid rgba(102,217,239,.22);padding:6px 7px;color:#eaffff;}
  .effectLogHeader{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:10px;font-weight:900;letter-spacing:.06em;color:#9eeeff;margin-bottom:4px;text-transform:uppercase;}
  .effectLogHint{font-size:10px;color:#aaa;font-weight:600;text-transform:none;letter-spacing:0;}
  .effectLogRow{display:grid;grid-template-columns:auto 1fr;gap:5px 7px;align-items:start;padding:3px 0;border-top:1px solid rgba(255,255,255,.06);}
  .effectLogRow:first-of-type{border-top:0;}
  .effectLogType{font-size:10px;font-weight:900;color:#111;background:#9eeeff;border-radius:999px;padding:1px 6px;white-space:nowrap;line-height:1.45;}
  .effectLogBody{min-width:0;font-size:11px;line-height:1.35;color:#e8faff;}
  .effectLogDetail{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .effectLogMeta{margin-top:1px;color:#b9c7cc;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  #rawLogText{flex:1 1 auto;min-height:0;overflow:auto;white-space:pre-wrap;color:#ddd;}

  /* energy UI */
  .energyUI{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-start;gap:calc(8px * var(--uiScale));padding:calc(26px * var(--uiScale)) calc(10px * var(--uiScale)) calc(10px * var(--uiScale)) calc(10px * var(--uiScale));}
  .energyUI .energyText{font-size:calc(14px * var(--uiScale));line-height:1.2;background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.12);border-radius:calc(12px * var(--uiScale));padding:calc(8px * var(--uiScale)) calc(10px * var(--uiScale));color:#eee;}
  .energyUI .btn{background:rgba(0,0,0,.65);color:#eee;border:1px solid rgba(255,255,255,.14);padding:calc(10px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:calc(12px * var(--uiScale));cursor:pointer;font-size:calc(13px * var(--uiScale));text-align:center;}
  .energyUI .btn.primary{background:#ffd54a;color:#111;border-color:rgba(0,0,0,.3);}
  .cardWrap.underEnergy{pointer-events:none;}

  /* small activation button on stage card */
  .actBtn{position:absolute;left:calc(6px * var(--uiScale));right:calc(6px * var(--uiScale));bottom:calc(6px * var(--uiScale));padding:calc(6px * var(--uiScale)) calc(6px * var(--uiScale));border-radius:calc(10px * var(--uiScale));border:1px solid rgba(255,255,255,.18);
          background:rgba(0,0,0,.6);color:#fff;font-size:calc(12px * var(--uiScale));cursor:pointer;}
  .actBtn:hover{background:rgba(0,0,0,.74);}
  .toggleActiveBtn{position:absolute;top:calc(4px * var(--uiScale));left:calc(34px * var(--uiScale));width:calc(24px * var(--uiScale));height:calc(24px * var(--uiScale));border-radius:50%;border:1px solid rgba(255,255,255,.4);
                   background:rgba(0,0,0,.55);color:#fff;font-size:calc(14px * var(--uiScale));line-height:calc(22px * var(--uiScale));text-align:center;cursor:pointer;padding:0;z-index:10;}
  .toggleActiveBtn:hover{background:rgba(80,180,255,.7);}
  .stageStatsBadge{position:absolute;left:50%;top:calc(-18px * var(--uiScale));transform:translateX(-50%);z-index:25;display:none;min-width:calc(48px * var(--uiScale));padding:calc(3px * var(--uiScale)) calc(8px * var(--uiScale));border-radius:999px;background:rgba(0,0,0,.74);border:1px solid rgba(255,255,255,.34);box-shadow:0 4px 12px rgba(0,0,0,.45);font-size:calc(13px * var(--uiScale));font-weight:900;color:#fff;text-align:center;pointer-events:none;}
  body.showStats .stageStatsBadge{display:block;}
  .statsPanel{position:absolute;left:calc(275px * var(--uiScale));top:calc(585px * var(--uiScale));width:calc(112px * var(--uiScale));z-index:7200;display:flex;flex-direction:column;gap:calc(6px * var(--uiScale));align-items:stretch;}
  .statsTotal{border-radius:calc(8px * var(--uiScale));border:1px solid rgba(255,255,255,.18);background:rgba(0,0,0,.58);padding:calc(5px * var(--uiScale));font-size:calc(12px * var(--uiScale));font-weight:900;text-align:center;color:#fff;}
  .statsToggleBtn{border-radius:calc(8px * var(--uiScale));border:1px solid rgba(255,255,255,.22);background:rgba(33,43,54,.84);color:#fff;padding:calc(6px * var(--uiScale));font-size:calc(12px * var(--uiScale));font-weight:800;cursor:pointer;}
  .statsToggleBtn.active{background:rgba(86,154,255,.78);}

  /* popups */
  #mask{position:absolute;left:0;top:0;bottom:0;right:var(--sideW);background:rgba(0,0,0,.55);display:none;z-index:9000;}
  #modal{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(94%, calc(var(--pmW) - var(--sideW) - calc(80px * var(--uiScale))));max-height:min(84%, calc(var(--pmH) - calc(64px * var(--uiScale))));overflow:hidden;background:#1b1b1b;border:1px solid rgba(255,255,255,.15);border-radius:calc(16px * var(--uiScale));padding:calc(12px * var(--uiScale));box-shadow:0 calc(14px * var(--uiScale)) calc(60px * var(--uiScale)) rgba(0,0,0,.7);display:flex;flex-direction:column;font-size:calc(16px * var(--uiScale));}
  #modalTitle{font-weight:700;flex:0 0 auto;font-size:calc(20px * var(--uiScale));line-height:1.25;}
  #modalMain{display:flex;gap:calc(16px * var(--uiScale));flex:1 1 auto;min-height:0;overflow:hidden;margin-top:calc(10px * var(--uiScale));}
  #modalLead{display:none;flex:0 0 calc(160px * var(--uiScale));max-width:calc(160px * var(--uiScale));min-width:calc(160px * var(--uiScale));flex-direction:column;gap:calc(8px * var(--uiScale));align-items:flex-start;}
  #modalLead.visible{display:flex;}
  #modalCond{display:none;margin:calc(6px * var(--uiScale)) 0 calc(8px * var(--uiScale)) 0;padding:calc(8px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:calc(10px * var(--uiScale));font-size:calc(12px * var(--uiScale));line-height:1.45;border:1px solid rgba(255,255,255,.14);}
  #modalCond.condMet{display:block;background:rgba(30,120,60,.18);color:#b8f3c7;border-color:rgba(90,220,130,.45);}
  #modalCond.condUnmet{display:block;background:rgba(140,40,40,.18);color:#ffbcbc;border-color:rgba(255,110,110,.45);}
  #modalCond.condNeutral{display:block;background:rgba(255,255,255,.06);color:#ddd;border-color:rgba(255,255,255,.18);}
  #modalCardTextWrap{display:none;margin:calc(2px * var(--uiScale)) 0 calc(10px * var(--uiScale)) 0;padding:calc(10px * var(--uiScale)) calc(12px * var(--uiScale));border-radius:calc(10px * var(--uiScale));background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);}
  #modalCardTextWrap.visible{display:block;}
  #modalCardTextTitle{font-size:calc(11px * var(--uiScale));font-weight:bold;letter-spacing:.04em;color:#bbb;margin-bottom:calc(6px * var(--uiScale));}
  #modalCardText{font-size:calc(12px * var(--uiScale));color:#ddd;line-height:1.55;white-space:pre-wrap;max-height:calc(220px * var(--uiScale));overflow:auto;}
  #modalSourceCard{width:calc(150px * var(--uiScale));min-width:calc(150px * var(--uiScale));}
  #modalSourceCard img{display:block;width:calc(150px * var(--uiScale));height:auto;max-height:calc(220px * var(--uiScale));object-fit:cover;border-radius:calc(12px * var(--uiScale));border:1px solid rgba(255,255,255,.14);box-shadow:0 calc(8px * var(--uiScale)) calc(24px * var(--uiScale)) rgba(0,0,0,.35);}
  #modalSourceName{width:calc(150px * var(--uiScale));font-weight:700;color:#fff;font-size:calc(13px * var(--uiScale));line-height:1.35;white-space:normal;word-break:break-word;}
  #modalSourceMeta{width:calc(150px * var(--uiScale));font-size:calc(11px * var(--uiScale));color:#aaa;line-height:1.35;white-space:pre-wrap;}
  #modalContent{display:flex;flex-direction:column;flex:1 1 auto;min-width:0;min-height:0;overflow:hidden;}
  #modalText{white-space:pre-wrap;line-height:1.45;color:#ddd;font-size:calc(13px * var(--uiScale));margin-top:0;flex:0 0 auto;}
  .yellRevealDrawNotice{display:inline-flex;align-items:center;gap:calc(7px * var(--uiScale));margin-top:calc(6px * var(--uiScale));padding:calc(4px * var(--uiScale)) calc(8px * var(--uiScale));border-radius:999px;background:rgba(92,200,255,.12);border:1px solid rgba(92,200,255,.42);color:#dff7ff;font-size:calc(12px * var(--uiScale));font-weight:800;line-height:1.15;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .yellRevealDrawNotice .tag{background:rgba(92,200,255,.86);color:#061018;border-radius:999px;padding:calc(2px * var(--uiScale)) calc(6px * var(--uiScale));font-size:calc(10px * var(--uiScale));font-weight:900;letter-spacing:.05em;flex:0 0 auto;}
  .yellRevealSummary{display:flex;flex-direction:column;gap:calc(8px * var(--uiScale));padding:calc(2px * var(--uiScale)) 0 calc(6px * var(--uiScale)) 0;}
  .yellRevealSection{display:flex;flex-direction:column;gap:calc(6px * var(--uiScale));padding:calc(7px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:calc(12px * var(--uiScale));background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);}
  .yellRevealSectionTitle{font-size:calc(13px * var(--uiScale));font-weight:900;letter-spacing:.04em;color:#f1f1f1;}
  .yellRevealHeartGrid{display:grid;grid-template-columns:repeat(8,minmax(calc(58px * var(--uiScale)),1fr));gap:calc(6px * var(--uiScale));}
  .yellRevealHeartGrid.withAny{grid-template-columns:repeat(8,minmax(calc(58px * var(--uiScale)),1fr));}
  .yellRevealMetric{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:calc(3px * var(--uiScale));min-height:calc(88px * var(--uiScale));padding:calc(8px * var(--uiScale)) calc(6px * var(--uiScale));border-radius:calc(12px * var(--uiScale));background:rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.12);text-align:center;}
  .yellRevealMetricLabel{display:inline-flex;align-items:center;justify-content:center;gap:calc(6px * var(--uiScale));font-size:calc(15px * var(--uiScale));font-weight:800;color:#eee;line-height:1.1;min-width:0;}
  .yellRevealMetricLabel img{width:1.45em !important;height:1.45em !important;}
  .yellRevealMetricCount{font-size:calc(34px * var(--uiScale));font-weight:900;line-height:1;color:#fff;}
  .yellRevealMetricSub{font-size:calc(11px * var(--uiScale));color:#bbb;line-height:1.15;}
  .yellRevealIconGrid{display:grid;grid-template-columns:repeat(4,minmax(calc(92px * var(--uiScale)),1fr));gap:calc(6px * var(--uiScale));align-items:stretch;width:100%;padding:0;box-sizing:border-box;}
  .yellRevealIconMetric{display:grid;grid-template-columns:minmax(0,max-content) max-content;justify-content:center;column-gap:calc(7px * var(--uiScale));align-items:center;min-height:calc(50px * var(--uiScale));padding:calc(5px * var(--uiScale)) calc(8px * var(--uiScale));border-radius:calc(12px * var(--uiScale));background:rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.12);box-sizing:border-box;}
  .yellRevealIconMetricLabel{display:flex;align-items:center;justify-content:flex-start;text-align:left;min-width:0;font-size:calc(14px * var(--uiScale));font-weight:800;color:#f2f2f2;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .yellRevealIconMetricValue{display:flex;align-items:center;justify-content:center;text-align:center;min-width:calc(30px * var(--uiScale));font-size:calc(28px * var(--uiScale));font-weight:900;color:#fff;line-height:1;font-family:inherit;font-variant-numeric:tabular-nums;}
  .yellRevealCardRow{display:flex;flex-wrap:nowrap;gap:calc(10px * var(--uiScale));align-items:flex-start;justify-content:flex-start;min-height:calc(228px * var(--uiScale));overflow-x:auto;overflow-y:hidden;padding-bottom:calc(4px * var(--uiScale));}
  .yellRevealCardRow::-webkit-scrollbar{height:calc(10px * var(--uiScale));}
  .yellRevealCardRow::-webkit-scrollbar-thumb{background:rgba(255,255,255,.16);border-radius:999px;}

  .liveAttemptSummary{display:flex;flex-direction:column;gap:calc(10px * var(--uiScale));width:min(calc(980px * var(--uiScale)),92vw);max-width:100%;box-sizing:border-box;}
  .liveAttemptTop{display:flex;align-items:center;justify-content:space-between;gap:calc(12px * var(--uiScale));flex-wrap:wrap;padding:calc(9px * var(--uiScale)) calc(12px * var(--uiScale));border-radius:calc(12px * var(--uiScale));background:rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.12);}
  .liveAttemptResult{font-size:calc(22px * var(--uiScale));font-weight:900;letter-spacing:.04em;padding:calc(7px * var(--uiScale)) calc(13px * var(--uiScale));border-radius:999px;border:1px solid rgba(255,255,255,.18);}
  .liveAttemptResult.success{background:rgba(55,190,120,.22);color:#d9ffe8;}
  .liveAttemptResult.fail{background:rgba(230,80,85,.22);color:#ffe0e2;}
  .liveAttemptScore{font-size:calc(18px * var(--uiScale));font-weight:800;color:#fff;}
  .liveAttemptNote{font-size:calc(12px * var(--uiScale));color:#bbb;line-height:1.35;}
  .liveAttemptSection{display:flex;flex-direction:column;gap:calc(6px * var(--uiScale));padding:calc(7px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:calc(12px * var(--uiScale));background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);}
  .liveAttemptSectionTitle{font-size:calc(13px * var(--uiScale));font-weight:900;letter-spacing:.04em;color:#f1f1f1;}
  .liveAttemptHeartGrid{display:grid;grid-template-columns:repeat(8,minmax(0,1fr)) minmax(calc(92px * var(--uiScale)),.82fr);gap:calc(7px * var(--uiScale));width:100%;align-items:stretch;}
  .liveAttemptSummary .yellRevealMetric{min-width:0;min-height:calc(76px * var(--uiScale));padding-left:calc(5px * var(--uiScale));padding-right:calc(5px * var(--uiScale));}
  .liveAttemptSummary .yellRevealMetricLabel{font-size:calc(15px * var(--uiScale));}
  .liveAttemptSummary .yellRevealMetricCount{font-size:calc(28px * var(--uiScale));font-variant-numeric:tabular-nums;}
  .liveAttemptSummary .yellRevealMetricSub{min-height:calc(13px * var(--uiScale));}
  .liveAttemptHeartTotal{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:calc(3px * var(--uiScale));min-width:0;min-height:calc(76px * var(--uiScale));padding:calc(6px * var(--uiScale));border-radius:calc(12px * var(--uiScale));box-sizing:border-box;background:linear-gradient(135deg,rgba(255,213,74,.20),rgba(255,255,255,.055));border:2px solid rgba(255,213,74,.72);box-shadow:inset 0 0 0 1px rgba(0,0,0,.24),0 0 calc(14px * var(--uiScale)) rgba(255,213,74,.08);}
  .liveAttemptHeartTotalLabel{display:flex;align-items:center;gap:calc(5px * var(--uiScale));font-size:calc(14px * var(--uiScale));font-weight:900;letter-spacing:.06em;color:#ffe89a;line-height:1;white-space:nowrap;}
  .liveAttemptHeartTotalMark{display:inline-flex;align-items:center;justify-content:center;width:calc(20px * var(--uiScale));height:calc(20px * var(--uiScale));border-radius:999px;background:rgba(255,213,74,.20);border:1px solid rgba(255,213,74,.58);font-size:calc(13px * var(--uiScale));font-weight:900;color:#fff3bd;}
  .liveAttemptHeartTotalCount{font-size:calc(34px * var(--uiScale));font-weight:950;line-height:1;color:#fff;font-variant-numeric:tabular-nums;}
  .liveAttemptHeartTotalSub{font-size:calc(10px * var(--uiScale));font-weight:800;color:#d8c98d;line-height:1;white-space:nowrap;}
  .yellRevealCardRow .cardWrap{position:relative !important;left:auto !important;top:auto !important;flex:0 0 auto;}
  .heartChoiceGrid{display:grid;gap:calc(10px * var(--uiScale));align-items:stretch;justify-content:center;margin:0 auto;max-width:min(78vw, calc(980px * var(--uiScale)));width:100%;}
  #modalCards{margin-top:calc(10px * var(--uiScale));overflow-x:auto;overflow-y:auto;padding-bottom:calc(6px * var(--uiScale));flex:1 1 auto;min-height:0;overscroll-behavior:contain;}
  #modalCards .surf{position:relative;height:1px;}
  #modalCards .broadCardListSurf,
  #viewerCards .broadCardListSurf{position:relative;height:1px;min-height:calc(92px * var(--uiScale));}
  #modalActions{display:flex;gap:calc(8px * var(--uiScale));justify-content:flex-end;margin-top:calc(10px * var(--uiScale));flex-wrap:wrap;flex:0 0 auto;}
  #modalActions .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:calc(6px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:calc(10px * var(--uiScale));font-size:calc(13px * var(--uiScale));cursor:pointer;}
  #popupPeekBtn{position:absolute;right:calc(6px * var(--uiScale));top:calc(6px * var(--uiScale));z-index:9800;display:none;align-items:center;gap:calc(6px * var(--uiScale));padding:calc(7px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:999px;border:1px solid rgba(255,255,255,.20);background:rgba(0,0,0,.68);color:#eee;font-size:calc(12px * var(--uiScale));font-weight:700;cursor:pointer;box-shadow:0 calc(6px * var(--uiScale)) calc(20px * var(--uiScale)) rgba(0,0,0,.35);}
  #popupPeekBtn:hover{background:rgba(40,40,40,.86);}
  #popupPeekBtn.active{display:flex;background:#ffd54a;color:#111;border-color:rgba(0,0,0,.35);}
  #popupPeekBtn.inspecting{display:flex;background:rgba(80,180,255,.85);color:#fff;border-color:rgba(255,255,255,.28);}
  .popupPeekHidden{visibility:hidden !important;pointer-events:none !important;}
  /* secondary inspect popup (can coexist with pending/effect popup) */
  #viewerLayer{position:absolute;inset:0;display:none;z-index:9200;pointer-events:none;}
  #viewerModal{position:absolute;right:calc(18px * var(--uiScale));top:calc(74px * var(--uiScale));width:min(46%, calc(560px * var(--uiScale)));max-height:min(74%, calc(var(--pmH) - calc(120px * var(--uiScale))));overflow:hidden;background:#1b1b1b;border:1px solid rgba(255,255,255,.15);border-radius:calc(16px * var(--uiScale));padding:calc(12px * var(--uiScale));box-shadow:0 calc(14px * var(--uiScale)) calc(60px * var(--uiScale)) rgba(0,0,0,.72);display:flex;flex-direction:column;pointer-events:auto;font-size:calc(16px * var(--uiScale));}
  #viewerHeader{display:flex;align-items:center;justify-content:space-between;gap:12px;flex:0 0 auto;}
  #viewerTitle{font-weight:700;min-width:0;}
  #viewerClose{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:10px;cursor:pointer;}
  #viewerText{white-space:pre-wrap;line-height:1.45;color:#ddd;font-size:calc(13px * var(--uiScale));margin-top:calc(10px * var(--uiScale));flex:0 0 auto;}
  #viewerCards{margin-top:10px;overflow-x:auto;overflow-y:auto;padding-bottom:6px;flex:1 1 auto;min-height:0;overscroll-behavior:contain;}
  #viewerCards .surf{position:relative;height:1px;}
  #viewerActions{display:flex;gap:8px;justify-content:flex-end;margin-top:10px;flex-wrap:wrap;flex:0 0 auto;}
  #viewerActions .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:calc(6px * var(--uiScale)) calc(10px * var(--uiScale));border-radius:calc(10px * var(--uiScale));font-size:calc(13px * var(--uiScale));cursor:pointer;}
/* UI_FIX_PENDING_CARD_CHOICES */
  /* pending card choice list (image buttons) */
  .choiceRow{display:inline-flex;gap:calc(8px * var(--uiScale));align-items:flex-start;overflow-x:auto;overflow-y:hidden;max-width:min(72vw, calc(1060px * var(--uiScale)));padding:calc(6px * var(--uiScale)) calc(2px * var(--uiScale)) calc(10px * var(--uiScale)) calc(2px * var(--uiScale));}
  .choiceBtn{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);border-radius:12px;padding:0;cursor:pointer;position:relative;flex:0 0 auto;box-shadow:0 6px 16px rgba(0,0,0,.35);}
  .choiceBtn:hover{outline:3px solid rgba(255,255,255,.22);outline-offset:-3px;}
  .choiceBtn.orderedSelected{outline:5px solid #ffe066;outline-offset:-5px;box-shadow:0 0 0 3px rgba(0,0,0,.65),0 0 22px rgba(255,224,102,.95),0 8px 20px rgba(0,0,0,.45);}
  .choiceBtn img{width:100%;height:100%;object-fit:cover;display:block;border-radius:12px;}
  .choiceCap{position:absolute;left:0;right:0;bottom:0;font-size:calc(11px * var(--uiScale));padding:calc(4px * var(--uiScale)) calc(6px * var(--uiScale));background:linear-gradient(to top, rgba(0,0,0,.65), rgba(0,0,0,.05));color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6);border-bottom-left-radius:calc(12px * var(--uiScale));border-bottom-right-radius:calc(12px * var(--uiScale));white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .choiceBtn.orderedSelected .choiceCap{font-size:13px;font-weight:900;background:linear-gradient(to top, rgba(0,0,0,.92), rgba(0,0,0,.35));color:#ffe066;text-shadow:0 2px 3px rgba(0,0,0,.95);}
  .orderBadge{position:absolute;left:calc(6px * var(--uiScale));top:calc(6px * var(--uiScale));display:none;align-items:center;justify-content:center;min-width:calc(28px * var(--uiScale));height:calc(28px * var(--uiScale));padding:0 calc(6px * var(--uiScale));border-radius:999px;background:#ffe066;color:#111;font-size:calc(17px * var(--uiScale));font-weight:900;line-height:1;border:2px solid #111;box-shadow:0 0 0 2px rgba(255,255,255,.92),0 3px 9px rgba(0,0,0,.72);z-index:4;pointer-events:none;}
  .choiceBtn.orderedSelected .orderBadge{display:flex;}
  /* BUILD_TAG: responsive_ui_scale_20260701ak */
  /* Additional responsive popup/chrome sizing. Existing inline popup UIs should prefer uiCalc(px). */
  .effectChoiceBtn{border-radius:calc(12px * var(--uiScale));padding:calc(10px * var(--uiScale)) calc(12px * var(--uiScale));gap:calc(10px * var(--uiScale));font-size:calc(13px * var(--uiScale));}
  .effectChoiceBullet{font-size:calc(12px * var(--uiScale));}
  .effectChoiceText{font-size:calc(13px * var(--uiScale));}
  .effectChoiceMeta{font-size:calc(11px * var(--uiScale));}
  .miniBtn{font-size:calc(13px * var(--uiScale));}
  .choiceTile{display:flex;flex-direction:column;align-items:stretch;gap:6px;flex:0 0 auto;max-width:240px;}
  /* effect-mode choices: text choices, not card-list tiles */
  .effectChoiceList{display:flex;flex-direction:column;gap:8px;max-width:min(76vw, 920px);padding:4px 2px 8px 2px;}
  .effectChoiceBtn{display:grid;grid-template-columns:2.2em 1fr;align-items:start;gap:10px;width:100%;text-align:left;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.065);color:#eee;border-radius:12px;padding:10px 12px;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.28);}
  .effectChoiceBtn:hover{background:rgba(255,255,255,.10);outline:2px solid rgba(255,255,255,.20);outline-offset:-2px;}
  .effectChoiceBullet{display:inline-flex;align-items:center;justify-content:center;width:1.8em;height:1.8em;border-radius:999px;background:rgba(255,255,255,.14);color:#fff;font-weight:800;font-size:12px;line-height:1;margin-top:0.05em;}
  .effectChoiceText{white-space:pre-wrap;line-height:1.55;font-size:13px;color:#f1f1f1;}
  .effectChoiceMeta{margin-top:6px;color:#aaa;font-size:11px;line-height:1.3;}
  .massInlineCount{display:inline-block;padding:0 4px;margin:0 1px;border-radius:5px;background:rgba(255,224,102,.15);color:#ffe68a;font-weight:800;box-shadow:inset 0 -1px 0 rgba(255,224,102,.38);}
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


  /* BUILD_TAG: responsive_ui_scale_full_chrome_20260701al */
  /* Final responsive overrides. Some legacy rules below/above used fixed px and
     overrode the earlier scaled declarations. Keep all chrome/popup parts tied
     to --uiScale so resizing the window changes cards, text and controls together. */
  #publicViewBadge{
    padding:calc(6px * var(--uiScale)) calc(10px * var(--uiScale)) !important;
    font-size:calc(12px * var(--uiScale)) !important;
  }
  .publicPendingNote{
    margin-top:calc(10px * var(--uiScale)) !important;
    padding:calc(10px * var(--uiScale)) calc(12px * var(--uiScale)) !important;
    border-radius:calc(10px * var(--uiScale)) !important;
    font-size:calc(13px * var(--uiScale)) !important;
  }
  .publicKnownHandPanel{
    right:calc(var(--sideW) + calc(14px * var(--uiScale))) !important;
    bottom:calc(18px * var(--uiScale)) !important;
    gap:calc(8px * var(--uiScale)) !important;
    padding:calc(9px * var(--uiScale)) calc(10px * var(--uiScale)) calc(10px * var(--uiScale)) !important;
    border-radius:calc(12px * var(--uiScale)) !important;
  }
  .publicKnownHandPanel .publicKnownTitle{font-size:calc(12px * var(--uiScale)) !important;}
  .publicRevealFloat{
    padding:calc(12px * var(--uiScale)) calc(16px * var(--uiScale)) !important;
    border-radius:calc(16px * var(--uiScale)) !important;
    gap:calc(12px * var(--uiScale)) !important;
    box-shadow:0 calc(10px * var(--uiScale)) calc(30px * var(--uiScale)) rgba(0,0,0,.62),0 0 calc(28px * var(--uiScale)) rgba(255,216,77,.38) !important;
  }
  .publicRevealFloatTitle{font-size:calc(16px * var(--uiScale)) !important;}
  #topBar .oppWaitPill{gap:calc(6px * var(--uiScale)) !important;}
  #topBar .oppWaitBtn{
    min-width:calc(24px * var(--uiScale)) !important;
    height:calc(22px * var(--uiScale)) !important;
    padding:0 calc(7px * var(--uiScale)) !important;
    line-height:calc(18px * var(--uiScale)) !important;
    font-size:calc(13px * var(--uiScale)) !important;
  }
  #topBar .turnOrderBtn{min-width:calc(42px * var(--uiScale)) !important;}
  #logBox{
    font-size:calc(12px * var(--uiScale)) !important;
    padding:calc(8px * var(--uiScale)) !important;
    border-radius:calc(10px * var(--uiScale)) !important;
    gap:calc(6px * var(--uiScale)) !important;
  }
  #effectLogPanel{
    max-height:calc(96px * var(--uiScale)) !important;
    padding:calc(6px * var(--uiScale)) calc(7px * var(--uiScale)) !important;
    border-radius:calc(8px * var(--uiScale)) !important;
  }
  .effectLogHeader{font-size:calc(10px * var(--uiScale)) !important;margin-bottom:calc(4px * var(--uiScale)) !important;}
  .effectLogHint,.effectLogType{font-size:calc(10px * var(--uiScale)) !important;}
  .effectLogBody{font-size:calc(11px * var(--uiScale)) !important;}
  #viewerHeader{gap:calc(12px * var(--uiScale)) !important;}
  #viewerTitle{font-size:calc(16px * var(--uiScale)) !important;}
  #viewerClose{
    padding:calc(6px * var(--uiScale)) calc(10px * var(--uiScale)) !important;
    border-radius:calc(10px * var(--uiScale)) !important;
    font-size:calc(13px * var(--uiScale)) !important;
  }
  #viewerCards{margin-top:calc(10px * var(--uiScale)) !important;padding-bottom:calc(6px * var(--uiScale)) !important;}
  #viewerActions{gap:calc(8px * var(--uiScale)) !important;margin-top:calc(10px * var(--uiScale)) !important;}
  #modal button, #viewerModal button, #topBar button, #resetPanel button, .energyUI button, #popupPeekBtn{
    font-size:calc(13px * var(--uiScale)) !important;
  }
  #modalActions .miniBtn, .miniBtn, .energyUI .btn{
    padding:calc(6px * var(--uiScale)) calc(10px * var(--uiScale)) !important;
    border-radius:calc(10px * var(--uiScale)) !important;
  }
  .energyUI .btn.primary{font-size:calc(13px * var(--uiScale)) !important;}
  /* BUILD_TAG: energy_undo_next_large_touch_targets_20260701am */
  .energyUI .btn{
    min-height:calc(54px * var(--uiScale)) !important;
    padding:calc(16px * var(--uiScale)) calc(10px * var(--uiScale)) !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    line-height:1.15 !important;
    font-weight:800 !important;
  }
  .energyUI .energyText div{font-size:calc(12px * var(--uiScale)) !important;margin-top:calc(2px * var(--uiScale)) !important;}
  .choiceTile{gap:calc(6px * var(--uiScale)) !important;max-width:calc(240px * var(--uiScale)) !important;}
  .choiceBtn{
    border-radius:calc(12px * var(--uiScale)) !important;
    box-shadow:0 calc(6px * var(--uiScale)) calc(16px * var(--uiScale)) rgba(0,0,0,.35) !important;
  }
  .choiceBtn img{border-radius:calc(12px * var(--uiScale)) !important;}
  .choiceBtn.orderedSelected .choiceCap{font-size:calc(13px * var(--uiScale)) !important;}
  .effectChoiceList{
    gap:calc(8px * var(--uiScale)) !important;
    max-width:min(76vw, calc(920px * var(--uiScale))) !important;
    padding:calc(4px * var(--uiScale)) calc(2px * var(--uiScale)) calc(8px * var(--uiScale)) calc(2px * var(--uiScale)) !important;
  }
  .effectChoiceBtn{
    grid-template-columns:calc(28px * var(--uiScale)) 1fr !important;
    gap:calc(10px * var(--uiScale)) !important;
    border-radius:calc(12px * var(--uiScale)) !important;
    padding:calc(10px * var(--uiScale)) calc(12px * var(--uiScale)) !important;
    box-shadow:0 calc(4px * var(--uiScale)) calc(14px * var(--uiScale)) rgba(0,0,0,.28) !important;
  }
  .effectChoiceBullet{
    width:calc(22px * var(--uiScale)) !important;
    height:calc(22px * var(--uiScale)) !important;
    font-size:calc(12px * var(--uiScale)) !important;
  }
  .effectChoiceText{font-size:calc(13px * var(--uiScale)) !important;}
  .effectChoiceMeta{margin-top:calc(6px * var(--uiScale)) !important;font-size:calc(11px * var(--uiScale)) !important;}
  .massInlineCount{padding:0 calc(4px * var(--uiScale)) !important;margin:0 calc(1px * var(--uiScale)) !important;border-radius:calc(5px * var(--uiScale)) !important;}
  .reorderHint{font-size:calc(12px * var(--uiScale)) !important;margin-bottom:calc(6px * var(--uiScale)) !important;gap:calc(6px * var(--uiScale)) !important;}
  .reorderHint .arrow{font-size:calc(16px * var(--uiScale)) !important;}
  .reorderRow{gap:calc(10px * var(--uiScale)) !important;padding:calc(8px * var(--uiScale)) calc(4px * var(--uiScale)) calc(12px * var(--uiScale)) calc(4px * var(--uiScale)) !important;min-height:calc(60px * var(--uiScale)) !important;}
  .reorderCard{border-radius:calc(12px * var(--uiScale)) !important;box-shadow:0 calc(6px * var(--uiScale)) calc(18px * var(--uiScale)) rgba(0,0,0,.4) !important;}
  .reorderCard .idxBadge{top:calc(4px * var(--uiScale)) !important;left:calc(4px * var(--uiScale)) !important;font-size:calc(11px * var(--uiScale)) !important;padding:calc(2px * var(--uiScale)) calc(6px * var(--uiScale)) !important;border-radius:calc(6px * var(--uiScale)) !important;}
  .reorderCard .cnCap{font-size:calc(10px * var(--uiScale)) !important;padding:calc(3px * var(--uiScale)) calc(5px * var(--uiScale)) !important;border-bottom-left-radius:calc(10px * var(--uiScale)) !important;border-bottom-right-radius:calc(10px * var(--uiScale)) !important;}
  #cardDetail{
    width:calc(340px * var(--uiScale)) !important;
    max-height:min(80vh, calc(var(--pmH) - calc(32px * var(--uiScale)))) !important;
    border-radius:calc(14px * var(--uiScale)) !important;
    box-shadow:0 calc(16px * var(--uiScale)) calc(60px * var(--uiScale)) rgba(0,0,0,.75) !important;
  }
  #cdImgWrap{width:calc(132px * var(--uiScale)) !important;min-width:calc(132px * var(--uiScale)) !important;}
  #cdBody{padding:calc(12px * var(--uiScale)) calc(14px * var(--uiScale)) !important;gap:calc(8px * var(--uiScale)) !important;}
  #cdTitle{font-size:calc(15px * var(--uiScale)) !important;}
  #cdNo{font-size:calc(11px * var(--uiScale)) !important;}
  #cdMeta{gap:calc(4px * var(--uiScale)) !important;}
  #cdMeta span{padding:calc(2px * var(--uiScale)) calc(7px * var(--uiScale)) !important;border-radius:calc(6px * var(--uiScale)) !important;font-size:calc(11px * var(--uiScale)) !important;}
  #cdAbilities{font-size:calc(12px * var(--uiScale)) !important;}

  /* BUILD_TAG: card_detail_responsive_scale_20260701ap */
  #cardDetail{
    width:calc(340px * var(--uiScale)) !important;
    max-width:min(92vw, calc(520px * var(--uiScale))) !important;
    max-height:min(80vh, calc(var(--pmH) - calc(32px * var(--uiScale)))) !important;
    border-radius:calc(14px * var(--uiScale)) !important;
    box-shadow:0 calc(16px * var(--uiScale)) calc(60px * var(--uiScale)) rgba(0,0,0,.75) !important;
  }
  .underInspectBtn{position:absolute;left:calc(8px * var(--uiScale));right:calc(8px * var(--uiScale));bottom:calc(8px * var(--uiScale));z-index:95;border:1px solid rgba(255,255,255,.24);border-radius:calc(10px * var(--uiScale));background:rgba(18,24,34,.82);color:#fff;padding:calc(5px * var(--uiScale)) calc(7px * var(--uiScale));font-size:calc(11px * var(--uiScale));font-weight:900;line-height:1.1;cursor:pointer;box-shadow:0 calc(3px * var(--uiScale)) calc(10px * var(--uiScale)) rgba(0,0,0,.42);}
  .underInspectBtn:hover{background:rgba(42,58,82,.94);}
  .underInspectBtn.stageOutside{left:auto;right:auto;bottom:auto;z-index:520;min-width:calc(92px * var(--uiScale));padding:calc(4px * var(--uiScale)) calc(7px * var(--uiScale));font-size:calc(10px * var(--uiScale));}
  .debugMoveSource{box-shadow:0 0 0 calc(4px * var(--uiScale)) rgba(255,218,98,.96),0 calc(6px * var(--uiScale)) calc(18px * var(--uiScale)) rgba(0,0,0,.55) !important;}
  .debugMoveTarget{outline:calc(2px * var(--uiScale)) solid rgba(255,218,98,.65);outline-offset:calc(-3px * var(--uiScale));}
  .debugCardListRow{display:flex;gap:calc(6px * var(--uiScale));align-items:center;margin-top:calc(8px * var(--uiScale));flex-wrap:wrap;}
  .debugCardListRow .miniBtn{font-size:calc(11px * var(--uiScale)) !important;padding:calc(4px * var(--uiScale)) calc(7px * var(--uiScale)) !important;}
  #cdImg{width:calc(140px * var(--uiScale)) !important;min-width:calc(140px * var(--uiScale)) !important;}
  #cdImg img{border-radius:calc(14px * var(--uiScale)) 0 0 calc(14px * var(--uiScale)) !important;}
  #cdBody{padding:calc(12px * var(--uiScale)) calc(14px * var(--uiScale)) !important;gap:calc(8px * var(--uiScale)) !important;}
  #cdName{font-size:calc(14px * var(--uiScale)) !important;line-height:1.3 !important;}
  #cdMeta{gap:calc(4px * var(--uiScale)) !important;}
  #cdMeta span{padding:calc(2px * var(--uiScale)) calc(7px * var(--uiScale)) !important;border-radius:calc(6px * var(--uiScale)) !important;font-size:calc(11px * var(--uiScale)) !important;}
  #cdAbilities{font-size:calc(11px * var(--uiScale)) !important;line-height:1.55 !important;}
  #cdClose{top:calc(6px * var(--uiScale)) !important;right:calc(8px * var(--uiScale)) !important;width:calc(22px * var(--uiScale)) !important;height:calc(22px * var(--uiScale)) !important;font-size:calc(13px * var(--uiScale)) !important;}

  @media (max-aspect-ratio: 4/3), (max-width: 900px) {
    #modal{
      width:min(96%, calc(var(--pmW) - calc(28px * var(--uiScale)))) !important;
      max-height:min(88%, calc(var(--pmH) - calc(42px * var(--uiScale)))) !important;
    }
    #modalMain{gap:calc(10px * var(--uiScale)) !important;}
    #modalLead.visible{
      flex-basis:calc(118px * var(--uiScale)) !important;
      min-width:calc(118px * var(--uiScale)) !important;
      max-width:calc(118px * var(--uiScale)) !important;
    }
    #modalSourceCard,
    #modalSourceName,
    #modalSourceMeta{width:calc(112px * var(--uiScale)) !important;min-width:calc(112px * var(--uiScale)) !important;}
    #modalSourceCard img{width:calc(112px * var(--uiScale)) !important;max-height:calc(166px * var(--uiScale)) !important;}
    #viewerModal{
      right:calc(10px * var(--uiScale)) !important;
      top:calc(64px * var(--uiScale)) !important;
      width:min(62%, calc(620px * var(--uiScale))) !important;
      max-height:min(78%, calc(var(--pmH) - calc(94px * var(--uiScale)))) !important;
    }
  }


</style>
</head>
<body>
<div id="root">
  <div id="pmWrap">
    <img id="playmat" src="/playmat" alt="playmat"/>

    <div id="topBar">
      <div id="publicViewBadge">PUBLIC VIEW / READ ONLY</div>
      <div class="pill">Turn: <b id="turn">?</b> | Phase: <b id="phase">?</b> | Energy: <b id="energy">?</b></div>
      <div class="pill oppWaitPill">Opponent wait: <b id="opponentWait">0</b>/3 <button class="oppWaitBtn" id="btnOppWaitMinus" title="相手ウェイト人数を減らす">−</button><button class="oppWaitBtn" id="btnOppWaitPlus" title="相手ウェイト人数を増やす">＋</button></div>
      <div class="pill oppWaitPill">Opp success: <b id="opponentSuccess">0</b>/2 <button class="oppWaitBtn" id="btnOppSuccessMinus" title="相手成功置き場枚数を減らす">−</button><button class="oppWaitBtn" id="btnOppSuccessPlus" title="相手成功置き場枚数を増やす">＋</button></div>
      <div class="pill oppWaitPill"><button class="oppWaitBtn turnOrderBtn" id="btnOrderFirst" title="現在ターンを先手扱いにする">先手</button><button class="oppWaitBtn turnOrderBtn" id="btnOrderSecond" title="現在ターンを後手扱いにする">後手</button></div>
      <div class="pill">Selected(hand): <b id="selected">0</b></div>
      <button class="miniBtn" id="btnSuspendSave">中断保存</button>
      <button class="miniBtn" id="btnSuspendLoad">再開読込</button>
      <input id="suspendFileInput" type="file" accept="application/json,.json" hidden>
      <button class="miniBtn" id="btnDbg">枠表示</button>
      <button class="miniBtn debugMoveBtn" id="btnDebugMove">デバッグモード OFF</button>
    </div>

    <div id="resetPanel" aria-label="リセット操作">
      <span class="resetPanelTitle">RESET</span>
      <button id="btnSingleReset" type="button">リセット</button>
      <button id="btnRecordWin" type="button">勝ち記録</button>
      <button id="btnRecordLose" type="button">負け記録</button>
      <button id="btnRecordNoGame" type="button">No Game</button>
    </div>

    <div id="banner"></div>

    <div id="zones"></div>

    <button id="popupPeekBtn" title="ポップアップを一時的に隠して盤面を確認">🙈 盤面確認</button>

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
            <div id="modalCond"></div>
            <div id="modalCardTextWrap">
              <div id="modalCardTextTitle">カードテキスト</div>
              <div id="modalCardText"></div>
            </div>
            <div id="modalCards"></div>
            <div id="modalActions"></div>
          </div>
        </div>
      </div>
    </div>

    <div id="viewerLayer">
      <div id="viewerModal">
        <div id="viewerHeader">
          <div id="viewerTitle">カード一覧</div>
          <button id="viewerClose">Close</button>
        </div>
        <div id="viewerText"></div>
        <div id="viewerCards"></div>
        <div id="viewerActions"></div>
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
  // BUILD_TAG: public_refresh_notice_client_version_reload_20260701ar
  // If a public window was left open across a local patch/restart, it may keep
  // running stale JS.  Compare the state ui_version and reload once when the
  // server-side bundle changes, so public refresh notices use the current modal
  // layout and owner-OK synchronization.
  const CLIENT_UI_VERSION = '__LOVECA_APP_VERSION__';
  let clientReloadingForVersion = false;
  const urlParams = new URLSearchParams(window.location.search || '');
  const VIEW_MODE = String(urlParams.get('view') || (window.location.pathname === '/public' ? 'public' : 'private')).toLowerCase();
  const IS_PUBLIC_VIEW = (VIEW_MODE === 'public');
  if(IS_PUBLIC_VIEW){ document.body.classList.add('publicView'); }

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

      hand:    {x:  390, y: 600, w: 835, h: 235, kind:"hand",    orient:"portrait",  label:"HAND"},
      log:     {x:    8, y: 585, w: 240, h: 235, kind:"log",     orient:"portrait",  label:"LOG"},
    }
  };

  const elZones = document.getElementById('zones');
  const elTurn = document.getElementById('turn');
  const elPhase = document.getElementById('phase');
  const elEnergy = document.getElementById('energy');
  const elOpponentWait = document.getElementById('opponentWait');
  const btnOppWaitMinus = document.getElementById('btnOppWaitMinus');
  const btnOppWaitPlus = document.getElementById('btnOppWaitPlus');
  const elOpponentSuccess = document.getElementById('opponentSuccess');
  const btnOppSuccessMinus = document.getElementById('btnOppSuccessMinus');
  const btnOppSuccessPlus = document.getElementById('btnOppSuccessPlus');
  const elTurnOrder = document.getElementById('turnOrder');
  const btnOrderFirst = document.getElementById('btnOrderFirst');
  const btnOrderSecond = document.getElementById('btnOrderSecond');
  const elSelected = document.getElementById('selected');
  const elBanner = document.getElementById('banner');
  const elResetPanel = document.getElementById('resetPanel');
  const btnSingleReset = document.getElementById('btnSingleReset');
  const btnRecordWin = document.getElementById('btnRecordWin');
  const btnRecordLose = document.getElementById('btnRecordLose');
  const btnRecordNoGame = document.getElementById('btnRecordNoGame');

  async function adjustOpponentWait(delta){
    st = await apiCmd('opponent_wait_delta', {delta});
    selHand = [];
    updateTop();
    render();
  }
  if(btnOppWaitMinus){
    btnOppWaitMinus.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      await adjustOpponentWait(-1);
    });
  }
  if(btnOppWaitPlus){
    btnOppWaitPlus.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      await adjustOpponentWait(1);
    });
  }

  async function adjustOpponentSuccess(delta){
    st = await apiCmd('opponent_success_delta', {delta});
    selHand = [];
    updateTop();
    render();
  }
  async function setTurnOrder(value){
    st = await apiCmd('turn_order_set', {value});
    selHand = [];
    updateTop();
    render();
  }
  if(btnOppSuccessMinus){
    btnOppSuccessMinus.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      await adjustOpponentSuccess(-1);
    });
  }
  if(btnOppSuccessPlus){
    btnOppSuccessPlus.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      await adjustOpponentSuccess(1);
    });
  }
  if(btnOrderFirst){
    btnOrderFirst.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      await setTurnOrder('first');
    });
  }
  if(btnOrderSecond){
    btnOrderSecond.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      await setTurnOrder('second');
    });
  }

  async function handleResetPanelCommand(cmd, payload, message){
    if(IS_PUBLIC_VIEW) return;
    if(message && !window.confirm(message)) return;
    st = await apiCmd(cmd, payload || {});
    selHand = [];
    updateTop();
    render();
  }
  async function shutdownSimulatorWindow(){
    try{
      await requestJson('/cmd', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({cmd:'shutdown', payload:{}})
      });
    }catch(e){}
    try{ window.close(); }catch(e){}
  }
  async function handleRemoteRecordResult(result, label){
    if(IS_PUBLIC_VIEW) return;
    const choice = window.prompt(
      label + 'として記録します。次の操作を数字で選んでください。\n\n' +
      '1: 同じデッキでもう一度対戦を開始\n' +
      '2: デッキを変更する\n' +
      '3: シミュレータを終了する',
      '1'
    );
    if(choice === null) return;
    const picked = String(choice).trim();
    if(picked === '1'){
      await handleResetPanelCommand('record_reset', {result}, '');
      return;
    }
    if(picked === '2'){
      st = await apiCmd('record_result', {result});
      selHand = [];
      updateTop();
      render();
      window.alert('勝敗を記録しました。アプリのリモート対戦画面でデッキを選び直してください。');
      try{ window.close(); }catch(e){}
      return;
    }
    if(picked === '3'){
      await apiCmd('record_result', {result});
      await shutdownSimulatorWindow();
      return;
    }
    window.alert('1、2、3 のいずれかを入力してください。');
  }
  if(btnSingleReset){
    btnSingleReset.addEventListener('click', ev=>{
      ev.stopPropagation();
      handleResetPanelCommand('reset', {}, '現在の対戦をリセットします。よろしいですか？');
    });
  }
  if(btnRecordWin){
    btnRecordWin.addEventListener('click', ev=>{
      ev.stopPropagation();
      handleRemoteRecordResult('win', '勝利');
    });
  }
  if(btnRecordLose){
    btnRecordLose.addEventListener('click', ev=>{
      ev.stopPropagation();
      handleRemoteRecordResult('lose', '敗北');
    });
  }
  if(btnRecordNoGame){
    btnRecordNoGame.addEventListener('click', ev=>{
      ev.stopPropagation();
      handleRemoteRecordResult('no_game', 'No Game');
    });
  }

  const elMask = document.getElementById('mask');
  const elModal = document.getElementById('modal');
  const elModalTitle = document.getElementById('modalTitle');
  const elModalLead = document.getElementById('modalLead');
  const elModalSourceCard = document.getElementById('modalSourceCard');
  const elModalSourceName = document.getElementById('modalSourceName');
  const elModalSourceMeta = document.getElementById('modalSourceMeta');
  const elModalText = document.getElementById('modalText');
  const elModalCond = document.getElementById('modalCond');
  const elModalCardTextWrap = document.getElementById('modalCardTextWrap');
  const elModalCardTextTitle = document.getElementById('modalCardTextTitle');
  const elModalCardText = document.getElementById('modalCardText');
  const elModalCards = document.getElementById('modalCards');
  const elModalActions = document.getElementById('modalActions');
  const btnPopupPeek = document.getElementById('popupPeekBtn');

  function installHorizontalWheelScroll(element){
    if(!element) return;
    element.addEventListener('wheel', (ev)=>{
      const target = ev.target && ev.target.closest ? ev.target.closest('.choiceRow, #modalCards, #viewerCards') : element;
      const scroller = (target && target.scrollWidth > target.clientWidth) ? target : element;
      if(!scroller || scroller.scrollWidth <= scroller.clientWidth) return;
      const vertical = Math.abs(ev.deltaY || 0) >= Math.abs(ev.deltaX || 0);
      if(!vertical || !ev.deltaY) return;
      scroller.scrollLeft += ev.deltaY;
      ev.preventDefault();
    }, {passive:false});
  }
  installHorizontalWheelScroll(elModalCards);

  const elViewerLayer = document.getElementById('viewerLayer');
  const elViewerModal = document.getElementById('viewerModal');
  const elViewerTitle = document.getElementById('viewerTitle');
  const elViewerText = document.getElementById('viewerText');
  const elViewerCards = document.getElementById('viewerCards');
  const elViewerActions = document.getElementById('viewerActions');
  const elViewerClose = document.getElementById('viewerClose');
  installHorizontalWheelScroll(elViewerCards);

  const btnDbg = document.getElementById('btnDbg');
  const btnDebugMove = document.getElementById('btnDebugMove');
  const btnSuspendSave = document.getElementById('btnSuspendSave');
  const btnSuspendLoad = document.getElementById('btnSuspendLoad');
  const suspendFileInput = document.getElementById('suspendFileInput');

  let debug = false;
  let st = null;
  let selHand = []; // indices
  let statsVisible = false;
  let debugMoveMode = false;
  let debugMoveSelection = null;
  let debugMoveEnabledServerDebug = false;
  let popup = {type:null};
  let viewerPopup = {type:null};
  let popupsHiddenForInspect = false;
  let bannerTimer = null;
  let stdPortrait = null;
  let stdLandscape = null;

  // ── Card detail panel ──
  const elCardDetail  = document.getElementById('cardDetail');
  const elCdImg       = document.getElementById('cdImgEl');
  const elCdName      = document.getElementById('cdName');
  const elCdMeta      = document.getElementById('cdMeta');
  const elCdAbilities = document.getElementById('cdAbilities');
  const cardInfoCache = new Map();
  let modalContextToken = 0;
  const elCdClose     = document.getElementById('cdClose');

  elCdClose.addEventListener('click', ()=>{ elCardDetail.classList.remove('visible'); applyPopupPeekState(); });
  elViewerClose.addEventListener('click', ()=>{ closeViewerPopup(); });
  document.addEventListener('keydown', ev=>{ if(ev.key==='Escape'){ elCardDetail.classList.remove('visible'); applyPopupPeekState(); } });

  function hasPopupForInspect(){
    return !!((popup && popup.type) || (viewerPopup && viewerPopup.type) || elCardDetail.classList.contains('visible'));
  }

  function applyPopupPeekState(){
    const has = hasPopupForInspect();
    if(!has) popupsHiddenForInspect = false;
    const hide = !!(has && popupsHiddenForInspect);
    if(elMask) elMask.classList.toggle('popupPeekHidden', hide);
    if(elViewerLayer) elViewerLayer.classList.toggle('popupPeekHidden', hide);
    // During board inspection, keep the card-detail panel usable for newly clicked board cards.
    // The main modal/viewer are hidden above and no longer intercept clicks.
    if(btnPopupPeek){
      btnPopupPeek.classList.toggle('active', has && !hide);
      btnPopupPeek.classList.toggle('inspecting', hide);
      btnPopupPeek.textContent = hide ? '👁️ ポップアップ表示' : '🙈 盤面確認';
      btnPopupPeek.title = hide ? 'ポップアップを再表示する' : 'ポップアップを一時的に隠して盤面を確認';
    }
  }

  if(btnPopupPeek){
    btnPopupPeek.addEventListener('click', (ev)=>{
      ev.stopPropagation();
      if(!hasPopupForInspect()) return;
      popupsHiddenForInspect = !popupsHiddenForInspect;
      if(popupsHiddenForInspect && elCardDetail) elCardDetail.classList.remove('visible');
      applyPopupPeekState();
    });
  }
  document.addEventListener('click', ev=>{
    if(elCardDetail.classList.contains('visible') && !elCardDetail.contains(ev.target)){
      elCardDetail.classList.remove('visible');
      applyPopupPeekState();
    }
  });

  async function showCardDetail(cn, anchorEl){
    if(!cn) return;
    elCdImg.src = imgUrl(cn);
    elCdName.textContent = cn;
    elCdMeta.innerHTML = '';
    elCdAbilities.textContent = '読み込み中…';
    elCardDetail.classList.add('visible');
    applyPopupPeekState();

    function clampCardDetailToViewport(anchor){
      elCardDetail.style.transform = '';
      const rect = anchor ? anchor.getBoundingClientRect() : {left:window.innerWidth/2, right:window.innerWidth/2, top:window.innerHeight/2};
      const w = Math.max(1, elCardDetail.offsetWidth || 340);
      const h = Math.max(1, elCardDetail.offsetHeight || 400);
      const gap = Math.max(4, Number(getComputedStyle(document.documentElement).getPropertyValue('--uiScale') || 1) * 8);
      let left = anchor ? (rect.right + gap) : ((window.innerWidth - w) / 2);
      let top  = anchor ? rect.top : ((window.innerHeight - h) / 2);
      if(left + w > window.innerWidth - gap) left = rect.left - w - gap;
      if(left < gap) left = Math.max(gap, window.innerWidth - w - gap);
      if(top + h > window.innerHeight - gap) top = window.innerHeight - h - gap;
      elCardDetail.style.left = Math.max(gap, left) + 'px';
      elCardDetail.style.top  = Math.max(gap, top)  + 'px';
    }

    // Position near the anchor element.  Use actual scaled panel dimensions, not fixed px.
    // BUILD_TAG: card_detail_responsive_scale_20260701ap
    if(anchorEl){
      clampCardDetailToViewport(anchorEl);
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
        const hStr = orderedHeartEntries(info.hearts).map(([k,v])=>`${jpMap[k]||k}×${v}`).join(' ');
        chips.push(hStr);
      }
      if(info.required_hearts && Object.keys(info.required_hearts).length){
        const jpMap = {pink:'桃',red:'赤',yellow:'黄',green:'緑',blue:'青',purple:'紫',any:'無色'};
        const rStr = '必要: ' + orderedHeartEntries(info.required_hearts).map(([k,v])=>`${jpMap[k]||k}×${v}`).join(' ');
        chips.push(rStr);
      }
      chips.forEach(c=>{ const s=document.createElement('span'); s.textContent=c; elCdMeta.appendChild(s); });

      // abilities
      if(info.abilities && info.abilities.length){
        elCdAbilities.textContent = info.abilities.join('\n\n');
      } else {
        elCdAbilities.textContent = '（効果なし）';
      }
      requestAnimationFrame(()=>clampCardDetailToViewport(anchorEl || null));
    } catch(e) {
      elCdAbilities.textContent = '（取得失敗）';
      requestAnimationFrame(()=>clampCardDetailToViewport(anchorEl || null));
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
    // BUILD_TAG: responsive_ui_scale_full_chrome_20260701al
    // UI chrome, popups, buttons, labels and popup-inner text/icons must track
    // the same scale as the playmat. Do not clamp this separately: a clamp makes
    // cards resize while text/buttons appear fixed, especially on large/small windows.
    const uiS = Math.max(0.38, s);
    document.documentElement.style.setProperty('--uiScale', uiS.toFixed(6));
    document.documentElement.style.setProperty('--cardW', (451*s).toFixed(2) + 'px');
    document.documentElement.style.setProperty('--cardH', (630*s).toFixed(2) + 'px');
    // right-side panel width in pixels (scaled)
    document.documentElement.style.setProperty('--sideW', (270*s).toFixed(2) + 'px');
  }

  function scale(){
    return parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--scale')) || 1.0;
  }
  function px(v){ return v * scale(); }

  let resizeRenderFrame = 0;
  function scheduleResizeRender(){
    if(resizeRenderFrame) cancelAnimationFrame(resizeRenderFrame);
    resizeRenderFrame = requestAnimationFrame(()=>{
      resizeRenderFrame = 0;
      cssScale();
      render();
    });
  }
  window.addEventListener('resize', scheduleResizeRender, {passive:true});
  if(window.visualViewport){
    window.visualViewport.addEventListener('resize', scheduleResizeRender, {passive:true});
  }

  function requestJson(url, options={}){
    const opts = options || {};
    return fetch(url, opts).catch(()=>{
      return new Promise((resolve, reject)=>{
        try{
          const xhr = new XMLHttpRequest();
          const method = String(opts.method || 'GET').toUpperCase();
          xhr.open(method, url, true);
          const headers = opts.headers || {};
          Object.keys(headers).forEach(k=>xhr.setRequestHeader(k, headers[k]));
          xhr.onload = ()=>{
            const body = xhr.responseText || '';
            const responseLike = {
              ok: xhr.status >= 200 && xhr.status < 300,
              status: xhr.status,
              text: async ()=>body,
              json: async ()=>JSON.parse(body)
            };
            resolve(responseLike);
          };
          xhr.onerror = ()=>reject(new Error('request failed'));
          xhr.send(opts.body || null);
        }catch(err){
          reject(err);
        }
      });
    });
  }

  async function apiState(){
    const url = IS_PUBLIC_VIEW ? '/state?view=public' : '/state';
    const r = await requestJson(url, {cache:'no-store'});
    const data = await r.json();
    // BUILD_TAG: public_refresh_notice_client_version_reload_20260701ar
    try{
      const serverVer = String((data && data.ui_version) || '');
      if(IS_PUBLIC_VIEW && serverVer && serverVer !== CLIENT_UI_VERSION && !clientReloadingForVersion){
        clientReloadingForVersion = true;
        window.location.reload();
      }
    }catch(e){}
    return data;
  }
  async function apiCmd(cmd, payload={}){
    // /public and ?view=public are read-only viewer modes.
    // Keep buttons harmless even if old controls remain visible.
    if(IS_PUBLIC_VIEW){
      return await apiState();
    }
    const r = await requestJson('/cmd', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({cmd, payload})
    });
    const data = await r.json();
    try{
      localStorage.setItem('llocg_public_refresh_ping', String(Date.now()) + ':' + String(cmd || ''));
    }catch(e){}
    return data;
  }

  async function saveSuspendData(){
    if(IS_PUBLIC_VIEW) return;
    try{
      const r = await requestJson('/suspend_state', {cache:'no-store'});
      if(!r.ok) throw new Error(await r.text());
      const data = await r.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
      const a = document.createElement('a');
      const stamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15);
      a.href = URL.createObjectURL(blob);
      a.download = `llocg_ui_suspend_${stamp}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(()=>URL.revokeObjectURL(a.href), 1200);
      setBanner('中断データを保存しました');
    }catch(e){
      console.error(e);
      alert('中断保存に失敗しました: ' + String(e && e.message || e));
    }
  }

  async function loadSuspendDataFile(file){
    if(IS_PUBLIC_VIEW || !file) return;
    try{
      const text = await file.text();
      const data = JSON.parse(text);
      const r = await requestJson('/resume_state', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });
      const out = await r.json();
      if(!r.ok || !out.ok) throw new Error(out.error || '再開に失敗しました');
      st = out.state;
      selHand = [];
      lastStateSignature = stableStateSignature(st);
      try{
        localStorage.setItem('llocg_public_refresh_ping', String(Date.now()) + ':resume_state');
      }catch(e){}
      closePopup();
      closeViewerPopup();
      updateTop();
      render();
      setBanner('中断データから再開しました');
    }catch(e){
      console.error(e);
      alert('再開読込に失敗しました: ' + String(e && e.message || e));
    }finally{
      if(suspendFileInput) suspendFileInput.value = '';
    }
  }

  function cnType(cn){
    try{ return String((st && st.cn2type && st.cn2type[cn]) || ''); }catch(e){ return ''; }
  }
  function publicKnownOrient(cn){
    try{
      const m = st && st.public_hand_revealed_orient;
      const v = m ? String(m[cn] || '') : '';
      if(v === 'landscape' || v === 'portrait') return v;
    }catch(e){}
    return '';
  }
  function cardLooksLive(cn){
    if(!cn || cn === '__BACK__' || cn === '__ENERGY__') return false;
    const po = publicKnownOrient(cn);
    if(po === 'landscape') return true;
    try{
      if(st && st.cn2is_live && st.cn2is_live[cn] === true) return true;
    }catch(e){}
    const t = cnType(cn).toUpperCase();
    if(t.includes('LIVE')) return true;
    try{
      const sc = st && st.cn2score ? Number(st.cn2score[cn] || 0) : 0;
      if(sc > 0) return true;
    }catch(e){}
    return false;
  }
  function intrinsicOrient(cn){
    const po = publicKnownOrient(cn);
    if(po === 'landscape' || po === 'portrait') return po;
    if(cardLooksLive(cn)) return 'landscape';
    return 'portrait';
  }
  function instanceMeta(instanceId){
    const id = String(instanceId || '').trim();
    if(!id || !st || !st.card_instance_meta) return null;
    const meta = st.card_instance_meta[id];
    return (meta && typeof meta === 'object') ? meta : null;
  }
  function zoneInstanceId(zone, index){
    try{
      const ci = st && st.card_instances ? st.card_instances : null;
      const arr = ci && Array.isArray(ci[zone]) ? ci[zone] : [];
      return (index >= 0 && index < arr.length) ? String(arr[index] || '') : '';
    }catch(e){ return ''; }
  }
  function stageInstanceId(pos){
    try{
      const stage = st && st.card_instances && st.card_instances.stage ? st.card_instances.stage : null;
      return stage ? String(stage[String(pos || '').toUpperCase()] || '') : '';
    }catch(e){ return ''; }
  }
  function debugZoneLabel(zone, pos=''){
    const z = String(zone || '');
    const p = String(pos || '').toUpperCase();
    if(z === 'hand') return '手札';
    if(z === 'deck') return '山札';
    if(z === 'green_room') return '控え室';
    if(z === 'success_zone') return '成功ライブ置き場';
    if(z === 'stage') return p ? `ステージ${p}` : 'ステージ';
    return z || '領域';
  }
  function debugSelectionSame(zone, index=-1, pos=''){
    if(!debugMoveSelection) return false;
    return String(debugMoveSelection.zone || '') === String(zone || '')
      && String(debugMoveSelection.pos || '') === String(pos || '')
      && Number(debugMoveSelection.index) === Number(index);
  }
  function updateDebugMoveButton(){
    if(!btnDebugMove) return;
    btnDebugMove.classList.toggle('active', !!debugMoveMode);
    btnDebugMove.textContent = debugMoveMode ? 'デバッグモード ON' : 'デバッグモード OFF';
    btnDebugMove.title = debugMoveMode
      ? 'カードを選び、移動先をクリックして配置を変更します'
      : '効果検証用にカードを自由移動するモード';
  }
  function clearDebugMoveSelection(){
    debugMoveSelection = null;
  }
  function selectDebugMoveCard(zone, index, cn, pos=''){
    if(!debugMoveMode || IS_PUBLIC_VIEW) return false;
    const cardnumber = String(cn || '').trim();
    if(!cardnumber || cardnumber === '__BACK__') return true;
    if(debugSelectionSame(zone, index, pos)){
      clearDebugMoveSelection();
      setBanner('デバッグ移動の選択を解除');
      render();
      return true;
    }
    debugMoveSelection = {zone:String(zone || ''), index:Number(index), cardnumber, pos:String(pos || '')};
    setBanner(`${cardDisplayText(cardnumber)} の移動先をクリック`);
    render();
    return true;
  }
  async function putDebugMoveCard(toZone, toIndex=null, toPos=''){
    if(!debugMoveMode || IS_PUBLIC_VIEW) return false;
    if(!debugMoveSelection){
      setBanner('先に移動するカードを選択してください');
      return true;
    }
    const payload = {
      from_zone: debugMoveSelection.zone,
      from_index: debugMoveSelection.index,
      from_pos: debugMoveSelection.pos || '',
      to_zone: String(toZone || ''),
      to_index: (toIndex === null || toIndex === undefined) ? null : Number(toIndex),
      to_pos: String(toPos || ''),
    };
    clearDebugMoveSelection();
    st = await apiCmd('debug_move_card', payload);
    selHand = [];
    updateTop();
    render();
    return true;
  }
  async function reorderDebugZone(zone, cards){
    if(!debugMoveMode || IS_PUBLIC_VIEW) return false;
    st = await apiCmd('debug_reorder_zone', {zone:String(zone || ''), cards:(cards || []).map(x=>String(x || ''))});
    updateTop();
    render();
    return true;
  }
  function imgUrl(cn, instanceId=''){
    const params = new URLSearchParams({cn:String(cn || '')});
    try{
      const meta = instanceMeta(instanceId);
      if(meta){
        const variantId0 = String(meta.variant_id || '');
        const rarity0 = String(meta.rarity || '');
        if(variantId0) params.set('variant_id', variantId0);
        if(rarity0) params.set('rarity', rarity0);
        return `/img?${params.toString()}`;
      }
      const variantMap = (st && st.cn2image_variant_id) ? st.cn2image_variant_id : null;
      const rarityMap = (st && st.cn2image_rarity) ? st.cn2image_rarity : null;
      const key = String(cn || '');
      const variantId = variantMap && variantMap[key] ? String(variantMap[key]) : '';
      const rarity = rarityMap && rarityMap[key] ? String(rarityMap[key]) : '';
      if(variantId) params.set('variant_id', variantId);
      if(rarity) params.set('rarity', rarity);
    }catch(e){}
    return `/img?${params.toString()}`;
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
  function cardDisplayText(cn){
    const s = String(cn || '').trim();
    if(!s) return '';
    if(s === '__BACK__') return '非公開カード';
    const name = cardNameFor(s);
    const t = cnType(s).toUpperCase();
    if(t.includes('MEMBER')){
      const cost = cardCostFor(s);
      const costLabel = Number.isFinite(cost) && cost > 0 ? `${cost}コスト` : 'コスト不明';
      return `${costLabel} ${name}`;
    }
    if(t.includes('LIVE')) return name;
    return name || s;
  }
  function choiceTextLabel(raw){
    const s = String(raw || '').trim();
    const low = s.toLowerCase();
    if(!s) return '';
    if(looksLikeCardNo(s)) return cardDisplayText(s);
    if(HEART_LABEL_BY_COLOR[low]) return `${HEART_LABEL_BY_COLOR[low]}ハート`;
    if(low === 'skip' || low === '__skip__') return 'スキップ';
    if(low === 'pay' || low === 'yes' || low === 'y' || low === '1' || low === 'true' || low === 'apply' || low === 'use') return '使う';
    if(low === 'no' || low === 'n' || low === '0' || low === 'false') return '使わない';
    if(low === 'ok') return '確認';
    if(low === 'self') return '自分';
    if(low === 'opponent') return '相手';
    if(low === 'draw') return '置いたのでカードを引く';
    if(low === 'no_draw') return '置かなかった / 引かない';
    if(low === 'threshold_met') return '条件達成';
    if(low === 'threshold_not_met') return '条件未達';
    if(low === 'top') return 'デッキの一番上';
    if(low === 'bottom') return 'デッキの一番下';
    if(low === 'green' || low === 'waiting') return '控え室に置く';
    if(low === 'keep') return 'デッキ上に残す';
    return s;
  }
  function isNumericChoicePendingKind(kind){
    const k = String(kind || '').trim();
    return k === 'choose_number_reveal_top_member_cost_compare'
      || k === 'opponent_wait_notify'
      || k === 'set_opponent_excess_for_live_success'
      || k === 'set_opponent_success_score_for_live_attempt'
      || k === 'choose_opponent_wait_count_for_topdeck_green_group_members'
      || k === 'choose_under_energy_return_count';
  }
  function choiceTextLabelForPending(raw, kind){
    const s = String(raw || '').trim();
    if(isNumericChoicePendingKind(kind) && /^-?\d+$/.test(s)) return s;
    return choiceTextLabel(s);
  }
  function choiceRichLabel(raw, kind=''){
    const s = String(raw || '').trim();
    const low = s.toLowerCase();
    const jpToColor = {'桃':'pink','赤':'red','黄':'yellow','緑':'green','青':'blue','紫':'purple','任意':'any','無色':'any','any':'any','all':'all'};
    const norm = HEART_TOKEN_BY_COLOR[low] ? low : (jpToColor[s] || jpToColor[low] || '');
    const token = HEART_TOKEN_BY_COLOR[norm];
    if(token){
      const span = document.createElement('span');
      span.style.cssText = 'display:inline-flex;align-items:center;gap:6px;';
      span.appendChild(makeTextIconImg(token, HEART_LABEL_BY_COLOR[norm] || s || low, '1.2em'));
      span.appendChild(document.createTextNode(`${HEART_LABEL_BY_COLOR[norm] || s || low}ハート`));
      return span;
    }
    return document.createTextNode(choiceTextLabelForPending(s, kind));
  }
  function cardChoiceCaption(cn, nth, tot){
    const name = cardDisplayText(cn);
    if(tot && tot > 1) return `${name} (${nth}/${tot})`;
    return name;
  }
  function shortAutoOrderLabel(label, cn){
    let s = String(label || '').trim();
    const c = String(cn || '').trim();
    if(c && s.startsWith(c + '：')) s = s.slice(c.length + 1).trim();
    if(s.length > 18) s = s.slice(0, 17) + '…';
    return s;
  }
  function pendingTitleFor(p){
    const kind = String((p && p.kind) || '').trim();
    if(kind === 'pay_or_skip' || kind === 'confirm_effect') return '効果を使いますか？';
    if(kind === 'choose_effects') return '効果を選択';
    if(kind === 'opponent_wait_notify') return '相手ウェイト人数を記録';
    if(kind === 'set_opponent_excess_for_live_success') return '相手余剰ハート数を指定';
    if(kind === 'set_opponent_success_score_for_live_attempt') return '相手成功スコア合計を指定';
    if(kind === 'confirm_yell_revealed_all_to_green_then_extra_yell') return '追加エール確認';
    if(kind === 'choose_yell_revealed_to_green_then_extra_yell') return '公開カードを選択';
    if(kind === 'live_attempt_summary_ack') return 'ライブ成功確認';
    if(kind === 'choose_stage_member_to_activate' || kind === 'choose_stage_member_to_gain_blade' || kind === 'choose_stage_member_to_gain_icons' || kind === 'choose_stage_member_to_position_change_source') return '対象メンバーを選択';
    if(kind === 'choose_heart_color' || kind === 'choose_heart_color_for_other') return 'ハートの色を選択';
    if(kind === 'discard_from_hand' || kind === 'discard_named_cards_from_hand') return '手札から選択';
    if(kind === 'position_change') return '移動先を選択';
    if(kind === 'choose_from_topk' || kind === 'choose_top_keep_one' || kind === 'topdeck_from_green' || kind === 'bottomdeck_from_green' || kind === 'live_storage_live_to_deck_top_gain_icons' || kind === 'hand_to_deck_bottom' || kind === 'hand_to_deck_top_or_bottom') return 'カードを選択';
    if(kind === 'choose_deck_top_or_bottom_for_hand_card' || kind === 'choose_deck_top_or_bottom_for_live_storage_card') return '置く場所を選択';
    if(kind === 'choose_player_for_green_bottom' || kind === 'choose_player_for_deck_top_action') return 'プレイヤーを選択';
    if(kind === 'live_storage_to_deck_top_or_bottom') return 'ライブカードを選択';
    if(kind === 'manual_opponent_green_bottom_notify' || kind === 'manual_opponent_deck_top_action_notify' || kind === 'manual_opponent_mass_bottom_threshold') return '相手への効果';
    if(kind === 'mass_bottom_auto_ack') return '自動効果確認';
    if(kind === 'mass_bottom_optional_result_ack') return '効果処理結果';
    if(kind === 'confirm_mass_green_members_to_bottom') return '効果を使いますか？';
    if(kind === 'self_top1_to_green_or_keep') return 'デッキ上を確認';
    if(kind === 'choose_member_from_green_multi_up_to') return 'カードを選択';
    if(kind === 'auto_order') return '解決順を選択';
    if(kind === 'choose_under_energy_return_count') return '戻す枚数を選択';
    if(kind === 'choose_number_reveal_top_member_cost_compare') return '数を選択';
    if(kind === 'choose_opponent_wait_count_for_topdeck_green_group_members') return '人数を選択';
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
    if(kind === 'choose_member_from_green_multi_up_to') return '控え室または手札からカードを0〜指定枚数まで選び、確定を押してください。';
    if(kind === 'choose_stage_member_to_activate') return '対象にするメンバーを選んでください。';
    if(kind === 'choose_stage_member_to_position_change_source') return 'ポジションチェンジさせるメンバーを選んでください。';
    if(kind === 'choose_stage_member_to_gain_blade' || kind === 'choose_stage_member_to_gain_icons') return '効果を受けるメンバーを選んでください。';
    if(kind === 'choose_heart_color' || kind === 'choose_heart_color_for_other') return '付与するハートの色を選んでください。';
    if(kind === 'discard_from_hand' || kind === 'discard_named_cards_from_hand') return '手札から選ぶカードを選択してください。';
    if(kind === 'choose_effects') return '解決する効果を選んでください。';
    if(kind === 'live_attempt_summary_ack') return '必要ハート・所持ハート・成功/失敗・スコアを確認してください。';
    if(kind === 'confirm_yell_revealed_all_to_green_then_extra_yell') return '控え室に置く公開カードを確認し、追加エールを行うか選んでください。';
    if(kind === 'choose_yell_revealed_to_green_then_extra_yell') return '控え室に置くエール公開カードを選んでください。';
    if(kind === 'auto_order') return '解決順を選んでください。';
    if(kind === 'set_opponent_excess_for_live_success') return 'このライブ成功時効果の処理で参照する相手余剰ハート数を選んでください。';
    if(kind === 'set_opponent_success_score_for_live_attempt') return 'このライブ判定で参照する相手成功ライブカード置き場のスコア合計を選んでください。';
    if(kind === 'position_change') return '移動先のエリアを選んでください。';
    if(kind === 'choose_deck_top_or_bottom_for_hand_card' || kind === 'choose_deck_top_or_bottom_for_live_storage_card') return 'デッキの一番上か一番下を選んでください。';
    if(kind === 'choose_player_for_green_bottom' || kind === 'choose_player_for_deck_top_action') return '自分か相手を選んでください。';
    if(kind === 'live_storage_to_deck_top_or_bottom') return '控え室に置かれるライブカードのうち、デッキ上/下へ置くカードを選んでください。';
    if(kind === 'manual_opponent_green_bottom_notify' || kind === 'manual_opponent_deck_top_action_notify' || kind === 'manual_opponent_mass_bottom_threshold') return '相手側の処理を手動で行い、条件達成/未達を選んでください。';
    if(kind === 'mass_bottom_auto_ack') return '自動効果を確認してから、後続処理へ進みます。';
    if(kind === 'mass_bottom_optional_result_ack') return '控え室から戻した枚数と条件達成状況を確認してください。';
    if(kind === 'confirm_mass_green_members_to_bottom') return '自分の控え室のメンバーカードをすべてデッキ下へ置くか選んでください。';
    if(kind === 'self_top1_to_green_or_keep') return '公開されたデッキ上カードを控え室に置くか、デッキ上に残すか選んでください。';
    return pendingSourceCn(p) ? '効果を解決するため、対象または選択肢を選んでください。' : '';
  }
  const TEXTICON_BASE = '/llocg_db_out_full/card_images/texticons/';
  const TEXTICON_FILE_BY_TOKEN = {
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
  const TEXTICON_LABEL_BY_TOKEN = {
    '<(ブレード)>':'ブレード',
    '<(桃)>':'桃',
    '<(赤)>':'赤',
    '<(黄)>':'黄',
    '<(緑)>':'緑',
    '<(青)>':'青',
    '<(紫)>':'紫',
    '<(任意)>':'任意',
    '<(虹)>':'ALL',
    '<(すべて)>':'ALL',
  };
  const HEART_TOKEN_BY_COLOR = {
    pink:'<(桃)>', red:'<(赤)>', yellow:'<(黄)>', green:'<(緑)>',
    blue:'<(青)>', purple:'<(紫)>', any:'<(任意)>', all:'<(虹)>',
  };
  const HEART_LABEL_BY_COLOR = {
    pink:'桃', red:'赤', yellow:'黄', green:'緑', blue:'青', purple:'紫', any:'任意', all:'ALL',
  };
  const HEART_COLOR_ORDER = ['pink','red','yellow','green','blue','purple','any','all'];
  function heartColorOrderKey(k){
    const idx = HEART_COLOR_ORDER.indexOf(String(k||'').toLowerCase());
    return idx >= 0 ? idx : HEART_COLOR_ORDER.length + String(k||'').charCodeAt(0);
  }
  function orderedHeartEntries(map){
    return Object.entries(map || {})
      .filter(([k,v]) => Number(v || 0) !== 0)
      .sort((a,b) => heartColorOrderKey(a[0]) - heartColorOrderKey(b[0]));
  }
  function yellHeartCountsForCard(cn){
    const m = (st && st.cn2yell_hearts) ? st.cn2yell_hearts : null;
    const v = (m && cn && typeof m[cn] === 'object') ? m[cn] : null;
    return v && !Array.isArray(v) ? v : {};
  }
  function baseHeartCountsForCard(cn){
    const m = (st && st.cn2base_hearts) ? st.cn2base_hearts : null;
    const v = (m && cn && typeof m[cn] === 'object') ? m[cn] : null;
    return v && !Array.isArray(v) ? v : {};
  }
  function yellDrawIconsForCard(cn){
    const m = (st && st.cn2yell_draw_icons) ? st.cn2yell_draw_icons : null;
    const v = m && cn ? Number(m[cn] || 0) : 0;
    return Number.isFinite(v) ? v : 0;
  }
  function yellScoreIconsForCard(cn){
    const m = (st && st.cn2yell_score_icons) ? st.cn2yell_score_icons : null;
    const v = m && cn ? Number(m[cn] || 0) : 0;
    return Number.isFinite(v) ? v : 0;
  }
  function yellDoubleColorlessIconsForCard(cn){
    const m = (st && st.cn2yell_double_colorless_icons) ? st.cn2yell_double_colorless_icons : null;
    const v = m && cn ? Number(m[cn] || 0) : 0;
    return Number.isFinite(v) ? v : 0;
  }
  function yellHasBladeHeartForCard(cn){
    const m = (st && st.cn2yell_has_blade_heart) ? st.cn2yell_has_blade_heart : null;
    if(!m || !cn) return false;
    return Boolean(m[String(cn || '')]);
  }
  function computeYellRevealSummary(cards, p){
    const out = {heartCounts:{pink:0, red:0, yellow:0, green:0, blue:0, purple:0, all:0, any:0}, drawIcons:0, scoreIcons:0, doubleColorlessIcons:0, noBladeHeartCards:0, drewCount:0};
    (Array.isArray(cards) ? cards : []).forEach(cn=>{
      const cnText = String(cn || '');
      const hm = yellHeartCountsForCard(cnText);
      Object.entries(hm || {}).forEach(([k,v])=>{
        const kk = String(k || '').toLowerCase();
        const n = Number(v || 0);
        if(!Number.isFinite(n)) return;
        out.heartCounts[kk] = Number(out.heartCounts[kk] || 0) + n;
      });
      out.drawIcons += yellDrawIconsForCard(cnText);
      out.scoreIcons += yellScoreIconsForCard(cnText);
      out.doubleColorlessIcons += yellDoubleColorlessIconsForCard(cnText);
      if(!yellHasBladeHeartForCard(cnText)) out.noBladeHeartCards += 1;
    });
    const metaDraw = Number(p && p.yell_draw_icon_count || 0);
    const metaDrew = Number(p && p.yell_draw_drew_count || 0);
    if(Number.isFinite(metaDraw) && metaDraw > 0) out.drawIcons = metaDraw;
    if(Number.isFinite(metaDrew) && metaDrew >= 0) out.drewCount = metaDrew;
    return out;
  }
  const TEXTICON_TOKEN_RE = /<\((ブレード|桃|赤|黄|緑|青|紫|任意|虹|すべて)\)>/g;

  function textIconLabel(tok, fallback){
    return TEXTICON_LABEL_BY_TOKEN[tok] || fallback || tok;
  }
  function makeTextIconImg(tok, fallback, sizeCss){
    const srcFile = TEXTICON_FILE_BY_TOKEN[tok] || '';
    if(!srcFile){
      return document.createTextNode(textIconLabel(tok, fallback));
    }
    const img = document.createElement('img');
    img.src = TEXTICON_BASE + srcFile;
    img.alt = textIconLabel(tok, fallback);
    img.style.width = sizeCss || '1em';
    img.style.height = sizeCss || '1em';
    img.style.objectFit = 'contain';
    img.style.verticalAlign = '-0.12em';
    img.style.margin = '0 0.05em';
    img.onerror = ()=>{
      const sp = document.createElement('span');
      sp.textContent = textIconLabel(tok, fallback);
      sp.style.cssText = img.style.cssText + ';display:inline-flex;align-items:center;justify-content:center;font-size:.72em;line-height:1;font-weight:700;color:#fff;';
      img.replaceWith(sp);
    };
    return img;
  }
  function appendRichText(el, raw){
    const s = String(raw || '');
    if(!s) return;
    let last = 0;
    let m;
    TEXTICON_TOKEN_RE.lastIndex = 0;
    while((m = TEXTICON_TOKEN_RE.exec(s)) !== null){
      if(m.index > last){
        el.appendChild(document.createTextNode(s.slice(last, m.index)));
      }
      el.appendChild(makeTextIconImg(m[0], m[1], '1em'));
      last = TEXTICON_TOKEN_RE.lastIndex;
    }
    if(last < s.length){
      el.appendChild(document.createTextNode(s.slice(last)));
    }
  }
  function setRichText(el, raw){
    el.innerHTML = '';
    appendRichText(el, raw);
  }
  function setRichTextWithMassCounts(el, raw){
    const s = String(raw || '');
    el.innerHTML = '';
    if(!s) return;
    const re = /([0-9０-９]+)\s*枚/g;
    let last = 0;
    let m;
    while((m = re.exec(s)) !== null){
      appendRichText(el, s.slice(last, m.index));
      const sp = document.createElement('span');
      sp.className = 'massInlineCount';
      sp.textContent = m[0];
      el.appendChild(sp);
      last = re.lastIndex;
    }
    appendRichText(el, s.slice(last));
  }
  function makeTextIconStack(iconSpecs, titleAll, iconPx=16, stepPx=10){
    const n = iconSpecs.length;
    const totalW = iconPx + stepPx * Math.max(0, n - 1);
    const wrap = document.createElement('div');
    wrap.title = titleAll || '';
    wrap.style.cssText = ['position:relative', `width:${uiCalc(totalW)}`, `height:${uiCalc(iconPx)}`, 'flex-shrink:0'].join(';');
    iconSpecs.forEach((spec, i)=>{
      const tok = (typeof spec === 'string') ? spec : String(spec.token || '');
      const fb = (typeof spec === 'string') ? textIconLabel(tok, '') : String(spec.alt || spec.fallback || '');
      const node = makeTextIconImg(tok, fb, uiCalc(iconPx));
      if(node.nodeType === Node.TEXT_NODE){
        const sp = document.createElement('span');
        sp.textContent = node.textContent || fb || tok;
        sp.style.cssText = [
          'position:absolute', `left:${uiCalc(stepPx*i)}`, 'top:0', `width:${uiCalc(iconPx)}`, `height:${uiCalc(iconPx)}`,
          'display:flex', 'align-items:center', 'justify-content:center', `font-size:${uiCalc(Math.max(9, iconPx-6))}`,
          'font-weight:700', 'line-height:1', 'color:#fff', `z-index:${10+i}`,
        ].join(';');
        wrap.appendChild(sp);
        return;
      }
      node.style.position = 'absolute';
      node.style.left = uiCalc(stepPx*i);
      node.style.top = '0';
      node.style.width = uiCalc(iconPx);
      node.style.height = uiCalc(iconPx);
      node.style.margin = '0';
      node.style.verticalAlign = 'initial';
      node.style.zIndex = String(10+i);
      wrap.appendChild(node);
    });
    return wrap;
  }
  function makeTextIconRow(signText, stack, titleAll){
    const row = document.createElement('div');
    row.title = titleAll || '';
    row.style.cssText = `display:flex;align-items:center;gap:${uiCalc(2)};`;
    const sign = document.createElement('span');
    sign.textContent = signText;
    sign.style.cssText = ['color:#fff',`font-size:${uiCalc(11)}`,'font-weight:700','line-height:1','flex-shrink:0'].join(';');
    row.appendChild(sign);
    row.appendChild(stack);
    return row;
  }

  function clearModalLead(){
    elModalLead.classList.remove('visible');
    elModalSourceCard.innerHTML = '';
    elModalSourceName.textContent = '';
    elModalSourceMeta.textContent = '';
    elModalCond.className = '';
    elModalCond.style.display = 'none';
    elModalCond.textContent = '';
    elModalCardTextWrap.classList.remove('visible');
    if(elModalCardTextTitle) elModalCardTextTitle.textContent = 'カードテキスト';
    elModalCardText.textContent = '';
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

  function cardGroupFor(cn){ try{ return String((st && st.cn2group && st.cn2group[cn]) || ''); }catch(e){ return ''; } }
  function cardUnitFor(cn){ try{ return String((st && st.cn2unit && st.cn2unit[cn]) || ''); }catch(e){ return ''; } }
  function cardCostFor(cn){ try{ return Number((st && st.cn2cost && st.cn2cost[cn]) || 0); }catch(e){ return 0; } }
  function cardBladeFor(cn){ try{ return Number((st && st.cn2blade && st.cn2blade[cn]) || 0); }catch(e){ return 0; } }
  function cardGroupKeysFor(cn){
    const vals = [cardGroupFor(cn), cardUnitFor(cn)];
    const out = [];
    vals.forEach(v=>{
      String(v || '').replace(/／/g, '/').split('/').forEach(part=>{
        const s = String(part || '').trim();
        if(s && s !== '-' && !out.includes(s)) out.push(s);
      });
    });
    return out;
  }
  function formatCostBadgeText(baseCost, effectiveCost){
    const base = Number(baseCost || 0);
    const eff = Number(effectiveCost || 0);
    const delta = eff - base;
    if(!Number.isFinite(base) || !Number.isFinite(eff) || !base || !delta) return '';
    const sign = delta >= 0 ? '+' : '-';
    return `cost ${base}${sign}${Math.abs(delta)}`;
  }
  function appendCostBadgeCurrent(cardEl, baseCost, effectiveCost, compact=false){
    try{
      const base = Number(baseCost || 0);
      const eff = Number(effectiveCost || 0);
      const delta = eff - base;
      const label = formatCostBadgeText(base, eff);
      if(!label || !cardEl) return;
      const cb = document.createElement('div');
      cb.className = 'costBadgeCurrent';
      cb.title = `current cost ${eff} (base ${base}, ${delta>=0?'bonus':'reduction'} ${Math.abs(delta)})`;
      cb.textContent = label;
      cb.style.cssText = [
        'position:absolute',
        'right:2px',
        'top:2px',
        'z-index:80',
        'display:inline-flex',
        'align-items:center',
        'justify-content:center',
        compact ? 'min-width:34px' : 'min-width:42px',
        compact ? 'height:16px' : 'height:18px',
        compact ? 'padding:1px 4px' : 'padding:1px 5px',
        'border-radius:999px',
        'background:rgba(245,245,245,.94)',
        'color:#111',
        'border:1px solid rgba(0,0,0,.28)',
        'box-shadow:0 1px 5px rgba(0,0,0,.38)',
        compact ? 'font-size:9px' : 'font-size:10px',
        'font-weight:900',
        'line-height:1',
        'white-space:nowrap',
        'pointer-events:none',
      ].join(';');
      cardEl.appendChild(cb);
    }catch(e){}
  }
  function cardScoreFor(cn){ try{ return Number((st && st.cn2score && st.cn2score[cn]) || 0); }catch(e){ return 0; } }
  function sumNumericMap(map){
    try{
      return Object.values(map || {}).reduce((acc,v)=>{
        const n = Number(v || 0);
        return acc + (Number.isFinite(n) ? n : 0);
      }, 0);
    }catch(e){ return 0; }
  }
  function stageStatsFor(slotKey, slotObj){
    if(!slotObj || !slotObj.cardnumber) return 0;
    const cn = String(slotObj.cardnumber || '');
    const sd = (st && st.stage_detail) ? st.stage_detail : null;
    const det = sd ? (sd[slotKey] || {}) : {};
    const baseBlade = cardBladeFor(cn);
    const baseHearts = sumNumericMap(baseHeartCountsForCard(cn));
    const bonusBlade = Number(det.temp_blade || 0) + Number(det.always_blade_bonus || 0);
    const bonusHearts =
      sumNumericMap(det.temp_hearts || {}) +
      sumNumericMap(det.success_zone_hearts_bonus || {}) +
      sumNumericMap(det.always_hearts_bonus || {});
    return Math.max(0, Math.round(baseBlade + baseHearts + bonusBlade + bonusHearts));
  }
  function totalStageStats(){
    const stage = (st && st.stage) ? st.stage : {};
    return ['L','C','R'].reduce((acc,pos)=>acc + stageStatsFor(pos, stage[pos]), 0);
  }
  function groupOrUnitMatch(cn, name){
    const target = String(name||'').trim();
    if(!target) return false;
    return cardGroupFor(cn) === target || cardUnitFor(cn) === target;
  }
  function countStageGroupMembers(name){
    let n = 0;
    const stage = (st && st.stage) ? st.stage : {};
    for(const pos of ['L','C','R']){
      const slot = stage[pos];
      const cn = slot && slot.cardnumber ? String(slot.cardnumber) : '';
      if(!cn) continue;
      if(cardTypeFor(cn) !== 'MEMBER') continue;
      if(groupOrUnitMatch(cn, name)) n += 1;
    }
    return n;
  }
  function stageAllGroupMembersMinCost(name, minCost){
    const stage = (st && st.stage) ? st.stage : {};
    let found = 0;
    for(const pos of ['L','C','R']){
      const slot = stage[pos];
      const cn = slot && slot.cardnumber ? String(slot.cardnumber) : '';
      if(!cn) continue;
      if(cardTypeFor(cn) !== 'MEMBER') continue;
      if(!groupOrUnitMatch(cn, name)) return false;
      if(cardCostFor(cn) < Number(minCost||0)) return false;
      found += 1;
    }
    return found > 0;
  }
  function countGreenLiveGroupOrUnit(name){
    const arr = (st && Array.isArray(st.green_room)) ? st.green_room : [];
    let n = 0;
    for(const cn of arr){
      const s = String(cn||'').trim();
      if(!s || cardTypeFor(s) !== 'LIVE') continue;
      if(groupOrUnitMatch(s, name)) n += 1;
    }
    return n;
  }
  function countGreenUniqueLiveNamesGroupOrUnit(name){
    const arr = (st && Array.isArray(st.green_room)) ? st.green_room : [];
    const seen = new Set();
    for(const cn of arr){
      const s = String(cn||'').trim();
      if(!s || cardTypeFor(s) !== 'LIVE') continue;
      if(!groupOrUnitMatch(s, name)) continue;
      const nm = cardNameFor(s);
      if(nm) seen.add(nm);
    }
    return seen.size;
  }
  function successZoneScoreSum(){
    const eff = Number(st && st.success_zone_score_sum);
    if(Number.isFinite(eff)) return eff;
    const arr = (st && Array.isArray(st.success_zone)) ? st.success_zone : [];
    return arr.reduce((a,cn)=>a + cardScoreFor(String(cn||'')), 0);
  }
  function successZoneHasScore(v){
    const arr = (st && Array.isArray(st.success_zone)) ? st.success_zone : [];
    return arr.some(cn => cardScoreFor(String(cn||'')) === Number(v||0));
  }
  function successZoneCardnameCount(name){
    const arr = (st && Array.isArray(st.success_zone)) ? st.success_zone : [];
    return arr.filter(cn => cardNameFor(String(cn||'')) === String(name||'')).length;
  }
  function liveZoneGroupCardCount(name){
    let n = 0;
    const arrs = [ (st && Array.isArray(st.set_zone)) ? st.set_zone : [], (st && Array.isArray(st.resolve_zone)) ? st.resolve_zone : [] ];
    for(const arr of arrs){
      for(const cn of arr){
        const s = String(cn||'').trim();
        if(!s) continue;
        if(groupOrUnitMatch(s, name)) n += 1;
      }
    }
    return n;
  }
  function pendingConditionStatus(p){
    if(!p || typeof p !== 'object') return null;
    if(p.condition_status && typeof p.condition_status === 'object'){
      const st0 = String(p.condition_status.state || 'neutral').trim();
      const txt0 = String(p.condition_status.text || '').trim();
      if(txt0) return {state: (st0 === 'met' || st0 === 'unmet' ? st0 : 'neutral'), text: txt0};
    }
    const kind = String(p.kind || '').trim();
    const neutral = (text)=>({state:'neutral', text});
    const met = (text)=>({state:'met', text:`条件達成: ${text}`});
    const unmet = (text)=>({state:'unmet', text:`条件未達成: ${text}`});
    if(kind === 'optional_pay_energy_for_self_score_if_group'){
      const g = String(p.condition_group_name || '');
      const got = countStageGroupMembers(g);
      return got >= 1 ? met(`ステージの『${g}』メンバー ${got}/1`) : unmet(`ステージの『${g}』メンバー ${got}/1`);
    }
    if(kind === 'execute_draw_then_choose_hand_cards_ordered_topdeck'){
      const g = String(p.condition_group_name || '');
      const min = Number(p.condition_min_cost || 0);
      if(g && min) return stageAllGroupMembersMinCost(g, min) ? met(`ステージ全員が『${g}』かつコスト${min}以上`) : unmet(`ステージ全員が『${g}』かつコスト${min}以上`);
      return neutral('条件判定後の解決です');
    }
    if(kind === 'execute_top_keep_one_then_reveal_top_score_if_live'){
      const g = String(p.condition_group_name || '');
      const got = countStageGroupMembers(g);
      return met(`ステージの『${g}』メンバー ${got}人`);
    }
    if(kind === 'live_start_score_if_live_zone_group_count_at_least'){
      const g = String(p.condition_group_name || '');
      const need = Number(p.condition_count || 0);
      const got = liveZoneGroupCardCount(g);
      return got >= need ? met(`ライブ中の『${g}』カード ${got}/${need}`) : unmet(`ライブ中の『${g}』カード ${got}/${need}`);
    }
    if(kind === 'live_start_score_if_green_live_group_count_at_least'){
      const g = String(p.condition_group_name || '');
      const need = Number(p.condition_count || 0);
      const got = countGreenLiveGroupOrUnit(g);
      return got >= need ? met(`控え室の『${g}』ライブ ${got}/${need}`) : unmet(`控え室の『${g}』ライブ ${got}/${need}`);
    }
    if(kind === 'live_start_score_if_success_zone_has_scores'){
      const a = Number(p.score_a || 0), b = Number(p.score_b || 0);
      const ha = successZoneHasScore(a), hb = successZoneHasScore(b);
      if(ha && hb) return met(`成功置き場にスコア${a}と${b}の両方があります`);
      if(ha || hb) return met(`成功置き場にスコア${ha ? a : b}があります`);
      return unmet(`成功置き場にスコア${a}/${b}がありません`);
    }
    if(kind === 'live_start_score_if_green_unique_live_names_group_count'){
      const g = String(p.condition_group_name || '');
      const c1 = Number(p.condition_count_one || 0);
      const c2 = Number(p.condition_count_two || 0);
      const got = countGreenUniqueLiveNamesGroupOrUnit(g);
      if(c2 && got >= c2) return met(`控え室の異名『${g}』ライブ ${got}/${c2}`);
      if(c1 && got >= c1) return met(`控え室の異名『${g}』ライブ ${got}/${c1}`);
      return unmet(`控え室の異名『${g}』ライブ ${got}/${Math.max(c1,c2)}`);
    }
    if(kind === 'live_start_score_and_increase_any_per_success_zone_cardname_count'){
      const nm = String(p.condition_cardname || '');
      const got = successZoneCardnameCount(nm);
      return got > 0 ? met(`成功置き場の「${nm}」 ${got}枚`) : unmet(`成功置き場の「${nm}」 0枚`);
    }
    if(kind === 'live_start_reduce_any_and_score_if_success_score_at_least'){
      const sum = successZoneScoreSum();
      const t1 = Number(p.reduce_threshold || 0), t2 = Number(p.score_threshold || 0);
      if(sum >= t2) return met(`成功置き場のスコア合計 ${sum} ≥ ${t2}`);
      if(sum >= t1) return met(`成功置き場のスコア合計 ${sum} ≥ ${t1}`);
      return unmet(`成功置き場のスコア合計 ${sum} < ${Math.min(t1||sum, t2||sum)}`);
    }
    if(kind === 'confirm_effect' || kind === 'pay_or_skip') return neutral('解決前の確認です');
    return null;
  }
  async function getCardInfoCached(cn){
    const key = String(cn||'').trim();
    if(!key || !looksLikeCardNo(key)) return null;
    if(cardInfoCache.has(key)) return cardInfoCache.get(key);
    try{
      const r = await fetch(`/cardinfo?cn=${encodeURIComponent(key)}`, {cache:'no-store'});
      if(!r.ok){ cardInfoCache.set(key, null); return null; }
      const info = await r.json();
      cardInfoCache.set(key, info);
      return info;
    }catch(e){ cardInfoCache.set(key, null); return null; }
  }
  function pendingEffectText(p){
    if(!p || typeof p !== 'object') return '';
    // BUILD_TAG: modal_current_effect_detail_text_20260626s
    // Effect-resolution modal must show only the currently resolving effect.
    // Use structured pending-level effect fields, including detail_text, but do
    // not fetch/fallback to the source card's full ability list.
    const direct = String((p.effect_text || p.effect || p.after_effect_template || p.detail_text || '') || '').trim();
    if(direct) return direct;
    const prm = (p.prompt && typeof p.prompt === 'object') ? p.prompt : null;
    if(prm){
      const t = String((prm.effect_text || prm.after_effect_template || prm.effect || prm.detail_text || '') || '').trim();
      if(t) return t;
    }
    const ctx = (p.ctx && typeof p.ctx === 'object') ? p.ctx : null;
    if(ctx){
      const t = String((ctx.effect_text || ctx.detail_text || '') || '').trim();
      if(t) return t;
    }
    return '';
  }

  function pendingHasInlineAutoEffectDetail(p){
    if(!p || typeof p !== 'object') return false;
    if(p.suppress_card_text || p.no_card_text) return true;
    const kind0 = String((p && p.kind) || '').trim();
    // Card-pick popups already show the selected source card at left and a short
    // instruction above the card list.  Showing the full source card text here
    // duplicates that context and pushes the actual card list out of view.
    if(kind0 === 'pick_from_yell' || kind0 === 'pick_from_yell_to_deck_top' || kind0 === 'pick_from_yell_to_deck_bottom') return true;
    const detail = String(p.auto_effect_detail || '');
    const text = String(p.text || '');
    const s = `${detail}
${text}`;
    // If the main prompt already contains the effect's condition/effect/action,
    // do not show the full card text panel as well.  That panel repeats the same
    // ability and makes automatic-effect choice popups too verbose.
    return !!(s && s.includes('【') && (s.includes('条件：') || s.includes('効果：') || s.includes('処理：')));
  }

  async function updateModalContextFromPending(p, token){
    elModalCond.className = '';
    elModalCond.style.display = 'none';
    elModalCond.textContent = '';
    elModalCardTextWrap.classList.remove('visible');
    if(elModalCardTextTitle) elModalCardTextTitle.textContent = 'カードテキスト';
    elModalCardText.textContent = '';
    const status = pendingConditionStatus(p);
    if(status && status.text){
      elModalCond.textContent = status.text;
      elModalCond.className = status.state === 'met' ? 'condMet' : (status.state === 'unmet' ? 'condUnmet' : 'condNeutral');
      elModalCond.style.display = 'block';
    }
    const specificEffect = pendingEffectText(p);
    if(specificEffect){
      if(token != null && token !== modalContextToken) return;
      if(elModalCardTextTitle) elModalCardTextTitle.textContent = '発動する効果';
      setRichText(elModalCardText, specificEffect);
      elModalCardTextWrap.classList.add('visible');
      return;
    }
    // Do not fall back to the source card's full ability text here.
    // Effect-resolution popups must show only the currently resolving effect
    // or the short instruction from pendingTextFor().  Full source-card text
    // makes target lists unreadable and violates the modal contract.
    if(pendingHasInlineAutoEffectDetail(p)) return;
    return;
  }
  function setModalChoiceHoverHint(msg){
    const s = String(msg || '').trim();
    if(!s) return;
    elModalCond.textContent = s;
    elModalCond.className = 'condNeutral';
    elModalCond.style.display = 'block';
  }
  function setModalContextFromPending(p){
    modalContextToken += 1;
    const token = modalContextToken;
    if(!p || typeof p !== 'object'){
      clearModalLead();
      return;
    }
    setModalLeadFromPending(p);
    updateModalContextFromPending(p, token).catch(err=>console.error(err));
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
    if(String(st.phase||'') === 'LIVE_SET'){
      const n = Number(st.live_set_limit);
      return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 3;
    }
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
    try{
      const handZone = layout && layout.zones && layout.zones.hand;
      if(handZone){
        const availW = px(handZone.w) - 20;
        const availH = px(handZone.h) - 22 - 10;
        const sz = computeDispSize('portrait', availW, availH);
        if(sz && sz.w > 0 && sz.h > 0){
          stdPortrait = {w: sz.w, h: sz.h};
          stdLandscape = {w: sz.h, h: sz.w};
          if(orient==='landscape') return stdLandscape;
          return stdPortrait;
        }
      }
    }catch(e){}
    const cw = px(451) * 0.38;
    const ch = px(630) * 0.38;
    if(orient==='landscape') return {w: ch, h: cw};
    return {w: cw, h: ch};
  }
  function makeCard(cn, wantOrient, x, y, w, h, capText, onClick, isSelected=false, z=100, noHover=false, forceIntrinsicOrient=null, normalizeNatural=false, instanceId=''){
    const wrap = document.createElement('div');
    wrap.className = 'cardWrap';
    wrap.style.left = x + 'px';
    wrap.style.top = y + 'px';
    wrap.style.width = w + 'px';
    wrap.style.height = h + 'px';
    wrap.style.zIndex = String(z);
    wrap.dataset.baseZ = String(z);
    wrap.dataset.cn = String(cn || '');
    if(instanceId) wrap.dataset.instanceId = String(instanceId);
    if(isSelected){ wrap.classList.add('selected'); wrap.style.zIndex='18000'; wrap.dataset.baseZ='18000'; }

    const intr = forceIntrinsicOrient || intrinsicOrient(cn);
    const needsRotate = (intr !== wantOrient);

    const appendPlainImg = ()=>{
      const img = document.createElement('img');
      img.src = imgUrl(cn, instanceId);
      img.alt = cn;
      img.style.objectFit = 'contain';
      wrap.appendChild(img);
      return img;
    };
    const appendRotatedImg = (rotDeg)=>{
      const inner = document.createElement('div');
      inner.className = 'rot';
      inner.style.transform = `translate(-50%,-50%) rotate(${rotDeg}deg)`;
      inner.style.width = h + 'px';
      inner.style.height = w + 'px';
      inner.style.left = '50%';
      inner.style.top = '50%';

      const img = document.createElement('img');
      img.src = imgUrl(cn, instanceId);
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
      return img;
    };

    if(normalizeNatural){
      const img = appendPlainImg();
      const normalizeLoadedImage = ()=>{
        try{
          const nw = Number(img.naturalWidth || 0);
          const nh = Number(img.naturalHeight || 0);
          if(nw <= 0 || nh <= 0) return;
          const naturalOrient = (nw >= nh) ? 'landscape' : 'portrait';
          if(naturalOrient === wantOrient) return;
          wrap.innerHTML = '';
          // portrait<-landscape : rotate +90 (CW)
          // landscape<-portrait : rotate -90 (CCW)
          appendRotatedImg((wantOrient === 'portrait') ? 90 : -90);
        }catch(e){}
      };
      img.addEventListener('load', normalizeLoadedImage, {once:true});
      // Cached images can already be complete before the load listener runs.
      if(img.complete) setTimeout(normalizeLoadedImage, 0);
    }else if(!needsRotate){
      appendPlainImg();
    }else{
      // portrait<-landscape : rotate +90 (CW)
      // landscape<-portrait : rotate -90 (CCW)
      appendRotatedImg((wantOrient === 'portrait') ? 90 : -90);
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

  function shortCardListForLog(cards, maxN){
    const arr = Array.isArray(cards) ? cards.map(x=>String(x||'').trim()).filter(Boolean) : [];
    if(!arr.length) return '';
    const n = Number.isFinite(Number(maxN)) ? Math.max(1, Number(maxN)) : 3;
    const head = arr.slice(0, n).map(cn => cardDisplayText(cn));
    if(arr.length > n) head.push(`他${arr.length - n}枚`);
    return head.join(' / ');
  }

  function effectEventLabel(ev){
    const t = String(ev && ev.type || '').trim();
    const map = {
      yell: 'YELL',
      additional_yell: 'ADD YELL',
      reroll_yell: 'RE-YELL',
      yell_bladeheart_loss: 'LOSS',
      yell_bladeheart_loss_warn: 'WARN'
    };
    return map[t] || (t ? t.toUpperCase().slice(0, 12) : 'EFFECT');
  }

  function effectEventBody(ev){
    if(!ev || typeof ev !== 'object') return {detail:'', meta:''};
    const type = String(ev.type || '');
    const detail = String(ev.detail || '');
    const src = String(ev.source_cn || '').trim();
    let meta = '';
    if(type === 'yell' || type === 'additional_yell'){
      const revealed = shortCardListForLog(ev.revealed, 3);
      const drew = Array.isArray(ev.drawn) ? ev.drawn.length : Number(ev.drew_count || ev.drew || 0) || 0;
      const drawIcons = Number(ev.draw_icons || ev.draw_icon_count || 0) || 0;
      meta = `${revealed || '公開カードなし'}${drawIcons ? ` / ドローアイコン×${drawIcons}` : ''}${drew ? ` / ${drew}枚ドロー` : ''}`;
    }else if(type === 'reroll_yell'){
      meta = `${src ? cardDisplayText(src) + ' / ' : ''}${shortCardListForLog(ev.moved, 3)}${ev.extra_count ? ` / 追加エール${ev.extra_count}枚` : ''}`;
    }else if(type === 'yell_bladeheart_loss' || type === 'yell_bladeheart_loss_warn'){
      meta = `${shortCardListForLog(ev.cards, 3)}${ev.lost_draw_icons ? ` / 失う対象にドローアイコン×${ev.lost_draw_icons}` : ''}`;
    }else{
      const cards = ev.cards || ev.revealed || ev.moved || [];
      meta = `${src ? cardDisplayText(src) : ''}${cards && cards.length ? (src ? ' / ' : '') + shortCardListForLog(cards, 3) : ''}`;
    }
    return {detail, meta};
  }

  function renderEffectEvents(container, events){
    const list = Array.isArray(events) ? events.filter(ev=>ev && typeof ev === 'object') : [];
    if(!list.length) return;
    const panel = document.createElement('div');
    panel.id = 'effectLogPanel';
    const header = document.createElement('div');
    header.className = 'effectLogHeader';
    const title = document.createElement('span');
    title.textContent = 'EFFECT EVENTS';
    const hint = document.createElement('span');
    hint.className = 'effectLogHint';
    hint.textContent = '最新8件';
    header.appendChild(title);
    header.appendChild(hint);
    panel.appendChild(header);

    for(const ev of list.slice(-8).reverse()){
      const row = document.createElement('div');
      row.className = 'effectLogRow';
      const type = document.createElement('div');
      type.className = 'effectLogType';
      type.textContent = effectEventLabel(ev);
      const body = document.createElement('div');
      body.className = 'effectLogBody';
      const obj = effectEventBody(ev);
      const detail = document.createElement('div');
      detail.className = 'effectLogDetail';
      const seq = ev.seq ? `#${ev.seq} ` : '';
      detail.textContent = `${seq}${obj.detail || effectEventLabel(ev)}`;
      const meta = document.createElement('div');
      meta.className = 'effectLogMeta';
      meta.textContent = obj.meta || `${ev.phase || ''}${ev.turn ? ` / turn ${ev.turn}` : ''}`;
      body.appendChild(detail);
      body.appendChild(meta);
      row.appendChild(type);
      row.appendChild(body);
      panel.appendChild(row);
    }
    container.appendChild(panel);
  }

  function renderLog(zoneEl, lines, events){
    const inner = zoneEl.querySelector('.zoneInner');
    const box = document.createElement('div');
    box.id = 'logBox';
    renderEffectEvents(box, events || []);
    if(debug || (st && st.debug)){
      const raw = document.createElement('div');
      raw.id = 'rawLogText';
      const tailN = (events && events.length) ? 20 : 28;
      raw.textContent = (lines||[]).slice(-tailN).join('\n');
      box.appendChild(raw);
    }
    inner.appendChild(box);
  }

  function renderStatsPanel(){
    if(IS_PUBLIC_VIEW) return;
    document.body.classList.toggle('showStats', !!statsVisible);
    const panel = document.createElement('div');
    panel.className = 'statsPanel';
    const total = document.createElement('div');
    total.className = 'statsTotal';
    total.textContent = `total stats ${totalStageStats()}`;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'statsToggleBtn' + (statsVisible ? ' active' : '');
    btn.textContent = statsVisible ? 'stats表示 ON' : 'stats表示 OFF';
    btn.title = 'ステージ上メンバーごとのstats表示を切り替え';
    btn.addEventListener('click', ev=>{
      ev.stopPropagation();
      statsVisible = !statsVisible;
      render();
    });
    panel.appendChild(total);
    panel.appendChild(btn);
    elZones.appendChild(panel);
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

  function renderTopCard(zoneEl, cn, wantOrient, countText, onClick, opts={}){
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
    let sz = computeDispSize(wantOrient, availW, availH);
    if(opts && opts.useStandardSize){
      const std = standardSize(wantOrient);
      if(std && std.w > 0 && std.h > 0){
        const fit = Math.min(1.0, availW / std.w, availH / std.h);
        const scale = (isFinite(fit) && fit > 0) ? fit : 1.0;
        sz = {w: std.w * scale, h: std.h * scale};
      }
    }
    const x = (zoneW - sz.w)/2;
    const y = Math.max(padTop, padTop + (availH - sz.h)/2);

    const instanceId = opts && opts.instanceId ? String(opts.instanceId) : '';
    const card = makeCard(cn, wantOrient, x, y, sz.w, sz.h, '', (onClick?()=>onClick():null), false, 200, false, null, false, instanceId);
    inner.appendChild(card);

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(countText);
    zoneEl.appendChild(badge);
  }

  function renderVertStack(zoneEl, cards, wantOrient, countText, onClick, {overlap=0.70, maxShow=4, forceIntrinsicOrient=null, instanceIds=[]} = {}){
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
    const allInstanceIds = Array.isArray(instanceIds) ? instanceIds.map(x=>String(x||'')) : [];
    const showInstanceIds = (nShow>0) ? allInstanceIds.slice(Math.max(0, allInstanceIds.length - nShow)) : [];

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
      const instanceId = (i < showInstanceIds.length) ? showInstanceIds[i] : '';
      const card = makeCard(String(cn), wantOrient, x, y, sz.w, sz.h, '', null, false, 200+i, false, forceIntrinsicOrient, false, instanceId);
      inner.appendChild(card);
    });

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(countText);
    zoneEl.appendChild(badge);
  }


  function publicCount(field, fallbackList){
    if(!IS_PUBLIC_VIEW) return Array.isArray(fallbackList) ? fallbackList.length : 0;
    const v = st ? Number(st[field] || 0) : 0;
    if(Number.isFinite(v) && v >= 0) return v;
    return Array.isArray(fallbackList) ? fallbackList.length : 0;
  }

  function renderMaskedHand(zoneEl, count, revealedCards){
    const inner = zoneEl.querySelector('.zoneInner');
    const zoneW = zoneEl.clientWidth;
    const zoneH = zoneEl.clientHeight;
    const padTop = 22;
    const padX = 10;
    const availW = zoneW - padX*2;
    const availH = zoneH - padTop - 10;

    // Use the normal portrait card geometry.  Non-public cards use the local
    // back.png returned by /img?cn=__BACK__.  Cards that were revealed while
    // being added to hand remain public in the hand row until the current turn
    // changes, so public viewers can visually match the known hand card.
    const sz = computeDispSize('portrait', availW, availH);
    stdPortrait = {w: sz.w, h: sz.h};
    stdLandscape = {w: sz.h, h: sz.w};

    const nAll = Math.max(0, Number(count || 0));
    const nShow = Math.min(nAll, 8);
    const revealed = (revealedCards || []).map(x=>String(x||'')).filter(Boolean);
    const revealedShow = revealed.slice(Math.max(0, revealed.length - nShow));
    const revealStart = Math.max(0, nShow - revealedShow.length);
    let step = 0;
    if(nShow <= 1){
      step = 0;
    }else{
      const maxStep = sz.w + px(8);
      const fitStep = (availW - sz.w) / (nShow - 1);
      step = Math.min(maxStep, fitStep);
      if(!isFinite(step) || step < 0) step = 0;
    }

    const totalW = (nShow===0) ? 0 : (sz.w + step*(nShow-1));
    const startX = (availW > totalW) ? (availW - totalW)/2 : 0;
    const baseY = padTop + Math.max(0, (availH - sz.h)/2);

    for(let i=0;i<nShow;i++){
      const x = padX + startX + step*i;
      const y = baseY;
      const ri = i - revealStart;
      const cn = (ri >= 0 && ri < revealedShow.length) ? revealedShow[ri] : '__BACK__';
      const isKnown = cn !== '__BACK__';
      const cap = isKnown ? labelFor(cn) : '';
      // Public-known cards in hand must use their real intrinsic orientation.
      // LIVE cards are force-marked as landscape by publicKnownOrient/cardLooksLive,
      // so they rotate into the portrait hand slot.  Only the non-public back
      // image is forced to portrait.
      const forceIntr = isKnown ? (cardLooksLive(cn) ? 'landscape' : 'portrait') : 'portrait';
      const card = makeCard(cn, 'portrait', x, y, sz.w, sz.h, cap, null, false, 100+i, true, forceIntr);
      if(isKnown){
        card.classList.add('publicKnownHandCard');
      }
      inner.appendChild(card);
    }

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(nAll);
    zoneEl.appendChild(badge);
  }

  function renderHand(zoneEl, cards){
    const inner = zoneEl.querySelector('.zoneInner');
    zoneEl.onclick = (ev)=>{
      if(debugMoveMode && !IS_PUBLIC_VIEW && debugMoveSelection){
        ev.stopPropagation();
        putDebugMoveCard('hand', (Array.isArray(st && st.hand) ? st.hand.length : 0));
      }
    };
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
      const instanceId = zoneInstanceId('hand', i);
      const onHandCardClick = ()=>{
        if(debugMoveMode && !IS_PUBLIC_VIEW) return selectDebugMoveCard('hand', i, cn);
        return toggleSel(i);
      };
      const card = makeCard(cn, 'portrait', x, y, sz.w, sz.h, cap, onHandCardClick, isSel, 100+i, false, null, false, instanceId);
      if(debugSelectionSame('hand', i)) card.classList.add('debugMoveSource');
      const publicIds = publicHandRevealedIds();
      const instanceTrackingReady = !!(st && st.card_instances);
      const publicCardsFallback = (publicIds.length || instanceTrackingReady) ? [] : publicHandRevealedCards();
      if((instanceId && publicIds.includes(String(instanceId))) || (!instanceId && publicCardsFallback.includes(String(cn)))){
        card.classList.add('publicKnownHandCard');
      }
      try{
        const hd = Array.isArray(st && st.hand_detail) ? st.hand_detail[i] : null;
        const baseCost = Number((hd && hd.base_cost) || cardCostFor(cn) || 0);
        const effectiveCost = Number((hd && hd.effective_cost) || baseCost || 0);
        appendCostBadgeCurrent(card, baseCost, effectiveCost, true);
        if(hd && hd.can_activate_from_hand){
          const b = document.createElement('button');
          b.className = 'actBtn';
          b.textContent = '能力';
          b.title = '手札から能力を起動';
          b.addEventListener('click', async ev => {
            ev.stopPropagation();
            st = await apiCmd('activate_from_hand', {hand_idx: i});
            selHand = [];
            updateTop();
            render();
          });
          card.appendChild(b);
        }
      }catch(e){}
      inner.appendChild(card);
    });

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(cards.length);
    zoneEl.appendChild(badge);
  }

  let lastPublicHandRevealSeq = 0;
  // BUILD_TAG: refresh_notice_undo_owner_resync_20260701aq
  // Keep the refresh acknowledgement local to the current browser lifecycle.
  // Persisting it in sessionStorage made undo/replay suppress a freshly restored
  // notice with the same seq.  The server-side ack is only used to close public
  // windows after the owner presses OK.
  let lastRefreshNoticeSeq = 0;
  function setLastRefreshNoticeSeq(v){
    const n = Math.max(0, Number(v || 0) || 0);
    lastRefreshNoticeSeq = n;
  }
  function ownerAckedRefreshSeq(){
    return Number(st && st.refresh_notice_ack_seq || 0) || 0;
  }

  function latestUnseenRefreshNotice(){
    // BUILD_TAG: refresh_notice_undo_replay_reset_20260701am
    // Undo restores an older game snapshot.  If the browser-side acknowledged
    // seq remains larger than the restored state seq, repeating the same action
    // can create the same refresh seq again and the popup would be suppressed.
    // Clamp the local acknowledgement back to the state timeline before looking
    // for unseen refresh notices.
    if(st){
      const stateSeq = Number(st.refresh_notice_seq || 0);
      if(isFinite(stateSeq) && stateSeq < lastRefreshNoticeSeq){
        setLastRefreshNoticeSeq(stateSeq);
      }
    }
    // BUILD_TAG: refresh_notice_undo_owner_resync_20260701aq
    // Owner-side display must not be suppressed by the synchronized public ack;
    // after undo, the owner may legitimately need to see the same seq again.
    // Public windows, however, should obey the owner's ack and close/ignore it.
    const ackFloor = IS_PUBLIC_VIEW
      ? Math.max(Number(lastRefreshNoticeSeq || 0) || 0, ownerAckedRefreshSeq())
      : (Number(lastRefreshNoticeSeq || 0) || 0);
    if(!st || !Array.isArray(st.refresh_notices)) return null;
    let best = null;
    st.refresh_notices.forEach(ev=>{
      if(!ev || typeof ev !== 'object') return;
      const seq = Number(ev.seq || 0);
      if(seq > ackFloor && (!best || seq > Number(best.seq || 0))) best = ev;
    });
    return best;
  }

  function liveCardsFromRefreshNotice(ev){
    const arr = (ev && Array.isArray(ev.returned_live_cards)) ? ev.returned_live_cards : [];
    return arr.map(x=>({cardnumber:String((x && x.cardnumber) || '').trim(), count:Number((x && x.count) || 0)})).filter(x=>x.cardnumber && x.count > 0);
  }

  function uiCalc(px){
    return `calc(${Number(px) || 0}px * var(--uiScale))`;
  }

  function showRefreshNoticePopup(ev){
    if(!ev) return false;
    const seq = Number(ev.seq || 0);
    popup = {type:'refresh_notice', seq:seq, closable:false};
    clearModalLead();
    elModalTitle.textContent = 'リフレッシュ';
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';
    elModalCardTextWrap.classList.remove('visible');
    // BUILD_TAG: responsive_ui_scale_20260701ak
    // Refresh notices are summary UIs, not effect-resolution UIs.  Keep the text
    // compact, remove internal reason keys, align count values, and show returned
    // LIVE cards as a scroll-safe compact list so 4+ kinds / 10+ cards do not clip.
    elModalCond.textContent = '';
    elModalCond.style.display = 'none';

    const total = Number(ev.returned_total || 0);
    const noBh = Number(ev.returned_no_bladeheart_count || 0);
    setRichText(elModalText, 'リフレッシュを行いました。');

    const summary = document.createElement('div');
    summary.style.cssText = [
      'display:grid',
      `grid-template-columns:minmax(${uiCalc(220)},auto) ${uiCalc(96)}`,
      `gap:${uiCalc(8)} ${uiCalc(14)}`,
      'align-items:center',
      `margin:${uiCalc(10)} 0 ${uiCalc(14)} 0`,
      `padding:${uiCalc(12)} ${uiCalc(14)}`,
      'border:1px solid rgba(255,255,255,.18)',
      `border-radius:${uiCalc(12)}`,
      'background:rgba(255,255,255,.045)',
      `max-width:${uiCalc(560)}`
    ].join(';');
    const addSummaryRow = (label, value)=>{
      const lab = document.createElement('div');
      lab.textContent = label;
      lab.style.cssText = `font-size:${uiCalc(16)};line-height:1.35;color:rgba(255,255,255,.88);white-space:normal;`;
      const val = document.createElement('div');
      val.textContent = `${value}枚`;
      val.style.cssText = [
        'justify-self:end',
        `min-width:${uiCalc(76)}`,
        `padding:${uiCalc(5)} ${uiCalc(10)}`,
        'border-radius:999px',
        'background:rgba(255,214,64,.18)',
        'border:1px solid rgba(255,214,64,.55)',
        'color:#ffe066',
        `font-size:${uiCalc(20)}`,
        'font-weight:900',
        'line-height:1',
        'text-align:right',
        'font-variant-numeric:tabular-nums'
      ].join(';');
      summary.appendChild(lab);
      summary.appendChild(val);
    };
    addSummaryRow('山札に戻った総枚数', total);
    addSummaryRow('ブレードハートを持たないカード', noBh);
    elModalCards.appendChild(summary);

    const lives = liveCardsFromRefreshNotice(ev);
    const section = document.createElement('div');
    section.style.cssText = [
      `margin-top:${uiCalc(6)}`,
      'border:1px solid rgba(111,210,255,.34)',
      `border-radius:${uiCalc(12)}`,
      'background:rgba(20,70,80,.24)',
      'overflow:hidden',
      `max-width:${uiCalc(720)}`
    ].join(';');
    const head = document.createElement('div');
    head.textContent = lives.length ? '山札に戻ったライブカード' : '山札に戻ったライブカード: なし';
    head.style.cssText = [
      `padding:${uiCalc(9)} ${uiCalc(12)}`,
      `font-size:${uiCalc(17)}`,
      'font-weight:800',
      'color:#e9fbff',
      'background:rgba(111,210,255,.12)',
      'border-bottom:1px solid rgba(111,210,255,.22)'
    ].join(';');
    section.appendChild(head);

    if(lives.length){
      const list = document.createElement('div');
      list.style.cssText = [
        'display:grid',
        'grid-template-columns:repeat(auto-fit,minmax(270px,1fr))',
        `gap:${uiCalc(8)}`,
        `padding:${uiCalc(10)}`,
        `max-height:min(calc(var(--pmH) * 0.40), ${uiCalc(360)})`,
        'overflow-y:auto',
        'overflow-x:hidden',
        'box-sizing:border-box'
      ].join(';');
      lives.forEach((it)=>{
        const cn = it.cardnumber;
        const row = document.createElement('div');
        row.style.cssText = [
          'display:grid',
          `grid-template-columns:${uiCalc(58)} minmax(0,1fr) ${uiCalc(46)}`,
          'align-items:center',
          `gap:${uiCalc(9)}`,
          `min-height:${uiCalc(48)}`,
          `padding:${uiCalc(6)} ${uiCalc(8)}`,
          'border:1px solid rgba(255,255,255,.14)',
          `border-radius:${uiCalc(10)}`,
          'background:rgba(0,0,0,.18)',
          'box-sizing:border-box'
        ].join(';');
        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;
        img.style.cssText = `width:${uiCalc(58)};height:${uiCalc(38)};object-fit:contain;border-radius:${uiCalc(5)};background:rgba(255,255,255,.04);`;
        const nameBox = document.createElement('div');
        nameBox.style.cssText = 'min-width:0;display:flex;flex-direction:column;gap:2px;';
        const name = document.createElement('div');
        name.textContent = cardNameFor(cn) || cn;
        name.style.cssText = `font-size:${uiCalc(15)};line-height:1.25;color:#fff;white-space:normal;overflow:visible;word-break:break-word;`;
        const code = document.createElement('div');
        code.textContent = cn;
        code.style.cssText = `font-size:${uiCalc(11)};line-height:1.15;color:rgba(255,255,255,.55);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;`;
        nameBox.appendChild(name);
        nameBox.appendChild(code);
        const cnt = document.createElement('div');
        cnt.textContent = `×${it.count}`;
        cnt.style.cssText = [
          'justify-self:end',
          `min-width:${uiCalc(38)}`,
          `padding:${uiCalc(4)} ${uiCalc(7)}`,
          'border-radius:999px',
          'background:rgba(255,255,255,.12)',
          'border:1px solid rgba(255,255,255,.24)',
          'color:#fff',
          `font-size:${uiCalc(17)}`,
          'font-weight:900',
          'font-variant-numeric:tabular-nums',
          'text-align:right'
        ].join(';');
        row.appendChild(img);
        row.appendChild(nameBox);
        row.appendChild(cnt);
        list.appendChild(row);
      });
      section.appendChild(list);
    }
    elModalCards.appendChild(section);

    const ok = document.createElement('button');
    ok.className = 'miniBtn';
    ok.textContent = 'OK';
    ok.addEventListener('click', async (ev2)=>{
      ev2.stopPropagation();
      setLastRefreshNoticeSeq(Math.max(lastRefreshNoticeSeq, seq));
      if(!IS_PUBLIC_VIEW){
        try{
          st = await apiCmd('ack_refresh_notice', {seq});
          updateTop();
        }catch(e){ console.warn(e); }
      }
      closePopup();
      render();
    });
    elModalActions.appendChild(ok);
    elMask.style.display = 'block';
    applyPopupPeekState();
    return true;
  }

  function maybeShowRefreshNotice(){
    const ev = latestUnseenRefreshNotice();
    if(ev){
      if(popup && popup.type === 'refresh_notice' && Number(popup.seq || 0) === Number(ev.seq || 0)) return true;
      showRefreshNoticePopup(ev);
      return true;
    }
    if(popup && popup.type === 'refresh_notice'){
      // If the owner window acknowledged the notice, public windows close it on poll.
      closePopup();
    }
    return false;
  }

  function publicHandRevealedCards(){
    const ids = publicHandRevealedIds();
    if(ids.length){
      return ids.map(iid=>{
        const meta = instanceMeta(iid);
        return String((meta && meta.cardnumber) || '');
      }).filter(Boolean);
    }
    if(!st || !Array.isArray(st.public_hand_revealed_cards)) return [];
    return st.public_hand_revealed_cards.map(x=>String(x||'')).filter(Boolean);
  }

  function publicHandRevealedIds(){
    const out = [];
    const seen = new Set();
    function addMany(list){
      if(!Array.isArray(list)) return;
      list.forEach(x=>{
        const iid = String(x || '').trim();
        if(iid && !seen.has(iid)){
          seen.add(iid);
          out.push(iid);
        }
      });
    }
    addMany(st && st.public_hand_revealed_instance_ids);
    addMany(st && st.card_instances && st.card_instances.public_hand_revealed);
    return out;
  }

  function renderPublicKnownHandPanel(){
    // The separate bottom-right "revealed hand" mini panel was removed.
    // Publicly revealed cards are represented in the hand row itself.
    const panel = document.getElementById('publicKnownHandPanel');
    if(panel){
      panel.innerHTML = '';
      panel.style.display = 'none';
    }
  }

  function flashCardsByNumber(cardNumbers){
    const want = new Set((cardNumbers||[]).map(x=>String(x||'')).filter(Boolean));
    if(!want.size) return;
    document.querySelectorAll('.cardWrap').forEach(el=>{
      const cn = String(el.dataset.cn || '');
      if(want.has(cn)){
        el.classList.remove('publicRevealFlash');
        void el.offsetWidth;
        el.classList.add('publicRevealFlash');
        setTimeout(()=>{ try{ el.classList.remove('publicRevealFlash'); }catch(e){} }, 2600);
      }
    });
  }

  function flashCardsByInstanceOrNumber(instanceIds, cardNumbers){
    const ids = new Set((instanceIds||[]).map(x=>String(x||'')).filter(Boolean));
    if(ids.size){
      document.querySelectorAll('.cardWrap').forEach(el=>{
        const iid = String(el.dataset.instanceId || '');
        if(ids.has(iid)){
          el.classList.remove('publicRevealFlash');
          void el.offsetWidth;
          el.classList.add('publicRevealFlash');
          setTimeout(()=>{ try{ el.classList.remove('publicRevealFlash'); }catch(e){} }, 2600);
        }
      });
      return;
    }
    flashCardsByNumber(cardNumbers || []);
  }

  function showPublicRevealFloat(ev){
    const cards = (ev && Array.isArray(ev.display_cards)) ? ev.display_cards.map(x=>String(x||'')).filter(Boolean) : [];
    if(!cards.length) return;
    const box = document.createElement('div');
    box.className = 'publicRevealFloat';
    const title = document.createElement('div');
    title.className = 'publicRevealFloatTitle';
    title.textContent = '公開して手札に加えました';
    box.appendChild(title);
    cards.forEach((cn, idx)=>{
      const orient = intrinsicOrient(cn);
      const d = standardSize(orient);
      const card = makeCard(cn, orient, 0, 0, d.w*0.48, d.h*0.48, cardNameFor(cn), null, false, 500+idx, true);
      card.style.position = 'relative';
      card.style.left = '0';
      card.style.top = '0';
      card.classList.add('publicRevealFlash');
      box.appendChild(card);
    });
    document.body.appendChild(box);
    setTimeout(()=>{ try{ box.remove(); }catch(e){} }, 3000);
  }

  function consumePublicHandRevealEvents(){
    if(!st || !Array.isArray(st.public_hand_reveal_events)) return;
    let maxSeq = lastPublicHandRevealSeq;
    st.public_hand_reveal_events.forEach(ev=>{
      const seq = Number(ev && ev.seq || 0);
      if(seq > lastPublicHandRevealSeq){
        showPublicRevealFloat(ev);
        flashCardsByInstanceOrNumber((ev && ev.display_instance_ids) || [], []);
        if(seq > maxSeq) maxSeq = seq;
      }
    });
    lastPublicHandRevealSeq = maxSeq;
  }

  function appendChoiceCardImage(btn, cn, wantOrient='portrait'){
    const intr = intrinsicOrient(cn);
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    if(intr === wantOrient){
      const img = document.createElement('img');
      img.src = imgUrl(cn);
      img.alt = cn;
      btn.appendChild(img);
      return;
    }

    const inner = document.createElement('div');
    inner.className = 'rot';
    inner.style.position = 'absolute';
    inner.style.left = '50%';
    inner.style.top = '50%';
    inner.style.width = (btn.clientHeight || btn.offsetHeight || 0) + 'px';
    inner.style.height = (btn.clientWidth || btn.offsetWidth || 0) + 'px';
    inner.style.transform = (wantOrient === 'portrait')
      ? 'translate(-50%, -50%) rotate(90deg)'
      : 'translate(-50%, -50%) rotate(-90deg)';
    inner.style.transformOrigin = 'center center';

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
    btn.appendChild(inner);
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
      const isBack = (cn === '__BACK__');
      const instanceId = zoneInstanceId('set_zone', i);
      const card = makeCard(cn, 'landscape', x, y, sz.w, sz.h, '', null, false, 100+i, isBack, isBack ? 'portrait' : null, false, instanceId);
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
      wrap.style.cssText = ['position:relative', `width:${uiCalc(totalW)}`, `height:${uiCalc(ICO2)}`, 'flex-shrink:0'].join(';');
      icons.forEach((ico, i)=>{
        const img = document.createElement('img');
        img.src = ico.src; img.alt = ico.alt;
        img.style.cssText = ['position:absolute', `left:${uiCalc(STEP2*i)}`, 'top:0', `width:${uiCalc(ICO2)}`, `height:${uiCalc(ICO2)}`, 'object-fit:contain', `z-index:${10+i}`].join(';');
        img.onerror = ()=>{
          const sp = document.createElement('span');
          sp.textContent = ico.fallbackText;
          sp.style.cssText = ['position:absolute', `left:${uiCalc(STEP2*i)}`, 'top:0', `width:${uiCalc(ICO2)}`, `height:${uiCalc(ICO2)}`, 'display:flex','align-items:center','justify-content:center',`font-size:${uiCalc(ICO2-2)}`, `color:${ico.fallbackColor}`, `z-index:${10+i}`].join(';');
          img.replaceWith(sp);
        };
        wrap.appendChild(img);
      });
      return wrap;
    };
    const makeIconRow2 = (signText, stack, titleAll)=>{
      const row2 = document.createElement('div');
      row2.title = titleAll;
      row2.style.cssText = `display:flex;align-items:center;gap:${uiCalc(2)};`;
      const sgn = document.createElement('span');
      sgn.textContent = signText;
      sgn.style.cssText = ['color:#fff',`font-size:${uiCalc(11)}`,'font-weight:700','line-height:1','flex-shrink:0'].join(';');
      row2.appendChild(sgn);
      row2.appendChild(stack);
      return row2;
    };
    const ov2 = document.createElement('div');
    ov2.style.cssText = ['position:absolute','right:0',`top:${uiCalc(14)}`,'display:flex','flex-direction:column','align-items:flex-end',`gap:${uiCalc(3)}`,`padding:${uiCalc(3)} ${uiCalc(4)}`,'background:rgba(0,0,0,0.62)',`border-radius:${uiCalc(6)} 0 0 ${uiCalc(6)}`,'pointer-events:none','z-index:50'].join(';');
    for(const [col, cnt] of orderedHeartEntries(reqDelta)){
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
      if(debugMoveMode && !IS_PUBLIC_VIEW){
        if(debugMoveSelection) return putDebugMoveCard('stage', null, slotKey);
        setBanner('移動するカードを選択してください');
        return;
      }
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
    const underCardsForButton = Array.isArray(slotObj.under_cards) ? slotObj.under_cards.map(x=>String(x||'')).filter(Boolean) : [];
    // spec: same scale for all cards; portrait is reference scale
    const szPortrait = computeDispSize('portrait', availW, availH);
    stdPortrait = {w: szPortrait.w, h: szPortrait.h};
    stdLandscape = {w: szPortrait.h, h: szPortrait.w};
    // wait → rotate in place at same scale (swap w/h, render as landscape)
    const sz = isWait ? {w: szPortrait.h, h: szPortrait.w} : szPortrait;
    const dispOrient = isWait ? 'landscape' : 'portrait';
    // wait card is wider than zone → allow overflow so it's not clipped
    inner.style.overflow = (isWait || underCardsForButton.length > 0) ? 'visible' : 'hidden';
    const x = (zoneW - sz.w)/2;
    const y = padTop + Math.max(0, (availH - sz.h)/2);

    // energies under this member (render behind)
    try{
      const underN = Number(slotObj.energy_under||0);
      if(underN > 0){
        const dx = sz.w * 0.05;
        const dy = sz.w * 0.05;
        let lastEnergyPos = null;
        for(let i=0;i<underN;i++){
          const ex = x + dx*(i+1);
          const ey = y + dy*(i+1);
          const ecard = makeCard('__ENERGY__', 'portrait', ex, ey, sz.w, sz.h, '', null, false, 350+i, true);
          ecard.classList.add('underEnergy');
          inner.appendChild(ecard);
          lastEnergyPos = {x: ex, y: ey};
        }
        if(lastEnergyPos){
          const badge = document.createElement('div');
          badge.className = 'underEnergyBadge';
          badge.style.left = `${lastEnergyPos.x + sz.w - 5}px`;
          badge.style.top = `${lastEnergyPos.y + sz.h - 5}px`;
          const icon = document.createElement('span');
          icon.className = 'underEnergyBadgeIcon';
          const count = document.createElement('span');
          count.className = 'underEnergyBadgeCount';
          count.textContent = `×${underN}`;
          badge.appendChild(icon);
          badge.appendChild(count);
          inner.appendChild(badge);
        }
      }
      const underCards = Array.isArray(slotObj.under_cards) ? slotObj.under_cards : [];
      if(underCards.length > 0){
        const dx = sz.w * 0.055;
        const dy = sz.w * 0.055;
        underCards.forEach((ucn, i)=>{
          const ux = x - dx*(i+1);
          const uy = y + dy*(i+1);
          const ucard = makeCard(ucn, 'portrait', ux, uy, sz.w, sz.h, '', null, false, 330+i, true);
          ucard.classList.add('underEnergy');
          inner.appendChild(ucard);
        });
      }
    }catch(e){}
    const instanceId = stageInstanceId(slotKey);
    const onStageCardClick = ()=>{
      if(debugMoveMode && !IS_PUBLIC_VIEW){
        if(debugMoveSelection && !debugSelectionSame('stage', -1, slotKey)) return putDebugMoveCard('stage', null, slotKey);
        return selectDebugMoveCard('stage', -1, cn, slotKey);
      }
      return doPlayHere();
    };
    const card = makeCard(cn, dispOrient, x, y, sz.w, sz.h, labelFor(cn), onStageCardClick, false, 400, false, null, false, instanceId);
    if(debugSelectionSame('stage', -1, slotKey)) card.classList.add('debugMoveSource');
    try{
      const sb = document.createElement('div');
      sb.className = 'stageStatsBadge';
      sb.textContent = `stats ${stageStatsFor(slotKey, slotObj)}`;
      card.appendChild(sb);
    }catch(e){}
    try{
      if(underCardsForButton.length > 0){
        const ub = document.createElement('button');
        ub.className = 'underInspectBtn stageOutside';
        ub.type = 'button';
        ub.textContent = `下部確認 ${underCardsForButton.length}`;
        ub.title = 'このメンバーの下に置かれているメンバーカードを確認';
        ub.style.left = `${Math.max(2, x + (sz.w - px(92)) / 2)}px`;
        ub.style.top = `${y + sz.h + px(6)}px`;
        ub.addEventListener('click', ev=>{
          ev.stopPropagation();
          openUnderCardsPopup(`${slotKey} 下部カード`, underCardsForButton, 'このメンバーの下に置かれているメンバーカードです。');
        });
        inner.appendChild(ub);
      }
    }catch(e){}

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

    // manual active/wait toggle button (beside L/C/R area label)
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
      zoneEl.appendChild(tb);
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
        const baseCost = Number(det.base_cost || 0);
        const effectiveCost = Number(det.effective_cost || 0);
        const showCostBadge = effectiveCost > 0 && effectiveCost !== baseCost;
        const tmpHearts = Object.assign({}, det.temp_hearts || {});
        const successHearts = Object.assign({}, det.success_zone_hearts_bonus || {});
        const alwHearts = Object.assign({}, det.always_hearts_bonus || {});

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
        const totalBlade = tmpBlade + alwBlade;

        const hasBonus = showCostBadge || totalBlade !== 0 || alwScore !== 0 || Object.keys(alwHearts).some(k=>Number(alwHearts[k])!==0) || Object.keys(successHearts).some(k=>Number(successHearts[k])!==0) || Object.keys(tmpHearts).some(k=>Number(tmpHearts[k])!==0);
        if(hasBonus){
          // オーバーレイ本体（縦並び、カード右上）
          // heart / blade は modal の setRichText と同じ texticons map を使う
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

          if(showCostBadge){
            const cb = document.createElement('div');
            cb.className = 'costBadgeCurrent';
            const costDelta = effectiveCost - baseCost;
            cb.title = `current cost ${effectiveCost} (base ${baseCost}, ${costDelta>=0?'bonus':'reduction'} ${Math.abs(costDelta)})`;
            cb.textContent = formatCostBadgeText(baseCost, effectiveCost);
            cb.style.cssText = [
              'display:inline-flex',
              'align-items:center',
              'justify-content:center',
              `min-width:${uiCalc(38)}`,
              'height:18px',
              'padding:1px 5px',
              'border-radius:999px',
              'background:rgba(245,245,245,.94)',
              'color:#111',
              'border:1px solid rgba(0,0,0,.28)',
              'box-shadow:0 1px 5px rgba(0,0,0,.38)',
              'font-size:10px',
              'font-weight:900',
              'line-height:1',
              'white-space:nowrap',
              'margin-bottom:1px',
            ].join(';');
            ov.appendChild(cb);
          }

          const appendBonusIconRow = (signText, specs, titleStr)=>{
            if(!specs || !specs.length) return;
            ov.appendChild(makeTextIconRow(signText, makeTextIconStack(specs, '', 16, 10), titleStr));
          };
          const appendHeartBonusRows = (bonusMap, suffix)=>{
            for(const [col, cnt] of orderedHeartEntries(bonusMap || {})){
              const n = Number(cnt);
              if(!n) continue;
              const token = HEART_TOKEN_BY_COLOR[col] || '<(任意)>';
              const label = HEART_LABEL_BY_COLOR[col] || col;
              const absn = Math.abs(n);
              const specs = Array.from({length: absn}, ()=>({token, alt: label}));
              appendBonusIconRow(n > 0 ? '＋' : '－', specs, `${label}ハート ${n > 0 ? '+' : ''}${n}${suffix || ''}`);
            }
          };

          // ブレードスタック
          if(totalBlade !== 0){
            const absBlade = Math.abs(totalBlade);
            const specs = Array.from({length: absBlade}, ()=>({token:'<(ブレード)>', alt:'ブレード'}));
            const titleStr = `ブレード ${totalBlade > 0 ? '+' : ''}${totalBlade}`;
            appendBonusIconRow(totalBlade > 0 ? '＋' : '－', specs, titleStr);
          }

          // 常時ハート / 成功置き場参照ハート / 一時ハート（色別）
          appendHeartBonusRows(alwHearts, '');
          appendHeartBonusRows(successHearts, '（成功置き場参照）');
          appendHeartBonusRows(tmpHearts, '（一時）');

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
      // BUILD_TAG: yell_no_bh_dual_menu_refresh_undo_20260722a
      // Server undo restores the app-side refresh acknowledgement captured with
      // that snapshot, so the browser mirrors it instead of forcing every undo
      // back to the refresh notice.
      try{
        const ackSeq = Number(st && st.refresh_notice_ack_seq || 0);
        setLastRefreshNoticeSeq(Number.isFinite(ackSeq) ? ackSeq : 0);
      }catch(e){}
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
      if(popup && popup.type === 'refresh_notice'){
        const seq = Number(popup.seq || 0);
        setLastRefreshNoticeSeq(Math.max(lastRefreshNoticeSeq, seq));
        if(!IS_PUBLIC_VIEW){
          try{
            st = await apiCmd('ack_refresh_notice', {seq});
            updateTop();
          }catch(e){ console.warn(e); }
        }
        closePopup();
        render();
        return;
      }
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

  function appendYellRevealDrawNotice(p){
    if(!p) return;
    const n = Number(p.yell_draw_icon_count || 0);
    if(!Number.isFinite(n) || n <= 0) return;
    const drew = Number(p.yell_draw_drew_count || 0);
    const label = String(p.yell_draw_notice_label || `ドローアイコン×${n} → ${Number.isFinite(drew) ? drew : 0}枚ドロー済み`);
    const note = document.createElement('div');
    note.className = 'yellRevealDrawNotice';
    note.title = String(p.yell_draw_notice_text || `このエールで公開されたドローアイコン×${n}は処理済みです。`);
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = 'DRAW';
    const body = document.createElement('span');
    body.textContent = label;
    note.appendChild(tag);
    note.appendChild(body);
    elModalText.appendChild(document.createElement('br'));
    elModalText.appendChild(note);
  }

  function isYellRevealPending(p){
    if(!p) return false;
    const label = String((p && p.label) || '');
    const kind = String((p && p.kind) || '');
    return !!(p.yell_reveal_ack || p.yell_draw_icon_count || p.yell_heart_counts || p.yell_score_icon_count)
      || label.includes('エール公開')
      || kind === 'choose_yell_revealed_to_green_then_extra_yell';
  }

  function openYellRevealPopup(p){
    const displayCards = Array.isArray(p && p.display_cards) ? p.display_cards.map(x=>String(x||'')).filter(Boolean) : [];
    const helperText = String((p && (p.text || p.prompt || p.message)) ? (p.text || p.prompt || p.message) : '公開されたカードを確認');
    const isYell = isYellRevealPending(p);
    const title = String((p && p.label) ? p.label : (isYell ? 'エール公開カード確認' : '公開カード確認'));
    popup = {type:'pending', title, cards: displayCards.slice(), closable:false, helperText};
    elModalTitle.textContent = title;
    setRichText(elModalText, helperText);
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const wrap = document.createElement('div');
    wrap.className = 'yellRevealSummary';

    if(isYell){
      const summary = computeYellRevealSummary(displayCards, p || {});
      const makeMetric = ({token='', label='', count=0, sub='', compact=false})=>{
        const box = document.createElement('div');
        box.className = 'yellRevealMetric' + (compact ? ' compact' : '');
        const lab = document.createElement('div');
        lab.className = 'yellRevealMetricLabel';
        if(token) lab.appendChild(makeTextIconImg(token, label, '1.15em'));
        const text = document.createElement('span');
        text.textContent = label;
        lab.appendChild(text);
        const cnt = document.createElement('div');
        cnt.className = 'yellRevealMetricCount';
        cnt.textContent = String(Number(count || 0));
        box.appendChild(lab);
        box.appendChild(cnt);
        if(sub){
          const s = document.createElement('div');
          s.className = 'yellRevealMetricSub';
          s.textContent = sub;
          box.appendChild(s);
        }
        return box;
      };

      const heartSec = document.createElement('div');
      heartSec.className = 'yellRevealSection';
      const heartTitle = document.createElement('div');
      heartTitle.className = 'yellRevealSectionTitle';
      heartTitle.textContent = '公開ハート';
      const heartGrid = document.createElement('div');
      const hasAny = Number(summary.heartCounts.any || 0) > 0;
      heartGrid.className = 'yellRevealHeartGrid' + (hasAny ? ' withAny' : '');
      [['pink','桃'],['red','赤'],['yellow','黄'],['green','緑'],['blue','青'],['purple','紫'],['all','ALL']].forEach(([k,lab])=>{
        heartGrid.appendChild(makeMetric({token: HEART_TOKEN_BY_COLOR[k], label: lab, count: Number(summary.heartCounts[k] || 0)}));
      });
      if(hasAny){
        heartGrid.appendChild(makeMetric({token: HEART_TOKEN_BY_COLOR.any, label: '任意', count: Number(summary.heartCounts.any || 0)}));
      }
      heartSec.appendChild(heartTitle);
      heartSec.appendChild(heartGrid);
      wrap.appendChild(heartSec);

      const iconSec = document.createElement('div');
      iconSec.className = 'yellRevealSection';
      const iconTitle = document.createElement('div');
      iconTitle.className = 'yellRevealSectionTitle';
      iconTitle.textContent = '公開アイコン';
      const iconBar = document.createElement('div');
      iconBar.className = 'yellRevealIconGrid';
      const appendIconPair = (label, count)=>{
        const item = document.createElement('div');
        item.className = 'yellRevealIconMetric';
        const lab = document.createElement('div');
        lab.className = 'yellRevealIconMetricLabel';
        lab.textContent = label;
        const cnt = document.createElement('div');
        cnt.className = 'yellRevealIconMetricValue';
        cnt.textContent = String(Number(count || 0));
        item.appendChild(lab);
        item.appendChild(cnt);
        iconBar.appendChild(item);
      };
      appendIconPair('ドロー', Number(summary.drawIcons || 0));
      appendIconPair('スコアUP', Number(summary.scoreIcons || 0));
      appendIconPair('ダブル無色', Number(summary.doubleColorlessIcons || 0));
      appendIconPair('BHなし', Number(summary.noBladeHeartCards || 0));
      iconSec.appendChild(iconTitle);
      iconSec.appendChild(iconBar);
      wrap.appendChild(iconSec);
    }

    const cardSec = document.createElement('div');
    cardSec.className = 'yellRevealSection';
    const cardTitle = document.createElement('div');
    cardTitle.className = 'yellRevealSectionTitle';
    cardTitle.textContent = `${isYell ? '公開カード' : '確認カード'} (${displayCards.length})`;
    cardSec.appendChild(cardTitle);
    const cardRow = document.createElement('div');
    cardRow.className = 'yellRevealCardRow';
    const dimsP = standardSize('portrait');
    const dimsL = standardSize('landscape');
    const scale = 1.00;
    const overlapCards = displayCards.length >= 5;
    displayCards.forEach((cn, idx)=>{
      const orient = intrinsicOrient(cn);
      const base = (orient === 'landscape') ? dimsL : dimsP;
      const cw = Math.round(base.w * scale);
      const ch = Math.round(base.h * scale);
      const card = makeCard(cn, orient, 0, 0, cw, ch, '', null, false, 100 + idx, false, null, true);
      card.style.position = 'relative';
      if(overlapCards && idx > 0){
        card.style.marginLeft = '-' + Math.round(cw * 0.34) + 'px';
      }
      cardRow.appendChild(card);
    });
    cardSec.appendChild(cardRow);
    wrap.appendChild(cardSec);

    elModalCards.appendChild(wrap);
    elMask.style.display = 'block';
    applyPopupPeekState();
  }



  function openLiveAttemptSummaryPopup(p){
    const summary = (p && p.live_attempt_summary) ? p.live_attempt_summary : {};
    const result = String(summary.result || p.result || '').toLowerCase();
    const ok = !!(summary.ok || result === 'success');
    popup = {type:'pending', title:'ライブ成功確認', closable:false};
    elModalTitle.textContent = 'ライブ成功確認';
    setRichText(elModalText, String((p && p.text) || '所持ハート合計と必要ハート合計、成功/失敗・スコアを確認してください。'));
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const wrap = document.createElement('div');
    wrap.className = 'liveAttemptSummary';

    const score = summary.score || {};
    const top = document.createElement('div');
    top.className = 'liveAttemptTop';
    const res = document.createElement('div');
    res.className = 'liveAttemptResult ' + (ok ? 'success' : 'fail');
    res.textContent = ok ? 'SUCCESS' : 'FAIL';
    top.appendChild(res);
    const scoreBox = document.createElement('div');
    scoreBox.className = 'liveAttemptScore';
    const liveTotal = Number(score.live_total || 0);
    scoreBox.textContent = `スコア: ${liveTotal}`;
    top.appendChild(scoreBox);
    const note = document.createElement('div');
    note.className = 'liveAttemptNote';
    note.textContent = 'ライブ成功時効果解決前の判定結果です。';
    top.appendChild(note);
    wrap.appendChild(top);

    const colorsOwned = ['pink','red','yellow','green','blue','purple','all','any'];
    const colorsRequired = ['pink','red','yellow','green','blue','purple','all','any'];
    const mkCounts = (x)=> x && typeof x === 'object' ? x : {};
    const addCounts = (rows, key)=>{
      const out = {};
      (Array.isArray(rows) ? rows : []).forEach(row=>{
        const obj = mkCounts(row && row[key]);
        Object.keys(obj).forEach(k=>{ out[k] = Number(out[k] || 0) + Number(obj[k] || 0); });
      });
      return out;
    };
    const owned = summary.owned_hearts || {};
    const stage = mkCounts(owned.stage);
    const yell = mkCounts(owned.yell);
    const total = mkCounts(owned.total);
    const reqTotal = mkCounts(summary.required_hearts_total);
    const reqEffective = Object.keys(mkCounts(reqTotal.effective)).length ? mkCounts(reqTotal.effective) : addCounts(summary.live_cards, 'required_effective');
    const reqOriginal = Object.keys(mkCounts(reqTotal.original)).length ? mkCounts(reqTotal.original) : addCounts(summary.live_cards, 'required_original');
    const sumHeartCounts = (obj, keys)=> keys.reduce((acc, key)=>acc + Number((obj && obj[key]) || 0), 0);
    const ownedCountTotal = Number.isFinite(Number(owned.count_total))
      ? Number(owned.count_total)
      : sumHeartCounts(total, colorsOwned);
    const requiredCountTotal = Number.isFinite(Number(reqTotal.effective_count))
      ? Number(reqTotal.effective_count)
      : sumHeartCounts(reqEffective, colorsRequired);

    const makeLiveMetric = ({col='', label='', token='', countText='0', sub=''})=>{
      const box = document.createElement('div');
      box.className = 'yellRevealMetric';
      const lab = document.createElement('div');
      lab.className = 'yellRevealMetricLabel';
      const tk = token || HEART_TOKEN_BY_COLOR[col];
      const lb = label || HEART_LABEL_BY_COLOR[col] || col;
      if(tk) lab.appendChild(makeTextIconImg(tk, lb, '1.15em'));
      const text = document.createElement('span');
      text.textContent = lb;
      lab.appendChild(text);
      const cnt = document.createElement('div');
      cnt.className = 'yellRevealMetricCount';
      cnt.textContent = String(countText);
      box.appendChild(lab);
      box.appendChild(cnt);
      const s = document.createElement('div');
      s.className = 'yellRevealMetricSub';
      s.textContent = sub || '';
      box.appendChild(s);
      return box;
    };

    const makeHeartTotalMetric = ({countText='0', sub=''})=>{
      const box = document.createElement('div');
      box.className = 'liveAttemptHeartTotal';
      const lab = document.createElement('div');
      lab.className = 'liveAttemptHeartTotalLabel';
      const mark = document.createElement('span');
      mark.className = 'liveAttemptHeartTotalMark';
      mark.textContent = 'Σ';
      const txt = document.createElement('span');
      txt.textContent = '総数';
      lab.appendChild(mark);
      lab.appendChild(txt);
      const cnt = document.createElement('div');
      cnt.className = 'liveAttemptHeartTotalCount';
      cnt.textContent = String(countText);
      const subEl = document.createElement('div');
      subEl.className = 'liveAttemptHeartTotalSub';
      subEl.textContent = String(sub || '');
      box.appendChild(lab);
      box.appendChild(cnt);
      box.appendChild(subEl);
      return box;
    };

    const ownedSec = document.createElement('div');
    ownedSec.className = 'liveAttemptSection';
    const ownedTitle = document.createElement('div');
    ownedTitle.className = 'liveAttemptSectionTitle';
    ownedTitle.textContent = '所持ハート合計（盤面＋エール）';
    const ownedGrid = document.createElement('div');
    // Owned and required rows both show six colors, ALL, and unspecified/any
    // so the rules-facing columns line up even when one side is zero.
    ownedGrid.className = 'liveAttemptHeartGrid';
    colorsOwned.forEach(col=>{
      const st = Number(stage[col] || 0);
      const ye = Number(yell[col] || 0);
      const tt = Number(total[col] || 0);
      ownedGrid.appendChild(makeLiveMetric({col, label: col === 'any' ? '不特定' : '', countText:`${st}+${ye}`, sub:`合計 ${tt}`}));
    });
    ownedGrid.appendChild(makeHeartTotalMetric({countText:String(ownedCountTotal), sub:'所持ハート'}));
    ownedSec.appendChild(ownedTitle);
    ownedSec.appendChild(ownedGrid);
    wrap.appendChild(ownedSec);

    const reqSec = document.createElement('div');
    reqSec.className = 'liveAttemptSection';
    const reqTitle = document.createElement('div');
    reqTitle.className = 'liveAttemptSectionTitle';
    reqTitle.textContent = '必要ハート合計';
    const reqGrid = document.createElement('div');
    // Required-heart comparison always includes the unspecified/any-heart slot.
    // Hiding the zero column made the rules-facing category disappear entirely.
    reqGrid.className = 'liveAttemptHeartGrid';
    colorsRequired.forEach(col=>{
      const eff = Number(reqEffective[col] || 0);
      const orig = Number(reqOriginal[col] || 0);
      const sub = (orig !== eff) ? `元 ${orig}` : '';
      reqGrid.appendChild(makeLiveMetric({col, label: col === 'any' ? '不特定' : '', countText:String(eff), sub}));
    });
    reqGrid.appendChild(makeHeartTotalMetric({countText:String(requiredCountTotal), sub:'必要ハート'}));
    reqSec.appendChild(reqTitle);
    reqSec.appendChild(reqGrid);
    wrap.appendChild(reqSec);

    elModalCards.appendChild(wrap);
    const btnOk = document.createElement('button');
    btnOk.className = 'miniBtn';
    btnOk.textContent = '確認';
    let submitting = false;
    btnOk.addEventListener('click', async ev=>{
      ev.stopPropagation();
      if(submitting) return;
      submitting = true;
      st = await apiCmd('resolve_pending', {idx:0, choice:'ok'});
      selHand = [];
      updateTop();
      render();
    });
    elModalActions.appendChild(btnOk);
    elMask.style.display = 'block';
    applyPopupPeekState();
  }

  function popupCardSurfaceMetrics(targetCards, cardsList){
    const dimsP0 = standardSize('portrait');
    const dimsL0 = standardSize('landscape');
    const maxW0 = Math.max(dimsP0.w, dimsL0.w);
    const maxH0 = Math.max(dimsP0.h, dimsL0.h);
    const viewportH = (window.visualViewport && window.visualViewport.height) ? window.visualViewport.height : window.innerHeight;
    const compactRatio = (targetCards && targetCards.id === 'viewerCards') ? 0.24 : 0.31;
    const maxAllowedH = Math.max(px(92), Math.min(maxH0, viewportH * compactRatio));
    const fit = (maxH0 > 0) ? Math.min(1.0, maxAllowedH / maxH0) : 1.0;
    const dimsP = {w:dimsP0.w * fit, h:dimsP0.h * fit};
    const dimsL = {w:dimsL0.w * fit, h:dimsL0.h * fit};
    const maxW = Math.max(dimsP.w, dimsL.w);
    const maxH = Math.max(dimsP.h, dimsL.h);
    const n = Array.isArray(cardsList) ? cardsList.length : 0;
    const availW = Math.max(0, Number(targetCards && targetCards.clientWidth || 0) - px(28));
    let step = maxW * 0.45;
    if(n > 1 && availW > maxW){
      const fitStep = (availW - maxW) / (n - 1);
      step = Math.max(maxW * 0.38, Math.min(maxW * 0.72, fitStep));
    }
    return {dimsP, dimsL, maxW, maxH, step};
  }

  function renderPopupCardSurface(targetCards, cardsList, {forcePortrait=false, forceLandscape=false, normalizeNatural=false, onCardClick=null} = {}){
    const list = Array.isArray(cardsList) ? cardsList.slice() : [];
    const {dimsP, dimsL, maxW, maxH, step} = popupCardSurfaceMetrics(targetCards, list);
    const surf = document.createElement('div');
    surf.className = 'surf broadCardListSurf';
    surf.style.height = uiCalc((maxH / (parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--uiScale')) || 1)) + 12);
    const minW = (list.length<=1) ? (maxW + px(24)) : (maxW + step*(list.length-1) + px(24));
    surf.style.minWidth = `${Math.ceil(minW)}px`;

    list.forEach((cn, i)=>{
      const s = String(cn);
      const orient = forceLandscape ? 'landscape' : (forcePortrait ? 'portrait' : intrinsicOrient(s));
      const d = (orient==='landscape') ? dimsL : dimsP;
      const x = px(12) + step*i + (maxW - d.w)/2;
      const y = px(6) + (maxH - d.h)/2;
      const card = makeCard(s, orient, x, y, d.w, d.h, '', onCardClick ? ()=>onCardClick(s, i) : null, false, 100+i, false, null, normalizeNatural);
      surf.appendChild(card);
    });
    return surf;
  }

  function openCardListPopup(title, cards, {closable=true, helperText='', forcePortrait=false, forceLandscape=false, confirmClose=false, normalizeNatural=false, debugZone='' } = {}){
    let cardsList = cards.slice();
    // sort waiting room cards (spec update): by cardnumber asc, then card type
    try{
      const t = String(title||'');
      if(!debugZone && (t.includes('控え室') || t.toLowerCase().includes('waiting'))){
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

    const useViewer = !!closable;
    if(useViewer){
      viewerPopup = {type:'cardlist', title, cards: cardsList.slice(), closable:true, helperText};
      elViewerTitle.textContent = title;
      setRichText(elViewerText, helperText || '');
      elViewerActions.innerHTML = '';
      elViewerCards.innerHTML = '';
    }else{
      popup = {type:'cardlist', title, cards: cardsList.slice(), closable:false, helperText};
      elModalTitle.textContent = title;
      setRichText(elModalText, helperText || '');
      elModalActions.innerHTML = '';
      elModalCards.innerHTML = '';
    }

    const targetCards = useViewer ? elViewerCards : elModalCards;
    const targetActions = useViewer ? elViewerActions : elModalActions;
    targetCards.style.display = '';
    targetCards.style.flexDirection = '';
    targetCards.style.gap = '';

    const isDebugList = !!debugZone && debugMoveMode && !IS_PUBLIC_VIEW;
    if(isDebugList){
      targetCards.style.display = 'flex';
      targetCards.style.flexDirection = 'column';
      targetCards.style.gap = uiCalc(7);
      targetCards.style.overflow = 'auto';
      cardsList.forEach((cn, i)=>{
        const row = document.createElement('div');
        row.className = 'debugCardListRow';
        const thumb = document.createElement('img');
        thumb.src = imgUrl(cn, zoneInstanceId(debugZone, i));
        thumb.alt = cn;
        thumb.style.cssText = `width:${uiCalc(34)};height:${uiCalc(48)};object-fit:contain;border-radius:${uiCalc(4)};background:rgba(0,0,0,.45);flex:0 0 auto;`;
        const label = document.createElement('div');
        label.textContent = `${i + 1}. ${cardDisplayText(cn)} / ${cn}`;
        label.style.cssText = 'min-width:0;flex:1 1 auto;font-size:12px;line-height:1.25;color:#eee;white-space:normal;word-break:break-word;';
        const bSelect = document.createElement('button');
        bSelect.className = 'miniBtn';
        bSelect.textContent = debugSelectionSame(debugZone, i) ? '選択中' : '選択';
        bSelect.addEventListener('click', ev=>{
          ev.stopPropagation();
          selectDebugMoveCard(debugZone, i, cn);
        });
        const bUp = document.createElement('button');
        bUp.className = 'miniBtn';
        bUp.textContent = '上へ';
        bUp.disabled = i <= 0;
        bUp.addEventListener('click', ev=>{
          ev.stopPropagation();
          const next = cardsList.slice();
          const tmp = next[i - 1];
          next[i - 1] = next[i];
          next[i] = tmp;
          reorderDebugZone(debugZone, next);
        });
        const bDown = document.createElement('button');
        bDown.className = 'miniBtn';
        bDown.textContent = '下へ';
        bDown.disabled = i >= cardsList.length - 1;
        bDown.addEventListener('click', ev=>{
          ev.stopPropagation();
          const next = cardsList.slice();
          const tmp = next[i + 1];
          next[i + 1] = next[i];
          next[i] = tmp;
          reorderDebugZone(debugZone, next);
        });
        row.appendChild(thumb);
        row.appendChild(label);
        row.appendChild(bSelect);
        if(debugZone === 'deck' || debugZone === 'green_room'){
          row.appendChild(bUp);
          row.appendChild(bDown);
        }
        targetCards.appendChild(row);
      });
    }else{
      targetCards.appendChild(renderPopupCardSurface(targetCards, cardsList, {
        forcePortrait,
        forceLandscape,
        normalizeNatural,
      }));
    }

    if(useViewer){
      if(isDebugList && debugMoveSelection){
        const topBtn = document.createElement('button');
        topBtn.className = 'miniBtn';
        topBtn.textContent = '選択カードを先頭へ';
        topBtn.addEventListener('click', ev=>{
          ev.stopPropagation();
          putDebugMoveCard(debugZone, 0);
          closeViewerPopup();
        });
        const endBtn = document.createElement('button');
        endBtn.className = 'miniBtn';
        endBtn.textContent = '選択カードを末尾へ';
        endBtn.addEventListener('click', ev=>{
          ev.stopPropagation();
          putDebugMoveCard(debugZone, cardsList.length);
          closeViewerPopup();
        });
        targetActions.appendChild(topBtn);
        targetActions.appendChild(endBtn);
      }
      const close = document.createElement('button');
      close.className = 'miniBtn';
      close.textContent = 'Close';
      close.addEventListener('click', ()=>{ closeViewerPopup(); });
      targetActions.appendChild(close);
      elViewerLayer.style.display = 'block';
      applyPopupPeekState();
    }else{
      if(confirmClose){
        const bConfirmClose = document.createElement('button');
        bConfirmClose.className = 'miniBtn';
        bConfirmClose.textContent = '確認';
        bConfirmClose.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          closePopup();
          st = await apiCmd('next', {indices: selHand.slice()});
          selHand = [];
          updateTop();
          render();
        });
        targetActions.appendChild(bConfirmClose);
      }
      elMask.style.display = 'block';
      applyPopupPeekState();
    }
  }

  function openUnderCardsPopup(title, cards, helperText=''){
    const cardsList = (Array.isArray(cards) ? cards : []).map(x=>String(x||'')).filter(Boolean);
    viewerPopup = {type:'under_cards', title, cards: cardsList.slice(), closable:true, helperText};
    elViewerTitle.textContent = title;
    setRichText(elViewerText, helperText || '');
    elViewerActions.innerHTML = '';
    elViewerCards.innerHTML = '';
    elViewerCards.style.display = 'flex';
    elViewerCards.style.flexDirection = 'column';
    elViewerCards.style.gap = uiCalc(7);
    cardsList.forEach((cn, idx)=>{
      const row = document.createElement('button');
      row.type = 'button';
      row.style.cssText = [
        'display:grid',
        `grid-template-columns:${uiCalc(44)} minmax(0,1fr)`,
        `gap:${uiCalc(8)}`,
        'align-items:center',
        `padding:${uiCalc(6)} ${uiCalc(7)}`,
        `border-radius:${uiCalc(9)}`,
        'border:1px solid rgba(255,255,255,.16)',
        'background:rgba(255,255,255,.06)',
        'color:#eee',
        'text-align:left',
        'cursor:pointer',
      ].join(';');
      const img = document.createElement('img');
      img.src = imgUrl(cn);
      img.alt = cn;
      img.style.cssText = `width:${uiCalc(44)};height:${uiCalc(62)};object-fit:contain;border-radius:${uiCalc(5)};background:rgba(0,0,0,.35);`;
      const body = document.createElement('div');
      body.style.cssText = 'min-width:0;display:flex;flex-direction:column;gap:2px;';
      const name = document.createElement('div');
      name.textContent = `${idx + 1}. ${cardDisplayText(cn)}`;
      name.style.cssText = `font-size:${uiCalc(13)};font-weight:850;line-height:1.25;white-space:normal;word-break:break-word;`;
      const code = document.createElement('div');
      code.textContent = cn;
      code.style.cssText = `font-size:${uiCalc(10)};color:rgba(255,255,255,.56);line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;`;
      body.appendChild(name);
      body.appendChild(code);
      row.appendChild(img);
      row.appendChild(body);
      row.addEventListener('click', ev=>{
        ev.stopPropagation();
        showCardDetail(cn, row);
      });
      elViewerCards.appendChild(row);
    });
    const close = document.createElement('button');
    close.className = 'miniBtn';
    close.textContent = 'Close';
    close.addEventListener('click', ()=>{ closeViewerPopup(); });
    elViewerActions.appendChild(close);
    elViewerLayer.style.display = 'block';
    applyPopupPeekState();
  }

  function openCardPickPopup(title, cards, {helperText='', forcePortrait=false, forceLandscape=false, allowSkip=true } = {}){
    // Like openCardListPopup, but each card is clickable to resolve pending (idx=0).
    let cardsList = (Array.isArray(cards) ? cards.slice() : []).filter(c=>!!c);
    popup = {type:'pending', title, cards: cardsList.slice(), closable:false, helperText};

    elModalTitle.textContent = title;
    setRichText(elModalText, helperText || '');
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const surf = renderPopupCardSurface(elModalCards, cardsList, {
      forcePortrait,
      forceLandscape,
      onCardClick: async (s)=>{
        st = await apiCmd('resolve_pending', {idx:0, choice: s});
        selHand = [];
        updateTop();
        render();
      },
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
    applyPopupPeekState();
  }

  function closePopup(){
    popup = {type:null};
    elMask.style.display = 'none';
    elMask.classList.remove('popupPeekHidden');
    clearModalLead();
    elModalCards.innerHTML = '';
    elModalText.textContent = '';
    elModalActions.innerHTML = '';
    applyPopupPeekState();
  }

  function closeViewerPopup(){
    viewerPopup = {type:null};
    elViewerLayer.style.display = 'none';
    elViewerLayer.classList.remove('popupPeekHidden');
    elViewerCards.innerHTML = '';
    elViewerText.textContent = '';
    elViewerActions.innerHTML = '';
    elViewerTitle.textContent = 'カード一覧';
    applyPopupPeekState();
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
    if(s === '__BACK__') return true;
    // Exact cardnumber only. Labels like "C: PL!N-bp1-003 ライブ開始時" must NOT match.
    // Prefixes: PL!, PL!N, PL!S, PL!SP, PL!HS, LL (series suffix optional after !)
    return /^(?:PL!|LL)[A-Za-z0-9]*-(?:bp\d+|pb\d+|sd\d+|cl\d+|PR|P\d+)-\d{3}$/i.test(s);
  }

  function showPending(p){
    const kind = (p && p.kind) ? String(p.kind) : '';
    setModalContextFromPending(p);

    // Drag-and-drop reorder UI
    if(kind === 'reorder_topk_keep_any'){
      showReorderPopup(p);
      return;
    }

    // 公開カード確認（サマリー + カード一覧 + OK）
    if(kind === 'show_revealed_cards_ack'){
      openYellRevealPopup(p);
      const btnOk = document.createElement('button');
      btnOk.className = 'miniBtn';
      btnOk.textContent = '確認';
      let _srcSubmitting = false;
      btnOk.addEventListener('click', async ev => {
        ev.stopPropagation();
        if(_srcSubmitting) return;
        _srcSubmitting = true;
        st = await apiCmd('resolve_pending', {idx:0, choice:'ok'});
        selHand = [];
        updateTop();
        render();
      });
      elModalActions.appendChild(btnOk);
      return;
    }

    if(kind === 'live_attempt_summary_ack'){
      openLiveAttemptSummaryPopup(p);
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
      const pickCount = Number((p && p.pick_count) || 1);
      const minPickCount = Number((p && p.min_pick_count) || 0);
      const maxPickCount = Number((p && p.max_pick_count) || pickCount || 1);

      // BUILD_TAG: server_choose_from_topk_duplicate_index_multi_20260701ai
      // Multi-pick topdeck effects must track selected *indices*, not cardnumbers.
      // Cardnumbers can appear multiple times in the revealed pool, and selecting a
      // second copy of the same cardnumber must not toggle the first copy off.
      if(pickCount > 1){
        const selected = [];  // indices into displayCards
        const uniqueByGroup = !!(p && p.unique_by_group);
        const row = document.createElement('div');
        row.className = 'choiceRow';
        row.style.overflowX = 'visible';
        row.style.overflowY = 'visible';
        row.style.maxWidth = 'none';
        row.style.width = 'max-content';
        const dupCount = {};
        displayCards.forEach(o=>{ const k=String(o).trim(); dupCount[k]=(dupCount[k]||0)+1; });
        const dupSeen = {};
        const cardsByIdx = {};
        const usedGroupKeys = ()=>{
          const keys = new Set();
          selected.forEach(idx => {
            const cn = String(displayCards[idx] || '').trim();
            cardGroupKeysFor(cn).forEach(k => keys.add(k));
          });
          return keys;
        };
        const refreshCards = ()=>{
          const used = usedGroupKeys();
          Object.entries(cardsByIdx).forEach(([idxStr, el])=>{
            const idx = Number(idxStr);
            const cn = String(displayCards[idx] || '').trim();
            const isCandidate = candidateSet.has(cn);
            const isSelected = selected.includes(idx);
            const groupBlocked = uniqueByGroup && !isSelected && cardGroupKeysFor(cn).some(k => used.has(k));
            const disabled = !isCandidate || groupBlocked || (!isSelected && selected.length >= maxPickCount);
            el.classList.toggle('selected', isSelected);
            el.style.outline = isSelected ? '3px solid #ffe066' : '';
            el.style.opacity = disabled ? '0.35' : '1';
            el.style.filter = disabled ? 'grayscale(80%)' : '';
            el.style.cursor = disabled ? 'not-allowed' : 'pointer';
            const badge = el.querySelector('.choiceOrderBadge');
            if(badge){
              badge.textContent = isSelected ? String(selected.indexOf(idx) + 1) : '';
              badge.style.display = isSelected ? 'flex' : 'none';
            }
          });
          if(optional && minPickCount <= 0){
            bDone.textContent = selected.length > 0 ? `確定 (${selected.length}/${maxPickCount}枚)` : '確定せず終了';
          }else{
            bDone.textContent = `確定 (${selected.length}/${maxPickCount}枚)`;
          }
          bDone.disabled = selected.length < minPickCount || selected.length > maxPickCount;
          bDone.style.opacity = bDone.disabled ? '0.5' : '1';
        };
        displayCards.forEach((rawCn, idx)=>{
          const cn = String(rawCn).trim();
          const intr = intrinsicOrient(cn);
          const d = (intr === 'landscape') ? dimsL : dimsP;
          const wrap = document.createElement('button');
          wrap.className = 'choiceBtn';
          wrap.style.width = d.w + 'px';
          wrap.style.height = d.h + 'px';
          wrap.style.position = 'relative';
          const img = document.createElement('img');
          img.src = imgUrl(cn);
          img.alt = cn;
          dupSeen[cn] = (dupSeen[cn] || 0) + 1;
          const cap = document.createElement('div');
          cap.className = 'choiceCap';
          cap.textContent = cardChoiceCaption(cn, dupSeen[cn], dupCount[cn] || 0);
          const badge = document.createElement('div');
          badge.className = 'choiceOrderBadge';
          badge.style.cssText = 'display:none;position:absolute;left:6px;top:6px;z-index:90;width:24px;height:24px;border-radius:999px;align-items:center;justify-content:center;background:#ffe066;color:#111;font-weight:900;border:1px solid rgba(0,0,0,.35);box-shadow:0 1px 5px rgba(0,0,0,.4);';
          wrap.appendChild(img);
          wrap.appendChild(cap);
          wrap.appendChild(badge);
          wrap.addEventListener('click', ev=>{
            ev.stopPropagation();
            const isCandidate = candidateSet.has(cn);
            const selIdx = selected.indexOf(idx);
            if(selIdx >= 0){
              selected.splice(selIdx, 1);
              refreshCards();
              return;
            }
            if(!isCandidate) return;
            if(selected.length >= maxPickCount) return;
            if(uniqueByGroup){
              const used = usedGroupKeys();
              if(cardGroupKeysFor(cn).some(k => used.has(k))) return;
            }
            selected.push(idx);
            refreshCards();
          });
          cardsByIdx[idx] = wrap;
          row.appendChild(wrap);
        });
        elModalCards.appendChild(row);

        const bDone = document.createElement('button');
        bDone.className = 'miniBtn';
        bDone.addEventListener('click', async ev=>{
          ev.stopPropagation();
          if(bDone.disabled) return;
          const selectedCards = selected.map(idx => String(displayCards[idx] || '').trim()).filter(Boolean);
          const choice = selectedCards.length ? (selectedCards.join(',') + ',') : 'done';
          st = await apiCmd('resolve_pending', {idx:0, choice});
          selHand = [];
          updateTop();
          render();
        });
        elModalActions.appendChild(bDone);

        if(optional){
          const bSkip = document.createElement('button');
          bSkip.className = 'miniBtn';
          bSkip.textContent = 'スキップ';
          bSkip.addEventListener('click', async ev => {
            ev.stopPropagation();
            st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
            selHand = [];
            updateTop();
            render();
          });
          elModalActions.appendChild(bSkip);
        }
        refreshCards();
        elMask.style.display = 'block';
        return;
      }

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
        const pickedCount = Array.isArray(p.picked) ? p.picked.length : 0;
        const hasDoneOption = Array.isArray(p.options) && p.options.some(o => {
          const s = String(o || '').trim();
          const low = s.toLowerCase();
          return low === 'done' || low === '__done__' || low === 'confirm' || s === '確定';
        });
        if(hasDoneOption || pickedCount > 0){
          const bDone = document.createElement('button');
          bDone.className = 'miniBtn';
          bDone.textContent = pickedCount > 0 ? `確定 (${pickedCount}枚)` : '確定';
          let _cfDoneSubmitting = false;
          bDone.addEventListener('click', async ev => {
            ev.stopPropagation();
            if(_cfDoneSubmitting) return;
            _cfDoneSubmitting = true;
            st = await apiCmd('resolve_pending', {idx:0, choice:'done'});
            selHand = [];
            updateTop();
            render();
          });
          elModalActions.appendChild(bDone);
        }
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

    // Multi-select: choose_hand_cards_ordered_topdeck（手札からN枚選択→クリック順でデッキ上へ）
    if(kind === 'choose_hand_cards_ordered_topdeck'){
      const maxPicks = (p && p.max_picks != null) ? parseInt(p.max_picks) : ((p && p.maxPicks != null) ? parseInt(p.maxPicks) : 0);
      const minPicks = (p && p.min_picks != null) ? parseInt(p.min_picks) : 0;
      const opts = (p && Array.isArray(p.options)) ? p.options : [];
      const title = String((p && (p.text || p.prompt || p.message)) ? (p.text || p.prompt || p.message) : `手札から${maxPicks}枚選択`);

      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '選択';
      setRichText(elModalText, title);
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';

      const selected = [];
      const dimsP = standardSize('portrait');
      const row = document.createElement('div');
      row.className = 'choiceRow';

      const counter = document.createElement('div');
      counter.style.cssText = 'width:100%;text-align:center;color:#fff;font-size:13px;margin-bottom:4px;padding:2px 0;';

      const doneBtn = document.createElement('button');
      doneBtn.className = 'miniBtn';

      const btnMap = {};
      const dupCount = {};
      opts.forEach(o => { const k=String(o).trim(); dupCount[k]=(dupCount[k]||0)+1; });
      const dupSeen = {};

      function updateCounter(){
        const n = selected.length;
        counter.textContent = `選択: ${n} / ${maxPicks} （クリック順 = デッキ上に置く順）`;
        doneBtn.textContent = `確定 (${n}/${maxPicks})`;
        doneBtn.disabled = (n < minPicks || n > maxPicks);
        doneBtn.style.opacity = doneBtn.disabled ? '0.5' : '1';

        opts.forEach((cn, i) => {
          const b = btnMap[i];
          if(!b) return;
          const k = String(cn).trim();
          const orderIdx = selected.indexOf(i);
          if(orderIdx >= 0){
            b.style.outline = `3px solid #ffe066`;
            b.style.outlineOffset = '-3px';
            const cap = b.querySelector('.choiceCap');
            if(cap) cap.textContent = `${k} [${orderIdx+1}]`;
          } else {
            b.style.outline = '';
            b.style.outlineOffset = '';
            const dup = opts.filter(x => String(x).trim() === k).length;
            const nth = opts.slice(0, i).filter(x => String(x).trim() === k).length + 1;
            const cap = b.querySelector('.choiceCap');
            if(cap) cap.textContent = (dup > 1) ? `${k} (${nth}/${dup})` : k;
          }
        });
      }

      opts.forEach((opt, i) => {
        const cn = String(opt).trim();
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = dimsP.w + 'px';
        b.style.height = dimsP.h + 'px';

        appendChoiceCardImage(b, cn, 'portrait');

        const badge = document.createElement('div');
        badge.className = 'orderBadge';
        b.appendChild(badge);

        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        dupSeen[cn] = (dupSeen[cn]||0) + 1;
        cap.textContent = cardChoiceCaption(cn, dupSeen[cn], dupCount[cn]);
        b.appendChild(cap);

        btnMap[i] = b;

        b.addEventListener('click', ev => {
          ev.stopPropagation();
          const alreadyIdx = selected.indexOf(i);
          if(alreadyIdx >= 0){
            selected.splice(alreadyIdx, 1);
          } else if(selected.length < maxPicks){
            selected.push(i);
          }
          updateCounter();
        });

        row.appendChild(b);
      });

      let submitting = false;
      doneBtn.addEventListener('click', async ev => {
        ev.stopPropagation();
        if(doneBtn.disabled) return;
        if(submitting) return;
        submitting = true;
        const choiceStr = selected.map(i => String(opts[i]).trim()).join(',');
        st = await apiCmd('resolve_pending', {idx:0, choice: choiceStr});
        selHand = [];
        updateTop();
        render();
      });

      updateCounter();
      elModalCards.appendChild(counter);
      elModalCards.appendChild(row);
      elModalActions.appendChild(doneBtn);
      elMask.style.display = 'block';
      return;
    }

    // Multi-select: reveal hand MEMBER cards and evaluate printed cost sum.
    if(kind === 'reveal_hand_members_cost_sum'){
      const maxPicks = (p && p.max_picks != null) ? parseInt(p.max_picks) : ((p && p.maxPicks != null) ? parseInt(p.maxPicks) : 0);
      const opts = (p && Array.isArray(p.options)) ? p.options : [];
      const validTotals = (p && Array.isArray(p.valid_totals)) ? p.valid_totals.map(x=>Number(x||0)) : [10,20,30,40,50];
      const title = String((p && (p.text || p.prompt || p.message)) ? (p.text || p.prompt || p.message) : `手札のメンバーカードを0〜${maxPicks}枚公開`);

      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '公開カードを選択';
      setRichText(elModalText, title);
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';

      const selectionKey = JSON.stringify({
        kind: kind,
        source: p && p.source ? String(p.source) : '',
        source_pos: p && p.source_pos ? String(p.source_pos) : '',
        options: opts.map(x=>String(x).trim()),
        max_picks: maxPicks,
        valid_totals: validTotals
      });
      if(!window.__revealCostSumSelection || window.__revealCostSumSelection.key !== selectionKey){
        window.__revealCostSumSelection = {key: selectionKey, selected: []};
      }
      const selected = window.__revealCostSumSelection.selected;
      for(let si = selected.length - 1; si >= 0; si--){
        const idx = Number(selected[si]);
        if(!Number.isInteger(idx) || idx < 0 || idx >= opts.length){
          selected.splice(si, 1);
        }
      }
      const dimsP = standardSize('portrait');
      const row = document.createElement('div');
      row.className = 'choiceRow';

      const counter = document.createElement('div');
      counter.style.cssText = 'width:100%;text-align:center;color:#fff;font-size:13px;margin-bottom:4px;padding:2px 0;';

      const doneBtn = document.createElement('button');
      doneBtn.className = 'miniBtn';
      const btnMap = {};
      const dupCount = {};
      opts.forEach(o => { const k=String(o).trim(); dupCount[k]=(dupCount[k]||0)+1; });
      const dupSeen = {};

      function printedCost(cn){
        try{
          const m = (st && st.cn2cost) ? st.cn2cost : {};
          return Number(m[String(cn)] || 0) || 0;
        }catch(e){ return 0; }
      }
      function selectedTotal(){
        return selected.reduce((acc, idx)=> acc + printedCost(opts[idx]), 0);
      }
      function updateCounter(){
        const n = selected.length;
        const total = selectedTotal();
        const met = validTotals.includes(total);
        counter.textContent = `選択: ${n} / 0〜${maxPicks}　コスト合計: ${total}　${met ? '条件達成' : '条件未達'}`;
        counter.className = met ? 'condMet' : 'condUnmet';
        doneBtn.textContent = `公開して解決 (${n}枚 / 合計${total})`;
        doneBtn.disabled = false;
        opts.forEach((cn, i) => {
          const b = btnMap[i];
          if(!b) return;
          const badge = b.querySelector('.orderBadge');
          const cap = b.querySelector('.choiceCap');
          if(selected.includes(i)){
            b.classList.add('orderedSelected');
            if(badge){ badge.textContent = '✓'; badge.style.display = 'flex'; }
            if(cap) cap.textContent = `${String(cn).trim()} cost${printedCost(cn)} ✓`;
          }else{
            b.classList.remove('orderedSelected');
            if(badge){ badge.textContent = ''; badge.style.display = 'none'; }
            if(cap){
              const k = String(cn).trim();
              const dup = opts.filter(x => String(x).trim() === k).length;
              const nth = opts.slice(0, i).filter(x => String(x).trim() === k).length + 1;
              cap.textContent = `${dup > 1 ? `${k} (${nth}/${dup})` : k} cost${printedCost(cn)}`;
            }
          }
        });
      }
      opts.forEach((opt, i) => {
        const cn = String(opt).trim();
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = dimsP.w + 'px';
        b.style.height = dimsP.h + 'px';
        appendChoiceCardImage(b, cn, 'portrait');
        const badge = document.createElement('div');
        badge.className = 'orderBadge';
        b.appendChild(badge);
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        dupSeen[cn] = (dupSeen[cn]||0) + 1;
        cap.textContent = `${cardChoiceCaption(cn, dupSeen[cn], dupCount[cn])} cost${printedCost(cn)}`;
        b.appendChild(cap);
        btnMap[i] = b;
        b.addEventListener('click', ev => {
          ev.stopPropagation();
          const j = selected.indexOf(i);
          if(j >= 0) selected.splice(j, 1);
          else if(selected.length < maxPicks) selected.push(i);
          window.__revealCostSumSelection = {key: selectionKey, selected: selected};
          updateCounter();
        });
        row.appendChild(b);
      });
      let submitting = false;
      doneBtn.addEventListener('click', async ev => {
        ev.stopPropagation();
        if(submitting) return;
        submitting = true;
        const choiceStr = selected.map(i => String(opts[i]).trim()).join(',');
        st = await apiCmd('resolve_pending', {idx:0, choice: choiceStr});
        if(window.__revealCostSumSelection && window.__revealCostSumSelection.key === selectionKey){
          window.__revealCostSumSelection = null;
        }
        selHand = [];
        updateTop();
        render();
      });
      updateCounter();
      elModalCards.appendChild(counter);
      elModalCards.appendChild(row);
      elModalActions.appendChild(doneBtn);
      elMask.style.display = 'block';
      return;
    }

    // Multi-select: choose_member_from_green_multi_up_to（控え室から0〜N枚選択→手札へ）
    if(kind === 'choose_member_from_green_multi_up_to'){
      const maxPicks = (p && p.max_picks != null) ? parseInt(p.max_picks) : ((p && p.maxPicks != null) ? parseInt(p.maxPicks) : 0);
      const minPicks = (p && p.min_picks != null) ? parseInt(p.min_picks) : 0;
      const exactOrZero = !!(p && p.exact_or_zero);
      const ordered = !!(p && p.ordered);
      const orderHint = String((p && p.order_hint) ? p.order_hint : '');
      const sourceZone = String((p && p.source_zone) ? p.source_zone : 'green').toLowerCase();
      const opts = (p && Array.isArray(p.options)) ? p.options : [];
      const defaultTitle = sourceZone === 'hand' ? `手札から${exactOrZero ? '0枚または' + maxPicks + '枚' : '0〜' + maxPicks + '枚'}選択` : `控え室から0〜${maxPicks}枚選択`;
      const title = String((p && (p.text || p.prompt || p.message)) ? (p.text || p.prompt || p.message) : defaultTitle);

      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '選択';
      setRichText(elModalText, title);
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';

      const selected = [];
      const dimsP = standardSize('portrait');
      const row = document.createElement('div');
      row.className = 'choiceRow';

      const counter = document.createElement('div');
      counter.style.cssText = 'width:100%;text-align:center;color:#fff;font-size:13px;margin-bottom:4px;padding:2px 0;';

      const doneBtn = document.createElement('button');
      doneBtn.className = 'miniBtn';

      const btnMap = {};
      const dupCount = {};
      opts.forEach(o => { const k=String(o).trim(); dupCount[k]=(dupCount[k]||0)+1; });
      const dupSeen = {};

      function updateCounter(){
        const n = selected.length;
        if(ordered && orderHint === 'deck_bottom_top_to_bottom'){
          counter.textContent = `選択: ${n} / 0〜${maxPicks} （クリック順：1枚目=上側、最後=一番下）`;
        } else if(ordered){
          counter.textContent = `選択: ${n} / 0〜${maxPicks} （クリック順 = 解決順）`;
        } else {
          counter.textContent = exactOrZero ? `選択: ${n} / 0 または ${maxPicks}` : `選択: ${n} / 0〜${maxPicks}`;
        }
        doneBtn.textContent = `確定 (${n}/${maxPicks})`;
        doneBtn.disabled = exactOrZero ? !(n === 0 || n === maxPicks) : (n < minPicks || n > maxPicks);
        doneBtn.style.opacity = doneBtn.disabled ? '0.5' : '1';

        opts.forEach((cn, i) => {
          const b = btnMap[i];
          if(!b) return;
          const k = String(cn).trim();
          const orderIdx = selected.indexOf(i);
          const timesThisIdx = selected.filter(x => x === i).length;
          const badge = b.querySelector('.orderBadge');
          if(timesThisIdx > 0){
            b.classList.add('orderedSelected');
            b.style.outline = '';
            b.style.outlineOffset = '';
            if(badge){
              badge.textContent = ordered ? String(orderIdx + 1) : '✓';
              badge.style.display = 'flex';
            }
            const cap = b.querySelector('.choiceCap');
            if(cap){
              if(ordered){
                cap.textContent = `${orderIdx+1}番目：${k}`;
              } else {
                cap.textContent = k + (timesThisIdx > 1 ? ` ×${timesThisIdx}` : ' ✓');
              }
            }
          } else {
            b.classList.remove('orderedSelected');
            b.style.outline = '';
            b.style.outlineOffset = '';
            if(badge){
              badge.textContent = '';
              badge.style.display = 'none';
            }
            const dup = opts.filter(x => String(x).trim() === k).length;
            const nth = opts.slice(0, i).filter(x => String(x).trim() === k).length + 1;
            const cap = b.querySelector('.choiceCap');
            if(cap) cap.textContent = (dup > 1) ? `${k} (${nth}/${dup})` : k;
          }
        });
      }

      opts.forEach((opt, i) => {
        const cn = String(opt).trim();
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = dimsP.w + 'px';
        b.style.height = dimsP.h + 'px';

        appendChoiceCardImage(b, cn, 'portrait');

        const badge = document.createElement('div');
        badge.className = 'orderBadge';
        b.appendChild(badge);

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
            selected.splice(alreadyIdx, 1);
          } else if(selected.length < maxPicks){
            selected.push(i);
          }
          updateCounter();
        });

        row.appendChild(b);
      });

      let submitting = false;
      doneBtn.addEventListener('click', async ev => {
        ev.stopPropagation();
        if(doneBtn.disabled) return;
        if(submitting) return;
        submitting = true;
        const choiceStr = selected.map(i => String(opts[i]).trim()).join(',');
        st = await apiCmd('resolve_pending', {idx:0, choice: choiceStr});
        selHand = [];
        updateTop();
        render();
      });

      updateCounter();
      elModalCards.appendChild(counter);
      elModalCards.appendChild(row);
      elModalActions.appendChild(doneBtn);
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
    if(kind === 'mass_bottom_auto_ack' || kind === 'mass_bottom_optional_result_ack') setRichTextWithMassCounts(elModalText, pendText);
    else setRichText(elModalText, pendText);
    const allowSkip = !!((p && (p.allow_less || p.allow_skip)) || /Skip可/i.test(pendText) || /\bskip\b/i.test(pendText) || (kind && /pick/i.test(kind)));
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const opts = (p && (Array.isArray(p.options)?p.options: (Array.isArray(p.candidates)?p.candidates:(Array.isArray(p.cards)?p.cards:(Array.isArray(p.shown)?p.shown:[]))))) || [];

    if(kind === 'choose_heart_color' || kind === 'choose_heart_color_for_other'){
      const row = document.createElement('div');
      row.className = 'heartChoiceGrid';
      const ordered = opts.slice().sort((a,b)=>{
        const normColor = (x)=>{
          const s0 = String(x || '').trim();
          const low0 = s0.toLowerCase();
          const jp = {'桃':'pink','赤':'red','黄':'yellow','緑':'green','青':'blue','紫':'purple','任意':'any','無色':'any'};
          return HEART_TOKEN_BY_COLOR[low0] ? low0 : (jp[s0] || low0);
        };
        return heartColorOrderKey(normColor(a)) - heartColorOrderKey(normColor(b));
      });
      row.style.gridTemplateColumns = (ordered.length <= 6)
        ? 'repeat(3, minmax(calc(160px * var(--uiScale)), 1fr))'
        : 'repeat(4, minmax(calc(140px * var(--uiScale)), 1fr))';
      ordered.forEach(opt=>{
        const b = document.createElement('button');
        b.className = 'miniBtn';
        b.style.cssText = 'min-width:0;width:100%;justify-content:center;display:inline-flex;align-items:center;';
        b.appendChild(choiceRichLabel(opt));
        b.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:String(opt)});
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
          selHand = []; updateTop(); render();
        });
        elModalActions.appendChild(bSkip);
      }
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'set_opponent_excess_for_live_success'){
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '相手余剰ハート数を指定';
      setRichText(elModalText, pendText || 'このライブ成功時効果の処理で参照する相手余剰ハート数を選んでください。');
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';
      const wrap = document.createElement('div');
      wrap.style.display = 'flex';
      wrap.style.alignItems = 'center';
      wrap.style.gap = '12px';
      wrap.style.padding = '14px 4px';
      const lab = document.createElement('label');
      lab.textContent = '相手余剰ハート数';
      lab.style.fontWeight = '700';
      const sel = document.createElement('select');
      sel.style.fontSize = '18px';
      sel.style.padding = '8px 14px';
      sel.style.borderRadius = '10px';
      sel.style.background = '#222';
      sel.style.color = '#fff';
      sel.style.border = '1px solid rgba(255,255,255,.28)';
      const cur = Math.max(0, Math.min(9, Number((p && p.current) || (st && st.opponent_excess_heart_count) || 0)));
      for(let i=0;i<=9;i++){
        const opt = document.createElement('option');
        opt.value = String(i);
        opt.textContent = String(i);
        if(i === cur) opt.selected = true;
        sel.appendChild(opt);
      }
      wrap.appendChild(lab);
      wrap.appendChild(sel);
      elModalCards.appendChild(wrap);
      const bOk = document.createElement('button');
      bOk.className = 'miniBtn';
      bOk.textContent = '確定';
      bOk.addEventListener('click', async (ev)=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:String(sel.value)});
        selHand=[]; updateTop(); render();
      });
      elModalActions.appendChild(bOk);
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'set_opponent_success_score_for_live_attempt'){
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '相手成功スコア合計を指定';
      setRichText(elModalText, pendText || 'このライブ判定で参照する相手成功ライブカード置き場のスコア合計を選んでください。');
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';
      const wrap = document.createElement('div');
      wrap.style.display = 'flex';
      wrap.style.alignItems = 'center';
      wrap.style.gap = '12px';
      wrap.style.padding = '14px 4px';
      const lab = document.createElement('label');
      lab.textContent = '相手成功スコア合計';
      lab.style.fontWeight = '700';
      const sel = document.createElement('select');
      sel.style.fontSize = '18px';
      sel.style.padding = '8px 14px';
      sel.style.borderRadius = '10px';
      sel.style.background = '#222';
      sel.style.color = '#fff';
      sel.style.border = '1px solid rgba(255,255,255,.28)';
      const rawCur = Number((p && p.current) || (st && st.opponent_success_score_sum) || 0);
      const cur = Math.max(0, Math.min(20, Number.isFinite(rawCur) ? rawCur : 0));
      for(let i=0;i<=20;i++){
        const opt = document.createElement('option');
        opt.value = String(i);
        opt.textContent = String(i);
        if(i === cur) opt.selected = true;
        sel.appendChild(opt);
      }
      wrap.appendChild(lab);
      wrap.appendChild(sel);
      elModalCards.appendChild(wrap);
      const bOk = document.createElement('button');
      bOk.className = 'miniBtn';
      bOk.textContent = '確定';
      bOk.addEventListener('click', async (ev)=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:String(sel.value)});
        selHand=[]; updateTop(); render();
      });
      elModalActions.appendChild(bOk);
      elMask.style.display = 'block';
      return;
    }


    if(kind === 'confirm_yell_revealed_all_to_green_then_extra_yell'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards : (Array.isArray(p.candidates) ? p.candidates : []);
      openCardListPopup('追加エール確認', displayCards, {
        closable: false,
        helperText: pendText || '公開カードを控え室に置いて追加エールを行うか選んでください。'
      });
      popup = {type:'pending', closable:false};
      const bUse = document.createElement('button');
      bUse.className = 'miniBtn';
      bUse.textContent = '使う';
      bUse.addEventListener('click', async ev=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'pay'});
        selHand=[]; updateTop(); render();
      });
      const bSkip = document.createElement('button');
      bSkip.className = 'miniBtn';
      bSkip.textContent = 'スキップ';
      bSkip.addEventListener('click', async ev=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
        selHand=[]; updateTop(); render();
      });
      elModalActions.appendChild(bUse);
      elModalActions.appendChild(bSkip);
      return;
    }

    if(kind === 'choose_yell_revealed_to_green_then_extra_yell'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards : (Array.isArray(p.candidates) ? p.candidates : opts);
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '公開カードを選択';
      setRichText(elModalText, pendText || '控え室に置くエール公開カードを選んでください。0枚で終了する場合はスキップしてください。');
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';
      const row = document.createElement('div');
      row.className = 'choiceRow';
      const dims = standardSize('portrait');
      displayCards.filter(cn=>looksLikeCardNo(String(cn))).forEach((cn)=>{
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = dims.w + 'px';
        b.style.height = dims.h + 'px';
        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = cardChoiceCaption(cn, 1, 1);
        b.appendChild(img);
        b.appendChild(cap);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:String(cn)});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      if(row.children.length){
        elModalCards.appendChild(row);
      }else{
        const note = document.createElement('div');
        note.style.opacity = '0.85';
        note.style.fontSize = '13px';
        note.style.padding = '6px 0';
        note.textContent = '選択できる公開カードがありません。';
        elModalCards.appendChild(note);
      }
      const bSkip = document.createElement('button');
      bSkip.className = 'miniBtn';
      const pickedN = Array.isArray(p.picked) ? p.picked.length : 0;
      bSkip.textContent = pickedN > 0 ? '選択を終了' : '0枚で終了';
      bSkip.addEventListener('click', async ev=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
        selHand=[]; updateTop(); render();
      });
      elModalActions.appendChild(bSkip);
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'hand_member_to_empty_area'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards : opts.filter(o=>looksLikeCardNo(String(o)));
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '手札からメンバーを選択';
      setRichText(elModalText, pendText || '手札から登場させるメンバーを選んでください。');
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';
      const row = document.createElement('div');
      row.className = 'choiceRow';
      const dims = standardSize('portrait');
      displayCards.filter(cn=>looksLikeCardNo(String(cn))).forEach((cn)=>{
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = dims.w + 'px';
        b.style.height = dims.h + 'px';
        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = cardChoiceCaption(cn, 1, 1);
        b.appendChild(img);
        b.appendChild(cap);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:String(cn)});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      if(row.children.length){
        elModalCards.appendChild(row);
      }else{
        const note = document.createElement('div');
        note.style.opacity = '0.85';
        note.style.fontSize = '13px';
        note.style.padding = '6px 0';
        note.textContent = '候補カードが表示できませんでした。';
        elModalCards.appendChild(note);
      }
      if(p && p.optional){
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn';
        bSkip.textContent = 'スキップ';
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

    if(kind === 'mass_bottom_auto_ack' || kind === 'mass_bottom_optional_result_ack'){
      // 結果本文は上部の既存 effect processing text に集約する。
      // 重複を避けるため下部には追加説明を出さず、可変枚数だけ軽く強調する。
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';
      const bOk = document.createElement('button');
      bOk.className = 'miniBtn';
      bOk.textContent = '確認';
      bOk.addEventListener('click', async (ev)=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'ok'});
        selHand = [];
        updateTop();
        render();
      });
      elModalActions.appendChild(bOk);
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'live_storage_to_deck_top_or_bottom'){
      const cards = opts.filter(o=>looksLikeCardNo(String(o)));
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = 'ライブカードを選択';
      setRichText(elModalText, pendText || '控え室に置かれるライブカードをデッキの一番上か一番下に置いてもよい。');
      elModalActions.innerHTML = '';
      elModalCards.innerHTML = '';
      if(cards.length){
        const row = document.createElement('div');
        row.className = 'choiceRow';
        const dimsL = standardSize('landscape');
        cards.forEach((cn)=>{
          const b = document.createElement('button');
          b.className = 'choiceBtn';
          b.style.width = dimsL.w + 'px';
          b.style.height = dimsL.h + 'px';
          const img = document.createElement('img');
          img.src = imgUrl(cn); img.alt = cn;
          const cap = document.createElement('div');
          cap.className = 'choiceCap';
          cap.textContent = cardChoiceCaption(cn, 1, 1);
          b.appendChild(img); b.appendChild(cap);
          b.addEventListener('click', async ev=>{
            ev.stopPropagation();
            st = await apiCmd('resolve_pending', {idx:0, choice: cn});
            selHand=[]; updateTop(); render();
          });
          row.appendChild(b);
        });
        elModalCards.appendChild(row);
      }
      const bSkip = document.createElement('button');
      bSkip.className = 'miniBtn';
      bSkip.textContent = 'スキップ';
      bSkip.addEventListener('click', async ev=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'skip'});
        selHand=[]; updateTop(); render();
      });
      elModalActions.appendChild(bSkip);
      elMask.style.display = 'block';
      return;
    }

    // Special: 成功ライブカード置き場へ置くカード選択（Skip可）
    if(kind === 'pick_success_to_store'){
      const cards = opts.filter(o=>looksLikeCardNo(o));
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '成功ライブ';
      setRichText(elModalText, pendText || '成功ライブカード置き場に置くカードを選択（Skip可）');
      elModalActions.innerHTML = '';
      elModalCards.innerHTML = '';

      const row = document.createElement('div');
      row.className = 'choiceRow';
      const dimsL = standardSize('landscape');
      const disabledOptions = (p && p.disabled_options && typeof p.disabled_options === 'object') ? p.disabled_options : {};

      cards.forEach((cn)=>{
        const disabledReason = String(disabledOptions[String(cn)] || '').trim();
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = dimsL.w + 'px';
        b.style.height = dimsL.h + 'px';
        if(disabledReason){
          b.disabled = true;
          b.style.opacity = '0.48';
          b.style.cursor = 'not-allowed';
          b.title = disabledReason;
        }

        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;
        b.appendChild(img);
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = disabledReason ? `選択不可：${disabledReason}` : cardChoiceCaption(cn, 1, 1);
        b.appendChild(cap);

        const applyChoice = async (ev)=>{
          if(ev) ev.stopPropagation();
          if(disabledReason) return;
          st = await apiCmd('resolve_pending', {idx:0, choice: cn});
          selHand = [];
          updateTop();
          render();
        };
        b.addEventListener('click', applyChoice);
        row.appendChild(b);
      });

      if(cards.length){
        elModalCards.appendChild(row);
      }else{
        const note = document.createElement('div');
        note.style.opacity = '0.85';
        note.style.fontSize = '13px';
        note.style.padding = '6px 0';
        note.textContent = '候補カードが表示できませんでした。Skip するか、ログを確認してください。';
        elModalCards.appendChild(note);
      }

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

      elMask.style.display = 'block';
      return;
    }

    if(kind === 'self_top1_to_green_or_keep'){
      const cn = String((p && p.top_cn) ? p.top_cn : '').trim();
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = 'デッキ上を確認';
      setRichText(elModalText, pendText || 'このカードを控え室に置くか、デッキ上に残すか選んでください。');
      elModalActions.innerHTML = '';
      elModalCards.innerHTML = '';
      if(cn && looksLikeCardNo(cn)){
        const row = document.createElement('div');
        row.className = 'choiceRow';
        const dimsP = standardSize('portrait');
        const dimsL = standardSize('landscape');
        const intr = intrinsicOrient(cn);
        const d = (intr==='landscape') ? dimsL : dimsP;
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = d.w + 'px';
        b.style.height = d.h + 'px';
        const img = document.createElement('img');
        img.src = imgUrl(cn); img.alt = cn;
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = cardNameFor(cn);
        b.appendChild(img); b.appendChild(cap);
        row.appendChild(b);
        elModalCards.appendChild(row);
      }
      const bGreen = document.createElement('button');
      bGreen.className = 'miniBtn';
      bGreen.textContent = '控え室に置く';
      bGreen.addEventListener('click', async ev=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'green'});
        selHand=[]; updateTop(); render();
      });
      const bKeep = document.createElement('button');
      bKeep.className = 'miniBtn';
      bKeep.textContent = 'デッキ上に残す';
      bKeep.addEventListener('click', async ev=>{
        ev.stopPropagation();
        st = await apiCmd('resolve_pending', {idx:0, choice:'keep'});
        selHand=[]; updateTop(); render();
      });
      elModalActions.appendChild(bGreen);
      elModalActions.appendChild(bKeep);
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'choose_effects'){
      // This is an effect-mode choice ("以下から1つ/1つ以上を選ぶ"), not a card pick.
      // Keep it as readable full-text options even when the option text contains card words.
      setModalContextFromPending(p);
      const list = document.createElement('div');
      list.className = 'effectChoiceList';
      const isDoneChoice = (v)=>{
        const low = String(v || '').trim().toLowerCase();
        return ['done','__done__','finish','end','終了','完了'].includes(low);
      };
      const effectOpts = opts.map(o=>String(o || '').trim()).filter(o=>o && !isDoneChoice(o));
      const hasDone = opts.some(o=>isDoneChoice(o));
      const pickedCount = Array.isArray(p.picked) ? p.picked.length : 0;
      const maxPick = Number(p.max || 1);

      effectOpts.forEach((opt, i)=>{
        const b = document.createElement('button');
        b.className = 'effectChoiceBtn';
        const bullet = document.createElement('span');
        bullet.className = 'effectChoiceBullet';
        bullet.textContent = String(i + 1);
        const body = document.createElement('div');
        body.className = 'effectChoiceText';
        setRichText(body, opt);
        b.appendChild(bullet);
        b.appendChild(body);
        b.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: opt});
          selHand = [];
          updateTop();
          render();
        });
        list.appendChild(b);
      });
      if(!effectOpts.length){
        const note = document.createElement('div');
        note.className = 'effectChoiceMeta';
        note.textContent = '選択できる効果がありません。ログを確認してください。';
        list.appendChild(note);
      }
      if(maxPick > 1){
        const meta = document.createElement('div');
        meta.className = 'effectChoiceMeta';
        meta.textContent = `選択済み: ${pickedCount} / 最大 ${maxPick}`;
        list.appendChild(meta);
      }
      elModalCards.appendChild(list);
      if(hasDone){
        const bDone = document.createElement('button');
        bDone.className = 'miniBtn';
        bDone.textContent = '選択終了';
        bDone.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:'Done'});
          selHand = [];
          updateTop();
          render();
        });
        elModalActions.appendChild(bDone);
      }
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'auto_order' && Array.isArray(p.queue) && p.queue.length){
      const row = document.createElement('div');
      row.className = 'choiceRow';

      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      const queue = Array.isArray(p.queue) && p.queue.length ? p.queue : [];

      const items = opts.map((opt, i)=>{
        const trig = queue[i] || {};
        const cn = String((trig && trig.source_cn) ? trig.source_cn : '').trim();
        const label = String(opt || '').trim();
        return {label, cn, trig};
      }).filter(it=>it.label);

      setModalChoiceHoverHint('カードにカーソルを合わせると、上の欄にその選択肢で発動する効果だけを表示します。');
      const showChoiceEffectContext = (it)=>{
        const trig = it && it.trig && Object.keys(it.trig).length ? it.trig : {source_cn: it && it.cn};
        setModalContextFromPending(trig);
      };
      if(items.length) showChoiceEffectContext(items[0]);

      const dupCountAuto = {};
      items.forEach(it=>{ const k = String(it.cn || it.label || '').trim(); dupCountAuto[k] = (dupCountAuto[k]||0) + 1; });
      const dupSeenAuto = {};

      items.forEach(it=>{
        const tile = document.createElement('div');
        tile.className = 'choiceTile';

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
        if(looksLikeCardNo(it.cn)){
          const key = String(it.cn).trim();
          dupSeenAuto[key] = (dupSeenAuto[key]||0) + 1;
          if((dupCountAuto[key]||0) > 1 && it.label && !looksLikeCardNo(it.label)){
            cap.textContent = `${cardNameFor(it.cn)}：${shortAutoOrderLabel(it.label, it.cn)}`;
          }else{
            cap.textContent = cardChoiceCaption(it.cn, dupSeenAuto[key], dupCountAuto[key]);
          }
        }else{
          cap.textContent = it.label;
        }
        b.appendChild(cap);

        const showCtx = ()=>{ showChoiceEffectContext(it); };
        b.addEventListener('mouseenter', showCtx);
        b.addEventListener('focus', showCtx);

        b.addEventListener('click', async (ev)=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: it.label});
          selHand = [];
          updateTop();
          render();
        });

        tile.appendChild(b);

        row.appendChild(tile);
      });

      elModalCards.appendChild(row);
      elMask.style.display = 'block';
      return;
    }

    const allCardNo = opts.length && opts.every(o=>looksLikeCardNo(o));

    if(kind === 'choose_revealed_for_heart_colors_to_stage_named'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards : (Array.isArray(p.pool) ? p.pool : opts);
      const candidateSet2 = new Set((Array.isArray(p.candidates) ? p.candidates : opts).map(c => String(c).trim()));
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '公開カードを選択';
      setRichText(elModalText, pendText || '公開されたカードのうち、条件に合うカードを選んでください。');
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';
      const row = document.createElement('div');
      row.className = 'choiceRow';
      row.style.overflowX = 'visible';
      row.style.overflowY = 'visible';
      row.style.maxWidth = 'none';
      row.style.width = 'max-content';
      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      const dupCount = {};
      displayCards.forEach(o=>{ const k=String(o).trim(); dupCount[k]=(dupCount[k]||0)+1; });
      const dupSeen = {};
      displayCards.forEach(rawCn=>{
        const cn = String(rawCn).trim();
        const intr = intrinsicOrient(cn);
        const d = (intr === 'landscape') ? dimsL : dimsP;
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = d.w + 'px';
        b.style.height = d.h + 'px';
        const selectable = candidateSet2.has(cn);
        if(!selectable){
          b.style.opacity = '0.35';
          b.style.filter = 'grayscale(80%)';
          b.style.cursor = 'not-allowed';
        }
        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;
        dupSeen[cn] = (dupSeen[cn] || 0) + 1;
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = cardChoiceCaption(cn, dupSeen[cn], dupCount[cn] || 0);
        b.appendChild(img);
        b.appendChild(cap);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          if(!selectable) return;
          st = await apiCmd('resolve_pending', {idx:0, choice:cn});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      elModalCards.appendChild(row);
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'choose_stage_named_for_picked_hearts'){
      const picked = String((p && p.picked_card) || '').trim();
      const posOpts = opts.filter(o => ['L','C','R'].includes(String(o).toUpperCase()));
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = '付与するメンバーを選択';
      setRichText(elModalText, pendText || `${cardDisplayText(picked)} が持つ色のハートを付与するステージ上メンバーを選んでください。`);
      elModalCards.innerHTML = '';
      elModalActions.innerHTML = '';
      const row = document.createElement('div');
      row.className = 'choiceRow';
      row.style.overflowX = 'visible';
      row.style.overflowY = 'visible';
      row.style.maxWidth = 'none';
      row.style.width = 'max-content';
      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');
      posOpts.forEach(rawPos=>{
        const pos = String(rawPos).toUpperCase();
        const slot = st && st.stage ? st.stage[pos] : null;
        const cn = slot && slot.cardnumber ? String(slot.cardnumber) : '';
        const label = {L:'レフトエリア', C:'センターエリア', R:'ライトエリア'}[pos] || pos;
        const intr = intrinsicOrient(cn);
        const d = (intr === 'landscape') ? dimsL : dimsP;
        const b = document.createElement('button');
        b.className = 'choiceBtn';
        b.style.width = d.w + 'px';
        b.style.height = d.h + 'px';
        const img = document.createElement('img');
        img.src = imgUrl(cn);
        img.alt = cn;
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = `${label} / ${cardDisplayText(cn)}`;
        b.appendChild(img);
        b.appendChild(cap);
        b.title = `${cardDisplayText(picked)} が持つ色のハートを ${label} の ${cardDisplayText(cn)} に付与`;
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:pos});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      elModalCards.appendChild(row);
      elMask.style.display = 'block';
      return;
    }

    if(kind === 'confirm_repeat_mill_top1_gain_blade_wait_if_live'){
      const displayCards = Array.isArray(p.display_cards) ? p.display_cards : [];
      if(displayCards.length){
        const helper = pendText || '直前に控え室へ置いたカードを確認し、続けるか選んでください。';
        openCardListPopup('効果処理結果', displayCards, {closable:false, helperText:helper});
        popup = {type:'pending', closable:false};
        elModalActions.innerHTML = '';
        const bUse = document.createElement('button');
        bUse.className = 'miniBtn';
        bUse.textContent = '続ける';
        bUse.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:'使う'});
          selHand=[]; updateTop(); render();
        });
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn';
        bSkip.textContent = '終了';
        bSkip.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:'スキップ'});
          selHand=[]; updateTop(); render();
        });
        elModalActions.appendChild(bUse);
        elModalActions.appendChild(bSkip);
        return;
      }
    }

    if(kind === 'topk_stage_or_hand'){
      const cardCn = String((p && p.card) || '').trim();
      const row = document.createElement('div');
      row.style.cssText = 'display:flex;flex-direction:column;gap:10px;align-items:stretch;max-width:720px;';
      const choices = [];
      if(opts.some(o => String(o).toLowerCase() === 'hand')){
        choices.push({choice:'hand', title:'手札に加える', body:`${cardDisplayText(cardCn)} を手札に加えます。`});
      }
      ['L','C','R'].forEach(pos=>{
        if(opts.some(o => String(o).toUpperCase() === pos)){
          const posLabel = {L:'レフトエリア', C:'センターエリア', R:'ライトエリア'}[pos] || pos;
          choices.push({choice:pos, title:`${posLabel}に登場させる`, body:`メンバーのいない${posLabel}に ${cardDisplayText(cardCn)} を登場させます。`});
        }
      });
      choices.forEach(it=>{
        const b = document.createElement('button');
        b.className = 'miniBtn';
        b.style.cssText = 'text-align:left;padding:12px 14px;border-radius:12px;line-height:1.45;background:rgba(255,255,255,.08);';
        const title = document.createElement('div');
        title.style.cssText = 'font-weight:900;color:#fff;font-size:14px;';
        title.textContent = it.title;
        const body = document.createElement('div');
        body.style.cssText = 'font-size:12px;color:#cfcfcf;margin-top:4px;';
        body.textContent = it.body;
        b.appendChild(title);
        b.appendChild(body);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice:it.choice});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      if(!choices.length){
        const note = document.createElement('div');
        note.style.cssText = 'color:#ddd;font-size:13px;';
        note.textContent = '選択できる移動先がありません。';
        row.appendChild(note);
      }
      elModalCards.appendChild(row);
      elMask.style.display = 'block';
      return;
    }

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

    // pick_from_yell / pick_from_yell_to_deck_top / pick_from_yell_to_deck_bottom: show yell-revealed card choices as card images + Skip.
    // options intentionally may contain 'skip', so handle this before the generic allCardNo fallback.
    if(kind === 'pick_from_yell' || kind === 'pick_from_yell_to_deck_top' || kind === 'pick_from_yell_to_deck_bottom'){
      const cardOpts = opts.filter(o => looksLikeCardNo(String(o)));
      const hasSkip  = opts.some(o => String(o).toLowerCase() === 'skip') || allowSkip;
      popup = {type:'pending', closable:false};
      elModalTitle.textContent = 'エール公開カードを選択';
      let defaultPickText = 'エールにより公開されたカードから、手札に加えるカードを選んでください。';
      if(kind === 'pick_from_yell_to_deck_top'){
        defaultPickText = 'エールにより公開されたカードから、デッキの一番上に置くカードを選んでください。';
      }else if(kind === 'pick_from_yell_to_deck_bottom'){
        defaultPickText = 'エールにより公開されたカードから、デッキの一番下に置くカードを選んでください。';
      }
      setRichText(elModalText, pendText || defaultPickText);
      elModalActions.innerHTML = '';
      elModalCards.innerHTML = '';

      const row = document.createElement('div');
      row.className = 'choiceRow';
      // Use only #modalCards as the horizontal scroller for this card list.
      // Leaving .choiceRow scrollable creates two horizontal scrollbars.
      row.style.overflowX = 'visible';
      row.style.overflowY = 'visible';
      row.style.maxWidth = 'none';
      row.style.width = 'max-content';
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
        img.src = imgUrl(cn);
        img.alt = cn;
        dupSeen[cn] = (dupSeen[cn]||0)+1;
        const nth = dupSeen[cn];
        const tot = dupCount[cn]||0;
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = cardChoiceCaption(cn, nth, tot);
        b.appendChild(img);
        b.appendChild(cap);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: cn});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      if(cardOpts.length){
        elModalCards.appendChild(row);
      }else{
        const note = document.createElement('div');
        note.style.opacity = '0.85';
        note.style.fontSize = '13px';
        note.style.padding = '6px 0';
        note.textContent = '候補カードが表示できませんでした。スキップするか、ログを確認してください。';
        elModalCards.appendChild(note);
      }
      if(hasSkip){
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn';
        bSkip.textContent = 'スキップ';
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

    // choose_*_from_green: card images + optional Skip button when 1枚まで/optional
    if(kind === 'choose_live_from_green' || kind === 'choose_member_from_green' || kind === 'choose_card_from_green' || kind === 'choose_live_from_green_to_deck_nth'){
      const cardOpts = opts.filter(o => looksLikeCardNo(String(o)));
      const hasSkip = !!(p && (p.allow_skip || p.allow_less || p.optional)) || opts.some(o => String(o).toLowerCase() === 'skip');
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
        const cap = document.createElement('div');
        cap.className = 'choiceCap';
        cap.textContent = cardChoiceCaption(cn, dupSeen[cn], dupCount[cn]||0);
        b.appendChild(img); b.appendChild(cap);
        b.addEventListener('click', async ev=>{
          ev.stopPropagation();
          st = await apiCmd('resolve_pending', {idx:0, choice: cn});
          selHand=[]; updateTop(); render();
        });
        row.appendChild(b);
      });
      if(cardOpts.length){
        elModalCards.appendChild(row);
      }else{
        const note = document.createElement('div');
        note.style.opacity = '0.85';
        note.style.fontSize = '13px';
        note.style.padding = '6px 0';
        note.textContent = '候補カードがありません。';
        elModalCards.appendChild(note);
      }
      if(hasSkip){
        const bSkip = document.createElement('button');
        bSkip.className = 'miniBtn';
        bSkip.textContent = 'スキップ';
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

    // topdeck_from_green / bottomdeck_from_green / live storage / hand_to_deck_bottom: card images + optional Skip button
    if(kind === 'topdeck_from_green' || kind === 'bottomdeck_from_green' || kind === 'live_storage_live_to_deck_top_gain_icons' || kind === 'hand_to_deck_bottom' || kind === 'hand_to_deck_top_or_bottom'){
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
        if(kind === 'choose_opponent_wait_count_for_topdeck_green_group_members' || kind === 'opponent_wait_notify'){
          b.textContent = String(opt);
        }else{
          b.textContent = '';
          b.appendChild(choiceRichLabel(opt, kind));
        }
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


  function showPublicPending(p){
    popup = {type:'public_pending', closable:false};
    clearModalLead();
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';
    elModalCond.className = '';
    elModalCond.textContent = '';

    const kind = String((p && p.kind) || 'pending');
    const hidden = !!(p && p.public_hidden);
    const title = String((p && p.title) || pendingTitleFor(p) || (hidden ? '非公開情報を確認中' : '効果の選択'));
    elModalTitle.textContent = title;

    const body = String((p && (p.text || p.effect_text)) || pendingTextFor(p) || (hidden ? 'メイン画面で非公開領域のカードを確認・選択しています。' : '効果を処理しています。'));
    setRichText(elModalText, body);

    const pubStatus = pendingConditionStatus(p || {});
    if(pubStatus && pubStatus.text){
      elModalCond.textContent = pubStatus.text;
      elModalCond.className = pubStatus.state === 'met' ? 'condMet' : (pubStatus.state === 'unmet' ? 'condUnmet' : 'condNeutral');
      elModalCond.style.display = 'block';
    }else{
      elModalCond.style.display = 'none';
    }

    const src = String((p && p.source) || '');
    if(src && looksLikeCardNo(src)){
      const row = document.createElement('div');
      row.className = 'choiceRow';
      const orient = intrinsicOrient(src);
      const d = standardSize(orient);
      const card = makeCard(src, orient, 0, 0, d.w, d.h, cardNameFor(src), null, false, 100);
      card.style.position = 'relative';
      row.appendChild(card);
      elModalCards.appendChild(row);
    }

    const displayCards = (p && Array.isArray(p.display_cards)) ? p.display_cards.map(x=>String(x||'')).filter(Boolean) : [];
    if(displayCards.length){
      const row = document.createElement('div');
      row.className = 'choiceRow';
      displayCards.forEach((cn0, idx)=>{
        const orient0 = intrinsicOrient(cn0);
        const d0 = standardSize(orient0);
        const card0 = makeCard(cn0, orient0, 0, 0, d0.w, d0.h, cardNameFor(cn0), null, false, 110 + idx);
        card0.style.position = 'relative';
        row.appendChild(card0);
      });
      elModalCards.appendChild(row);
      if(isYellRevealPending(p)){
        appendYellRevealDrawNotice(p);
      }
    }

    const publicOptions = (p && Array.isArray(p.options)) ? p.options.map(x=>String(x||'')).filter(Boolean) : [];
    if(publicOptions.length){
      const row = document.createElement('div');
      row.className = 'choiceRow';
      row.style.cssText = 'gap:calc(7px * var(--uiScale));align-items:center;justify-content:center;flex-wrap:wrap;';
      publicOptions.forEach(opt=>{
        const chip = document.createElement('span');
        chip.className = 'miniBtn';
        chip.style.cssText = 'opacity:.75;cursor:default;pointer-events:none;';
        chip.appendChild(choiceRichLabel(opt, kind));
        row.appendChild(chip);
      });
      elModalCards.appendChild(row);
    }

    const note = document.createElement('div');
    note.className = 'publicPendingNote';
    if(hidden){
      note.textContent = 'PUBLIC VIEW: 非公開領域を含むため、詳細なカード候補はメイン画面だけに表示しています。';
    }else{
      note.textContent = 'PUBLIC VIEW: 表示内容はメイン画面と同じです。操作はメイン画面で行います。';
    }
    elModalActions.appendChild(note);
    elMask.style.display = 'block';
    applyPopupPeekState();
  }

  function maybeShowPublicPending(){
    if(!IS_PUBLIC_VIEW) return false;
    // Pending windows are now sanitized in views.py and rendered through the same
    // showPending() path as the owner window.  This function is kept only for
    // short-lived public reveal ledger popups after owner-side ACKs disappear.
    const ev = (st && Array.isArray(st.public_reveal_events) && st.public_reveal_events.length) ? st.public_reveal_events[0] : null;
    if(ev){
      showPublicPending(ev);
      return true;
    }
    if(popup && popup.type === 'public_pending'){
      closePopup();
    }
    return false;
  }

  function maybeShowPending(){
    const p = (st && Array.isArray(st.pending) && st.pending.length) ? st.pending[0] : null;
    if(p){
      if(popup && popup.type === 'cardlist' && !popup.closable) closePopup();
      showPending(p);
      return true;
    }
    if(popup && popup.type==='pending'){
      closePopup();
    }
    return false;
  }

  function maybeShowResolvePopup(){
    const rz = (st && Array.isArray(st.resolve_zone)) ? st.resolve_zone.map(x=>String(x||'')).filter(Boolean) : [];
    if(!!(st && st.yell_reveal_acknowledged_this_live)){
      if(popup && popup.type==='yell_reveal_fallback') closePopup();
      return false;
    }
    if(rz.length <= 0){
      if(popup && popup.type==='yell_reveal_fallback') closePopup();
      if(popup && popup.type==='cardlist' && !popup.closable && String(popup.title || '') === '解決領域') closePopup();
      return false;
    }

    // Fallback for YELL reveal routes that currently do not create an explicit
    // show_revealed_cards_ack pending.  Do not show the old generic
    // "解決領域" modal; synthesize the dedicated YELL reveal confirmation
    // layout from resolve_zone instead.
    const synthetic = {
      kind: 'show_revealed_cards_ack',
      label: 'エール公開カード確認',
      text: 'エールで公開されたカードを確認してから、NEXTで次へ進みます。',
      display_cards: rz
    };
    openYellRevealPopup(synthetic);
    popup = {type:'yell_reveal_fallback', closable:false, title:'エール公開カード確認'};
    const btnOk = document.createElement('button');
    btnOk.className = 'miniBtn';
    btnOk.textContent = '確認';
    let submitting = false;
    btnOk.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      if(submitting) return;
      submitting = true;
      st = await apiCmd('ack_yell_reveal', {});
      selHand = [];
      updateTop();
      render();
    });
    elModalActions.appendChild(btnOk);
    return true;
  }

  function updateTop(){
    elTurn.textContent = st ? String(st.turn) : '?';
    elPhase.textContent = st ? String(st.phase) : '?';
    const active = st ? Number(st.energy_active||0) : 0;
    const wait = st ? Number(st.energy_wait||0) : 0;
    elEnergy.textContent = st ? `${active}/${active+wait}` : '?';
    if(elOpponentWait) elOpponentWait.textContent = st ? String(Math.max(0, Math.min(3, Number(st.opponent_wait_count||0)))) : '?';
    if(btnOppWaitMinus) btnOppWaitMinus.disabled = !st || Number(st.opponent_wait_count||0) <= 0;
    if(btnOppWaitPlus) btnOppWaitPlus.disabled = !st || Number(st.opponent_wait_count||0) >= 3;
    if(elOpponentSuccess) elOpponentSuccess.textContent = st ? String(Math.max(0, Math.min(2, Number(st.opponent_success_count||0)))) : '?';
    if(btnOppSuccessMinus) btnOppSuccessMinus.disabled = !st || Number(st.opponent_success_count||0) <= 0;
    if(btnOppSuccessPlus) btnOppSuccessPlus.disabled = !st || Number(st.opponent_success_count||0) >= 2;
    const ord = st ? String(st.turn_order || 'first') : 'first';
    if(elTurnOrder) elTurnOrder.textContent = (ord === 'second') ? '後手' : '先手';
    if(btnOrderFirst){
      btnOrderFirst.disabled = !st;
      btnOrderFirst.classList.toggle('orderSelected', !!st && ord !== 'second');
    }
    if(btnOrderSecond){
      btnOrderSecond.disabled = !st;
      btnOrderSecond.classList.toggle('orderSelected', !!st && ord === 'second');
    }
    elSelected.textContent = String(selHand.length);
    if(elResetPanel){
      const show = !!st && !IS_PUBLIC_VIEW;
      const remote = !!(st && st.remote_mode);
      elResetPanel.classList.toggle('visible', show);
      if(btnSingleReset) btnSingleReset.style.display = (show && !remote) ? '' : 'none';
      if(btnRecordWin) btnRecordWin.style.display = (show && remote) ? '' : 'none';
      if(btnRecordLose) btnRecordLose.style.display = (show && remote) ? '' : 'none';
      if(btnRecordNoGame) btnRecordNoGame.style.display = (show && remote) ? '' : 'none';
      [btnSingleReset, btnRecordWin, btnRecordLose, btnRecordNoGame].forEach(btn=>{ if(btn) btn.disabled = !show; });
    }
    updateDebugMoveButton();
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
      if(z.kind==='log') renderLog(zd, st.log || [], st.effect_events || []);
    }
    renderStatsPanel();

    // DECK: public view receives only deck_count, so keep the back-card mask visible.
    const deckCount = IS_PUBLIC_VIEW ? publicCount('deck_count', st.deck||[]) : ((st.deck||[]).length);
    const deckClick = (!IS_PUBLIC_VIEW && debugMoveMode)
      ? (()=>openCardListPopup('山札', Array.isArray(st.deck) ? st.deck : [], {closable:true, helperText:'デバッグモード: 山札の順番を入れ替え、カードを選んで移動できます。', debugZone:'deck'}))
      : null;
    if(deckCount > 0){
      renderTopCard(zels.deck, '__BACK__', 'portrait', deckCount, deckClick, {useStandardSize:true});
    }else{
      renderEmptyZone(zels.deck, 0, (debugMoveMode && debugMoveSelection && !IS_PUBLIC_VIEW) ? (()=>putDebugMoveCard('deck', 0)) : deckClick);
    }

    // Waiting room: カードあり→最後尾を表示、なし→何も表示しない
    const gr = Array.isArray(st.green_room) ? st.green_room : [];
    if(gr.length){
      renderTopCard(zels.green, String(gr[gr.length-1]), 'portrait', gr.length, ()=>{
        openCardListPopup('控え室', gr, {closable:true, helperText: debugMoveMode ? 'デバッグモード: 控え室の順番を入れ替え、カードを選んで移動できます。' : '', debugZone: debugMoveMode ? 'green_room' : ''});
      }, {instanceId: zoneInstanceId('green_room', gr.length - 1)});
    }else{
      renderEmptyZone(zels.green, 0, (debugMoveMode && debugMoveSelection && !IS_PUBLIC_VIEW) ? (()=>putDebugMoveCard('green_room', 0)) : null);
    }

    // Success live storage: カードあり→縦スタック表示、なし→何も表示しない
    const sz = Array.isArray(st.success_zone) ? st.success_zone : [];
    if(sz.length){
      renderVertStack(zels.success, sz, 'landscape', sz.length, ()=>{
        openCardListPopup('成功ライブ', sz, {closable:true, helperText: debugMoveMode ? 'デバッグモード: カードを選んで移動できます。' : '', forceLandscape:true, debugZone: debugMoveMode ? 'success_zone' : ''});
      }, {overlap:0.70, maxShow:4, forceIntrinsicOrient:'landscape', instanceIds: st.card_instances && st.card_instances.success_zone});
    }else{
      renderEmptyZone(zels.success, null, (debugMoveMode && debugMoveSelection && !IS_PUBLIC_VIEW) ? (()=>putDebugMoveCard('success_zone', 0)) : null);
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

    // Hand: public view must show a masked hand, not an empty 0-card area.
    if(IS_PUBLIC_VIEW){
      renderMaskedHand(zels.hand, publicCount('hand_count', st.hand||[]), publicHandRevealedCards());
    }else{
      renderHand(zels.hand, Array.isArray(st.hand)?st.hand:[]);
    }

    renderPublicKnownHandPanel();
    consumePublicHandRevealEvents();

    // Refresh notices are rule-processing results and should be shown before
    // any follow-up choice pending created by the interrupted effect.
    if(maybeShowRefreshNotice()){
      // wait for local OK; after closing, render() will continue to pending.
    }else if(IS_PUBLIC_VIEW){
      if(!maybeShowPending()){
        if(!maybeShowPublicPending()){
          maybeShowResolvePopup();
        }
      }
    }else if(!maybeShowPending()){
      maybeShowResolvePopup();
    }
    applyPopupPeekState();
  }

  btnDbg.addEventListener('click', ()=>{ debug = !debug; render(); });
  if(btnDebugMove){
    btnDebugMove.addEventListener('click', async ()=>{
      const nextMode = !debugMoveMode;
      debugMoveMode = nextMode;
      clearDebugMoveSelection();
      selHand = [];
      if(debugMoveMode && st && !st.debug){
        st = await apiCmd('toggle_debug', {});
        debugMoveEnabledServerDebug = true;
      }else if(!debugMoveMode && debugMoveEnabledServerDebug && st && st.debug){
        st = await apiCmd('toggle_debug', {});
        debugMoveEnabledServerDebug = false;
      }
      updateDebugMoveButton();
      setBanner(debugMoveMode ? 'デバッグモード: カードを選んで移動先をクリック' : 'デバッグモードを終了');
      render();
    });
  }
  if(btnSuspendSave){
    btnSuspendSave.addEventListener('click', (ev)=>{
      ev.stopPropagation();
      saveSuspendData();
    });
  }
  if(btnSuspendLoad && suspendFileInput){
    btnSuspendLoad.addEventListener('click', (ev)=>{
      ev.stopPropagation();
      suspendFileInput.click();
    });
    suspendFileInput.addEventListener('change', (ev)=>{
      const file = ev && ev.target && ev.target.files ? ev.target.files[0] : null;
      loadSuspendDataFile(file);
    });
  }
  elMask.addEventListener('click', (ev)=>{ if(popup && popup.type==='cardlist' && popup.closable){ closePopup(); } });
  elViewerLayer.addEventListener('click', (ev)=>{ if(ev.target === elViewerLayer){ closeViewerPopup(); } });
  elViewerModal.addEventListener('click', (ev)=>{ ev.stopPropagation(); });

  let lastStateSignature = '';
  let statePollInFlight = false;
  function stableStateSignature(s){
    try { return JSON.stringify(s || {}); }
    catch(e){ return String(Date.now()); }
  }
  async function refreshStateFromServer({force=false} = {}){
    if(statePollInFlight) return;
    statePollInFlight = true;
    try{
      const next = await apiState();
      const sig = stableStateSignature(next);
      if(force || sig !== lastStateSignature){
        st = next;
        lastStateSignature = sig;
        updateTop();
        render();
      }
    }catch(err){
      console.error(err);
      if(force) alert('Failed to load /state. Is the server running?');
    }finally{
      statePollInFlight = false;
    }
  }

  // init
  cssScale();
  refreshStateFromServer({force:true});
  // Public window is read-only and must follow the owner window automatically.
  // The owner/private window still updates immediately after each /cmd response.
  if(IS_PUBLIC_VIEW){
    setInterval(()=>{ refreshStateFromServer({force:false}); }, 1200);
    window.addEventListener('storage', (ev)=>{
      if(ev && ev.key === 'llocg_public_refresh_ping'){
        refreshStateFromServer({force:true});
      }
    });
  }
})();
</script>
</body>
</html>'''

HTML = HTML.replace('__LOVECA_APP_VERSION__', APP_VERSION)
