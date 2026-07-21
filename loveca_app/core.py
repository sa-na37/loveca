#!/usr/bin/env python3
# BUILD_TAG = "hide_update_console_window_20260721a"
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
import csv
import io
import hashlib
import html
import json
import re
import mimetypes
import os
import random
import platform
import secrets
import shutil
import signal
import socket
import string
import subprocess
import sys
import threading
import tempfile
import unicodedata
import time
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


BUILD_TAG = "hide_update_console_window_20260721a"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8875
SESSION_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
SESSION_DIR = "user_data/remote_sessions"
SETTINGS_PATH = "user_data/settings.json"
APP_LOG_DIR = "user_data/logs"
RUNTIME_DECK_BRIDGE = "user_data/runtime/selected_deck.json"
DECK_IMPORT_STAGING_DIR = "user_data/runtime/deck_imports"
PRIMARY_DECK_DIR = "llocg_db_out_full/decklists"
CARD_IMAGE_DIRS = (
    "llocg_db_out_full/card_images",
    "card_images",
)
PREVIEW_CARD_IMAGE_DIR = "llocg_db_out_full/preview_card_images"

MANUAL_SCRIPT = "run_llocg_ui_web.py"

# Debug/start overrides must never leak from the shell into a normal match.
NORMAL_MATCH_UNSET_ENV = (
    "LLOCG_START_STAGE",
    "LLOCG_START_STAGE_L",
    "LLOCG_START_STAGE_C",
    "LLOCG_START_STAGE_R",
    "LLOCG_START_HAND",
    "LLOCG_START_HAND_SIZE",
    "LLOCG_START_SHUFFLE",
    "LLOCG_START_GREEN",
    "LLOCG_START_SUCCESS",
    "LLOCG_START_RESOLVE",
    "LLOCG_START_DECK_TOP",
    "LLOCG_START_DECK_EXACT",
    "LLOCG_START_DECK_EXACT_STRICT",
    "LLOCG_START_PHASE",
    "LLOCG_START_TURN",
    "LLOCG_START_ENERGY_ACTIVE",
    "LLOCG_START_ENERGY_WAIT",
    "LLOCG_DEBUG_PRESET",
    "LLOCG_START_DEBUG",
    "LLOCG_DEBUG_LIVE_IN_HAND",
    "LLOCG_DEBUG_MEMBER_IN_HAND",
)
UPDATE_SCRIPT = "llocg_update_database.py"
FIELD_SCHEMA_PATH = "manual_overrides/loveca_field_schema.json"
DB_COMPILED = "llocg_db_out_full/cards_compiled_v7h.json"
DB_MIN_JSON = "llocg_db_out_full/cards_min_tokv1.json"
DB_MIN_CSV = "llocg_db_out_full/cards_min_tokv1.csv"
PREVIEW_MANIFEST = "llocg_db_out_full/official_preview_image_manifest.json"
PRODUCT_CATALOG = "llocg_db_out_full/product_catalog.json"

