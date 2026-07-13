#!/usr/bin/env python3
# BUILD_TAG = "loveca_app_launcher_menu_remote_key_20260713a"
"""
Loveca application launcher (phase 1).

- Does not modify llocg_ui runtime files.
- Launches the existing manual simulator.
- Runs the existing database update pipeline.
- Lists existing deck files.
- Creates short remote-session keys (3-5 alphanumeric characters).
- Shows basic diagnostics.

Standard-library only.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import platform
import secrets
import string
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


BUILD_TAG = "loveca_app_launcher_menu_remote_key_20260713a"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
SESSION_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
SESSION_DIR = "user_data/remote_sessions"
SETTINGS_PATH = "user_data/settings.json"

MANUAL_SCRIPT = "run_llocg_ui_web.py"
UPDATE_SCRIPT = "llocg_update_database.py"
DB_COMPILED = "llocg_db_out_full/cards_compiled_v7h.json"

DECK_PATTERNS = (
    "sim_decks/deck_*.json",
    "sim_decks/deck_*.tsv",
    "decklists/*.tsv",
    "decklists/deck_*.tsv",
    "decklists/*.txt",
)


def utc_now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_player_id(raw: str) -> str:
    filtered = "".join(ch for ch in raw.strip() if ch.isalnum() or ch in "-_")
    return filtered[:24] or "PLAYER"


def create_short_key(length: int = 4) -> str:
    if length < 3 or length > 5:
        raise ValueError("key length must be between 3 and 5")
    return "".join(secrets.choice(SESSION_ALPHABET) for _ in range(length))


def compute_session_uid(date_text: str, player_id: str, short_key: str) -> str:
    material = f"{date_text}|{player_id}|{short_key}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


@dataclass
class JobState:
    name: str = ""
    status: str = "idle"
    started_at: str = ""
    finished_at: str = ""
    returncode: int | None = None
    lines: list[str] = field(default_factory=list)

    def reset(self, name: str) -> None:
        self.name = name
        self.status = "running"
        self.started_at = utc_now_iso()
        self.finished_at = ""
        self.returncode = None
        self.lines = []

    def append(self, line: str) -> None:
        self.lines.append(line.rstrip("\n"))
        if len(self.lines) > 500:
            del self.lines[:100]


class AppState:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.lock = threading.RLock()
        self.update_job = JobState()
        self.manual_process: subprocess.Popen[str] | None = None

    def path(self, relative: str) -> Path:
        return self.root / relative

    def list_decks(self) -> list[dict[str, Any]]:
        found: dict[str, Path] = {}
        for pattern in DECK_PATTERNS:
            for path in self.root.glob(pattern):
                if path.is_file():
                    found[str(path.resolve())] = path
        decks = []
        for path in sorted(found.values(), key=lambda p: (p.name.lower(), str(p))):
            stat = path.stat()
            decks.append(
                {
                    "name": path.stem,
                    "path": str(path.relative_to(self.root)),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
                }
            )
        return decks

    def diagnostics(self) -> dict[str, Any]:
        compiled = self.path(DB_COMPILED)
        card_count: int | None = None
        db_error = ""
        if compiled.exists():
            try:
                raw = json.loads(compiled.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    card_count = len(raw)
                elif isinstance(raw, dict):
                    cards = raw.get("cards")
                    if isinstance(cards, list):
                        card_count = len(cards)
                    else:
                        card_count = len(raw)
            except Exception as exc:
                db_error = f"{type(exc).__name__}: {exc}"

        image_dir = self.path("llocg_db_out_full/card_images")
        image_count = 0
        if image_dir.is_dir():
            image_count = sum(
                1 for p in image_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
            )

        return {
            "build_tag": BUILD_TAG,
            "root": str(self.root),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "manual_script": self.path(MANUAL_SCRIPT).exists(),
            "update_script": self.path(UPDATE_SCRIPT).exists(),
            "compiled_db": compiled.exists(),
            "card_count": card_count,
            "db_error": db_error,
            "image_count": image_count,
            "deck_count": len(self.list_decks()),
        }

    def start_manual(self) -> tuple[bool, str]:
        script = self.path(MANUAL_SCRIPT)
        if not script.exists():
            return False, f"{MANUAL_SCRIPT} が見つかりません。"

        with self.lock:
            if self.manual_process and self.manual_process.poll() is None:
                return False, "手動シミュレータはすでに起動しています。"
            try:
                self.manual_process = subprocess.Popen(
                    [sys.executable, str(script)],
                    cwd=str(self.root),
                    text=True,
                )
            except Exception as exc:
                return False, f"起動に失敗しました: {type(exc).__name__}: {exc}"
        return True, "手動シミュレータを起動しました。"

    def start_update(self) -> tuple[bool, str]:
        script = self.path(UPDATE_SCRIPT)
        if not script.exists():
            return False, f"{UPDATE_SCRIPT} が見つかりません。"

        with self.lock:
            if self.update_job.status == "running":
                return False, "データ更新はすでに実行中です。"
            self.update_job.reset("database_update")

        def worker() -> None:
            try:
                process = subprocess.Popen(
                    [sys.executable, str(script), "--require-preview-posts"],
                    cwd=str(self.root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                assert process.stdout is not None
                for line in process.stdout:
                    with self.lock:
                        self.update_job.append(line)
                returncode = process.wait()
                with self.lock:
                    self.update_job.returncode = returncode
                    self.update_job.status = "success" if returncode == 0 else "failed"
                    self.update_job.finished_at = utc_now_iso()
            except Exception as exc:
                with self.lock:
                    self.update_job.append(f"{type(exc).__name__}: {exc}")
                    self.update_job.returncode = -1
                    self.update_job.status = "failed"
                    self.update_job.finished_at = utc_now_iso()

        threading.Thread(target=worker, daemon=True).start()
        return True, "データ更新を開始しました。"

    def create_remote_session(
        self,
        player_id: str,
        key_length: int,
        short_key: str | None = None,
    ) -> dict[str, Any]:
        player = safe_player_id(player_id)
        key = (short_key or "").strip().upper()
        if key:
            if len(key) < 3 or len(key) > 5 or any(ch not in SESSION_ALPHABET for ch in key):
                raise ValueError("キーは英数字3〜5桁で入力してください。")
        else:
            key = create_short_key(key_length)

        date_text = datetime.now().astimezone().strftime("%Y%m%d")
        uid = compute_session_uid(date_text, player, key)
        record = {
            "schema_version": 1,
            "created_at": utc_now_iso(),
            "date": date_text,
            "player_id": player,
            "short_key": key,
            "session_label": f"{date_text}-{player}-{key}",
            "session_uid": uid,
            "event_integrity": "deferred",
        }

        folder = self.path(SESSION_DIR)
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / f"{record['session_label']}.json"
        target.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        record["saved_to"] = str(target.relative_to(self.root))
        return record


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
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
}
header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
header h1 { font-size: 21px; margin: 0; }
header .tag { color: var(--muted); font-size: 12px; }
main { max-width: 1120px; margin: 0 auto; padding: 24px; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
  gap: 16px;
}
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
label { display: block; color: var(--muted); margin: 12px 0 6px; }
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #0d1015;
  padding: 12px;
  border-radius: 9px;
  max-height: 430px;
  overflow: auto;
}
.status { margin-top: 12px; color: var(--muted); }
.ok { color: var(--ok); }
.bad { color: var(--bad); }
.warn { color: var(--warn); }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 9px; border-bottom: 1px solid var(--line); }
nav a { color: var(--text); margin-left: 14px; }
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 18px; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 640px) { .row { grid-template-columns: 1fr; } }
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
<header>
  <h1>Loveca Application</h1>
  <div>
    <span class="tag">{html.escape(BUILD_TAG)}</span>
    <nav><a href="/">メニュー</a><a href="/remote">リモート対戦</a><a href="/decks">デッキ</a><a href="/update">更新</a><a href="/diagnostics">診断</a></nav>
  </div>
</header>
<main>{body}</main>
</body>
</html>"""
    return doc.encode("utf-8")


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
        self.wfile.write(payload)

    def send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def read_form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        parsed = parse_qs(raw)
        return {key: values[0] for key, values in parsed.items() if values}

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_html(page("Loveca", self.home_body()))
        elif path == "/remote":
            self.send_html(page("リモート対戦", self.remote_body()))
        elif path == "/decks":
            self.send_html(page("デッキ管理", self.decks_body()))
        elif path == "/update":
            self.send_html(page("データ更新", self.update_body()))
        elif path == "/diagnostics":
            self.send_html(page("診断", self.diagnostics_body()))
        elif path == "/api/update/status":
            with self.app.lock:
                job = self.app.update_job
                self.send_json(
                    {
                        "name": job.name,
                        "status": job.status,
                        "started_at": job.started_at,
                        "finished_at": job.finished_at,
                        "returncode": job.returncode,
                        "lines": job.lines[-200:],
                    }
                )
        else:
            self.send_html(page("Not Found", "<h2>ページが見つかりません。</h2>"), HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/manual/start":
            ok, message = self.app.start_manual()
            self.send_json({"ok": ok, "message": message}, HTTPStatus.OK if ok else HTTPStatus.CONFLICT)
        elif path == "/api/update/start":
            ok, message = self.app.start_update()
            self.send_json({"ok": ok, "message": message}, HTTPStatus.OK if ok else HTTPStatus.CONFLICT)
        elif path == "/remote/create":
            form = self.read_form()
            try:
                key_length = int(form.get("key_length", "4"))
                record = self.app.create_remote_session(
                    player_id=form.get("player_id", ""),
                    key_length=key_length,
                    short_key=form.get("short_key") or None,
                )
                body = f"""
<section class="panel">
<h2>リモート対戦キー</h2>
<p>相手へ伝えるキー：</p>
<div style="font-size:42px;font-weight:800;letter-spacing:.18em">{html.escape(record['short_key'])}</div>
<p>ログ識別子：</p>
<pre>{html.escape(record['session_label'])}</pre>
<p class="status">保存先：{html.escape(record['saved_to'])}</p>
<p class="warn">イベント単位の差分照合は後続実装です。現段階では日付・プレイヤー識別子・短縮キーで対戦ログを対応付けます。</p>
<a class="button secondary" href="/remote">戻る</a>
</section>
"""
                self.send_html(page("リモート対戦キー", body))
            except (ValueError, OSError) as exc:
                self.send_html(
                    page("入力エラー", f"<section class='panel'><h2>作成できませんでした</h2><p class='bad'>{html.escape(str(exc))}</p><a class='button secondary' href='/remote'>戻る</a></section>"),
                    HTTPStatus.BAD_REQUEST,
                )
        else:
            self.send_json({"ok": False, "message": "unknown endpoint"}, HTTPStatus.NOT_FOUND)

    def home_body(self) -> str:
        return """
<div class="grid">
<section class="card">
  <h2>手動シミュレータ</h2>
  <p>既存の手動シミュレータを別プロセスで起動します。</p>
  <button onclick="startManual()">起動</button>
  <div id="manualStatus" class="status"></div>
</section>
<section class="card">
  <h2>リモート対戦</h2>
  <p>画面共有用パブリックウインドウと対応付ける短い対戦キーを作成します。</p>
  <a class="button" href="/remote">開く</a>
</section>
<section class="card">
  <h2>自動シミュレータ</h2>
  <p>候補手一覧・評価値・選択理由を確認する観戦モードを今後追加します。</p>
  <button disabled>準備中</button>
</section>
<section class="card">
  <h2>デッキ管理</h2>
  <p>現在のデッキファイルを検出して一覧表示します。</p>
  <a class="button" href="/decks">開く</a>
</section>
<section class="card">
  <h2>データ更新</h2>
  <p>安定化済みのDB・画像更新パイプラインを実行します。</p>
  <a class="button" href="/update">開く</a>
</section>
<section class="card">
  <h2>ログ管理</h2>
  <p>対局ログ、共有ログ、AI観戦ログを今後まとめます。</p>
  <button disabled>準備中</button>
</section>
<section class="card">
  <h2>設定</h2>
  <p>UI倍率、保存先、更新設定、開発者モードを今後追加します。</p>
  <button disabled>準備中</button>
</section>
<section class="card">
  <h2>診断・バージョン</h2>
  <p>スクリプト、DB、画像、デッキの検出状況を表示します。</p>
  <a class="button" href="/diagnostics">開く</a>
</section>
</div>
<script>
async function startManual() {
  const box = document.getElementById("manualStatus");
  box.textContent = "起動中...";
  try {
    const res = await fetch("/api/manual/start", {method:"POST"});
    const data = await res.json();
    box.className = "status " + (data.ok ? "ok" : "bad");
    box.textContent = data.message;
  } catch (e) {
    box.className = "status bad";
    box.textContent = String(e);
  }
}
</script>
"""

    def remote_body(self) -> str:
        return """
<section class="panel">
<h2>リモート対戦セッション</h2>
<p>キーは英数字3〜5桁です。ログ上では日付・プレイヤー識別子・キーを結合して区別します。</p>
<form method="post" action="/remote/create">
  <div class="row">
    <div>
      <label for="player_id">プレイヤー識別子</label>
      <input id="player_id" name="player_id" maxlength="24" required placeholder="TAKESHI">
    </div>
    <div>
      <label for="key_length">自動生成するキー長</label>
      <select id="key_length" name="key_length">
        <option value="3">3桁</option>
        <option value="4" selected>4桁</option>
        <option value="5">5桁</option>
      </select>
    </div>
  </div>
  <label for="short_key">相手から受け取ったキー（任意）</label>
  <input id="short_key" name="short_key" minlength="3" maxlength="5" placeholder="空欄なら自動生成">
  <div style="margin-top:16px"><button type="submit">セッションを作成</button></div>
</form>
</section>
"""

    def decks_body(self) -> str:
        decks = self.app.list_decks()
        if not decks:
            rows = "<tr><td colspan='4' class='warn'>既存デッキが見つかりません。</td></tr>"
        else:
            rows = "".join(
                f"<tr><td>{html.escape(deck['name'])}</td><td><code>{html.escape(deck['path'])}</code></td><td>{deck['size']}</td><td>{html.escape(deck['modified'])}</td></tr>"
                for deck in decks
            )
        return f"""
<section class="panel">
<h2>検出済みデッキ</h2>
<p>初期版では既存ファイルの一覧表示のみです。編集・検証・シミュレータへの受け渡しは次段階で追加します。</p>
<table>
<thead><tr><th>名前</th><th>パス</th><th>bytes</th><th>更新日時</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
"""

    def update_body(self) -> str:
        return """
<section class="panel">
<h2>データ更新</h2>
<p><code>python3 ./llocg_update_database.py --require-preview-posts</code> を別プロセスで実行します。</p>
<button id="startButton" onclick="startUpdate()">更新開始</button>
<div id="jobMeta" class="status"></div>
<pre id="jobLog">未実行</pre>
</section>
<script>
async function startUpdate() {
  const button = document.getElementById("startButton");
  button.disabled = true;
  try {
    const res = await fetch("/api/update/start", {method:"POST"});
    const data = await res.json();
    document.getElementById("jobMeta").textContent = data.message;
  } catch (e) {
    document.getElementById("jobMeta").textContent = String(e);
  }
  await poll();
}
async function poll() {
  try {
    const res = await fetch("/api/update/status", {cache:"no-store"});
    const data = await res.json();
    document.getElementById("jobMeta").textContent =
      `状態: ${data.status} / 開始: ${data.started_at || "-"} / 終了: ${data.finished_at || "-"} / code: ${data.returncode ?? "-"}`;
    document.getElementById("jobLog").textContent = (data.lines || []).join("\\n") || "ログなし";
    const running = data.status === "running";
    document.getElementById("startButton").disabled = running;
    if (running) setTimeout(poll, 1200);
  } catch (e) {
    document.getElementById("jobMeta").textContent = String(e);
  }
}
poll();
</script>
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
<tr><th>デッキ数</th><td>{html.escape(str(diag['deck_count']))}</td></tr>
</table>
</section>
"""


class LovecaHTTPServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], handler: type[BaseHTTPRequestHandler], app_state: AppState) -> None:
        super().__init__(address, handler)
        self.app_state = app_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loveca application launcher")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent, help="Loveca project root")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.exists():
        print(f"[ERROR] root does not exist: {root}", file=sys.stderr)
        return 2

    app_state = AppState(root)
    server = LovecaHTTPServer((args.host, args.port), Handler, app_state)
    url = f"http://{args.host}:{args.port}/"
    print(f"[LOVECА APP] BUILD_TAG={BUILD_TAG}")
    print(f"[LOVECА APP] root={root}")
    print(f"[LOVECА APP] open={url}")
    print("[LOVECА APP] stop with Ctrl+C")

    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[LOVECА APP] stopping")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
