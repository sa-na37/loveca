from __future__ import annotations
import json
import mimetypes
import pathlib
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional

from .db import load_compiled_db, load_tokv1, load_decklist
from .images import ImageLocator
from .engine import Card, Engine, make_initial

BASE_PLAYMAT_W = 1560
BASE_PLAYMAT_H = 851

def _guess_type(compiled_row: Dict[str, Any], tok_row: Dict[str, Any]) -> str:
    for src in (compiled_row, tok_row):
        for k in ("card_type_norm","type_norm","card_type","type"):
            v = src.get(k)
            if isinstance(v, str) and v.strip():
                s = v.strip().upper()
                if "MEM" in s or "MEMBER" in s or "メンバー" in s:
                    return "MEMBER"
                if "LIVE" in s or "ライブ" in s:
                    return "LIVE"
    return ""

def _guess_text(compiled_row: Dict[str, Any], tok_row: Dict[str, Any]) -> str:
    for src in (tok_row, compiled_row):
        for k in ("effect_text_raw","effect_text_norm","text","cardtext","effect_text","raw_text"):
            v = src.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    ab = compiled_row.get("abilities")
    if isinstance(ab, list):
        for a in ab:
            if isinstance(a, dict):
                raw = a.get("raw") or a.get("text") or a.get("effect_raw")
                if isinstance(raw, str) and raw.strip():
                    return raw.strip()
    return ""

def _guess_name(compiled_row: Dict[str, Any], tok_row: Dict[str, Any]) -> str:
    for src in (tok_row, compiled_row):
        for k in ("cardname","name","jp_name","title"):
            v = src.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""

def _img_orient(p: Optional[pathlib.Path]) -> str:
    if not p or not p.exists():
        return ""
    try:
        from PIL import Image  # type: ignore
        with Image.open(p) as im:
            w, h = im.size
        return "portrait" if h >= w else "landscape"
    except Exception:
        suf = p.suffix.lower()
        try:
            b = p.read_bytes()
        except Exception:
            return ""
        if suf == ".png":
            if len(b) >= 24 and b[:8] == b"\x89PNG\r\n\x1a\n":
                w = int.from_bytes(b[16:20], "big")
                h = int.from_bytes(b[20:24], "big")
                return "portrait" if h >= w else "landscape"
        if suf in (".jpg",".jpeg"):
            i = 2
            while i + 9 < len(b):
                if b[i] != 0xFF:
                    i += 1
                    continue
                marker = b[i+1]
                if marker in (0xC0,0xC2):
                    h = int.from_bytes(b[i+5:i+7], "big")
                    w = int.from_bytes(b[i+7:i+9], "big")
                    return "portrait" if h >= w else "landscape"
                if i+4 <= len(b):
                    seglen = int.from_bytes(b[i+2:i+4], "big")
                    i += 2 + seglen
                else:
                    break
    return ""

