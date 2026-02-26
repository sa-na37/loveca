# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
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
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs, unquote

from .db import load_cards_db
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
    cmd_resolve_pending,
    _get_card,
    _has_sacrifice_ability,
    can_activate,
)

APP_VERSION = "clean-ui-v2_6_waiting_sort_click_and_skip"


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
        self.save_trace()

    def save_trace(self) -> None:
        self.outdir.mkdir(parents=True, exist_ok=True)
        _write_text(self.outdir / "ui_trace.txt", "\n".join(self.gs.log) + ("\n" if self.gs.log else ""))

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
            "resolve_zone": list(self.gs.resolve_zone),
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
                        "can_activate": can_activate(_get_card(self.cards_db, v.cardnumber)),
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

    def cmd(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
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
            cmd_next(self.gs, self.rng, self.cards_db, [int(x) for x in idxs])
        elif name == "end_turn":
            cmd_end_turn(self.gs, self.rng)
        elif name == "undo":
            do_undo(self.gs, self.rng)
        elif name == "toggle_debug":
            self.gs.debug = not self.gs.debug
            self.gs.log.append(f"[DEBUG] debug={self.gs.debug}")
        else:
            self.gs.log.append(f"[ERR] unknown cmd: {name}")

        self.save_trace()
        return self.state_json()



# PATCH_SORT_META_V1
_CN_META_CACHE = None

def _infer_num(cn: str) -> int:
    m = re.search(r"(\d+)(?!.*\d)", cn or "")
    return int(m.group(1)) if m else 10**9

def _infer_prefix(cn: str) -> str:
    cn = (cn or '').rstrip('-')
    m = re.search(r'^(.*?)-(\d+)$', cn)
    return m.group(1) if m else cn

def _infer_rarity_from_cn(cn: str) -> str:
    if not cn:
        return ""
    m = re.search(r"-(PR|UR|SR|R|U|C|SEC)(?:-|$)", cn, flags=re.I)
    return (m.group(1) or "").upper() if m else ""

def _normalize_type(t: str) -> str:
    if not t:
        return ""
    tt = str(t).strip().upper()
    if "MEMBER" in tt or "メンバー" in tt:
        return "MEMBER"
    if "LIVE" in tt or "ライブ" in tt:
        return "LIVE"
    if "SUPPORT" in tt or "サポート" in tt:
        return "SUPPORT"
    if "EVENT" in tt:
        return "EVENT"
    return tt

def _load_cn_meta():
    global _CN_META_CACHE
    if _CN_META_CACHE is not None:
        return _CN_META_CACHE

    here = Path(__file__).resolve()
    root = here.parent.parent
    cand = [
        root / "cards_min_tokv1.csv",
        root / "llocg_db_out_full" / "cards_min_tokv1.csv",
        here.parent / "cards_min_tokv1.csv",
    ]
    fp = None
    for c in cand:
        if c.exists():
            fp = c
            break

    meta = {}
    if fp is None:
        _CN_META_CACHE = meta
        return meta

    def pick(row, keys):
        for k in keys:
            if k in row and row[k] not in (None, ""):
                return row[k]
        low = {kk.lower(): kk for kk in row.keys()}
        for k in keys:
            kk = low.get(k.lower())
            if kk and row.get(kk) not in (None, ""):
                return row.get(kk)
        return ""

    with fp.open("r", encoding="utf-8-sig", newline="") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            cn = pick(row, ["cardnumber","card_no","cn","\ufeffcardnumber"])
            if not cn:
                continue
            rarity = pick(row, ["rarity","rare","rar"])
            ctype = pick(row, ["card_type_norm","card_type_raw","card_type","type","db_type","category","cardtype"])
            cn = str(cn)
            meta[cn] = {
                "type": _normalize_type(ctype),
                "prefix": _infer_prefix(cn),
                "num": _infer_num(cn),
                "rarity": (str(rarity).strip().upper() if rarity else _infer_rarity_from_cn(cn)),
            }

    _CN_META_CACHE = meta
    return meta

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

        if u.path == "/meta":

            qs = dict(parse_qsl(u.query))

            cn = qs.get("cn","")

            meta = _load_cn_meta().get(cn, {})

            self._send(200, json.dumps(meta, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

            return

        if u.path == "/meta_bulk":

            qs = dict(parse_qsl(u.query))

            raw = qs.get("cns","")

            cns = [x for x in raw.split(",") if x]

            allm = _load_cn_meta()

            out = {cn: allm.get(cn, {}) for cn in cns}

            self._send(200, json.dumps(out, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

            return


        if u.path == "/img":
            qs = parse_qs(u.query)
            cn = unquote((qs.get("cn", [""])[0] or "").strip())
            p = self.app.img.find(cn)
            if p and p.exists():
                ctype = "image/png"
                if str(p).lower().endswith((".jpg", ".jpeg")):
                    ctype = "image/jpeg"
                self._send(200, p.read_bytes(), ctype)
            else:
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

  /* small activation button on stage card */
  .actBtn{position:absolute;left:6px;right:6px;bottom:6px;padding:6px 6px;border-radius:10px;border:1px solid rgba(255,255,255,.18);
          background:rgba(0,0,0,.6);color:#fff;font-size:12px;cursor:pointer;}
  .actBtn:hover{background:rgba(0,0,0,.74);}

  /* popups */
  #mask{position:absolute;left:0;top:0;bottom:0;right:var(--sideW);background:rgba(0,0,0,.55);display:none;z-index:9000;}
  #modal{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(92%, calc(var(--pmW) - var(--sideW) - 140px));max-height:min(64%, calc(var(--pmH) - 160px));overflow:hidden;background:#1b1b1b;border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:12px;box-shadow:0 14px 60px rgba(0,0,0,.7);display:flex;flex-direction:column;}
  #modalTitle{font-weight:700;}
  #modalText{white-space:pre-wrap;line-height:1.35;color:#ddd;font-size:13px;margin-top:8px;}
  #modalCards{margin-top:10px;overflow-x:auto;overflow-y:hidden;padding-bottom:6px;} 
  #modalCards .surf{position:relative;height:1px;}
  #modalActions{display:flex;gap:8px;justify-content:flex-end;margin-top:10px;flex-wrap:wrap;}
  #modalActions .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:10px;cursor:pointer;}
/* UI_FIX_PENDING_CARD_CHOICES */
  /* pending card choice list (image buttons) */
  .choiceRow{display:inline-flex;gap:8px;align-items:flex-start;overflow-x:auto;overflow-y:hidden;max-width:min(72vw, 1060px);padding:6px 2px 10px 2px;}
  .choiceBtn{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);border-radius:12px;padding:0;cursor:pointer;position:relative;flex:0 0 auto;box-shadow:0 6px 16px rgba(0,0,0,.35);}
  .choiceBtn:hover{outline:3px solid rgba(255,255,255,.22);outline-offset:-3px;}
  .choiceBtn img{width:100%;height:100%;object-fit:cover;display:block;border-radius:12px;}
  .choiceCap{position:absolute;left:0;right:0;bottom:0;font-size:11px;padding:4px 6px;background:linear-gradient(to top, rgba(0,0,0,.65), rgba(0,0,0,.05));color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6);border-bottom-left-radius:12px;border-bottom-right-radius:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
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
        <div id="modalText"></div>
        <div id="modalCards"></div>
        <div id="modalActions"></div>
      </div>
    </div>
  </div>
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

  function selLimit(){
    if(!st) return 1;
    return (st.phase === 'LIVE_SET') ? 3 : 1;
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
  function makeCard(cn, wantOrient, x, y, w, h, capText, onClick, isSelected=false, z=100){
    const wrap = document.createElement('div');
    wrap.className = 'cardWrap';
    wrap.style.left = x + 'px';
    wrap.style.top = y + 'px';
    wrap.style.width = w + 'px';
    wrap.style.height = h + 'px';
    wrap.style.zIndex = String(z);
    wrap.dataset.baseZ = String(z);
    if(isSelected){ wrap.classList.add('selected'); wrap.style.zIndex='18000'; wrap.dataset.baseZ='18000'; }

    const intr = intrinsicOrient(cn);
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

    // hover: lift + bring front
    wrap.addEventListener('mouseenter', ()=>{
      const lift = Math.max(4, Math.floor(w * 0.05));
      wrap.style.transform = `translateY(${-lift}px)`;
      wrap.style.zIndex = '20000';
    });
    wrap.addEventListener('mouseleave', ()=>{
      wrap.style.transform = '';
      wrap.style.zIndex = wrap.dataset.baseZ || '100';
    });

    if(onClick){
      wrap.addEventListener('click', (ev)=>{ ev.stopPropagation(); onClick(); });
    }else{
      wrap.addEventListener('click', (ev)=>{ ev.stopPropagation(); });
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
    for(let i=0;i<3;i++){
      const cn = (Array.isArray(cards) && i < cards.length) ? String(cards[i]) : null;
      if(!cn) continue;
      const sz = computeDispSize('landscape', slotW, availH);
      const x = padX + slotsX[i] + (slotW - sz.w)/2;
      const y = padTop + Math.max(0, (availH - sz.h)/2);
      const card = makeCard(cn, 'landscape', x, y, sz.w, sz.h, '', null, false, 100+i);
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
    const sz = computeDispSize('portrait', availW, availH);
    // cache standard card size from hand area
    stdPortrait = {w: sz.w, h: sz.h};
    stdLandscape = {w: sz.h, h: sz.w};
    const x = (zoneW - sz.w)/2;
    const y = padTop + Math.max(0, (availH - sz.h)/2);

    const card = makeCard(cn, 'portrait', x, y, sz.w, sz.h, labelFor(cn), ()=>doPlayHere(), false, 400);

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

    inner.appendChild(card);
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
    btnNext.textContent = 'NEXT';
    btnNext.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      st = await apiCmd('next', {indices: selHand.slice()});
      selHand = [];
      updateTop();
      render();
    });

    wrap.appendChild(btnUndo);
    wrap.appendChild(btnNext);
    inner.appendChild(wrap);
  }

  function openCardListPopup(title, cards, {closable=true, helperText='', forcePortrait=false } = {}){
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
    elModalText.textContent = helperText || '';
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
      const orient = forcePortrait ? 'portrait' : intrinsicOrient(cn);
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

  function closePopup(){
    popup = {type:null};
    elMask.style.display = 'none';
    elModalCards.innerHTML = '';
    elModalText.textContent = '';
    elModalActions.innerHTML = '';
  }


  
  function looksLikeCardNo(x){
    if(x==null) return false;
    const s = String(x).trim();
    if(!s) return false;
    // Typical cardnumber patterns in this project
    return (s.includes('!') && /\d{2,3}/.test(s)) || /bp\d-\d{3}/i.test(s) || /-PR-\d{3}/i.test(s) || /-P\d-\d{3}/i.test(s);
  }

  function showPending(p){
    popup = {type:'pending', closable:false};
    elModalTitle.textContent = '選択';
    elModalText.textContent = String((p && (p.text || p.prompt || p.message)) ? (p.text || p.prompt || p.message) : '');
    const pendText = String((p && (p.text || p.prompt || p.message)) ? (p.text || p.prompt || p.message) : '');
    const allowSkip = /Skip可/i.test(pendText) || /\bskip\b/i.test(pendText) || (p && p.kind && /pick/i.test(String(p.kind)));
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const opts = (p && (Array.isArray(p.options)?p.options: (Array.isArray(p.candidates)?p.candidates:(Array.isArray(p.cards)?p.cards:(Array.isArray(p.shown)?p.shown:[]))))) || [];
    const allCardNo = opts.length && opts.every(o=>looksLikeCardNo(o));

    if(allCardNo){
      // Render as image list (clickable) in modalCards; keep card size unified
      const row = document.createElement('div');
      row.className = 'choiceRow';

      const dimsP = standardSize('portrait');
      const dimsL = standardSize('landscape');

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
        cap.textContent = cn;

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

    }else if(opts.length){
      // Fallback: text buttons
      opts.forEach(opt=>{
        const b = document.createElement('button');
        b.className = 'miniBtn';
        b.textContent = String(opt);
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

    // DECK (always back)
    const deckCount = (st.deck||[]).length;
    renderTopCard(zels.deck, '__BACK__', 'portrait', deckCount, null);

    // Waiting room (show top card if exists)
    const gr = Array.isArray(st.green_room) ? st.green_room : [];
    const top = gr.length ? String(gr[gr.length-1]) : '__BACK__';
    renderTopCard(zels.green, top, 'portrait', gr.length, ()=>{
      if(gr.length){
        openCardListPopup('控え室', gr, {closable:true, helperText:''});
      }else{
        openCardListPopup('控え室', ['__BACK__'], {closable:true, helperText:'（空）'});
      }
    });

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

<script id="llEnhSortV2">
(()=> {
  /* PATCH_SORT_JS_V2 */
  if (window.__llEnhSortV2) return;
  window.__llEnhSortV2 = true;

  const TYPE_RANK = (t)=> {
    const x = String(t||"").toUpperCase();
    if (x.includes("MEMBER")) return 0;
    if (x.includes("LIVE")) return 1;
    if (x.includes("SUPPORT")) return 2;
    if (x.includes("EVENT")) return 3;
    return 9;
  };
  const RAR_RANK = (r)=> {
    const x = String(r||"").toUpperCase();
    const map = { "C":0, "U":1, "R":2, "SR":3, "UR":4, "SEC":5, "PR":6 };
    return (map[x] ?? 99);
  };
  const PREF_OF = (cn, meta)=> {
    if (meta && meta.prefix) return String(meta.prefix);
    const s = String(cn||"").replace(/-+$/,"");
    const m = s.match(/^(.*?)-(\d+)$/);
    return m ? m[1] : s;
  };
  const NUM_OF = (cn, meta)=> {
    if (meta && typeof meta.num === "number") return meta.num;
    const m = String(cn||"").match(/(\d+)(?!.*\d)/);
    return m ? parseInt(m[1],10) : 1e9;
  };

  const metaCache = new Map(); // cn -> meta
  async function getMetaBulk(cns){
    const need = cns.filter(cn => !metaCache.has(cn));
    if (need.length){
      try{
        const url = "/meta_bulk?cns=" + encodeURIComponent(need.join(","));
        const r = await fetch(url, {cache:"no-store"});
        if (r.ok){
          const obj = await r.json();
          for (const [cn, m] of Object.entries(obj||{})) {
            metaCache.set(cn, m||{});
          }
        }
      }catch(_e){}
      for (const cn of need) if (!metaCache.has(cn)) metaCache.set(cn, {});
    }
  }

  function getCN(el){
    const cap = el.querySelector(".llEnhCap");
    return cap ? cap.textContent.trim() : "";
  }

  async function sortContainer(container){
    if (!container) return;
    const kids = Array.from(container.children);
    const items = kids.filter(ch => ch.querySelector && ch.querySelector(".llEnhCap"));
    if (items.length < 2) return;
    const cns = items.map(getCN).filter(Boolean);
    if (cns.length < 2) return;

    await getMetaBulk(cns);

    items.sort((a,b)=>{
      const ca = getCN(a), cb = getCN(b);
      const ma = metaCache.get(ca) || {};
      const mb = metaCache.get(cb) || {};

      const ta = TYPE_RANK(ma.type), tb = TYPE_RANK(mb.type);
      if (ta !== tb) return ta - tb;

      const pa = PREF_OF(ca, ma), pb = PREF_OF(cb, mb);
      if (pa !== pb) return pa.localeCompare(pb);

      const na = NUM_OF(ca, ma), nb = NUM_OF(cb, mb);
      if (na !== nb) return na - nb;

      const ra = RAR_RANK(ma.rarity), rb = RAR_RANK(mb.rarity);
      if (ra !== rb) return ra - rb;

      return ca.localeCompare(cb);
    });

    for (const it of items) container.appendChild(it);
  }

  function scanAndSort(){
    document.querySelectorAll(".llEnhRow").forEach(c=>sortContainer(c));
    document.querySelectorAll(".llEnhChoiceWrap").forEach(c=>sortContainer(c));
    document.querySelectorAll(".cardList,.cards,.cardlist,.list").forEach(c=>sortContainer(c));
  }

  const mo = new MutationObserver(()=>scanAndSort());
  mo.observe(document.documentElement, {subtree:true, childList:true});
  document.addEventListener("DOMContentLoaded", ()=>setTimeout(scanAndSort, 120));
  setTimeout(scanAndSort, 900);
})();
</script>

</body>
</html>'''