# BUILD_TAG = "update_dependency_bootstrap_20260721a"
"""Loveca local web UI and HTTP routing."""
from __future__ import annotations

import html
import json
import threading
import mimetypes
import os
import platform
import re
import subprocess
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse

from .core import *

CSS = """
:root {
  color-scheme: dark;
  --bg: #111318;
  --panel: #1b1f27;
  --panel2: #242a34;
  --text: #f4f6fa;
  --muted: #aeb7c5;
  --line: #3a4352;
  --accent: #f07eb0;
  --ok: #74d89b;
  --warn: #f1c86d;
  --bad: #ef7777;
}
* { box-sizing: border-box; }
html {
  --loveca-app-scale: 1;
  --loveca-layout-width: 1920px;
  --loveca-layout-height: 1200px;
  background: var(--bg);
}
body {
  margin: 0;
  font-size: 16px;
  min-width: 0;
  overflow: auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
}
#lovecaScaleRoot {
  width: var(--loveca-layout-width);
  min-height: var(--loveca-layout-height);
  zoom: var(--loveca-app-scale);
}
@supports not (zoom: 1) {
  #lovecaScaleRoot {
    transform: scale(var(--loveca-app-scale));
    transform-origin: top left;
  }
}
header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
header h1 { font-size: 21px; margin: 0; }
header .tag { color: var(--muted); font-size: 14px; }
main {
  width: 100%;
  max-width: min(1600px, calc(var(--loveca-layout-width) - 48px));
  margin: 0 auto;
  padding: 24px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
  gap: 16px;
}
.menu-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}
.menu-grid .card {
  min-height: 205px;
  padding: 22px;
}
.menu-grid .card h2 { font-size: 21px; }
.menu-grid .card p { font-size: 16px; min-height: 58px; }
.card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px;
  min-height: 180px;
}
.card h2 { margin: 0 0 8px; font-size: 18px; }
.card p { color: var(--muted); min-height: 48px; line-height: 1.55; }
button, .button {
  border: 0;
  border-radius: 9px;
  padding: 10px 14px;
  background: var(--accent);
  color: #1b1016;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}
button.secondary, .button.secondary {
  background: var(--panel2);
  color: var(--text);
  border: 1px solid var(--line);
}
button:disabled { opacity: .5; cursor: not-allowed; }
input, select {
  width: 100%;
  background: #10141a;
  color: var(--text);
  border: 1px solid var(--line);
  padding: 10px 11px;
  border-radius: 8px;
}
label { display: block; color: var(--muted); margin: 12px 0 6px; font-size:15px; }
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #0d1015;
  padding: 12px;
  border-radius: 9px;
  max-height: 430px;
  overflow: auto;
}
.status { margin-top: 12px; color: var(--muted); font-size:15px; line-height:1.45; }
.ok { color: var(--ok); }
.bad { color: var(--bad); }
.warn { color: var(--warn); }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 9px; border-bottom: 1px solid var(--line); }
nav a { color: var(--text); margin-left: 14px; font-size:15px; }
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 18px; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.deck-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 18px;
}
.deck-card {
  position: relative;
  background: var(--panel2);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px;
  cursor: pointer;
  transition: transform .12s ease, border-color .12s ease;
}
.deck-card:hover { transform: translateY(-2px); border-color: var(--accent); }
.deck-card-image-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 451 / 630;
  border-radius: 8px;
  overflow: hidden;
  background: #0d1015;
}
.deck-card-image { width: 100%; height: 100%; object-fit: contain; display: block; }
.deck-card-placeholder {
  display: none;
  width: 100%; height: 100%; align-items: center; justify-content: center;
  text-align: center; color: var(--muted); padding: 10px; overflow-wrap: anywhere;
}
.deck-count-badge {
  position: absolute; top: 6px; right: 6px; z-index: 2;
  min-width: 34px; height: 34px; padding: 0 8px;
  border-radius: 18px; display: flex; align-items: center; justify-content: center;
  background: rgba(10,12,17,.92); color: white; border: 2px solid var(--accent);
  font-weight: 800; font-size: 17px;
}
.deck-card-title { font-weight: 700; margin-top: 9px; line-height: 1.35; min-height: 2.7em; }
.deck-card-number { color: var(--muted); font-size: 13px; overflow-wrap: anywhere; }
.modal-backdrop {
  position: fixed; inset: 0; display: none; align-items: center; justify-content: center;
  background: rgba(0,0,0,.78); z-index: 1000; padding: 24px;
}
.modal-backdrop.open { display: flex; }
.card-modal {
  width: min(920px, calc(var(--loveca-layout-width) * .96));
  max-height: calc(var(--loveca-layout-height) * .92);
  overflow: auto;
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 18px;
}
.card-modal-grid { display: grid; grid-template-columns: minmax(220px, 340px) 1fr; gap: 22px; }
.card-modal img { width: 100%; max-height: calc(var(--loveca-layout-height) * .68); object-fit: contain; background:#0d1015; border-radius:9px; }
.card-detail-table th { width: 105px; color: var(--muted); vertical-align: top; }
.card-effect { white-space: pre-wrap; line-height: 1.6; background:#0d1015; padding:12px; border-radius:8px; }
@media (max-width: 680px) { .card-modal-grid { grid-template-columns: 1fr; } }

@media (max-width: 640px) { .row { grid-template-columns: 1fr; } }
.simulator-shell {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: var(--bg);
  display: grid;
  grid-template-rows: auto 1fr;
}
.simulator-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 14px;
  border-bottom: 1px solid var(--line);
  background: var(--panel);
}
.simulator-toolbar .spacer { flex: 1; }
.simulator-frame {
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}
 :root {
  --loveca-user-scale: 1;
  --loveca-control-height: 38px;
  --loveca-control-pad-y: 9px;
  --loveca-control-pad-x: 14px;
  --loveca-control-font-size: 14px;
  --loveca-control-radius: 8px;
  --loveca-control-min-width: 42px;
  --loveca-spinner-width: 88px;
  --loveca-stepper-width: 28px;
}
body[data-control-size="large"] {
  --loveca-control-height: 48px;
  --loveca-control-pad-y: 12px;
  --loveca-control-pad-x: 19px;
  --loveca-control-font-size: 17px;
  --loveca-control-radius: 10px;
  --loveca-control-min-width: 54px;
  --loveca-spinner-width: 116px;
  --loveca-stepper-width: 38px;
}
body[data-control-size="compact"] {
  --loveca-control-height: 32px;
  --loveca-control-pad-y: 6px;
  --loveca-control-pad-x: 10px;
  --loveca-control-font-size: 13px;
  --loveca-control-radius: 7px;
  --loveca-control-min-width: 34px;
  --loveca-spinner-width: 76px;
  --loveca-stepper-width: 24px;
}
button, .button, input, select {
  min-height:var(--loveca-control-height);
  font-size:var(--loveca-control-font-size);
  border-radius:var(--loveca-control-radius);
}
button, .button {
  min-width:var(--loveca-control-min-width);
  padding:var(--loveca-control-pad-y) var(--loveca-control-pad-x);
}
input, select { padding:var(--loveca-control-pad-y) 11px; }
select option { font-size:15px; }
/* macOSなどではネイティブselectの展開メニューがOS描画となり、
   optionのfont-sizeが反映されないため、検索条件だけカスタム表示にする。 */
.custom-select-native {
  position:absolute !important;
  width:1px !important;
  height:1px !important;
  opacity:0 !important;
  pointer-events:none !important;
}
.custom-select-wrap { position:relative; width:100%; }
.custom-select-wrap[data-select-id="search_product"] .custom-select-menu {
  right:auto;
  width:min(720px,calc(var(--loveca-layout-width) - 80px));
  min-width:max(100%,560px);
}
.custom-select-button {
  width:100%;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  text-align:left;
  background:#10141a;
  color:var(--text);
  border:1px solid var(--line);
  font-weight:500;
}
.custom-select-button::after { content:"▾"; flex:0 0 auto; font-size:1.05em; }
.custom-select-wrap.open .custom-select-button::after { content:"▴"; }
.custom-select-menu {
  position:absolute;
  left:0; right:0; top:calc(100% + 4px);
  z-index:22000;
  max-height:420px;
  overflow:auto;
  padding:6px;
  border:1px solid var(--line);
  border-radius:10px;
  background:#e4e5e8;
  color:#17191d;
  box-shadow:0 14px 40px rgba(0,0,0,.4);
}
.custom-select-menu[hidden] { display:none; }
.custom-select-option {
  width:100%;
  min-height:38px;
  padding:8px 10px;
  border:0;
  border-bottom:1px solid rgba(30,40,58,.18);
  border-radius:0;
  background:transparent;
  color:inherit;
  font-size:15px;
  font-weight:500;
  text-align:left;
  display:flex;
  align-items:center;
  gap:8px;
}
.custom-select-option:last-child { border-bottom:0; }
.custom-select-option:hover,
.custom-select-option:focus-visible { background:rgba(30,40,58,.12); outline:none; }
.custom-select-wrap[data-select-id="search_product"] .custom-select-option {
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}
.custom-select-option.selected::before { content:"✓"; width:16px; font-weight:800; }
.custom-select-option:not(.selected)::before { content:""; width:16px; }
body[data-control-size="large"] .custom-select-option { min-height:46px; font-size:17px; padding:10px 12px; }
body[data-control-size="compact"] .custom-select-option { min-height:34px; font-size:14px; padding:7px 9px; }
input[type="number"] {
  min-width:0;
  width:100%;
  appearance:textfield;
  -moz-appearance:textfield;
}
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance:none;
  margin:0;
}
.number-stepper {
  display:grid;
  grid-template-columns:minmax(0,1fr) var(--loveca-stepper-width);
  width:var(--loveca-spinner-width);
  min-width:var(--loveca-spinner-width);
  height:var(--loveca-control-height);
  border:1px solid var(--line);
  border-radius:var(--loveca-control-radius);
  overflow:hidden;
  background:#10141a;
}
.number-stepper input[type="number"] {
  height:100%;
  min-height:0;
  border:0;
  border-radius:0;
  padding:0 8px;
  background:transparent;
}
.number-stepper-buttons {
  display:grid;
  grid-template-rows:1fr 1fr;
  border-left:1px solid var(--line);
}
.number-stepper-button {
  min-width:0;
  min-height:0;
  width:100%;
  height:100%;
  padding:0;
  border:0;
  border-radius:0;
  font-size:calc(var(--loveca-control-font-size) * .9);
  line-height:1;
  background:var(--panel2);
  color:var(--text);
}
.number-stepper-button:first-child { border-bottom:1px solid var(--line); }
.number-stepper-button:hover { filter:brightness(1.16); }
.quick-settings-overlay[hidden] { display:none; }
.quick-settings-overlay {
  position:fixed; inset:0; z-index:30000; display:flex; align-items:flex-start; justify-content:flex-end;
  padding:72px 22px 22px; background:rgba(0,0,0,.46);
}
.quick-settings-dialog {
  width:min(420px,calc(100vw - 44px)); border:1px solid var(--line); border-radius:14px;
  background:var(--panel); box-shadow:0 24px 80px rgba(0,0,0,.55); padding:18px;
}
.quick-settings-dialog h2 { margin:0 0 12px; }
.quick-settings-row { margin:14px 0; }
.quick-settings-actions { display:flex;gap:8px;justify-content:flex-end;margin-top:16px; }
"""


def page(title: str, body: str) -> bytes:
    doc = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div id="lovecaScaleRoot">
<header>
  <h1>Loveca Application</h1>
  <div>
    <span class="tag">{html.escape(BUILD_TAG)}</span>
    <nav><a href="/">メニュー</a><a href="/remote">リモート対戦</a><a href="/decks">デッキ</a><a href="/update">更新</a><a href="/logs">ログ</a><button type="button" class="secondary" style="margin-left:14px" onclick="openQuickSettings()">簡易設定</button><a href="/diagnostics">診断</a><button type="button" style="background:var(--bad);color:white;margin-left:8px" onclick="shutdownLovecaApp()">アプリ終了</button></nav>
  </div>
</header>
<main>{body}</main>
</div>
<div id="quickSettingsOverlay" class="quick-settings-overlay" hidden onclick="if(event.target===this)closeQuickSettings()">
  <section class="quick-settings-dialog" role="dialog" aria-modal="true" aria-labelledby="quickSettingsTitle">
    <h2 id="quickSettingsTitle">簡易設定</h2>
    <div class="quick-settings-row"><label for="quick_ui_scale">画面表示サイズ</label><select id="quick_ui_scale"><option value="100">100%</option><option value="110">110%</option><option value="120">120%</option></select></div>
    <div class="quick-settings-row"><label for="quick_control_size">枠・ボタン・数値入力の操作サイズ</label><select id="quick_control_size"><option value="compact">小さめ</option><option value="standard">標準</option><option value="large">大きめ</option></select></div>
    <div id="quickSettingsStatus" class="status"></div>
    <div class="quick-settings-actions"><a class="button secondary" href="/settings">詳細設定</a><button type="button" class="secondary" onclick="closeQuickSettings()">閉じる</button></div>
  </section>
</div>
<script>
const LOVECA_DESIGN_WIDTH = 1920;
const LOVECA_DESIGN_HEIGHT = 1200;
const LOVECA_MIN_SUPPORTED_WIDTH = 1440;
const LOVECA_MIN_SUPPORTED_HEIGHT = 900;
const LOVECA_MIN_SCALE = 0.55;
const LOVECA_MAX_SCALE = 1.15;

function updateLovecaViewportScale() {{
  const viewportWidth=Math.max(320,Number(window.innerWidth)||LOVECA_DESIGN_WIDTH);
  const viewportHeight=Math.max(320,Number(window.innerHeight)||LOVECA_DESIGN_HEIGHT);
  const widthScale=viewportWidth/LOVECA_DESIGN_WIDTH;
  const heightScale=viewportHeight/LOVECA_DESIGN_HEIGHT;
  const userScale=Math.max(.8,Math.min(1.25,Number(document.documentElement.dataset.userScale||1)));
  const scale=Math.min(
    LOVECA_MAX_SCALE*userScale,
    Math.max(LOVECA_MIN_SCALE,Math.min(widthScale,heightScale)*userScale)
  );
  const layoutWidth=viewportWidth/scale;
  const layoutHeight=viewportHeight/scale;
  const root=document.getElementById("lovecaScaleRoot");

  document.documentElement.style.setProperty("--loveca-app-scale",String(scale));
  document.documentElement.style.setProperty("--loveca-layout-width",layoutWidth+"px");
  document.documentElement.style.setProperty("--loveca-layout-height",layoutHeight+"px");

  if(root) {{
    root.style.width=layoutWidth+"px";
    root.style.minHeight=layoutHeight+"px";
  }}

  window.dispatchEvent(new CustomEvent("loveca:viewport-scale",{{
    detail:{{scale,layoutWidth,layoutHeight}}
  }}));
}}

let lovecaViewportResizeFrame=0;
function scheduleLovecaViewportScale() {{
  if(lovecaViewportResizeFrame) cancelAnimationFrame(lovecaViewportResizeFrame);
  lovecaViewportResizeFrame=requestAnimationFrame(()=>{{
    lovecaViewportResizeFrame=0;
    updateLovecaViewportScale();
  }});
}}

updateLovecaViewportScale();
window.addEventListener("resize",scheduleLovecaViewportScale,{{passive:true}});
window.addEventListener("orientationchange",scheduleLovecaViewportScale,{{passive:true}});

// Keep the launcher process tied to this application window. Internal page
// navigation briefly unloads the page, so the server waits before shutting
// down and cancels that shutdown as soon as the next page becomes active.
let lovecaWindowClosing=false;
let lovecaInternalNavigation=false;
function markLovecaInternalNavigation() {{ lovecaInternalNavigation=true; }}
document.addEventListener('click',(event)=>{{
  const anchor=event.target && event.target.closest ? event.target.closest('a[href]') : null;
  if(!anchor) return;
  const url=new URL(anchor.href,location.href);
  if(url.origin===location.origin) markLovecaInternalNavigation();
}},{{capture:true}});
document.addEventListener('submit',(event)=>{{
  const form=event.target;
  if(!form || !form.action) return;
  const url=new URL(form.action,location.href);
  if(url.origin===location.origin) markLovecaInternalNavigation();
}},{{capture:true}});
const lovecaWindowHeartbeat=()=>{{
  if(lovecaWindowClosing) return;
  fetch('/api/app/window-heartbeat',{{method:'POST',keepalive:true}}).catch(()=>{{}});
}};
lovecaWindowHeartbeat();
const lovecaHeartbeatTimer=setInterval(lovecaWindowHeartbeat,1000);
window.addEventListener('pagehide',()=>{{
  if(lovecaInternalNavigation) return;
  lovecaWindowClosing=true;
  clearInterval(lovecaHeartbeatTimer);
  try {{ navigator.sendBeacon('/api/app/window-closed',''); }} catch(_e) {{}}
}},{{capture:true}});

function applyQuickSettings(settings) {{
  const percent=Math.max(100,Math.min(120,Number(settings.ui_scale_percent)||100));
  const control=["compact","standard","large"].includes(settings.control_size)?settings.control_size:"standard";
  document.documentElement.dataset.userScale=String(percent/100);
  document.body.dataset.controlSize=control;
  const a=document.getElementById("quick_ui_scale"); if(a) a.value=String(percent);
  const b=document.getElementById("quick_control_size"); if(b) b.value=control;
  updateLovecaViewportScale();
}}
async function loadQuickSettings() {{
  try {{ const r=await fetch("/api/settings/ui",{{cache:"no-store"}}); applyQuickSettings(await r.json()); }}
  catch(error){{ console.warn("quick settings load failed",error); }}
}}
async function saveQuickSettings() {{
  const status=document.getElementById("quickSettingsStatus");
  const payload={{ui_scale_percent:Number(quick_ui_scale.value)||100,control_size:quick_control_size.value||"standard"}};
  applyQuickSettings(payload); if(status) status.textContent="保存中...";
  try {{ const r=await fetch("/api/settings/ui",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify(payload)}}); const d=await r.json(); if(!r.ok) throw new Error(d.message||"保存に失敗しました"); applyQuickSettings(d); if(status) status.textContent="保存しました"; }}
  catch(error){{ if(status) status.textContent=String(error); }}
}}
function openQuickSettings(){{ quickSettingsOverlay.hidden=false; }}
function closeQuickSettings(){{ quickSettingsOverlay.hidden=true; }}
document.addEventListener("change",event=>{{ if(event.target && (event.target.id==="quick_ui_scale" || event.target.id==="quick_control_size")) saveQuickSettings(); }});
document.addEventListener("keydown",event=>{{ if(event.key==="Escape") closeQuickSettings(); }});
function enhanceNumberInputs(root=document) {{
  for(const input of root.querySelectorAll('input[type="number"]')) {{
    if(input.closest('.number-stepper')) continue;
    const wrapper=document.createElement('span');
    wrapper.className='number-stepper';
    input.parentNode.insertBefore(wrapper,input);
    wrapper.appendChild(input);
    const buttons=document.createElement('span');
    buttons.className='number-stepper-buttons';
    buttons.innerHTML='<button type="button" class="number-stepper-button" data-step="1" aria-label="数値を増やす">▲</button><button type="button" class="number-stepper-button" data-step="-1" aria-label="数値を減らす">▼</button>';
    wrapper.appendChild(buttons);
  }}
}}
document.addEventListener('click',event=>{{
  const button=event.target.closest('.number-stepper-button');
  if(!button) return;
  const input=button.closest('.number-stepper')?.querySelector('input[type="number"]');
  if(!input) return;
  const direction=Number(button.dataset.step)||1;
  direction>0 ? input.stepUp() : input.stepDown();
  input.dispatchEvent(new Event('input',{{bubbles:true}}));
  input.dispatchEvent(new Event('change',{{bubbles:true}}));
}});
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>enhanceNumberInputs(),{{once:true}});
else enhanceNumberInputs();
loadQuickSettings();

