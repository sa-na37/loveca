# -*- coding: utf-8 -*-
from __future__ import annotations

"""llocg_ui.server

HTTP サーバ（/ , /state, /cmd, /img）とフロントHTML。

- `App` が状態（GameState/RNG/DB/ImageLocator）を保持
- `Handler` は stdlib の http.server でルーティング
"""

import json
import time
from dataclasses import asdict

APP_VERSION = "v15"
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs, unquote

from .db import load_cards_db
from .images import ImageLocator
from .engine import (
    GameState,
    new_game,
    push_undo, do_undo,
    cmd_play, cmd_set, cmd_yell, cmd_attempt, cmd_ack,
    cmd_end_turn, cmd_next,
    cmd_activate_to_green,
    cmd_resolve_pending,
    trace_write,
    _get_card, _has_sacrifice_ability, can_activate,
)

def _write_text(path, text, encoding="utf-8"):
    """Write text to path, creating parent dirs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding=encoding)


HTML = r"""<!doctype html><html><head><meta charset="utf-8"/>
<title>LLCG Manual UI v15</title>
<style>
body{font-family:system-ui,sans-serif;margin:0}
.wrap{display:grid;grid-template-columns:1fr 380px;height:100vh}
.main{padding:10px;overflow:auto;background:#f7f7f7}
.side{border-left:1px solid #ddd;padding:10px;overflow:auto;background:#fff}
.row{display:flex;gap:10px;align-items:flex-start;flex-wrap:wrap}
.panel{background:#fff;border:1px solid #ddd;border-radius:8px;padding:10px}
.title{font-weight:600;margin-bottom:6px}
.cards{display:flex;gap:6px;flex-wrap:wrap}

/* Card rendering (MEMBER upright, LIVE rotated).
   Baseline size is aligned to the stage slot (~110px wide).
   Keep captions outside the media box so they never get clipped. */
.card{width:130px}
.cardLiveSet{width:auto}
.media{width:110px;height:154px;position:relative;display:flex;align-items:center;justify-content:center}
.media img{width:100%;height:100%;border-radius:6px;border:1px solid #ccc;object-fit:contain;display:block;background:#fff}
.card .cap{font-size:12px;line-height:1.2;margin-top:4px}

/* LIVE: portrait box; rotate the landscape image inside, centered */
.liveBox{width:110px;height:158px;position:relative;overflow:hidden;border-radius:6px}
/* rotate wrappers (used both inside liveBox and in stack/zone overlays) */
.rotWrap{position:absolute;top:50%;left:50%;width:158px;height:110px;transform:translate(-50%,-50%) rotate(90deg);transform-origin:center;display:flex;align-items:center;justify-content:center}
.rotWrap img{width:100%;height:100%;object-fit:contain;border:none;border-radius:0;background:transparent}
.rotWrapCCW{position:absolute;top:50%;left:50%;width:158px;height:110px;transform:translate(-50%,-50%) rotate(-90deg);transform-origin:center;display:flex;align-items:center;justify-content:center}
.rotWrapCCW img{width:100%;height:100%;object-fit:contain;border:none;border-radius:0;background:transparent}
.liveBox .rotWrap{position:absolute;top:50%;left:50%;width:158px;height:110px;transform:translate(-50%,-50%) rotate(90deg);transform-origin:center;display:flex;align-items:center;justify-content:center}
.liveBox .rotWrap img{width:100%;height:100%;object-fit:contain;border:none;border-radius:0;background:transparent}

/* Stage slots */
.stageSlot{width:120px;height:160px;border:2px dashed #aaa;border-radius:10px;display:flex;align-items:center;justify-content:center;background:#fafafa}

/* Resolve stack */
.stack{display:flex;align-items:flex-start;gap:0;overflow-x:auto;overflow-y:hidden;padding:4px 4px 10px 4px;min-height:190px}
.stack .card{width:auto}
.stack .media{width:110px;height:154px}
/* ~2/3 overlap (show ~1/3 of next) */
.stack .card + .card{margin-left:-75px}
.stack .card{position:relative}

/* Buttons */
.btn{padding:4px 8px;border:1px solid #999;background:#fff;border-radius:6px;cursor:pointer;font-size:16px;line-height:1.1}
.actBtn{position:absolute;left:50%;bottom:4px;transform:translateX(-50%);padding:4px 10px;border:1px solid rgba(0,0,0,.25);background:rgba(255,255,255,.92);border-radius:999px;cursor:pointer;font-size:12px}
.matWrap{position:relative;width:100%;max-width:1100px;aspect-ratio:1560/851;border:1px solid #ddd;border-radius:10px;overflow:hidden;background:#222;margin-bottom:10px}
.matImg{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:contain;object-position:center;opacity:1}
.zone{position:absolute;border:2px dashed rgba(255,255,255,0.35);border-radius:10px;pointer-events:none}
.zoneInner{position:absolute;inset:0;display:flex;gap:6px;align-items:center;justify-content:flex-start;flex-wrap:nowrap;overflow:hidden;padding:6px;pointer-events:auto}
.zoneInner .card img{width:100%;height:100%}
.zoneTitle{position:absolute;left:6px;top:6px;font-size:12px;color:#fff;background:rgba(0,0,0,.55);padding:2px 6px;border-radius:6px}
.matLog{position:absolute;left:1.2%;top:60.5%;width:16.6%;height:36.8%;background:rgba(255,255,255,.78);border:1px solid rgba(0,0,0,.15);border-radius:12px;overflow:auto;padding:10px;z-index:6;box-shadow:0 8px 30px rgba(0,0,0,.12)}
.matLog pre{margin:0;font-size:11px;line-height:1.25;white-space:pre-wrap;word-break:break-word}
.matLog .matLogTitle{font-weight:700;font-size:12px;margin:0 0 6px 0;opacity:.8}

	.matCmdBar{position:absolute;right:1.6%;bottom:2.2%;display:flex;flex-direction:column !important;gap:4px;z-index:120;pointer-events:auto}
	.matInfo{font-size:12px;line-height:1.05;background:rgba(255,255,255,.85);border:1px solid rgba(0,0,0,.18);border-radius:8px;padding:4px 8px;min-width:92px;text-align:right}
	.matCmdBar button{font-size:12px;padding:4px 8px;border-radius:8px;border:1px solid rgba(0,0,0,.25);background:#fff;cursor:pointer}
.matCmdBar button:hover{background:rgba(255,255,255,.92)}

.matOverlay{position:absolute;left:0;top:0;right:0;bottom:0;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,.12);z-index:9}
.matOverlayPanel{background:rgba(255,255,255,.92);border:1px solid rgba(0,0,0,.12);border-radius:18px;box-shadow:0 20px 60px rgba(0,0,0,.18);padding:14px 14px 12px 14px;max-width:75%;min-width:420px}
.matOverlayHeader{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.matOverlayBadge{background:rgba(0,0,0,.70);color:#fff;border-radius:999px;padding:4px 10px;font-size:12px;font-weight:700}
.matOverlayText{font-size:14px;font-weight:700;opacity:.9}
.matOverlayChoices{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.matOverlayChoices select{font-size:14px;padding:6px 8px;border-radius:10px;border:1px solid rgba(0,0,0,.2)}
.matOverlayChoices button{font-size:14px;padding:6px 10px;border-radius:10px;border:1px solid rgba(0,0,0,.25);background:#fff;cursor:pointer}

.matResolveLabel{position:absolute;left:10px;top:10px;background:rgba(0,0,0,.70);color:#fff;border-radius:999px;padding:4px 10px;font-size:12px;font-weight:700;z-index:2}
.deckBadge{position:absolute;right:6px;bottom:6px;font-size:12px;color:#fff;background:rgba(0,0,0,.65);padding:2px 6px;border-radius:6px}
.clickSlot{width:120px;height:160px;border:2px dashed rgba(255,255,255,0.55);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;background:rgba(0,0,0,0.15);pointer-events:auto;cursor:pointer}
.matStageSlot{width:120px;height:160px;display:flex;align-items:center;justify-content:center;border:2px dashed rgba(120,120,120,0.55);border-radius:12px;background:rgba(255,255,255,0.15);cursor:pointer;pointer-events:auto;}
.matStageSlot:hover{background:rgba(255,255,255,0.22);}
.matStageSlot.sel{outline:3px solid rgba(0,0,0,0.35);outline-offset:2px;}
.matStageSlot .card{position:relative}

.log{font-family:ui-monospace,Menlo,monospace;font-size:12px;white-space:pre-wrap}
.small{font-size:12px;color:#444}
.kbd{font-family:ui-monospace,monospace;background:#eee;padding:1px 6px;border-radius:6px;border:1px solid #ddd}


/* LIVE rotation is handled by .liveBox/.rotWrap (see above). */

/* Playmat: use the same baseline size as the main UI (aligned to stage slot).
   This avoids the "small cards" regression and keeps LIVE rotation consistent. */
.zoneInner .card{width:auto}
.zoneInner .media{width:110px;height:154px}
.zoneInner .liveBox{width:110px;height:158px}
.zoneInner .liveBox .rotWrap{width:158px;height:110px}
.zoneInner .media img{border-radius:6px}

/* Set zone panel: fixed height, horizontal scroll so Next button doesn't move */
#setZone{flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden;height:190px;align-items:flex-start}
#setZone .card{flex:0 0 auto}

/* Playmat: rotated live cards inside mat zones (smaller) */

/* Cheer/reveal stack on playmat */
.stackRow{display:flex;align-items:center;justify-content:flex-start;flex-wrap:nowrap;overflow:hidden}
.stackRow .card{flex:0 0 auto}
.stackRow .card + .card{margin-left:-36px}

/* Playmat hand: overlap-to-fit + hover bring-to-front */
.zoneInner.handLayout{position:relative;overflow:hidden}
.zoneInner.handLayout .card{position:absolute;top:6px;left:0;transition:transform 80ms ease}
.zoneInner.handLayout .card:hover{transform:translateY(-3px)}

/* Playmat resolve overlay: appears only when resolve has cards */
.resolveOverlay{position:absolute;left:22%;top:46%;width:56%;height:30%;background:rgba(255,255,255,0.90);border:2px solid rgba(0,0,0,0.08);border-radius:14px;box-shadow:0 10px 24px rgba(0,0,0,0.08);padding:10px;z-index:30;}
.resolveOverlay .overlayLabel{position:absolute;left:10px;top:8px;background:rgba(0,0,0,.65);color:#fff;padding:4px 10px;border-radius:10px;font-size:13px;z-index:31}
.pendingBox{position:absolute;left:22%;top:33%;width:56%;background:rgba(255,255,255,0.92);border:2px solid rgba(0,0,0,0.08);border-radius:14px;box-shadow:0 10px 24px rgba(0,0,0,0.10);padding:12px 12px 10px 12px;z-index:35;display:none}
.pendingBox .pendingTitle{font-weight:800;font-size:16px;margin:0 0 8px 0}
.pendingBox .pendingText{font-size:13px;color:#222;margin:0 0 10px 0;white-space:pre-wrap}
.pendingBox .pendingRow{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.pendingBox select{padding:6px 8px;border-radius:8px;border:1px solid #bbb;background:#fff}
.pendingBox .btn{padding:6px 10px;border:1px solid #999;border-radius:10px;background:#fff;cursor:pointer;font-size:16px;line-height:1.1}
.pendingBox .btn.primary{background:#111;color:#fff;border-color:#111}
.resolveOverlay .zoneInner{height:calc(100% - 26px);overflow:hidden}
.matBanner{position:absolute;left:50%;top:60%;transform:translate(-50%,-50%);padding:10px 18px;border-radius:14px;background:rgba(0,0,0,0.75);color:#fff;font-size:44px;font-weight:800;letter-spacing:1px;z-index:40;pointer-events:none;}

/* Live-set zone on playmat: landscape box base (110x154 -> 154x110) */
.liveSetBox{width:var(--w,154px);height:var(--h,110px);position:relative;overflow:hidden;border-radius:6px;background:#fff}
.liveSetBox img{width:100%;height:100%;object-fit:contain;border-radius:6px}
.liveSetBox .rotWrapCCW{position:absolute;top:50%;left:50%;width:var(--h,110px);height:var(--w,154px);transform:translate(-50%,-50%) rotate(-90deg);transform-origin:center;}
.liveSetBox .rotWrapCCW img{width:100%;height:100%;object-fit:contain;border-radius:6px}




/* --- UI hotfix: energy/phase split + zone preview/popup --- */
#matInfoBox{height:32px; display:flex; align-items:center; justify-content:center;}
#matInfo{font-size:14px; font-weight:800; white-space:nowrap;}
#phasePill{position:absolute; left:50%; bottom:6px; transform:translateX(-50%);
  background:rgba(0,0,0,0.62); color:#fff; padding:2px 8px; border-radius:8px;
  font-size:12px; font-weight:800; letter-spacing:0.2px; z-index:20; line-height:1.1;}
#matZoneOverlay{position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
  width:980px; max-width:92%; height:380px; max-height:55%;
  background:rgba(255,255,255,0.86); border-radius:16px; box-shadow:0 10px 28px rgba(0,0,0,0.25);
  padding:14px 14px 10px 14px; display:none; z-index:30; overflow:hidden;}
#matZoneOverlay .titleRow{display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;}
#matZoneOverlay .title{font-weight:900; font-size:18px; color:#222;}
#matZoneOverlay .closeBtn{cursor:pointer; background:rgba(0,0,0,0.65); color:#fff; border:none;
  border-radius:10px; padding:6px 10px; font-weight:800;}
#matZoneOverlay .grid{display:flex; flex-wrap:wrap; gap:10px; overflow:auto; height:260px; padding-right:6px;}
#matZoneOverlay .cardThumb{width:110px; height:160px; border-radius:10px; border:1px solid rgba(0,0,0,0.18);
  background:linear-gradient(135deg,#ddd,#bbb); display:flex; align-items:center; justify-content:center; font-weight:900; color:#444;}
#matZoneOverlay img{width:110px; height:160px; object-fit:cover; border-radius:10px; border:1px solid rgba(0,0,0,0.18);}

/* Slightly larger pending overlay (still within screen) */
.resolveOverlay{height:38%; top:58%;}

/* Mini stacks inside deck/green */
.stackMini{position:absolute; left:8px; top:8px; width:76px; height:110px;}
.stackMini img{position:absolute; width:76px; height:110px; border-radius:10px; object-fit:cover; border:1px solid rgba(0,0,0,0.25);}
.stackMini .back{position:absolute; width:76px; height:110px; border-radius:10px; border:1px solid rgba(0,0,0,0.25);
  background:linear-gradient(135deg,#f7f7f7,#cfcfcf); display:flex; align-items:center; justify-content:center; font-weight:900; color:#666;}

</style></head><body>
<div class="wrap">
<div class="main">
<div class="panel" style="width:100%;">
  <div class="title">Playmat</div>
  <div class="matWrap" id="matWrap">
    <img class="matImg" src="/playmat" alt="playmat"/>
    <div id="matLog" class="matLog" style="display:none;">
      <div class="matLogTitle" style="font-weight:700;margin-bottom:6px;">Log</div>
      <pre id="matLogBody" style="white-space:pre-wrap;word-break:break-word;font-size:11px;line-height:1.25;"></pre>
    </div>
    <!-- zones (approx; adjust later) -->
    <div class="zone" id="zLive" style="left:19.2%;top:2.4%;width:60.6%;height:25.0%;">
      <div class="zoneTitle">Live set</div>
      <div class="zoneInner" id="matSet"></div>
    </div>
    <div class="zone" id="zStage" style="left:19.2%;top:28.6%;width:60.6%;height:33.2%;">
      <div class="zoneTitle">Stage</div>
      <div class="zoneInner" id="matStage" style="justify-content:space-around;">
        <div class="matStageSlot" id="matStageL"></div>
        <div class="matStageSlot" id="matStageC"></div>
        <div class="matStageSlot" id="matStageR"></div>
      </div>
    </div>
    <div class="zone" id="zHand" style="left:19.2%;top:63.0%;width:60.6%;height:34.6%;">
      <div class="zoneTitle">Hand</div>
      <div class="zoneInner handLayout" id="matHand"></div>

    </div>
    <div class="zone" id="zDeck" style="left:80.4%;top:2.4%;width:18.8%;height:28.0%;">
      <div class="zoneTitle">Deck</div>
      <div class="zoneInner" id="matDeck" style="justify-content:center;"></div>
      <div class="deckBadge" id="matDeckCount"></div>
    </div>

    <div class="zone" id="zReveal" style="left:1.2%;top:29.0%;width:16.8%;height:33.0%;">
      <div class="zoneInner stackRow" id="matReveal"></div>
    </div>
    <div class="zone" id="zGreen" style="left:80.4%;top:34.2%;width:18.8%;height:33.0%;">
      <div class="zoneTitle">Waiting room</div>
      <div class="zoneInner" id="matGreen" style="justify-content:center;"></div>
      <div class="deckBadge" id="matGreenCount"></div>
    </div>

    <div class="matCmdBar" id="matCmdBar">
      <div class="matInfo" id="matInfo">Energy: -</div>
      <button class="btn" id="btnUndo">Undo</button>
      <button class="btn" id="btnNext">Next</button>
    </div>

    <div id="matResolveOverlay" class="resolveOverlay" style="display:none;">
      <div class="overlayLabel">Cheer / Resolve</div>
      <div class="zoneInner stackRow" id="matResolve"></div>
    </div>

    <div id="matPendingOverlay" class="resolveOverlay" style="display:none;">
      <div class="overlayLabel">Auto choice</div>
      <div style="padding-top:26px;">
        <div id="matPendingText" class="small" style="font-size:12px;margin-bottom:8px;"></div>
        <div id="matPendingChoices"></div>
      </div>
    </div>

    <div class="phasePill" id="phasePill">Turn - | -</div>

    <div class="zoneOverlay" id="matZoneOverlay" style="display:none;">
      <div class="zoneOverlayInner">
        <div class="zoneOverlayHdr">
          <div id="matZoneTitle" style="font-weight:800;">Zone</div>
          <button class="btn" id="matZoneClose" style="padding:6px 10px;">Close</button>
        </div>
        <div id="matZoneGrid" class="zoneGrid"></div>
      </div>
    </div>

    <div id="matBanner" class="matBanner" style="display:none;"></div>
    </div>
  </div>
  <div class="small">※ 枠位置は暫定（playmat基準で後で微調整）。左の成功ライブ置き場は背景位置で実質カットしています。</div>
</div>

  <div class="row">
    <div class="panel" style="min-width:420px;">
      <div class="title">Stage</div>
      <div class="row">
        <div class="stageSlot" id="slotL" onclick="slotClick('L')">L</div>
        <div class="stageSlot" id="slotC" onclick="slotClick('C')">C</div>
        <div class="stageSlot" id="slotR" onclick="slotClick('R')">R</div>
      </div>
      <div class="small">Click a hand card → click L/C/R to play.</div>
    </div>

    <div class="panel">
      <div class="title">Resolve Zone (解決領域) / ACK → Green Room (控室)</div>
      <div class="stack" id="resolveStack"></div>
      <div class="row" style="margin-top:8px;">
        <button class="btn" onclick="sendCmd('yell', {})">Yell (エール)</button>
        <button class="btn" onclick="sendCmd('ack', {})">ACK (確認→控室)</button>
        <button class="btn" onclick="sendCmd('undo', {})">Undo</button>
      </div>
    </div>

    <div class="panel">
      <div class="title">Set Zone (伏せ)</div>
      <div class="cards" id="setZone"></div>
      <div class="row" style="margin-top:8px;">
        <button class="btn" onclick="setSelected()">Set selected (max3)</button>
        <button class="btn" onclick="sendCmd('attempt', {})">Attempt LIVE</button>
        <button class="btn" onclick="sendCmd('end_turn', {})">End Turn</button>
        <button class="btn" onclick="nextStep()">Next</button>
      </div>
    </div>
  </div>

  <div class="panel" style="margin-top:10px;">
    <div class="title">Hand</div>
    <div class="cards" id="hand"></div>
    <div class="small">Selected: <span class="kbd" id="selInfo">none</span></div>
  </div>
</div>

<div class="side">
  <div class="panel">
    <div class="title">Status</div>
    <div class="small" id="statusLine"></div>
    <div class="small" id="countsLine"></div>
    <div class="panel" style="margin-top:10px;">
      <div class="title">Selected Stage</div>
      <div class="small" id="selStageInfo">(click a stage slot)</div>
      <div id="selStageActions" class="row" style="margin-top:8px;"></div>
    </div>
    <div class="panel" style="margin-top:10px;">
      <div class="title">Pending Prompts</div>
      <div class="small" id="pendingBox">(none)</div>
    </div>
    <div class="row" style="margin-top:8px;">
      <button class="btn" onclick="sendCmd('toggle_debug', {})">Toggle Debug</button>
      <button class="btn" onclick="sendCmd('peek', {n:5})">Peek 5</button>
    </div>
  </div>

  <div class="panel" style="margin-top:10px;">
    <div class="title">Log</div>
    <div class="log" id="log"></div>
  </div>
</div>
</div>

<script>
(()=>{
let STATE=null;
// SAFETY_NORMALIZE_PENDING: avoid null state crash
if (STATE == null || typeof STATE !== "object") STATE = {};
if (!STATE.pending || typeof STATE.pending !== "object") STATE.pending = {};

let bannerTimer=null;
let selectedHand=new Set();
let playPick=null;
let selectedStage=null;

function escapeHtml(s){return (s||"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");}
function imgUrl(cn){return "/img?cn="+encodeURIComponent(cn);}

function makeCardBackEl(w,h,label){
  const d=document.createElement('div');
  d.className='cardBack';
  d.style.width=w+'px';
  d.style.height=h+'px';
  // Use back.jpeg (served via ImageLocator using cn=__BACK__).
  const img=document.createElement('img');
  img.src='/img?cn=__BACK__';
  img.alt='BACK';
  img.style.width='100%';
  img.style.height='100%';
  img.style.objectFit='cover';
  img.style.borderRadius='12px';
  d.appendChild(img);
  if(label){
    const t=document.createElement('div');
    t.textContent=label;
    t.style.position='absolute';
    t.style.right='8px';
    t.style.bottom='6px';
    t.style.background='rgba(0,0,0,0.55)';
    t.style.color='#fff';
    t.style.padding='2px 6px';
    t.style.borderRadius='10px';
    t.style.fontSize='12px';
    d.appendChild(t);
  }
  return d;
}

function isCardNo(cn){
  if(!cn) return false;
  if(typeof cn!=='string') return false;
  return cn.includes('!') || cn.startsWith('PL!') || cn.startsWith('L!') || cn.startsWith('S!') || cn.startsWith('M!');
}

function renderMiniStack(container, items, w=54, h=76, maxN=3){
  if(!container) return;
  container.innerHTML='';
  const n=Math.min(maxN, items.length);
  for(let i=0;i<n;i++){
    const cn=items[items.length-1-i];
    let el;
    if(isCardNo(cn)) {
      el=document.createElement('img');
      el.src=imgUrl(cn);
      el.className='miniCard';
      el.style.width=w+'px';
      el.style.height=h+'px';
    } else {
      el=makeCardBackEl(w,h,'');
      el.classList.add('miniCard');
    }
    el.style.position='absolute';
    el.style.left=(i*10)+'px';
    el.style.top=(i*6)+'px';
    container.appendChild(el);
  }
}

function showZoneOverlay(title, items){
  const ov=document.getElementById('matZoneOverlay');
  const titleEl=document.getElementById('matZoneTitle');
  const grid=document.getElementById('matZoneGrid');
  if(!ov||!grid||!titleEl) return;
  titleEl.textContent=title;
  grid.innerHTML='';
  const maxShow=120;
  const arr=Array.isArray(items)?items.slice(0,maxShow):[];
  arr.forEach((cn,idx)=>{
    const box=document.createElement('div');
    box.style.width='110px';
    box.style.height='154px';
    box.style.position='relative';
    if(isCardNo(cn)){
      const media=document.createElement('div');
      media.className = 'media' + (isLive(cn)?' liveBox':'');
      media.style.width='110px';
      media.style.height='154px';
      const img=document.createElement('img');
      img.src=imgUrl(cn);
      img.style.width='110px';
      img.style.height='154px';
      img.style.borderRadius='8px';
      img.style.boxShadow='0 2px 8px rgba(0,0,0,0.35)';
      if(isLive(cn)){
        // Rotate live cards to fit portrait slot
        const w=document.createElement('div');
        w.className='rotWrap';
        w.style.width='154px';
        w.style.height='110px';
        w.appendChild(img);
        media.appendChild(w);
      }else{
        media.appendChild(img);
      }
      box.appendChild(media);
    } else {
      box.appendChild(makeCardBackEl(110,154,'?'));
    }
    grid.appendChild(box);
  });
  ov.style.display='block';
}

function hideZoneOverlay(){
  const ov=document.getElementById('matZoneOverlay');
  if(ov) ov.style.display='none';
}

function labelFor(cn){
  const mLabel=(STATE&&STATE.cn2label)?STATE.cn2label:{};
  const mName=(STATE&&STATE.cn2name)?STATE.cn2name:{};
  return mLabel[cn] || mName[cn] || cn;
}
// State objects sometimes store cards as raw cardnumber strings ("PL!..."),
// and sometimes as objects like {cardnumber, name, ...}. Normalize here.
function cnOf(x){
  if(!x) return "";
  if(typeof x === 'string') return x;
  if(typeof x === 'object'){
    if(x.cardnumber) return x.cardnumber;
    if(x.cn) return x.cn;
  }
  return "";
}
function isCardNo(x){
  const cn = cnOf(x);
  return (typeof cn === 'string') && cn.includes('!') && cn.includes('-') && cn.length>=8;
}
function isLive(cn){
  const t=(STATE&&STATE.cn2type)?(STATE.cn2type[cn]||""): "";
  const s=String(t).toLowerCase();
  // Live cards may be typed as LIVE / LIVE_CARD / MUSIC, etc.
  return s.includes('live') || s.includes('music');
}

function renderMat(){
  const wrap=document.getElementById("matWrap");
  if(!wrap) return;

  // --- Stage slots ---
  const slots=["L","C","R"];
  slots.forEach(s=>{
    const box=document.getElementById("matStage"+s);
    if(!box) return;
    box.style.position = 'relative';
    const stageW = Math.max(1, Math.floor(box.clientWidth || 0));
    const stageH = Math.max(1, Math.floor(box.clientHeight || 0));
    box.innerHTML="";
    const cn=cnOf((STATE.stage||{})[s]) || "";
    if(cn){
      const d=document.createElement("div");
	      d.className="card cardLiveSet";
	      d.style.width = stageW + "px";
	      d.style.height = stageH + "px";
	      d.style.flex = "0 0 auto";
      const media=document.createElement("div");
      media.className="media" + (isLive(cn)?" liveBox":"");
      const img=document.createElement("img");
      img.src=imgUrl(cn);
      img.alt=cn;
      if(isLive(cn)){
        const w=document.createElement("div");
        w.className="rotWrap";
        w.appendChild(img);
        media.appendChild(w);
      }else{
        media.appendChild(img);
      }
      d.appendChild(media);
      box.appendChild(d);

      // Activated ability button (clicking stage itself is used for play/baton; avoid misclicks)
      const sd = (STATE.stage_detail||{})[s] || {};
      if(sd && sd.can_activate){
        const btn=document.createElement('button');
        btn.className='actBtn';
        btn.textContent='起動';
        btn.onclick=(ev)=>{
          ev.stopPropagation();
          sendCmd('activate_to_green', {pos: s});
        };
        box.appendChild(btn);
      }
    }else{
      const em=document.createElement('div');
      em.style.fontSize='12px';
      em.style.opacity=0.6;
      em.style.textAlign='center';
      em.style.height='100%';
      em.style.display='flex';
      em.style.alignItems='center';
      em.style.justifyContent='center';
      em.textContent='(empty)';
      box.appendChild(em);
    }

    // click-to-play (playmat-first): select a hand card, then click L/C/R
    box.onclick = () => {
      selectedStage = s;
      if(playPick === null || playPick === undefined){
        render();
        return;
      }
      sendCmd('play', { hand_idx: playPick, pos: s });
    };
  });

  // --- Live set (伏せ) on playmat ---
  const setBox=document.getElementById("matSet");
  if(setBox){
    setBox.innerHTML="";
    const arr=(STATE.set_zone||[]);

	    // Compute per-slot pixel size based on the *rendered* matSet size.
	    // (The playmat is responsive; do NOT hardcode px here.)
	    const SLOT_W=154, SLOT_H=110; // target landscape ratio
	    const gap=8;
	    const n=Math.max(1, arr.length);
	    const availW=Math.max(0, setBox.clientWidth||0);
	    const availH=Math.max(0, setBox.clientHeight||0);
	    let boxH=availH;
	    let boxW=boxH*(SLOT_W/SLOT_H);
	    const total0=n*boxW+(n-1)*gap;
	    if(availW>0 && total0>availW){
	      const scale=(availW-(n-1)*gap)/(n*boxW);
	      boxW*=Math.max(0.2, scale);
	      boxH*=Math.max(0.2, scale);
	    }
	    // Prevent pathological zero sizes (e.g., first render before layout)
	    if(!(boxW>0 && boxH>0)) { boxW=SLOT_W; boxH=SLOT_H; }
	    setBox.style.gap=gap+"px";
    arr.forEach((raw,idx)=>{
      const cn = cnOf(raw);
      const d=document.createElement("div");
      // Live-set area is landscape; use the dedicated sizing class so
      // live cards keep their aspect and member cards (rotated) don't get cropped.
      d.className="card cardLiveSet";
      // Keep deterministic stacking; selection for set-zone is handled on the hand side.
      d.style.zIndex=String(10+idx);
      const media=document.createElement("div");
      media.className="media liveSetBox";
	      // Enforce slot size (px) so cards keep aspect ratio regardless of viewport scaling.
	      media.style.width = boxW + "px";
	      media.style.height = boxH + "px";
	      media.style.setProperty('--w', boxW + "px");
	      media.style.setProperty('--h', boxH + "px");
      const img=document.createElement("img");
      img.src=imgUrl(cn);
      img.alt=cn;
      if(isLive(cn)){
        // LIVE card: keep landscape (no rotation)
        media.appendChild(img);
      }else{
        // Member card: rotate CCW to fit landscape slot
        const w=document.createElement("div");
        w.className="rotWrapCCW";
        w.appendChild(img);
        media.appendChild(w);
}
      d.appendChild(media);
      setBox.appendChild(d);
    });
    const cnt=document.getElementById("matSetCount");
    if(cnt) cnt.textContent = "x" + String(((STATE.set_zone||[]).length));
  }

  // --- Waiting room / Green room ---
  const greenBox=document.getElementById("matGreen");
  if(greenBox){
    greenBox.innerHTML="";
    const top=cnOf(STATE.green_room_top||"");
    if(top){
      const d=document.createElement("div");
      d.className="card";
      const media=document.createElement("div");
      media.className="media" + (isLive(top)?" liveBox":"");
      const img=document.createElement("img");
      img.src=imgUrl(top);
      img.alt=top;
      if(isLive(top)){
        const w=document.createElement("div");
        w.className="rotWrap";
        w.appendChild(img);
        media.appendChild(w);
      }else{
        media.appendChild(img);
      }
      d.appendChild(media);
      greenBox.appendChild(d);
    }
    const cnt=document.getElementById("matGreenCount");
    if(cnt) cnt.textContent = "x" + String((STATE.green_room_count||0));
  }

  // --- Hand on playmat: overlap to fit, hover to front ---
  const handBox=document.getElementById("matHand");
  if(handBox){
    handBox.innerHTML="";
    (STATE.hand||[]).forEach((raw,idx)=>{
      const cn = cnOf(raw);
      const d=document.createElement("div");
      d.className="card";
      d.style.cursor = 'pointer';
      d.dataset.baseZ=String(10+idx);
      d.style.zIndex=d.dataset.baseZ;
      const picked = (STATE && STATE.phase === 'LIVE_SET') ? selectedHand.has(idx) : (playPick === idx);
      if(picked){
        d.style.outline = '3px solid #111';
        d.style.outlineOffset = '2px';
        // Bring selected to front so the highlight is visible immediately.
        d.style.zIndex = '9999';
      }
      const media=document.createElement("div");
      media.className="media" + (isLive(cn)?" liveBox":"");
      const img=document.createElement("img");
      img.src=imgUrl(cn);
      img.alt=cn;
      if(isLive(cn)){
        const w=document.createElement("div");
        w.className="rotWrap";
        w.appendChild(img);
        media.appendChild(w);
      }else{
        media.appendChild(img);
      }
      d.appendChild(media);
      d.addEventListener("mouseenter", ()=>{ d.style.zIndex="9999"; });
      d.addEventListener("mouseleave", ()=>{ d.style.zIndex=d.dataset.baseZ || "10"; });
      d.addEventListener('click', ()=>{
        // LIVE_SET: choose up to 3 cards from hand to set.
        if(STATE && STATE.phase === 'LIVE_SET'){
          if(selectedHand.has(idx)){
            selectedHand.delete(idx);
          }else{
            if(selectedHand.size >= 3) return;
            selectedHand.add(idx);
          }
          render();
          return;
        }
        // MAIN: select from hand on playmat; then click Stage L/C/R to play
        playPick = idx;
        render();
      });
      handBox.appendChild(d);
    });

    // layout
    const cards=[...handBox.children];
    const n=cards.length;
    if(n>0){
      const cardW=110;
      const gap=8;
      const avail=Math.max(0, handBox.clientWidth - 12);
      const step = (n<=1) ? 0 : Math.min(cardW+gap, (avail-cardW)/(n-1));
      cards.forEach((el,i)=>{
        el.style.position="absolute";
        el.style.top="6px";
        el.style.left=(i*step)+"px";
        el.dataset.baseZ=String(10+i);
        el.style.zIndex=el.dataset.baseZ;
      });
      const totalW = (n==1) ? cardW : ( (n-1)*step + cardW );
      handBox.style.minHeight="170px";
      handBox.style.width = "100%";
      // allow some right padding
      handBox.style.overflow="hidden";
    }
  }

  // --- Resolve overlay on playmat (expanded only when needed) ---
  const overlay=document.getElementById("matResolveOverlay");
  const resBox=document.getElementById("matResolve");
  if(overlay && resBox){
    const arr=(STATE.resolve_zone||[]);
    if(!arr.length){
      overlay.style.display="none";
      resBox.innerHTML="";
    }else{
      overlay.style.display="block";
      resBox.innerHTML="";
      // Dynamic overlap so cards stay inside the resolve area (no overflow/scroll)
      const cardW = 110; // matches .stack .media width
      const W = Math.max(0, (resBox.clientWidth||0) - 8);
      const n = arr.length;
      let overlap = 0;
      if(n>1 && W>0){
        overlap = Math.max(0, (cardW*n - W) / (n-1));
        overlap = Math.min(cardW-12, overlap);
      }
      arr.forEach((cn,idx)=>{
        const d=document.createElement("div");
        d.className="card";
        d.style.zIndex=String(10+idx);
        if(idx>0 && overlap>0){ d.style.marginLeft = `-${overlap}px`; }
        const media=document.createElement("div");
        media.className="media" + (isLive(cn)?" liveBox":"");
        const img=document.createElement("img");
        img.src=imgUrl(cn);
        img.alt=cn;
        if(isLive(cn)){
          const w=document.createElement("div");
          w.className="rotWrap";
          w.appendChild(img);
          media.appendChild(w);
        }else{
          media.appendChild(img);
        }
        d.appendChild(media);
        resBox.appendChild(d);
      });
    }
  }
  }

  // --- Pending prompts popup on playmat (only when fired) ---
  const pov = document.getElementById('matPendingOverlay');
  const pText = document.getElementById('matPendingText');
  const pChoices = document.getElementById('matPendingChoices');
  if(pov && pText && pChoices){
    const pend = (STATE.pending || []);
    if(!pend.length){
      pov.style.display='none';
      pText.textContent='';
      pChoices.innerHTML='';
    }else{
      pov.style.display='block';
      const p = pend[0];
      const idx = 0;
      pText.textContent = p.title || p.text || 'Pending';
      pChoices.innerHTML='';

      // options model:
      // - live-start pay/skip: p.options == ['pay','skip']
      // - pick prompts: p.options contains cardnumbers (+ sometimes 'skip')
      // - where p.candidates exists, we treat it as selectable targets
      let opts = (p.options || p.choices || []);
      const cand = (p.candidates || []);
      const labelMap = {
        'pay':'Pay (E1)',
        'skip':'Skip',
        '__SKIP__':'Skip',
        'topdeck':'Top of deck',
        'green_room':'Green Room',
        'hand':'Hand',
      };

      // If the engine says "you may choose fewer", always provide a Skip/Finish button.
      const allowLess = !!p.allow_less;
      const hasSkip = allowLess || (opts||[]).includes('skip') || (opts||[]).includes('__SKIP__');

      // If candidates exist, use select+buttons (Choose / Skip)
      if(cand.length){
        const sel = document.createElement('select');
        sel.style.maxWidth='100%';
        sel.style.padding='6px 8px';
        sel.style.borderRadius='8px';
        sel.style.border='1px solid rgba(0,0,0,.18)';

        // Prefer opts that look like cardnumbers; otherwise fall back to candidates.
        const pickList = (opts && opts.length) ? opts.filter(v => String(v) !== 'skip' && String(v) !== '__SKIP__') : cand;

        const allCard = pickList.length>0 && pickList.every(v=>isCardNo(v));
        if(allCard){
          // Image grid (same scale as hand cards)
          pChoices.innerHTML='';
          const grid=document.createElement('div');
          grid.style.display='flex';
          grid.style.flexWrap='wrap';
          grid.style.gap='10px';
          grid.style.alignItems='flex-start';
          grid.style.marginTop='10px';
          // Slightly larger popup is acceptable; the card thumbnails should stay hand-sized.
          pickList.forEach(v=>{
            const cn=String(v);
            const box=document.createElement('div');
            box.className='cardBox';
            box.style.width='110px';
            box.style.height='160px';
            box.style.backgroundImage=`url(/img?cn=${encodeURIComponent(cn)})`;
            box.style.backgroundSize='contain';
            box.style.backgroundRepeat='no-repeat';
            box.style.backgroundPosition='center center';
            box.title=labelFor(cn);
            box.onclick=()=>{ sendCmd('resolve_pending',{idx,choice:cn}); };
            grid.appendChild(box);
          });

          const row=document.createElement('div');
          row.style.display='flex';
          row.style.gap='10px';
          row.style.alignItems='center';
          row.style.marginTop='10px';
          if(hasSkip){
            const btnSkip = document.createElement('button');
            btnSkip.className='btn';
            btnSkip.textContent='Skip';
            btnSkip.onclick=()=>{ sendCmd('resolve_pending',{idx,choice:'skip'}); };
            row.appendChild(btnSkip);
          }
          pChoices.appendChild(grid);
          pChoices.appendChild(row);
          return;
        }

        pickList.forEach(v=>{
          const o=document.createElement('option');
          o.value=String(v);
          const s=String(v);
          o.textContent = labelMap[s] || labelFor(s);
          sel.appendChild(o);
        });

        const row=document.createElement('div');
        row.style.display='flex';
        row.style.gap='10px';
        row.style.alignItems='center';
        row.style.marginTop='10px';

        const btnChoose = document.createElement('button');
        btnChoose.className='btn';
        btnChoose.textContent='Choose';
        btnChoose.onclick=()=>{
          const choice = sel.value;
          sendCmd('resolve_pending',{idx,choice});
        };

        row.appendChild(sel);
        row.appendChild(btnChoose);

        if(hasSkip){
          const btnSkip = document.createElement('button');
          btnSkip.className='btn';
          btnSkip.textContent='Skip';
          btnSkip.onclick=()=>{
            sendCmd('resolve_pending',{idx,choice:'skip'});
          };
          row.appendChild(btnSkip);
        }
        pChoices.appendChild(row);
      } else {
        // Otherwise: render one button per option (pay/skip etc). If no options, show OK.
        const row=document.createElement('div');
        row.style.display='flex';
        row.style.flexWrap='wrap';
        row.style.gap='10px';
        row.style.alignItems='center';
        row.style.marginTop='10px';

        if(opts && opts.length){
          opts.forEach(v=>{
            const s=String(v);
            const btn = document.createElement('button');
            btn.className='btn';
            btn.textContent = labelMap[s] || labelFor(s);
            btn.onclick = ()=>{ sendCmd('resolve_pending',{idx,choice:s}); };
            row.appendChild(btn);
          });
          if(hasSkip && !opts.includes('skip')){
            const btnSkip = document.createElement('button');
            btnSkip.className='btn';
            btnSkip.textContent='Skip';
            btnSkip.onclick=()=>{ sendCmd('resolve_pending',{idx,choice:'skip'}); };
            row.appendChild(btnSkip);
          }
        }else{
          const btn = document.createElement('button');
          btn.className='btn';
          btn.textContent='OK';
          btn.onclick=()=>{ sendCmd('resolve_pending',{idx,choice:''}); };
          row.appendChild(btn);
        }
        pChoices.appendChild(row);
      }
    }
  }

  // --- LIVE success/fail banner ---
  const b = document.getElementById('matBanner');
  if(b){
    if(STATE.banner && STATE.banner.text){
      b.textContent = STATE.banner.text;
      b.style.display='block';
      // Auto-hide locally: the UI only refreshes on commands, so without this
      // the banner may stick on screen. Keep it brief.
      if(bannerTimer){ try{ clearTimeout(bannerTimer); }catch(e){} }
      const shownText = STATE.banner.text;
      bannerTimer = setTimeout(()=>{
        // Only clear if it's still showing the same message.
        if(STATE && STATE.banner && STATE.banner.text === shownText){
          STATE.banner = null;
          b.textContent='';
          b.style.display='none';
        }
      }, 2600);
    }else{
      b.textContent='';
      b.style.display='none';
    }
  }

  // --- Playmat log panel (use empty left area) ---
  const ml = document.getElementById('matLog');
  const mlb = document.getElementById('matLogBody');
  if(ml && mlb){
    const lines = (STATE.log || []);
    if(!lines.length){
      ml.style.display='none';
      mlb.textContent='';
    }else{
      ml.style.display='block';
      const tail = lines.slice(Math.max(0, lines.length-18));
      mlb.textContent = tail.join('\n');
      ml.scrollTop = ml.scrollHeight;
    }
  }


async function fetchState(){
  const r=await fetch("/state");
  STATE=await r.json();
  render();
}

function renderCard(cn, cap){
  const div=document.createElement("div");
  div.className = isLive(cn) ? "card liveCard" : "card";

  const media=document.createElement("div");
  media.className = isLive(cn) ? "media liveBox" : "media";

  const img=document.createElement("img");
  img.src=imgUrl(cn);
  img.onerror=()=>{img.style.display="none";};

  if(isLive(cn)){
    const w=document.createElement('div');
    w.className='rotWrap';
    w.appendChild(img);
    media.appendChild(w);
  }else{
    media.appendChild(img);
  }
  div.appendChild(media);

  const p=document.createElement("div");
  p.className="cap";
  p.innerHTML=escapeHtml(cap);
  div.appendChild(p);
  return div;
}

function render(){
  if(!STATE) return;
  document.getElementById("statusLine").innerText =
    `Turn ${STATE.turn} | Phase=${STATE.phase} | Energy active=${STATE.energy_active} wait=${STATE.energy_wait} | Debug=${STATE.debug}`;
  document.getElementById("countsLine").innerText =
    `Deck=${STATE.deck.length} Hand=${STATE.hand.length} GreenRoom=${STATE.green_room.length} Resolve=${STATE.resolve_zone.length} | v20`;

  // Use playmat UI as the primary rendering surface.
  renderMat();
  // Energy (near Undo/Next)
  const mi = document.getElementById('matInfo');
  if(mi){
    const ea = Number(STATE.energy_active||0);
    const ew = Number(STATE.energy_wait||0);
    const tot = ea + ew;
    mi.textContent = `E ${ea}/${tot}`;
  }
  // Phase pill (bottom center)
  const pp = document.getElementById('phasePill');
  if(pp){
    pp.textContent = `Turn ${STATE.turn} | ${STATE.phase||'-'}`;
  }

  // Deck / Green room badges + mini previews + viewer popup
  const deckN = Number(STATE.deck_n ?? (Array.isArray(STATE.deck)?STATE.deck.length:0));
  const greenN = Number(STATE.green_n ?? (Array.isArray(STATE.green_room)?STATE.green_room.length:0));
  const deckCount = document.getElementById('matDeckCount');
  const greenCount = document.getElementById('matGreenCount');
  if(deckCount) deckCount.textContent = String(deckN);
  if(greenCount) greenCount.textContent = String(greenN);

  const deckEl = document.getElementById('matDeck');
  const greenEl = document.getElementById('matGreen');
  if(deckEl){
    if(!deckEl.querySelector('#matDeckStack')){
      const s=document.createElement('div');
      s.id='matDeckStack';
      s.className='miniStack';
      deckEl.appendChild(s);
    }
    const deckList = Array.isArray(STATE.deck)?STATE.deck:[];
    const visible = deckList.filter(c=>typeof c==='string').slice(-3);
    const stack = deckEl.querySelector('#matDeckStack');
    if(stack){
      stack.innerHTML='';
      if(visible.length){
        renderMiniStack(stack, visible, 38, 54);
      }else{
        // unknown or hidden deck: show card backs
        const n=Math.min(deckN,3);
        for(let i=0;i<n;i++) stack.appendChild(makeCardBackEl(38,54,''));
        [...stack.children].forEach((ch,i)=>{ch.style.left=(i*10)+'px'; ch.style.top=(i*6)+'px';});
      }
    }
    if(!deckEl.dataset.bound){
      deckEl.dataset.bound='1';
      deckEl.onclick=()=>{
        const cards = (Array.isArray(STATE.deck) && STATE.deck.length && typeof STATE.deck[0]==='string') ? STATE.deck : [];
        showZone('Main deck', cards, deckN);
      };
    }
  }
  if(greenEl){
    if(!greenEl.querySelector('#matGreenStack')){
      const s=document.createElement('div');
      s.id='matGreenStack';
      s.className='miniStack';
      greenEl.appendChild(s);
    }
    const gr = Array.isArray(STATE.green_room)?STATE.green_room:[];
    const visible = gr.filter(c=>typeof c==='string').slice(-3);
    const stack = greenEl.querySelector('#matGreenStack');
    if(stack){
      stack.innerHTML='';
      if(visible.length){
        renderMiniStack(stack, visible, 38, 54);
      }
    }
    if(!greenEl.dataset.bound){
      greenEl.dataset.bound='1';
      greenEl.onclick=()=>showZone('Waiting room', Array.isArray(STATE.green_room)?STATE.green_room:[], greenN);
    }
  }

      // NOTE: pending/choice UI is rendered inline above (playmat layout).
      // Older refactors left a stray renderPending() call; when undefined it
      // breaks the entire render loop (ReferenceError) and cascades into many
      // UI regressions. Keep render() self-contained.
      return;

  ["L","C","R"].forEach(pos=>{
    const el=document.getElementById("slot"+pos);
    el.innerHTML="";
    el.style.outline = (selectedStage===pos ? "3px solid #333" : "none");
    const slot=STATE.stage[pos];
    const cn = cnOf(slot);
    if(cn){
      const img=document.createElement("img");
      img.src=imgUrl(cn);
      img.style.width="110px";
      img.style.borderRadius="6px";
      img.style.border="1px solid #ccc";
      el.appendChild(img);
    }else{
      el.innerText=pos;
    }
  });

  
  // Selected stage + actions
  const selInfo=document.getElementById("selStageInfo");
  const selActions=document.getElementById("selStageActions");
  selActions.innerHTML="";
  if(!selectedStage){
    selInfo.innerText="(click a stage slot)";
  }else{
    const slot=STATE.stage[selectedStage];
    if(!slot || !slot.cardnumber){
      selInfo.innerText=`${selectedStage}: (empty)`;
    }else{
      const det=(STATE.stage_detail||{})[selectedStage]||{};
      selInfo.innerText=`${selectedStage}: ${det.cardnumber||slot.cardnumber}  ${det.name||""}  [${det.type||""}]`;
      if(det.has_sac){
        const b=document.createElement("button");
        b.className="btn";
        b.innerText="起動：このメンバーを控え室に置く";
        b.onclick=()=>sendCmd("activate_to_green",{pos:selectedStage});
        selActions.appendChild(b);
      }
    }
  }

  // Pending prompts
  const pb=document.getElementById("pendingBox");
  const pend=STATE.pending||[];
  if(!pend.length){
    pb.innerText="(none)";
  }else{
    pb.innerHTML="";
    pend.forEach((p,idx)=>{
      const row=document.createElement("div");
      row.className="row";
      row.style.gap="6px";
      row.style.alignItems="center";

      const t=document.createElement("div");
      t.className="small";
      t.style.flex="1";
      t.innerText=p.text||JSON.stringify(p);
      row.appendChild(t);

if((p.kind||"")==="choose_shioriko_enter"){
  const sel=document.createElement("select");
  sel.className="btn";
  const op1=document.createElement("option"); op1.value="energy"; op1.innerText="エネルギーを1枚アクティブ";
  const op2=document.createElement("option"); op2.value="topdeck"; op2.innerText="虹ヶ咲LIVEを最大2枚デッキ上";
  sel.appendChild(op1); sel.appendChild(op2);
  row.appendChild(sel);
  const go=document.createElement("button");
  go.className="btn";
  go.innerText="Choose";
  go.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:(sel.value||"")});
  row.appendChild(go);
}else if((p.kind||"")==="topdeck_live_from_green"){
  const sel=document.createElement("select");
  sel.className="btn";
  (p.options||[]).forEach((cn)=>{
    const op=document.createElement("option");
    op.value=cn;
    op.innerText=labelFor(cn);
    sel.appendChild(op);
  });
  row.appendChild(sel);
  const put=document.createElement("button");
  put.className="btn";
  put.innerText="Put";
  put.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:(sel.value||"")});
  const no=document.createElement("button");
  no.className="btn";
  no.innerText="Skip";
  no.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:"skip"});
  row.appendChild(put);
  row.appendChild(no);
}else if((p.kind||"")==="shioriko_topdeck_pick1" || (p.kind||"")==="shioriko_topdeck_pick2"){
  const sel=document.createElement("select");
  sel.className="btn";
  (p.options||[]).forEach((cn)=>{
    const op=document.createElement("option");
    op.value=cn;
    op.innerText=labelFor(cn);
    sel.appendChild(op);
  });
  row.appendChild(sel);
  const put=document.createElement("button");
  put.className="btn";
  put.innerText="Topdeck";
  put.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:(sel.value||"")});
  const no=document.createElement("button");
  no.className="btn";
  no.innerText="Skip";
  no.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:"skip"});
  row.appendChild(put);
  row.appendChild(no);
}else if((p.kind||"")==="pick_live_from_green"){

        const sel=document.createElement("select");
        sel.className="btn";
        (p.options||[]).forEach((cn)=>{
          const op=document.createElement("option");
          op.value=cn;
          op.innerText=labelFor(cn);
          sel.appendChild(op);
        });
        row.appendChild(sel);

        const take=document.createElement("button");
        take.className="btn";
        take.innerText="Take";
        take.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:(sel.value||"")});

        const no=document.createElement("button");
        no.className="btn";
        no.innerText="Skip";
        no.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:"skip"});

        row.appendChild(take);
        row.appendChild(no);
      }else{
        const yes=document.createElement("button");
        yes.className="btn";
        yes.innerText="Pay";
        yes.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:"pay"});
        const no=document.createElement("button");
        no.className="btn";
        no.innerText="Skip";
        no.onclick=()=>sendCmd("resolve_pending",{idx:idx,choice:"skip"});
        row.appendChild(yes);
        row.appendChild(no);
      }

      pb.appendChild(row);
    });
  }

  renderMat();

  const rs=document.getElementById("resolveStack");
  rs.innerHTML="";
  const rz=STATE.resolve_zone||[];
  const show=rz.slice(Math.max(0, rz.length-12));

  // Dynamic overlap so cards stay inside the resolve area
  const cardW = 90; // matches CSS .card width
  const W = Math.max(0, (rs.clientWidth||0) - 8);
  const n = show.length;
  let overlap = 0;
  if(n>1 && W>0){
    overlap = Math.max(0, (cardW*n - W) / (n-1));
    overlap = Math.min(cardW-10, overlap);
  }

show.forEach((cn, i)=>{
  const d=document.createElement('div');
  d.className = isLive(cn) ? 'card liveCard' : 'card';
  d.style.position = 'relative';
  d.style.zIndex = String(10 + i);
  if(i>0 && overlap>0){ d.style.marginLeft = `-${overlap}px`; }

  const media=document.createElement("div");
  media.className = isLive(cn) ? "media liveBox" : "media";

  const img=document.createElement('img');
  img.src=imgUrl(cn);
  img.title=labelFor(cn);

  if(isLive(cn)){
    const w=document.createElement('div');
    w.className='rotWrap';
    w.appendChild(img);
    media.appendChild(w);
  }else{
    media.appendChild(img);
  }
  d.appendChild(media);
  rs.appendChild(d);
});

  const sz=document.getElementById("setZone");
  sz.innerHTML="";
  (STATE.set_zone||[]).forEach(cn=>{ const el=renderCard(cn, labelFor(cn)); sz.appendChild(el); });

  const hand=document.getElementById("hand");
  hand.innerHTML="";
  (STATE.hand||[]).forEach((cn, idx)=>{
    const div=renderCard(cn, `${idx}: ${labelFor(cn)}`);
    // selection highlight should be visible immediately even when cards are overlapping
    if(selectedHand.has(idx)) {
      div.style.outline="none";
      div.style.boxShadow="0 0 0 3px rgba(0,0,0,0.85)";
      div.style.zIndex="9999";
    } else {
      div.style.outline="none";
      div.style.boxShadow="none";
    }
    div.style.cursor="pointer";
    div.onclick=()=>{
      if(selectedHand.has(idx)) selectedHand.delete(idx);
      else selectedHand.add(idx);
      playPick=idx;
      document.getElementById("selInfo").innerText = Array.from(selectedHand).sort((a,b)=>a-b).join(", ");
      render();
    };
    hand.appendChild(div);
  });

  document.getElementById("log").innerText=(STATE.log||[]).slice(-120).join("\n");
}

function slotClick(pos){
  if(playPick===null){
    selectedStage = (selectedStage===pos ? null : pos);
    render();
    return;
  }
  sendCmd("play",{hand_idx:playPick,pos:pos});
  playPick=null;
  selectedHand.clear();
}

function setSelected(){
  const idxs=Array.from(selectedHand).sort((a,b)=>a-b).slice(0,3);
  sendCmd("set",{indices:idxs});
  selectedHand.clear();
  playPick=null;
}


function nextStep(){
  const idxs=Array.from(selectedHand).sort((a,b)=>a-b).slice(0,3);
  sendCmd("next",{indices:idxs});
  selectedHand.clear();
  playPick=null;
}


async function sendCmd(cmd,payload){
  const body={cmd:cmd,payload:payload||{}};
  const r=await fetch("/cmd",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  STATE=await r.json();
  render();
}

fetchState();
// Command buttons (Undo/Next)
function bindClick(id, fn){
  const el = document.getElementById(id);
  if(!el) return;
  el.addEventListener('click', (e)=>{ e.preventDefault(); e.stopPropagation(); fn(); });
}
bindClick('btnUndo', ()=>sendCmd('undo', {}));
bindClick('btnNext', ()=>nextStep());
// legacy ids (older builds)
bindClick('btnUndoPM', ()=>sendCmd('undo', {}));
bindClick('btnNextPM', ()=>nextStep());
function _mkBackCard(){
  const d=document.createElement('div');
  d.className='stackMini back';
  d.style.position='absolute';
  d.style.left='0'; d.style.top='0';
  return d;
}

function renderMiniStack(container, cns){
  container.innerHTML='';
  const wrap=document.createElement('div');
  wrap.className='stackMini';
  const last = (cns||[]).slice(-3);
  // draw from back to front
  for (let i=0;i<Math.max(1,last.length);i++){
    const cn = last[i] ?? '?';
    const off = i*4;
    if (!isCardNo(cn)){
      const back=document.createElement('div');
      back.className='back';
      back.style.left = `${off}px`;
      back.style.top = `${off}px`;
      wrap.appendChild(back);
    } else {
      const im=document.createElement('img');
      im.src = `/img?cn=${encodeURIComponent(cn)}`;
      im.style.left = `${off}px`;
      im.style.top = `${off}px`;
      wrap.appendChild(im);
    }
  }
  container.appendChild(wrap);
}

function showZone(title, cns){
  if (!matZoneOverlay || !matZoneGrid) return;
  matZoneTitle.textContent = title;
  matZoneGrid.innerHTML='';
  const list = (cns||[]);
  if (list.length===0){
    const d=document.createElement('div');
    d.style.opacity='0.8';
    d.textContent='(empty)';
    matZoneGrid.appendChild(d);
  } else {
    for (const cn of list){
      const card=document.createElement('div');
      card.className='card';
      card.style.width='110px';
      card.style.height='154px';
      card.style.borderRadius='12px';
      card.style.overflow='hidden';
      card.style.boxShadow='0 2px 8px rgba(0,0,0,0.15)';
      card.style.background='#fff';
      if (isCardNo(cn)){
        const im=document.createElement('img');
        im.src=`/img?cn=${encodeURIComponent(cn)}`;
        im.style.width='110px';
        im.style.height='154px';
        im.style.objectFit='cover';
        card.appendChild(im);
      } else {
        const back=document.createElement('div');
        back.className='stackMini back';
        back.style.position='static';
        back.style.width='110px';
        back.style.height='154px';
        back.style.borderRadius='12px';
        back.textContent='?';
        back.style.display='flex';
        back.style.alignItems='center';
        back.style.justifyContent='center';
        back.style.fontWeight='900';
        back.style.fontSize='32px';
        card.appendChild(back);
      }
      matZoneGrid.appendChild(card);
    }
  }
  matZoneOverlay.style.display='flex';
}



})();
</script>
</body></html>
"""


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
        self.root = root
        self.outdir = root / "sim_out"
        self.cards_db = load_cards_db(root, compiled_path=compiled, tokv1_path=tokv1)
        self.img = ImageLocator(root)
        self.ui_code = str(code)
        self.deck_code = str(deck_code)
        self.gs, self.rng = new_game(root, self.deck_code, seed=seed, debug=debug)
        self.save_trace()

    def save_trace(self):
        self.outdir.mkdir(parents=True, exist_ok=True)
        _write_text(self.outdir / "ui_trace.txt", "\n".join(self.gs.log) + ("\n" if self.gs.log else ""))

    def _cn2type(self) -> Dict[str, str]:
        cns: set = set()
        try:
            cns.update(self.gs.hand or [])
            cns.update(self.gs.green_room or [])
            cns.update(self.gs.set_zone or [])
            cns.update(self.gs.resolve_zone or [])
        except Exception:
            pass
        try:
            for _pos, v in (self.gs.stage or {}).items():
                if v and getattr(v, "cardnumber", None):
                    cns.add(v.cardnumber)
        except Exception:
            pass

        out: Dict[str, str] = {}
        for cn in sorted(cns):
            ci = _get_card(self.cards_db, cn)
            if ci and getattr(ci, "type", None):
                out[cn] = str(ci.type)
        return out

    def _all_cardnumbers_in_state(self) -> List[str]:
        """Collect all cardnumbers referenced by the current game state.

        Used by the UI to build cn->label/name maps. Must never throw.
        """
        gs = getattr(self, "gs", None)
        if gs is None:
            return []
        cns: set[str] = set()

        def _add_from_iter(items: Any):
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

        # Common zones
        _add_from_iter(getattr(gs, "hand", None))
        _add_from_iter(getattr(gs, "green_room", None))
        _add_from_iter(getattr(gs, "set_zone", None))
        _add_from_iter(getattr(gs, "resolve_zone", None))
        _add_from_iter(getattr(gs, "deck", None))

        # Stage slots can be dict-like
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                _add_from_iter(st.values())
        except Exception:
            pass

        # Pending prompts may include candidates / cards
        try:
            for item in getattr(gs, "pending", []) or []:
                if not isinstance(item, dict):
                    continue
                _add_from_iter(item.get("candidates"))
                _add_from_iter(item.get("cards"))
                _add_from_iter(item.get("shown"))
        except Exception:
            pass

        return sorted(cns)

    def _cn2name(self) -> Dict[str, str]:
        cns: set = set()
        try:
            cns.update(self.gs.hand or [])
            cns.update(self.gs.green_room or [])
            cns.update(self.gs.set_zone or [])
            cns.update(self.gs.resolve_zone or [])
        except Exception:
            pass
        try:
            for _pos, v in (self.gs.stage or {}).items():
                if v and getattr(v, "cardnumber", None):
                    cns.add(v.cardnumber)
        except Exception:
            pass

        out: Dict[str, str] = {}
        for cn in sorted(cns):
            ci = _get_card(self.cards_db, cn)
            if ci and ci.name:
                out[cn] = ci.name
        return out

    def _cn2label(self) -> Dict[str, str]:
        """UI label policy:
        - LIVE card: "<name>"
        - MEMBER card: "<exp>/<cost>/<name>" (exp = token before first '-')
        """
        cns: set[str] = set()
        for cn in self._all_cardnumbers_in_state():
            cns.add(cn)
        # Also include candidate options from pending prompts so popups can show names.
        for p in self.gs.pending:
            for opt in (p.get("options") or []):
                if isinstance(opt, str) and "PL!" in opt:
                    cns.add(opt)

        def _exp_token(cardnumber: str) -> str:
            try:
                s = cardnumber.split("!", 1)[1]
                return s.split("-", 1)[0]
            except Exception:
                return ""

        out: Dict[str, str] = {}
        cn2type = self._cn2type()
        for cn in sorted(cns):
            ci = _get_card(self.cards_db, cn)
            if not ci or not ci.name:
                continue
            t = cn2type.get(cn, "")
            if t == "LIVE":
                out[cn] = ci.name
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
        if getattr(self.gs, 'banner_text', '') and (now - getattr(self.gs, 'banner_ts', 0.0) <= getattr(self.gs, 'banner_ttl', 0.0)):
            banner = {"text": self.gs.banner_text}
        return {
            "root": self.gs.root,
            "code": self.ui_code,
            "deck_code": self.deck_code,
            "seed": self.gs.seed,
            "debug": self.gs.debug,
            "turn": self.gs.turn,
            "phase": self.gs.phase,
            "deck": self.gs.deck if self.gs.debug else ["?"] * len(self.gs.deck),
            "hand": self.gs.hand,
            "energy_active": self.gs.energy_active,
            "energy_wait": self.gs.energy_wait,
            "stage": {k: (asdict(v) if v else None) for k, v in self.gs.stage.items()},
            "green_room": self.gs.green_room,
            "set_zone": self.gs.set_zone,
            "resolve_zone": self.gs.resolve_zone,
            "pending": self.gs.pending,
            "cn2name": self._cn2name(),
            "cn2label": self._cn2label(),
            "cn2type": self._cn2type(),
            "stage_detail": {k: ({
                "cardnumber": v.cardnumber,
                "name": (_get_card(self.cards_db, v.cardnumber).name if _get_card(self.cards_db, v.cardnumber) else ""),
                "type": (_get_card(self.cards_db, v.cardnumber).type if _get_card(self.cards_db, v.cardnumber) else ""),
                "has_sac": _has_sacrifice_ability(_get_card(self.cards_db, v.cardnumber)),
                "can_activate": can_activate(_get_card(self.cards_db, v.cardnumber)),
            } if v else None) for k, v in self.gs.stage.items()},
            "log": self.gs.log,
            "banner": banner,
        }

    def cmd(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        mutating = name in {"play", "set", "yell", "attempt", "ack", "end_turn", "toggle_debug", "activate_to_green", "resolve_pending", "next"}
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
            cmd_resolve_pending(self.gs, self.cards_db, int(payload.get("idx", -1)), str(payload.get("choice", "")))
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
        elif name == "peek":
            n = _safe_int(payload.get("n", 5), 5)
            if not self.gs.debug:
                self.gs.log.append("[PEEK] enable debug first")
            else:
                top = self.gs.deck[:max(0, n)]
                self.gs.log.append("[PEEK] top: " + ", ".join(top))
        else:
            self.gs.log.append(f"[ERR] unknown cmd: {name}")

        self.save_trace()
        return self.state_json()


class Handler(BaseHTTPRequestHandler):
    app: App = None  # type: ignore

    def _send(self, code: int, content: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if u.path == "/favicon.ico":
            self._send(204, b"", "image/x-icon")
            return
        if u.path == "/playmat":
            # Serve playmat.jpg from loveca root (next to scripts) if present.
            candidates = []
            try:
                here = Path(__file__).resolve()
                candidates.append(here.parents[1] / "playmat.jpg")  # loveca/playmat.jpg
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
                if str(p).lower().endswith(".jpg") or str(p).lower().endswith(".jpeg"):
                    ctype = "image/jpeg"
                self._send(200, p.read_bytes(), ctype)
            else:
                self._send(404, b"", "text/plain")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self):
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

