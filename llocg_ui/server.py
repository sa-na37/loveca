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

APP_VERSION = "clean-ui-v2_3"


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
  .cardWrap.selected{outline:6px solid rgba(0,0,0,.85); outline-offset:-6px;}
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

/* PATCH_v2_4_CARDLIST_SHRINK */
#modal, #modalActions, #modalCards, #modalText, #modalTitle {
  /* popup を中央寄せ（横幅は中身に追従） */
  text-align: center;
}

/* 「カードリスト」ポップアップ本体：中身サイズに追従しつつ上限を設ける */
#modal, #modalActions, #modalCards, #modalText, #modalTitle .popupBox,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .popupPanel,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .popupInner,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .cardListPopup {
  width: max-content;
  max-width: min(72vw, 1100px);
}

/* カード列：横方向は「必要分だけ」幅を取る（＝余白だらけを防ぐ） */
#modal, #modalActions, #modalCards, #modalText, #modalTitle .cardList,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .cards,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .cardlist,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .list {
  display: inline-flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0;
}

/* カードが多い時は横スクロールで救済 */
#modal, #modalActions, #modalCards, #modalText, #modalTitle .cardListScroll,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .scrollX,
#modal, #modalActions, #modalCards, #modalText, #modalTitle .scroll {
  overflow-x: auto;
  overflow-y: hidden;
  max-width: min(70vw, 1060px);
  padding-bottom: 6px;
}


/* PATCH_v2_5_WAITINGLIST_AND_PENDING_CARDLIST */
/* waiting-room list modal (self-contained) */
.llEnhMask {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.55);
  z-index: 100000;
  display: none;
  align-items: center;
  justify-content: center;
}
.llEnhPanel {
  background: rgba(20,20,20,0.95);
  color: #fff;
  border-radius: 16px;
  padding: 14px 14px 10px 14px;
  width: min(78vw, 1100px);
  max-height: min(72vh, 720px);
  box-shadow: 0 10px 40px rgba(0,0,0,0.6);
}
.llEnhHead {
  display:flex; align-items:center; justify-content:space-between;
  gap: 10px; margin-bottom: 10px;
}
.llEnhTitle { font-size: 18px; font-weight: 700; }
.llEnhClose {
  border: 0; color: #fff; background: rgba(255,255,255,0.12);
  border-radius: 10px; padding: 6px 10px; cursor: pointer;
}
.llEnhSub { font-size: 13px; opacity: 0.85; margin-bottom: 10px; }

.llEnhScroll {
  overflow-x: auto; overflow-y: hidden;
  padding-bottom: 8px;
  max-width: 100%;
}
.llEnhRow {
  display: inline-flex;
  gap: 8px;
  align-items: flex-start;
}
.llEnhCard {
  width: var(--cardW, 156px);
  height: var(--cardH, 218px);
  border-radius: 12px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
  position: relative;
  flex: 0 0 auto;
  box-shadow: 0 6px 16px rgba(0,0,0,0.35);
}
.llEnhCard img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display:block;
}
.llEnhCap {
  position:absolute; left:0; right:0; bottom:0;
  font-size: 11px;
  padding: 4px 6px;
  background: linear-gradient(to top, rgba(0,0,0,0.65), rgba(0,0,0,0.05));
  color:#fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.6);
}

/* pending choice button -> image card style */
.llEnhChoiceBtn {
  width: var(--cardW, 156px);
  height: var(--cardH, 218px);
  padding: 0 !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  position: relative !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.06) !important;
}
.llEnhChoiceBtn img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display:block;
}
.llEnhChoiceBtn .llEnhCap {
  font-size: 11px;
}
.llEnhChoiceWrap {
  display: inline-flex !important;
  gap: 8px !important;
  align-items: flex-start !important;
  overflow-x: auto !important;
  max-width: min(72vw, 1060px) !important;
  padding-bottom: 6px !important;
}