async function shutdownLovecaApp() {{
  if(!confirm('Loveca Applicationを終了しますか？\\n起動中のシミュレータも終了します。')) return;
  try {{
    const res=await fetch('/api/app/shutdown',{{method:'POST'}});
    const data=await res.json();
    document.body.innerHTML='<main><section class="panel"><h2>アプリを終了しました</h2><p>'+String(data.message||'ウインドウを閉じます。')+'</p></section></main>';
    setTimeout(()=>{{
      try {{
        window.open('', '_self');
        window.close();
      }} catch(_closeError) {{}}
    }},150);
  }} catch(e) {{
    document.body.innerHTML='<main><section class="panel"><h2>アプリを終了しました</h2><p>ウインドウを閉じます。</p></section></main>';
    setTimeout(()=>{{
      try {{
        window.open('', '_self');
        window.close();
      }} catch(_closeError) {{}}
    }},150);
  }}
}}
</script>
</body>
</html>"""
    return doc.encode("utf-8")


def close_browser_tabs_for_urls_later(
    urls: list[str],
    delay: float = 0.4,
) -> None:
    """Best-effort close of simulator/public browser tabs on macOS."""
    if platform.system() != "Darwin":
        return

    needles: list[str] = []
    for raw_url in urls:
        value = str(raw_url or "").strip()
        if not value:
            continue
        parsed = urlparse(value)
        if parsed.netloc:
            if parsed.path and parsed.path != "/":
                needles.append(parsed.netloc + parsed.path.rstrip("/"))
            needles.append(parsed.netloc)
        else:
            needles.append(value.rstrip("/"))

    needles = sorted({item for item in needles if item}, key=len, reverse=True)
    if not needles:
        return

    conditions = " or ".join(
        'u contains "{}"'.format(item.replace('"', '\\"'))
        for item in needles
    )
    apple_script = """
delay {delay}
tell application "System Events"
    set runningApps to name of every application process
end tell

if runningApps contains "Google Chrome" then
    tell application "Google Chrome"
        repeat with w in windows
            set tabsToClose to {{}}
            repeat with t in tabs of w
                try
                    set u to URL of t
                    if {conditions} then set end of tabsToClose to t
                end try
            end repeat
            repeat with t in tabsToClose
                try
                    close t
                end try
            end repeat
        end repeat
    end tell
end if

if runningApps contains "Safari" then
    tell application "Safari"
        repeat with w in windows
            set tabsToClose to {{}}
            repeat with t in tabs of w
                try
                    set u to URL of t
                    if {conditions} then set end of tabsToClose to t
                end try
            end repeat
            repeat with t in tabsToClose
                try
                    close t
                end try
            end repeat
        end repeat
    end tell
end if
""".format(delay=delay, conditions=conditions)
    try:
        subprocess.Popen(
            ["osascript", "-e", apple_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def close_launcher_browser_tabs_later(port: int, delay: float = 0.8) -> None:
    """Best-effort close of tabs showing this local launcher on macOS."""
    if platform.system() != "Darwin":
        return

    target_a = "127.0.0.1:{}".format(port)
    target_b = "localhost:{}".format(port)
    apple_script = """
delay {delay}
tell application "System Events"
    set runningApps to name of every application process
end tell

if runningApps contains "Google Chrome" then
    tell application "Google Chrome"
        repeat with w in windows
            repeat with t in tabs of w
                try
                    set u to URL of t
                    if u contains "{target_a}" or u contains "{target_b}" then
                        close t
                    end if
                end try
            end repeat
        end repeat
    end tell
end if

if runningApps contains "Safari" then
    tell application "Safari"
        repeat with w in windows
            repeat with t in tabs of w
                try
                    set u to URL of t
                    if u contains "{target_a}" or u contains "{target_b}" then
                        close t
                    end if
                end try
            end repeat
        end repeat
    end tell
end if
""".format(
        delay=delay,
        target_a=target_a,
        target_b=target_b,
    )
    try:
        subprocess.Popen(
            ["osascript", "-e", apple_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


class Handler(BaseHTTPRequestHandler):
    server_version = "LovecaLauncher/1.0"

    @property
    def app(self) -> AppState:
        return self.server.app_state  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[HTTP] {self.address_string()} - {format % args}")

    def send_html(self, payload: bytes, status: int = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(payload)

    def send_file(self, path: Path) -> None:
        try:
            payload = path.read_bytes()
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "public, max-age=3600")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(payload)

    def send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(payload)

    def read_form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        parsed = parse_qs(raw)
        return {key: values[0] for key, values in parsed.items() if values}

    def do_HEAD(self) -> None:
        self._head_only = True
        try:
            self.do_GET()
        finally:
            self._head_only = False

    def do_GET(self) -> None:
        self.server.note_launcher_activity()
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        if path == "/texticon":
            token = query.get("token", [""])[0]
            icon_path = self.app.resolve_texticon(token)
            if icon_path is None:
                self.send_error(404, "Text icon not found")
                return
            self.send_file(icon_path)
            return

        if path == "/api/remote/session":
            relative = (query.get("path") or [""])[0]
            candidate = (self.app.root / relative).resolve()
            session_root = self.app.path(SESSION_DIR).resolve()
            try:
                candidate.relative_to(session_root)
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid session path")
                return
            if not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.send_file(candidate)
            return

        if path == "/api/settings/ui":
            settings = self.app.load_settings()
            self.send_json({"ui_scale_percent": int(settings.get("ui_scale_percent") or 100), "control_size": str(settings.get("control_size") or "standard")})
            return

        if path == "/card-image":
            card_no = (query.get("card_no") or [""])[0]
            variant_id = (query.get("variant_id") or [""])[0]
            rarity = (query.get("rarity") or [""])[0]
            image_path = self.app.find_card_image(card_no, variant_id=variant_id, rarity=rarity)
            if image_path is None:
                image_path = self.app.no_image_path()
            if image_path is None:
                self.send_error(HTTPStatus.NOT_FOUND)
            else:
                self.send_file(image_path)
        elif path == "/api/cards/search":
            try:
                limit = int((query.get("limit") or ["120"])[0])
            except ValueError:
                limit = 120
            def qv(name: str) -> str:
                return (query.get(name) or [""])[0]

            heart_keys = ("pink", "red", "yellow", "green", "blue", "purple", "all", "any")
            heart_ranges = {
                key: (qv(f"heart_{key}_min"), qv(f"heart_{key}_max"))
                for key in heart_keys
            }
            required_ranges = {
                key: (qv(f"required_{key}_min"), qv(f"required_{key}_max"))
                for key in heart_keys
            }
            blade_tokens = [
                token for token in qv("blade_heart_tokens").split(",") if token
            ]
            ability_types = [
                value for value in qv("ability_types").split(",") if value
            ]

            cards = self.app.search_cards(
                query=qv("q"),
                product=qv("product"),
                card_type=qv("card_type"),
                group=qv("group"),
                unit=qv("unit"),
                rarity=qv("rarity"),
                include_parallel=qv("include_parallel") in ("1", "true", "on", "yes"),
                include_prerelease=qv("include_prerelease") not in ("0", "false", "off", "no"),
                cost_min=qv("cost_min"),
                cost_max=qv("cost_max"),
                score_min=qv("score_min"),
                score_max=qv("score_max"),
                blade_min=qv("blade_min"),
                blade_max=qv("blade_max"),
                heart_ranges=heart_ranges,
                heart_mode=qv("heart_mode") or "and",
                required_heart_ranges=required_ranges,
                required_heart_mode=qv("required_heart_mode") or "and",
                blade_heart_tokens=blade_tokens,
                blade_heart_mode=qv("blade_heart_mode") or "or",
                ability_types=ability_types,
                effect=qv("effect"),
                limit=limit,
            )
            self.send_json({"cards": cards, "count": len(cards)})
        elif path == "/":
            self.send_html(page("Loveca", self.home_body()))
        elif path == "/manual":
            self.send_html(page("手動シミュレータ", self.manual_body()))
        elif path == "/remote":
            self.send_html(page("リモート対戦", self.remote_body()))
        elif path == "/simulator":
            self.send_html(self.simulator_page())
        elif path == "/decks":
            self.send_html(page("デッキ管理", self.decks_body()))
        elif path == "/decks/new":
            self.send_html(page("新規デッキ", self.deck_edit_body("", True)))
        elif path == "/decks/import":
            self.send_html(page("デッキコードから読込", self.deck_code_import_body()))
        elif path == "/decks/view":
            query = parse_qs(urlparse(self.path).query)
            deck_path = (query.get("path") or [""])[0]
            self.send_html(page("デッキ内容", self.deck_view_body(deck_path)))
        elif path == "/decks/edit":
            query = parse_qs(urlparse(self.path).query)
            deck_path = (query.get("path") or [""])[0]
            self.send_html(page("デッキ編集", self.deck_edit_body(deck_path, False)))
        elif path == "/update":
            self.send_html(page("データ更新", self.update_body()))
        elif path == "/logs":
            self.send_html(page("ログ管理", self.logs_body()))
        elif path == "/settings":
            self.send_html(page("設定", self.settings_body()))
        elif path == "/diagnostics":
            self.send_html(page("診断", self.diagnostics_body()))
        elif path == "/api/manual/window-status":
            self.send_json(self.app.manual_window_status())
        elif path == "/api/update/status":
            with self.app.lock:
                self.send_json(self.app.update_job.snapshot())
        else:
            self.send_html(page("Not Found", "<h2>ページが見つかりません。</h2>"), HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/app/window-closed":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.server.schedule_launcher_close_shutdown()
            return
        self.server.note_launcher_activity()
        if path == "/api/settings/ui":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                percent = int(raw.get("ui_scale_percent", 100))
                control = str(raw.get("control_size", "standard"))
                if percent not in (100, 110, 120): raise ValueError("画面表示サイズが不正です。")
                if control not in ("compact", "standard", "large"): raise ValueError("操作サイズが不正です。")
                self.app.save_settings({"ui_scale_percent": percent, "control_size": control})
                self.send_json({"ui_scale_percent": percent, "control_size": control})
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json({"ok": False, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if path == "/api/app/window-heartbeat":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
        elif path == "/api/manual/start":
            form = self.read_form()
            try:
                ok, message = self.app.start_manual(form.get("deck_path", ""))
                self.send_json({"ok": ok, "message": message}, HTTPStatus.OK if ok else HTTPStatus.CONFLICT)
            except ValueError as exc:
                self.send_json({"ok": False, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
        elif path == "/api/remote/start":
            form = self.read_form()
            try:
                key_length = int(form.get("key_length", "4"))
                deck_path = form.get("deck_path", "")
                if not deck_path:
                    raise ValueError("使用するデッキを選択してください。")
                record = self.app.create_remote_session(
                    player_id=form.get("player_id", ""),
                    key_length=key_length,
                    short_key=form.get("short_key") or None,
                )
                ok, message = self.app.start_manual(deck_path, remote_session=record)
                payload = {
                    "ok": ok,
                    "message": message,
                    "short_key": record.get("short_key", ""),
                    "session_label": record.get("session_label", ""),
                    "saved_to": record.get("saved_to", ""),
                    "session_record": record,
                }
                self.send_json(payload, HTTPStatus.OK if ok else HTTPStatus.CONFLICT)
            except ValueError as exc:
                self.send_json({"ok": False, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
        elif path == "/remote/verify":
            form = self.read_form()
            try:
                result = self.app.verify_remote_session_pair(
                    form.get("local_session", ""),
                    form.get("counterpart_json", ""),
                )
                result_class = "ok" if result.get("ok") else "bad"
                body = f"""
<section class="panel">
<h2>リモート対戦記録の照合結果</h2>
<p class="{result_class}">{html.escape(str(result.get('message') or ''))}</p>
<table>
<tr><th></th><th>ローカル</th><th>相手側</th></tr>
<tr><th>日付</th><td>{html.escape(result['local']['date'])}</td><td>{html.escape(result['counterpart']['date'])}</td></tr>
<tr><th>共有キー</th><td>{html.escape(result['local']['short_key'])}</td><td>{html.escape(result['counterpart']['short_key'])}</td></tr>
<tr><th>プレイヤー</th><td>{html.escape(result['local']['player_id'])}</td><td>{html.escape(result['counterpart']['player_id'])}</td></tr>
<tr><th>共有照合ID</th><td><code>{html.escape(result['local']['match_uid'])}</code></td><td><code>{html.escape(result['counterpart']['match_uid'])}</code></td></tr>
</table>
<a class="button secondary" href="/remote">リモート対戦画面へ戻る</a>
</section>
"""
                self.send_html(page("リモート対戦ログ照合", body), HTTPStatus.OK if result.get("ok") else HTTPStatus.CONFLICT)
            except ValueError as exc:
                self.send_html(page("照合エラー", f"<section class='panel'><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/remote'>戻る</a></section>"), HTTPStatus.BAD_REQUEST)
        elif path == "/api/manual/stop":
            state = self.app.manual_window_status()
            urls_to_close = [
                str(state.get("private_url") or ""),
                str(state.get("public_url") or ""),
            ]
            ok, message = self.app.stop_manual()
            self.send_json(
                {"ok": ok, "message": message},
                HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            if ok:
                close_browser_tabs_for_urls_later(urls_to_close)
        elif path == "/api/app/shutdown":
            ok, detail = self.app.stop_all_child_processes()
            server_port = int(self.server.server_address[1])
            self.send_json({
                "ok": ok,
                "message": "Loveca Applicationを終了しました。 " + detail,
            })
            close_launcher_browser_tabs_later(server_port)
            threading.Thread(
                target=self.server.force_shutdown_process,
                daemon=True,
            ).start()
        elif path == "/api/update/start":
            ok, message = self.app.start_update()
            self.send_json({"ok": ok, "message": message}, HTTPStatus.OK if ok else HTTPStatus.CONFLICT)
        elif path == "/api/update/startup-confirmed":
            ok, message = self.app.maybe_start_startup_update()
            self.send_json({"ok": ok, "message": message}, HTTPStatus.OK if ok else HTTPStatus.CONFLICT)
        elif path == "/decks/import/run":
            form = self.read_form()
            try:
                imported = self.app.import_deck_code(form.get("deck_code", ""))
                self.send_html(
                    page(
                        "デッキコード読込結果",
                        self.deck_code_import_result_body(imported),
                    )
                )
            except ValueError as exc:
                self.send_html(
                    page(
                        "デッキコード読込エラー",
                        self.deck_code_import_body(
                            deck_code=form.get("deck_code", ""),
                            error=str(exc),
                        ),
                    ),
                    HTTPStatus.BAD_REQUEST,
                )
        elif path == "/decks/import/save":
            form = self.read_form()
            try:
                record = self.app.save_imported_deck(
                    import_token=form.get("import_token", ""),
                    deck_code=form.get("deck_code", ""),
                    deck_name=form.get("deck_name", ""),
                    tags=form.get("tags", ""),
                )
                self.send_html(page("保存完了", """
<section class="panel">
<h2>デッキコードからデッキを保存しました</h2>
<p><strong>{}</strong></p>
<p>デッキコード：<code>{}</code></p>
<p>カード種類数：{} / 合計枚数：{}</p>
<a class="button" href="/decks/view?path={}">内容を確認</a>
<a class="button secondary" href="/decks">一覧へ</a>
</section>
""".format(
                    html.escape(record["name"]),
                    html.escape(record["code"]),
                    record["card_types"],
                    record["card_count"],
                    html.escape(record["path"], quote=True),
                )))
            except ValueError as exc:
                self.send_html(
                    page(
                        "保存エラー",
                        "<section class='panel'><p class='bad'>{}</p>"
                        "<a class='button secondary' href='/decks/import'>戻る</a></section>".format(
                            html.escape(str(exc))
                        ),
                    ),
                    HTTPStatus.BAD_REQUEST,
                )
        elif path == "/decks/save":
            form = self.read_form()
            try:
                record = self.app.save_deck(
                    deck_name=form.get("deck_name", ""),
                    tsv_text=form.get("tsv_text", ""),
                    existing_path=form.get("existing_path", ""),
                    tags=form.get("tags", ""),
                )
                start_after_save = form.get("start_after_save", "") == "1"
                start_result = ""
                if start_after_save:
                    ok, message = self.app.start_manual(record["path"])
                    result_class = "ok" if ok else "bad"
                    start_result = (
                        "<p class='" + result_class + "'>"
                        + html.escape(message)
                        + "</p>"
                    )
                self.send_html(page("保存完了", f"""
<section class="panel">
<h2>デッキを保存しました</h2>
<p><strong>{html.escape(record['name'])}</strong></p>
<p>カード種類数：{record['card_types']} / 合計枚数：{record['card_count']}</p>
<p class="{'ok' if record['composition']['valid'] else 'warn'}">
メンバー：{record['composition']['member']} / 48、
ライブ：{record['composition']['live']} / 12
{('' if record['composition']['other'] == 0 else f"、その他：{record['composition']['other']}")}
</p>
{start_result}
<a class="button" href="/decks/view?path={html.escape(record['path'], quote=True)}">内容を確認</a>
<a class="button secondary" href="/decks">一覧へ</a>
</section>
"""))
            except ValueError as exc:
                self.send_html(page("入力エラー", f"<section class='panel'><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/decks'>一覧へ</a></section>"), HTTPStatus.BAD_REQUEST)
        elif path == "/decks/delete":
            form = self.read_form()
            try:
                deleted = self.app.delete_deck(form.get("deck_path", ""))
                self.send_html(page("削除完了", f"<section class='panel'><h2>デッキを削除しました</h2><pre>{html.escape(deleted['deck'])}</pre><a class='button' href='/decks'>一覧へ</a></section>"))
            except ValueError as exc:
                self.send_html(page("削除エラー", f"<section class='panel'><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/decks'>一覧へ</a></section>"), HTTPStatus.BAD_REQUEST)
        elif path == "/decks/select":
            form = self.read_form()
            try:
                record = self.app.select_deck(form.get("deck_path", ""))
                self.send_html(page("デッキ選択", f"""
