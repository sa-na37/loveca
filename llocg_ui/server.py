# -*- coding: utf-8 -*-
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

APP_VERSION = "clean-ui-v1"


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
<title>LLCG Manual UI (Clean)</title>
<style>
  :root{
    --pmW: 1200px;
    --pmH: 654px;
    --scale: 0.77;
    --cardW: 347px;
    --cardH: 485px;
    --gap: 8px;
  }
  html,body{height:100%;margin:0;background:#111;color:#eee;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;}
  #root{height:100%;display:flex;align-items:center;justify-content:center;}
  #pmWrap{position:relative;width:var(--pmW);height:var(--pmH);background:#222;box-shadow:0 10px 40px rgba(0,0,0,.6);overflow:hidden;border-radius:10px;}
  #playmat{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;user-select:none;pointer-events:none;}
  #zones{position:absolute;inset:0;}

  /* zone shell */
  .zone{position:absolute;box-sizing:border-box;}
  .zone.debug{outline:2px dashed rgba(0,0,0,.35);}
  .label{position:absolute;left:6px;top:6px;padding:2px 6px;font-size:12px;background:rgba(0,0,0,.55);border-radius:6px;pointer-events:none;}
  .countBadge{position:absolute;right:6px;bottom:6px;padding:2px 6px;font-size:12px;background:rgba(0,0,0,.75);border-radius:6px;pointer-events:none;}
  .zoneInner{position:absolute;inset:0;overflow:hidden;}
  .scrollX{overflow-x:auto;overflow-y:hidden;}

  /* cards */
  .cardWrap{position:absolute;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,.55);user-select:none;cursor:pointer;background:#000;}
  .cardWrap img{position:absolute;left:0;top:0;border-radius:8px;display:block;width:100%;height:100%;pointer-events:none;}
  .cardWrap.selected{outline:6px solid rgba(255,213,74,.95); outline-offset:-6px;}
  .cap{position:absolute;left:6px;right:6px;bottom:-18px;font-size:11px;line-height:1.1;color:#eee;text-shadow:0 1px 2px rgba(0,0,0,.8);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none;}

  /* rotation wrappers */
  .rot{position:absolute;left:50%;top:50%;transform-origin:center;}

  /* top bar */
  #topBar{position:absolute;left:10px;top:10px;display:flex;gap:8px;align-items:center;z-index:6000;flex-wrap:wrap;}
  #topBar .pill{background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:6px 10px;font-size:12px;}
  #topBar .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:10px;cursor:pointer;}
  #topBar .miniBtn:hover{background:rgba(255,255,255,.18);}

  /* right command bar */
  #cmdBar{position:absolute;right:10px;top:80px;display:flex;flex-direction:column;gap:8px;z-index:6500;}
  #cmdBar .cmdBtn{background:rgba(0,0,0,.65);color:#eee;border:1px solid rgba(255,255,255,.14);padding:8px 10px;border-radius:12px;cursor:pointer;font-size:12px;text-align:left;min-width:150px;}
  #cmdBar .cmdBtn.primary{background:#ffd54a;color:#111;border-color:rgba(0,0,0,.3);}
  #cmdBar .cmdBtn:disabled{opacity:.45;cursor:not-allowed;}

  /* modal */
  #mask{position:absolute;inset:0;background:rgba(0,0,0,.55);display:none;z-index:9000;}
  #modal{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(92%, calc(var(--pmW) * 0.82));background:#1b1b1b;border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:12px;box-shadow:0 14px 60px rgba(0,0,0,.7);}
  #modalTitle{font-weight:700;}
  #modalText{white-space:pre-wrap;line-height:1.35;color:#ddd;font-size:13px;margin-top:10px;}
  #modalActions{display:flex;gap:8px;justify-content:flex-end;margin-top:12px;flex-wrap:wrap;}
  #modalActions .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:10px;cursor:pointer;}

  /* banner */
  #banner{position:absolute;left:50%;top:54px;transform:translateX(-50%);padding:6px 10px;border-radius:999px;background:rgba(0,0,0,.7);border:1px solid rgba(255,255,255,.18);z-index:7000;display:none;font-size:12px;}

  /* log */
  #logBox{position:absolute;inset:0;overflow:auto;font-size:12px;line-height:1.3;padding:8px;background:rgba(0,0,0,.45);border-radius:10px;white-space:pre-wrap;}
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
      <button class="miniBtn" id="btnDebugToggle">debug</button>
      <div class="pill" id="deckInfo"></div>
    </div>

    <div id="banner"></div>

    <div id="cmdBar">
      <button class="cmdBtn" id="btnUndo">UNDO</button>
      <button class="cmdBtn primary" id="btnNext">NEXT</button>
      <button class="cmdBtn" id="btnEnd">END TURN</button>
      <button class="cmdBtn" id="btnSet">SET (from hand)</button>
      <button class="cmdBtn" id="btnPlayL">PLAY → L</button>
      <button class="cmdBtn" id="btnPlayC">PLAY → C</button>
      <button class="cmdBtn" id="btnPlayR">PLAY → R</button>
      <button class="cmdBtn" id="btnActL">ACTIVATE L→GREEN</button>
      <button class="cmdBtn" id="btnActC">ACTIVATE C→GREEN</button>
      <button class="cmdBtn" id="btnActR">ACTIVATE R→GREEN</button>
      <button class="cmdBtn" id="btnYell">YELL</button>
      <button class="cmdBtn" id="btnAttempt">ATTEMPT</button>
      <button class="cmdBtn" id="btnAck">ACK</button>
    </div>

    <div id="zones"></div>

    <div id="mask">
      <div id="modal">
        <div id="modalTitle">Pending</div>
        <div id="modalText"></div>
        <div id="modalActions"></div>
      </div>
    </div>

  </div>
</div>

<script>
(()=>{
  const BASE_W = 1560;
  const BASE_H = 851;

  // Base (playmat) coordinates; scaled to viewport.
  const layout = {
    zones: {
      deck:    {x: 1235, y:  60, w: 270, h: 180, kind:"stack", orient:"portrait", label:"DECK"},
      green:   {x: 1235, y: 255, w: 270, h: 260, kind:"stack", orient:"portrait", label:"GREEN"},
      log:     {x:   50, y: 585, w: 430, h: 235, kind:"log",   orient:"portrait", label:"LOG"},
      hand:    {x:  520, y: 600, w: 650, h: 235, kind:"fan",   orient:"portrait", label:"HAND"},
      stageL:  {x:  352, y: 280, w: 181, h: 252, kind:"stage", orient:"portrait", label:"L", slot:"L"},
      stageC:  {x:  683, y: 280, w: 180, h: 251, kind:"stage", orient:"portrait", label:"C", slot:"C"},
      stageR:  {x:  995, y: 280, w: 180, h: 251, kind:"stage", orient:"portrait", label:"R", slot:"R"},
      liveset: {x:  600, y:  80, w: 650, h: 200, kind:"fan",   orient:"landscape", label:"LIVE SET"},
      resolve: {x:  520, y: 445, w: 710, h: 160, kind:"fan",   orient:"portrait", label:"RESOLVE"},
      energy:  {x: 1235, y: 545, w: 270, h: 280, kind:"energy",orient:"portrait", label:"ENERGY"},
    }
  };

  const elZones = document.getElementById('zones');
  const elTurn = document.getElementById('turn');
  const elPhase = document.getElementById('phase');
  const elEnergy = document.getElementById('energy');
  const elSelected = document.getElementById('selected');
  const elDeckInfo = document.getElementById('deckInfo');
  const elBanner = document.getElementById('banner');

  const elMask = document.getElementById('mask');
  const elModalTitle = document.getElementById('modalTitle');
  const elModalText = document.getElementById('modalText');
  const elModalActions = document.getElementById('modalActions');

  const btnDbg = document.getElementById('btnDbg');
  const btnDebugToggle = document.getElementById('btnDebugToggle');
  const btnUndo = document.getElementById('btnUndo');
  const btnNext = document.getElementById('btnNext');
  const btnEnd = document.getElementById('btnEnd');
  const btnSet = document.getElementById('btnSet');
  const btnPlayL = document.getElementById('btnPlayL');
  const btnPlayC = document.getElementById('btnPlayC');
  const btnPlayR = document.getElementById('btnPlayR');
  const btnActL = document.getElementById('btnActL');
  const btnActC = document.getElementById('btnActC');
  const btnActR = document.getElementById('btnActR');
  const btnYell = document.getElementById('btnYell');
  const btnAttempt = document.getElementById('btnAttempt');
  const btnAck = document.getElementById('btnAck');

  let debug = false;
  let st = null;
  let selHand = []; // indices

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

  function labelFor(cn){
    const m = (st && st.cn2label) ? st.cn2label : null;
    return (m && m[cn]) ? String(m[cn]) : String(cn);
  }

  function imgUrl(cn){
    const enc = encodeURIComponent(cn);
    return `/img?cn=${enc}`;
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
    render();
  }
  function clearSel(){ selHand = []; render(); }

  function computeDispSize(wantOrient, zoneW, zoneH){
    const cw = px(451), ch = px(630);
    let baseW = (wantOrient==='portrait') ? cw : ch;
    let baseH = (wantOrient==='portrait') ? ch : cw;
    const s = Math.min(1.0, zoneW / baseW, zoneH / baseH);
    return {w: baseW*s, h: baseH*s};
  }

  function makeCard(cn, wantOrient, x, y, w, h, capText, onClick, isSelected=false, z=100){
    const wrap = document.createElement('div');
    wrap.className = 'cardWrap';
    wrap.style.left = x + 'px';
    wrap.style.top = y + 'px';
    wrap.style.width = w + 'px';
    wrap.style.height = h + 'px';
    wrap.style.zIndex = String(z);
    if(isSelected) wrap.classList.add('selected');

    const intr = intrinsicOrient(cn);
    const needsRotate = (intr !== wantOrient);

    if(!needsRotate){
      const img = document.createElement('img');
      img.src = imgUrl(cn);
      img.alt = cn;
      wrap.appendChild(img);
    }else{
      // We keep the wrapper box as desired (w x h), and place a rotated inner box.
      // portrait<-landscape : rotate +90 (CW)
      // landscape<-portrait : rotate -90 (CCW)
      const inner = document.createElement('div');
      inner.className = 'rot';
      const rotDeg = (wantOrient==='portrait') ? 90 : -90;
      inner.style.transform = `translate(-50%,-50%) rotate(${rotDeg}deg)`;
      // inner box should be swapped
      inner.style.width = h + 'px';
      inner.style.height = w + 'px';
      inner.style.marginLeft = '0';
      inner.style.marginTop = '0';
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

    if(onClick){
      wrap.addEventListener('click', (ev)=>{ ev.stopPropagation(); onClick(); });
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

    return d;
  }

  function renderLog(zone, lines){
    const inner = document.createElement('div');
    inner.className = 'zoneInner';
    const box = document.createElement('div');
    box.id = 'logBox';
    const tail = (lines||[]).slice(-28).join('\n');
    box.textContent = tail;
    inner.appendChild(box);
    zone.appendChild(inner);
  }

  function renderStack(zone, cards, wantOrient){
    const ZW = px(zone._zw), ZH = px(zone._zh);
    const w = px(zone._zw), h = px(zone._zh);

    const d = document.createElement('div');
    d.className = 'zoneInner scrollX';
    d.style.paddingTop = '18px';
    d.style.paddingLeft = '6px';
    d.style.paddingRight = '6px';

    const zoneW = px(zone._zw) - 12;
    const zoneH = px(zone._zh) - 24;
    const sz = computeDispSize(wantOrient, zoneW*0.65, zoneH*0.75);

    const overlap = sz.w * 0.22;
    const step = Math.max(6, Math.floor(overlap));

    // horizontal layout with overlap, inside a wider scrollable surface
    const surf = document.createElement('div');
    surf.style.position = 'relative';
    surf.style.height = Math.max(sz.h + 26, zoneH) + 'px';
    surf.style.minWidth = (cards.length ? (sz.w + step*(cards.length-1) + 20) : zoneW) + 'px';

    cards.forEach((cn, i)=>{
      const x = 0 + step*i;
      const y = 10;
      const card = makeCard(cn, wantOrient, x, y, sz.w, sz.h, '', null, false, 100+i);
      surf.appendChild(card);
    });

    d.appendChild(surf);

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(cards.length);
    zone.appendChild(badge);

    zone.appendChild(d);
  }

  function renderFan(zone, cards, wantOrient, clickKind){
    const zoneW = px(zone._zw);
    const zoneH = px(zone._zh);

    const padTop = 20;
    const padX = 8;
    const availW = zoneW - padX*2;
    const availH = zoneH - padTop - 8;

    const sz = computeDispSize(wantOrient, availW, availH);
    const step = Math.max(10, Math.floor(sz.w * (cards.length <= 3 ? 0.34 : 0.24)));

    cards.forEach((cn, i)=>{
      const x = px(zone._zx) + padX + step*i;
      const y = px(zone._zy) + padTop;
      const cap = (clickKind === 'hand') ? labelFor(cn) : '';
      const isSel = (clickKind === 'hand') ? selHand.includes(i) : false;

      const onClick = (clickKind === 'hand') ? (()=>toggleSel(i)) : null;
      const card = makeCard(cn, wantOrient, x, y, sz.w, sz.h, cap, onClick, isSel, 200+i);
      elZones.appendChild(card);
    });

    const badge = document.createElement('div');
    badge.className = 'countBadge';
    badge.textContent = String(cards.length);
    zone._el.appendChild(badge);
  }

  function renderStageSlot(zone, slot){
    const zoneW = px(zone._zw);
    const zoneH = px(zone._zh);
    const padTop = 20;
    const availW = zoneW - 10;
    const availH = zoneH - padTop - 8;
    const sz = computeDispSize('portrait', availW, availH);

    const cn = slot ? String(slot.cardnumber||'') : '';
    if(!cn) return;

    const x = px(zone._zx) + (zoneW - sz.w)/2;
    const y = px(zone._zy) + padTop;
    const cap = labelFor(cn);

    const card = makeCard(cn, 'portrait', x, y, sz.w, sz.h, cap, null, false, 400);
    elZones.appendChild(card);
  }

  function setBanner(text){
    if(text){
      elBanner.textContent = text;
      elBanner.style.display = 'block';
    }else{
      elBanner.style.display = 'none';
    }
  }

  function showPending(p){
    elModalTitle.textContent = 'Pending';
    elModalText.textContent = String(p.text || '');
    elModalActions.innerHTML = '';

    const opts = Array.isArray(p.options) ? p.options : [];
    if(opts.length){
      opts.forEach(opt=>{
        const b = document.createElement('button');
        b.className = 'miniBtn';
        b.textContent = String(opt);
        b.addEventListener('click', async ()=>{
          elMask.style.display = 'none';
          selHand = [];
          st = await apiCmd('resolve_pending', {idx:0, choice:String(opt)});
          updateTop();
          render();
        });
        elModalActions.appendChild(b);
      });
    }
    const close = document.createElement('button');
    close.className = 'miniBtn';
    close.textContent = 'Close';
    close.addEventListener('click', ()=>{ elMask.style.display='none'; });
    elModalActions.appendChild(close);

    elMask.style.display = 'block';
  }

  function updateButtons(){
    const hasSel1 = selHand.length === 1;
    btnPlayL.disabled = !hasSel1;
    btnPlayC.disabled = !hasSel1;
    btnPlayR.disabled = !hasSel1;

    const canSet = (st && st.phase === 'LIVE_SET');
    btnSet.disabled = !(canSet && selHand.length >= 1);

    const sd = (st && st.stage_detail) ? st.stage_detail : {};
    btnActL.disabled = !(sd && sd.L && sd.L.can_activate);
    btnActC.disabled = !(sd && sd.C && sd.C.can_activate);
    btnActR.disabled = !(sd && sd.R && sd.R.can_activate);
  }

  function updateTop(){
    elTurn.textContent = st ? String(st.turn) : '?';
    elPhase.textContent = st ? String(st.phase) : '?';
    elEnergy.textContent = st ? String(st.energy_active) + ' / wait ' + String(st.energy_wait) : '?';
    elSelected.textContent = String(selHand.length);
    if(st){
      elDeckInfo.textContent = `deck=${(st.deck||[]).length} hand=${(st.hand||[]).length} green=${(st.green_room||[]).length} set=${(st.set_zone||[]).length} resolve=${(st.resolve_zone||[]).length}`;
      setBanner(st.banner && st.banner.text ? String(st.banner.text) : '');
    }else{
      elDeckInfo.textContent = '';
      setBanner('');
    }
    updateButtons();
  }

  function render(){
    if(!st) return;

    elZones.innerHTML = '';

    // zones (with cached px values)
    for(const [k,z] of Object.entries(layout.zones)){
      const zd = zoneDiv(z);
      // cache base coords for render helpers
      z._el = zd;
      z._zx = z.x; z._zy = z.y; z._zw = z.w; z._zh = z.h;
      elZones.appendChild(zd);

      if(z.kind === 'log'){
        renderLog(zd, st.log || []);
      }
      if(z.kind === 'stack'){
        const cards = (k === 'deck') ? (st.deck || []).map(()=> '__BACK__') : (k === 'green' ? (st.green_room || []) : []);
        renderStack(zd, cards, 'portrait');
      }
      if(z.kind === 'energy'){
        const inner = document.createElement('div');
        inner.className = 'zoneInner';
        inner.style.paddingTop = '22px';
        inner.style.paddingLeft = '10px';
        inner.style.fontSize = '14px';
        inner.style.lineHeight = '1.4';
        inner.innerHTML = `<div>Active: <b>${st.energy_active}</b></div><div>Wait: <b>${st.energy_wait}</b></div>`;
        zd.appendChild(inner);
      }
    }

    // stage
    const stage = st.stage || {};
    renderStageSlot(layout.zones.stageL, stage.L);
    renderStageSlot(layout.zones.stageC, stage.C);
    renderStageSlot(layout.zones.stageR, stage.R);

    // liveset (landscape desired)
    renderFan(layout.zones.liveset, st.set_zone || [], 'landscape', '');

    // resolve (portrait desired)
    renderFan(layout.zones.resolve, st.resolve_zone || [], 'portrait', '');

    // hand (portrait desired, selectable indices)
    renderFan(layout.zones.hand, st.hand || [], 'portrait', 'hand');

    // pending modal
    if(st.pending && st.pending.length){
      // show only the first pending prompt
      showPending(st.pending[0]);
    }

    updateTop();
  }

  // Wire commands
  btnDbg.addEventListener('click', ()=>{ debug = !debug; render(); });
  btnDebugToggle.addEventListener('click', async ()=>{ st = await apiCmd('toggle_debug', {}); updateTop(); render(); });

  btnUndo.addEventListener('click', async ()=>{ st = await apiCmd('undo', {}); clearSel(); updateTop(); render(); });
  btnNext.addEventListener('click', async ()=>{ st = await apiCmd('next', {indices: selHand.slice()}); clearSel(); updateTop(); render(); });
  btnEnd.addEventListener('click', async ()=>{ st = await apiCmd('end_turn', {}); clearSel(); updateTop(); render(); });
  btnSet.addEventListener('click', async ()=>{ st = await apiCmd('set', {indices: selHand.slice()}); clearSel(); updateTop(); render(); });

  async function doPlay(pos){
    if(selHand.length !== 1) return;
    const idx = selHand[0];
    st = await apiCmd('play', {hand_idx: idx, pos});
    clearSel();
    updateTop();
    render();
  }
  btnPlayL.addEventListener('click', ()=>doPlay('L'));
  btnPlayC.addEventListener('click', ()=>doPlay('C'));
  btnPlayR.addEventListener('click', ()=>doPlay('R'));

  btnActL.addEventListener('click', async ()=>{ st = await apiCmd('activate_to_green', {pos:'L'}); updateTop(); render(); });
  btnActC.addEventListener('click', async ()=>{ st = await apiCmd('activate_to_green', {pos:'C'}); updateTop(); render(); });
  btnActR.addEventListener('click', async ()=>{ st = await apiCmd('activate_to_green', {pos:'R'}); updateTop(); render(); });

  btnYell.addEventListener('click', async ()=>{ st = await apiCmd('yell', {}); updateTop(); render(); });
  btnAttempt.addEventListener('click', async ()=>{ st = await apiCmd('attempt', {}); updateTop(); render(); });
  btnAck.addEventListener('click', async ()=>{ st = await apiCmd('ack', {}); updateTop(); render(); });

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