def serve(root: pathlib.Path, host: str, port: int, deck_code: str, open_browser: bool = True) -> None:
    root = root.resolve()
    card_images_dir = root / "llocg_db_out_full" / "card_images"
    locator = ImageLocator(card_images_dir)

    compiled = load_compiled_db(root)
    tokv1 = load_tokv1(root)
    deck_rows, deck_err, deck_fname = load_decklist(root, deck_code)

    cards: Dict[str, Card] = {}
    deck_cids = []
    seq = 1
    for r in deck_rows:
        cn = r.get("card_no","")
        rr = (r.get("rarity","") or "").strip()
        comp = compiled.get(cn, {})
        tok = tokv1.get(cn, {})
        img_path = locator.resolve(cn, rr)
        cid = f"c{seq:05d}"
        cards[cid] = Card(
            cid=cid,
            card_no=cn,
            rarity=rr,
            name=_guess_name(comp, tok),
            card_type=_guess_type(comp, tok),
            img_orient=_img_orient(img_path),
            text=_guess_text(comp, tok),
        )
        deck_cids.append(cid)
        seq += 1

    engine = Engine(cards=cards, initial=make_initial(deck_cids, auto_draw=7))

    back_path = locator.resolve("back") or (card_images_dir / "back.jpeg")
    energy_path = (card_images_dir / "energy.jpg")

    def _image_for_cid(cid: str) -> Optional[pathlib.Path]:
        c = engine.cards.get(cid)
        if not c:
            return None
        return locator.resolve(c.card_no, c.rarity)

    def _view_state() -> Dict[str, Any]:
        def image_url(cid: str) -> str:
            return f"/asset/card/{cid}"
        return engine.to_view(image_url)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, data: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if data:
                self.wfile.write(data)

        def _json(self, obj: Any, code: int = 200) -> None:
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self._send(code, data, "application/json; charset=utf-8")

        def log_message(self, fmt: str, *args) -> None:
            sys.stdout.write("[UI] " + (fmt % args) + "\n")

        def _send_file(self, p: pathlib.Path) -> None:
            ctype, _ = mimetypes.guess_type(str(p))
            ctype = ctype or "application/octet-stream"
            data = p.read_bytes()
            self._send(200, data, ctype)

        def do_GET(self) -> None:
            path = urllib.parse.urlparse(self.path).path

            if path == "/":
                self._send(200, INDEX_HTML.encode("utf-8"), "text/html; charset=utf-8")
                return

            if path == "/favicon.ico":
                self._send(204, b"", "image/x-icon")
                return

            if path == "/api/state":
                self._json({"ok": True, "state": _view_state(), "deck_error": deck_err, "deck_file": deck_fname})
                return

            if path == "/asset/playmat":
                p = root / "playmat.jpg"
                if p.exists():
                    self._send_file(p)
                else:
                    self._send(404, b"playmat.jpg not found", "text/plain; charset=utf-8")
                return

            if path == "/asset/back":
                if back_path and pathlib.Path(back_path).exists():
                    self._send_file(pathlib.Path(back_path))
                else:
                    self._send(404, b"back not found", "text/plain; charset=utf-8")
                return

            if path == "/asset/energy":
                if energy_path.exists():
                    self._send_file(energy_path)
                else:
                    self._send(404, b"energy.jpg not found", "text/plain; charset=utf-8")
                return

            if path.startswith("/asset/card/"):
                cid = path.split("/")[-1]
                p = _image_for_cid(cid)
                if p and p.exists():
                    self._send_file(p)
                elif back_path and pathlib.Path(back_path).exists():
                    self._send_file(pathlib.Path(back_path))
                else:
                    self._send(404, b"card image not found", "text/plain; charset=utf-8")
                return

            self._send(404, b"Not Found", "text/plain; charset=utf-8")

        def do_POST(self) -> None:
            path = urllib.parse.urlparse(self.path).path
            if path != "/api/action":
                self._send(404, b"Not Found", "text/plain; charset=utf-8")
                return

            length = int(self.headers.get("Content-Length","0") or "0")
            body = self.rfile.read(length) if length > 0 else b"{}"
            try:
                req = json.loads(body.decode("utf-8"))
            except:
                self._json({"ok": False, "error": "Invalid JSON"}, 400)
                return

            act = (req.get("action") or "").strip()
            try:
                if act == "draw":
                    engine.draw(int(req.get("n",1)))
                elif act == "undo":
                    engine.undo()
                elif act == "next":
                    p = engine.state.popup or {}
                    if p.get("mode") == "confirm" and p.get("next_closes"):
                        if p.get("requires_choice") and not p.get("choice_ok"):
                            raise RuntimeError("Choice required")
                        na = (p.get("next_action") or "").strip()
                        if na == "ack_resolve":
                            engine.ack_resolve()
                        elif na == "close_popup":
                            engine.close_popup(force=True)
                    else:
                        if engine.state.resolve:
                            engine.ack_resolve()
                    engine.next_phase()
                elif act == "play_to_stage":
                    engine.play_to_stage(req.get("cid",""), req.get("slot",""))
                elif act == "add_energy_under":
                    engine.add_energy_under(req.get("slot",""), int(req.get("k",1)))
                elif act == "move_to_liveset":
                    engine.move_to_liveset(list(req.get("cids") or []))
                elif act == "commit_liveset":
                    engine.move_liveset_to_resolve()
                elif act == "ack_resolve":
                    engine.ack_resolve()
                elif act == "open_waiting":
                    engine.open_waiting_popup()
                elif act == "close_popup":
                    engine.close_popup()
                elif act == "activate":
                    engine.activate(req.get("slot",""))
                else:
                    self._json({"ok": False, "error": f"Unknown action: {act}"}, 400)
                    return
            except Exception as e:
                self._json({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)
                return

            self._json({"ok": True, "state": _view_state(), "deck_error": deck_err, "deck_file": deck_fname})

    httpd = ThreadingHTTPServer((host, int(port)), Handler)

    url = f"http://{host}:{int(port)}/"
    print(f"[LLCG UI v5] root={root}")
    print(f"[LLCG UI v5] card_images={card_images_dir}")
    print(f"[LLCG UI v5] deck_code={deck_code} (file={deck_fname})")
    if deck_err:
        print(f"[LLCG UI v5][WARN] {deck_err}")
    print(f"[LLCG UI v5] open: {url}")

    if open_browser:
        try:
            threading.Timer(0.3, lambda: webbrowser.open(url)).start()
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

# No %-formatting to avoid CSS percent conflicts
INDEX_HTML = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>LLCG Manual UI (Clean v5)</title>
<style>
  :root{
    --pmW: 1200px;
    --pmH: 654px;
    --scale: 0.77;
    --cardW: 347px;
    --cardH: 485px;
  }
  html,body{height:100%;margin:0;background:#111;color:#eee;font-family:system-ui, -apple-system, Segoe UI, Roboto, sans-serif;}
  #root{height:100%;display:flex;align-items:center;justify-content:center;}
  #pmWrap{position:relative;width:var(--pmW);height:var(--pmH);background:#222;box-shadow:0 10px 40px rgba(0,0,0,.6);overflow:hidden;border-radius:10px;}
  #playmat{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;user-select:none;pointer-events:none;}
  .zone{position:absolute;box-sizing:border-box;}
  .zone.debug{outline:2px dashed rgba(0,0,0,.35);}
  .label{position:absolute;left:6px;top:6px;padding:2px 6px;font-size:12px;background:rgba(0,0,0,.55);border-radius:6px;pointer-events:none;}
  .countBadge{position:absolute;right:6px;bottom:6px;padding:2px 6px;font-size:12px;background:rgba(0,0,0,.75);border-radius:6px;}
  #topBar{position:absolute;left:10px;top:10px;display:flex;gap:8px;align-items:center;z-index:6000;}
  #topBar .pill{background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:6px 10px;font-size:12px;}
  #topBar .miniBtn{background:rgba(255,255,255,.12);color:#eee;border:1px solid rgba(255,255,255,.12);padding:6px 10px;border-radius:10px;cursor:pointer;}
  #zones{position:absolute;inset:0;}
  .cardWrap{
    position:absolute;
    border-radius:8px;
    box-shadow: 0 6px 18px rgba(0,0,0,.55);
    user-select:none;
    cursor:pointer;
    background:#000;
  }
  .cardWrap img{
    position:absolute;left:0;top:0;
    border-radius:8px;
    display:block;
    width:100%;height:100%;
    pointer-events:none;
  }
  .cardWrap.selected{outline:6px solid rgba(255,213,74,.95); outline-offset:-6px;}
  .selBadge{
    position:absolute;left:8px;top:8px;
    padding:2px 6px;font-size:11px;
    background:rgba(255,210,70,.95); color:#111;
    border-radius:999px;
    pointer-events:none;
  }
  .actBtn{
    position:absolute; left:50%; transform:translateX(-50%);
    bottom:-34px; z-index:6500;
    font-size:12px; padding:6px 10px; border-radius:12px;
    background:#ffd54a; color:#111;
    box-shadow:0 6px 18px rgba(0,0,0,.55);
    cursor:pointer;
  }
  #popupMask{position:absolute; inset:0; background:rgba(0,0,0,.55); display:none; z-index:9000;}
  #popup{
    position:absolute;
    width:min(92%, calc(var(--pmW) * 0.82));
    background:#1b1b1b; border:1px solid rgba(255,255,255,.15);
    border-radius:16px; padding:12px 12px 14px 12px;
    box-shadow: 0 14px 60px rgba(0,0,0,.7);
  }
  #popupHeader{display:flex;justify-content:space-between;gap:10px;align-items:center;}
  #popupTitle{font-weight:700;}
  #popupText{white-space:pre-wrap;line-height:1.35;color:#ddd;font-size:13px;margin-top:10px;}
  #popupCards{position:relative;height: calc(var(--cardH) * 0.72); overflow-x:auto; overflow-y:hidden; padding-bottom:10px; display:none; margin-top:10px;}
  #popupCardsInner{position:relative;height:100%; min-width:100%;}
  #logBox{position:absolute; inset:0; overflow:auto; font-size:12px; line-height:1.3; padding:8px; background:rgba(0,0,0,.45); border-radius:10px; white-space:pre-wrap;}
</style>
</head>
<body>
<div id="root">
  <div id="pmWrap">
    <img id="playmat" src="/asset/playmat" alt="playmat"/>
    <div id="topBar">
      <div class="pill">Turn: <b id="turn"></b> | Energy: <b id="energy"></b> | Phase: <b id="phase"></b></div>
      <div class="pill">Selected: <b id="selected"></b></div>
      <button class="miniBtn" id="btnDraw">Draw</button>
      <button class="miniBtn" id="btnCommit">LiveSet→Resolve</button>
      <button class="miniBtn" id="btnUndo">UNDO</button>
      <button class="miniBtn" id="btnNext">NEXT</button>
      <button class="miniBtn" id="btnWaiting">控え室</button>
      <button class="miniBtn" id="btnDbg">枠表示</button>
      <div class="pill" id="deckInfo"></div>
    </div>

    <div id="zones"></div>

    <div id="popupMask">
      <div id="popup">
        <div id="popupHeader">
          <div id="popupTitle">Popup</div>
        </div>
        <div id="popupText"></div>
        <div id="popupCards"><div id="popupCardsInner"></div></div>
        <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:10px;">
          <button class="miniBtn" id="popupAck" style="display:none;">ACK</button>
        </div>
      </div>
    </div>

  </div>
</div>

<script>
const BASE_W = 1560;
const BASE_H = 851;

const layout = {
  pm: {w: BASE_W, h: BASE_H},
  zones: {
    deck:    {x: 1235, y:  60, w: 270, h: 180, kind:"stack"},
    waiting: {x: 1235, y: 255, w: 270, h: 260, kind:"stack"},
    log:     {x:  50, y: 585, w: 430, h: 235, kind:"log"},
    hand:    {x: 520, y: 600, w: 650, h: 235, kind:"fan", orient:"portrait"},
    stageL:  {x: 352, y: 280, w: 181, h: 252, kind:"stage", slot:"L", orient:"portrait"},
    stageC:  {x: 683, y: 280, w: 180, h: 251, kind:"stage", slot:"C", orient:"portrait"},
    stageR:  {x: 995, y: 280, w: 180, h: 251, kind:"stage", slot:"R", orient:"portrait"},
    liveset: {x: 600, y:  80, w: 650, h: 200, kind:"fan", orient:"landscape"},
    resolve: {x: 520, y: 445, w: 710, h: 160, kind:"fan", orient:"portrait"},
    energy:  {x: 1235, y: 545, w: 270, h: 280, kind:"energy"},
  },
  popupAnchor: {x: 860, y: 510}
};

let debug = false;
let state = null;
let sel = [];

function setCSSScale(){
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
window.addEventListener('resize', ()=>{ setCSSScale(); render(); });

function px(v){ return (v * parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--scale'))); }

async function apiState(){
  const r = await fetch('/api/state');
  return await r.json();
}
async function apiAction(action, payload={}){
  const r = await fetch('/api/action', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({action, ...payload})
  });
  return await r.json();
}

function limitByPhase(){
  if(!state) return 1;
  return (state.phase === 'LIVESET') ? 3 : 1;
}
function toggleSelect(cid){
  const idx = sel.indexOf(cid);
  if(idx >= 0) sel.splice(idx,1);
  else{
    sel.push(cid);
    const lim = limitByPhase();
    while(sel.length > lim) sel.shift();
  }
  render();
}
function clearSelect(){ sel = []; render(); }

function getCardByCid(cid){
  const all = (state.hand||[]).concat(state.liveset||[], state.resolve||[]);
  for(const k of ['L','C','R']){
    if(state.stage && state.stage[k]) all.push(state.stage[k]);
  }
  return all.find(x=>x.cid===cid) || null;
}

function storedOrient(card){
  if(card.img_orient) return card.img_orient;
  const t = (card.card_type||"").toUpperCase();
  if(t === 'LIVE') return 'landscape';
  return 'portrait';
}

function hasActivation(card){
  const t = (card && card.text) ? String(card.text) : "";
  return /【\s*起動\s*】|<\s*起動\s*>|\[\s*起動\s*\]|［\s*起動\s*］/.test(t);
}


function computeDispSize(wantOrient, zoneW, zoneH){
  const cardW = px(451), cardH = px(630);
  let baseW = (wantOrient==='portrait') ? cardW : cardH;
  let baseH = (wantOrient==='portrait') ? cardH : cardW;
  const s = Math.min(1.0, zoneW / baseW, zoneH / baseH);
  return {w: baseW*s, h: baseH*s};
}

function makeCardWrap(card, wantOrient, x, y, w, h, clickable=true, zBase=100, allowHover=null){
  const wrap = document.createElement('div');
  wrap.className = 'cardWrap';
  wrap.style.left = x + 'px';
  wrap.style.top  = y + 'px';
  wrap.style.width  = w + 'px';
  wrap.style.height = h + 'px';

  const isSel = sel.includes(card.cid);
  if(isSel){
    wrap.classList.add('selected');
    wrap.style.zIndex = String(9000 + sel.indexOf(card.cid));
  }else{
    wrap.style.zIndex = String(zBase);
  }

  const img = document.createElement('img');
  img.alt = card.card_no;
  img.src = card.img;

  const stored = storedOrient(card);
  let rot = 0;
  if(wantOrient !== stored){
    rot = (wantOrient==='portrait' && stored==='landscape') ? 90 : -90;
  }

  if(rot === 0){
    img.style.width = '100%';
    img.style.height = '100%';
  }else{
    img.style.width = h + 'px';
    img.style.height = w + 'px';
    img.style.transformOrigin = '0 0';
    if(rot === 90){
      img.style.transform = `translate(${w}px, 0px) rotate(90deg)`;
    }else{
      img.style.transform = `translate(0px, ${h}px) rotate(-90deg)`;
    }
  }
  wrap.appendChild(img);

  if(isSel){
    const b = document.createElement('div');
    b.className = 'selBadge';
    b.textContent = 'SELECTED';
    wrap.appendChild(b);
  }

  if(allowHover === null) allowHover = clickable;

  if(allowHover){
    const lift = Math.max(6, Math.floor(h*0.06));
    wrap.addEventListener('mouseenter', ()=>{
      if(!sel.includes(card.cid)) wrap.style.zIndex = '8800';
      wrap.style.transform = `translateY(${-lift}px)`;
    });
    wrap.addEventListener('mouseleave', ()=>{
      wrap.style.transform = 'translateY(0px)';
      if(!sel.includes(card.cid)) wrap.style.zIndex = String(zBase);
    });
  }

  if(clickable){
    wrap.addEventListener('click', (e)=>{
      e.stopPropagation();
      toggleSelect(card.cid);
    });
  }else{
    wrap.style.cursor = 'default';
  }
  return wrap;
}

function render(){
  if(!state) return;
  document.getElementById('turn').textContent = String(state.turn||1);
  document.getElementById('phase').textContent = state.phase || '';
  document.getElementById('energy').textContent = `${(state.energy||{}).cur||0}/${(state.energy||{}).max||0}`;

  const selLabel = sel.map(cid => {
    const c = getCardByCid(cid);
    return c ? c.card_no : cid;
  }).join(', ');
  document.getElementById('selected').textContent = selLabel || '-';
  document.getElementById('deckInfo').textContent = state.deck_file ? `Deck: ${state.deck_file}` : '';

  const zones = document.getElementById('zones');
  zones.innerHTML = '';

  for(const [k,z] of Object.entries(layout.zones)){
    const zn = document.createElement('div');
    zn.className = 'zone' + (debug ? ' debug':'' );
    zn.style.left = px(z.x) + 'px';
    zn.style.top  = px(z.y) + 'px';
    zn.style.width = px(z.w) + 'px';
    zn.style.height = px(z.h) + 'px';

    const lab = document.createElement('div');
    lab.className = 'label';
    lab.textContent = k;
    zn.appendChild(lab);

    const zoneW = px(z.w), zoneH = px(z.h);

    if(z.kind === 'log'){
      const box = document.createElement('div');
      box.id = 'logBox';
      box.textContent = (state.log||[]).slice(-80).join('\n');
      zn.appendChild(box);
    }

    if(z.kind === 'stack'){
      const img = document.createElement('img');
      img.src = (k==='deck') ? '/asset/back' : ((state.waiting_top && state.waiting_top.img) ? state.waiting_top.img : '/asset/back');
      img.style.width = '100%';
      img.style.height = '100%';
      img.style.objectFit = 'contain';
      img.style.borderRadius = '10px';
      img.style.boxShadow = '0 6px 18px rgba(0,0,0,.55)';
      zn.appendChild(img);

      const badge = document.createElement('div');
      badge.className = 'countBadge';
      badge.textContent = (k==='deck') ? String((state.counts||{}).deck||0) : String((state.counts||{}).waiting||0);
      zn.appendChild(badge);

      zn.addEventListener('click', async (e)=>{
        e.stopPropagation();
        if(k==='deck'){
          const r = await apiAction('draw', {n: (e.shiftKey ? 3 : 1)});
          if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); }
          else alert(r.error||'error');
        }else{
          const r = await apiAction('open_waiting', {});
          if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); showPopupFromState(); }
          else alert(r.error||'error');
        }
      });
    }

    if(z.kind === 'fan'){
      let cards = [];
      if(k==='hand') cards = state.hand || [];
      if(k==='liveset') cards = state.liveset || [];
      if(k==='resolve') cards = state.resolve || [];
      const wantOrient = z.orient;

      const sz = computeDispSize(wantOrient, zoneW, zoneH);
      let drawW = sz.w, drawH = sz.h;
      let step = drawW;
      if(cards.length > 1){
        const maxStep = drawW * 0.55;
        const fitStep = (zoneW - drawW) / (cards.length - 1);
        step = Math.max(10, Math.min(maxStep, fitStep));
      }

      const clickable = (k==='hand' || k==='liveset');

      cards.forEach((c,i)=>{
        const x = i*step;
        const y = 0;
        const el = makeCardWrap(c, wantOrient, x, y, drawW, drawH, clickable, 100+i);
        zn.appendChild(el);
      });

      if(k==='hand'){
        zn.addEventListener('click', (e)=>{ e.stopPropagation(); clearSelect(); });
      }

      if(k==='liveset'){
        zn.addEventListener('click', async (e)=>{
          e.stopPropagation();
          if((state.phase||'') !== 'LIVESET') return;
          if(sel.length === 0) return;
          const r = await apiAction('move_to_liveset', {cids: sel});
          if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; sel=[]; render(); }
          else alert(r.error||'error');
        });
      }
    }

    if(z.kind === 'stage'){
      const slot = z.slot;
      const card = (state.stage||{})[slot];
      const wantOrient = 'portrait';

      const ecount = ((state.energies_under||{})[slot]) || 0;
      for(let i=0;i<ecount;i++){
        const eg = document.createElement('img');
        eg.src = '/asset/energy';
        eg.style.position = 'absolute';
        eg.style.left = (i * zoneW * 0.05) + 'px';
        eg.style.top  = (i * zoneH * 0.05) + 'px';
        eg.style.width = (zoneW * 0.92) + 'px';
        eg.style.height = (zoneH * 0.98) + 'px';
        eg.style.objectFit = 'contain';
        eg.style.opacity = 0.95;
        eg.style.pointerEvents = 'none';
        zn.appendChild(eg);
      }

      if(card){
        const sz = computeDispSize(wantOrient, zoneW, zoneH);
        const x = Math.max(0, (zoneW - sz.w)/2);
        const y = Math.max(0, (zoneH - sz.h)/2);
        const el = makeCardWrap(card, wantOrient, x, y, sz.w, sz.h, false, 200);
        el.style.pointerEvents = 'none';
        zn.appendChild(el);
        if(hasActivation(card)){

        const b = document.createElement('button');
        b.className = 'actBtn';
        b.textContent = '起動';
        b.addEventListener('click', async (e)=>{
          e.stopPropagation();
          const r = await apiAction('activate', {slot});
          if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); showPopupFromState(); }
          else alert(r.error||'error');
        });
        zn.appendChild(b);

        }
      }

      zn.addEventListener('click', async (e)=>{
        e.stopPropagation();
        if(sel.length === 0) return;
        const cid = sel[sel.length-1];
        const r = await apiAction('play_to_stage', {cid, slot});
        if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; sel=[]; render(); showPopupFromState(); }
        else alert(r.error||'error');
      });

      zn.addEventListener('contextmenu', async (e)=>{
        e.preventDefault();
        const r = await apiAction('add_energy_under', {slot, k:1});
        if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); }
      });
    }

    if(z.kind === 'energy'){
      const box = document.createElement('div');
      box.style.position='absolute'; box.style.inset='0';
      box.style.display='flex'; box.style.flexDirection='column'; box.style.justifyContent='flex-start';
      box.style.gap='8px';
      box.style.padding='10px';
      box.style.background='rgba(0,0,0,.35)';
      box.style.borderRadius='12px';
      box.style.pointerEvents='none';

      const t = document.createElement('div');
      t.textContent = `Energy: ${(state.energy||{}).cur||0}/${(state.energy||{}).max||0}`;
      t.style.fontWeight='700';
      box.appendChild(t);

      const t2 = document.createElement('div');
      t2.textContent = `Turn: ${state.turn||1} | Phase: ${state.phase||''}`;
      t2.style.fontWeight='700';
      box.appendChild(t2);

      const note = document.createElement('div');
      note.style.fontSize='11px';
      note.style.color='#bbb';
      note.textContent = '右クリックでステージにEnergy追加（暫定）';
      box.appendChild(note);

      zn.appendChild(box);
    }

    zones.appendChild(zn);
  }

  const popup = document.getElementById('popup');
  const ax = px(layout.popupAnchor.x);
  const ay = px(layout.popupAnchor.y);
  popup.style.left = `calc(${ax}px - (min(92%, (var(--pmW) * 0.82)) / 2))`;
  popup.style.top  = `calc(${ay}px - 120px)`;

  showPopupFromState();
}