<section class="panel">
<h2>使用デッキを選択しました</h2>
<p><strong>{html.escape(record['name'])}</strong></p>
<pre>{html.escape(record['path'])}</pre>
<p class="status">このデッキを次回の対戦で使用するデッキに設定しました。</p>
<a class="button secondary" href="/decks">戻る</a>
<a class="button" href="/">メニューへ</a>
</section>
"""))
            except ValueError as exc:
                self.send_html(page("入力エラー", f"<section class='panel'><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/decks'>戻る</a></section>"), HTTPStatus.BAD_REQUEST)
        elif path == "/settings/save":
            form = self.read_form()
            try:
                player = safe_player_id(form.get("player_id", ""))
                key_length = int(form.get("remote_key_length", "4"))
                if key_length < 3 or key_length > 5:
                    raise ValueError("キー長は3〜5桁で指定してください。")
                auto_update = form.get("auto_update_on_startup", "") == "1"
                self.app.save_settings({
                    "player_id": player,
                    "remote_key_length": key_length,
                    "auto_update_on_startup": auto_update,
                })
                self.send_html(page("設定", "<section class='panel'><h2>設定を保存しました</h2><a class='button' href='/settings'>戻る</a></section>"))
            except ValueError as exc:
                self.send_html(page("入力エラー", f"<section class='panel'><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/settings'>戻る</a></section>"), HTTPStatus.BAD_REQUEST)
        elif path == "/remote/create":
            form = self.read_form()
            try:
                key_length = int(form.get("key_length", "4"))
                deck_path = form.get("deck_path", "")
                if not deck_path:
                    raise ValueError("使用するデッキを選択してください。")
                record = self.app.create_remote_session(
                    player_id=form.get("player_id", ""),
                    key_length=key_length,
                    short_key=form.get("short_key") or None,
                )
                ok, launch_message = self.app.start_manual(
                    deck_path,
                    remote_session=record,
                )
                result_class = "ok" if ok else "bad"
                body = """
<section class="panel">
<h2>リモート対戦キー</h2>
<p>相手へ伝えるキー：</p>
<div style="font-size:42px;font-weight:800;letter-spacing:.18em">{}</div>
<p>ログ識別子：</p>
<pre>{}</pre>
<p class="status">保存先：{}</p>
<p class="{}">{}</p>
<p class="status">リモート対戦ではシミュレータ本体と画面共有用パブリックウインドウを起動します。通常対戦から起動した場合、パブリックウインドウは開きません。</p>
<a class="button secondary" href="/remote">戻る</a>
</section>
""".format(
                    html.escape(record["short_key"]),
                    html.escape(record["session_label"]),
                    html.escape(record["saved_to"]),
                    result_class,
                    html.escape(launch_message),
                )
                self.send_html(
                    page("リモート対戦開始", body),
                    HTTPStatus.OK if ok else HTTPStatus.CONFLICT,
                )
            except (ValueError, OSError) as exc:
                error_body = (
                    "<section class='panel'><h2>開始できませんでした</h2>"
                    "<p class='bad'>" + html.escape(str(exc)) + "</p>"
                    "<a class='button secondary' href='/remote'>戻る</a></section>"
                )
                self.send_html(
                    page("入力エラー", error_body),
                    HTTPStatus.BAD_REQUEST,
                )
        else:
            self.send_json({"ok": False, "message": "unknown endpoint"}, HTTPStatus.NOT_FOUND)

    def simulator_page(self) -> bytes:
        state = self.app.manual_window_status()
        running = bool(state.get("running"))
        private_url = html.escape(str(state.get("private_url") or ""), quote=True)
        public_url = html.escape(str(state.get("public_url") or ""), quote=True)
        remote = bool(state.get("remote"))
        remote_key = html.escape(str(state.get("remote_key") or ""))
        deck_name = html.escape(str(state.get("deck_name") or ""))
        return_path = "/remote" if remote else "/manual"

        if not running:
            body = """