/* PATCH_v2_6_WAITING_PENDING_HANDSEL */
/* 1) 選択(候補)ポップアップ内のカードが大きすぎる→最大サイズを制限 */
.llEnhChoiceBtn {
  width: var(--cardW, 156px);
  height: var(--cardH, 218px);
  max-width: 180px;
  max-height: 252px;
}
.llEnhChoiceBtn img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 2) 手札選択枠が見えない→強制アウトライン（z-indexも上げる） */
.llHandSel {
  outline: 4px solid rgba(255, 120, 190, 0.95);
  outline-offset: -4px;
  border-radius: 12px;
  position: relative;
  z-index: 90000;
}

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
    if(isSelected) wrap.classList.add('selected');

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
      zoneEl.addEventListener('click', (ev)=>{ ev.stopPropagation(); onClick(); });
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

    const card = makeCard(cn, wantOrient, x, y, sz.w, sz.h, '', null, false, 200);
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
    // clicking the zone plays a selected hand card into this slot
    zoneEl.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      if(selHand.length !== 1){
        setBanner('手札を1枚選択して、置きたい枠をクリック');
        return;
      }
      const idx = selHand[0];
      st = await apiCmd('play', {hand_idx: idx, pos: slotKey});
      selHand = [];
      updateTop();
      render();
    });

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

    const card = makeCard(cn, 'portrait', x, y, sz.w, sz.h, labelFor(cn), null, false, 400);

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

  function openCardListPopup(title, cards, {closable=true, helperText='' } = {}){
    popup = {type:'cardlist', title, cards: cards.slice(), closable, helperText};
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
    const minW = (cards.length<=1) ? (maxW + 24) : (maxW + step*(cards.length-1) + 24);
    surf.style.minWidth = minW + 'px';

    cards.forEach((cn, i)=>{
      const orient = intrinsicOrient(cn);
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


  function showPending(p){
    popup = {type:'pending', closable:false};
    elModalTitle.textContent = '選択';
    elModalText.textContent = String(p && p.text ? p.text : '');
    elModalActions.innerHTML = '';
    elModalCards.innerHTML = '';

    const opts = Array.isArray(p && p.options) ? p.options : [];
    if(opts.length){
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
      openCardListPopup('解決領域', rz, {closable:false, helperText:'NEXTで次へ進みます'});
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

<script id="llEnhV25">
(()=> {
  if (window.__llEnhV25) return;
  window.__llEnhV25 = true;

  function qs(sel, root=document){ return root.querySelector(sel); }
  function qsa(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

  function isCardNo(t){
    if(!t) return false;
    const s = t.trim();
    if (s.length < 6) return false;
    // typical: PL!N-bp1-029 / PLN-bp1-029 / ...-PR-018 etc
    return /[!]|bp\d-\d{3}|-PR-\d{3}|-P\d-\d{3}/i.test(s) || (/^[A-Z]{2,}[-!]/.test(s) && /\d/.test(s));
  }

  // ---------- Waiting room list modal ----------
  const mask = document.createElement("div");
  mask.className = "llEnhMask";
  mask.innerHTML = `
    <div class="llEnhPanel" role="dialog" aria-modal="true">
      <div class="llEnhHead">
        <div class="llEnhTitle">控え室</div>
        <button class="llEnhClose" type="button">Close</button>
      </div>
      <div class="llEnhSub">クリックで確認できます（選択は行いません）</div>
      <div class="llEnhScroll"><div class="llEnhRow"></div></div>
    </div>
  `;
  document.addEventListener("DOMContentLoaded", ()=> document.body.appendChild(mask));
  mask.addEventListener("click", (e)=>{
    if (e.target === mask) hideWaiting();
  });
  qs(".llEnhClose", mask).addEventListener("click", hideWaiting);

  function showWaiting(cards){
    const row = qs(".llEnhRow", mask);
    row.innerHTML = "";
    for (const cn of cards){
      const d = document.createElement("div");
      d.className = "llEnhCard";
      const img = document.createElement("img");
      img.loading = "lazy";
      img.src = "/img?cn=" + encodeURIComponent(cn);
      const cap = document.createElement("div");
      cap.className = "llEnhCap";
      cap.textContent = cn;
      d.appendChild(img);
      d.appendChild(cap);
      row.appendChild(d);
    }
    mask.style.display = "flex";
  }
  function hideWaiting(){ mask.style.display = "none"; }

  async function fetchState(){
    const r = await fetch("/state", {cache:"no-store"});
    return await r.json();
  }
  function extractWaitingList(st){
    // try common keys first
    const candKeys = Object.keys(st).filter(k => /wait/i.test(k));
    const keys = ["waiting", "waiting_room", "waitingRoom", "wait", "grave", ...candKeys];
    for (const k of keys){
      const v = st[k];
      if (!v) continue;
      if (Array.isArray(v) && v.length){
        // strings
        if (typeof v[0] === "string") return v;
        // objects
        const out = [];
        for (const it of v){
          if (typeof it === "string") { out.append(it); continue; }
          if (it && typeof it === "object"){
            const cn = it.cn || it.card_no || it.cardnumber || it.cardNumber || it.db_id || it.id;
            if (cn) out.push(String(cn));
          }
        }
        if (out.length) return out;
      }
    }
    return [];
  }

  function clickedWaitingRoom(e){
    const t = e.target;
    if (!t) return false;
    // explicit selectors if present
    const hit = t.closest('[data-zone="waiting"],[data-zone="waiting_room"],[data-zone="waitingRoom"],#zone_waiting,#zone_waiting_room,.zone-waiting,.waitingRoom,.waiting-room,#waitingRoom');
    if (hit) return true;
    // fallback: within sidebar label
    let n = t;
    for (let i=0; i<6 && n; i++, n=n.parentElement){
      if (!n || !n.textContent) continue;
      const txt = n.textContent;
      if (txt.includes("Waiting room") || txt.includes("控え室")) return true;
    }
    return false;
  }

  document.addEventListener("click", async (e)=>{
    if (!clickedWaitingRoom(e)) return;
    try{
      const st = await fetchState();
      const cards = extractWaitingList(st);
      if (cards.length) showWaiting(cards);
    } catch(_){}
  }, true);

  // ---------- Pending choice: transform card-no buttons into image list ----------
  function upgradePendingButtons(root=document.body){
    // find groups of buttons that look like card numbers
    const btns = qsa("button", root);
    const targets = btns.filter(b => {
      if (b.classList.contains("llEnhChoiceBtn")) return false;
      const txt = (b.textContent || "").trim();
      if (!isCardNo(txt)) return false;
      // ignore UNDO/NEXT etc
      if (/UNDO|NEXT|PLAY|Close/i.test(txt)) return false;
      return true;
    });

    // group by closest modal/popup container
    const groups = new Map();
    for (const b of targets){
      const box = b.closest(".popupBox,.popupPanel,.popupInner,.modal,.dialog,.llEnhPanel") || b.parentElement;
      if (!box) continue;
      const key = box;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(b);
    }

    for (const [box, bs] of groups.entries()){
      if (bs.length < 2) continue; // likely not a choice list
      // wrap their parent into scrollable row
      const parent = bs[0].parentElement;
      if (parent && !parent.classList.contains("llEnhChoiceWrap")){
        parent.classList.add("llEnhChoiceWrap");
      }
      for (const b of bs){
        const cn = (b.textContent || "").trim();
        // preserve click handler; just replace content
        b.classList.add("llEnhChoiceBtn");
        b.textContent = "";
        const img = document.createElement("img");
        img.loading = "lazy";
        img.src = "/img?cn=" + encodeURIComponent(cn);
        const cap = document.createElement("div");
        cap.className = "llEnhCap";
        cap.textContent = cn;
        b.appendChild(img);
        b.appendChild(cap);
      }
    }
  }

  const mo = new MutationObserver(()=>upgradePendingButtons());
  mo.observe(document.documentElement, {subtree:true, childList:true});
  setTimeout(()=>upgradePendingButtons(), 500);

})();
</script>


<script id="llEnhV26">
(()=> {
  if (window.__llEnhV26) return;
  window.__llEnhV26 = true;

  const qs = (sel, root=document) => root.querySelector(sel);
  const qsa = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  function isCardNo(t){
    if(!t) return false;
    const s = String(t).trim();
    if (s.length < 6) return false;
    return /[!]|bp\d-\d{3}|-PR-\d{3}|-P\d-\d{3}/i.test(s) || (/^[A-Z]{2,}[-!]/.test(s) && /\d/.test(s));
  }

  // ---------- waiting room: robust extractor ----------
  function extractCardNosFromArray(arr){
    const out = [];
    for (const it of arr){
      if (typeof it === "string"){
        const cn = it.trim();
        if (cn) out.push(cn);
        continue;
      }
      if (it && typeof it === "object"){
        const cn = it.cn || it.card_no || it.cardnumber || it.cardNumber || it.db_id || it.id || it.card;
        if (cn) out.push(String(cn));
      }
    }
    return out.filter(Boolean);
  }

  function findWaitingCardsDeep(obj){
    let best = [];
    const seen = new Set();

    function visit(node, kHint=""){
      if (!node) return;
      if (seen.has(node)) return;
      if (typeof node === "object") seen.add(node);

      // key-hinted candidates
      if (Array.isArray(node)){
        return;
      }
      if (typeof node !== "object") return;

      for (const [k,v] of Object.entries(node)){
        const kk = String(k).toLowerCase();
        const isWaitKey = /wait|waiting|grave|discard|trash|yard|控え|墓地|捨て/i.test(kk) || /wait|waiting|grave|discard|trash|yard|控え|墓地|捨て/i.test(kHint);
        if (v && typeof v === "object"){
          // direct array
          if (isWaitKey && Array.isArray(v)){
            const c = extractCardNosFromArray(v);
            if (c.length > best.length) best = c;
          }
          // dict with cards/list
          if (isWaitKey && !Array.isArray(v)){
            for (const kk2 of ["cards","list","pile","stack","items"]){
              if (Array.isArray(v[kk2])){
                const c = extractCardNosFromArray(v[kk2]);
                if (c.length > best.length) best = c;
              }
            }
          }
        }
        // recurse
        if (v && typeof v === "object") visit(v, kk);
      }
    }
    visit(obj, "");
    return best;
  }

  async function fetchState(){
    const r = await fetch("/state", {cache:"no-store"});
    return await r.json();
  }

  // ---------- waiting room modal (reuse existing mask if v25 exists) ----------
  function ensureWaitingModal(){
    let mask = document.querySelector(".llEnhMask");
    if (mask) return mask;

    mask = document.createElement("div");
    mask.className = "llEnhMask";
    mask.innerHTML = `
      <div class="llEnhPanel" role="dialog" aria-modal="true">
        <div class="llEnhHead">
          <div class="llEnhTitle">控え室</div>
          <button class="llEnhClose" type="button">Close</button>
        </div>
        <div class="llEnhSub">クリックで確認できます（選択は行いません）</div>
        <div class="llEnhScroll"><div class="llEnhRow"></div></div>
      </div>
    `;
    document.body.appendChild(mask);
    mask.addEventListener("click", (e)=>{ if (e.target===mask) mask.style.display="none"; });
    qs(".llEnhClose", mask).addEventListener("click", ()=> mask.style.display="none");
    return mask;
  }

  function showWaiting(cards){
    const mask = ensureWaitingModal();
    const row = qs(".llEnhRow", mask);
    row.innerHTML = "";
    for (const cn of cards){
      const d = document.createElement("div");
      d.className = "llEnhCard";
      const img = document.createElement("img");
      img.loading = "lazy";
      img.src = "/img?cn=" + encodeURIComponent(cn);
      const cap = document.createElement("div");
      cap.className = "llEnhCap";
      cap.textContent = cn;
      d.appendChild(img);
      d.appendChild(cap);
      row.appendChild(d);
    }
    mask.style.display = "flex";
  }

  async function openWaiting(){
    try{
      const st = await fetchState();
      const cards = findWaitingCardsDeep(st);
      if (cards && cards.length) showWaiting(cards);
    }catch(e){}
  }

  // 「Waiting room」ラベル周辺をホットスポット化（クリック検出を確実に）
  function wireWaitingHotspots(){
    const nodes = qsa("*").filter(el=>{
      if (!el || el.dataset && el.dataset.llWaitingHot==="1") return false;
      const t = (el.textContent||"").trim();
      if (!t) return false;
      if (t === "Waiting room" || t === "控え室" || t.includes("Waiting room") || t.includes("控え室")) return true;
      return false;
    });
    for (const el of nodes){
      const box = el.closest("div") || el.parentElement;
      if (!box) continue;
      box.dataset.llWaitingHot = "1";
      box.style.cursor = "pointer";
      box.addEventListener("click", (e)=>{ e.stopPropagation(); openWaiting(); }, true);
    }
  }

  // ---------- hand selection outline ----------
  function isInHandZone(el){
    if (!el) return false;
    const hit = el.closest('[data-zone="hand"],#zone_hand,.zone-hand,.handZone,#handZone,.hand');
    if (hit) return true;
    // fallback: near "HAND" label
    let n = el;
    for (let i=0; i<6 && n; i++, n=n.parentElement){
      const t = (n.textContent||"");
      if (t.includes("HAND")) return true;
    }
    return false;
  }

  function findCardContainer(el){
    if (!el) return null;
    const cand = el.closest("button,div");
    if (!cand) return null;
    const img = cand.querySelector('img[src*="/img?cn="]');
    if (!img) return null;
    return cand;
  }

  document.addEventListener("click", (e)=>{
    const t = e.target;
    if (!isInHandZone(t)) return;
    const card = findCardContainer(t);
    if (!card) return;
    // clear
    qsa(".llHandSel").forEach(x=>x.classList.remove("llHandSel"));
    card.classList.add("llHandSel");
  }, true);

  // init + observe
  const mo = new MutationObserver(()=>wireWaitingHotspots());
  mo.observe(document.documentElement, {subtree:true, childList:true});
  document.addEventListener("DOMContentLoaded", ()=> setTimeout(wireWaitingHotspots, 50));
  setTimeout(wireWaitingHotspots, 500);

})();
</script>

</body>
</html>'''