function showPopupFromState(){
  const mask = document.getElementById('popupMask');
  const title = document.getElementById('popupTitle');
  const text = document.getElementById('popupText');
  const cardsWrap = document.getElementById('popupCards');
  const cardsInner = document.getElementById('popupCardsInner');
  const btnAck = document.getElementById('popupAck');

  if(!state || !state.popup){
    mask.style.display = 'none';
    return;
  }
  mask.style.display = 'block';
  const p = state.popup;
  title.textContent = p.title || 'Popup';

  const kind = (p.kind || '');
  const isResolve = (kind === 'resolve_confirm') || ((p.title||'').includes('Resolve'));
  const isWaiting = (kind === 'waiting') || ((p.title||'').includes('控え室'));

  const hasText = !!(p.text && String(p.text).trim());
  if(hasText){
    text.style.display = 'block';
    text.textContent = p.text;
  }else{
    text.style.display = 'none';
    text.textContent = '';
  }

  cardsInner.innerHTML = '';
  let cards = [];
  if(p.content === 'cards' || isResolve || isWaiting){
    if(isResolve) cards = state.resolve || [];
    else if(isWaiting) cards = state.waiting || [];
  }

  if(cards.length > 0){
    cardsWrap.style.display = 'block';
    const wantOrient = 'portrait';
    const zoneW = cardsWrap.clientWidth || px(900);
    const zoneH = cardsWrap.clientHeight || px(300);
    const sz = computeDispSize(wantOrient, zoneW, zoneH);
    const drawW = sz.w, drawH = sz.h;

    const step = Math.max(12, drawW * 0.45); // overlap ~55%
    const totalW = (cards.length<=1) ? drawW : ((cards.length-1)*step + drawW);
    cardsInner.style.width = Math.max(zoneW, totalW) + 'px';

    cards.forEach((c,i)=>{
      const x = i*step;
      const y = 0;
      const el = makeCardWrap(c, wantOrient, x, y, drawW, drawH, false, 100+i, true);
      cardsInner.appendChild(el);
    });
  }else{
    cardsWrap.style.display = 'none';
  }

  btnAck.style.display = 'inline-block';
  if(isResolve){
    btnAck.textContent = 'ACK(控え室へ)';
    btnAck.onclick = async ()=>{
      const r = await apiAction('ack_resolve', {});
      if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); }
      else alert(r.error||'error');
    };
  }else{
    btnAck.textContent = 'OK';
    btnAck.onclick = async ()=>{
      const r = await apiAction('close_popup', {});
      if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); }
      else alert(r.error||'error');
    };
  }
}