<section class="panel">
<h2>シミュレータは起動していません</h2>
<p class="status">{}</p>
<a class="button" href="{}">起動画面へ戻る</a>
</section>
""".format(
                html.escape(str(state.get("message") or "")),
                return_path,
            )
            return page("シミュレータ", body)

        public_button = ""
        if remote and public_url:
            public_button = (
                "<a class='button secondary' target='loveca_public' href='{}'>"
                "パブリック画面を表示</a>"
            ).format(public_url)

        key_html = ""
        if remote_key:
            key_html = "<strong>対戦キー: {}</strong>".format(remote_key)

        doc = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Loveca シミュレータ</title>
<style>{css}</style>
</head>
<body>
<div class="simulator-shell">
  <div class="simulator-toolbar">
    <strong>{deck}</strong>
    {key_html}
    <span class="spacer"></span>
    {public_button}
    <a class="button secondary" href="{return_path}">起動設定へ戻る</a>
    <button type="button" style="background:var(--bad);color:white" onclick="stopEmbeddedSimulator()">シミュレータを終了</button>
    <button type="button" style="background:var(--bad);color:white" onclick="shutdownLovecaApp()">アプリ終了</button>
  </div>
  <iframe class="simulator-frame" src="{private_url}" title="Loveca simulator"></iframe>
</div>
<script>
let lovecaSimulatorPageClosing=false;
const lovecaSimulatorHeartbeat=()=>{{
  if(lovecaSimulatorPageClosing) return;
  fetch('/api/app/window-heartbeat',{{method:'POST',keepalive:true}}).catch(()=>{{}});
}};
lovecaSimulatorHeartbeat();
const lovecaSimulatorHeartbeatTimer=setInterval(lovecaSimulatorHeartbeat,1000);
window.addEventListener('pagehide',()=>{{
  lovecaSimulatorPageClosing=true;
  clearInterval(lovecaSimulatorHeartbeatTimer);
  try {{ navigator.sendBeacon('/api/app/window-closed',''); }} catch(_e) {{}}
}},{{capture:true}});

async function stopEmbeddedSimulator() {{
  if(!confirm('シミュレータを終了しますか？')) return;
  const res=await fetch('/api/manual/stop',{{method:'POST'}});
  const data=await res.json();
  if(data.ok) location.replace('{return_path}');
  else alert(data.message||'終了に失敗しました。');
}}
async function shutdownLovecaApp() {{
  if(!confirm('Loveca Applicationを終了しますか？')) return;
  try {{
    await fetch('/api/app/shutdown',{{method:'POST'}});
  }} finally {{
    try {{ window.open('', '_self'); window.close(); }} catch(_e) {{}}
  }}
}}
</script>
</body>
</html>""".format(
            css=CSS,
            deck=deck_name,
            key_html=key_html,
            public_button=public_button,
            return_path=return_path,
            private_url=private_url,
        )
        return doc.encode("utf-8")

    def home_body(self) -> str:
        settings = self.app.load_settings()
        active_deck = html.escape(str(settings.get("active_deck") or "未選択"))
        body = """
<div class="grid menu-grid">
<section class="card"><h2>手動シミュレータ</h2><p>起動時に使用デッキを選択します。</p><a class="button" href="/manual">デッキを選んで起動</a></section>
<section class="card"><h2>リモート対戦</h2><p>対戦コードを発行し、シミュレータ本体とパブリック画面を起動します。</p><a class="button" href="/remote">開く</a></section>
<section class="card"><h2>自動シミュレータ</h2><p>コンピューター同士の対戦や候補手の確認に対応予定です。</p><button disabled>準備中</button></section>
<section class="card"><h2>デッキ管理</h2><p>デッキの作成、読込、編集、整理を行います。</p><a class="button" href="/decks">開く</a></section>
<section class="card"><h2>データ更新</h2><p>新しいカード情報やカード画像を取得します。</p><a class="button" href="/update">開く</a></section>
<section class="card"><h2>ログ管理</h2><p>対戦や更新処理の履歴を確認します。</p><a class="button" href="/logs">開く</a></section>
<section class="card"><h2>設定</h2><p>プレイヤー名やリモート対戦の設定を変更します。</p><a class="button" href="/settings">開く</a></section>
<section class="card"><h2>診断・バージョン</h2><p>アプリのバージョンとカードデータの状態を確認します。</p><a class="button" href="/diagnostics">開く</a></section>
</div>
"""
        return body.replace("{active_deck}", active_deck)

    def simulator_session_panel(self, remote_screen: bool) -> str:
        state = self.app.manual_window_status()
        if not state.get("running") or bool(state.get("remote")) != remote_screen:
            return ""

        private_url = html.escape(str(state.get("private_url") or ""), quote=True)
        public_url = html.escape(str(state.get("public_url") or ""), quote=True)
        status_text = html.escape(str(state.get("message") or "シミュレータ起動中"))
        deck_name = html.escape(str(state.get("deck_name") or "使用デッキ"))
        actions: list[str] = []

        if private_url:
            actions.append("<a class='button' href='/simulator'>シミュレータへ戻る</a>".format(private_url))
        else:
            actions.append("<button disabled>表示先を検出中</button>")

        if remote_screen:
            if public_url:
                actions.append("<a class='button secondary' target='loveca_public' href='{}'>パブリック画面へ戻る</a>".format(public_url))
            else:
                actions.append("<button class='secondary' disabled>パブリック画面を検出中</button>")

        actions.append("<button type='button' style='background:var(--bad);color:white' onclick='stopSimulatorOnPage()'>シミュレータを終了</button>")
        return """
<section class="panel" id="runningSimulatorPanel">
  <h2>シミュレータ起動中</h2>
  <p>{}</p>
  <p class="status">{}</p>
  <div style="display:flex;gap:10px;flex-wrap:wrap">{}</div>
  <div id="stopSimulatorStatus" class="status"></div>
</section>
<script>
async function stopSimulatorOnPage() {{
  const box=document.getElementById('stopSimulatorStatus');
  if(!confirm('起動中のシミュレータを終了しますか？')) return;

  // 起動時に使った固定ウインドウ名から、実際のタブ／ウインドウを再取得する。
  let simulatorWindow=null;
  let publicWindow=null;
  try {{ simulatorWindow=window.open('', 'loveca_simulator'); }} catch(_e) {{}}
  try {{ publicWindow=window.open('', 'loveca_public'); }} catch(_e) {{}}

  box.textContent='終了しています...';
  try {{
    const res=await fetch('/api/manual/stop',{{method:'POST'}});
    const data=await res.json();
    box.className='status '+(data.ok?'ok':'bad');
    box.textContent=data.message;
    if(data.ok) {{
      try {{ if(simulatorWindow && !simulatorWindow.closed) simulatorWindow.close(); }} catch(_e) {{}}
      try {{ if(publicWindow && !publicWindow.closed) publicWindow.close(); }} catch(_e) {{}}
      setTimeout(()=>location.reload(),700);
    }}
  }} catch(e) {{
    box.className='status bad';
    box.textContent=String(e);
  }}
}}
</script>
""".format(deck_name, status_text, "".join(actions))

    def manual_body(self) -> str:
        decks = self.app.list_decks()
        rendered = []
        for deck in decks:
            comp = deck.get("composition", {}); valid = bool(deck.get("valid"))
            status = "<span class='ok'>使用可能</span>" if valid else "<span class='bad'>構成不正</span>"
            button = f"<button onclick='startManual({json.dumps(deck['path'])})'>このデッキで起動</button>" if valid else "<button disabled>起動不可</button>"
            rendered.append(f"<tr><td>{html.escape(deck['name'])}</td><td>{status}</td><td>{comp.get('member',0)}/48</td><td>{comp.get('live',0)}/12</td><td>{comp.get('total',0)}/60</td><td><a class='button secondary' href='/decks/view?path={html.escape(deck['path'], quote=True)}'>確認</a></td><td>{button}</td></tr>")
        rows = "".join(rendered) if rendered else "<tr><td colspan='7' class='warn'>使用できるデッキがありません。</td></tr>"
        session_panel = self.simulator_session_panel(False)
        return session_panel + f"""
<section class="panel"><h2>手動シミュレータを起動</h2><p class="status">通常対戦セットアップ：選択した60枚デッキをシャッフルし、手札6枚・山札54枚へ分割します。引き直しとエネルギー配置は通常のゲーム開始処理で行います。</p><p>構成検証済みのデッキだけを起動できます。</p>
<table><thead><tr><th>名前</th><th>状態</th><th>メンバー</th><th>ライブ</th><th>合計</th><th></th><th></th></tr></thead><tbody>{rows}</tbody></table><div id="manualStatus" class="status"></div></section>
<script>
function reserveWindow(name) {{
  const popup=window.open('about:blank',name);
  if(popup) {{ popup.document.write('<title>起動中</title><p style=\"font-family:sans-serif;padding:24px\">シミュレータを起動しています...</p>'); }}
  return popup;
}}
async function waitForWindows(privatePopup, publicPopup, box) {{
  for(let i=0;i<140;i++) {{
    const res=await fetch('/api/manual/window-status',{{cache:'no-store'}});
    const state=await res.json();
    if(state.private_url && privatePopup && !privatePopup.closed) privatePopup.location.replace(state.private_url);
    if(state.public_url && publicPopup && !publicPopup.closed) publicPopup.location.replace(state.public_url);
    if(state.status==='ready') {{ box.className='status ok'; box.textContent='シミュレータ画面を開きました。'; return true; }}
    if(state.status==='failed'||state.status==='timeout') {{
      box.className='status bad'; box.textContent=state.message||'表示先を検出できませんでした。';
      if(privatePopup && !state.private_url) privatePopup.close();
      if(publicPopup && !state.public_url) publicPopup.close();
      return false;
    }}
    await new Promise(resolve=>setTimeout(resolve,350));
  }}
  box.className='status bad'; box.textContent='表示先の検出がタイムアウトしました。この画面を再読み込みすると、起動状態の確認・復帰・終了ができます。';
  return false;
}}
async function startManual(deckPath) {{
  const box=document.getElementById('manualStatus');
  box.textContent='起動中...';
  const body=new URLSearchParams({{deck_path:deckPath}});
  try {{
    const res=await fetch('/api/manual/start',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body}});
    const data=await res.json();
    if(!data.ok) {{ box.className='status bad'; box.textContent=data.message; return; }}
    for(let i=0;i<140;i++) {{
      const statusRes=await fetch('/api/manual/window-status',{{cache:'no-store'}});
      const state=await statusRes.json();
      if(state.status==='ready' && state.private_url) {{
        markLovecaInternalNavigation();
        location.replace('/simulator');
        return;
      }}
      if(state.status==='failed'||state.status==='timeout') {{
        box.className='status bad';
        box.textContent=state.message||'シミュレータを起動できませんでした。';
        return;
      }}
      await new Promise(resolve=>setTimeout(resolve,350));
    }}
    box.className='status bad';
    box.textContent='シミュレータの起動確認がタイムアウトしました。';
  }} catch(e) {{
    box.className='status bad';
    box.textContent=String(e);
  }}
}}
</script>"""

    def remote_body(self) -> str:
        settings = self.app.load_settings()
        player_id = html.escape(str(settings.get("player_id") or ""))
        key_length = int(settings.get("remote_key_length") or 4)
        options = "".join(
            '<option value="{}" {}>{}桁</option>'.format(
                n,
                "selected" if n == key_length else "",
                n,
            )
            for n in (3, 4, 5)
        )
        deck_options = []
        for deck in self.app.list_decks():
            if not bool(deck.get("valid")):
                continue
            comp = deck.get("composition", {})
            label = "{}（メンバー{} / ライブ{}）".format(
                deck.get("name", ""),
                comp.get("member", 0),
                comp.get("live", 0),
            )
            deck_options.append(
                '<option value="{}">{}</option>'.format(
                    html.escape(str(deck.get("path") or ""), quote=True),
                    html.escape(label),
                )
            )
        if deck_options:
            deck_select = "".join(deck_options)
            start_button = '<button type="submit">コード発行してリモート対戦を開始</button>'
        else:
            deck_select = '<option value="">使用可能なデッキがありません</option>'
            start_button = '<button type="submit" disabled>開始不可</button>'
        session_panel = self.simulator_session_panel(True)
        remote_sessions = self.app.list_remote_sessions()
        session_options = "".join(
            '<option value="{}">{} / {} / {}</option>'.format(
                html.escape(str(item.get("saved_to") or ""), quote=True),
                html.escape(str(item.get("date") or "")),
                html.escape(str(item.get("player_id") or "")),
                html.escape(str(item.get("short_key") or "")),
            )
            for item in remote_sessions
        )
        if not session_options:
            session_options = '<option value="">照合できるローカル記録がありません</option>'
        session_rows = "".join(
            '<tr><td>{}</td><td>{}</td><td>{}</td><td><a class="button secondary" href="/api/remote/session?path={}">JSONを開く</a></td></tr>'.format(
                html.escape(str(item.get("date") or "")),
                html.escape(str(item.get("player_id") or "")),
                html.escape(str(item.get("short_key") or "")),
                quote(str(item.get("saved_to") or "")),
            )
            for item in remote_sessions[:20]
        )
        if not session_rows:
            session_rows = '<tr><td colspan="4" class="warn">セッション記録はまだありません。</td></tr>'
        return session_panel + """
<section class="panel">
<h2>リモート対戦セッション</h2>
<p>コードを発行し、選択したデッキでシミュレータ本体と画面共有用パブリックウインドウを起動します。</p><p class="status">通常対戦セットアップ：選択した60枚デッキをシャッフルし、手札6枚・山札54枚へ分割します。引き直しとエネルギー配置は通常のゲーム開始処理で行います。</p>
<p class="status">通常の手動シミュレータ起動ではパブリックウインドウを開きません。</p>
<form id="remoteStartForm" onsubmit="return startRemote(event)">
  <label for="deck_path">使用デッキ</label>
  <select id="deck_path" name="deck_path" required>{}</select>
  <div class="row">
    <div>
      <label for="player_id">プレイヤー識別子</label>
      <input id="player_id" name="player_id" maxlength="24" required placeholder="TAKESHI" value="{}">
    </div>
    <div>
      <label for="key_length">自動生成するキー長</label>
      <select id="key_length" name="key_length">{}</select>
    </div>
  </div>
  <label for="short_key">相手から受け取ったキー（任意）</label>
  <input id="short_key" name="short_key" minlength="3" maxlength="5" placeholder="空欄なら自動生成">
  <div style="margin-top:16px">{}</div>
</form>
<div id="remoteStartStatus" class="status"></div>
<div id="remoteKeyResult"></div>
</section>
<section class="panel">
<h2>リモート対戦ログ同一性確認</h2>
<p>相手から受け取ったセッションJSONとローカル記録を照合します。対戦日・共有キー・共有照合IDが一致し、プレイヤー識別子が異なる場合のみ同一対戦として承認します。</p>
<table><thead><tr><th>日付</th><th>プレイヤー</th><th>共有キー</th><th>共有用記録</th></tr></thead><tbody>{}</tbody></table>
<form method="post" action="/remote/verify" style="margin-top:18px">
<label for="local_session">ローカル側セッション記録</label>
<select id="local_session" name="local_session" required>{}</select>
<label for="counterpart_json">相手側セッションJSON</label>
<textarea id="counterpart_json" name="counterpart_json" rows="12" style="width:100%;background:#10141a;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:10px" required placeholder='{{"date":"20260716","player_id":"OPPONENT","short_key":"AB12",...}}'></textarea>
<div style="margin-top:12px"><button type="submit">記録を照合</button></div>
</form>
</section>
<script>
function reserveRemoteWindow(name,label) {{
  const popup=window.open('about:blank',name);
  if(popup) popup.document.write('<title>起動中</title><p style="font-family:sans-serif;padding:24px">'+label+'を起動しています...</p>');
  return popup;
}}
async function startRemote(event) {{
  event.preventDefault();
  const box=document.getElementById('remoteStartStatus');
  const publicPopup=reserveRemoteWindow('loveca_public','パブリック画面');
  if(!publicPopup) {{
    box.className='status bad';
    box.textContent='パブリック画面のポップアップを許可してください。';
    return false;
  }}
  box.className='status'; box.textContent='コード発行・起動中...';
  try {{
    const form=new FormData(document.getElementById('remoteStartForm'));
    const body=new URLSearchParams(form);
    const res=await fetch('/api/remote/start',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body}});
    const data=await res.json();
    if(!data.ok) {{ publicPopup.close(); box.className='status bad'; box.textContent=data.message; return false; }}
    document.getElementById('remoteKeyResult').innerHTML='<h3>対戦キー</h3><div style="font-size:42px;font-weight:800;letter-spacing:.18em">'+data.short_key+'</div><p class="status">相手へ共有するセッションJSON</p><pre>'+JSON.stringify(data.session_record||{{}},null,2)+'</pre>';
    for(let i=0;i<140;i++) {{
      const statusRes=await fetch('/api/manual/window-status',{{cache:'no-store'}});
      const state=await statusRes.json();
      if(state.public_url && !publicPopup.closed) publicPopup.location.replace(state.public_url);
      if(state.status==='ready') {{
        box.className='status ok';
        box.textContent='シミュレータとパブリック画面を開きました。';
        markLovecaInternalNavigation();
        location.replace('/simulator');
        return false;
      }}
      if(state.status==='failed'||state.status==='timeout') {{
        box.className='status bad'; box.textContent=state.message||'表示先を検出できませんでした。';
        if(!state.public_url) publicPopup.close(); return false;
      }}
      await new Promise(resolve=>setTimeout(resolve,350));
    }}
    box.className='status bad'; box.textContent='表示先の検出がタイムアウトしました。この画面を再読み込みすると、起動状態の確認・復帰・終了ができます。';
  }} catch(e) {{ publicPopup.close(); box.className='status bad'; box.textContent=String(e); }}
  return false;
}}
</script>
""".format(deck_select, player_id, options, start_button, session_rows, session_options)

    def deck_code_import_body(
        self,
        deck_code: str = "",
        error: str = "",
    ) -> str:
        error_html = ""
        if error:
            error_html = "<p class='bad'>{}</p>".format(html.escape(error))
        return """
<section class="panel" style="max-width:760px;margin-inline:auto">
<h2>デッキコードから読込</h2>
<p>公開されているデッキコードを入力すると、カード構成を読み込んで保存前に確認できます。</p>
{error_html}
<form id="deckCodeImportForm" method="post" action="/decks/import/run"
      onsubmit="return beginDeckCodeImport()">
<label for="deck_code">デッキコード</label>
<input id="deck_code" name="deck_code" value="{deck_code}" required autofocus
       autocomplete="off" style="font-size:24px;letter-spacing:.12em;text-transform:uppercase">
<div style="display:flex;gap:10px;margin-top:14px">
<button id="deckCodeImportButton" type="submit">読込</button>
<a id="deckCodeImportCancel" class="button secondary" href="/decks">キャンセル</a>
</div>
<div id="deckCodeImportProgress" class="deck-import-progress" hidden
     role="status" aria-live="polite">
  <div class="deck-import-progress-label">
    <strong>読込中...</strong>
    <span>デッキコードからカードリストを取得しています。</span>
  </div>
  <div class="deck-import-progress-track" aria-hidden="true">
    <div class="deck-import-progress-bar"></div>
  </div>
</div>
</form>
</section>
<style>
.deck-import-progress {{
  margin-top:18px;
  padding:14px;
  border:1px solid var(--line);
  border-radius:10px;
  background:var(--panel2);
}}
.deck-import-progress-label {{
  display:flex;
  justify-content:space-between;
  gap:12px;
  flex-wrap:wrap;
  margin-bottom:10px;
}}
.deck-import-progress-label span {{
  color:var(--muted);
}}
.deck-import-progress-track {{
  height:10px;
  overflow:hidden;
  border-radius:999px;
  background:#0d1015;
}}
.deck-import-progress-bar {{
  width:35%;
  height:100%;
  border-radius:999px;
  background:linear-gradient(90deg,#4c8dff,#8cc8ff);
  animation:deckImportLoading 1.15s ease-in-out infinite;
}}
@keyframes deckImportLoading {{
  0% {{transform:translateX(-110%);}}
  100% {{transform:translateX(315%);}}
}}
</style>
<script>
function beginDeckCodeImport() {{
  const form=document.getElementById('deckCodeImportForm');
  const input=document.getElementById('deck_code');
  const button=document.getElementById('deckCodeImportButton');
  const cancel=document.getElementById('deckCodeImportCancel');
  const progress=document.getElementById('deckCodeImportProgress');

  if(!form || !input || !input.value.trim()) return true;
  if(button.disabled) return false;

  input.value=input.value.trim().toUpperCase();
  button.disabled=true;
  button.textContent='読込中...';
  input.readOnly=true;
  if(cancel) {{
    cancel.setAttribute('aria-disabled','true');
    cancel.style.pointerEvents='none';
    cancel.style.opacity='.55';
  }}
  if(progress) progress.hidden=false;

  setTimeout(()=>form.submit(),40);
  return false;
}}
</script>
""".format(
            error_html=error_html,
            deck_code=html.escape(deck_code, quote=True),
        )

    def deck_code_import_result_body(self, imported: dict[str, Any]) -> str:
        cards: list[str] = []
        for row in imported["rows"]:
            card = self.app.card_display_data(row)
            image_params = {"card_no": card["card_no"]}
            requested_rarity = self.app._normalize_rarity(card.get("rarity", ""))
            matching_variant = next(
                (
                    variant
                    for variant in self.app.card_variants(card["card_no"])
                    if self.app._normalize_rarity(variant.get("raw_rarity", ""))
                    == requested_rarity
                    and variant.get("path") is not None
                ),
                None,
            )
            if matching_variant:
                image_params["variant_id"] = str(
                    matching_variant.get("variant_id") or ""
                )
            elif card.get("variant_id"):
                image_params["variant_id"] = card["variant_id"]
            elif card.get("rarity"):
                image_params["rarity"] = card["rarity"]
            image_url = "/card-image?" + urlencode(image_params)
            cards.append(
                """
<article class="import-card">
  <div class="import-count">×{count}</div>
  <img src="{image}" alt="{name}" onerror="this.style.visibility='hidden'">
  <div class="import-name">{name}</div>
  <div class="import-number">{card_no}</div>
</article>
""".format(
                    count=html.escape(str(card["count"])),
                    image=html.escape(image_url, quote=True),
                    name=html.escape(str(card["name"] or card["card_no"])),
                    card_no=html.escape(str(card["card_no"])),
                )
            )

        composition = imported["composition"]
        status_class = "ok" if composition.get("valid") else "warn"
        return """
<style>
.import-grid {{
  display:grid;
  grid-template-columns:repeat(12,minmax(62px,1fr));
  gap:7px;
  align-items:start;
}}
.import-card {{
  min-width:0;
  position:relative;
  text-align:center;
  font-size:10px;
}}
.import-card img {{
  display:block;
  width:100%;
  max-width:82px;
  aspect-ratio:5/7;
  object-fit:contain;
  margin:0 auto 3px;
  background:#0d1015;
  border-radius:5px;
}}
.import-count {{
  position:absolute;
  right:2px;
  top:2px;
  z-index:2;
  background:rgba(0,0,0,.82);
  color:white;
  border-radius:999px;
  padding:2px 5px;
  font-weight:800;
  font-size:11px;
}}
.import-name {{
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}}
.import-number {{
  color:var(--muted);
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}}
@media(max-width:1000px) {{
  .import-grid {{grid-template-columns:repeat(8,minmax(58px,1fr));}}
}}
@media(max-width:640px) {{
  .import-grid {{grid-template-columns:repeat(5,minmax(52px,1fr));}}
}}
</style>
<section class="panel">
<h2>抽出結果の確認</h2>
<p>デッキコード：<code>{code}</code></p>
<details>
<summary>読込情報</summary>
<p>読込機能：<code>{script}</code></p>
<p>一時データ：<code>{source_tsv}</code></p>
</details>
<p class="{status_class}">
種類数：{types} / 合計：{total}枚 /
メンバー：{member} / 48、ライブ：{live} / 12
</p>
<div class="import-grid">{cards}</div>
</section>
<section class="panel">
<h2>保存</h2>
<form method="post" action="/decks/import/save">
<input type="hidden" name="import_token" value="{import_token}">
<input type="hidden" name="deck_code" value="{code_attr}">
<label for="deck_name">デッキ名</label>
<input id="deck_name" name="deck_name" value="{deck_name_attr}" required>
<label for="deck_tags">タグ（任意・カンマ区切り）</label>
<input id="deck_tags" name="tags" placeholder="例：大会用, お気に入り">
<div style="display:flex;gap:10px;margin-top:14px">
<button type="submit">保存</button>
<a class="button secondary" href="/decks/import">コードを入力し直す</a>
<a class="button secondary" href="/decks">キャンセル</a>
</div>
</form>
</section>
""".format(
            code=html.escape(str(imported["deck_code"])),
            code_attr=html.escape(str(imported["deck_code"]), quote=True),
            import_token=html.escape(str(imported["import_token"]), quote=True),
            deck_name_attr=html.escape(str(imported["deck_name"]), quote=True),
            script=html.escape(str(imported["script"])),
            source_tsv=html.escape(str(imported["source_tsv"])),
            command=html.escape(" ".join(imported["command"])),
            status_class=status_class,
            types=imported["card_types"],
            total=imported["card_count"],
            member=composition.get("member", 0),
            live=composition.get("live", 0),
            cards="".join(cards),
        )

    def decks_body(self) -> str:
        decks = self.app.list_decks()
        rendered: list[str] = []
        all_tags: set[str] = set()

        for deck in decks:
            comp = deck.get("composition", {})
            valid = bool(deck.get("valid"))
            tags = [str(tag) for tag in deck.get("tags", [])]
            all_tags.update(tags)
            if valid:
                status = "<span class='ok'>使用可能</span>"
                start_button = (
                    "<button type='button' onclick='startDeck({})'>開始</button>"
                ).format(json.dumps(deck.get("path", ""), ensure_ascii=False))
            else:
                status = "<span class='bad' title='{}'>要確認</span>".format(
                    html.escape(str(deck.get("validation_error", "")), quote=True)
                )
                start_button = "<button disabled>開始不可</button>"

            tag_html = "".join(
                "<span class='deck-tag'>{}</span>".format(html.escape(tag))
                for tag in tags
            ) or "<span class='status'>タグなし</span>"

            rendered.append(
                """
<tr data-name="{name_key}" data-modified="{modified}" data-code="{code_key}"
    data-tags="{tags_key}" data-valid="{valid_key}">
  <td><strong>{name}</strong><div class="status">{code}</div></td>
  <td>{tags}</td>
  <td>{status}</td>
  <td>{total}</td>
  <td>{modified_text}</td>
  <td class="deck-actions">
    <a class="button secondary" href="/decks/view?path={path_attr}">確認</a>
    <a class="button secondary" href="/decks/edit?path={path_attr}">編集</a>
    {start}
    <form method="post" action="/decks/delete"
          onsubmit="return confirm('このデッキを削除しますか？\\n削除後は元に戻せません。')">
      <input type="hidden" name="deck_path" value="{path_attr}">
      <button type="submit" class="danger-button">削除</button>
    </form>
  </td>
</tr>
""".format(
                    name_key=html.escape(str(deck.get("name", "")).casefold(), quote=True),
                    modified=html.escape(str(deck.get("modified", "")), quote=True),
                    code_key=html.escape(str(deck.get("code", "")).casefold(), quote=True),
                    tags_key=html.escape("|".join(tag.casefold() for tag in tags), quote=True),
                    valid_key="1" if valid else "0",
                    name=html.escape(str(deck.get("name", ""))),
                    code=html.escape(str(deck.get("code", ""))),
                    tags=tag_html,
                    status=status,
                    total=comp.get("total", 0),
                    modified_text=html.escape(str(deck.get("modified", ""))),
                    path_attr=html.escape(str(deck.get("path", "")), quote=True),
                    start=start_button,
                )
            )

        rows = "".join(rendered)
        if not rows:
            rows = "<tr><td colspan='6' class='warn'>保存されているデッキはありません。</td></tr>"

        tag_options = "".join(
            "<option value='{}'>{}</option>".format(
                html.escape(tag.casefold(), quote=True),
                html.escape(tag),
            )
            for tag in sorted(all_tags, key=str.casefold)
        )

        return """
<style>
.deck-list-tools {{display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin:14px 0}}
.deck-list-tools label {{min-width:180px}}
.deck-tag {{display:inline-block;margin:2px;padding:3px 8px;border-radius:999px;background:var(--panel2);border:1px solid var(--line);font-size:12px}}
.deck-actions {{display:flex;gap:7px;flex-wrap:wrap;align-items:center}}
.deck-actions form {{margin:0}}
.danger-button {{background:var(--bad);color:white}}
</style>
<section class='panel'>
<h2>デッキ管理</h2>
<p>デッキの作成・読込・整理を行えます。名前やタグで見つけやすく整理できます。</p>
<p style='display:flex;gap:10px;flex-wrap:wrap'>
  <a class='button' href='/decks/new'>新規デッキ作成</a>
  <a class='button secondary' href='/decks/import'>デッキコードから読込</a>
</p>
<div class="deck-list-tools">
  <label>並び順
    <select id="deckSort" onchange="applyDeckListView()">
      <option value="modified_desc">更新が新しい順</option>
      <option value="modified_asc">更新が古い順</option>
      <option value="name_asc">名前順</option>
      <option value="code_asc">デッキコード順</option>
    </select>
  </label>
  <label>タグ
    <select id="deckTagFilter" onchange="applyDeckListView()">
      <option value="">すべて</option>
      {tag_options}
    </select>
  </label>
  <label>状態
    <select id="deckValidFilter" onchange="applyDeckListView()">
      <option value="">すべて</option>
      <option value="1">使用可能</option>
      <option value="0">要確認</option>
    </select>
  </label>
</div>
<table>
<thead><tr><th>名前</th><th>タグ</th><th>状態</th><th>枚数</th><th>更新日時</th><th>操作</th></tr></thead>
<tbody id="deckListRows">{rows}</tbody>
</table>
<div id='deckListStatus' class='status'></div>
</section>
<script>
function applyDeckListView() {{
  const body=document.getElementById('deckListRows');
  if(!body) return;
  const rows=[...body.querySelectorAll('tr[data-name]')];
  const sort=document.getElementById('deckSort').value;
  const tag=document.getElementById('deckTagFilter').value;
  const valid=document.getElementById('deckValidFilter').value;
  for(const row of rows) {{
    const tagOk=!tag || (row.dataset.tags||'').split('|').includes(tag);
    const validOk=!valid || row.dataset.valid===valid;
    row.hidden=!(tagOk&&validOk);
  }}
  rows.sort((a,b)=>{{
    if(sort==='name_asc') return (a.dataset.name||'').localeCompare(b.dataset.name||'','ja');
    if(sort==='code_asc') return (a.dataset.code||'').localeCompare(b.dataset.code||'','ja');
    const cmp=(a.dataset.modified||'').localeCompare(b.dataset.modified||'');
    return sort==='modified_asc'?cmp:-cmp;
  }});
  for(const row of rows) body.appendChild(row);
}}
applyDeckListView();

async function startDeck(deckPath) {{
  const box=document.getElementById('deckListStatus');
  box.textContent='シミュレータを起動しています...';
  const body=new URLSearchParams({{deck_path:deckPath}});
  try {{
    const res=await fetch('/api/manual/start',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body}});
    const data=await res.json();
    if(!data.ok) {{ box.className='status bad'; box.textContent=data.message; return; }}
    for(let i=0;i<140;i++) {{
      const r=await fetch('/api/manual/window-status',{{cache:'no-store'}});
      const state=await r.json();
      if(state.status==='ready' && state.private_url) {{ markLovecaInternalNavigation(); location.replace('/simulator'); return; }}
      if(state.status==='failed'||state.status==='timeout') {{
        box.className='status bad'; box.textContent=state.message; return;
      }}
      await new Promise(resolve=>setTimeout(resolve,350));
    }}
    box.className='status bad'; box.textContent='起動確認がタイムアウトしました。';
  }} catch(e) {{ box.className='status bad'; box.textContent=String(e); }}
}}
</script>
""".format(tag_options=tag_options, rows=rows)

    def deck_view_body(self, deck_path: str) -> str:
        try:
            metadata, rows = self.app.read_deck_rows(deck_path)
        except ValueError as exc:
            return f"<section class='panel'><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/decks'>戻る</a></section>"
        name = str(metadata.get("deck_name") or Path(deck_path).stem)
        code = str(metadata.get("deck_code") or Path(deck_path).stem.removeprefix("deck_"))
        total = sum(int(row["count"]) for row in rows)
        validation = self.app.deck_validation(deck_path)
        valid = bool(validation.get("valid"))
        if valid:
            validation_html = "<span class='ok'>ゲーム開始可能</span>"
            start_button = "<button type='button' onclick='startDeckGame({})'>このデッキで開始</button>".format(
                json.dumps(deck_path, ensure_ascii=False)
            )
        else:
            validation_html = "<span class='bad'>ゲーム開始不可：{}</span>".format(
                html.escape(str(validation.get("error") or "構成不正"))
            )
            start_button = "<button type='button' disabled>構成不正のため開始不可</button>"

        cards: list[str] = []
        for row in rows:
            card = self.app.card_display_data(row)
            image_params = {"card_no": card["card_no"]}
            if card.get("variant_id"):
                image_params["variant_id"] = card["variant_id"]
            elif card.get("rarity"):
                image_params["rarity"] = card["rarity"]
            image_url = "/card-image?" + urlencode(image_params)
            data_attrs = {
                "count": card["count"],
                "card_no": card["card_no"],
                "rarity": card["rarity"],
                "name": card["name"],
                "card_type": card["card_type"],
                "group": card["group"],
                "unit": card["unit"],
                "cost": card["cost"],
                "effect": card["effect"],
                "image_url": image_url,
            }
            encoded = html.escape(json.dumps(data_attrs, ensure_ascii=False), quote=True)
            cards.append(f"""
<article class="deck-card" tabindex="0" role="button" data-card="{encoded}" onclick="openCard(this)" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();openCard(this);}}">
  <div class="deck-card-image-wrap">
    <div class="deck-count-badge">×{html.escape(card['count'])}</div>
    <img class="deck-card-image" src="{html.escape(image_url, quote=True)}" alt="{html.escape(card['name'] or card['card_no'], quote=True)}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
    <div class="deck-card-placeholder">画像なし<br>{html.escape(card['card_no'])}</div>
  </div>
  <div class="deck-card-title">{html.escape(card['name'] or '名称未取得')}</div>
  <div class="deck-card-number">{html.escape(card['card_no'])}</div>
</article>
""")

        return f"""
<section class="panel">
<h2>{html.escape(name)} <small><code>{html.escape(code)}</code></small></h2>
<p>カード種類数：{len(rows)} / 合計枚数：{total}</p><p>{validation_html}</p>
<div style="margin-bottom:14px">{start_button}
<a class="button" href="/decks/edit?path={html.escape(deck_path, quote=True)}">編集</a>
<a class="button secondary" href="/decks">一覧へ</a>
</div><div id="deckStartStatus" class="status"></div>
<div class="deck-card-grid">{''.join(cards)}</div>
<hr style="border-color:var(--line);margin:22px 0">
<form method="post" action="/decks/delete" onsubmit="return confirm('このデッキを削除しますか？');">
<input type="hidden" name="deck_path" value="{html.escape(deck_path, quote=True)}">
<button type="submit" style="background:var(--bad);color:white">削除</button>
</form>
</section>
<div id="cardModalBackdrop" class="modal-backdrop" onclick="if(event.target===this)closeCard()">
  <section class="card-modal" role="dialog" aria-modal="true" aria-labelledby="modalCardName">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px">
      <h2 id="modalCardName" style="margin:0"></h2>
      <button class="secondary" onclick="closeCard()">閉じる</button>
    </div>
    <div class="card-modal-grid">
      <div><img id="modalCardImage" alt="カード画像"></div>
      <div>
        <table class="card-detail-table">
          <tr><th>投入枚数</th><td id="modalCount"></td></tr>
          <tr><th>カード番号</th><td id="modalNumber"></td></tr>
          <tr><th>種類</th><td id="modalType"></td></tr>
          <tr><th>レアリティ</th><td id="modalRarity"></td></tr>
          <tr><th>グループ</th><td id="modalGroup"></td></tr>
          <tr><th>ユニット</th><td id="modalUnit"></td></tr>
          <tr><th>コスト</th><td id="modalCost"></td></tr>
        </table>
        <h3>カードテキスト</h3>
        <div id="modalEffect" class="card-effect"></div>
      </div>
    </div>
  </section>
</div>
<script>
function valueOrDash(value) {{ return value === null || value === undefined || value === '' ? '—' : value; }}
function openCard(element) {{
  const card = JSON.parse(element.dataset.card);
  document.getElementById('modalCardName').textContent = valueOrDash(card.name);
  document.getElementById('modalCount').textContent = '×' + valueOrDash(card.count);
  document.getElementById('modalNumber').textContent = valueOrDash(card.card_no);
  document.getElementById('modalType').textContent = valueOrDash(card.card_type);
  document.getElementById('modalRarity').textContent = valueOrDash(card.rarity);
  document.getElementById('modalGroup').textContent = valueOrDash(card.group);
  document.getElementById('modalUnit').textContent = valueOrDash(card.unit);
  document.getElementById('modalCost').textContent = valueOrDash(card.cost);
  document.getElementById('modalEffect').textContent = valueOrDash(card.effect);
  const image = document.getElementById('modalCardImage');
  image.src = card.image_url;
  image.alt = valueOrDash(card.name);
  document.getElementById('cardModalBackdrop').classList.add('open');
}}
function closeCard() {{ document.getElementById('cardModalBackdrop').classList.remove('open'); }}
async function startDeckGame(deckPath) {{
  const box=document.getElementById('deckStartStatus');
  box.textContent='シミュレータを起動しています...';
  const body=new URLSearchParams({{deck_path:deckPath}});
  try {{
    const res=await fetch('/api/manual/start',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body}}); const data=await res.json();
    if(!data.ok) {{ box.className='status bad'; box.textContent=data.message; return; }}
    for(let i=0;i<140;i++) {{
      const r=await fetch('/api/manual/window-status',{{cache:'no-store'}}); const state=await r.json();
      if(state.status==='ready' && state.private_url) {{ markLovecaInternalNavigation(); location.replace('/simulator'); return; }}
      if(state.status==='failed'||state.status==='timeout') {{ box.className='status bad'; box.textContent=state.message; return; }}
      await new Promise(resolve=>setTimeout(resolve,350));
    }}
    box.className='status bad'; box.textContent='表示先の検出がタイムアウトしました。この画面を再読み込みすると、起動状態の確認・復帰・終了ができます。';
  }} catch(e) {{ box.className='status bad'; box.textContent=String(e); }}
}}
document.addEventListener('keydown', event => {{ if (event.key === 'Escape') closeCard(); }});
</script>
"""

    def deck_edit_body(self, deck_path: str, is_new: bool) -> str:
        initial_cards: list[dict[str, Any]] = []
        if is_new:
            name = ""
            tags_text = ""
            existing = ""
            title = "新規デッキ作成"
        else:
            try:
                metadata, rows = self.app.read_deck_rows(deck_path)
            except ValueError as exc:
                return f"<section class='panel'><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/decks'>戻る</a></section>"
            name = str(metadata.get("deck_name") or Path(deck_path).stem)
            tags_text = ", ".join(self.app._normalize_deck_tags(metadata.get("tags")))
            existing = deck_path
            title = "デッキ編集"
            for row in rows:
                display = self.app.card_display_data(row)
                card = self.app.searchable_card(
                    display["card_no"], self.app.card_record(display["card_no"])
                )
                card["count"] = display["count"]
                card["rarity"] = display["rarity"] or card["rarity"]
                card["name"] = display["name"] or card["name"]
                saved_variant = display.get("variant_id", "")
                if saved_variant:
                    card["variant_id"] = saved_variant
                else:
                    matching = [
                        variant
                        for variant in self.app.card_variants(display["card_no"])
                        if self.app._normalize_rarity(variant.get("raw_rarity", ""))
                        == self.app._normalize_rarity(display["rarity"])
                    ]
                    if matching:
                        card["variant_id"] = str(matching[0].get("variant_id") or "")
                initial_cards.append(card)

        options = self.app.card_filter_options()

        def select_options(items: list[str]) -> str:
            return '<option value="">すべて</option>' + "".join(
                f'<option value="{html.escape(item, quote=True)}">{html.escape(item)}</option>'
                for item in items
            )

        member_heart_defs = [
            ("pink", "桃", "heart-pink"),
            ("red", "赤", "heart-red"),
            ("yellow", "黄", "heart-yellow"),
            ("green", "緑", "heart-green"),
            ("blue", "青", "heart-blue"),
            ("purple", "紫", "heart-purple"),
        ]
        required_heart_defs = member_heart_defs + [
            ("any", "任意", "heart-any"),
        ]

        def heart_rows(prefix: str, definitions: list[tuple[str, str, str]]) -> str:
            return "".join(
                f"""
                <div class="heart-range-row">
                  <span class="heart-icon {css_class}">♥</span>
                  <span class="heart-label">{label}</span>
                  <input id="{prefix}_{key}_min" type="number" min="0" placeholder="最小">
                  <span>～</span>
                  <input id="{prefix}_{key}_max" type="number" min="0" placeholder="最大">
                </div>
                """
                for key, label, css_class in definitions
            )

        blade_defs = [
            ("none", "なし", "blade-special"),
            ("pink", "桃", "heart-pink"),
            ("red", "赤", "heart-red"),
            ("yellow", "黄", "heart-yellow"),
            ("green", "緑", "heart-green"),
            ("blue", "青", "heart-blue"),
            ("purple", "紫", "heart-purple"),
            ("all", "ALL", "heart-all"),
            ("draw", "ドロー", "blade-special"),
            ("score", "スコア+", "blade-special"),
            ("double_any", "ダブル無色", "heart-any"),
        ]
        blade_chips = "".join(
            f"""
            <label class="token-chip">
              <input type="checkbox" name="blade_heart_token" value="{token}">
              <span class="heart-icon {css_class}">{'♥' if token not in ('draw','score') else '◆'}</span>
              {label}
            </label>
            """
            for token, label, css_class in blade_defs
        )

        initial_json = json.dumps(initial_cards, ensure_ascii=False).replace("</", "<\\/")
        base_rarity_json = json.dumps(options.get("rarity", []), ensure_ascii=False).replace("</", "<\\/")
        parallel_rarity_json = json.dumps(options.get("parallel_rarity", []), ensure_ascii=False).replace("</", "<\\/")
        return f"""
<style>
html,body {{min-width:0}}
main {{
  width:100%;
  max-width:none;
  margin:0;
  padding:20px 595px 20px 20px;
}}
.deck-editor-layout {{
  display:block;
  width:100%;
}}
.basic-search {{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
  gap:12px;
}}
.basic-search .search-field:first-child {{
  grid-column:span 2;
}}
.advanced-columns {{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(360px,1fr));
  gap:16px;
  margin-top:14px;
}}
.range-group {{
  border:1px solid var(--line);
  border-radius:10px;
  padding:12px;
}}
.range-title {{font-weight:700;margin-bottom:10px}}
.numeric-ranges {{
  display:flex;
  flex-wrap:wrap;
  gap:16px;
}}
.numeric-range-row {{
  display:grid;
  grid-template-columns:var(--loveca-spinner-width) 18px var(--loveca-spinner-width);
  gap:6px;
  align-items:center;
}}
.numeric-range-row .number-stepper,
.heart-range-row .number-stepper {{
  width:var(--loveca-spinner-width);
  min-width:var(--loveca-spinner-width);
  max-width:var(--loveca-spinner-width);
}}
.heart-range-row {{
  display:grid;
  grid-template-columns:28px 48px var(--loveca-spinner-width) 18px var(--loveca-spinner-width);
  gap:6px;
  align-items:center;
  margin:6px 0;
}}
.heart-icon {{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  width:24px;
  height:24px;
  border-radius:50%;
  font-size:17px;
  font-weight:800;
  background:#111;
}}
.heart-pink {{color:#ff79b4}}
.heart-red {{color:#ff5353}}
.heart-yellow {{color:#ffd84d}}
.heart-green {{color:#60d47f}}
.heart-blue {{color:#65a7ff}}
.heart-purple {{color:#b985ff}}
.heart-all {{color:white;background:conic-gradient(#ff79b4,#ff5353,#ffd84d,#60d47f,#65a7ff,#b985ff,#ff79b4)}}
.heart-any {{color:#d7dce6;border:1px dashed #d7dce6}}
.blade-special {{color:#fff;background:#5f6878}}
.mode-row {{display:flex;gap:14px;align-items:center;margin:8px 0}}
.token-grid {{display:flex;flex-wrap:wrap;gap:8px}}
.token-chip {{
  display:flex;
  align-items:center;
  gap:6px;
  background:var(--panel2);
  border:1px solid var(--line);
  padding:7px 9px;
  border-radius:9px;
  cursor:pointer;
}}
.token-chip input {{width:auto}}
.parallel-toggle {{
  display:inline-flex;
  align-items:center;
  gap:7px;
  padding:7px 10px;
  border:1px solid var(--line);
  border-radius:8px;
  background:var(--panel2);
  white-space:nowrap;
}}
.parallel-toggle input {{width:auto;margin:0}}
.search-grid {{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(154px,1fr));
  gap:12px;
  margin-top:16px;
  width:100%;
}}
.search-card {{
  background:var(--panel2);
  border:1px solid var(--line);
  border-radius:10px;
  padding:8px;
  display:flex;
  flex-direction:column;
  gap:6px;
}}
.search-card img {{width:100%;aspect-ratio:451/630;object-fit:contain;background:#0d1015;border-radius:6px}}
.search-name {{font-size:14px;line-height:1.4;min-height:40px}}
.search-meta {{font-size:12px;line-height:1.35;color:var(--muted);overflow-wrap:anywhere}}
.deck-side {{
  position:fixed;
  right:20px;
  top:86px;
  width:555px;
  max-height:calc(var(--loveca-layout-height) - 106px);
  overflow:auto;
  z-index:20;
}}
.deck-row {{
  display:grid;
  grid-template-columns:66px minmax(0,1fr) auto;
  gap:10px;
  align-items:center;
  border-bottom:1px solid var(--line);
  padding:10px 0;
  min-height:96px;
}}
.deck-row img {{width:66px;height:92px;object-fit:contain;background:#0d1015;border-radius:6px}}
.count-controls {{display:flex;align-items:center;gap:6px}}
.count-controls button {{padding:6px 10px}}
.composition {{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:10px 0}}
.composition div {{background:var(--panel2);padding:8px;border-radius:8px;text-align:center}}
details.advanced {{
  margin-top:12px;
  border:1px solid var(--line);
  border-radius:10px;
  padding:12px;
}}
details.advanced summary {{cursor:pointer;font-weight:700;font-size:16px}}
body {{overflow-x:hidden}}

details.subfilter {{
  margin-top:12px;
  border:1px solid var(--line);
  border-radius:9px;
  padding:10px;
  position:relative;
}}
details.subfilter summary {{
  cursor:pointer;
  font-weight:700;
  padding-right:130px;
}}
.section-clear {{
  position:absolute;
  right:10px;
  top:6px;
  padding:4px 8px;
  font-size:12px;
  background:#1f6feb !important;
  color:#ffffff !important;
  border:1px solid #8bb9ff !important;
  opacity:1 !important;
}}
.search-field {{
  position:relative;
}}
.field-clear {{
  position:absolute;
  right:6px;
  top:27px;
  width:24px;
  height:24px;
  padding:0;
  border-radius:50%;
  background:#1f6feb !important;
  color:#ffffff !important;
  border:1px solid #8bb9ff !important;
  opacity:1 !important;
  font-size:15px;
  font-weight:800;
}}
.search-field input,
.search-field select {{
  padding-right:34px;
}}


.editor-leave-modal[hidden] {{display:none}}
.editor-leave-modal {{
  position:fixed;
  left:0;
  top:0;
  width:var(--loveca-layout-width);
  height:var(--loveca-layout-height);
  z-index:10000;
  display:grid;place-items:center;
  background:rgba(0,0,0,.68);
  padding:20px;
}}
.editor-leave-dialog {{
  width:min(560px,100%);
  padding:22px;
  border:1px solid var(--line);
  border-radius:14px;
  background:var(--panel);
  box-shadow:0 24px 80px rgba(0,0,0,.45);
}}
.editor-leave-dialog h2 {{margin-top:0}}
.editor-leave-actions {{
  display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;margin-top:18px;
}}

.card-detail-overlay[hidden] {{display:none}}
.card-detail-overlay {{position:fixed;inset:0;z-index:25000;display:flex;align-items:center;justify-content:center;padding:24px;background:rgba(0,0,0,.72)}}
.card-detail-dialog {{width:min(980px,calc(100vw - 48px));max-height:calc(100vh - 48px);overflow:auto;display:grid;grid-template-columns:minmax(280px,420px) minmax(320px,1fr);gap:22px;padding:20px;border:1px solid var(--line);border-radius:14px;background:var(--panel)}}
.card-detail-image {{width:100%;max-height:72vh;object-fit:contain;background:#0d1015;border-radius:8px}}
.card-detail-info h2 {{margin-top:0}}
.card-detail-text {{white-space:pre-line;line-height:1.75;font-size:15px;background:var(--panel2);padding:14px;border-radius:10px;overflow-wrap:anywhere}}
.card-detail-meta {{color:var(--muted);line-height:1.6}}
.card-detail-actions {{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}}
.search-card img {{cursor:zoom-in}}
@media(max-width:760px) {{.card-detail-dialog {{grid-template-columns:1fr}}}}

.deck-analysis-overlay[hidden] {{display:none}}
.deck-analysis-overlay {{
  position:fixed;
  left:0;
  top:0;
  width:var(--loveca-layout-width);
  height:var(--loveca-layout-height);
  z-index:12000;
  overflow:auto;
  background:var(--bg);
  padding:12px;
  box-sizing:border-box;
}}
.deck-analysis-shell {{
  width:100%;
  max-width:none;
  min-height:calc(var(--loveca-layout-height) - 24px);
  margin:0;
}}
.deck-analysis-header {{
  position:sticky;
  top:0;
  z-index:5;
  display:flex;
  align-items:center;
  gap:10px;
  padding:8px 0 10px;
  background:var(--bg);
}}
.deck-analysis-header h1 {{
  margin:0;
  font-size:24px;
}}
.deck-analysis-header .spacer {{flex:1}}
.deck-analysis-summary {{
  display:grid;
  grid-template-columns:minmax(0,30fr) minmax(0,30fr) minmax(0,40fr);
  gap:12px;
  width:100%;
  margin:6px 0 14px;
  align-items:start;
}}
.deck-analysis-block[data-analysis-kind="cost"],
.deck-analysis-block[data-analysis-kind="group"],
.deck-analysis-block[data-analysis-kind="blade"] {{
  width:100%;
  min-width:0;
  grid-column:auto;
}}
.deck-analysis-block {{
  min-width:0;
  border:1px solid var(--line);
  border-radius:14px;
  padding:12px 12px 10px;
  background:var(--panel);
}}
.deck-analysis-block h2 {{
  margin:0 0 10px;
  font-size:19px;
}}
.histogram-vertical {{
  display:flex;
  align-items:flex-end;
  justify-content:flex-start;
  gap:6px;
  min-height:132px;
  overflow-x:visible;
  padding:0 2px;
}}
.histogram-column {{
  flex:1 1 0;
  min-width:0;
  display:grid;
  grid-template-rows:18px 90px minmax(24px,auto);
  gap:5px;
  align-items:end;
  text-align:center;
}}
.histogram-value {{
  font-weight:800;
  font-size:13px;
}}
.histogram-track {{
  position:relative;
  width:min(100%,30px);
  height:90px;
  margin:0 auto;
  border-radius:8px 8px 4px 4px;
  background:var(--panel2);
  border:1px solid var(--line);
  overflow:hidden;
}}
.histogram-bar {{
  position:absolute;
  left:0;
  right:0;
  bottom:0;
  min-height:0;
  border-radius:7px 7px 3px 3px;
  background:linear-gradient(180deg,#8cc8ff,#4c8dff);
}}
.histogram-label {{
  min-height:24px;
  font-size:11px;
  line-height:1.15;
  overflow-wrap:anywhere;
}}
.histogram-label-with-icon {{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:flex-start;
  gap:2px;
  min-height:28px;
  font-size:10px;
  line-height:1.1;
  overflow-wrap:anywhere;
}}
.histogram-heart-icon {{
  width:14px;
  height:14px;
  object-fit:contain;
  flex:0 0 auto;
}}
.histogram-bar[data-token="pink"] {{background:#ef86b7}}
.histogram-bar[data-token="red"] {{background:#e75d5d}}
.histogram-bar[data-token="yellow"] {{background:#e4c94f}}
.histogram-bar[data-token="green"] {{background:#55b879}}
.histogram-bar[data-token="blue"] {{background:#5d91e7}}
.histogram-bar[data-token="purple"] {{background:#a875dc}}
.histogram-bar[data-token="all"] {{
  background:linear-gradient(180deg,#ef86b7 0 16%,#e75d5d 16% 32%,#e4c94f 32% 48%,#55b879 48% 64%,#5d91e7 64% 80%,#a875dc 80% 100%);
}}
.histogram-bar[data-token="draw"] {{background:#52b8c8}}
.histogram-bar[data-token="score"] {{background:#d49b45}}
.histogram-bar[data-token="double_any"] {{background:#9aa3ad}}
.histogram-bar[data-token="none"] {{background:#59616d}}
.deck-analysis-grid {{
  display:grid;
  grid-template-columns:repeat(12,minmax(86px,1fr));
  gap:8px;
  align-items:start;
}}
.deck-analysis-card {{
  position:relative;
  min-width:0;
  text-align:center;
  font-size:11px;
}}
.deck-analysis-card img {{
  display:block;
  width:100%;
  max-width:116px;
  aspect-ratio:5/7;
  object-fit:contain;
  margin:0 auto 4px;
  border-radius:6px;
  background:#0d1015;
}}
.deck-analysis-count {{
  position:absolute;
  top:3px;
  right:3px;
  z-index:2;
  padding:2px 6px;
  border-radius:999px;
  background:rgba(0,0,0,.84);
  color:#fff;
  font-size:12px;
  font-weight:800;
}}
.deck-analysis-card-name,
.deck-analysis-card-number {{
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}}
.deck-analysis-card-number {{color:var(--muted)}}
body.deck-analysis-open {{overflow:hidden}}
@media(max-width:1200px) {{
  .deck-analysis-grid {{grid-template-columns:repeat(10,minmax(58px,1fr))}}
}}
@media(max-width:760px) {{
  .deck-analysis-grid {{grid-template-columns:repeat(6,minmax(52px,1fr))}}
}}
</style>

<section class="panel">
<h2>{title}</h2>
<label for="deck_name">デッキ名</label>
<input id="deck_name" value="{html.escape(name, quote=True)}" required placeholder="デッキ名を入力">
</section>

<div class="deck-editor-layout" style="margin-top:16px">
<section class="panel">
<h2>カード検索</h2>

<div class="basic-search">
  <div class="search-field">
    <label>カード名・カード番号</label>
    <input id="search_q" placeholder="例：高坂穂乃果 / PL!-...">
  </div>
  <div class="search-field">
    <label>商品</label>
    <select id="search_product">{select_options(options["product"])}</select>
  </div>
  <div class="search-field">
    <label>グループ</label>
    <select id="search_group">{select_options(options["group"])}</select>
  </div>
  <div class="search-field">
    <label>カードタイプ</label>
    <select id="search_type">{select_options(options["card_type"])}</select>
  </div>
</div>

<details class="advanced">
<summary>詳細検索</summary>

<div class="advanced-columns">
  <div>
    <details class="subfilter" open>
      <summary>数値条件</summary>
      <button type="button" class="section-clear" data-clear-section="numeric">この項目をクリア</button>
      <div class="range-group" data-search-section="numeric">
      <div class="numeric-ranges">
        <div>
          <label>コスト</label>
          <div class="numeric-range-row"><input id="search_cost_min" type="number" min="0" placeholder="最小"><span>～</span><input id="search_cost_max" type="number" min="0" placeholder="最大"></div>
        </div>
        <div>
          <label>ライブカードのスコア</label>
          <div class="numeric-range-row"><input id="search_score_min" type="number" min="0" placeholder="最小"><span>～</span><input id="search_score_max" type="number" min="0" placeholder="最大"></div>
        </div>
        <div>
          <label>ブレード数</label>
          <div class="numeric-range-row"><input id="search_blade_min" type="number" min="0" placeholder="最小"><span>～</span><input id="search_blade_max" type="number" min="0" placeholder="最大"></div>
        </div>
      </div>
      </div>
    </details>

    <details class="subfilter">
      <summary>メンバーのハート</summary>
      <button type="button" class="section-clear" data-clear-section="member-heart">この項目をクリア</button>
      <div class="range-group" data-search-section="member-heart">
      <div class="mode-row">
        <label><input type="radio" name="heart_mode" value="and" checked> AND</label>
        <label><input type="radio" name="heart_mode" value="or"> OR</label>
      </div>
      {heart_rows("heart", member_heart_defs)}
      </div>
    </details>
  </div>

  <div>
    <details class="subfilter">
      <summary>ライブの必要ハート</summary>
      <button type="button" class="section-clear" data-clear-section="required-heart">この項目をクリア</button>
      <div class="range-group" data-search-section="required-heart">
      <div class="mode-row">
        <label><input type="radio" name="required_heart_mode" value="and" checked> AND</label>
        <label><input type="radio" name="required_heart_mode" value="or"> OR</label>
      </div>
      {heart_rows("required", required_heart_defs)}
      </div>
    </details>

    <details class="subfilter">
      <summary>ブレードハート</summary>
      <button type="button" class="section-clear" data-clear-section="blade-heart">この項目をクリア</button>
      <div class="range-group" data-search-section="blade-heart">
      <div class="mode-row">
        <label><input type="radio" name="blade_heart_mode" value="and"> AND</label>
        <label><input type="radio" name="blade_heart_mode" value="or" checked> OR</label>
      </div>
      <div class="token-grid">{blade_chips}</div>
      </div>
    </details>
  </div>
</div>

<details class="subfilter">
<summary>能力種別</summary>
<button type="button" class="section-clear" data-clear-section="ability-type">この項目をクリア</button>
<div class="token-grid" data-search-section="ability-type">
  <label class="token-chip"><input type="checkbox" name="ability_type" value="auto">自動</label>
  <label class="token-chip"><input type="checkbox" name="ability_type" value="live_start">ライブ開始時</label>
  <label class="token-chip"><input type="checkbox" name="ability_type" value="live_success">ライブ成功時</label>
  <label class="token-chip"><input type="checkbox" name="ability_type" value="on_entry">登場時</label>
  <label class="token-chip"><input type="checkbox" name="ability_type" value="continuous">常時</label>
  <label class="token-chip"><input type="checkbox" name="ability_type" value="activated">起動</label>
  <label class="token-chip"><input type="checkbox" name="ability_type" value="none">能力なし</label>
</div>
</details>

<details class="subfilter">
<summary>その他の詳細条件</summary>
<button type="button" class="section-clear" data-clear-section="other-detail">この項目をクリア</button>
<div class="advanced-columns" data-search-section="other-detail">
  <div class="search-field">
    <label>ユニット</label>
    <select id="search_unit">{select_options(options["unit"])}</select>
  </div>
  <div class="search-field">
    <label>レアリティ</label>
    <select id="search_rarity">{select_options(options["rarity"])}</select>
  </div>
  <div class="search-field" style="grid-column:1 / -1">
    <label>カードテキスト</label>
    <input id="search_effect" placeholder="効果文を検索">
  </div>
</div>
</details>
</details>

<div style="display:flex;gap:8px;align-items:center;margin-top:12px">
<button type="button" onclick="searchCards()">今すぐ検索</button>
<button type="button" class="secondary" onclick="resetSearch()">全条件をクリア</button>
<label class="parallel-toggle">
  <input id="search_include_prerelease" type="checkbox" checked>
  プレリリースを表示する
</label>
<label class="parallel-toggle">
  <input id="search_include_parallel" type="checkbox">
  パラレルを表示する
</label>
<span class="status">入力後、自動検索します</span>
<span id="searchStatus" class="status"></span>
</div>

<div id="searchResults" class="search-grid"></div>
</section>

<section class="panel deck-side">
<h2>現在のデッキ</h2>
<label for="visible_deck_name">デッキ名</label>
<input id="visible_deck_name" value="{html.escape(name, quote=True)}">
<label for="visible_deck_tags">タグ（任意・カンマ区切り）</label>
<input id="visible_deck_tags" value="{html.escape(tags_text, quote=True)}" placeholder="例：大会用, お気に入り">
<div class="composition">
  <div>メンバー<br><strong id="memberCount">0</strong> / 48</div>
  <div>ライブ<br><strong id="liveCount">0</strong> / 12</div>
  <div>合計<br><strong id="totalCount">0</strong> / 60</div>
</div>
<div id="deckWarning" class="status"></div>
<div id="deckLoadStatus" class="status"></div>
<button type="button" class="secondary" style="width:100%;margin:8px 0 12px"
        onclick="openDeckAnalysis()">詳細分析ツール</button>
<div id="deckRows"></div>
<hr style="border-color:var(--line);margin:16px 0">
<form id="saveForm" method="post" action="/decks/save">
<input type="hidden" name="existing_path" value="{html.escape(existing, quote=True)}">
<input type="hidden" name="deck_name" id="save_deck_name">
<input type="hidden" name="tags" id="save_deck_tags">
<textarea name="tsv_text" id="save_tsv" hidden></textarea>
<input type="hidden" name="start_after_save" id="start_after_save" value="0">
<button type="submit" onclick="return prepareSave(false)">保存</button>
<button type="submit" onclick="return prepareSave(true)">保存してこのデッキで開始</button>
<a class="button secondary" href="/decks">キャンセル</a>
</form>
</section>
</div>

<div id="cardDetailOverlay" class="card-detail-overlay" hidden onclick="if(event.target===this)closeCardDetail()">
  <section class="card-detail-dialog" role="dialog" aria-modal="true" aria-labelledby="cardDetailTitle">
    <img id="cardDetailImage" class="card-detail-image" alt="">
    <div class="card-detail-info"><h2 id="cardDetailTitle"></h2><div id="cardDetailMeta" class="card-detail-meta"></div><h3>カードテキスト</h3><div id="cardDetailText" class="card-detail-text"></div><div class="card-detail-actions"><button type="button" class="secondary" onclick="closeCardDetail()">閉じる</button></div></div>
  </section>
</div>

<div id="deckAnalysisOverlay" class="deck-analysis-overlay" hidden
     role="dialog" aria-modal="true" aria-labelledby="deckAnalysisTitle">
  <div class="deck-analysis-shell">
    <div class="deck-analysis-header">
      <h1 id="deckAnalysisTitle">デッキ内容確認</h1>
      <span id="deckAnalysisDeckName" class="status"></span>
      <span class="spacer"></span>
      <button type="button" class="secondary" onclick="closeDeckAnalysis()">編集画面へ戻る</button>
    </div>
    <div id="deckAnalysisSummary" class="deck-analysis-summary"></div>
    <section class="deck-analysis-block">
      <h2>カード画像一覧</h2>
      <div id="deckAnalysisGrid" class="deck-analysis-grid"></div>
    </section>
  </div>
</div>

<div id="editorLeaveModal" class="editor-leave-modal" hidden
     role="dialog" aria-modal="true" aria-labelledby="editorLeaveTitle">
  <div class="editor-leave-dialog">
    <h2 id="editorLeaveTitle">変更内容が保存されていません</h2>
    <p>この画面を離れる前に、現在の変更を保存しますか？</p>
    <div id="editorLeaveError" class="status bad" hidden></div>
    <div class="editor-leave-actions">
      <button id="editorLeaveSave" type="button">保存する</button>
      <button id="editorLeaveDiscard" type="button" class="secondary">保存しない</button>
      <button id="editorLeaveCancel" type="button" class="secondary">画面遷移をキャンセル</button>
    </div>
  </div>
</div>

<script id="initialDeckData" type="application/json">{initial_json}</script>
<script>
const deck = new Map();
const searchCardCache = new Map();
let initialCards = [];
let editorInitialized = false;
const baseRarityOptions = {base_rarity_json};
const parallelRarityOptions = {parallel_rarity_json};
function deckKey(card) {{
  return card.variant_id || `${{card.card_no}}|${{card.rarity||""}}`;
}}
const memberHeartKeys = ["pink","red","yellow","green","blue","purple"];
const requiredHeartKeys = ["pink","red","yellow","green","blue","purple","any"];

function esc(value) {{
  return String(value ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
}}
function imageUrl(card) {{
  const params=new URLSearchParams({{card_no:card.card_no}});
  if(card.variant_id) params.set("variant_id",card.variant_id);
  else if(card.rarity) params.set("rarity",card.rarity);
  return "/card-image?"+params.toString();
}}
function typeKind(card) {{
  const t=String(card.card_type||"").toLowerCase();
  if(t.includes("メンバー")||t.includes("member")) return "member";
  if(t.includes("ライブ")||t.includes("live")) return "live";
  return "other";
}}
function cardNumberCount(cardNo) {{
  let total=0;
  for(const card of deck.values()) if(card.card_no===cardNo) total+=Number(card.count)||0;
  return total;
}}
function copyLimitViolations() {{
  const totals=new Map();
  for(const card of deck.values()) {{
    totals.set(card.card_no,(totals.get(card.card_no)||0)+(Number(card.count)||0));
  }}
  return [...totals.entries()].filter(([,count])=>count>4).sort((a,b)=>a[0].localeCompare(b[0]));
}}
function addCard(card) {{
  if(cardNumberCount(card.card_no)>=4) {{
    alert(`${{card.card_no}} は通常版・パラレル版を合計して4枚までです。`);
    return;
  }}
  const key=deckKey(card);
  const current=deck.get(key);
  if(current) current.count+=1; else deck.set(key,{{...card,count:1}});
  renderDeck();
}}
function addSearchCard(variantId) {{
  const card=searchCardCache.get(variantId);
  if(card) addCard(card);
}}
function changeCount(key,delta) {{
  const card=deck.get(key); if(!card)return;
  if(delta>0 && cardNumberCount(card.card_no)>=4) {{
    alert(`${{card.card_no}} は通常版・パラレル版を合計して4枚までです。`);
    return;
  }}
  card.count+=delta;
  if(card.count<=0) deck.delete(key);
  renderDeck();
}}
function composition() {{
  let member=0,live=0,other=0;
  for(const card of deck.values()) {{
    const kind=typeKind(card);
    if(kind==="member")member+=card.count; else if(kind==="live")live+=card.count; else other+=card.count;
  }}
  return {{member,live,other,total:member+live+other}};
}}
function renderDeck() {{
  const cards=[...deck.values()].sort((a,b)=>(a.card_no+"|"+(a.rarity||"")).localeCompare(b.card_no+"|"+(b.rarity||"")));
  const c=composition();
  memberCount.textContent=c.member; liveCount.textContent=c.live; totalCount.textContent=c.total;
  const copyErrors=copyLimitViolations();
  const valid=c.member===48&&c.live===12&&c.other===0&&copyErrors.length===0;
  deckWarning.className="status "+(valid?"ok":"warn");
  if(valid) {{
    deckWarning.textContent="デッキ構成要件を満たしています。";
  }} else {{
    const messages=[];
    if(!(c.member===48&&c.live===12&&c.other===0)) {{
      messages.push(`構成未達：メンバー ${{c.member}}/48、ライブ ${{c.live}}/12${{c.other?`、その他 ${{c.other}}`:``}}`);
    }}
    if(copyErrors.length) {{
      messages.push("4枚超過："+copyErrors.map(([cardNo,count])=>`${{cardNo}}=${{count}}枚`).join("、"));
    }}
    deckWarning.textContent=messages.join(" / ");
  }}
  deckRows.innerHTML=cards.map(card=>`
    <div class="deck-row">
      <img src="${{imageUrl(card)}}" alt="" onerror="this.style.visibility='hidden'">
      <div><div>${{esc(card.name||card.card_no)}}</div><div class="search-meta">${{esc(card.card_no)}} / ${{esc(card.card_type||"—")}}</div></div>
      <div class="count-controls">
        <button type="button" class="secondary" onclick='changeCount(${{JSON.stringify(deckKey(card))}},-1)'>−</button>
        <strong>${{card.count}}</strong>
        <button type="button" class="secondary" onclick='changeCount(${{JSON.stringify(deckKey(card))}},1)'>＋</button>
      </div>
    </div>`).join("");
}}

const bladeAnalysisDefinitions = [
  ["pink","桃"],
  ["red","赤"],
  ["yellow","黄"],
  ["green","緑"],
  ["blue","青"],
  ["purple","紫"],
  ["all","ALL"],
  ["draw","ドロー"],
  ["score","スコア＋"],
  ["double_any","ダブル無色"],
  ["none","ブレードハートなし"],
];

function isMemberCard(card) {{
  const value=String(card.card_type||"").toLowerCase();
  return value.includes("member") || value.includes("メンバー");
}}

function memberCostBucket(costValue) {{
  const cost=Number(costValue);
  if(!Number.isFinite(cost)) return null;
  if(cost<=2) return "0～2";
  if(cost<=4) return "3～4";
  if(cost<=10) return "5～10";
  if(cost<=13) return "11～13";
  if(cost<=17) return "14～17";
  return "18以上";
}}

function textIconUrl(token) {{
  return "/texticon?token="+encodeURIComponent(token);
}}

function histogramHtml(title, entries, options={{}}) {{
  const maximum=Math.max(1,...entries.map(entry=>Number(entry[1])||0));
  const kind=String(options.kind||"");
  const showIcons=Boolean(options.showIcons);
  return `
    <section class="deck-analysis-block" data-analysis-kind="${{esc(kind)}}">
      <h2>${{esc(title)}}</h2>
      <div class="histogram-vertical">
        ${{entries.map(entry=>{{
          const label=String(entry[0]);
          const numeric=Number(entry[1])||0;
          const token=String(entry[2]||"");
          const height=numeric===0 ? 0 : Math.max(8,(numeric/maximum)*100);
          const iconHtml=showIcons && ["pink","red","yellow","green","blue","purple","all"].includes(token)
            ? `<img class="histogram-heart-icon" src="${{textIconUrl(token)}}" alt="" onerror="this.style.display='none'">`
            : "";
          return `
            <div class="histogram-column" title="${{esc(label)}}：${{numeric}}">
              <span class="histogram-value">${{numeric}}</span>
              <div class="histogram-track">
                <div class="histogram-bar" data-token="${{esc(token)}}" style="height:${{height}}%"></div>
              </div>
              <span class="${{showIcons?"histogram-label-with-icon":"histogram-label"}}">
                ${{esc(label)}}${{iconHtml}}
              </span>
            </div>`;
        }}).join("")}}
      </div>
    </section>`;
}}

function buildDeckAnalysis() {{
  const cards=[...deck.values()].sort(
    (a,b)=>(a.card_no+"|"+(a.rarity||"")).localeCompare(
      b.card_no+"|"+(b.rarity||""),"ja"
    )
  );

  const costLabels=["0～2","3～4","5～10","11～13","14～17","18以上"];
  const costCounts=Object.fromEntries(costLabels.map(label=>[label,0]));
  const bladeCounts=Object.fromEntries(
    bladeAnalysisDefinitions.map(([token])=>[token,0])
  );
  const groupCounts=new Map();

  for(const card of cards) {{
    const count=Math.max(0,Number(card.count)||0);
    if(count===0) continue;

    if(isMemberCard(card)) {{
      const bucket=memberCostBucket(card.cost_num ?? card.cost);
      if(bucket) costCounts[bucket]+=count;
    }}

    let tokens=Array.isArray(card.blade_heart_tokens)
      ? card.blade_heart_tokens.map(value=>String(value))
      : [];
    tokens=[...new Set(tokens)];
    const knownTokens=tokens.filter(token=>Object.hasOwn(bladeCounts,token));
    if(knownTokens.length===0) {{
      bladeCounts.none+=count;
    }} else {{
      for(const token of knownTokens) bladeCounts[token]+=count;
    }}

    const groups=String(card.group||"")
      .split(/[/／,、・|]/)
      .map(value=>value.trim())
      .filter(Boolean);
    const normalizedGroups=[...new Set(groups.length ? groups : ["その他"])];
    let matchedMainGroup=false;
    for(const group of normalizedGroups) {{
      if(group.includes("μ's") || group.includes("µ's") || group.includes("ミューズ")) {{
        groupCounts.set("μ's",(groupCounts.get("μ's")||0)+count);
        matchedMainGroup=true;
      }} else if(group.includes("Aqours") || group.includes("アクア")) {{
        groupCounts.set("Aqours",(groupCounts.get("Aqours")||0)+count);
        matchedMainGroup=true;
      }} else if(group.includes("虹ヶ咲") || group.includes("ニジガク")) {{
        groupCounts.set("虹ヶ咲",(groupCounts.get("虹ヶ咲")||0)+count);
        matchedMainGroup=true;
      }} else if(group.includes("Liella")) {{
        groupCounts.set("Liella!",(groupCounts.get("Liella!")||0)+count);
        matchedMainGroup=true;
      }} else if(group.includes("蓮ノ空")) {{
        groupCounts.set("蓮ノ空",(groupCounts.get("蓮ノ空")||0)+count);
        matchedMainGroup=true;
      }}
    }}
    if(!matchedMainGroup) {{
      groupCounts.set("その他",(groupCounts.get("その他")||0)+count);
    }}
  }}

  const mainGroupLabels=["μ's","Aqours","虹ヶ咲","Liella!","蓮ノ空","その他"];
  const groupEntries=mainGroupLabels.map(label=>[label, groupCounts.get(label)||0]);

  deckAnalysisSummary.innerHTML=[
    histogramHtml(
      "メンバーカードのコスト内訳",
      costLabels.map(label=>[label,costCounts[label],"cost"]),
      {{kind:"cost"}}
    ),
    histogramHtml(
      "グループ内訳",
      (groupEntries.length ? groupEntries : [["未設定",0]])
        .map(([label,value])=>[label,value,"group"]),
      {{kind:"group"}}
    ),
    histogramHtml(
      "ブレードハートの内訳",
      bladeAnalysisDefinitions.map(([token,label])=>[label,bladeCounts[token],token]),
      {{kind:"blade",showIcons:true}}
    ),
  ].join("");

  deckAnalysisGrid.innerHTML=cards.map(card=>`
    <article class="deck-analysis-card">
      <div class="deck-analysis-count">×${{Number(card.count)||0}}</div>
      <img src="${{imageUrl(card)}}" alt="${{esc(card.name||card.card_no)}}"
           onerror="this.style.visibility='hidden'">
      <div class="deck-analysis-card-name" title="${{esc(card.name||card.card_no)}}">
        ${{esc(card.name||card.card_no)}}
      </div>
      <div class="deck-analysis-card-number">${{esc(card.card_no)}}</div>
    </article>
  `).join("");

  deckAnalysisDeckName.textContent=
    `${{visible_deck_name.value.trim()||"名称未設定"}} / ${{composition().total}}枚`;
}}

function openDeckAnalysis() {{
  buildDeckAnalysis();
  deckAnalysisOverlay.hidden=false;
  document.body.classList.add("deck-analysis-open");
  deckAnalysisOverlay.scrollTop=0;
}}

function closeDeckAnalysis() {{
  deckAnalysisOverlay.hidden=true;
  document.body.classList.remove("deck-analysis-open");
}}

deckAnalysisOverlay.addEventListener("click",event=>{{
  if(event.target===deckAnalysisOverlay) closeDeckAnalysis();
}});
document.addEventListener("keydown",event=>{{
  if(event.key==="Escape" && !deckAnalysisOverlay.hidden) closeDeckAnalysis();
}});

function radioValue(name) {{
  const checked=document.querySelector(`input[name="${{name}}"]:checked`);
  return checked ? checked.value : "";
}}

function refreshRarityOptions() {{
  const selected=search_rarity.value;
  const values=[...baseRarityOptions];
  if(search_include_parallel.checked) {{
    for(const value of parallelRarityOptions) {{
      if(!values.includes(value)) values.push(value);
    }}
  }}
  // Preserve the catalogue order supplied by the server. Do not alphabetically
  // re-sort it, because the rarity sequence has game-specific meaning.
  search_rarity.innerHTML='<option value="">すべて</option>'+values.map(
    value=>`<option value="${{esc(value)}}">${{esc(value)}}</option>`
  ).join("");
  const controller=customSelectControllers.get(search_rarity);
  if(controller) controller.sync();
  if(values.includes(selected)) search_rarity.value=selected;
}}

let searchRequestSerial=0;
let searchAbortController=null;

async function searchCards() {{
  const requestSerial=++searchRequestSerial;
  if(searchAbortController) searchAbortController.abort();
  searchAbortController=new AbortController();
  const requestController=searchAbortController;
  const params=new URLSearchParams({{limit:"120"}});
  params.set("q",search_q.value);
  params.set("product",search_product.value);
  params.set("group",search_group.value);
  params.set("card_type",search_type.value);
  params.set("unit",search_unit.value);
  params.set("rarity",search_rarity.value);
  params.set("include_parallel",search_include_parallel.checked ? "1" : "0");
  params.set("include_prerelease",search_include_prerelease.checked ? "1" : "0");
  params.set("cost_min",search_cost_min.value);
  params.set("cost_max",search_cost_max.value);
  params.set("score_min",search_score_min.value);
  params.set("score_max",search_score_max.value);
  params.set("blade_min",search_blade_min.value);
  params.set("blade_max",search_blade_max.value);
  params.set("heart_mode",radioValue("heart_mode")||"and");
  params.set("required_heart_mode",radioValue("required_heart_mode")||"and");
  params.set("blade_heart_mode",radioValue("blade_heart_mode")||"or");
  params.set("effect",search_effect.value);

  for(const key of memberHeartKeys) {{
    params.set(`heart_${{key}}_min`,document.getElementById(`heart_${{key}}_min`).value);
    params.set(`heart_${{key}}_max`,document.getElementById(`heart_${{key}}_max`).value);
  }}
  for(const key of requiredHeartKeys) {{
    params.set(`required_${{key}}_min`,document.getElementById(`required_${{key}}_min`).value);
    params.set(`required_${{key}}_max`,document.getElementById(`required_${{key}}_max`).value);
  }}

  const selectedTokens=[...document.querySelectorAll('input[name="blade_heart_token"]:checked')].map(el=>el.value);
  params.set("blade_heart_tokens",selectedTokens.join(","));
  const selectedAbilityTypes=[...document.querySelectorAll('input[name="ability_type"]:checked')].map(el=>el.value);
  params.set("ability_types",selectedAbilityTypes.join(","));

  searchStatus.textContent="検索中...";
  try {{
    const res=await fetch("/api/cards/search?"+params.toString(),{{signal:requestController.signal}});
    const data=await res.json();
    if(requestSerial!==searchRequestSerial) return;
    searchStatus.textContent=`${{data.count}}件表示`;
    searchCardCache.clear();
    for (const card of data.cards) searchCardCache.set(card.variant_id, card);
    searchResults.innerHTML=data.cards.map(card=>`
      <article class="search-card">
        <img class="search-card-image" data-variant-id="${{esc(card.variant_id)}}" src="${{imageUrl(card)}}" alt="${{esc(card.name)}}" onerror="this.style.visibility='hidden'">
        <div class="search-name">${{esc(card.name||card.card_no)}}</div>
        <div class="search-meta">${{esc(card.card_no)}}</div>
        <div class="search-meta">${{esc(card.expansion_name||card.product||"—")}}</div>
        <div class="search-meta">${{card.is_prerelease ? "プレリリース / " : ""}}${{esc(card.product_code||"")}}</div>
        <div class="search-meta">${{esc(card.card_type||"—")}} / ${{esc(card.group||"—")}}</div>
        <div class="search-meta">${{card.is_parallel ? "パラレル / " + esc(card.raw_rarity||"別レアリティ") : esc(card.rarity||"レアリティ不明")}}</div>
        <button type="button" class="add-search-card" data-variant-id="${{esc(card.variant_id)}}">＋ デッキへ追加</button>
      </article>`).join("");
    for (const button of searchResults.querySelectorAll(".add-search-card")) {{
      button.addEventListener("click", () => addSearchCard(button.dataset.variantId));
    }}
    for (const image of searchResults.querySelectorAll(".search-card-image")) {{
      image.addEventListener("click", () => openCardDetail(image.dataset.variantId));
    }}
  }} catch(error) {{
    if(error && error.name==="AbortError") return;
    if(requestSerial!==searchRequestSerial) return;
    searchStatus.textContent=String(error);
  }} finally {{
    if(searchAbortController===requestController) searchAbortController=null;
  }}
}}

function formatCardTextForDisplay(value) {{
  let text=String(value||"")
    .split(String.fromCharCode(13)).join("")
    .split(String.fromCharCode(10)).join(" ")
    .replace(/[\t ]+/g," ")
    .trim();
  if(!text) return "能力なし";

  // 機械処理用の改行を畳み、能力の開始タグだけを段落の先頭にする。
  const abilityStarts=[
    "起動","自動","登場","ライブ開始時","ライブ成功時","ライブ終了時","常時"
  ];
  for(const label of abilityStarts) {{
    for(const tag of [`<${{label}}>` , `［${{label}}］`, `[${{label}}]`]) {{
      text=text.split(tag).join(String.fromCharCode(10)+tag+" ");
    }}
  }}
  while(text.startsWith(String.fromCharCode(10))) text=text.slice(1);
  return text.trim();
}}

function openCardDetail(variantId) {{
  const card=searchCardCache.get(variantId); if(!card) return;
  cardDetailTitle.textContent=card.name||card.card_no||"カード詳細";
  cardDetailImage.src=imageUrl(card); cardDetailImage.alt=card.name||card.card_no||"";
  const values=[card.card_no,card.card_type||"—",card.group||"—",card.unit||"",card.cost!==""?`コスト：${{card.cost}}`:"",card.score!==""?`スコア：${{card.score}}`:"",card.blade!==""?`ブレード：${{card.blade}}`:"",card.rarity||card.raw_rarity||""].filter(Boolean);
  cardDetailMeta.textContent=values.join(" / ");
  cardDetailText.textContent=formatCardTextForDisplay(card.effect);
  cardDetailOverlay.hidden=false;
}}
function closeCardDetail() {{ cardDetailOverlay.hidden=true; }}
document.addEventListener("keydown",event=>{{if(event.key==="Escape")closeCardDetail();}});

const customSelectControllers=new Map();
function closeAllCustomSelects(except=null) {{
  for(const [select,controller] of customSelectControllers) {{
    if(select===except) continue;
    controller.close();
  }}
}}
function enhanceSearchSelect(select) {{
  if(!select || customSelectControllers.has(select)) return;

  const wrap=document.createElement("div");
  wrap.className="custom-select-wrap";
  wrap.dataset.selectId=select.id||"";
  const button=document.createElement("button");
  button.type="button";
  button.className="custom-select-button";
  button.setAttribute("aria-haspopup","listbox");
  button.setAttribute("aria-expanded","false");
  const menu=document.createElement("div");
  menu.className="custom-select-menu";
  menu.setAttribute("role","listbox");
  menu.hidden=true;

  const controller={{
    open() {{
      closeAllCustomSelects(select);
      controller.sync();
      menu.hidden=false;
      wrap.classList.add("open");
      button.setAttribute("aria-expanded","true");
    }},
    close() {{
      menu.hidden=true;
      wrap.classList.remove("open");
      button.setAttribute("aria-expanded","false");
    }},
    sync() {{
      menu.replaceChildren();
      for(const option of Array.from(select.options)) {{
        const item=document.createElement("button");
        item.type="button";
        item.className="custom-select-option"+(option.selected?" selected":"");
        item.textContent=option.textContent||"";
        item.dataset.value=option.value;
        item.setAttribute("role","option");
        item.setAttribute("aria-selected",option.selected?"true":"false");
        item.addEventListener("click",()=>{{
          select.value=option.value;
          select.dispatchEvent(new Event("change",{{bubbles:true}}));
          controller.close();
        }});
        menu.appendChild(item);
      }}
      const chosen=select.options[select.selectedIndex];
      button.textContent=chosen ? chosen.textContent : "すべて";
    }},
  }};

  // UIを完成させてからネイティブselectを隠す。初期化失敗時に検索自体を壊さない。
  select.insertAdjacentElement("afterend",wrap);
  wrap.append(button,menu);
  controller.sync();
  customSelectControllers.set(select,controller);
  select.classList.add("custom-select-native");

  button.addEventListener("click",()=>{{
    if(menu.hidden) controller.open(); else controller.close();
  }});
  select.addEventListener("change",controller.sync);
}}
function enhanceSearchSelects() {{
  for(const id of ["search_product","search_group","search_type","search_unit","search_rarity"]) {{
    enhanceSearchSelect(document.getElementById(id));
  }}
}}
document.addEventListener("click",event=>{{
  if(!event.target.closest(".custom-select-wrap")) closeAllCustomSelects();
}});

function resetSearch() {{
  for(const element of document.querySelectorAll('input[type="text"],input[type="number"],select')) {{
    if(element.id==="deck_name") continue;
    element.value="";
  }}
  for(const checkbox of document.querySelectorAll('input[name="blade_heart_token"]')) checkbox.checked=false;
  search_include_prerelease.checked=true;
  search_include_parallel.checked=false;
  refreshRarityOptions();
  document.querySelector('input[name="heart_mode"][value="and"]').checked=true;
  document.querySelector('input[name="required_heart_mode"][value="and"]').checked=true;
  document.querySelector('input[name="blade_heart_mode"][value="or"]').checked=true;
  for(const controller of customSelectControllers.values()) controller.sync();
  searchCards();
}}

function buildSavePayload(startAfterSave=false, allowInvalidPrompt=true) {{
  const name=visible_deck_name.value.trim();
  if(!name){{alert("デッキ名を入力してください。");return null}}
  if(deck.size===0){{alert("カードを1枚以上追加してください。");return null}}
  const copyErrors=copyLimitViolations();
  if(copyErrors.length) {{
    alert("同一カードナンバーは通常版・パラレル版を合計して4枚までです。\\n"+
      copyErrors.map(([cardNo,count])=>`${{cardNo}}：${{count}}枚`).join("\\n"));
    return null;
  }}
  const c=composition();
  if(!(c.member===48&&c.live===12&&c.other===0)) {{
    if(!allowInvalidPrompt || !confirm(
      `デッキ構成要件を満たしていません。\\nメンバー ${{c.member}}/48\\nライブ ${{c.live}}/12\\nこのまま保存しますか？`
    )) return null;
  }}

  const rows=[...deck.values()].sort((a,b)=>a.card_no.localeCompare(b.card_no));
  const clean=value=>String(value??"").replaceAll("\\t"," ").replaceAll("\\n"," ");
  const lines=["count\\tcard_no\\trarity\\tname\\tvariant_id"];
  for(const card of rows) lines.push([
    card.count,
    clean(card.card_no),
    clean(card.rarity),
    clean(card.name),
    clean(card.variant_id)
  ].join("\\t"));

  return {{
    existing_path:document.querySelector('#saveForm input[name="existing_path"]').value,
    deck_name:name,
    tags:visible_deck_tags.value.trim(),
    tsv_text:lines.join("\\n")+"\\n",
    start_after_save:startAfterSave ? "1" : "0",
  }};
}}

function prepareSave(startAfterSave=false) {{
  const payload=buildSavePayload(startAfterSave,true);
  if(!payload) return false;
  save_deck_name.value=payload.deck_name;
  save_deck_tags.value=payload.tags;
  save_tsv.value=payload.tsv_text;
  start_after_save.value=payload.start_after_save;
  editorAllowLeave=true;
  return true;
}}

function editorSnapshot() {{
  const rows=[...deck.values()]
    .map(card=>({{
      card_no:String(card.card_no||""),
      rarity:String(card.rarity||""),
      variant_id:String(card.variant_id||""),
      count:Number(card.count)||0,
    }}))
    .sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
  return JSON.stringify({{
    name:visible_deck_name.value.trim(),
    tags:visible_deck_tags.value.trim(),
    rows,
  }});
}}

let editorInitialSnapshot="";
let editorAllowLeave=false;
let editorPendingNavigation=null;

function editorIsDirty() {{
  return !editorAllowLeave && editorInitialSnapshot !== "" &&
    editorSnapshot() !== editorInitialSnapshot;
}}

function closeEditorLeaveModal() {{
  editorLeaveModal.hidden=true;
  editorLeaveError.hidden=true;
  editorLeaveError.textContent="";
  editorPendingNavigation=null;
}}

function performPendingNavigation() {{
  const pending=editorPendingNavigation;
  editorPendingNavigation=null;
  editorAllowLeave=true;
  editorLeaveModal.hidden=true;
  if(!pending) return;
  if(pending.type==="href") {{
    location.href=pending.value;
  }} else if(pending.type==="shutdown") {{
    shutdownLovecaApp();
  }}
}}

function requestEditorLeave(pending) {{
  // Product requirement: leaving the deck editor always requires an explicit
  // choice, even when no card change has been detected.
  editorPendingNavigation=pending;
  editorLeaveModal.hidden=false;
  editorLeaveSave.focus();
}}

async function saveEditorBeforeLeave() {{
  const payload=buildSavePayload(false,true);
  if(!payload) return;
  editorLeaveSave.disabled=true;
  editorLeaveDiscard.disabled=true;
  editorLeaveCancel.disabled=true;
  editorLeaveError.hidden=true;
  try {{
    const response=await fetch("/decks/save",{{
      method:"POST",
      headers:{{"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"}},
      body:new URLSearchParams(payload),
      redirect:"follow",
    }});
    if(!response.ok) {{
      throw new Error(`保存に失敗しました（HTTP ${{response.status}}）`);
    }}
    editorInitialSnapshot=editorSnapshot();
    performPendingNavigation();
  }} catch(error) {{
    editorLeaveError.hidden=false;
    editorLeaveError.textContent=String(error);
  }} finally {{
    editorLeaveSave.disabled=false;
    editorLeaveDiscard.disabled=false;
    editorLeaveCancel.disabled=false;
  }}
}}

editorLeaveSave.addEventListener("click",saveEditorBeforeLeave);
editorLeaveDiscard.addEventListener("click",performPendingNavigation);
editorLeaveCancel.addEventListener("click",closeEditorLeaveModal);

document.addEventListener("click",event=>{{
  if(editorAllowLeave || event.defaultPrevented || event.button!==0) return;
  const anchor=event.target.closest("a[href]");
  if(!anchor) return;
  if(anchor.target==="_blank" || anchor.hasAttribute("download")) return;
  const url=new URL(anchor.href,location.href);
  if(url.origin!==location.origin) return;
  event.preventDefault();
  requestEditorLeave({{type:"href",value:url.href}});
}},true);

const appShutdownButton=[...document.querySelectorAll("button")]
  .find(button=>String(button.getAttribute("onclick")||"").includes("shutdownLovecaApp"));
if(appShutdownButton) {{
  appShutdownButton.addEventListener("click",event=>{{
    if(editorAllowLeave) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    requestEditorLeave({{type:"shutdown",value:""}});
  }},true);
}}

window.addEventListener("beforeunload",event=>{{
  if(editorAllowLeave) return;
  event.preventDefault();
  event.returnValue="";
}});

function applyDeckEditorViewportMetrics() {{
  const layoutHeightRaw=getComputedStyle(document.documentElement)
    .getPropertyValue("--loveca-layout-height");
  const layoutHeight=parseFloat(layoutHeightRaw)||1200;
  const deckPanel=document.querySelector(".deck-side");
  if(deckPanel) {{
    deckPanel.style.maxHeight=Math.max(420,layoutHeight-106)+"px";
  }}
}}

window.addEventListener("loveca:viewport-scale",applyDeckEditorViewportMetrics);
applyDeckEditorViewportMetrics();

function loadInitialDeckData() {{
  const element=document.getElementById("initialDeckData");
  if(!element) throw new Error("保存済みデッキ情報の読込領域がありません。");
  const parsed=JSON.parse(element.textContent||"[]");
  if(!Array.isArray(parsed)) throw new Error("保存済みデッキ情報の形式が不正です。");
  return parsed;
}}

function rebuildDeckFromInitialData() {{
  deck.clear();
  initialCards=loadInitialDeckData();
  for(const rawCard of initialCards) {{
    const card={{...rawCard}};
    const count=Math.max(1,Number(card.count)||1);
    const key=deckKey(card);
    const current=deck.get(key);
    if(current) current.count+=count;
    else deck.set(key,{{...card,count}});
  }}
  renderDeck();

  if(initialCards.length>0 && deck.size===0) {{
    deckLoadStatus.className="status bad";
    deckLoadStatus.textContent=
      `保存済みカード ${{initialCards.length}}件を読み込みましたが、デッキ欄へ反映できませんでした。`;
  }} else if(initialCards.length>0) {{
    deckLoadStatus.className="status ok";
    deckLoadStatus.textContent=
      `保存済みデッキを読み込みました（${{initialCards.length}}種類）。`;
  }} else {{
    deckLoadStatus.className="status";
    deckLoadStatus.textContent="新規デッキです。";
  }}
}}

function initializeDeckEditor() {{
  if(editorInitialized) return;
  editorInitialized=true;
  try {{
    rebuildDeckFromInitialData();
  }} catch(error) {{
    deck.clear();
    renderDeck();
    deckLoadStatus.className="status bad";
    deckLoadStatus.textContent="保存済みデッキを読み込めませんでした："+String(error);
  }}

  editorAllowLeave=false;
  editorPendingNavigation=null;
  editorLeaveModal.hidden=true;
  editorLeaveError.hidden=true;
  editorLeaveError.textContent="";
  refreshRarityOptions();
  editorInitialSnapshot=editorSnapshot();

  searchCardCache.clear();
  searchResults.innerHTML="";
  searchStatus.textContent="カード一覧を読み込んでいます...";
  searchCards();
}}

window.addEventListener("pageshow",event=>{{
  // BFCache can restore an old DOM. Rebuild from the immutable JSON payload,
  // rather than relying on the previous Map or request state.
  if(event.persisted) {{
    editorInitialized=false;
    initializeDeckEditor();
  }}
}});



let searchTimer = null;
function scheduleSearch() {{
  clearTimeout(searchTimer);
  searchTimer = setTimeout(searchCards, 280);
}}

function clearControls(container) {{
  for (const element of container.querySelectorAll('input,select')) {{
    if (element.type === "radio") {{
      const defaultValue = element.name === "blade_heart_mode" ? "or" : "and";
      element.checked = element.value === defaultValue;
    }} else if (element.type === "checkbox") {{
      element.checked = false;
    }} else {{
      element.value = "";
      if(element.tagName === "SELECT") element.dispatchEvent(new Event("change", {{bubbles:true}}));
    }}
  }}
  scheduleSearch();
}}

for (const field of document.querySelectorAll(".search-field")) {{
  const control = field.querySelector("input,select");
  if (!control || control.id === "deck_name") continue;
  const button = document.createElement("button");
  button.type = "button";
  button.className = "field-clear";
  button.textContent = "×";
  button.title = "この項目をクリア";
  button.addEventListener("click", () => {{
    control.value = "";
    control.dispatchEvent(new Event(control.tagName === "SELECT" ? "change" : "input", {{bubbles:true}}));
  }});
  field.appendChild(button);
}}

for (const button of document.querySelectorAll("[data-clear-section]")) {{
  button.addEventListener("click", event => {{
    event.preventDefault();
    event.stopPropagation();
    const details = button.closest("details.subfilter");
    const section = details ? details.querySelector("[data-search-section]") : null;
    if (section) clearControls(section);
  }});
}}

search_include_prerelease.addEventListener("change", scheduleSearch);
search_product.addEventListener("change", () => {{
  if(search_product.value === "プレリリース") search_include_prerelease.checked = true;
}});

search_include_parallel.addEventListener("change", () => {{
  refreshRarityOptions();
  scheduleSearch();
}});

for (const control of document.querySelectorAll(
  '#search_q,#search_product,#search_group,#search_type,#search_unit,#search_rarity,' +
  '#search_cost_min,#search_cost_max,#search_score_min,#search_score_max,' +
  '#search_blade_min,#search_blade_max,#search_effect,' +
  'input[id^="heart_"],input[id^="required_"],' +
  'input[name="heart_mode"],input[name="required_heart_mode"],' +
  'input[name="blade_heart_mode"],input[name="blade_heart_token"],input[name="ability_type"]'
)) {{
  control.addEventListener(control.tagName === "SELECT" || control.type === "radio" || control.type === "checkbox" ? "change" : "input", scheduleSearch);
}}

search_q.addEventListener("keydown",event=>{{if(event.key==="Enter"){{event.preventDefault();searchCards()}}}});

function initializeDeckEditorWithCustomSelects() {{
  initializeDeckEditor();
  try {{
    enhanceSearchSelects();
  }} catch(error) {{
    console.error("custom select initialization failed",error);
    for(const select of document.querySelectorAll("select.custom-select-native")) {{
      select.classList.remove("custom-select-native");
    }}
  }}
}}
if(document.readyState==="loading") {{
  document.addEventListener("DOMContentLoaded",initializeDeckEditorWithCustomSelects,{{once:true}});
}} else {{
  initializeDeckEditorWithCustomSelects();
}}
</script>
"""

    def update_body(self) -> str:
        return """
<style>
.update-progress-wrap {
  margin:18px 0;
  padding:16px;
  border:1px solid var(--line);
  border-radius:12px;
  background:var(--panel2);
}
.update-progress-track {
  height:14px;
  overflow:hidden;
  border-radius:999px;
  background:#0d1015;
}
.update-progress-bar {
  width:0%;
  height:100%;
  border-radius:999px;
  background:linear-gradient(90deg,#4c8dff,#8cc8ff);
  transition:width .45s ease;
  position:relative;
}
.update-progress-bar.running::after {
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.45),transparent);
  animation:updateSweep 1.25s linear infinite;
}
@keyframes updateSweep {
  from {transform:translateX(-100%)}
  to {transform:translateX(100%)}
}
.update-stage {
  display:flex;
  justify-content:space-between;
  gap:12px;
  flex-wrap:wrap;
  margin-bottom:10px;
}
.update-stats {
  display:grid;
  grid-template-columns:repeat(4,minmax(130px,1fr));
  gap:8px;
  margin-top:12px;
}
.update-stat {
  padding:9px;
  border:1px solid var(--line);
  border-radius:8px;
}
.update-stat strong {display:block;font-size:18px}
.startup-update-dialog {
  display:none;
  margin:0 0 16px;
  padding:14px;
  border:1px solid var(--warn);
  border-radius:10px;
  background:#292517;
}
.startup-update-dialog.open { display:block; }
.startup-update-actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
#jobLog {
  max-height:360px;
  overflow:auto;
  white-space:pre-wrap;
}
@media(max-width:700px) {
  .update-stats {grid-template-columns:repeat(2,minmax(120px,1fr))}
}
</style>
<section class="panel">
<h2>データ更新</h2>
<p>新しいカード情報、商品情報、先行公開カード、カード画像を順番に確認します。取得後はグループ・ユニット・カード種別・数値項目などの定義済みフィールドを自動補正し、監査結果も保存します。処理には時間がかかる場合があります。</p>
<p class="status">起動時更新確認が有効な場合、この画面で確認してから更新を開始できます。更新では、初回に必要なPython追加部品を確認し、外部サイトからカード情報と画像情報を取得します。</p>
<div id="startupUpdateDialog" class="startup-update-dialog">
  <strong>カードデータの更新を確認しますか？</strong>
  <p class="status">初回はPython追加部品の導入が必要になる場合があります。その後、公式情報・Wiki・画像取得先などの外部サイトへアクセスします。時間がかかる場合があります。許可した場合のみ更新を開始します。</p>
  <div class="startup-update-actions">
    <button type="button" onclick="confirmStartupUpdate()">更新する</button>
    <button type="button" class="secondary" onclick="dismissStartupUpdate()">あとで</button>
  </div>
</div>
<button id="startButton" onclick="startUpdate()">更新開始</button>

<div class="update-progress-wrap">
  <div class="update-stage">
    <strong id="jobStage">待機中</strong>
    <strong id="jobPercent">0%</strong>
  </div>
  <div class="update-progress-track">
    <div id="jobProgressBar" class="update-progress-bar"></div>
  </div>
  <p id="jobMessage" class="status">更新は開始されていません。</p>
  <div class="update-stats">
    <div class="update-stat"><span>状態</span><strong id="jobStatus">idle</strong></div>
    <div class="update-stat"><span>経過時間</span><strong id="jobElapsed">0:00</strong></div>
    <div class="update-stat"><span>最終ログ</span><strong id="jobSilence">-</strong></div>
    <div class="update-stat"><span>ログ行数</span><strong id="jobLineCount">0</strong></div>
  </div>
</div>

<h3>最新ログ</h3>
<pre id="jobLog">未実行</pre>
</section>
<script>
function formatDuration(seconds) {
  const value=Math.max(0,Number(seconds)||0);
  const hours=Math.floor(value/3600);
  const minutes=Math.floor((value%3600)/60);
  const secs=value%60;
  if(hours) return `${hours}:${String(minutes).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
  return `${minutes}:${String(secs).padStart(2,'0')}`;
}

async function startUpdate() {
  const button=document.getElementById("startButton");
  button.disabled=true;
  document.getElementById("jobMessage").textContent="更新処理を開始しています...";
  try {
    const res=await fetch("/api/update/start",{method:"POST"});
    const data=await res.json();
    document.getElementById("jobMessage").textContent=data.message;
  } catch(e) {
    document.getElementById("jobMessage").textContent=String(e);
  }
  await poll();
}

function isStartupUpdatePrompt() {
  const params=new URLSearchParams(location.search);
  return params.get("startup")==="1";
}

function setStartupDialog(open) {
  const dialog=document.getElementById("startupUpdateDialog");
  if(dialog) dialog.classList.toggle("open",!!open);
}

async function confirmStartupUpdate() {
  setStartupDialog(false);
  const button=document.getElementById("startButton");
  button.disabled=true;
  document.getElementById("jobMessage").textContent="カードデータ更新を開始しています...";
  try {
    const res=await fetch("/api/update/startup-confirmed",{method:"POST"});
    const data=await res.json();
    document.getElementById("jobMessage").textContent=data.message;
  } catch(e) {
    document.getElementById("jobMessage").textContent=String(e);
  }
  await poll();
}

function dismissStartupUpdate() {
  setStartupDialog(false);
  document.getElementById("jobMessage").textContent="起動時更新確認はキャンセルされました。必要なときは「更新開始」を押してください。";
  history.replaceState(null,"",location.pathname);
}

async function poll() {
  try {
    const res=await fetch("/api/update/status",{cache:"no-store"});
    const data=await res.json();
    const running=data.status==="running";
    const percent=Math.max(0,Math.min(100,Number(data.progress_percent)||0));
    const bar=document.getElementById("jobProgressBar");

    document.getElementById("jobStage").textContent=data.stage||"待機中";
    document.getElementById("jobPercent").textContent=`${percent}%`;
    document.getElementById("jobMessage").textContent=data.message||"";
    document.getElementById("jobStatus").textContent=data.status||"idle";
    document.getElementById("jobElapsed").textContent=formatDuration(data.elapsed_seconds);
    document.getElementById("jobSilence").textContent=
      data.status==="running" ? `${data.seconds_since_output||0}秒前` : "-";
    document.getElementById("jobLineCount").textContent=String(data.line_count||0);

    bar.style.width=`${percent}%`;
    bar.classList.toggle("running",running);
    document.getElementById("jobMessage").className=
      "status "+(data.stale?"warn":data.status==="success"?"ok":data.status==="failed"?"bad":"");

    const log=document.getElementById("jobLog");
    const nearBottom=log.scrollHeight-log.scrollTop-log.clientHeight<60;
    log.textContent=(data.lines||[]).join("\\n")||"ログなし";
    if(nearBottom) log.scrollTop=log.scrollHeight;

    document.getElementById("startButton").disabled=running;
    if(running) setTimeout(poll,1000);
  } catch(e) {
    document.getElementById("jobMessage").className="status bad";
    document.getElementById("jobMessage").textContent=String(e);
    setTimeout(poll,3000);
  }
}
if(isStartupUpdatePrompt()) {
  setStartupDialog(true);
  document.getElementById("jobStage").textContent="確認待ち";
  document.getElementById("jobMessage").textContent="カードデータ更新はまだ開始していません。確認してから開始できます。";
} else {
  setStartupDialog(false);
}
poll();
</script>
"""

    def logs_body(self) -> str:
        logs = self.app.list_logs()
        if not logs:
            rows = "<tr><td colspan='4' class='warn'>ログファイルはまだありません。</td></tr>"
        else:
            rows = "".join(
                f"<tr><td>{html.escape(item['name'])}</td><td><code>{html.escape(item['path'])}</code></td><td>{item['size']}</td><td>{html.escape(item['modified'])}</td></tr>"
                for item in logs
            )
        return f"""
<section class="panel">
<h2>ログ管理</h2>
<p>現在はファイル一覧まで実装しています。対局イベント表示と比較は後続実装です。</p>
<table>
<thead><tr><th>名前</th><th>パス</th><th>bytes</th><th>更新日時</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
"""

    def settings_body(self) -> str:
        settings = self.app.load_settings()
        player = html.escape(str(settings.get("player_id") or ""))
        key_length = int(settings.get("remote_key_length") or 4)
        auto_update_checked = "checked" if bool(settings.get("auto_update_on_startup", True)) else ""
        options = "".join(
            f'<option value="{n}" {"selected" if n == key_length else ""}>{n}桁</option>'
            for n in (3, 4, 5)
        )
        return f"""
<section class="panel">
<h2>設定</h2>
<form method="post" action="/settings/save">
<label for="player_id">プレイヤー識別子</label>
<input id="player_id" name="player_id" maxlength="24" value="{player}" required>
<label for="remote_key_length">リモート対戦キー長</label>
<select id="remote_key_length" name="remote_key_length">{options}</select>
<label><input type="checkbox" name="auto_update_on_startup" value="1" {auto_update_checked} style="width:auto;margin-right:8px">起動時にカードデータ更新を確認する</label>
<p class="status">有効な場合、アプリ起動後にデータ更新ページと同じ処理を自動で開始します。失敗した場合も、現在のカードデータでアプリは起動したままになります。</p>
<p class="status">画面表示サイズと操作部サイズは、右上の「簡易設定」からページ遷移なしで変更できます。</p>
<div style="margin-top:16px"><button type="submit">保存</button></div>
</form>
<p class="status">保存先：<code>{html.escape(SETTINGS_PATH)}</code></p>
</section>
"""

    def diagnostics_body(self) -> str:
        diag = self.app.diagnostics()
        def flag(value: bool) -> str:
            return "<span class='ok'>OK</span>" if value else "<span class='bad'>MISSING</span>"
        return f"""
<section class="panel">
<h2>診断・バージョン</h2>
<table>
<tr><th>BUILD_TAG</th><td><code>{html.escape(str(diag['build_tag']))}</code></td></tr>
<tr><th>作業ルート</th><td><code>{html.escape(str(diag['root']))}</code></td></tr>
<tr><th>Python</th><td>{html.escape(str(diag['python']))}</td></tr>
<tr><th>OS</th><td>{html.escape(str(diag['platform']))}</td></tr>
<tr><th>手動シミュレータ</th><td>{flag(bool(diag['manual_script']))}</td></tr>
<tr><th>DB更新スクリプト</th><td>{flag(bool(diag['update_script']))}</td></tr>
<tr><th>compiled DB</th><td>{flag(bool(diag['compiled_db']))}</td></tr>
<tr><th>DB件数</th><td>{html.escape(str(diag['card_count']))}</td></tr>
<tr><th>DB読込エラー</th><td>{html.escape(str(diag['db_error'] or '-'))}</td></tr>
<tr><th>カード画像数</th><td>{html.escape(str(diag['image_count']))}</td></tr>
<tr><th>画像フォルダ</th><td><pre>{html.escape(json.dumps(diag['image_directories'], ensure_ascii=False, indent=2))}</pre></td></tr>
<tr><th>デッキ数</th><td>{html.escape(str(diag['deck_count']))}</td></tr>
<tr><th>ログ数</th><td>{html.escape(str(diag['log_count']))}</td></tr>
</table>
</section>
"""


class LovecaHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        handler: type[BaseHTTPRequestHandler],
        app_state: AppState,
    ) -> None:
        super().__init__(address, handler)
        self.app_state = app_state
        self._launcher_close_lock = threading.RLock()
        self._launcher_close_timer: threading.Timer | None = None
        self._launcher_close_generation = 0

    def note_launcher_activity(self) -> None:
        """Cancel a pending close-triggered shutdown after navigation/activity."""
        with self._launcher_close_lock:
            self._launcher_close_generation += 1
            timer = self._launcher_close_timer
            self._launcher_close_timer = None
        if timer is not None:
            timer.cancel()

    def schedule_launcher_close_shutdown(self, delay: float = 2.5) -> None:
        """Stop the app if no launcher page becomes active after pagehide."""
        with self._launcher_close_lock:
            self._launcher_close_generation += 1
            generation = self._launcher_close_generation
            previous = self._launcher_close_timer
            timer = threading.Timer(
                delay,
                self._shutdown_after_launcher_close,
                args=(generation,),
            )
            timer.daemon = True
            self._launcher_close_timer = timer
        if previous is not None:
            previous.cancel()
        timer.start()

    def _shutdown_after_launcher_close(self, generation: int) -> None:
        with self._launcher_close_lock:
            if generation != self._launcher_close_generation:
                return
            self._launcher_close_timer = None
        try:
            self.app_state.stop_all_child_processes()
        finally:
            self.force_shutdown_process()

    def force_shutdown_process(self) -> None:
        # Let the shutdown response reach the browser, then close the listening
        # socket and terminate the launcher process even if a library thread is
        # still alive.
        time.sleep(0.35)
        try:
            self.shutdown()
        finally:
            try:
                self.server_close()
            finally:
                os._exit(0)