DECK_PATTERNS = (
    "llocg_db_out_full/decklists/deck_*.tsv",
    "llocg_db_out_full/decklists/*.tsv",
    "llocg_db_out_full/decklists/*.txt",
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


def compute_match_uid(date_text: str, short_key: str) -> str:
    """Shared identifier that must match on both players' records."""
    material = f"{date_text}|{short_key}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def compute_session_uid(date_text: str, player_id: str, short_key: str) -> str:
    """Participant-specific identifier used to detect duplicated records."""
    material = f"{date_text}|{player_id}|{short_key}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def reserve_free_local_port(host: str = DEFAULT_HOST) -> int:
    """Return an unused local TCP port for the simulator process."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def console_python_executable() -> str:
    """Return a console Python executable for subprocesses that must log output."""
    exe = Path(sys.executable or "")
    if platform.system() == "Windows" and exe.name.lower() == "pythonw.exe":
        candidate = exe.with_name("python.exe")
        if candidate.exists():
            return str(candidate)
    return sys.executable or "python3"


def no_window_subprocess_kwargs() -> dict[str, Any]:
    if platform.system() != "Windows":
        return {}
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return {"creationflags": flags} if flags else {}


@dataclass
class JobState:
    name: str = ""
    status: str = "idle"
    started_at: str = ""
    finished_at: str = ""
    returncode: int | None = None
    lines: list[str] = field(default_factory=list)
    started_monotonic: float = 0.0
    last_output_monotonic: float = 0.0
    stage: str = ""
    progress_percent: int = 0
    message: str = ""

    def reset(self, name: str) -> None:
        now = time.monotonic()
        self.name = name
        self.status = "running"
        self.started_at = utc_now_iso()
        self.finished_at = ""
        self.returncode = None
        self.lines = []
        self.started_monotonic = now
        self.last_output_monotonic = now
        self.stage = "更新準備"
        self.progress_percent = 2
        self.message = "更新処理を準備しています。"

    def append(self, line: str) -> None:
        clean = line.rstrip("\n")
        self.lines.append(clean)
        self.last_output_monotonic = time.monotonic()
        if len(self.lines) > 500:
            del self.lines[:100]
        self._update_stage_from_line(clean)

    def _update_stage_from_line(self, line: str) -> None:
        upper = line.upper()
        stage = self.stage
        percent = self.progress_percent
        message = self.message

        rules = (
            (("PREFETCH_OFFICIAL_POSTS", "WIKI-OFFICIAL-POSTS"), "公式公開情報の確認", 8,
             "公開済み・公開予定カードの情報を確認しています。"),
            (("PREVIEW-MANIFEST", "PREVIEW_MANIFEST"), "先行公開カードの整理", 16,
             "先行公開カードの一覧を整理しています。"),
            (("WIKI", "SCRAPE"), "カード情報の取得", 30,
             "カードテキストと商品情報を取得しています。"),
            (("COMPILE", "COMPILED", "DB GENERATION"), "カードデータの構築", 55,
             "取得した情報からカードデータを構築しています。"),
            (("AUDIT", "CONSISTENCY"), "データ整合性の確認", 72,
             "カード件数と生成結果を検証しています。"),
            (("FETCH", "IMAGE"), "カード画像の確認", 84,
             "不足しているカード画像を確認しています。"),
            (("DONE", "SUCCESS", "PASS"), "完了処理", 96,
             "更新結果を保存しています。"),
        )
        for needles, candidate_stage, candidate_percent, candidate_message in rules:
            if any(needle in upper for needle in needles):
                if candidate_percent >= percent:
                    stage = candidate_stage
                    percent = candidate_percent
                    message = candidate_message
                break

        self.stage = stage
        self.progress_percent = percent
        self.message = message

    def snapshot(self) -> dict[str, Any]:
        now = time.monotonic()
        elapsed = max(0, int(now - self.started_monotonic)) if self.started_monotonic else 0
        silence = max(0, int(now - self.last_output_monotonic)) if self.last_output_monotonic else 0
        stale = self.status == "running" and silence >= 30
        message = self.message
        if stale:
            message = (
                "処理は継続中ですが、{}秒間新しいログがありません。"
                "ネットワーク応答や子処理の完了を待っている可能性があります。"
            ).format(silence)
        return {
            "name": self.name,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "returncode": self.returncode,
            "lines": self.lines[-200:],
            "stage": self.stage,
            "progress_percent": self.progress_percent,
            "message": message,
            "elapsed_seconds": elapsed,
            "seconds_since_output": silence,
            "stale": stale,
            "line_count": len(self.lines),
        }


class AppState:
    # Shared rarity catalogue for selectors and image-variant handling.
    BASE_RARITY_CATALOG = (
        "SD", "CL", "N", "R", "R＋", "L", "PR", "PR＋",
    )
    PARALLEL_RARITY_CATALOG = (
        "L＋", "P", "P＋", "SEC", "SEC＋", "SECL", "SRL", "DUO",
        "AR", "RM", "RE", "PE", "PE＋", "SECE", "LLE",
        "PP", "SR", "UR", "SP",
    )
    RARITY_SORT_ORDER = {
        value: index
        for index, value in enumerate(
            BASE_RARITY_CATALOG + PARALLEL_RARITY_CATALOG
        )
    }

    def __init__(self, root: Path) -> None:
        self.root = root
        self.lock = threading.RLock()
        self.update_job = JobState()
        self.update_process: subprocess.Popen[str] | None = None
        self.manual_process: subprocess.Popen[str] | None = None
        self.manual_launch_state: dict[str, Any] = {
            "status": "idle",
            "private_url": "",
            "public_url": "",
            "remote": False,
            "message": "",
            "pid": None,
            "deck_path": "",
            "deck_name": "",
            "started_at": "",
            "simulator_host": "",
            "simulator_port": None,
            "remote_key": "",
            "remote_label": "",
            "output": [],
        }
        self._card_index_cache: dict[str, dict[str, Any]] | None = None
        self._image_index_cache: dict[str, Path] | None = None
        self._rarity_meta_cache: dict[str, dict[str, Any]] | None = None
        self._signature_normal_rarity_cache: dict[str, str] | None = None
        self._image_variants_cache: list[dict[str, Any]] | None = None
        self._variants_by_card_cache: dict[str, list[dict[str, Any]]] | None = None
        self._variant_path_cache: dict[str, Path] | None = None
        self._product_catalog_cache: dict[str, str] | None = None

    def path(self, relative: str) -> Path:
        return self.root / relative

    def _invalidate_card_data_caches(self) -> None:
        self._card_index_cache = None
        self._image_index_cache = None
        self._rarity_meta_cache = None
        self._signature_normal_rarity_cache = None
        self._image_variants_cache = None
        self._variants_by_card_cache = None
        self._variant_path_cache = None
        self._product_catalog_cache = None

    def load_settings(self) -> dict[str, Any]:
        path = self.path(SETTINGS_PATH)
        defaults: dict[str, Any] = {
            "schema_version": 1,
            "player_id": "",
            "remote_key_length": 4,
            "active_deck": "",
            "ui_scale_percent": 100,
            "control_size": "standard",
            "auto_update_on_startup": True,
        }
        if not path.exists():
            return defaults
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                defaults.update(raw)
        except Exception:
            pass
        return defaults

    def save_settings(self, patch: dict[str, Any]) -> dict[str, Any]:
        current = self.load_settings()
        current.update(patch)
        current["schema_version"] = 1
        current["updated_at"] = utc_now_iso()
        path = self.path(SETTINGS_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        return current

    def select_deck(self, relative_path: str) -> dict[str, Any]:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("プロジェクト外のファイルは選択できません。") from exc
        valid = {str((self.root / d["path"]).resolve()): d for d in self.list_decks()}
        record = valid.get(str(candidate))
        if record is None:
            raise ValueError("選択したデッキファイルが見つかりません。")
        self.save_settings({"active_deck": record["path"]})
        return record

    def list_logs(self) -> list[dict[str, Any]]:
        roots = [
            self.path(APP_LOG_DIR),
            self.path(SESSION_DIR),
            self.path("logs"),
        ]
        seen: set[str] = set()
        records: list[dict[str, Any]] = []
        for base in roots:
            if not base.is_dir():
                continue
            for path in base.rglob("*"):
                if not path.is_file():
                    continue
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                stat = path.stat()
                records.append(
                    {
                        "name": path.name,
                        "path": str(path.relative_to(self.root)),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
                    }
                )
        return sorted(records, key=lambda x: x["modified"], reverse=True)

    def _read_deck_metadata(self, deck_path: Path) -> dict[str, Any]:
        candidates = [
            deck_path.with_suffix(".meta.json"),
            deck_path.parent / f"{deck_path.stem}.meta.json",
        ]
        for meta_path in candidates:
            if not meta_path.is_file():
                continue
            try:
                raw = json.loads(meta_path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    return raw
            except Exception:
                continue
        return {}

    def deck_validation(self, relative_path: str) -> dict[str, Any]:
        try:
            path = (self.root / relative_path).resolve()
            path.relative_to(self.root)
            if not path.is_file():
                raise ValueError("選択したデッキファイルが見つかりません。")
            metadata = self._read_deck_metadata(path)
            rows: list[dict[str, str]] = []
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh, delimiter="\t")
                fields = [str(x or "").strip() for x in (reader.fieldnames or [])]
                count_key = next((x for x in ("count", "枚数", "qty", "quantity") if x in fields), "")
                card_key = next((x for x in ("card_no", "cardnumber", "card_number", "カード番号") if x in fields), "")
                rarity_key = next((x for x in ("rarity", "レアリティ") if x in fields), "")
                name_key = next((x for x in ("name", "cardname", "カード名") if x in fields), "")
                variant_key = next((x for x in ("variant_id", "image_variant_id") if x in fields), "")
                if not count_key or not card_key:
                    raise ValueError("TSVヘッダーにcountとcard_noが必要です。")
                for row in reader:
                    count = str(row.get(count_key, "") or "").strip()
                    card_no = str(row.get(card_key, "") or "").strip()
                    if not count and not card_no:
                        continue
                    rows.append({"count": count or "1", "card_no": card_no, "rarity": str(row.get(rarity_key, "") or "").strip() if rarity_key else "", "name": str(row.get(name_key, "") or "").strip() if name_key else "", "variant_id": str(row.get(variant_key, "") or "").strip() if variant_key else ""})
        except (ValueError, OSError) as exc:
            return {"valid": False, "error": str(exc), "composition": {"member": 0, "live": 0, "other": 0, "total": 0, "valid": False}, "copy_violations": {}, "card_types": 0, "metadata": {}}
        copy_totals: dict[str, int] = {}
        for index, row in enumerate(rows, start=2):
            try:
                count = int(str(row.get("count", "") or "0"))
            except ValueError:
                return {"valid": False, "error": f"{index}行目のcountが整数ではありません。", "composition": {"member": 0, "live": 0, "other": 0, "total": 0, "valid": False}, "copy_violations": {}, "card_types": len(rows), "metadata": metadata}
            card_no = str(row.get("card_no", "") or "").strip()
            if count <= 0 or not card_no or self.card_record(card_no) == {}:
                return {"valid": False, "error": f"デッキ行が不正です：{card_no or '(空欄)'}", "composition": {"member": 0, "live": 0, "other": 0, "total": 0, "valid": False}, "copy_violations": {}, "card_types": len(rows), "metadata": metadata}
            copy_totals[card_no] = copy_totals.get(card_no, 0) + count
        composition = self.deck_composition(rows)
        copy_violations = {card_no: count for card_no, count in sorted(copy_totals.items()) if count > 4}
        valid = bool(composition["valid"] and not copy_violations)
        errors: list[str] = []
        if not composition["valid"]:
            errors.append(f"メンバー {composition['member']}/48、ライブ {composition['live']}/12、その他 {composition['other']}")
        if copy_violations:
            errors.append("4枚超過：" + "、".join(f"{k}={v}枚" for k, v in copy_violations.items()))
        return {"valid": valid, "error": " / ".join(errors), "composition": composition, "copy_violations": copy_violations, "copy_totals": copy_totals, "card_types": len(rows), "metadata": metadata, "rows": rows}

    def prepare_runtime_deck(self, relative_path: str) -> dict[str, Any]:
        selected = self.select_deck(relative_path)
        validation = self.deck_validation(selected["path"])
        if not validation["valid"]:
            raise ValueError("デッキ構成が不正なため起動できません：" + (validation["error"] or "検証失敗"))
        exact_cards: list[str] = []
        variants: list[dict[str, Any]] = []
        for row in validation["rows"]:
            count = int(row["count"]); card_no = str(row["card_no"])
            exact_cards.extend([card_no] * count)
            variants.append({"card_no": card_no, "count": count, "rarity": str(row.get("rarity", "") or ""), "variant_id": str(row.get("variant_id", "") or "")})
        payload = {"schema_version": 1, "generated_at": utc_now_iso(), "deck_name": selected["name"], "deck_path": selected["path"], "cards": exact_cards, "variants": variants, "composition": validation["composition"]}
        bridge = self.path(RUNTIME_DECK_BRIDGE); bridge.parent.mkdir(parents=True, exist_ok=True)
        bridge.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["bridge_path"] = str(bridge)
        return payload

    @staticmethod
    def _normalize_deck_tags(value: Any) -> list[str]:
        if isinstance(value, str):
            source = re.split(r"[,、\n]+", value)
        elif isinstance(value, list):
            source = [str(item) for item in value]
        else:
            source = []
        tags: list[str] = []
        seen: set[str] = set()
        for raw in source:
            tag = unicodedata.normalize("NFKC", str(raw or "")).strip()
            if not tag:
                continue
            tag = tag[:24]
            key = tag.casefold()
            if key in seen:
                continue
            seen.add(key)
            tags.append(tag)
            if len(tags) >= 12:
                break
        return tags

    @staticmethod
    def _new_deck_id() -> str:
        return secrets.token_hex(10)

    def _new_unique_deck_target(self, deck_dir: Path) -> tuple[str, Path]:
        for _ in range(100):
            deck_id = self._new_deck_id()
            target = deck_dir / "deck_{}.tsv".format(deck_id)
            if not target.exists() and not target.with_suffix(".meta.json").exists():
                return deck_id, target
        raise ValueError("一意なデッキ保存先を作成できませんでした。")

    def list_decks(self) -> list[dict[str, Any]]:
        found: dict[str, Path] = {}
        for pattern in DECK_PATTERNS:
            for path in self.root.glob(pattern):
                if path.is_file():
                    found[str(path.resolve())] = path
        decks = []
        for path in sorted(found.values(), key=lambda p: (p.name.lower(), str(p))):
            stat = path.stat()
            metadata = self._read_deck_metadata(path)
            deck_code = str(metadata.get("deck_code") or path.stem.removeprefix("deck_"))
            deck_name = str(metadata.get("deck_name") or path.stem)
            relative_path = str(path.relative_to(self.root))
            validation = self.deck_validation(relative_path)
            decks.append({
                "name": deck_name,
                "code": deck_code,
                "deck_id": str(metadata.get("deck_id") or path.stem.removeprefix("deck_")),
                "tags": self._normalize_deck_tags(metadata.get("tags")),
                "source": str(metadata.get("source") or ""),
                "path": relative_path,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
                "source_url": str(metadata.get("source_url") or ""),
                "valid": bool(validation.get("valid")),
                "validation_error": str(validation.get("error") or ""),
                "composition": validation.get("composition", {}),
                "card_types": int(validation.get("card_types") or 0),
            })
        return decks

    @staticmethod
    def _records_from_json(path: Path) -> list[dict[str, Any]]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
        if isinstance(raw, list):
            records = raw
        elif isinstance(raw, dict) and isinstance(raw.get("cards"), list):
            records = raw["cards"]
        elif isinstance(raw, dict):
            records = []
            for key, value in raw.items():
                if isinstance(value, dict):
                    record = dict(value)
                    record.setdefault("cardnumber", key)
                    records.append(record)
        else:
            records = []
        return [dict(record) for record in records if isinstance(record, dict)]

    @staticmethod
    def _records_from_csv(path: Path) -> list[dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as fh:
                return [dict(row) for row in csv.DictReader(fh)]
        except Exception:
            return []

    @staticmethod
    def _card_number(record: dict[str, Any]) -> str:
        return str(
            record.get("cardnumber")
            or record.get("card_no")
            or record.get("cardNumber")
            or record.get("number")
            or ""
        ).strip()

    def load_card_index(self) -> dict[str, dict[str, Any]]:
        if self._card_index_cache is not None:
            return self._card_index_cache

        # Static card attributes live in cards_min_tokv1. The compiled DB is
        # intentionally ability-oriented and does not retain heart/cost/score
        # fields, so it is merged only as an abilities supplement.
        min_records = self._records_from_json(self.path(DB_MIN_JSON))
        if not min_records:
            min_records = self._records_from_csv(self.path(DB_MIN_CSV))
        compiled_records = self._records_from_json(self.path(DB_COMPILED))

        index: dict[str, dict[str, Any]] = {}
        for record in min_records:
            number = self._card_number(record)
            if number:
                index[number] = record

        for compiled in compiled_records:
            number = self._card_number(compiled)
            if not number:
                continue
            if number in index:
                merged = dict(compiled)
                merged.update(index[number])  # static/min fields win
                if "abilities" in compiled:
                    merged["abilities"] = compiled["abilities"]
                if "parse_status" in compiled:
                    merged["parse_status"] = compiled["parse_status"]
                index[number] = merged
            else:
                index[number] = compiled

        self._card_index_cache = index
        return index

    def card_record(self, card_no: str) -> dict[str, Any]:
        return self.load_card_index().get(card_no, {})

    @staticmethod
    def _normalize_image_key(value: str) -> str:
        decoded = unquote(value).strip().casefold()
        return "".join(ch for ch in decoded if ch.isalnum())

    def _build_image_index(self) -> dict[str, Path]:
        if self._image_index_cache is not None:
            return self._image_index_cache

        index: dict[str, Path] = {}
        allowed = {".png", ".jpg", ".jpeg", ".webp", ".avif"}

        for relative_dir in CARD_IMAGE_DIRS:
            base = self.path(relative_dir)
            if not base.is_dir():
                continue

            for image_path in base.rglob("*"):
                if not image_path.is_file() or image_path.suffix.lower() not in allowed:
                    continue

                stem = unquote(image_path.stem).strip()
                exact_key = stem.casefold()
                normalized_key = self._normalize_image_key(stem)

                # Earlier directories have higher priority.
                index.setdefault(f"exact:{exact_key}", image_path)
                if normalized_key:
                    index.setdefault(f"normalized:{normalized_key}", image_path)

                # Some fetch generations append rarity, sequence, or side
                # information after the card number. Register the leading
                # card-number-looking section as a fallback.
                separators = ("_", " ", "__")
                for separator in separators:
                    if separator in stem:
                        leading = stem.split(separator, 1)[0].strip()
                        leading_key = self._normalize_image_key(leading)
                        if leading_key:
                            index.setdefault(f"normalized:{leading_key}", image_path)

        self._image_index_cache = index
        return index

    def card_display_data(self, row: dict[str, str]) -> dict[str, str]:
        record = self.card_record(row["card_no"])
        def first(*keys: str) -> str:
            for key in keys:
                value = record.get(key)
                if value not in (None, "", [], {}):
                    if isinstance(value, (dict, list)):
                        return json.dumps(value, ensure_ascii=False)
                    return str(value)
            return ""
        return {
            "count": row["count"],
            "card_no": row["card_no"],
            "rarity": row.get("rarity", "") or first("rarity"),
            "variant_id": row.get("variant_id", ""),
            "name": row.get("name", "") or first("cardname", "name", "card_name"),
            "card_type": first("card_type", "type", "cardtype"),
            "group": first("group", "group_name", "groupname"),
            "unit": first("unit", "unit_name", "unitname"),
            "cost": first("cost"),
            "effect": first("effect", "effect_text", "text", "cardtext"),
        }

    @staticmethod
    def _record_first(record: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = record.get(key)
            if value not in (None, "", [], {}):
                if isinstance(value, (dict, list)):
                    return json.dumps(value, ensure_ascii=False)
                return str(value)
        return ""

    @staticmethod
    def _numeric_text(value: Any) -> str:
        if value in (None, "", [], {}):
            return ""
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            return str(len(value))
        return str(value)

    @staticmethod
    def _flatten_values(value: Any) -> list[str]:
        values: list[str] = []
        if value in (None, "", [], {}):
            return values
        if isinstance(value, dict):
            for key, child in value.items():
                values.append(str(key))
                values.extend(AppState._flatten_values(child))
        elif isinstance(value, list):
            for child in value:
                values.extend(AppState._flatten_values(child))
        else:
            values.append(str(value))
        return values

    @staticmethod
    def _deep_find(record: dict[str, Any], aliases: tuple[str, ...]) -> Any:
        normalized_aliases = {
            re.sub(r"[^a-z0-9]", "", alias.casefold())
            for alias in aliases
        }
        queue: list[Any] = [record]
        while queue:
            current = queue.pop(0)
            if isinstance(current, dict):
                for key, value in current.items():
                    normalized_key = re.sub(r"[^a-z0-9]", "", str(key).casefold())
                    if normalized_key in normalized_aliases and value not in (None, "", [], {}):
                        return value
                    if isinstance(value, (dict, list)):
                        queue.append(value)
            elif isinstance(current, list):
                queue.extend(item for item in current if isinstance(item, (dict, list)))
        return ""

    @staticmethod
    def _value_text(value: Any) -> str:
        if value in (None, "", [], {}):
            return ""
        if isinstance(value, (dict, list)):
            return " / ".join(AppState._flatten_values(value))
        return str(value)

    @staticmethod
    def _first_number(value: str) -> int | None:
        match = re.search(r"-?\d+", value)
        return int(match.group(0)) if match else None

    @staticmethod
    def _card_prefix(card_no: str) -> str:
        lower = card_no.casefold()
        marker_match = re.search(r"-(?:bp|pb|sd|pr|cl)\d*-", lower)
        if marker_match:
            return card_no[:marker_match.start()]
        return card_no.split("-", 1)[0]

    @staticmethod
    def _product_code(card_no: str) -> str:
        card = card_no.strip()
        prefix = AppState._card_prefix(card).upper()

        match = re.search(r"-bp(\d+)-", card, re.I)
        if match:
            return f"BP{int(match.group(1)):02d}"

        match = re.search(r"-pb(\d+)-", card, re.I)
        if match:
            mapping = {
                "PL!HS": "PBHS",
                "PL!SP": "PBSP",
                "PL!S": "PBLS",
                "PL!LS": "PBLS",
                "PL!N": "PBNJ",
                "PL!": "PBLL",
                "LL": "PBLL",
            }
            number = int(match.group(1))
            base = mapping.get(prefix)
            if base:
                return base if number == 1 else f"{base}{number:02d}"
            return f"{prefix}-PB{number:02d}"

        match = re.search(r"-sd(\d+)-", card, re.I)
        if match:
            mapping = {
                "PL!SP": "SPSD",
                "PL!N": "NSD",
                "PL!HS": "HSSD",
                "PL!LS": "LSSD",
                "PL!S": "SSD",
                "PL!": "PLSD",
            }
            return f"{mapping.get(prefix, prefix + '-SD')}{int(match.group(1)):02d}"

        match = re.search(r"-cl(\d+)-", card, re.I)
        if match:
            return f"CL{prefix.replace('PL!', '')}{int(match.group(1)):02d}"

        if re.search(r"-PR-", card, re.I):
            return "PR"
        return ""

    def _load_product_catalog(self) -> dict[str, str]:
        if self._product_catalog_cache is not None:
            return self._product_catalog_cache

        catalog: dict[str, str] = {}
        path = self.path(PRODUCT_CATALOG)
        if path.is_file():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                product_data = payload.get("products", payload) if isinstance(payload, dict) else payload
                if isinstance(product_data, dict):
                    for code, value in product_data.items():
                        if isinstance(value, str):
                            catalog[str(code).upper()] = value.strip()
                        elif isinstance(value, dict):
                            name = (
                                value.get("name")
                                or value.get("title")
                                or value.get("product_name")
                                or value.get("expansion_name")
                            )
                            if name:
                                catalog[str(code).upper()] = str(name).strip()
                elif isinstance(product_data, list):
                    for item in product_data:
                        if not isinstance(item, dict):
                            continue
                        code = item.get("code") or item.get("product_code") or item.get("expansion")
                        name = (
                            item.get("name")
                            or item.get("title")
                            or item.get("product_name")
                            or item.get("expansion_name")
                        )
                        if code and name:
                            catalog[str(code).upper()] = str(name).strip()
            except Exception as exc:
                print(f"[PRODUCT-CATALOG][WARN] failed to load {path}: {exc}")

        # Fallbacks are intentionally keyed by official expansion/folder code.
        catalog.setdefault("PBHS", "プレミアムブースター 蓮ノ空女学院スクールアイドルクラブ")
        catalog.setdefault("PBSP", "プレミアムブースター ラブライブ！スーパースター!!")
        catalog.setdefault("PBLS", "プレミアムブースター ラブライブ！サンシャイン!!")
        catalog.setdefault("PBNJ", "プレミアムブースター ラブライブ！虹ヶ咲学園スクールアイドル同好会")
        catalog.setdefault("PBLL", "プレミアムブースター ラブライブ！")
        catalog.setdefault("PR", "PRカード")

        self._product_catalog_cache = catalog
        return catalog

    def _derive_product(self, card_no: str) -> str:
        code = self._product_code(card_no)
        catalog = self._load_product_catalog()
        if code in catalog:
            return catalog[code]
        if code.startswith("BP") and code[2:].isdigit():
            return f"ブースターパック BP{int(code[2:]):02d}"
        if re.search(r"SD\d+$", code):
            return f"スタートデッキ {code}"
        if code:
            return code
        return ""

    @staticmethod
    def _heart_counts_from_value(value: Any) -> dict[str, int]:
        result = {
            "pink": 0, "red": 0, "yellow": 0, "green": 0,
            "blue": 0, "purple": 0, "all": 0, "any": 0,
        }
        aliases = {
            "pink": ("pink", "桃", "桃色"),
            "red": ("red", "赤"),
            "yellow": ("yellow", "黄", "黄色"),
            "green": ("green", "緑"),
            "blue": ("blue", "青"),
            "purple": ("purple", "紫"),
            "all": ("all", "オール"),
            "any": ("any", "任意", "無色", "colorless"),
        }

        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key)
                if isinstance(child, (int, float)):
                    count = int(child)
                else:
                    child_number = AppState._first_number(AppState._value_text(child))
                    count = child_number if child_number is not None else 1
                for canonical, names in aliases.items():
                    if any(name.casefold() in key_text.casefold() for name in names):
                        result[canonical] += max(0, count)
                        break
            return result

        text = AppState._value_text(value)
        # Primary DB format: <桃> 3, <赤> 1, <任意> 4.
        token_map = {
            "桃": "pink", "赤": "red", "黄": "yellow", "緑": "green",
            "青": "blue", "紫": "purple", "ALL": "all", "任意": "any",
            "無色": "any",
        }
        consumed_spans: list[tuple[int, int]] = []
        for match in re.finditer(r"<\s*(桃|赤|黄|緑|青|紫|ALL|任意|無色)\s*>\s*(?:(?:[:x×*]\s*)?(\d+))?", text, flags=re.I):
            raw_name = match.group(1)
            canonical = token_map.get(raw_name.upper() if raw_name.upper() == "ALL" else raw_name)
            if canonical:
                result[canonical] += int(match.group(2) or 1)
                consumed_spans.append(match.span())

        # Fallback for non-angle-bracket forms such as pink:2 or 赤×2.
        residual = text
        for start, end in reversed(consumed_spans):
            residual = residual[:start] + " " * (end - start) + residual[end:]
        for canonical, names in aliases.items():
            for name in names:
                pattern = rf"(?<![\w]){re.escape(name)}\s*(?:[:x×*]\s*)?(\d+)"
                for number in re.findall(pattern, residual, flags=re.I):
                    result[canonical] += int(number)
        return result

    @staticmethod
    def _blade_heart_tokens_from_value(value: Any) -> list[str]:
        text = AppState._value_text(value)
        candidates = [
            ("pink", ("pink", "桃")),
            ("red", ("red", "赤")),
            ("yellow", ("yellow", "黄")),
            ("green", ("green", "緑")),
            ("blue", ("blue", "青")),
            ("purple", ("purple", "紫")),
            ("all", ("all", "ALL")),
            ("draw", ("draw", "ドロー")),
            ("score", ("score", "スコア")),
            ("double_any", ("double_any", "ダブル無色", "ダブル無色")),
        ]
        found: list[str] = []
        for token, names in candidates:
            if any(name.casefold() in text.casefold() for name in names):
                found.append(token)
        return found

    @staticmethod
    def _json_dict(value: Any) -> dict[str, int]:
        if isinstance(value, dict):
            source = value
        elif isinstance(value, str):
            try:
                source = json.loads(value)
            except Exception:
                return {}
        else:
            return {}
        result: dict[str, int] = {}
        for key, child in source.items():
            try:
                result[str(key)] = int(float(child))
            except (TypeError, ValueError):
                continue
        return result

    @staticmethod
    def _json_list(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except Exception:
                pass
        return []

    @staticmethod
    def _normalize_unit_value(value: Any) -> str:
        text = unicodedata.normalize("NFKC", str(value or "")).strip()
        if not text or text == "-":
            return text
        # Remove one or more unmatched/wrapping brackets produced by source parsing.
        text = re.sub(r"^[\s\(\（]+", "", text)
        text = re.sub(r"[\s\)\）]+$", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _normalize_rarity(value: Any) -> str:
        text = unicodedata.normalize("NFKC", str(value or "")).strip().upper()
        text = text.replace("＋", "+").replace(" ", "")
        return {
            "R2": "R＋",
            "R+": "R＋",
            "RP": "R＋",
            "L2": "L＋",
            "L+": "L＋",
            "P2": "P＋",
            "P+": "P＋",
            "PE2": "PE＋",
            "PE+": "PE＋",
            "SEC2": "SEC＋",
            "SEC+": "SEC＋",
            "PR2": "PR＋",
            "PR+": "PR＋",
        }.get(text, text)

    @staticmethod
    def _card_text_signature(record: dict[str, Any]) -> str:
        fields = (
            "cardname", "card_type_norm", "card_type_raw", "work_title",
            "group", "unit", "cost", "blade", "blade_heart_raw",
            "base_hearts_raw", "required_hearts_raw", "score",
            "effect_text_norm", "effect_text_raw",
        )
        payload = {
            key: unicodedata.normalize("NFKC", str(record.get(key) or "")).strip()
            for key in fields
        }
        return hashlib.sha1(canonical_json(payload).encode("utf-8")).hexdigest()

    @classmethod
    def _walk_manifest_rarities(cls, value: Any) -> list[tuple[str, str]]:
        found: list[tuple[str, str]] = []
        if isinstance(value, dict):
            card_no = str(
                value.get("cardnumber")
                or value.get("card_no")
                or value.get("cardNumber")
                or value.get("number")
                or ""
            ).strip()
            rarity = str(
                value.get("rarity")
                or value.get("rare")
                or value.get("rarity_name")
                or ""
            ).strip()
            if card_no and rarity:
                found.append((card_no, rarity))
            for child in value.values():
                if isinstance(child, (dict, list)):
                    found.extend(cls._walk_manifest_rarities(child))
        elif isinstance(value, list):
            for child in value:
                found.extend(cls._walk_manifest_rarities(child))
        return found

    @staticmethod
    def _extract_card_number_from_image(
        image_path: Path,
        normalized_numbers: list[tuple[str, str]],
    ) -> str:
        stem_key = AppState._normalize_image_key(image_path.stem)
        for normalized, card_no in normalized_numbers:
            if stem_key.startswith(normalized):
                return card_no
        return ""

    @classmethod
    def _rarity_from_image_path(cls, image_path: Path, card_no: str) -> str:
        stem = unicodedata.normalize("NFKC", unquote(image_path.stem))
        suffix = stem
        match = re.search(re.escape(card_no), stem, flags=re.I)
        if match:
            suffix = stem[match.end():]
        token_text = " ".join(
            [suffix, image_path.parent.name, image_path.parent.parent.name]
        ).upper().replace("＋", "+")
        tokens = [
            token for token in re.split(r"[^A-Z0-9+]+", token_text)
            if token
        ]
        known = (
            "PARALLEL", "SECL", "SRL", "SEC", "DUO", "ALT", "UR", "SR",
            "SP", "PE+", "PE", "R2", "P2", "R+", "P+",
            "AR", "RM", "SD", "PR", "CL", "N", "R", "L", "P",
        )
        for wanted in known:
            if wanted in tokens:
                return cls._normalize_rarity(wanted)
        return ""

    def no_image_path(self) -> Path | None:
        for relative_dir in CARD_IMAGE_DIRS:
            base = self.path(relative_dir)
            for name in ("NoImage.PNG", "NoImage.png", "noimage.png", "noimage.PNG"):
                candidate = base / name
                if candidate.is_file():
                    return candidate
        return None

    @staticmethod
    def _base_variant_rank(card_no: str, rarity: str, path_text: str) -> tuple[int, str]:
        rarity = AppState._normalize_rarity(rarity)
        card_upper = card_no.upper()
        if "-PR-" in card_upper and rarity == "PR":
            return (0, rarity)
        if re.search(r"-CL\d*-", card_upper) and rarity == "CL":
            return (0, rarity)
        rank = {
            "N": 10, "R": 11, "R＋": 12, "L": 13,
            "SD": 14, "PR": 15, "CL": 16,
        }
        if rarity in rank:
            return (rank[rarity], rarity)
        parallel_markers = (
            "SEC", "SECL", "SR", "SRL", "UR", "PARALLEL",
            "ALT", "SP", "DUO", "AR", "RM", "P2", "P+", "P＋",
        )
        if not any(marker in path_text.upper() for marker in parallel_markers):
            return (30, rarity)
        return (50, rarity)

    def _build_image_variants(self) -> list[dict[str, Any]]:
        if self._image_variants_cache is not None:
            return self._image_variants_cache

        index = self.load_card_index()
        normalized_numbers = sorted(
            (
                (self._normalize_image_key(card_no), card_no)
                for card_no in index
                if self._normalize_image_key(card_no)
            ),
            key=lambda item: len(item[0]),
            reverse=True,
        )
        allowed = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
        variants: list[dict[str, Any]] = []
        variant_paths: dict[str, Path] = {}
        seen: set[Path] = set()

        image_sources = [
            *((relative_dir, False) for relative_dir in CARD_IMAGE_DIRS),
            (PREVIEW_CARD_IMAGE_DIR, True),
        ]
        for relative_dir, source_is_prerelease in image_sources:
            base = self.path(relative_dir)
            if not base.is_dir():
                continue
            for image_path in sorted(base.rglob("*")):
                if not image_path.is_file() or image_path.suffix.lower() not in allowed:
                    continue
                resolved = image_path.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                card_no = self._extract_card_number_from_image(image_path, normalized_numbers)
                if not card_no:
                    continue
                rarity = self._rarity_from_image_path(image_path, card_no)
                token = hashlib.sha1(
                    str(image_path.relative_to(self.root)).encode("utf-8")
                ).hexdigest()[:16]
                variant_id = f"{card_no}|{rarity or 'UNKNOWN'}|{token}"
                variant = {
                    "variant_id": variant_id,
                    "card_no": card_no,
                    "raw_rarity": rarity,
                    "is_prerelease": source_is_prerelease,
                    "image_source": "preview" if source_is_prerelease else "card_images",
                    "path": image_path,
                    "path_text": str(image_path),
                }
                variants.append(variant)
                variant_paths[variant_id] = image_path

        # Keep cards searchable even when an image is absent.
        cards_with_images = {variant["card_no"] for variant in variants}
        for card_no in index:
            if card_no not in cards_with_images:
                variants.append({
                    "variant_id": f"{card_no}|UNKNOWN|db",
                    "card_no": card_no,
                    "raw_rarity": "",
                    "is_prerelease": False,
                    "image_source": "database",
                    "path": None,
                    "path_text": "",
                })

        card_number_groups: dict[tuple[str, bool], list[dict[str, Any]]] = {}
        for variant in variants:
            identity = (variant["card_no"], bool(variant.get("is_prerelease")))
            variant["signature"] = variant["card_no"]
            card_number_groups.setdefault(identity, []).append(variant)

        for group in card_number_groups.values():
            image_group = [variant for variant in group if variant["path"] is not None]
            if len(image_group) <= 1:
                for variant in group:
                    variant["is_parallel"] = False
                    variant["base_rarity"] = variant["raw_rarity"]
                continue

            canonical = min(
                image_group,
                key=lambda variant: self._base_variant_rank(
                    variant["card_no"],
                    variant["raw_rarity"],
                    variant["path_text"],
                ),
            )
            for variant in group:
                variant["is_parallel"] = variant is not canonical
                variant["base_rarity"] = canonical["raw_rarity"]

        by_card: dict[str, list[dict[str, Any]]] = {}
        for variant in variants:
            by_card.setdefault(variant["card_no"], []).append(variant)
        for card_variants in by_card.values():
            card_variants.sort(
                key=lambda variant: (
                    bool(variant.get("is_parallel")),
                    str(variant.get("raw_rarity") or ""),
                    str(variant.get("path_text") or ""),
                )
            )

        self._image_variants_cache = variants
        self._variants_by_card_cache = by_card
        self._variant_path_cache = variant_paths
        return variants

    def card_variants(self, card_no: str) -> list[dict[str, Any]]:
        self._build_image_variants()
        assert self._variants_by_card_cache is not None
        return self._variants_by_card_cache.get(card_no, [])

    def resolve_texticon(self, token: str) -> Path | None:
        icon_dir = self.dbdir / "card_images" / "texticons"
        if not icon_dir.is_dir():
            return None

        normalized = str(token or "").strip().casefold()
        aliases = {
            "pink": ("pink", "桃", "ピンク"),
            "red": ("red", "赤"),
            "yellow": ("yellow", "黄"),
            "green": ("green", "緑"),
            "blue": ("blue", "青"),
            "purple": ("purple", "紫"),
            "all": ("all", "ALL", "オール"),
        }
        needles = aliases.get(normalized, (normalized,))
        candidates = [
            path for path in icon_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
        ]

        def score(path: Path) -> tuple[int, int, str]:
            stem = path.stem.casefold()
            best = 999
            for index, needle in enumerate(needles):
                value = str(needle).casefold()
                if stem == value:
                    best = min(best, index)
                elif value and value in stem:
                    best = min(best, 10 + index)
            return best, len(path.name), path.name.casefold()

        matched = [path for path in candidates if score(path)[0] < 999]
        return min(matched, key=score) if matched else None

    def find_card_image(
        self,
        card_no: str,
        variant_id: str = "",
        rarity: str = "",
    ) -> Path | None:
        self._build_image_variants()
        if variant_id and self._variant_path_cache is not None:
            path = self._variant_path_cache.get(variant_id)
            if path is not None:
                return path
        normalized_rarity = self._normalize_rarity(rarity)
        for variant in self.card_variants(card_no):
            if normalized_rarity and self._normalize_rarity(
                variant.get("raw_rarity")
            ) != normalized_rarity:
                continue
            path = variant.get("path")
            if isinstance(path, Path):
                return path
        return None

    def _build_rarity_metadata(self) -> dict[str, dict[str, Any]]:
        if self._rarity_meta_cache is not None:
            return self._rarity_meta_cache
        metadata: dict[str, dict[str, Any]] = {}
        for card_no in self.load_card_index():
            variants = self.card_variants(card_no)
            base = next(
                (variant for variant in variants if not variant.get("is_parallel")),
                variants[0] if variants else {},
            )
            metadata[card_no] = {
                "raw_rarity": str(base.get("raw_rarity") or ""),
                "base_rarity": str(base.get("base_rarity") or base.get("raw_rarity") or ""),
                "is_parallel": False,
                "signature": str(base.get("signature") or ""),
            }
        self._rarity_meta_cache = metadata
        return metadata

    def searchable_card(self, card_no: str, record: dict[str, Any]) -> dict[str, Any]:
        name = str(record.get("cardname") or record.get("name") or "")
        product_code = self._product_code(card_no)
        product = str(
            record.get("product_name")
            or record.get("product")
            or record.get("expansion_name")
            or record.get("expansion")
            or self._derive_product(card_no)
            or ""
        )
        rarity_meta = self._build_rarity_metadata().get(card_no, {})
        rarity = str(rarity_meta.get("base_rarity") or "")
        raw_rarity = str(rarity_meta.get("raw_rarity") or "")
        is_parallel = bool(rarity_meta.get("is_parallel"))
        card_type = str(record.get("card_type_norm") or record.get("card_type") or record.get("card_type_raw") or "")
        group = str(record.get("group") or "")
        unit = self._normalize_unit_value(record.get("unit") or "")
        work_title = str(record.get("work_title") or "")
        cost = str(record.get("cost") or "")
        score = str(record.get("score") or "")
        blade = str(record.get("blade") or "")
        effect_raw = str(
            record.get("effect_text_raw")
            or record.get("effect")
            or record.get("effect_text")
            or record.get("text")
            or record.get("cardtext")
            or ""
        )
        effect_search = str(record.get("effect_text_norm") or effect_raw)

        base_raw = record.get("base_hearts_raw", "")
        required_raw = record.get("required_hearts_raw", "")
        blade_heart_raw = record.get("blade_heart_raw", "")

        base_counts = self._json_dict(record.get("base_hearts_counts_json"))
        if not base_counts:
            base_counts = self._heart_counts_from_value(base_raw)

        required_counts = self._json_dict(record.get("required_hearts_counts_json"))
        if not required_counts:
            required_counts = self._heart_counts_from_value(required_raw)

        blade_counts = self._json_dict(record.get("blade_heart_counts_json"))
        blade_tags = self._json_list(record.get("blade_heart_tags_json"))
        blade_tokens = [key for key, value in blade_counts.items() if value > 0]
        raw_text = self._value_text(blade_heart_raw)
        blade_tokens.extend(self._blade_heart_tokens_from_value(raw_text))
        if self._first_number(str(record.get("blade_heart_draw_n") or "")) not in (None, 0):
            blade_tokens.append("draw")
        if self._first_number(str(record.get("blade_heart_score_n") or "")) not in (None, 0):
            blade_tokens.append("score")
        if self._first_number(str(record.get("blade_heart_colorless_n") or "")) not in (None, 0):
            blade_tokens.append("double_any")
        tags_text = " ".join(blade_tags).casefold()
        if "ドロー" in tags_text or "draw" in tags_text:
            blade_tokens.append("draw")
        if "スコア" in tags_text or "score" in tags_text:
            blade_tokens.append("score")
        if "無色" in tags_text or "colorless" in tags_text or "任意" in tags_text:
            blade_tokens.append("double_any")
        if not blade_tokens and raw_text.strip().casefold() in ("", "なし", "none", "-"):
            blade_tokens.append("none")

        return {
            "card_no": card_no,
            "name": name,
            "product": product,
            "product_code": product_code,
            "expansion_name": product,
            "rarity": rarity,
            "raw_rarity": raw_rarity,
            "is_parallel": is_parallel,
            "card_type": card_type,
            "group": group,
            "unit": unit,
            "work_title": work_title,
            "cost": cost,
            "cost_num": self._first_number(cost),
            "score": score,
            "score_num": self._first_number(score),
            "blade": blade,
            "blade_num": self._first_number(blade),
            "heart": self._value_text(base_raw),
            "heart_counts": {key: int(value) for key, value in base_counts.items()},
            "required_heart": self._value_text(required_raw),
            "required_heart_counts": {key: int(value) for key, value in required_counts.items()},
            "blade_heart": raw_text,
            "blade_heart_tokens": sorted(set(blade_tokens)),
            "effect": effect_raw,
            "effect_search": effect_search,
        }

    @staticmethod
    def _range_matches(value: int | None, minimum: str, maximum: str) -> bool:
        if not minimum.strip() and not maximum.strip():
            return True
        if value is None:
            return False
        if minimum.strip() and value < int(minimum):
            return False
        if maximum.strip() and value > int(maximum):
            return False
        return True

    @staticmethod
    def _heart_filter_matches(
        counts: dict[str, int],
        ranges: dict[str, tuple[str, str]],
        mode: str,
    ) -> bool:
        # AND/OR applies only between active colors. Each color's own min/max
        # is always evaluated together. When only max is supplied, minimum 1
        # is implied so that the selected color must actually be present.
        color_results: list[bool] = []
        for key, (minimum, maximum) in ranges.items():
            minimum = minimum.strip()
            maximum = maximum.strip()
            if not minimum and not maximum:
                continue
            value = int(counts.get(key, 0) or 0)
            effective_minimum = int(minimum) if minimum else (1 if maximum else 0)
            passed = value >= effective_minimum
            if maximum:
                passed = passed and value <= int(maximum)
            color_results.append(passed)
        if not color_results:
            return True
        return any(color_results) if mode == "or" else all(color_results)

    @staticmethod
    def _token_filter_matches(card_tokens: list[str], selected: list[str], mode: str) -> bool:
        if not selected:
            return True
        card_set = set(card_tokens)
        selected_set = set(selected)
        return bool(card_set & selected_set) if mode == "or" else selected_set.issubset(card_set)

    def search_cards(
        self,
        query: str = "",
        product: str = "",
        card_type: str = "",
        group: str = "",
        unit: str = "",
        rarity: str = "",
        include_parallel: bool = False,
        include_prerelease: bool = True,
        cost_min: str = "",
        cost_max: str = "",
        score_min: str = "",
        score_max: str = "",
        blade_min: str = "",
        blade_max: str = "",
        heart_ranges: dict[str, tuple[str, str]] | None = None,
        heart_mode: str = "and",
        required_heart_ranges: dict[str, tuple[str, str]] | None = None,
        required_heart_mode: str = "and",
        blade_heart_tokens: list[str] | None = None,
        blade_heart_mode: str = "or",
        ability_types: list[str] | None = None,
        effect: str = "",
        limit: int = 120,
    ) -> list[dict[str, Any]]:
        q = query.strip().casefold()
        product_filter = product.strip().casefold()
        type_filter = card_type.strip().casefold()
        group_filter = group.strip().casefold()
        unit_filter = unit.strip().casefold()
        rarity_filter = rarity.strip().casefold()
        effect_filter = effect.strip().casefold()
        heart_ranges = heart_ranges or {}
        required_heart_ranges = required_heart_ranges or {}
        blade_heart_tokens = blade_heart_tokens or []
        ability_types = [str(value).strip() for value in (ability_types or []) if str(value).strip()]

        results: list[dict[str, Any]] = []
        for card_no, record in self.load_card_index().items():
            base_card = self.searchable_card(card_no, record)
            broad = " ".join([base_card["card_no"], base_card["name"]]).casefold()
            if q and q not in broad:
                continue
            if product_filter and product_filter != "プレリリース" and product_filter not in str(base_card["product"]).casefold():
                continue
            if type_filter and type_filter not in str(base_card["card_type"]).casefold():
                continue
            if group_filter and group_filter not in str(base_card["group"]).casefold():
                continue
            if unit_filter and unit_filter not in str(base_card["unit"]).casefold():
                continue
            if not self._range_matches(base_card["cost_num"], cost_min, cost_max):
                continue
            if not self._range_matches(base_card["score_num"], score_min, score_max):
                continue
            if not self._range_matches(base_card["blade_num"], blade_min, blade_max):
                continue
            if not self._heart_filter_matches(base_card["heart_counts"], heart_ranges, heart_mode):
                continue
            if not self._heart_filter_matches(
                base_card["required_heart_counts"], required_heart_ranges, required_heart_mode
            ):
                continue
            if not self._token_filter_matches(
                base_card["blade_heart_tokens"], blade_heart_tokens, blade_heart_mode
            ):
                continue
            effect_text = str(base_card.get("effect_search") or base_card.get("effect") or "")
            if ability_types:
                marker_map = {
                    "auto": ("<自動>", "［自動］", "[自動]"),
                    "live_start": ("<ライブ開始時>", "［ライブ開始時］", "[ライブ開始時]"),
                    "live_success": ("<ライブ成功時>", "［ライブ成功時］", "[ライブ成功時]"),
                    "on_entry": ("<登場>", "［登場］", "[登場]", "<登場時>"),
                    "continuous": ("<常時>", "［常時］", "[常時]"),
                    "activated": ("<起動>", "［起動］", "[起動]"),
                }
                present = {
                    key for key, markers in marker_map.items()
                    if any(marker in effect_text for marker in markers)
                }
                if not present:
                    present.add("none")
                if not (present & set(ability_types)):
                    continue
            if effect_filter and effect_filter not in effect_text.casefold():
                continue

            for variant in self.card_variants(card_no):
                is_prerelease = bool(variant.get("is_prerelease"))
                if product_filter == "プレリリース" and not is_prerelease:
                    continue
                if not include_prerelease and is_prerelease:
                    continue
                if variant.get("is_parallel") and not include_parallel:
                    continue
                displayed_rarity = str(variant.get("raw_rarity") or "")
                if rarity_filter and rarity_filter != displayed_rarity.casefold():
                    continue
                card = dict(base_card)
                card.update({
                    "variant_id": str(variant.get("variant_id") or card_no),
                    "rarity": displayed_rarity,
                    "raw_rarity": displayed_rarity,
                    "base_rarity": str(variant.get("base_rarity") or ""),
                    "is_parallel": bool(variant.get("is_parallel")),
                    "has_image": variant.get("path") is not None,
                    "is_prerelease": is_prerelease,
                })
                results.append(card)

        results.sort(
            key=lambda card: (
                str(card["card_no"]).casefold(),
                bool(card.get("is_parallel")),
                str(card.get("rarity") or "").casefold(),
            )
        )
        return results[:max(1, min(limit, 300))]

    @staticmethod
    def _product_sort_key(
        name: str,
        product_codes: dict[str, set[str]] | None = None,
    ) -> tuple[int, int, str]:
        text = unicodedata.normalize("NFKC", str(name or "")).strip()
        upper = text.upper()

        if text == "プレリリース":
            return (5, 0, text)

        codes = sorted((product_codes or {}).get(text, set()))
        code = codes[0].upper() if codes else ""

        if code.startswith("BP"):
            group = 0
        elif code.startswith("PB"):
            group = 1
        elif "SD" in code:
            group = 2
        elif code == "PR" or text == "PRカード":
            group = 4
        else:
            group = 3

        number = 9999
        match = re.search(r"(?:BP|PB|SD)0*([0-9]+)$", code)
        if match:
            number = int(match.group(1))
        else:
            match = re.search(r"([0-9]+)$", code)
            if match:
                number = int(match.group(1))

        return (group, number, text.casefold())

    def card_filter_options(self) -> dict[str, list[str]]:
        values = {
            "product": set(),
            "card_type": set(),
            "group": set(),
            "unit": set(),
        }
        product_codes: dict[str, set[str]] = {}
        for card_no, record in self.load_card_index().items():
            card = self.searchable_card(card_no, record)
            product_name = str(card.get("product") or "").strip()
            product_code = str(card.get("product_code") or "").strip().upper()
            if product_name and product_code:
                product_codes.setdefault(product_name, set()).add(product_code)

            for key in values:
                raw = str(card[key]).strip()
                if not raw or raw == "-":
                    continue
                parts = re.split(r"\s*/\s*|\s*,\s*|\s*\|\s*", raw)
                for part in parts:
                    part = self._normalize_unit_value(part) if key == "unit" else part.strip(" []{}'\"()（）")
                    part = re.sub(r"\s+", " ", part).strip()
                    if part and part != "-":
                        values[key].add(part)

        base_rarities: set[str] = set()
        parallel_rarities: set[str] = set()
        for variant in self._build_image_variants():
            rarity = str(variant.get("raw_rarity") or "").strip()
            if not rarity:
                continue
            if variant.get("is_parallel"):
                parallel_rarities.add(rarity)
            else:
                base_rarities.add(rarity)

        result = {key: sorted(items, key=str.casefold) for key, items in values.items()}

        def normalized_sort_text(value: str) -> str:
            return re.sub(r"[\s・･!！'’\-_.]+", "", str(value)).casefold()

        group_priority = [
            ("μ's", ("μ's", "µ's", "ミューズ")),
            ("Aqours", ("Aqours", "アクア")),
            ("虹ヶ咲", ("虹ヶ咲", "ニジガク")),
            ("Liella!", ("Liella!", "Liella", "リエラ")),
            ("蓮ノ空", ("蓮ノ空",)),
            ("A-RISE", ("A-RISE", "ARISE", "A‐RISE")),
            ("Saint Snow", ("Saint Snow", "SaintSnow", "セイントスノー")),
            ("Sunny Passion", ("Sunny Passion", "SunnyPassion", "サニーパッション")),
        ]

        def priority_key(value: str, priority_groups: list[tuple[str, tuple[str, ...]]]) -> tuple[int, str]:
            normalized = normalized_sort_text(value)
            for index, (_label, aliases) in enumerate(priority_groups):
                if any(normalized == normalized_sort_text(alias) for alias in aliases):
                    return index, normalized
            return len(priority_groups), normalized

        unit_priority = [
            ("Printemps", ("Printemps",)),
            ("lily white", ("lily white", "lilywhite")),
            ("BiBi", ("BiBi",)),
            ("CYaRon!", ("CYaRon!", "CYaRon")),
            ("AZALEA", ("AZALEA",)),
            ("Guilty Kiss", ("Guilty Kiss", "GuiltyKiss")),
            ("A-RISE", ("A-RISE", "ARISE")),
            ("Saint Snow", ("Saint Snow", "SaintSnow")),
            ("A・ZU・NA", ("A・ZU・NA", "AZUNA")),
            ("DiverDiva", ("DiverDiva",)),
            ("QU4RTZ", ("QU4RTZ",)),
            ("R3BIRTH", ("R3BIRTH",)),
            ("CatChu!", ("CatChu!", "CatChu")),
            ("KALEIDOSCORE", ("KALEIDOSCORE",)),
            ("5yncri5e!", ("5yncri5e!", "5yncri5e")),
            ("Sunny Passion", ("Sunny Passion", "SunnyPassion")),
            ("スリーズブーケ", ("スリーズブーケ",)),
            ("DOLLCHESTRA", ("DOLLCHESTRA",)),
            ("みらくらぱーく！", ("みらくらぱーく！", "みらくらぱーく")),
            ("Edel Note", ("Edel Note", "EdelNote")),
        ]

        result["group"] = sorted(values["group"], key=lambda value: priority_key(value, group_priority))

        # Some source records incorrectly copy the group name into the unit field.
        # Group names are not unit names, so exclude every recognized group alias
        # from the unit-filter choices while preserving legitimate units.
        group_alias_keys = {
            normalized_sort_text(alias)
            for _label, aliases in group_priority
            for alias in aliases
        }
        values["unit"] = {
            value for value in values["unit"]
            if normalized_sort_text(value) not in group_alias_keys
        }

        result["card_type"] = sorted(
            values["card_type"],
            key=lambda value: (
                0 if "member" in value.casefold() or "メンバー" in value else
                1 if "live" in value.casefold() or "ライブ" in value else 2,
                value.casefold(),
            ),
        )
        result["unit"] = sorted(values["unit"], key=lambda value: priority_key(value, unit_priority))
        result["product"] = sorted(
            values["product"],
            key=lambda name: self._product_sort_key(name, product_codes),
        )
        if any(v.get("is_prerelease") for v in self._build_image_variants()):
            result["product"].append("プレリリース")
        # The catalogue is authoritative. Image-derived classification can be
        # wrong when only one variant has been downloaded, so normalize and move
        # every known parallel rarity out of the base bucket.
        base_rarities = {
            self._normalize_rarity(value)
            for value in base_rarities
            if self._normalize_rarity(value)
        }
        parallel_rarities = {
            self._normalize_rarity(value)
            for value in parallel_rarities
            if self._normalize_rarity(value)
        }
        parallel_catalog = set(self.PARALLEL_RARITY_CATALOG)
        for rarity in list(base_rarities):
            if rarity in parallel_catalog:
                base_rarities.discard(rarity)
                parallel_rarities.add(rarity)

        base_rarities.update(self.BASE_RARITY_CATALOG)
        parallel_rarities.update(self.PARALLEL_RARITY_CATALOG)

        def rarity_key(value: str) -> tuple[int, str]:
            normalized = self._normalize_rarity(value)
            return (
                self.RARITY_SORT_ORDER.get(normalized, 999),
                normalized.casefold(),
            )

        result["rarity"] = sorted(base_rarities, key=rarity_key)
        result["parallel_rarity"] = sorted(parallel_rarities, key=rarity_key)
        return result

    def _resolve_known_deck_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("プロジェクト外のファイルは扱えません。") from exc
        known = {str((self.root / d["path"]).resolve()) for d in self.list_decks()}
        if str(candidate) not in known:
            raise ValueError("デッキファイルが見つかりません。")
        return candidate

    def read_deck_rows(self, relative_path: str) -> tuple[dict[str, Any], list[dict[str, str]]]:
        path = self._resolve_known_deck_path(relative_path)
        metadata = self._read_deck_metadata(path)
        rows: list[dict[str, str]] = []

        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            fields = [str(x or "").strip() for x in (reader.fieldnames or [])]

            # Current format:
            # count, card_no, rarity, name, variant_id
            # Legacy formats without rarity/name/variant_id remain readable.
            count_key = next((x for x in ("count", "枚数", "qty", "quantity") if x in fields), "")
            card_key = next((x for x in ("card_no", "cardnumber", "card_number", "カード番号") if x in fields), "")
            rarity_key = next((x for x in ("rarity", "レアリティ") if x in fields), "")
            name_key = next((x for x in ("name", "cardname", "カード名") if x in fields), "")
            variant_key = next((x for x in ("variant_id", "image_variant_id") if x in fields), "")

            if not count_key or not card_key:
                raise ValueError("TSVヘッダーにcountとcard_noが必要です。")

            for row_index, row in enumerate(reader, start=2):
                count = str(row.get(count_key, "") or "").strip()
                card_no = str(row.get(card_key, "") or "").strip()
                if not count and not card_no:
                    continue
                if not card_no:
                    raise ValueError(f"{row_index}行目のcard_noが空です。")
                rows.append({
                    "count": count or "1",
                    "card_no": card_no,
                    "rarity": str(row.get(rarity_key, "") or "").strip() if rarity_key else "",
                    "name": str(row.get(name_key, "") or "").strip() if name_key else "",
                    "variant_id": str(row.get(variant_key, "") or "").strip() if variant_key else "",
                })
        return metadata, rows

    def deck_tsv_text(self, relative_path: str) -> str:
        path = self._resolve_known_deck_path(relative_path)
        return path.read_text(encoding="utf-8-sig")

    @staticmethod
    def _deck_filename_token(name: str) -> str:
        normalized = unicodedata.normalize("NFKC", name)
        ascii_part = "".join(
            ch.lower() if ch.isascii() and ch.isalnum() else "_"
            for ch in normalized
        )
        ascii_part = re.sub(r"_+", "_", ascii_part).strip("_")
        return ascii_part[:32] or datetime.now().strftime("%Y%m%d_%H%M%S")

    def deck_composition(self, rows: list[dict[str, str]]) -> dict[str, int | bool]:
        member_count = 0
        live_count = 0
        other_count = 0
        for row in rows:
            count = int(row["count"])
            card_type = self.searchable_card(
                row["card_no"], self.card_record(row["card_no"])
            )["card_type"].casefold()
            if "メンバー" in card_type or "member" in card_type:
                member_count += count
            elif "ライブ" in card_type or "live" in card_type:
                live_count += count
            else:
                other_count += count
        total = member_count + live_count + other_count
        return {
            "member": member_count,
            "live": live_count,
            "other": other_count,
            "total": total,
            "valid": member_count == 48 and live_count == 12 and other_count == 0,
        }


    def _validate_deck_tsv_for_import(self, tsv_text: str) -> None:
        reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
        fields = [str(field or "").strip() for field in (reader.fieldnames or [])]
        if "count" not in fields or "card_no" not in fields:
            raise ValueError("TSVヘッダーにcountとcard_noが必要です。")

        totals: dict[str, int] = {}
        total_cards = 0

        for row_index, row in enumerate(reader, start=2):
            card_no = str(row.get("card_no") or "").strip()
            count_text = str(row.get("count") or "").strip()

            if not card_no and not count_text:
                continue
            if not card_no:
                raise ValueError("{}行目のcard_noが空です。".format(row_index))

            try:
                count = int(count_text)
            except ValueError as exc:
                raise ValueError(
                    "{}行目のcountが整数ではありません。".format(row_index)
                ) from exc

            if count <= 0:
                raise ValueError(
                    "{}行目のcountは1以上にしてください。".format(row_index)
                )

            if not self.card_record(card_no):
                raise ValueError(
                    "抽出されたカード番号がDBにありません：{}".format(card_no)
                )

            totals[card_no] = totals.get(card_no, 0) + count
            total_cards += count

        if total_cards <= 0:
            raise ValueError("出力TSVにカードがありません。")

        over_limit = {
            card_no: count
            for card_no, count in sorted(totals.items())
            if count > 4
        }
        if over_limit:
            details = "、".join(
                "{}={}枚".format(card_no, count)
                for card_no, count in over_limit.items()
            )
            raise ValueError(
                "同一カードナンバーは通常版・パラレル版を合計して4枚までです："
                + details
            )

    def _deck_import_session_dir(self, import_token: str) -> Path:
        token = str(import_token or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{16,80}", token):
            raise ValueError("デッキ読込セッションが不正です。")
        base = self.path(DECK_IMPORT_STAGING_DIR).resolve()
        candidate = (base / token).resolve()
        if candidate.parent != base:
            raise ValueError("デッキ読込セッションが不正です。")
        return candidate

    def import_deck_code(self, deck_code: str) -> dict[str, Any]:
        code = "".join(
            char
            for char in str(deck_code or "").strip().upper()
            if char.isalnum()
        )
        if not code:
            raise ValueError("デッキコードを入力してください。")
        if len(code) > 32:
            raise ValueError("デッキコードが長すぎます。")

        script = self.root / "llocg_deckcode_to_decklist.py"
        if not script.is_file():
            raise ValueError(
                "デッキコード読込スクリプトが見つかりません：{}".format(script)
            )

        # The script writes to <root>/decklists.  Give it a dedicated temporary
        # root so the official deck folder is untouched until Save is pressed.
        import_token = secrets.token_urlsafe(24).replace("-", "_")
        session_dir = self._deck_import_session_dir(import_token)
        staging_root = session_dir / "source"
        staging_decklists = staging_root / "decklists"
        staging_decklists.mkdir(parents=True, exist_ok=False)

        output_path = staging_decklists / "deck_{}.tsv".format(code)
        meta_path = staging_decklists / "deck_{}.meta.json".format(code)

        command = [
            sys.executable,
            str(script),
            "--root",
            str(staging_root),
            "--code",
            code,
        ]

        try:
            run = subprocess.run(
                command,
                cwd=str(self.root),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=180,
            )
        except Exception:
            shutil.rmtree(session_dir, ignore_errors=True)
            raise

        output_text = run.stdout or ""
        if run.returncode != 0:
            shutil.rmtree(session_dir, ignore_errors=True)
            detail = "\n".join(output_text.strip().splitlines()[-30:])
            raise ValueError(
                "デッキコード読込スクリプトが失敗しました。\n"
                "command: {}\n"
                "returncode: {}\n{}".format(
                    " ".join(command),
                    run.returncode,
                    detail or "出力なし",
                )
            )

        if not output_path.is_file():
            shutil.rmtree(session_dir, ignore_errors=True)
            detail = "\n".join(output_text.strip().splitlines()[-30:])
            raise ValueError(
                "デッキコード読込は完了しましたが、一時出力TSVが見つかりません。\n"
                "expected: {}\n{}".format(
                    output_path,
                    detail or "出力なし",
                )
            )

        rows: list[dict[str, str]] = []
        with output_path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            fields = [str(field or "").strip() for field in (reader.fieldnames or [])]
            if "count" not in fields or "card_no" not in fields:
                shutil.rmtree(session_dir, ignore_errors=True)
                raise ValueError(
                    "出力TSVのヘッダーが不正です：{}".format(", ".join(fields))
                )

            for row_index, row in enumerate(reader, start=2):
                card_no = str(row.get("card_no") or "").strip()
                if not card_no:
                    continue
                try:
                    count = int(str(row.get("count") or "0").strip())
                except ValueError as exc:
                    shutil.rmtree(session_dir, ignore_errors=True)
                    raise ValueError(
                        "{}行目のcountが整数ではありません。".format(row_index)
                    ) from exc
                if count <= 0:
                    continue

                record = self.card_record(card_no)
                if not record:
                    shutil.rmtree(session_dir, ignore_errors=True)
                    raise ValueError(
                        "抽出されたカード番号がDBにありません：{}".format(card_no)
                    )
                searchable = self.searchable_card(card_no, record)
                rows.append({
                    "count": str(count),
                    "card_no": card_no,
                    "rarity": str(
                        row.get("rarity")
                        or searchable.get("rarity")
                        or ""
                    ).strip(),
                    "name": str(
                        row.get("name")
                        or searchable.get("name")
                        or card_no
                    ).strip(),
                    "variant_id": "",
                })

        if not rows:
            shutil.rmtree(session_dir, ignore_errors=True)
            raise ValueError("出力TSVにカードがありません。")

        normalized = sorted(
            rows,
            key=lambda row: (
                row["card_no"],
                row["rarity"],
                row["variant_id"],
            ),
        )

        tsv_buffer = io.StringIO()
        writer = csv.DictWriter(
            tsv_buffer,
            fieldnames=["count", "card_no", "rarity", "name", "variant_id"],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(normalized)
        self._validate_deck_tsv_for_import(tsv_buffer.getvalue())
        composition = self.deck_composition(normalized)

        deck_name = code
        source_meta: dict[str, Any] = {}
        if meta_path.is_file():
            try:
                loaded_meta = json.loads(meta_path.read_text(encoding="utf-8"))
                if isinstance(loaded_meta, dict):
                    source_meta = loaded_meta
                    deck_name = (
                        str(loaded_meta.get("deck_name") or "").strip()
                        or code
                    )
            except Exception:
                pass

        # Store the normalized preview TSV separately.  The raw fetched files
        # remain in this session directory until the user explicitly saves.
        preview_tsv = session_dir / "preview.tsv"
        preview_tsv.write_text(tsv_buffer.getvalue(), encoding="utf-8")
        session_manifest = {
            "import_token": import_token,
            "deck_code": code,
            "deck_name": deck_name,
            "source_tsv": str(output_path),
            "source_meta": str(meta_path) if meta_path.is_file() else "",
            "preview_tsv": str(preview_tsv),
            "created_at": utc_now_iso(),
            "script": script.name,
            "command": command,
            "source_metadata": source_meta,
        }
        (session_dir / "import.json").write_text(
            json.dumps(session_manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "import_token": import_token,
            "deck_code": code,
            "deck_name": deck_name,
            "script": script.name,
            "command": command,
            "rows": normalized,
            "composition": composition,
            "card_types": len(normalized),
            "card_count": composition["total"],
            "source_tsv": str(output_path),
            "script_output": output_text,
        }

    def save_imported_deck(
        self,
        import_token: str,
        deck_code: str,
        deck_name: str,
        tags: Any = "",
    ) -> dict[str, Any]:
        session_dir = self._deck_import_session_dir(import_token)
        manifest_path = session_dir / "import.json"
        if not manifest_path.is_file():
            raise ValueError(
                "一時保存されたデッキ読込結果が見つかりません。もう一度読み込んでください。"
            )

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError("デッキ読込セッションを読み取れません。") from exc
        if not isinstance(manifest, dict):
            raise ValueError("デッキ読込セッションが不正です。")

        stored_code = str(manifest.get("deck_code") or "").strip().upper()
        requested_code = str(deck_code or "").strip().upper()
        if not stored_code or stored_code != requested_code:
            raise ValueError("デッキコードと読込セッションが一致しません。")

        preview_tsv = Path(str(manifest.get("preview_tsv") or ""))
        source_tsv = Path(str(manifest.get("source_tsv") or ""))
        source_meta_text = str(manifest.get("source_meta") or "")
        source_meta = Path(source_meta_text) if source_meta_text else None

        if not preview_tsv.is_file() or not source_tsv.is_file():
            raise ValueError(
                "一時保存されたデッキファイルが見つかりません。もう一度読み込んでください。"
            )

        tsv_text = preview_tsv.read_text(encoding="utf-8-sig")
        self._validate_deck_tsv_for_import(tsv_text)

        final_name = (
            str(deck_name or "").strip()
            or str(manifest.get("deck_name") or "").strip()
            or stored_code
        )
        official_dir = self.path(PRIMARY_DECK_DIR)
        official_dir.mkdir(parents=True, exist_ok=True)
        deck_id, target = self._new_unique_deck_target(official_dir)
        target_meta = target.with_suffix(".meta.json")

        # Promote only now, after the user pressed Save.  Use normalized TSV so
        # the app's variant/name columns are retained.
        staged_target = session_dir / "promote.tsv"
        staged_target.write_text(tsv_text, encoding="utf-8")
        staged_target.replace(target)

        metadata: dict[str, Any] = {}
        if source_meta is not None and source_meta.is_file():
            try:
                loaded = json.loads(source_meta.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    metadata.update(loaded)
            except Exception:
                pass
        metadata.update({
            "deck_id": deck_id,
            "deck_code": stored_code,
            "deck_name": final_name,
            "tags": self._normalize_deck_tags(tags),
            "source": "deck_code_import",
            "tsv_path": str(target),
            "created_at": metadata.get("created_at") or utc_now_iso(),
            "updated_at": utc_now_iso(),
            "format_version": 3,
        })
        target_meta.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        rows: list[dict[str, str]] = []
        with target.open("r", encoding="utf-8-sig", newline="") as fh:
            rows.extend(dict(row) for row in csv.DictReader(fh, delimiter="\t"))
        composition = self.deck_composition(rows)

        shutil.rmtree(session_dir, ignore_errors=True)
        return {
            "name": final_name,
            "code": stored_code,
            "path": str(target.relative_to(self.root)),
            "card_types": len(rows),
            "card_count": composition["total"],
            "composition": composition,
        }

    def save_deck(
        self,
        deck_name: str,
        tsv_text: str,
        existing_path: str = "",
        tags: Any = "",
    ) -> dict[str, Any]:
        name = deck_name.strip()
        if not name:
            raise ValueError("デッキ名を入力してください。")

        reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
        fields = [str(x or "").strip() for x in (reader.fieldnames or [])]
        if "count" not in fields or "card_no" not in fields:
            raise ValueError("TSVヘッダーにcountとcard_noが必要です。")

        variant_rows: dict[tuple[str, str, str], dict[str, str]] = {}
        cardnumber_totals: dict[str, int] = {}

        for index, row in enumerate(reader, start=2):
            count_text = str(row.get("count", "") or "").strip()
            card_no = str(row.get("card_no", "") or "").strip()
            rarity = str(row.get("rarity", "") or "").strip()
            card_name = str(row.get("name", "") or "").strip()
            variant_id = str(row.get("variant_id", "") or "").strip()

            if not any([count_text, card_no, rarity, card_name, variant_id]):
                continue

            try:
                count = int(count_text)
            except ValueError as exc:
                raise ValueError(f"{index}行目のcountが整数ではありません。") from exc
            if count <= 0:
                raise ValueError(f"{index}行目のcountは1以上にしてください。")
            if not card_no:
                raise ValueError(f"{index}行目のcard_noが空です。")
            if self.card_record(card_no) == {}:
                raise ValueError(f"{index}行目のカード番号がDBにありません：{card_no}")

            key = (card_no, rarity, variant_id)
            if key not in variant_rows:
                variant_rows[key] = {
                    "count": "0",
                    "card_no": card_no,
                    "rarity": rarity,
                    "name": card_name,
                    "variant_id": variant_id,
                }
            variant_rows[key]["count"] = str(int(variant_rows[key]["count"]) + count)
            if not variant_rows[key]["name"] and card_name:
                variant_rows[key]["name"] = card_name

            cardnumber_totals[card_no] = cardnumber_totals.get(card_no, 0) + count

        if not variant_rows:
            raise ValueError("カードを1枚以上追加してください。")

        over_limit = {
            card_no: count
            for card_no, count in sorted(cardnumber_totals.items())
            if count > 4
        }
        if over_limit:
            details = "、".join(f"{card_no}={count}枚" for card_no, count in over_limit.items())
            raise ValueError(
                "同一カードナンバーは通常版・パラレル版を合計して4枚までです："
                + details
            )

        normalized = sorted(
            variant_rows.values(),
            key=lambda row: (
                row["card_no"],
                row["rarity"],
                row["variant_id"],
            ),
        )

        deck_dir = self.path(PRIMARY_DECK_DIR)
        deck_dir.mkdir(parents=True, exist_ok=True)

        if existing_path:
            target = self._resolve_known_deck_path(existing_path)
            existing_meta = self._read_deck_metadata(target)
            deck_id = str(
                existing_meta.get("deck_id")
                or target.stem.removeprefix("deck_")
            )
        else:
            deck_id, target = self._new_unique_deck_target(deck_dir)

        required = ["count", "card_no", "rarity", "name", "variant_id"]
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=required,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(normalized)
        target.write_text(output.getvalue(), encoding="utf-8")

        meta_path = target.with_suffix(".meta.json")
        metadata: dict[str, Any] = {}
        if meta_path.exists():
            try:
                old = json.loads(meta_path.read_text(encoding="utf-8"))
                if isinstance(old, dict):
                    metadata.update(old)
            except Exception:
                pass
        metadata.update({
            "deck_id": deck_id,
            "deck_name": name,
            "tags": self._normalize_deck_tags(tags),
            "tsv_path": str(target),
            "created_at": metadata.get("created_at") or utc_now_iso(),
            "updated_at": utc_now_iso(),
            "source": metadata.get("source") or "loveca_app",
            "format_version": 3,
        })
        meta_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        composition = self.deck_composition(normalized)
        return {
            "name": name,
            "code": str(metadata.get("deck_code") or ""),
            "path": str(target.relative_to(self.root)),
            "card_types": len(normalized),
            "card_count": composition["total"],
            "composition": composition,
            "copy_totals": cardnumber_totals,
        }

    def delete_deck(self, relative_path: str) -> dict[str, str]:
        path = self._resolve_known_deck_path(relative_path)
        meta = self._read_deck_metadata(path)
        meta_path = path.with_suffix(".meta.json")
        deleted = {"deck": str(path.relative_to(self.root)), "meta": ""}
        path.unlink()
        if meta_path.exists():
            meta_path.unlink()
            deleted["meta"] = str(meta_path.relative_to(self.root))
        settings = self.load_settings()
        if settings.get("active_deck") == deleted["deck"]:
            self.save_settings({"active_deck": ""})
        return deleted

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

        image_directories = {
            relative: self.path(relative).is_dir()
            for relative in CARD_IMAGE_DIRS
        }
        active_deck = str(self.load_settings().get("active_deck") or "")
        active_deck_image_matches: int | None = None
        active_deck_card_types: int | None = None
        if active_deck:
            try:
                _, active_rows = self.read_deck_rows(active_deck)
                active_deck_card_types = len(active_rows)
                active_deck_image_matches = sum(
                    1 for row in active_rows if self.find_card_image(row["card_no"]) is not None
                )
            except Exception:
                pass

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
            "log_count": len(self.list_logs()),
            "active_deck": self.load_settings().get("active_deck", ""),
            "image_directories": image_directories,
            "active_deck_image_matches": active_deck_image_matches,
            "active_deck_card_types": active_deck_card_types,
        }

    def _manual_process_ids(self) -> set[int]:
        process = self.manual_process
        if process is None or process.poll() is not None:
            return set()
        found = {int(process.pid)}
        pending = [int(process.pid)]
        while pending:
            parent = pending.pop()
            try:
                result = subprocess.run(
                    ["pgrep", "-P", str(parent)],
                    capture_output=True,
                    text=True,
                    timeout=0.5,
                )
            except Exception:
                continue
            for token in result.stdout.split():
                try:
                    child = int(token)
                except ValueError:
                    continue
                if child not in found:
                    found.add(child)
                    pending.append(child)
        return found

    def _manual_listening_ports(self) -> set[int]:
        ports: set[int] = set()
        for pid in self._manual_process_ids():
            try:
                result = subprocess.run(
                    ["lsof", "-Pan", "-p", str(pid), "-iTCP", "-sTCP:LISTEN"],
                    capture_output=True,
                    text=True,
                    timeout=0.8,
                )
            except Exception:
                continue
            for match in re.finditer(r"TCP\s+(?:\[[^\]]+\]|[^:\s]+):(\d+)\s+\(LISTEN\)", result.stdout):
                try:
                    ports.add(int(match.group(1)))
                except ValueError:
                    pass
        return ports

    def _read_manual_output(self, process: subprocess.Popen[str]) -> None:
        stream = process.stdout
        if stream is None:
            return
        for line in stream:
            clean = line.rstrip("\r\n")
            print(clean, flush=True)
            urls = re.findall(r"https?://(?:127\.0\.0\.1|localhost):\d+[^\s'\"<>]*", clean)
            with self.lock:
                output = self.manual_launch_state.setdefault("output", [])
                output.append(clean)
                if len(output) > 100:
                    del output[:20]
                for url in urls:
                    if any(token in url.lower() for token in ("public", "spectator")):
                        self.manual_launch_state["public_url"] = url.rstrip(".,)")
                    elif not self.manual_launch_state.get("private_url"):
                        self.manual_launch_state["private_url"] = url.rstrip(".,)")

    def _detect_simulator_windows(self, remote: bool) -> None:
        with self.lock:
            configured_port = self.manual_launch_state.get("simulator_port")
        known_ports = {8000, 8080, 8766, 5000, 7860, 3000}
        if isinstance(configured_port, int) and configured_port > 0:
            known_ports.add(configured_port)
        private_paths = ("/", "/game", "/play", "/index.html")
        public_paths = ("/public", "/public/", "/?view=public", "/?public=1", "/public.html")
        deadline = time.monotonic() + 45.0
        headers = {"User-Agent": "LovecaApp-WindowProbe/3.0"}

        def probe(url: str) -> tuple[bool, str]:
            try:
                request = Request(url, headers=headers)
                with urlopen(request, timeout=0.6) as response:
                    status = int(getattr(response, "status", 200))
                    content_type = str(response.headers.get("Content-Type") or "")
                    body = response.read(262144).decode("utf-8", errors="ignore")
                if status >= 400 or "text/html" not in content_type.lower():
                    return False, ""
                return True, body
            except (URLError, HTTPError, TimeoutError, OSError):
                return False, ""

        while time.monotonic() < deadline:
            process = self.manual_process
            if process is None or process.poll() is not None:
                with self.lock:
                    output = list(self.manual_launch_state.get("output") or [])
                    detail = output[-1] if output else ""
                    message = "シミュレータプロセスが終了しました。"
                    if detail:
                        message += " 最終出力: " + detail
                    self.manual_launch_state.update({
                        "status": "failed",
                        "message": message,
                    })
                return

            with self.lock:
                private_url = str(self.manual_launch_state.get("private_url") or "")
                public_url = str(self.manual_launch_state.get("public_url") or "")

            ports = set(known_ports)
            ports.update(self._manual_listening_ports())
            for url in (private_url, public_url):
                match = re.search(r":(\d+)", url)
                if match:
                    ports.add(int(match.group(1)))
            ports.discard(DEFAULT_PORT)

            for port in sorted(ports):
                base = "http://127.0.0.1:{}".format(port)
                private_body = ""
                if not private_url:
                    for path in private_paths:
                        url = base + path
                        ok, body = probe(url)
                        if not ok:
                            continue
                        lower = body.lower()
                        if "loveca デスクトップ" in lower or ("データ更新" in body and "デッキ管理" in body):
                            continue
                        private_url = url
                        private_body = body
                        break
                elif private_url.startswith(base):
                    ok, private_body = probe(private_url)
                    if not ok:
                        private_body = ""

                if remote and not public_url:
                    # Prefer explicit public/spectator links exposed by the simulator HTML.
                    for match in re.finditer(r"(?:href|src)=[\"']([^\"']*(?:public|spectator)[^\"']*)[\"']", private_body, flags=re.I):
                        target = match.group(1)
                        if target.startswith("http://") or target.startswith("https://"):
                            candidate = target
                        elif target.startswith("/"):
                            candidate = base + target
                        else:
                            candidate = base + "/" + target
                        ok, _ = probe(candidate)
                        if ok:
                            public_url = candidate
                            break
                    if not public_url:
                        for path in public_paths:
                            candidate = base + path
                            ok, _ = probe(candidate)
                            if ok:
                                public_url = candidate
                                break

                if private_url and (not remote or public_url):
                    break

            with self.lock:
                self.manual_launch_state["private_url"] = private_url
                self.manual_launch_state["public_url"] = public_url
                if private_url and (not remote or public_url):
                    self.manual_launch_state["status"] = "ready"
                    self.manual_launch_state["message"] = "表示先を検出しました。"
                    return
            time.sleep(0.4)

        with self.lock:
            private_url = str(self.manual_launch_state.get("private_url") or "")
            public_url = str(self.manual_launch_state.get("public_url") or "")
            missing = []
            if not private_url:
                missing.append("シミュレータ画面")
            if remote and not public_url:
                missing.append("パブリック画面")
            self.manual_launch_state.update({
                "status": "timeout",
                "message": " / ".join(missing) + "のURLを検出できませんでした。",
            })

    def manual_window_status(self) -> dict[str, Any]:
        with self.lock:
            process = self.manual_process
            state = dict(self.manual_launch_state)
            running = bool(process and process.poll() is None)
            state["running"] = running
            if not running and state.get("status") in ("starting", "ready"):
                state["status"] = "stopped"
                state["message"] = "シミュレータは終了しています。"
                self.manual_launch_state.update(state)
            return state

    def stop_update(self, *, reason: str = "user") -> tuple[bool, str]:
        with self.lock:
            process = self.update_process
            if process is None or process.poll() is not None:
                self.update_process = None
                return True, "データ更新処理は起動していません。"
            pid = int(process.pid)

        try:
            if platform.system() == "Windows":
                try:
                    subprocess.run(
                        ["taskkill", "/PID", str(pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=6.0,
                        check=False,
                    )
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    process.terminate()
            elif hasattr(os, "killpg"):
                os.killpg(pid, signal.SIGTERM)
            else:
                process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                if hasattr(os, "killpg"):
                    os.killpg(pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait(timeout=2.0)
        except ProcessLookupError:
            pass
        except Exception as exc:
            return False, "データ更新の終了に失敗しました: {}: {}".format(
                type(exc).__name__, exc
            )

        with self.lock:
            self.update_process = None
            if self.update_job.status == "running":
                self.update_job.status = "cancelled"
                self.update_job.stage = "中断"
                if reason == "shutdown":
                    self.update_job.message = "アプリ終了に伴いデータ更新を中断しました。"
                else:
                    self.update_job.message = "ユーザー操作によりデータ更新を中断しました。"
                self.update_job.finished_at = utc_now_iso()
                self.update_job.returncode = -15
        return True, "データ更新処理を終了しました。"

    def stop_all_child_processes(self) -> tuple[bool, str]:
        update_ok, update_message = self.stop_update(reason="shutdown")
        manual_ok, manual_message = self.stop_manual()
        return (
            update_ok and manual_ok,
            "{} / {}".format(manual_message, update_message),
        )

    def stop_manual(self) -> tuple[bool, str]:
        with self.lock:
            process = self.manual_process
            if process is None or process.poll() is not None:
                self.manual_process = None
                self.manual_launch_state.update({
                    "status": "idle",
                    "private_url": "",
                    "public_url": "",
                    "message": "シミュレータは起動していません。",
                    "pid": None,
                    "simulator_host": "",
                    "simulator_port": None,
                    "remote_key": "",
                    "remote_label": "",
                })
                return True, "シミュレータはすでに終了しています。"
            pid = int(process.pid)
        try:
            if hasattr(os, "killpg"):
                os.killpg(pid, signal.SIGTERM)
            else:
                process.terminate()
            try:
                process.wait(timeout=4.0)
            except subprocess.TimeoutExpired:
                if hasattr(os, "killpg"):
                    os.killpg(pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait(timeout=2.0)
        except ProcessLookupError:
            pass
        except Exception as exc:
            return False, "終了に失敗しました: {}: {}".format(type(exc).__name__, exc)
        with self.lock:
            self.manual_process = None
            self.manual_launch_state.update({
                "status": "idle",
                "private_url": "",
                "public_url": "",
                "message": "シミュレータを終了しました。",
                "pid": None,
                "simulator_host": "",
                "simulator_port": None,
            })
        return True, "シミュレータを終了しました。"

    def start_manual(
        self,
        deck_path: str = "",
        remote_session: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        script = self.path(MANUAL_SCRIPT)
        if not script.exists():
            return False, "{} が見つかりません。".format(MANUAL_SCRIPT)
        selected_path = deck_path or str(self.load_settings().get("active_deck") or "")
        if not selected_path:
            return False, "使用するデッキを選択してください。"
        try:
            runtime_deck = self.prepare_runtime_deck(selected_path)
        except ValueError as exc:
            return False, str(exc)
        with self.lock:
            if self.manual_process and self.manual_process.poll() is None:
                state = self.manual_window_status()
                if state.get("private_url"):
                    return False, "手動シミュレータはすでに起動しています。メイン画面の「シミュレータへ戻る」を使用してください。"
                return False, "手動シミュレータはすでに起動しています。終了してから再起動してください。"
            try:
                env = os.environ.copy()

                # Equivalent to the documented common `unset` block.
                # This prevents old regression/debug settings from changing or
                # terminating a normal game launched from the application.
                for key in NORMAL_MATCH_UNSET_ENV:
                    env.pop(key, None)

                env["LLOCG_APP_SELECTED_DECK"] = runtime_deck["deck_path"]
                env["LLOCG_APP_SELECTED_DECK_JSON"] = runtime_deck["bridge_path"]
                env["LLOCG_APP_DECK_VARIANTS_JSON"] = json.dumps(
                    runtime_deck["variants"], ensure_ascii=False, separators=(",", ":")
                )
                # Shuffle real deck copies, not only card numbers.  This keeps
                # image rarity/variant metadata attached to each opening hand
                # and deck copy for the simulator's instance display layer.
                expanded_entries: list[dict[str, Any]] = []
                instance_seq = 0
                for row in runtime_deck["variants"]:
                    card_no = str(row.get("card_no") or "").strip()
                    if not card_no:
                        continue
                    try:
                        count = max(0, int(row.get("count", 0) or 0))
                    except Exception:
                        count = 0
                    for _ in range(count):
                        instance_seq += 1
                        expanded_entries.append({
                            "instance_id": f"dc{instance_seq:03d}",
                            "cardnumber": card_no,
                            "rarity": str(row.get("rarity", "") or ""),
                            "variant_id": str(row.get("variant_id", "") or ""),
                        })

                random.SystemRandom().shuffle(expanded_entries)
                opening_entries = expanded_entries[:6]
                remaining_entries = expanded_entries[6:]
                opening_hand = [str(x.get("cardnumber") or "") for x in opening_entries]
                remaining_deck = [str(x.get("cardnumber") or "") for x in remaining_entries]

                if len(opening_hand) != 6 or len(remaining_deck) != 54:
                    raise ValueError(
                        "通常対戦の初期化に失敗しました：手札={} 山札={}".format(
                            len(opening_hand),
                            len(remaining_deck),
                        )
                    )

                env["LLOCG_START_HAND"] = ",".join(opening_hand)
                env["LLOCG_START_HAND_SIZE"] = "0"
                env["LLOCG_START_DECK_EXACT"] = ",".join(remaining_deck)
                env["LLOCG_START_DECK_EXACT_STRICT"] = "1"
                env["LLOCG_START_SHUFFLE"] = "0"
                env["LLOCG_APP_INITIAL_INSTANCES_JSON"] = json.dumps(
                    {"hand": opening_entries, "deck": remaining_entries},
                    ensure_ascii=False,
                    separators=(",", ":"),
                )

                # Phase, turn and energy overrides remain unset.  The simulator
                # continues through its ordinary mulligan and energy setup.
                env["LLOCG_APP_NORMAL_MATCH_SETUP"] = "1"
                env["LLOCG_APP_MULLIGAN_REQUIRED"] = "1"
                env["LLOCG_APP_INITIAL_HAND_COUNT"] = "6"
                env["LLOCG_APP_INITIAL_DECK_COUNT"] = "54"

                env["LLOCG_APP_SETTINGS_PATH"] = str(self.path(SETTINGS_PATH))
                if remote_session is not None:
                    env["LLOCG_APP_REMOTE_MODE"] = "1"
                    env["LLOCG_APP_OPEN_PUBLIC_WINDOW"] = "1"
                    env["LLOCG_APP_REMOTE_SESSION_JSON"] = json.dumps(remote_session, ensure_ascii=False, separators=(",", ":"))
                    env["LLOCG_APP_REMOTE_SESSION_KEY"] = str(remote_session.get("short_key") or "")
                    env["LLOCG_APP_REMOTE_SESSION_UID"] = str(remote_session.get("session_uid") or "")
                else:
                    for key in (
                        "LLOCG_APP_REMOTE_MODE", "LLOCG_APP_OPEN_PUBLIC_WINDOW",
                        "LLOCG_APP_REMOTE_SESSION_JSON", "LLOCG_APP_REMOTE_SESSION_KEY",
                        "LLOCG_APP_REMOTE_SESSION_UID",
                    ):
                        env.pop(key, None)

                simulator_host = DEFAULT_HOST
                simulator_port = reserve_free_local_port(simulator_host)
                simulator_base_url = "http://{}:{}/".format(
                    simulator_host,
                    simulator_port,
                )

                # run_llocg_ui_web.py accepts explicit host/port arguments.
                # The launcher itself uses 8765, so using the simulator default
                # would cause Errno 48: Address already in use.
                launch_command = [
                    sys.executable,
                    str(script),
                    "--host",
                    simulator_host,
                    "--port",
                    str(simulator_port),
                ]

                self.manual_process = subprocess.Popen(
                    launch_command,
                    cwd=str(self.root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env,
                    start_new_session=True,
                )
                self.manual_launch_state = {
                    "status": "starting",
                    "private_url": simulator_base_url,
                    "public_url": "",
                    "remote": remote_session is not None,
                    "message": "シミュレータの待受開始を確認しています。 port={}".format(
                        simulator_port
                    ),
                    "pid": self.manual_process.pid,
                    "deck_path": runtime_deck.get("deck_path", ""),
                    "deck_name": runtime_deck.get("deck_name", ""),
                    "started_at": utc_now_iso(),
                    "simulator_host": simulator_host,
                    "simulator_port": simulator_port,
                    "remote_key": str((remote_session or {}).get("short_key") or ""),
                    "remote_label": str((remote_session or {}).get("session_label") or ""),
                    "output": [],
                }
                threading.Thread(target=self._read_manual_output, args=(self.manual_process,), daemon=True).start()
                threading.Thread(target=self._detect_simulator_windows, args=(remote_session is not None,), daemon=True).start()
            except Exception as exc:
                return False, "起動に失敗しました: {}: {}".format(type(exc).__name__, exc)
        mode = "リモート対戦" if remote_session is not None else "通常対戦"
        message = (
            "{}シミュレータを起動しました：{} ({}枚) / "
            "通常セットアップ: 手札6枚・山札54枚へ分割しました"
        ).format(
            mode,
            runtime_deck.get("deck_name", ""),
            len(runtime_deck.get("cards", [])),
        )
        return True, message

    def start_update(self, *, source: str = "manual") -> tuple[bool, str]:
        script = self.path(UPDATE_SCRIPT)
        if not script.exists():
            return False, f"{UPDATE_SCRIPT} が見つかりません。"
        field_schema = self.path(FIELD_SCHEMA_PATH)
        if not field_schema.exists():
            return False, (
                "DB補正定義が見つかりません: {}。"
                "manual_overrides/loveca_field_schema.json を配置してください。"
            ).format(field_schema)

        with self.lock:
            if self.update_job.status == "running":
                return False, "データ更新はすでに実行中です。"
            job_name = "startup_database_update" if source == "startup" else "database_update"
            self.update_job.reset(job_name)
            if source == "startup":
                self.update_job.stage = "起動時更新"
                self.update_job.message = "許可されたため、必要部品の確認とカードデータ更新を開始しています。"

        def worker() -> None:
            try:
                update_env = os.environ.copy()
                update_env["PYTHONUNBUFFERED"] = "1"
                python_exe = console_python_executable()
                update_args = [
                    python_exe,
                    "-u",
                    str(script),
                    "--require-preview-posts",
                ]
                if source == "startup":
                    update_args.extend([
                        "--delay",
                        "10.0",
                        "--max-429",
                        "8",
                        "--http-cache-ttl-hours",
                        "24",
                        "--released-product-grace-days",
                        "0",
                        "--product-page-cache-ttl-days",
                        "3650",
                        "--preview-index-cache-minutes",
                        "360",
                        "--preview-page-cache-ttl-hours",
                        "24",
                        "--preview-empty-recheck-hours",
                        "24",
                    ])
                self.update_job.append("[APP-UPDATE] command=" + " ".join(update_args))
                process = subprocess.Popen(
                    update_args,
                    cwd=str(self.root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=update_env,
                    start_new_session=True,
                    **no_window_subprocess_kwargs(),
                )
                with self.lock:
                    self.update_process = process
                assert process.stdout is not None
                for line in process.stdout:
                    with self.lock:
                        self.update_job.append(line)
                returncode = process.wait()
                with self.lock:
                    if self.update_process is process:
                        self.update_process = None
                    if self.update_job.status == "cancelled":
                        self.update_job.append("[APP-UPDATE] update was cancelled.")
                        return
                    self.update_job.returncode = returncode
                    self.update_job.status = "success" if returncode == 0 else "failed"
                    self.update_job.finished_at = utc_now_iso()
                    if returncode == 0:
                        self._invalidate_card_data_caches()
                        self.update_job.stage = "完了"
                        self.update_job.progress_percent = 100
                        self.update_job.message = "カードデータの更新が完了しました。"
                    else:
                        self.update_job.stage = "更新失敗"
                        self.update_job.message = (
                            "更新処理がエラーで終了しました。最新ログを確認してください。"
                        )
            except Exception as exc:
                with self.lock:
                    self.update_process = None
                    self.update_job.append(f"{type(exc).__name__}: {exc}")
                    self.update_job.returncode = -1
                    self.update_job.status = "failed"
                    self.update_job.stage = "更新失敗"
                    self.update_job.message = "更新処理を開始または継続できませんでした。"
                    self.update_job.finished_at = utc_now_iso()

        threading.Thread(target=worker, daemon=True).start()
        if source == "startup":
            return True, "カードデータ更新を開始しました。初回は必要なPython追加部品を確認してから、外部サイトのカード情報と画像情報を取得します。"
        return True, "DBフィールド補正を含むデータ更新を開始しました。"

    def maybe_start_startup_update(self) -> tuple[bool, str]:
        settings = self.load_settings()
        if not bool(settings.get("auto_update_on_startup", True)):
            return False, "起動時更新確認は設定で無効です。"
        return self.start_update(source="startup")

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
            "schema_version": 2,
            "created_at": utc_now_iso(),
            "date": date_text,
            "player_id": player,
            "short_key": key,
            "session_label": f"{date_text}-{player}-{key}",
            "match_uid": compute_match_uid(date_text, key),
            "session_uid": uid,
            "event_integrity": "metadata-linked",
        }

        folder = self.path(SESSION_DIR)
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / f"{record['session_label']}.json"
        target.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        record["saved_to"] = str(target.relative_to(self.root))
        return record

    def list_remote_sessions(self) -> list[dict[str, Any]]:
        folder = self.path(SESSION_DIR)
        records: list[dict[str, Any]] = []
        if not folder.is_dir():
            return records
        for path in sorted(folder.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
                date_text = str(data.get("date") or "")
                short_key = str(data.get("short_key") or "").upper()
                data["match_uid"] = str(data.get("match_uid") or compute_match_uid(date_text, short_key))
                data["saved_to"] = str(path.relative_to(self.root))
                records.append(data)
            except Exception:
                continue
        return records

    def verify_remote_session_pair(self, local_path: str, counterpart_text: str) -> dict[str, Any]:
        local_candidate = (self.root / local_path).resolve()
        session_root = self.path(SESSION_DIR).resolve()
        try:
            local_candidate.relative_to(session_root)
        except ValueError as exc:
            raise ValueError("ローカル記録のパスが不正です。") from exc
        if not local_candidate.is_file():
            raise ValueError("選択したローカル記録が見つかりません。")
        try:
            local = json.loads(local_candidate.read_text(encoding="utf-8"))
            other = json.loads(counterpart_text)
        except json.JSONDecodeError as exc:
            raise ValueError("相手側の記録が正しいJSONではありません。") from exc
        if not isinstance(local, dict) or not isinstance(other, dict):
            raise ValueError("照合記録はJSONオブジェクトである必要があります。")

        def normalized(record: dict[str, Any]) -> dict[str, str]:
            date_text = str(record.get("date") or "").strip()
            key = str(record.get("short_key") or "").strip().upper()
            player = safe_player_id(str(record.get("player_id") or ""))
            match_uid = str(record.get("match_uid") or compute_match_uid(date_text, key))
            session_uid = str(record.get("session_uid") or compute_session_uid(date_text, player, key))
            return {"date": date_text, "short_key": key, "player_id": player, "match_uid": match_uid, "session_uid": session_uid}

        left = normalized(local)
        right = normalized(other)
        same_match = bool(left["date"] and left["short_key"] and left["match_uid"] == right["match_uid"] and left["date"] == right["date"] and left["short_key"] == right["short_key"])
        distinct_players = left["player_id"] != right["player_id"]
        duplicate_record = left["session_uid"] == right["session_uid"]
        ok = same_match and distinct_players and not duplicate_record
        reasons: list[str] = []
        if not same_match:
            reasons.append("対戦日・共有キー・共有照合IDが一致しません")
        if not distinct_players:
            reasons.append("プレイヤー識別子が同一です")
        if duplicate_record:
            reasons.append("同一参加者の記録を二重に指定しています")
        return {
            "ok": ok,
            "message": "同一対戦の別プレイヤー記録として照合できました。" if ok else " / ".join(reasons),
            "local": left,
            "counterpart": right,
        }
