# -*- coding: utf-8 -*-
# BUILD_TAG: llocg_dual_controls_phase_banner_20260716d
from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from llocg_ui.server import App, HTML as SINGLE_HTML
from llocg_ui.views import make_view_state

BUILD_TAG = "llocg_dual_controls_phase_banner_20260716d"


@dataclass
class PlayerRuntime:
    player_id: str
    label: str
    color: str
    app: App


class MatchState:
    """Two-player coordinator layered over the existing single-player engine.

    The single-player engine remains untouched.  This class supplies shared
    opponent facts, active-player ownership, and the official coarse order:
    P1 normal -> P2 normal -> both set -> P1 performance -> P2 performance.
    """

    def __init__(self, p1: PlayerRuntime, p2: PlayerRuntime):
        self.players: Dict[str, PlayerRuntime] = {"p1": p1, "p2": p2}
        self.active_player_id = "p1"
        self.first_player_id = "p1"
        self.match_turn = 0
        self.match_phase = "MULLIGAN"
        self.mulligan_done = {"p1": False, "p2": False}
        self.performance_done = {"p1": False, "p2": False}
        self.lock = threading.RLock()
        self.match_log = [f"[MATCH] initialized {p1.label}={p1.app.deck_code} / {p2.label}={p2.app.deck_code}"]
        self.sync_all_opponent_facts()

    def player(self, player_id: str) -> PlayerRuntime:
        key = str(player_id or "").lower()
        if key not in self.players:
            raise KeyError(key)
        return self.players[key]

    def opponent_id(self, player_id: str) -> str:
        return "p2" if player_id == "p1" else "p1"

    @staticmethod
    def _stage_wait_count(app: App) -> int:
        n = 0
        for slot in (getattr(app.gs, "stage", {}) or {}).values():
            if slot and bool(getattr(slot, "wait", False)):
                n += 1
        return n

    @staticmethod
    def _success_score_sum(app: App) -> int:
        total = 0
        db = getattr(app, "cards_db", {}) or {}
        for cn in list(getattr(app.gs, "success_zone", []) or []):
            ci = db.get(cn)
            try:
                total += int(getattr(ci, "score", 0) or 0)
            except Exception:
                pass
        return total

    def sync_opponent_facts(self, player_id: str) -> None:
        own = self.player(player_id).app
        opp = self.player(self.opponent_id(player_id)).app
        gs = own.gs
        setattr(gs, "opponent_wait_count", self._stage_wait_count(opp))
        setattr(gs, "opponent_success_count", len(list(getattr(opp.gs, "success_zone", []) or [])))
        setattr(gs, "opponent_success_score_sum", self._success_score_sum(opp))
        setattr(gs, "opponent_excess_heart_count", int(getattr(opp.gs, "excess_heart_count", 0) or 0))
        # Runtime extensions can use this direct peer reference for later
        # cross-board target selection without changing the legacy core API.
        setattr(gs, "_dual_opponent_gs", opp.gs)
        setattr(gs, "_dual_player_id", player_id)

    def sync_all_opponent_facts(self) -> None:
        self.sync_opponent_facts("p1")
        self.sync_opponent_facts("p2")

    def switch_active(self, requested: str = "") -> str:
        with self.lock:
            if requested in self.players:
                self.active_player_id = requested
            else:
                self.active_player_id = "p2" if self.active_player_id == "p1" else "p1"
            self.match_log.append(f"[MATCH] active_player={self.active_player_id}")
            return self.active_player_id

    def _after_both_mulligans(self) -> None:
        self.match_turn = 1
        self.match_phase = "P1_NORMAL"
        self.active_player_id = self.first_player_id
        # The legacy app starts both players in MAIN after mulligan.  We retain
        # that initialized state but expose only the official first normal phase.
        self.match_log.append("[RULE 7.1-7.3] turn 1: first normal phase")

    def _set_live_set(self, player_id: str) -> None:
        app = self.player(player_id).app
        app.gs.phase = "LIVE_SET"
        app.gs.live_set_limit = max(0, 3 + int(getattr(app.gs, "next_live_set_limit_delta", 0) or 0))
        app.gs.next_live_set_limit_delta = 0
        app.gs.live_start_prompted = False
        app.gs.turn_blade_bonus = 0
        app.gs.log.append(f"[DUAL PHASE] LIVE_SET turn={self.match_turn}")

    def _coordinate_before(self, player_id: str, cmd: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Return (consume_without_app_cmd, response)."""
        if cmd == "mulligan_next":
            return False, None
        if player_id != self.active_player_id and cmd not in {"undo", "ack_refresh_notice"}:
            return True, self.player(player_id).app.state_json()
        if cmd != "next":
            return False, None

        phase = str(getattr(self.player(player_id).app.gs, "phase", "") or "").upper()
        if self.match_phase == "P1_NORMAL" and player_id == "p1" and phase == "MAIN":
            self.match_phase = "P2_NORMAL"
            self.active_player_id = "p2"
            self.match_log.append("[RULE 7.3] first normal complete -> second normal")
            return True, self.player(player_id).app.state_json()
        if self.match_phase == "P2_NORMAL" and player_id == "p2" and phase == "MAIN":
            self.match_phase = "LIVE_SET_P1"
            self._set_live_set("p1")
            self._set_live_set("p2")
            self.active_player_id = "p1"
            self.match_log.append("[RULE 8.2] live card set: first player")
            return True, self.player(player_id).app.state_json()
        return False, None

    def _coordinate_after(self, player_id: str, cmd: str, before_phase: str, before_turn: int) -> None:
        app = self.player(player_id).app
        phase = str(getattr(app.gs, "phase", "") or "").upper()
        if cmd == "mulligan_next":
            self.mulligan_done[player_id] = True
            self.active_player_id = "p2" if player_id == "p1" and not self.mulligan_done["p2"] else player_id
            self.match_log.append(f"[MULLIGAN] {player_id} complete")
            if all(self.mulligan_done.values()):
                self._after_both_mulligans()
            return
        if cmd != "next":
            return
        if self.match_phase == "LIVE_SET_P1" and player_id == "p1" and before_phase == "LIVE_SET" and phase == "LIVE_CONFIRM":
            self.match_phase = "LIVE_SET_P2"
            self.active_player_id = "p2"
            self.match_log.append("[RULE 8.2] first set complete -> second set")
            return
        if self.match_phase == "LIVE_SET_P2" and player_id == "p2" and before_phase == "LIVE_SET" and phase == "LIVE_CONFIRM":
            self.match_phase = "PERFORMANCE_P1"
            self.active_player_id = "p1"
            self.match_log.append("[RULE 8.3] set complete -> first performance")
            return
        # Legacy engine advances to next MAIN after its own LIVE_RESOLVE cleanup.
        # Use that transition only as a completion signal and keep the other side
        # inactive until its performance is finished.
        if before_phase == "LIVE_RESOLVE" and phase == "MAIN" and int(getattr(app.gs, "turn", 0) or 0) > before_turn:
            self.performance_done[player_id] = True
            if player_id == "p1" and self.match_phase == "PERFORMANCE_P1":
                self.match_phase = "PERFORMANCE_P2"
                self.active_player_id = "p2"
                self.match_log.append("[RULE 8.3] first performance complete -> second performance")
            elif player_id == "p2" and self.match_phase == "PERFORMANCE_P2":
                self.match_turn += 1
                self.performance_done = {"p1": False, "p2": False}
                self.match_phase = "P1_NORMAL"
                self.active_player_id = self.first_player_id
                self.match_log.append(f"[RULE 8.4] live phase complete -> turn {self.match_turn}")

    def dispatch(self, player_id: str, cmd: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            self.sync_all_opponent_facts()
            consumed, response = self._coordinate_before(player_id, cmd)
            if consumed:
                self.sync_all_opponent_facts()
                return response or self.player(player_id).app.state_json()
            runtime = self.player(player_id)
            before_phase = str(getattr(runtime.app.gs, "phase", "") or "").upper()
            before_turn = int(getattr(runtime.app.gs, "turn", 0) or 0)
            out = runtime.app.cmd(cmd, payload)
            self._coordinate_after(player_id, cmd, before_phase, before_turn)
            self.sync_all_opponent_facts()
            self.match_log.append(f"[{player_id}] cmd={cmd} phase={before_phase}->{getattr(runtime.app.gs, 'phase', '')}")
            return out

    def shell_state(self) -> Dict[str, Any]:
        with self.lock:
            self.sync_all_opponent_facts()
            return {
                "build_tag": BUILD_TAG,
                "active_player_id": self.active_player_id,
                "first_player_id": self.first_player_id,
                "match_turn": self.match_turn,
                "match_phase": self.match_phase,
                "match_log": list(self.match_log[-100:]),
                "players": {
                    key: {
                        "player_id": key,
                        "label": runtime.label,
                        "color": runtime.color,
                        "deck_code": runtime.app.deck_code,
                        "phase": str(getattr(runtime.app.gs, "phase", "")),
                        "turn": int(getattr(runtime.app.gs, "turn", 0) or 0),
                        "pending_count": len(list(getattr(runtime.app.gs, "pending", []) or [])),
                    }
                    for key, runtime in self.players.items()
                },
            }


def _scoped_single_html(prefix: str, *, upper: bool, label: str, color: str) -> str:
    html = SINGLE_HTML
    html = html.replace('src="/playmat"', f'src="/{prefix}/playmat"')
    html = html.replace("`/img?cn=", f"`/{prefix}/img?cn=")
    html = html.replace("`/cardinfo?cn=", f"`/{prefix}/cardinfo?cn=")
    html = html.replace("const url = IS_PUBLIC_VIEW ? '/state?view=public' : '/state';",
                        f"const url = IS_PUBLIC_VIEW ? '/{prefix}/state?view=public' : '/{prefix}/state';")
    html = html.replace("fetch('/cmd',", f"fetch('/{prefix}/cmd',")
    html = html.replace('<title>LLCG Manual UI</title>', f'<title>{label} | LLCG Dual</title>')
    html = html.replace('<body>', f'<body class="dualPlayerView {"dualUpper" if upper else "dualLower"}">')
    injected = f'''
<style>
  body.dualPlayerView::before{{content:{json.dumps(label, ensure_ascii=False)};position:fixed;left:12px;top:10px;z-index:50000;padding:7px 13px;border-radius:999px;background:{color};color:#fff;font-size:15px;font-weight:900;box-shadow:0 3px 14px rgba(0,0,0,.55)}}
  /* Mirror only zone placement.  Counter-rotating every zone keeps cards,
     hover transforms, labels, log text, and controls screen-upright. */
  body.dualUpper #zones{{transform:rotate(180deg);transform-origin:50% 50%;}}
  body.dualUpper #zones>.zone{{transform:rotate(180deg);transform-origin:50% 50%;}}
  /* Shared shell owns NEXT/UNDO. Keep the native buttons available for
     programmatic clicks so selected hand indices remain inside legacy UI. */
  body.dualPlayerView .energyUI button{{position:absolute!important;width:1px!important;height:1px!important;opacity:0!important;pointer-events:none!important;overflow:hidden!important;}}
  /* Manual opponent counters and turn-order toggles are invalid in dual mode. */
  body.dualPlayerView #topBar .oppWaitPill{{display:none!important;}}
  body.dualPlayerView #topBar{{padding-left:130px;}}
  html,body{{overflow:hidden;}}
</style>
'''
    html = html.replace('</head>', injected + '</head>')
    return html


def _dual_shell_html() -> str:
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>LLCG 2デッキ対戦</title><style>
html,body{{height:100%;margin:0;background:#080a0e;color:#fff;font-family:system-ui,-apple-system,sans-serif;overflow:hidden}}
#shell{{height:100%;display:grid;grid-template-rows:1fr 74px 1fr}}
.playerFrame{{width:100%;height:100%;border:0;background:#111}}
#divider{{position:relative;display:flex;align-items:center;justify-content:center;background:#151922;border-top:2px solid #343b4c;border-bottom:2px solid #343b4c;z-index:10;box-shadow:0 0 18px rgba(0,0,0,.6)}}
#phaseBanner{{font-weight:950;font-size:25px;letter-spacing:.04em;text-align:center;white-space:nowrap;text-shadow:0 2px 8px rgba(0,0,0,.75)}}
#phaseSub{{display:block;font-size:13px;font-weight:750;letter-spacing:0;margin-top:3px;opacity:.82}}
button{{border:1px solid rgba(255,255,255,.25);border-radius:9px;background:#2a3140;color:#fff;padding:9px 18px;font-weight:900;cursor:pointer;font-size:15px}}
button:hover{{background:#384258}}.p1{{color:#72b7ff}}.p2{{color:#ffad69}}
#tag{{position:fixed;right:8px;top:4px;z-index:20;font-size:10px;color:#9aa4b5}}
#globalControls{{position:absolute;right:14px;top:50%;transform:translateY(-50%);z-index:100;display:flex;gap:9px}}
#globalNext{{background:#276fca;min-width:108px}}#globalUndo{{background:#555}}
</style></head><body><div id="tag">{BUILD_TAG}</div><div id="shell"><iframe id="p2frame" class="playerFrame" src="/p2/ui?upper=1"></iframe><div id="divider"><div id="phaseBanner"></div><div id="globalControls"><button id="globalUndo">UNDO</button><button id="globalNext">NEXT</button></div></div><iframe id="p1frame" class="playerFrame" src="/p1/ui"></iframe></div>
<script>
let currentActive='p1';
let currentPhase='MULLIGAN';
async function dispatchAction(action){{
  const cmd=action==='UNDO'?'undo':(String(currentPhase).toUpperCase()==='MULLIGAN'?'mulligan_next':'next');
  const r=await fetch('/'+currentActive+'/cmd',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{cmd:cmd,payload:{{}}}})}});
  if(!r.ok) throw new Error('command failed: '+r.status);
  await refreshMatch();
}}
async function refreshMatch(){{
  const r=await fetch('/match_state',{{cache:'no-store'}});const s=await r.json();
  currentActive=s.active_player_id;currentPhase=s.match_phase;
  const p=s.players[currentActive];
  const phase=document.getElementById('phaseBanner');
  phase.className=currentActive;
  phase.innerHTML='Turn '+s.match_turn+'　'+s.match_phase+'<span id="phaseSub">操作：'+p.label+'（'+p.deck_code+'）</span>';
  document.getElementById('globalNext').textContent=String(s.match_phase).toUpperCase()==='MULLIGAN'?'マリガン決定':'NEXT';
}}
document.getElementById('globalNext').onclick=()=>dispatchAction('NEXT').catch(console.error);
document.getElementById('globalUndo').onclick=()=>dispatchAction('UNDO').catch(console.error);
refreshMatch();setInterval(refreshMatch,400);
</script></body></html>'''


class DualHandler(BaseHTTPRequestHandler):
    match: MatchState
    def log_message(self, fmt: str, *args: Any) -> None: print("[DUAL HTTP] " + (fmt % args))
    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers()
        if self.command != "HEAD": self.wfile.write(body)
    def _player_path(self, path: str):
        parts=path.lstrip('/').split('/',1)
        if parts and parts[0] in self.match.players: return self.match.player(parts[0]), '/'+(parts[1] if len(parts)>1 else '')
        return None,path
    def do_HEAD(self): self.do_GET()
    def do_GET(self):
        u=urlparse(self.path)
        if u.path in {'/','/dual'}: return self._send(200,_dual_shell_html().encode(),'text/html; charset=utf-8')
        if u.path=='/match_state': return self._send(200,json.dumps(self.match.shell_state(),ensure_ascii=False).encode(),'application/json; charset=utf-8')
        runtime,subpath=self._player_path(u.path)
        if runtime is None: return self._send(404,b'not found','text/plain')
        prefix=runtime.player_id
        if subpath in {'/ui','/'}:
            upper=parse_qs(u.query).get('upper',['0'])[0]=='1'; body=_scoped_single_html(prefix,upper=upper,label=runtime.label,color=runtime.color); return self._send(200,body.encode(),'text/html; charset=utf-8')
        if subpath=='/state':
            mode=parse_qs(u.query).get('view',['private'])[0]; self.match.sync_all_opponent_facts(); state=runtime.app.state_json(); state.update({'dual_player_id':prefix,'dual_player_label':runtime.label,'dual_active_player_id':self.match.active_player_id,'dual_match_phase':self.match.match_phase}); return self._send(200,json.dumps(make_view_state(state,mode),ensure_ascii=False).encode(),'application/json; charset=utf-8')
        if subpath=='/playmat':
            for p in [runtime.app.root/'playmat.jpg',Path.cwd()/'playmat.jpg']:
                if p.exists(): return self._send(200,p.read_bytes(),'image/jpeg')
            return self._send(404,b'','text/plain')
        if subpath=='/cardinfo':
            from llocg_ui.db import _get_card as db_get_card
            cn=parse_qs(u.query).get('cn',[''])[0]; ci=db_get_card(runtime.app.cards_db,cn) if cn else None
            if not ci:return self._send(404,b'{}','application/json')
            payload={'cn':cn,'name':str(getattr(ci,'name','') or ''),'type':str(getattr(ci,'type','') or ''),'group':str(getattr(ci,'group','') or ''),'cost':str(getattr(ci,'cost','') or ''),'blade':str(getattr(ci,'blade','') or ''),'effect':str(getattr(ci,'effect_text_raw','') or getattr(ci,'effect_text_norm','') or '')}
            return self._send(200,json.dumps(payload,ensure_ascii=False).encode(),'application/json; charset=utf-8')
        if subpath=='/img':
            cn=parse_qs(u.query).get('cn',[''])[0]
            if cn=='__BACK__':
                for p in [Path.cwd()/'card_back.jpg',runtime.app.root/'card_back.jpg']:
                    if p.exists(): return self._send(200,p.read_bytes(),'image/jpeg')
            if cn=='__ENERGY__':
                for p in [Path.cwd()/'energy.jpg',runtime.app.root/'energy.jpg']:
                    if p.exists(): return self._send(200,p.read_bytes(),'image/jpeg')
            p=runtime.app.img.find(cn)
            if p and p.exists():
                ct='image/jpeg' if p.suffix.lower() in {'.jpg','.jpeg'} else 'image/webp' if p.suffix.lower()=='.webp' else 'image/png'; return self._send(200,p.read_bytes(),ct)
            return self._send(404,b'','text/plain')
        return self._send(404,b'not found','text/plain')
    def do_POST(self):
        u=urlparse(self.path); n=int(self.headers.get('Content-Length','0') or 0); raw=self.rfile.read(n) if n else b'{}'
        try: obj=json.loads(raw.decode())
        except Exception: obj={}
        if u.path=='/match_cmd':
            if str(obj.get('cmd',''))=='switch_active_player':
                active=self.match.switch_active(str((obj.get('payload') or {}).get('player_id',''))); return self._send(200,json.dumps({'ok':True,'active_player_id':active}).encode(),'application/json')
            return self._send(400,b'{"ok":false}','application/json')
        runtime,subpath=self._player_path(u.path)
        if runtime is None or subpath!='/cmd': return self._send(404,b'not found','text/plain')
        cmd=str(obj.get('cmd','')).strip(); payload=obj.get('payload') or {}; out=self.match.dispatch(runtime.player_id,cmd,payload if isinstance(payload,dict) else {})
        return self._send(200,json.dumps(out,ensure_ascii=False).encode(),'application/json; charset=utf-8')


def serve_dual(*,host:str,port:int,root:Path,deck1:str,deck2:str,seed:int,debug:bool,compiled:Optional[Path]=None,tokv1:Optional[Path]=None)->None:
    p1_app=App(root=root,code='dual-p1',deck_code=deck1,seed=seed,debug=debug,compiled=compiled,tokv1=tokv1); p2_app=App(root=root,code='dual-p2',deck_code=deck2,seed=seed+1,debug=debug,compiled=compiled,tokv1=tokv1)
    match=MatchState(PlayerRuntime('p1','プレイヤー1','#2578d4',p1_app),PlayerRuntime('p2','プレイヤー2','#d96a22',p2_app)); DualHandler.match=match; httpd=ThreadingHTTPServer((host,int(port)),DualHandler); print(f"[LLCG DUAL] BUILD_TAG={BUILD_TAG}"); print(f"[LLCG DUAL] http://{host}:{port} p1={deck1} p2={deck2}"); httpd.serve_forever()