async function init(){
  setCSSScale();
  const r = await apiState();
  if(r.ok){
    state = r.state;
    state.deck_file = r.deck_file || '';
    render();

  // Popup interactions (no Close button)
  const mask = document.getElementById('popupMask');
  const popup = document.getElementById('popup');
  popup.addEventListener('click', (e)=>e.stopPropagation());
  mask.addEventListener('click', async ()=>{
    if(!state || !state.popup) return;
    const p = state.popup;
    const kind = (p.kind || '');
    const isResolve = (kind === 'resolve_confirm') || ((p.title||'').includes('Resolve'));
    if(isResolve) return;
    if(p.closable === false) return;
    const r = await apiAction('close_popup', {});
    if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); }
  });
  window.addEventListener('keydown', async (ev)=>{
    if(ev.key !== 'Escape') return;
    if(!state || !state.popup) return;
    const p = state.popup;
    const kind = (p.kind || '');
    const isResolve = (kind === 'resolve_confirm') || ((p.title||'').includes('Resolve'));
    if(isResolve) return;
    if(p.closable === false) return;
    const r = await apiAction('close_popup', {});
    if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); }
  });
  }else{
    alert('state error');
  }

  document.getElementById('btnDraw').onclick = async ()=>{
    const r = await apiAction('draw', {n:1});
    if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); }
  };
  document.getElementById('btnCommit').onclick = async ()=>{
    const r = await apiAction('commit_liveset', {});
    if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); showPopupFromState(); }
  };
  document.getElementById('btnUndo').onclick = async ()=>{
    const r = await apiAction('undo', {});
    if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; sel=[]; render(); }
  };
  document.getElementById('btnNext').onclick = async ()=>{
    if(state && state.popup && state.popup.mode==='confirm' && state.popup.requires_choice && !state.popup.choice_ok){
      alert('選択が必要です');
      return;
    }
    const r = await apiAction('next', {});
    if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; sel=[]; render(); showPopupFromState(); }
  };
  document.getElementById('btnWaiting').onclick = async ()=>{
    const r = await apiAction('open_waiting', {});
    if(r.ok){ state = r.state; state.deck_file = r.deck_file || ''; render(); showPopupFromState(); }
  };
  document.getElementById('btnDbg').onclick = ()=>{ debug = !debug; render(); };
}
init();
</script>
</body>
</html>'''
