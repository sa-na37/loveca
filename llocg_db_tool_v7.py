#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LL-OCG DB Tool (single-file) v7

Subcommands:
  scrape    : wiki -> cards_min.csv/json  (with normalize columns if enabled)
  normalize : postprocess effect_tokens_json: (E)/(ALL)/(ブレード)/(スコア+N)
              + normalize blade-heart special metadata (draw/score/colorless)
              + classify effect text into NO_ABILITY / HAS_TEXT
  mine      : mine frequent effect templates -> CSV + stub YAML
  audit     : audit CSV (missing, json parse, unknown tokens, cardno format)
  db-generation-audit : compare canonical 5 DB files for cardnumber generation drift
  all       : scrape -> normalize -> mine -> audit

Deps:
  pip install requests beautifulsoup4 lxml pandas
"""

from __future__ import annotations

BUILD_TAG = "rm_rarity_image_manifest_20260721a"

import argparse
import csv
import hashlib
import json
import random
import re
import time
import urllib.parse
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import Counter

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from bs4 import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

CONFIG = {
    "products_url": "https://wikiwiki.jp/llocardgame/%E5%95%86%E5%93%81%E4%B8%80%E8%A6%A7",
    "outdir": "llocg_db_out",
    "cache": ".cache_llocg",
    "delay": 5.0,
    "cache_ttl_sec": 21600.0,
    "checkpoint_every": 50,
    "max_fail": 500,
    "max_429": 3,
    "user_agent": "LL-OCG-DB-Build/1.0 (polite crawler; contact: your_email@example.com)",
    "normalize_suffix": "_tokv1",
    "manual_overrides": "manual_overrides/loveca_card_text_overrides.json",
    "field_schema": "manual_overrides/loveca_field_schema.json",
}

TRANSIENT_HTTP_STATUSES = {500, 502, 503, 504}
TRANSIENT_MAX_RETRIES = 3
TRANSIENT_BASE_BACKOFF_SEC = 5.0
TRANSIENT_MAX_BACKOFF_SEC = 60.0
RATE_LIMIT_BASE_BACKOFF_SEC = 300.0
RATE_LIMIT_MAX_BACKOFF_SEC = 1800.0
ADAPTIVE_RATE_LIMIT_INITIAL_MULTIPLIER = 2.0
ADAPTIVE_RATE_LIMIT_STEP = 1.75
ADAPTIVE_RATE_LIMIT_MAX_MULTIPLIER = 8.0
ADAPTIVE_RATE_LIMIT_RECOVERY_SUCCESSES = 40
ADAPTIVE_RATE_LIMIT_RECOVERY_DIVISOR = 1.5
FAILURE_LOG_COLUMNS = [
    "url",
    "stage",
    "status_code",
    "error_type",
    "attempts",
    "last_error",
    "timestamp",
]


class FetchSafetyStop(RuntimeError):
    """Raised when repeated HTTP 429 responses require a safe stop."""


@dataclass
class FetchFailure:
    url: str
    stage: str
    status_code: str
    error_type: str
    attempts: int
    last_error: str
    timestamp: str

    def as_row(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "stage": self.stage,
            "status_code": self.status_code,
            "error_type": self.error_type,
            "attempts": self.attempts,
            "last_error": self.last_error,
            "timestamp": self.timestamp,
        }


class FetchState:
    """Execution-scoped HTTP retry/failure state."""

    def __init__(self, failure_csv: Optional[Path], max_429: int = 3):
        self.failure_csv = failure_csv
        self.max_429 = max(1, int(max_429))
        self.consecutive_429 = 0
        self.rate_limit_events = 0
        self.rate_limit_delay_multiplier = 1.0
        self.successes_since_429 = 0
        self.failures: Dict[Tuple[str, str], FetchFailure] = {}
        self._load_existing()

    def effective_delay(self, base_delay: float) -> float:
        return max(0.0, float(base_delay)) * self.rate_limit_delay_multiplier

    def note_rate_limit(self) -> Tuple[float, float]:
        self.rate_limit_events += 1
        self.successes_since_429 = 0
        before = self.rate_limit_delay_multiplier
        if before <= 1.0:
            after = ADAPTIVE_RATE_LIMIT_INITIAL_MULTIPLIER
        else:
            after = before * ADAPTIVE_RATE_LIMIT_STEP
        self.rate_limit_delay_multiplier = min(
            ADAPTIVE_RATE_LIMIT_MAX_MULTIPLIER,
            max(1.0, after),
        )
        return before, self.rate_limit_delay_multiplier

    def note_network_success(self) -> Optional[Tuple[float, float]]:
        self.consecutive_429 = 0
        self.successes_since_429 += 1
        if (
            self.rate_limit_delay_multiplier > 1.0
            and self.successes_since_429 >= ADAPTIVE_RATE_LIMIT_RECOVERY_SUCCESSES
        ):
            before = self.rate_limit_delay_multiplier
            self.rate_limit_delay_multiplier = max(
                1.0,
                before / ADAPTIVE_RATE_LIMIT_RECOVERY_DIVISOR,
            )
            self.successes_since_429 = 0
            return before, self.rate_limit_delay_multiplier
        return None

    def _load_existing(self) -> None:
        if not self.failure_csv or not self.failure_csv.exists():
            return
        try:
            with self.failure_csv.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    url = str(row.get("url", "") or "").strip()
                    stage = str(row.get("stage", "") or "unknown").strip() or "unknown"
                    if not url:
                        continue
                    try:
                        attempts = int(row.get("attempts", 0) or 0)
                    except Exception:
                        attempts = 0
                    self.failures[(url, stage)] = FetchFailure(
                        url=url,
                        stage=stage,
                        status_code=str(row.get("status_code", "") or ""),
                        error_type=str(row.get("error_type", "") or ""),
                        attempts=attempts,
                        last_error=str(row.get("last_error", "") or ""),
                        timestamp=str(row.get("timestamp", "") or ""),
                    )
        except Exception as e:
            print(f"[WARN] failed_fetches.csv load failed: {e}")

    def flush(self) -> None:
        if not self.failure_csv:
            return
        self.failure_csv.parent.mkdir(parents=True, exist_ok=True)
        rows = [v.as_row() for _, v in sorted(self.failures.items())]
        with self.failure_csv.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FAILURE_LOG_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    def record_failure(
        self,
        *,
        url: str,
        stage: str,
        status_code: Optional[int],
        error_type: str,
        attempts: int,
        last_error: str,
    ) -> None:
        self.failures[(url, stage)] = FetchFailure(
            url=url,
            stage=stage,
            status_code="" if status_code is None else str(status_code),
            error_type=error_type,
            attempts=int(attempts),
            last_error=str(last_error),
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        self.flush()

    def clear_failure(self, url: str, stage: str) -> None:
        if self.failures.pop((url, stage), None) is not None:
            self.flush()

# Manual corrections for known upstream/wiki typos.
# External JSON at CONFIG["manual_overrides"] can add/override entries.
# This built-in entry intentionally prevents future wiki refreshes from reintroducing
# the known PL!S-bp5-020 typo if the external file is missing.
BUILTIN_CARD_TEXT_OVERRIDES: Dict[str, Dict[str, str]] = {
    "PL!S-bp5-020": {
        "cardname": "Landing action Yeah!!",
        "reason": "wiki typo: effect says 3つ, official/manual correction is 3つ以上",
        "effect_text_raw": "<ライブ成功時>\n自分が余剰ハートを3つ以上持っている場合、それらをすべて失い、このカードのスコアを+1する。",
        "effect_text_norm": "<ライブ成功時>\n自分が余剰ハートを3つ以上持っている場合、それらをすべて失い、このカードのスコアを+1する。",
    },
}

def load_card_text_overrides(path: Optional[Path]) -> Dict[str, Dict[str, str]]:
    overrides: Dict[str, Dict[str, str]] = {k: dict(v) for k, v in BUILTIN_CARD_TEXT_OVERRIDES.items()}
    if path and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cards = data.get("cards", data) if isinstance(data, dict) else {}
            if isinstance(cards, dict):
                for cn, obj in cards.items():
                    if isinstance(cn, str) and isinstance(obj, dict):
                        merged = dict(overrides.get(cn, {}))
                        merged.update({str(k): str(v) for k, v in obj.items() if isinstance(v, (str, int, float))})
                        overrides[cn] = merged
        except Exception as e:
            print(f"[WARN] failed to load manual card text overrides: {path} ({e})")
    return overrides

def _apply_card_text_override_to_record(rec: Dict[str, Any], overrides: Dict[str, Dict[str, str]]) -> bool:
    if not isinstance(rec, dict):
        return False
    cn = str(rec.get("cardnumber", "") or "").strip()
    if not cn or cn not in overrides:
        return False
    ov = overrides[cn]
    changed = False
    for key in ("effect_text_raw", "effect_text_norm"):
        if key in ov and str(ov[key]) != str(rec.get(key, "") or ""):
            rec[key] = str(ov[key])
            changed = True
    if changed:
        raw = str(rec.get("effect_text_raw", "") or "")
        norm = str(rec.get("effect_text_norm", "") or "") or normalize_effect_text(raw)
        rec["effect_text_norm"] = norm
        rec["effect_text_status"] = classify_effect_text_status(raw, norm)
        rec["effect_text_is_no_ability"] = 1 if rec["effect_text_status"] == "NO_ABILITY" else 0
        rec["effect_tokens_json"] = json.dumps(extract_effect_tokens(norm), ensure_ascii=False)
        rec["manual_override_applied"] = 1
        rec["manual_override_reason"] = str(ov.get("reason", ""))
    return changed

def apply_card_text_overrides_to_records(records: List[Dict[str, Any]], overrides: Dict[str, Dict[str, str]], label: str = "") -> int:
    n = 0
    for rec in records:
        if _apply_card_text_override_to_record(rec, overrides):
            n += 1
    if n:
        print(f"[OVERRIDE] applied manual card text overrides: {n}" + (f" ({label})" if label else ""))
    return n

def apply_card_text_overrides_to_dataframe(df: pd.DataFrame, overrides: Dict[str, Dict[str, str]], label: str = "") -> pd.DataFrame:
    if df is None or df.empty or "cardnumber" not in df.columns:
        return df
    records = df.to_dict(orient="records")
    n = apply_card_text_overrides_to_records(records, overrides, label=label)
    if n:
        return pd.DataFrame(records)
    return df

# Allow: PL!-xxx-001, PL!HS-xxx-001, PL!SP-..., PL!N-..., etc.
CARDNO_IN_TEXT = re.compile(
    r"\b([A-Z]{1,4}(?:!(?:[A-Z0-9]{0,8})?)?-[A-Za-z0-9]+-\d{3}(?:-[A-Za-z0-9]+)?)\b"
)

AUDIT_CARDNO_RE = re.compile(r"^[A-Z]{1,4}(?:!(?:[A-Z0-9]{0,8})?)?-[A-Za-z0-9]+-\d{3}(?:-[A-Za-z0-9]+)?$")

# A wiki page title may temporarily include a rarity suffix in the cardnumber
# itself, especially on prerelease pages. Runtime/compiled DB cardnumbers are
# rarity-agnostic, so known rarity tails are stripped only when there is no
# canonical-cardnumber collision in the same record batch.
CARDNUMBER_RARITY_SUFFIXES = {
    "SD", "CL", "N", "R", "R2", "L", "L2", "PR", "PR2", "P", "P2",
    "SEC", "SEC2", "SECL", "SRL", "DUO", "AR", "RM", "RE", "PE", "PE2",
    "SECE", "LLE",
}
_CARDNUMBER_RARITY_ALT = "|".join(
    re.escape(x) for x in sorted(CARDNUMBER_RARITY_SUFFIXES, key=len, reverse=True)
)
CARDNUMBER_RARITY_SUFFIX_RE = re.compile(
    rf"^(?P<base>[A-Z]{{1,4}}(?:!(?:[A-Z0-9]{{0,8}})?)?-[A-Za-z0-9]+-\d{{3}})-(?P<rarity>{_CARDNUMBER_RARITY_ALT})$",
    re.IGNORECASE,
)


def split_cardnumber_rarity_suffix(cardnumber: str) -> Tuple[str, str]:
    """Return (canonical_cardnumber, rarity_suffix) for a known rarity tail."""
    cn = str(cardnumber or "").strip()
    m = CARDNUMBER_RARITY_SUFFIX_RE.match(cn)
    if not m:
        return cn, ""
    return m.group("base"), m.group("rarity").upper()


def _write_cardnumber_canonicalization_audit(
    outdir: Optional[Path],
    rows: List[Dict[str, Any]],
    label: str,
) -> None:
    if outdir is None:
        return
    outdir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", str(label or "run")).strip("_").lower() or "run"
    json_path = outdir / f"cardnumber_canonicalization_audit_{slug}.json"
    tsv_path = outdir / f"cardnumber_canonicalization_audit_{slug}.tsv"

    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    fields = [
        "source_cardnumber",
        "canonical_cardnumber",
        "rarity_suffix",
        "status",
        "collision_cardnumbers",
        "cardname",
        "source_url",
    ]
    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def canonicalize_cardnumbers_in_records(
    records: List[Dict[str, Any]],
    outdir: Optional[Path] = None,
    label: str = "",
) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Safely strip known rarity suffixes from record cardnumbers.

    Collision policy:
    - If only one distinct source cardnumber maps to a canonical cardnumber,
      rewrite it automatically.
    - If the canonical cardnumber already exists, or multiple distinct rarity-
      suffixed cardnumbers map to the same canonical value, leave the records
      unchanged and report COLLISION_NO_CHANGE.
    """
    all_cardnumbers: Set[str] = {
        str(r.get("cardnumber", "") or "").strip()
        for r in records
        if isinstance(r, dict) and str(r.get("cardnumber", "") or "").strip()
    }
    candidate_sources: Dict[str, Set[str]] = {}
    candidates: List[Tuple[Dict[str, Any], str, str, str]] = []

    for rec in records:
        if not isinstance(rec, dict):
            continue
        source_cn = str(rec.get("cardnumber", "") or "").strip()
        canonical_cn, rarity = split_cardnumber_rarity_suffix(source_cn)
        if not rarity or canonical_cn == source_cn:
            continue
        candidates.append((rec, source_cn, canonical_cn, rarity))
        candidate_sources.setdefault(canonical_cn, set()).add(source_cn)

    audit_rows: List[Dict[str, Any]] = []
    rewritten = 0
    collisions = 0

    for rec, source_cn, canonical_cn, rarity in candidates:
        colliders = set(candidate_sources.get(canonical_cn, set()))
        if canonical_cn in all_cardnumbers:
            colliders.add(canonical_cn)
        is_collision = len(colliders) > 1

        if is_collision:
            status = "COLLISION_NO_CHANGE"
            collisions += 1
        else:
            rec["cardnumber"] = canonical_cn
            status = "RARITY_SUFFIX_STRIPPED"
            rewritten += 1

        audit_rows.append({
            "source_cardnumber": source_cn,
            "canonical_cardnumber": canonical_cn,
            "rarity_suffix": rarity,
            "status": status,
            "collision_cardnumbers": "|".join(sorted(colliders)) if is_collision else "",
            "cardname": str(rec.get("cardname", "") or ""),
            "source_url": str(rec.get("source_url", "") or ""),
        })

    _write_cardnumber_canonicalization_audit(outdir, audit_rows, label=label)

    if audit_rows:
        print(
            f"[CARDNO] rarity-suffix candidates={len(audit_rows)} "
            f"rewritten={rewritten} collisions={collisions}"
            + (f" ({label})" if label else "")
        )
    return rewritten, collisions, audit_rows

START_MARKERS = ["▼効果テキスト", "▼カードテキスト", "▼テキスト"]
STOP_HEADINGS = {
    "カード解説", "収録状況", "コメント", "関連カード", "関連", "各種データ", "編集補助", "画像", "テンプレート",
    "カード検索補助", "人気", "今日人気", "最新"
}

KEY_MAP_EXACT = {
    "カードタイプ": "card_type",
    "カード種別": "card_type",
    "種別": "card_type",
    "作品": "work_title",
    "作品名": "work_title",
    "参加グループ": "group",
    "グループ": "group",
    "参加ユニット": "unit",
    "ユニット": "unit",
    "コスト": "cost",
    "ブレード": "blade",
    "ブレードハート": "blade_heart",
    "基本ハート": "base_hearts",
    "必要ハート": "required_hearts",
    "スコア": "score",
}
KEY_MAP_CONTAINS = [
    ("カードタイプ", "card_type"),
    ("カード種別", "card_type"),
    ("種別", "card_type"),
    ("作品名", "work_title"),
    ("作品", "work_title"),
    ("参加グループ", "group"),
    ("グループ", "group"),
    ("参加ユニット", "unit"),
    ("ユニット", "unit"),
    ("コスト", "cost"),
    ("ブレードハート", "blade_heart"),
    ("ブレード", "blade"),
    ("基本ハート", "base_hearts"),
    ("必要ハート", "required_hearts"),
    ("スコア", "score"),
]

COLOR_MAP = {
    "桃": "pink", "(桃)": "pink",
    "黄": "yellow", "(黄)": "yellow",
    "紫": "purple", "(紫)": "purple",
    "青": "blue", "(青)": "blue",
    "緑": "green", "(緑)": "green",
    "赤": "red", "(赤)": "red",
    "白": "white", "(白)": "white",
    "黒": "black", "(黒)": "black",
    "任意": "any", "(任意)": "any",
    "ALL": "all", "(ALL)": "all",
}

# Blade-heart-only special icons.
# IMPORTANT: colorless is intentionally NOT an alias of `any`.
# `any` is a requirement category/flexible heart representation used elsewhere;
# a colorless heart contributes to the total heart count but never satisfies a
# colored minimum by itself. The new double-colorless blade heart therefore
# normalizes to colorless=2.
BLADE_HEART_SPECIAL_KEYS = ("draw", "score", "colorless")
DOUBLE_COLORLESS_ALIASES = {
    "ダブル無色",
    "ダブル無色ハート",
    "DOUBLECOLORLESS",
    "DOUBLECOLORLESSHEART",
}
SINGLE_COLORLESS_ALIASES = {
    "無色",
    "無色ハート",
    "COLORLESS",
    "COLORLESSHEART",
}

# Accept both old normalized icons '<(桃)>×2' and new official-like icons '<桃> 2'.
ICON_COUNT_RE = re.compile(r"<\s*\(?\s*([^<>（）()]+?)\s*\)?\s*>\s*(?:(?:×|x|X)\s*)?([0-9０-９]+)?")
TOTAL_RE = re.compile(r"\(合計\s*(\d+)\)")
FW_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")

# token postprocess
SCORE_TAG_RE = re.compile(r"^\(\s*(?:スコア|ｽｺｱ|SCORE|Score)\s*([+\-＋－])\s*(\d+)\s*\)$")
PLUS_MINUS_MAP = str.maketrans({"＋": "+", "－": "-"})
KNOWN_SIMPLE = {
    "(ブレード)": "blade_icon_n",
    "(E)": "energy_icon_n",     # Energy
    "(ALL)": "all_heart_n",     # All-heart
}

NO_ABILITY_MARKERS = {"", "(なし)", "(テキストなし)"}


# -------------------------
# official image manifest
# -------------------------
OFFICIAL_BASE_URL = "https://llofficial-cardgame.com"
OFFICIAL_CARDLIST_SEARCH_URL = OFFICIAL_BASE_URL + "/cardlist/searchresults/"
OFFICIAL_CARDLIST_MORE_URL = OFFICIAL_BASE_URL + "/cardlist/cardsearch_ex"

PB_PREFIX_TO_OFFICIAL_EXPANSION = {
    "PL!SP": "PBSP",
    "PL!HS": "PBHS",
    "PL!LS": "PBLS",
    # Current official image assets for PL!S-pb1 are also under PBLS.
    "PL!S": "PBLS",
    "PL!N": "PBnj",
    "PL!": "PBLL",
    "LL": "PBLL",
}
SD_PREFIX_TO_OFFICIAL_EXPANSION = {
    "PL!SP": "SPSD01",
    "PL!N": "NSD01",
    "PL!HS": "HSSD01",
    "PL!LS": "LSSD01",
    "PL!S": "SSD01",
    "PL!": "PLSD01",
}
CL_PREFIX_TO_OFFICIAL_EXPANSION = {
    "PL!HS": "CLHS01",
}
OFFICIAL_RARITY_ALIAS = {
    "R＋": "R2", "R+": "R2",
    "L＋": "L2", "L+": "L2",
    "P＋": "P2", "P+": "P2",
    "PE＋": "PE2", "PE+": "PE2",
    "SEC＋": "SEC2", "SEC+": "SEC2",
    "PR＋": "PR2", "PR+": "PR2",
}
OFFICIAL_RARITY_TOKENS = {
    "SD", "CL", "N", "R", "R2", "L", "L2", "PR", "PR2",
    "P", "P2", "SEC", "SEC2", "SECL", "SRL", "DUO", "AR",
    "RM", "RE", "PE", "PE2", "SECE", "LLE", "PP", "SR", "UR", "SP",
}
OFFICIAL_CARD_RARITY_TAIL_RE = re.compile(r"^(?P<base>.+?)[-_\s](?P<rarity>[A-Za-z0-9＋\+]{1,8})$")


def _card_prefix_from_cardno(cardno: str) -> str:
    parts = (cardno or "").split("-")
    if not parts:
        return cardno
    head = parts[0]
    if head.startswith("PL!"):
        return head
    return head


def official_expansion_from_cardno(cardno: str) -> Optional[str]:
    c = (cardno or "").strip()
    if not c:
        return None
    m = re.search(r"(?:^|-)bp([1-9][0-9]*)(?:-|$)", c, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        return f"BP{n:02d}"
    m = re.search(r"(?:^|-)pb([1-9][0-9]*)(?:-|$)", c, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        base = PB_PREFIX_TO_OFFICIAL_EXPANSION.get(_card_prefix_from_cardno(c))
        if not base:
            return None
        # Official PB product/image folder codes keep the legacy unsuffixed
        # name for pb1, then append a zero-padded product number from pb2 on.
        # Example: PL!SP-pb1 -> PBSP, PL!SP-pb2 -> PBSP02.
        return base if n == 1 else f"{base}{n:02d}"
    m = re.search(r"(?:^|-)sd([1-9][0-9]*)(?:-|$)", c, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        base = SD_PREFIX_TO_OFFICIAL_EXPANSION.get(_card_prefix_from_cardno(c))
        if not base:
            return None
        return re.sub(r"SD\d{2}$", f"SD{n:02d}", base)
    m = re.search(r"(?:^|-)cl([1-9][0-9]*)(?:-|$)", c, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        base = CL_PREFIX_TO_OFFICIAL_EXPANSION.get(_card_prefix_from_cardno(c))
        if not base:
            return None
        return re.sub(r"\d{2}$", f"{n:02d}", base)
    return None


def official_normalize_rarity_token(token: str) -> str:
    t = (token or "").strip().upper().replace("＋", "+")
    return OFFICIAL_RARITY_ALIAS.get(t, t)


def split_display_card_and_rarity(display_card: str) -> Tuple[str, str]:
    s = (display_card or "").strip()
    m = OFFICIAL_CARD_RARITY_TAIL_RE.match(s)
    if not m:
        return s, ""
    base = m.group("base").strip()
    rarity = m.group("rarity").strip()
    if official_normalize_rarity_token(rarity) not in OFFICIAL_RARITY_TOKENS:
        return s, ""
    return base, rarity


def infer_rarity_from_filename(filename: str) -> str:
    stem = Path(urllib.parse.unquote(filename or "")).stem
    parts = [part for part in re.split(r"[-_\s]+", stem) if part]
    if len(parts) < 2:
        return ""
    tail = parts[-1]
    normalized = official_normalize_rarity_token(tail)
    return normalized if normalized in OFFICIAL_RARITY_TOKENS else ""


def infer_cardnumber_from_official_filename(
    filename: str,
    wanted_cardnos: Optional[Set[str]] = None,
) -> str:
    stem = Path(urllib.parse.unquote(filename or "")).stem.strip()
    if not stem:
        return ""

    if wanted_cardnos:
        direct = [
            cn for cn in wanted_cardnos
            if stem == cn or stem.startswith(cn + "-")
        ]
        if direct:
            return max(direct, key=len)

        nums = re.findall(r"(?<!\d)(\d{3})(?!\d)", stem)
        for num in reversed(nums):
            candidates = []
            for cn in wanted_cardnos:
                if not re.search(rf"(?:^|-){re.escape(num)}(?:-|$)", cn):
                    continue
                prefix = re.sub(rf"-{re.escape(num)}(?:-[A-Za-z0-9]+)?$", "", cn)
                if prefix and stem.startswith(prefix + "-"):
                    candidates.append(cn)
            if len(candidates) == 1:
                return candidates[0]

    m = re.search(
        r"(?P<cardno>[A-Z]{1,4}(?:!(?:[A-Z0-9]{0,8})?)?-[A-Za-z0-9]+-\d{3}(?:-[A-Za-z0-9]+)?)",
        stem,
    )
    return m.group("cardno") if m else ""


def parse_official_cardlist_items(
    html: str,
    expansion: str,
    wanted_cardnos: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, Any]] = []
    seen: Set[Tuple[str, str, str]] = set()

    # The official site has changed wrapper classes several times.  The stable
    # signals are the `card` attribute and a card image inside the item.
    for node in soup.select("[card]"):
        display_card = (node.get("card") or "").strip()
        img = node.find("img")
        if not img:
            continue
        src = (img.get("src") or "").strip()
        if not src:
            continue

        parsed = urllib.parse.urlparse(src)
        remote_filename = Path(urllib.parse.unquote(parsed.path)).name
        if not remote_filename:
            continue

        base_cardno, rarity_display = split_display_card_and_rarity(display_card)
        if wanted_cardnos is not None and base_cardno not in wanted_cardnos:
            inferred = infer_cardnumber_from_official_filename(
                remote_filename,
                wanted_cardnos=wanted_cardnos,
            )
            if inferred:
                base_cardno = inferred

        if not base_cardno:
            base_cardno = infer_cardnumber_from_official_filename(
                remote_filename,
                wanted_cardnos=wanted_cardnos,
            )
        if not base_cardno:
            continue
        if wanted_cardnos is not None and base_cardno not in wanted_cardnos:
            continue

        rarity_norm = (
            infer_rarity_from_filename(remote_filename)
            or official_normalize_rarity_token(rarity_display)
        )
        folder = expansion
        mm = re.search(r"/cardlist/([^/]+)/[^/]+$", parsed.path)
        if mm:
            folder = mm.group(1)

        exact_url = (
            f"{OFFICIAL_BASE_URL}/wordpress/wp-content/images/cardlist/"
            f"{folder}/{remote_filename}"
        )
        key = (base_cardno, rarity_norm, remote_filename)
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "cardnumber": base_cardno,
            "card_attr": display_card,
            "rarity_display": rarity_display,
            "rarity_norm": rarity_norm,
            "folder": folder,
            "remote_filename": remote_filename,
            "exact_url": exact_url,
        })
    return items


def extract_official_max_page(html: str) -> int:
    m = re.search(r"max_page\s*=\s*([0-9]+)", html)
    if not m:
        return 1
    try:
        return max(1, int(m.group(1)))
    except Exception:
        return 1


def load_cardnumbers_from_db(db_json: Optional[Path], db_csv: Optional[Path]) -> List[str]:
    out: List[str] = []
    if db_json and db_json.exists():
        try:
            data = json.loads(db_json.read_text(encoding="utf-8"))
            rows = data if isinstance(data, list) else data.get("cards", data)
            if isinstance(rows, list):
                for r in rows:
                    if isinstance(r, dict):
                        cn = r.get("cardnumber")
                        if isinstance(cn, str) and cn.strip():
                            out.append(cn.strip())
        except Exception:
            pass
    if (not out) and db_csv and db_csv.exists():
        try:
            df = pd.read_csv(db_csv)
            if "cardnumber" in df.columns:
                out.extend([str(x).strip() for x in df["cardnumber"].dropna().tolist() if str(x).strip()])
        except Exception:
            pass
    # Canonicalize known rarity tails before manifest grouping so a stale
    # prerelease cardnumber such as PL!SP-bp7-004-P does not poison exact-image
    # lookup.  Manifest loading is set-like; collisions naturally de-duplicate.
    canonical_out: List[str] = []
    for cn in out:
        canonical_cn, _rarity = split_cardnumber_rarity_suffix(cn)
        canonical_out.append(canonical_cn)

    # de-dup keep order
    seen = set()
    uniq: List[str] = []
    for cn in canonical_out:
        if cn not in seen:
            uniq.append(cn)
            seen.add(cn)
    return uniq


def cmd_official_image_manifest(
    db_json: Optional[Path],
    db_csv: Optional[Path],
    outdir: Path,
    cache_dir: Path,
    delay: float,
    user_agent: str,
    timeout: float = 25.0,
    per_card_fallback: bool = True,
    fetch_state: Optional[FetchState] = None,
) -> Path:
    wanted_cardnos = load_cardnumbers_from_db(db_json, db_csv)
    if not wanted_cardnos:
        raise SystemExit("[ERROR] no cardnumber rows found for official image manifest generation")

    if fetch_state is None:
        fetch_state = FetchState(outdir / "failed_fetches.csv", max_429=CONFIG["max_429"])

    wanted_set = set(wanted_cardnos)
    expansion_to_cards: Dict[str, Set[str]] = {}
    unmatched: List[str] = []
    for cn in wanted_cardnos:
        exp = official_expansion_from_cardno(cn)
        if exp:
            expansion_to_cards.setdefault(exp, set()).add(cn)
        else:
            unmatched.append(cn)

    cards_map: Dict[str, List[Dict[str, Any]]] = {}
    expansions_summary: Dict[str, Any] = {}

    def push_items(items: List[Dict[str, Any]]) -> None:
        for item in items:
            cn = item["cardnumber"]
            if cn not in wanted_set:
                continue
            cards_map.setdefault(cn, [])
            key = (item["rarity_norm"], item["remote_filename"], item["folder"])
            seen_keys = {
                (x["rarity_norm"], x["remote_filename"], x["folder"])
                for x in cards_map[cn]
            }
            if key not in seen_keys:
                cards_map[cn].append(item)

    sorted_expansions = sorted(expansion_to_cards.keys())
    print(
        "[IMAGE-MANIFEST] "
        f"targets={len(wanted_cardnos)} expansions={len(sorted_expansions)} "
        f"per_card_fallback={per_card_fallback}"
    )
    for expansion_index, expansion in enumerate(sorted_expansions, 1):
        wanted_for_expansion = expansion_to_cards[expansion]
        print(
            "[IMAGE-MANIFEST] "
            f"expansion={expansion} {expansion_index}/{len(sorted_expansions)} "
            f"target_cards={len(wanted_for_expansion)}"
        )
        variants: List[str] = []
        pages_done = 0
        max_page_seen = 1

        for query_key in ("title", "expansion"):
            first_url = (
                f"{OFFICIAL_CARDLIST_SEARCH_URL}?"
                f"{query_key}={urllib.parse.quote(expansion)}&view=image&sort=new"
            )
            html = fetch(
                first_url,
                cache_dir,
                delay=delay,
                user_agent=user_agent,
                timeout=timeout,
                stage="official_manifest",
                fetch_state=fetch_state,
            )
            page_items = parse_official_cardlist_items(
                html,
                expansion,
                wanted_cardnos=wanted_for_expansion,
            )
            push_items(page_items)
            max_page = extract_official_max_page(html)
            max_page_seen = max(max_page_seen, max_page)
            pages_done += 1
            variants.append(
                f"{first_url} :: items={len(page_items)} max_page={max_page}"
            )

            for page in range(2, max_page + 1):
                more_url = (
                    f"{OFFICIAL_CARDLIST_MORE_URL}?"
                    f"{query_key}={urllib.parse.quote(expansion)}"
                    f"&view=image&page={page}"
                )
                more_html = fetch(
                    more_url,
                    cache_dir,
                    delay=delay,
                    user_agent=user_agent,
                    timeout=timeout,
                    stage="official_manifest",
                    fetch_state=fetch_state,
                )
                more_items = parse_official_cardlist_items(
                    more_html,
                    expansion,
                    wanted_cardnos=wanted_for_expansion,
                )
                push_items(more_items)
                pages_done += 1
                variants.append(f"{more_url} :: items={len(more_items)}")

        expansions_summary[expansion] = {
            "cards_wanted": len(wanted_for_expansion),
            "pages_fetched": pages_done,
            "max_page": max_page_seen,
            "variants": variants,
        }

    missing_after_expansion = [cn for cn in wanted_cardnos if cn not in cards_map]
    if per_card_fallback and missing_after_expansion:
        print(
            "[IMAGE-MANIFEST] "
            f"per_card_fallback_targets={len(missing_after_expansion)}"
        )
        for fallback_index, cn in enumerate(missing_after_expansion, 1):
            if fallback_index == 1 or fallback_index % 25 == 0 or fallback_index == len(missing_after_expansion):
                print(
                    "[IMAGE-MANIFEST] "
                    f"per_card_fallback={fallback_index}/{len(missing_after_expansion)} "
                    f"card={cn}"
                )
            url = (
                f"{OFFICIAL_CARDLIST_SEARCH_URL}?"
                f"cardno={urllib.parse.quote(cn)}&view=image&sort=new"
            )
            try:
                html = fetch(
                    url,
                    cache_dir,
                    delay=delay,
                    user_agent=user_agent,
                    timeout=timeout,
                    stage="official_per_card",
                    fetch_state=fetch_state,
                )
            except FetchSafetyStop:
                raise
            except Exception:
                continue
            push_items(
                parse_official_cardlist_items(
                    html,
                    official_expansion_from_cardno(cn) or "UNKNOWN",
                    wanted_cardnos={cn},
                )
            )

    manifest = {
        "version": 1,
        "source": "official_cardlist",
        "generated_from": {
            "db_json": str(db_json) if db_json else "",
            "db_csv": str(db_csv) if db_csv else "",
        },
        "base_url": f"{OFFICIAL_BASE_URL}/wordpress/wp-content/images/cardlist",
        "cards_total_in_db": len(wanted_cardnos),
        "cards_with_manifest": len(cards_map),
        "cards_missing_manifest": len(
            [cn for cn in wanted_cardnos if cn not in cards_map]
        ),
        "expansions": expansions_summary,
        "cards": {
            cn: cards_map.get(cn, [])
            for cn in wanted_cardnos
            if cards_map.get(cn)
        },
    }

    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "official_image_manifest.json"
    out_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    flat_rows: List[Dict[str, Any]] = []
    for cn, entries in manifest["cards"].items():
        for e in entries:
            flat_rows.append({
                "cardnumber": cn,
                "rarity_norm": e.get("rarity_norm", ""),
                "rarity_display": e.get("rarity_display", ""),
                "folder": e.get("folder", ""),
                "remote_filename": e.get("remote_filename", ""),
                "exact_url": e.get("exact_url", ""),
            })
    flat_path = outdir / "official_image_manifest.tsv"
    pd.DataFrame(
        flat_rows,
        columns=[
            "cardnumber",
            "rarity_norm",
            "rarity_display",
            "folder",
            "remote_filename",
            "exact_url",
        ],
    ).to_csv(flat_path, index=False, encoding="utf-8-sig", sep="\t")
    print(f"[DONE] official image manifest -> {out_path}")
    print(f"[DONE] official image manifest TSV -> {flat_path}")
    return out_path


def sha_path(cache_dir: Path, url: str) -> Path:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
    return cache_dir / f"{h}.html"


def _parse_retry_after_seconds(value: Optional[str]) -> Optional[float]:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return max(0.0, float(int(raw)))
    except Exception:
        pass
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return max(0.0, (dt.astimezone(timezone.utc) - now).total_seconds())
    except Exception:
        return None

def _request_delay_seconds(delay: float) -> float:
    base = max(0.0, float(delay))
    if base <= 0:
        return 0.0
    return base + random.uniform(0.0, base * 0.5)

def _transient_backoff_seconds(retry_index: int) -> float:
    base = min(
        TRANSIENT_MAX_BACKOFF_SEC,
        TRANSIENT_BASE_BACKOFF_SEC * (2 ** max(0, retry_index)),
    )
    return base + random.uniform(0.0, min(5.0, base * 0.25))

def _rate_limit_backoff_seconds(consecutive_429: int) -> float:
    base = min(
        RATE_LIMIT_MAX_BACKOFF_SEC,
        RATE_LIMIT_BASE_BACKOFF_SEC * (2 ** max(0, consecutive_429 - 1)),
    )
    return base + random.uniform(0.0, min(60.0, base * 0.25))

def fetch(
    url: str,
    cache_dir: Path,
    delay: float,
    user_agent: str,
    timeout: float = 25.0,
    *,
    stage: str = "unknown",
    fetch_state: Optional[FetchState] = None,
    cache_ttl_sec: Optional[float] = None,
) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = sha_path(cache_dir, url)
    if p.exists():
        effective_cache_ttl_sec = (
            max(0.0, float(cache_ttl_sec))
            if cache_ttl_sec is not None
            else max(0.0, float(CONFIG.get("cache_ttl_sec", 0.0)))
        )
        try:
            cache_age_sec = max(0.0, time.time() - p.stat().st_mtime)
        except OSError:
            cache_age_sec = effective_cache_ttl_sec + 1.0
        if effective_cache_ttl_sec <= 0.0 or cache_age_sec <= effective_cache_ttl_sec:
            if fetch_state is not None:
                fetch_state.clear_failure(url, stage)
            return p.read_text(encoding="utf-8", errors="ignore")

    attempts = 0
    transient_retry_index = 0
    local_consecutive_429 = 0

    while True:
        effective_delay = (
            fetch_state.effective_delay(delay)
            if fetch_state is not None
            else max(0.0, float(delay))
        )
        wait_before = _request_delay_seconds(effective_delay)
        if wait_before > 0:
            time.sleep(wait_before)

        attempts += 1
        try:
            r = requests.get(
                url,
                headers={"User-Agent": user_agent},
                timeout=timeout,
            )
        except (requests.Timeout, requests.ConnectionError) as e:
            if transient_retry_index < TRANSIENT_MAX_RETRIES:
                wait_sec = _transient_backoff_seconds(transient_retry_index)
                transient_retry_index += 1
                print(
                    f"[WARN] transient network error stage={stage} "
                    f"attempt={attempts} retry_in={wait_sec:.1f}s url={url} ({e})"
                )
                time.sleep(wait_sec)
                continue

            if fetch_state is not None:
                fetch_state.record_failure(
                    url=url,
                    stage=stage,
                    status_code=None,
                    error_type=type(e).__name__,
                    attempts=attempts,
                    last_error=str(e),
                )
            raise

        status = int(r.status_code)

        if status == 429:
            if fetch_state is not None:
                fetch_state.consecutive_429 += 1
                consecutive_429 = fetch_state.consecutive_429
                max_429 = fetch_state.max_429
            else:
                local_consecutive_429 += 1
                consecutive_429 = local_consecutive_429
                max_429 = int(CONFIG["max_429"])

            throttle_before = None
            throttle_after = None
            total_rate_limit_events = consecutive_429
            if fetch_state is not None:
                throttle_before, throttle_after = fetch_state.note_rate_limit()
                total_rate_limit_events = fetch_state.rate_limit_events

            if consecutive_429 >= max_429:
                msg = (
                    f"HTTP 429 repeated {consecutive_429} times "
                    f"(max_429={max_429}) stage={stage} url={url}"
                )
                if fetch_state is not None:
                    fetch_state.record_failure(
                        url=url,
                        stage=stage,
                        status_code=status,
                        error_type="HTTP429SafetyStop",
                        attempts=attempts,
                        last_error=msg,
                    )
                raise FetchSafetyStop(msg)

            retry_after = _parse_retry_after_seconds(r.headers.get("Retry-After"))
            if retry_after is not None:
                wait_sec = retry_after
                wait_source = "Retry-After"
            else:
                wait_sec = _rate_limit_backoff_seconds(consecutive_429)
                wait_source = "exponential-backoff"

            throttle_text = ""
            if throttle_after is not None:
                throttle_text = (
                    f" total_events={total_rate_limit_events} "
                    f"normal_delay_multiplier={throttle_after:.2f}x"
                )
            print(
                f"[RATE-LIMIT] 429 stage={stage} "
                f"consecutive={consecutive_429}/{max_429}"
                f"{throttle_text} "
                f"wait={wait_sec:.1f}s source={wait_source} url={url}"
            )
            time.sleep(wait_sec)
            continue

        if status in TRANSIENT_HTTP_STATUSES:
            if transient_retry_index < TRANSIENT_MAX_RETRIES:
                wait_sec = _transient_backoff_seconds(transient_retry_index)
                transient_retry_index += 1
                print(
                    f"[WARN] HTTP {status} stage={stage} attempt={attempts} "
                    f"retry_in={wait_sec:.1f}s url={url}"
                )
                time.sleep(wait_sec)
                continue

            err = requests.HTTPError(
                f"{status} Server Error after {attempts} attempts for url: {url}",
                response=r,
            )
            if fetch_state is not None:
                fetch_state.record_failure(
                    url=url,
                    stage=stage,
                    status_code=status,
                    error_type="HTTPServerError",
                    attempts=attempts,
                    last_error=str(err),
                )
            raise err

        if 400 <= status < 500:
            try:
                r.raise_for_status()
            except requests.HTTPError as e:
                if fetch_state is not None:
                    fetch_state.record_failure(
                        url=url,
                        stage=stage,
                        status_code=status,
                        error_type="HTTPClientError",
                        attempts=attempts,
                        last_error=str(e),
                    )
                raise

        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            if fetch_state is not None:
                fetch_state.record_failure(
                    url=url,
                    stage=stage,
                    status_code=status,
                    error_type="HTTPError",
                    attempts=attempts,
                    last_error=str(e),
                )
            raise

        if fetch_state is not None:
            throttle_recovery = fetch_state.note_network_success()
            fetch_state.clear_failure(url, stage)
            if throttle_recovery is not None:
                before, after = throttle_recovery
                print(
                    f"[THROTTLE] recovered after "
                    f"{ADAPTIVE_RATE_LIMIT_RECOVERY_SUCCESSES} successful requests "
                    f"normal_delay_multiplier={before:.2f}x->{after:.2f}x"
                )

        html = r.text
        p.write_text(html, encoding="utf-8")
        return html


def norm_url(href: str) -> Optional[str]:
    if not href:
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/llocardgame/"):
        return "https://wikiwiki.jp" + href
    return None


def cardno_name_from_url(url: str) -> Tuple[str, str]:
    try:
        seg = url.split("/llocardgame/")[-1]
        seg = seg.split("#")[0].split("?")[0]
        seg = urllib.parse.unquote(seg)
        parts = seg.split(" ", 1)
        cardno = parts[0].strip()
        name = parts[1].strip() if len(parts) == 2 else ""
        return cardno, name
    except Exception:
        return "", ""


def replace_icons(node: Tag) -> None:
    for img in list(node.find_all("img")):
        alt = (img.get("alt") or img.get("title") or "").strip()
        if not alt:
            src = (img.get("src") or "").split("/")[-1]
            alt = src or "ICON"
        img.replace_with(f"<{alt}>")


def cell_text(cell: Tag) -> str:
    frag = BeautifulSoup(str(cell), "lxml")
    c = frag.find(["th", "td"]) or frag
    replace_icons(c)
    return c.get_text(" ", strip=True)


def normalize_key(k: str) -> str:
    if not k:
        return ""
    k = k.replace("　", " ")
    k = re.sub(r"\s+", "", k)
    k = k.replace("：", "").replace(":", "").replace("・", "")
    return k.strip()


def map_key(k_norm: str) -> Optional[str]:
    if not k_norm:
        return None
    if k_norm in KEY_MAP_EXACT:
        return KEY_MAP_EXACT[k_norm]
    for needle, col in KEY_MAP_CONTAINS:
        if needle in k_norm:
            return col
    return None


def parse_info_table(soup: BeautifulSoup, key_set: Set[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"], recursive=True)
            if len(cells) < 2:
                continue
            k_raw = cell_text(cells[0])
            v_raw = cell_text(cells[1])
            k_norm = normalize_key(k_raw)
            if not k_norm:
                continue
            key_set.add(k_norm)

            col = map_key(k_norm)
            if not col:
                continue

            if col in {"cost", "blade", "score"}:
                mm = re.search(r"(\d+)", v_raw.translate(FW_DIGITS))
                out[col] = mm.group(1) if mm else ""
            else:
                out[col] = v_raw

    # guard
    if out.get("blade_heart", "") == "効果テキスト":
        out["blade_heart"] = ""
    return out


def main_container(soup: BeautifulSoup) -> Tag:
    return soup.find(id="content") or soup.find(id="body") or soup


def soup_main_text(soup: BeautifulSoup) -> str:
    main = main_container(soup)
    replace_icons(main)
    return main.get_text("\n", strip=True)


def extract_effect_text(main_text: str) -> str:
    lines = [ln.strip() for ln in main_text.splitlines() if ln.strip()]
    start_idx = None
    for s in START_MARKERS:
        if s in lines:
            start_idx = lines.index(s) + 1
            break
    if start_idx is None:
        return ""
    out: List[str] = []
    for i in range(start_idx, len(lines)):
        ln = lines[i]
        if ln.startswith("▼") and i > start_idx:
            break
        if ln in STOP_HEADINGS:
            break
        if ln.startswith("最終更新") or ln.startswith("広告") or ln.startswith("これらのキーワード"):
            continue
        out.append(ln)
    return "\n".join(out).strip()


def parse_heart_expr(raw: str) -> Tuple[Dict[str, int], Optional[int], List[str]]:
    counts: Dict[str, int] = {}
    tags: List[str] = []
    if not raw or not isinstance(raw, str):
        return counts, None, tags

    s = raw.translate(FW_DIGITS)
    m_total = TOTAL_RE.search(s)
    total = int(m_total.group(1)) if m_total else None

    for m in ICON_COUNT_RE.finditer(s):
        raw_token = str(m.group(1) or "").strip().replace(" ", "")
        token = raw_token if raw_token in COLOR_MAP else f"({raw_token})"
        n = int(str(m.group(2)).translate(FW_DIGITS)) if m.group(2) else 1
        if token in COLOR_MAP:
            key = COLOR_MAP[token]
            counts[key] = counts.get(key, 0) + n
        else:
            tags.append(f"({raw_token})")
    return counts, total, tags


def _normalize_blade_heart_token(raw_token: str) -> str:
    return (
        str(raw_token or "")
        .translate(FW_DIGITS)
        .translate(PLUS_MINUS_MAP)
        .replace(" ", "")
        .replace("×", "X")
        .replace("ｘ", "X")
        .replace("Ｘ", "X")
        .strip()
    )


def parse_blade_heart_expr(
    raw: str,
) -> Tuple[Dict[str, int], Optional[int], List[str], Dict[str, int]]:
    """Normalize blade-heart icons, including non-heart special icons.

    Returns:
      heart_counts: colored / ALL hearts only
      heart_total : explicit total when present, otherwise colored/ALL + colorless
      unknown_tags: blade-heart tokens not recognized by this parser
      special_counts: {draw, score, colorless}

    The BP07 "double colorless heart" is represented as colorless=2.
    Colorless hearts are deliberately kept separate from `any`: runtime heart
    matching can add colorless to the total-heart pool without using it for any
    colored minimum.
    """
    counts, explicit_total, _ = parse_heart_expr(raw)
    special = {key: 0 for key in BLADE_HEART_SPECIAL_KEYS}
    unknown_tags: List[str] = []

    if not raw or not isinstance(raw, str):
        return counts, explicit_total, unknown_tags, special

    s = raw.translate(FW_DIGITS)
    for m in ICON_COUNT_RE.finditer(s):
        raw_token = str(m.group(1) or "").strip().replace(" ", "")
        token = raw_token if raw_token in COLOR_MAP else f"({raw_token})"
        icon_n = int(str(m.group(2)).translate(FW_DIGITS)) if m.group(2) else 1

        if token in COLOR_MAP:
            continue

        normalized = _normalize_blade_heart_token(raw_token)

        draw_m = re.fullmatch(r"(?:ドロー|DRAW)(?:\+?([0-9]+))?", normalized, re.IGNORECASE)
        if draw_m:
            per_icon = int(draw_m.group(1)) if draw_m.group(1) else 1
            special["draw"] += per_icon * icon_n
            continue

        score_m = re.fullmatch(r"(?:スコア|SCORE)(?:\+?([0-9]+))?", normalized, re.IGNORECASE)
        if score_m:
            per_icon = int(score_m.group(1)) if score_m.group(1) else 1
            special["score"] += per_icon * icon_n
            continue

        normalized_upper = normalized.upper()

        double_colorless_m = re.fullmatch(
            r"(?:ダブル無色(?:ハート)?|DOUBLECOLORLESS(?:HEART)?)(?:X?([0-9]+))?",
            normalized_upper,
            re.IGNORECASE,
        )
        if double_colorless_m:
            repeated = int(double_colorless_m.group(1)) if double_colorless_m.group(1) else 1
            special["colorless"] += 2 * repeated * icon_n
            continue

        colorless_m = re.fullmatch(
            r"(?:無色(?:ハート)?|COLORLESS(?:HEART)?)(?:X?([0-9]+))?",
            normalized_upper,
            re.IGNORECASE,
        )
        if colorless_m:
            repeated = int(colorless_m.group(1)) if colorless_m.group(1) else 1
            special["colorless"] += repeated * icon_n
            continue

        unknown_tags.append(f"({raw_token})")

    heart_total = explicit_total
    if heart_total is None:
        heart_total = sum(counts.values()) + int(special["colorless"])

    return counts, heart_total, unknown_tags, special


def _has_text_value(v: Any) -> bool:
    if v is None:
        return False
    try:
        s = str(v).strip()
    except Exception:
        return False
    if not s:
        return False
    return s not in {"nan", "None", "null"}


def _canonical_card_type_raw(norm: str) -> str:
    return {
        "LIVE": "ライブ",
        "MEMBER": "メンバー",
        "EVENT": "イベント",
        "SUPPORT": "サポート",
    }.get((norm or "").strip().upper(), "")


def norm_card_type(raw: str) -> str:
    if not raw:
        return ""
    s = str(raw).strip()
    if "ライブ" in s:
        return "LIVE"
    if "メンバー" in s:
        return "MEMBER"
    if "イベント" in s:
        return "EVENT"
    if "サポート" in s:
        return "SUPPORT"
    return s


def infer_card_type(raw: Any, required_hearts_raw: Any = "", score: Any = "", cost: Any = "", blade: Any = "", base_hearts_raw: Any = "") -> Tuple[str, str]:
    raw_norm = norm_card_type(str(raw or ""))

    # Explicit non-member/live types stay authoritative.
    if raw_norm in {"EVENT", "SUPPORT"}:
        return raw_norm, _canonical_card_type_raw(raw_norm)

    has_live_signals = _has_text_value(required_hearts_raw) or _has_text_value(score)
    has_member_signals = _has_text_value(cost) or _has_text_value(blade) or _has_text_value(base_hearts_raw)

    inferred = raw_norm
    if has_live_signals and not has_member_signals:
        inferred = "LIVE"
    elif has_member_signals and not has_live_signals:
        inferred = "MEMBER"
    elif not inferred:
        if has_live_signals:
            inferred = "LIVE"
        elif has_member_signals:
            inferred = "MEMBER"

    canonical_raw = _canonical_card_type_raw(inferred) if inferred in {"LIVE", "MEMBER", "EVENT", "SUPPORT"} else str(raw or "")
    return inferred, canonical_raw



# -------------------------
# field schema validation / correction
# -------------------------
# Canonical vocabularies are deliberately explicit. Unknown values are retained
# and written to an unresolved audit instead of being silently discarded.
BUILTIN_FIELD_SCHEMA: Dict[str, Any] = {
    "schema_version": 1,
    "vocabularies": {
        "group": {
            "values": [
                "μ's", "Aqours", "虹ヶ咲", "Liella!", "蓮ノ空",
                "A-RISE", "Saint Snow", "Sunny Passion",
            ],
            "aliases": {
                "μｓ": "μ's", "Muse": "μ's", "ミューズ": "μ's",
                "AQUORS": "Aqours", "アクア": "Aqours",
                "虹ヶ咲学園スクールアイドル同好会": "虹ヶ咲",
                "ニジガク": "虹ヶ咲",
                "Liella": "Liella!", "リエラ": "Liella!",
                "蓮ノ空女学院スクールアイドルクラブ": "蓮ノ空",
                "蓮ノ空女学院": "蓮ノ空", "蓮": "蓮ノ空",
                "ARISE": "A-RISE", "A‐RISE": "A-RISE",
                "SAINT SNOW": "Saint Snow", "SaintSnow": "Saint Snow",
                "SUNNY PASSION": "Sunny Passion", "SunnyPassion": "Sunny Passion",
            },
        },
        "unit": {
            "values": [
                "Printemps", "lily white", "BiBi",
                "CYaRon!", "AZALEA", "Guilty Kiss",
                "DiverDiva", "A・ZU・NA", "QU4RTZ", "R3BIRTH",
                "CatChu!", "KALEIDOSCORE", "5yncri5e!",
                "スリーズブーケ", "DOLLCHESTRA", "みらくらぱーく！", "Edel Note",
            ],
            "aliases": {
                "LILY WHITE": "lily white", "lilywhite": "lily white",
                "CYaRon": "CYaRon!", "GuiltyKiss": "Guilty Kiss",
                "A-ZU-NA": "A・ZU・NA", "A･ZU･NA": "A・ZU・NA", "AZUNA": "A・ZU・NA",
                "CatChu": "CatChu!", "5yncri5e": "5yncri5e!",
                "Cerise Bouquet": "スリーズブーケ",
                "Mira-Cra Park!": "みらくらぱーく！", "Mira-Cra Park": "みらくらぱーく！",
                "みらくらぱーく": "みらくらぱーく！", "EdelNote": "Edel Note",
            },
        },
        "card_type_norm": {
            "values": ["MEMBER", "LIVE", "EVENT", "SUPPORT"],
            "aliases": {
                "メンバー": "MEMBER", "メンバーカード": "MEMBER",
                "ライブ": "LIVE", "ライブカード": "LIVE",
                "イベント": "EVENT", "イベントカード": "EVENT",
                "サポート": "SUPPORT", "サポートカード": "SUPPORT",
            },
        },
        "card_type_raw": {
            "values": ["メンバー", "ライブ", "イベント", "サポート"],
            "aliases": {
                "MEMBER": "メンバー", "メンバーカード": "メンバー",
                "LIVE": "ライブ", "ライブカード": "ライブ",
                "EVENT": "イベント", "イベントカード": "イベント",
                "SUPPORT": "サポート", "サポートカード": "サポート",
            },
        },
    },
    "numeric_fields": {
        "cost": {"min": 0, "max": 99, "integer": True},
        "blade": {"min": 0, "max": 99, "integer": True},
        "score": {"min": 0, "max": 99, "integer": True},
        "base_hearts_total": {"min": 0, "max": 99, "integer": True},
        "required_hearts_total": {"min": 0, "max": 99, "integer": True},
        "blade_heart_total": {"min": 0, "max": 99, "integer": True},
    },
    "json_count_fields": {
        "base_hearts_counts_json": ["pink", "red", "yellow", "green", "blue", "purple", "white", "black", "any", "all"],
        "required_hearts_counts_json": ["pink", "red", "yellow", "green", "blue", "purple", "white", "black", "any", "all"],
        "blade_heart_counts_json": ["pink", "red", "yellow", "green", "blue", "purple", "white", "black", "any", "all"],
        "blade_heart_special_counts_json": ["draw", "score", "colorless"],
    },
}

_FIELD_SPLIT_RE = re.compile(r"\s*(?:/|／|、|,|\||・|;|；)\s*")
_EMPTY_FIELD_MARKERS = {"", "-", "—", "―", "なし", "無し", "nan", "none", "null"}


def _is_empty_field_value(value: Any) -> bool:
    """Treat CSV NaN and configured source placeholders as semantic blanks."""
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    return str(value).strip().casefold() in _EMPTY_FIELD_MARKERS


def _normalized_field_text(value: Any) -> str:
    """Canonical comparison form used to avoid auditing blank-marker cleanup."""
    return _join_field_tokens(_field_tokens(value))


def _deep_merge_schema(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(base, ensure_ascii=False))
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge_schema(out[key], value)
        else:
            out[key] = value
    return out


def load_field_schema(path: Optional[Path]) -> Dict[str, Any]:
    schema = json.loads(json.dumps(BUILTIN_FIELD_SCHEMA, ensure_ascii=False))
    if path and path.exists():
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                schema = _deep_merge_schema(schema, obj)
        except Exception as exc:
            print(f"[WARN] failed to load field schema: {path} ({exc})")
    return schema


def _field_tokens(value: Any) -> List[str]:
    if _is_empty_field_value(value):
        return []
    raw = str(value).strip()
    return [x.strip() for x in _FIELD_SPLIT_RE.split(raw) if x.strip()]


def _join_field_tokens(tokens: List[str]) -> str:
    return " / ".join(dict.fromkeys(x for x in tokens if x))


def _vocab_maps(schema: Dict[str, Any], field: str) -> Tuple[Set[str], Dict[str, str], Dict[str, str]]:
    spec = schema.get("vocabularies", {}).get(field, {})
    values = {str(x) for x in spec.get("values", []) if str(x).strip()}
    aliases = {str(k): str(v) for k, v in spec.get("aliases", {}).items()}
    folded: Dict[str, str] = {}
    for value in values:
        folded[value.casefold()] = value
    for alias, canonical in aliases.items():
        folded[alias.casefold()] = canonical
    return values, aliases, folded


def _audit_row(rec: Dict[str, Any], *, field: str, source_value: Any, corrected_value: Any,
               action: str, reason: str, status: str) -> Dict[str, Any]:
    return {
        "cardnumber": str(rec.get("cardnumber", "") or ""),
        "cardname": str(rec.get("cardname", "") or ""),
        "field": field,
        "source_value": "" if source_value is None else str(source_value),
        "corrected_value": "" if corrected_value is None else str(corrected_value),
        "action": action,
        "reason": reason,
        "status": status,
        "source_url": str(rec.get("source_url", "") or ""),
    }


def validate_and_correct_record_fields(
    rec: Dict[str, Any], schema: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    corrections: List[Dict[str, Any]] = []
    unresolved: List[Dict[str, Any]] = []

    # First canonicalize every enum vocabulary independently.
    for field in schema.get("vocabularies", {}):
        if field not in rec:
            continue
        source = rec.get(field, "")
        tokens = _field_tokens(source)
        if not tokens:
            # Normalize source placeholders internally, but do not count routine
            # blank cleanup ("-", NaN, None, etc.) as a semantic correction.
            if source != "":
                rec[field] = ""
            continue
        allowed, _aliases, folded = _vocab_maps(schema, field)
        canonical_tokens: List[str] = []
        unknown_tokens: List[str] = []
        for token in tokens:
            canonical = folded.get(token.casefold())
            if canonical:
                canonical_tokens.append(canonical)
            else:
                canonical_tokens.append(token)
                unknown_tokens.append(token)
        corrected = _join_field_tokens(canonical_tokens)
        if corrected != _normalized_field_text(source):
            rec[field] = corrected
            corrections.append(_audit_row(
                rec, field=field, source_value=source, corrected_value=corrected,
                action="CANONICALIZE_ENUM", reason="matched canonical vocabulary or alias",
                status="CORRECTED",
            ))
        for token in unknown_tokens:
            # A value belonging to the opposite taxonomy is resolved by the
            # cross-field repair below, so do not report it as unresolved here.
            if field == "group":
                _a, _b, opposite_folded = _vocab_maps(schema, "unit")
                if token.casefold() in opposite_folded:
                    continue
            if field == "unit":
                _a, _b, opposite_folded = _vocab_maps(schema, "group")
                if token.casefold() in opposite_folded:
                    continue
            unresolved.append(_audit_row(
                rec, field=field, source_value=token, corrected_value=token,
                action="UNKNOWN_ENUM_VALUE_RETAINED",
                reason="value is not in the configured canonical vocabulary",
                status="UNRESOLVED",
            ))

    # Cross-field taxonomy repair. Group and unit are mutually exclusive vocabularies.
    group_allowed, _, group_folded = _vocab_maps(schema, "group")
    unit_allowed, _, unit_folded = _vocab_maps(schema, "unit")
    group_source = rec.get("group", "")
    unit_source = rec.get("unit", "")
    group_tokens = _field_tokens(group_source)
    unit_tokens = _field_tokens(unit_source)

    corrected_groups: List[str] = []
    corrected_units: List[str] = []
    moved_to_group: List[str] = []
    moved_to_unit: List[str] = []

    for token in group_tokens:
        group_value = group_folded.get(token.casefold())
        unit_value = unit_folded.get(token.casefold())
        if group_value:
            corrected_groups.append(group_value)
        elif unit_value:
            corrected_units.append(unit_value)
            moved_to_unit.append(token)
        else:
            corrected_groups.append(token)

    for token in unit_tokens:
        unit_value = unit_folded.get(token.casefold())
        group_value = group_folded.get(token.casefold())
        if unit_value:
            corrected_units.append(unit_value)
        elif group_value:
            corrected_groups.append(group_value)
            moved_to_group.append(token)
        else:
            corrected_units.append(token)

    new_group = _join_field_tokens(corrected_groups)
    new_unit = _join_field_tokens(corrected_units)
    if new_group != _normalized_field_text(group_source):
        rec["group"] = new_group
        corrections.append(_audit_row(
            rec, field="group", source_value=group_source, corrected_value=new_group,
            action="CROSS_FIELD_TAXONOMY_REPAIR",
            reason=("moved unit vocabulary out of group: " + ", ".join(moved_to_unit)) if moved_to_unit else "deduplicated/canonicalized group values",
            status="CORRECTED",
        ))
    if new_unit != _normalized_field_text(unit_source):
        rec["unit"] = new_unit
        corrections.append(_audit_row(
            rec, field="unit", source_value=unit_source, corrected_value=new_unit,
            action="CROSS_FIELD_TAXONOMY_REPAIR",
            reason=("moved group vocabulary out of unit: " + ", ".join(moved_to_group)) if moved_to_group else "deduplicated/canonicalized unit values",
            status="CORRECTED",
        ))

    # Numeric domain validation. Invalid values are retained and surfaced.
    for field, spec in schema.get("numeric_fields", {}).items():
        if field not in rec or _is_empty_field_value(rec.get(field)):
            continue
        raw = rec.get(field)
        text = str(raw).strip().translate(FW_DIGITS)
        try:
            number = float(text)
        except ValueError:
            unresolved.append(_audit_row(
                rec, field=field, source_value=raw, corrected_value=raw,
                action="INVALID_NUMERIC_RETAINED", reason="not a numeric value",
                status="UNRESOLVED",
            ))
            continue
        if spec.get("integer") and not number.is_integer():
            unresolved.append(_audit_row(
                rec, field=field, source_value=raw, corrected_value=raw,
                action="NON_INTEGER_RETAINED", reason="field requires an integer",
                status="UNRESOLVED",
            ))
        lo, hi = spec.get("min"), spec.get("max")
        if (lo is not None and number < float(lo)) or (hi is not None and number > float(hi)):
            unresolved.append(_audit_row(
                rec, field=field, source_value=raw, corrected_value=raw,
                action="OUT_OF_RANGE_RETAINED", reason=f"expected range {lo}..{hi}",
                status="UNRESOLVED",
            ))

    # Structured JSON count validation.
    for field, allowed_keys_raw in schema.get("json_count_fields", {}).items():
        if field not in rec or _is_empty_field_value(rec.get(field)):
            continue
        ok, obj = safe_json_loads(rec.get(field))
        if not ok or not isinstance(obj, dict):
            unresolved.append(_audit_row(
                rec, field=field, source_value=rec.get(field), corrected_value=rec.get(field),
                action="INVALID_JSON_RETAINED", reason="expected a JSON object",
                status="UNRESOLVED",
            ))
            continue
        allowed_keys = {str(x) for x in allowed_keys_raw}
        unknown_keys = sorted(set(str(k) for k in obj) - allowed_keys)
        bad_values = [str(k) for k, v in obj.items() if not isinstance(v, int) or v < 0]
        if unknown_keys or bad_values:
            unresolved.append(_audit_row(
                rec, field=field, source_value=rec.get(field), corrected_value=rec.get(field),
                action="INVALID_COUNT_MAP_RETAINED",
                reason=f"unknown_keys={unknown_keys}; nonnegative_integer_required={bad_values}",
                status="UNRESOLVED",
            ))

    # Cross-field card-type consistency audit after infer_card_type repair.
    inferred, _raw = infer_card_type(
        rec.get("card_type_raw", ""),
        required_hearts_raw=rec.get("required_hearts_raw", ""),
        score=rec.get("score", ""), cost=rec.get("cost", ""),
        blade=rec.get("blade", ""), base_hearts_raw=rec.get("base_hearts_raw", ""),
    )
    current = str(rec.get("card_type_norm", "") or "").strip()
    if inferred and current and inferred != current:
        source = current
        rec["card_type_norm"] = inferred
        canonical_raw = _canonical_card_type_raw(inferred)
        if canonical_raw:
            rec["card_type_raw"] = canonical_raw
        corrections.append(_audit_row(
            rec, field="card_type_norm", source_value=source, corrected_value=inferred,
            action="CARD_TYPE_SIGNAL_REPAIR",
            reason="cost/heart/score field signals contradicted the extracted card type",
            status="CORRECTED",
        ))

    return corrections, unresolved


def _write_field_validation_audits(
    outdir: Path, corrections: List[Dict[str, Any]], unresolved: List[Dict[str, Any]], label: str,
    idempotence_failures: Optional[List[Dict[str, Any]]] = None,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    final_names = label in {"normalize_csv", "normalize_final"}
    suffix = "" if final_names else "_" + re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_").lower()
    fields = ["cardnumber", "cardname", "field", "source_value", "corrected_value", "action", "reason", "status", "source_url"]
    datasets = [
        ("field_validation_corrections", corrections),
        ("field_validation_unresolved", unresolved),
        ("field_validation_idempotence_failures", idempotence_failures or []),
    ]
    for stem, rows in datasets:
        tsv_path = outdir / f"{stem}{suffix}.tsv"
        json_path = outdir / f"{stem}{suffix}.json"
        with tsv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
            writer.writeheader(); writer.writerows(rows)
        json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    # Compact field/action summary keeps real anomalies visible even for large DBs.
    summary_rows: List[Dict[str, Any]] = []
    for category, rows in (("CORRECTED", corrections), ("UNRESOLVED", unresolved), ("IDEMPOTENCE_FAILURE", idempotence_failures or [])):
        counts = Counter((str(r.get("field", "")), str(r.get("action", "")), str(r.get("reason", ""))) for r in rows)
        for (field, action, reason), count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            summary_rows.append({"category": category, "field": field, "action": action, "reason": reason, "count": count})
    summary_tsv = outdir / f"field_validation_summary{suffix}.tsv"
    summary_json = outdir / f"field_validation_summary{suffix}.json"
    summary_fields = ["category", "field", "action", "reason", "count"]
    with summary_tsv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields, delimiter="\t")
        writer.writeheader(); writer.writerows(summary_rows)
    summary_json.write_text(json.dumps(summary_rows, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_field_schema_to_records(
    records: List[Dict[str, Any]], *, outdir: Path, label: str, schema_path: Optional[Path]
) -> Tuple[int, int]:
    schema = load_field_schema(schema_path)
    corrections: List[Dict[str, Any]] = []
    unresolved: List[Dict[str, Any]] = []
    valid_records: List[Dict[str, Any]] = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        valid_records.append(rec)
        c, u = validate_and_correct_record_fields(rec, schema)
        corrections.extend(c); unresolved.extend(u)

    # A second pass must produce no further semantic corrections.  It is cheap,
    # catches ordering bugs in repair rules, and leaves the output fully settled.
    idempotence_failures: List[Dict[str, Any]] = []
    for rec in valid_records:
        c2, _u2 = validate_and_correct_record_fields(rec, schema)
        idempotence_failures.extend(c2)

    _write_field_validation_audits(
        outdir, corrections, unresolved, label,
        idempotence_failures=idempotence_failures,
    )
    idem_status = "PASS" if not idempotence_failures else "FAIL"
    print(
        f"[FIELD-SCHEMA] label={label} corrected={len(corrections)} "
        f"unresolved={len(unresolved)} idempotence={idem_status} "
        f"idempotence_corrections={len(idempotence_failures)}"
    )
    return len(corrections), len(unresolved)

def normalize_effect_text(effect_text: str) -> str:
    if not effect_text or not isinstance(effect_text, str):
        return ""
    s = effect_text.translate(FW_DIGITS)
    s = s.replace("×", "x").replace("ｘ", "x").replace("Ｘ", "X")
    s = re.sub(r"(<\([^)]+\)>)\s*(?:x|X)\s*(\d+)", r"\1\2", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s).strip()
    return s


def classify_effect_text_status(effect_text_raw: Any, effect_text_norm: Any = "") -> str:
    raw = normalize_effect_text(effect_text_raw) if isinstance(effect_text_raw, str) else ""
    norm = normalize_effect_text(effect_text_norm) if isinstance(effect_text_norm, str) else ""
    s = norm or raw
    return "NO_ABILITY" if s in NO_ABILITY_MARKERS else "HAS_TEXT"


def extract_effect_tokens(effect_text_norm: str) -> Dict[str, Any]:
    tokens: Dict[str, Any] = {"hearts": {}, "blade_mentions": []}
    if not effect_text_norm:
        return tokens
    s = effect_text_norm

    for m in ICON_COUNT_RE.finditer(s):
        raw_token = str(m.group(1) or "").strip().replace(" ", "")
        token = raw_token if raw_token in COLOR_MAP else f"({raw_token})"
        n = int(str(m.group(2)).translate(FW_DIGITS)) if m.group(2) else 1
        if token in COLOR_MAP:
            key = COLOR_MAP[token]
            tokens["hearts"][key] = tokens["hearts"].get(key, 0) + n
        else:
            tokens.setdefault("tags", []).append(f"({raw_token})")
    return tokens


def extract_product_urls(products_html: str, products_url: str) -> List[str]:
    soup = BeautifulSoup(products_html, "lxml")
    urls: Set[str] = set()
    for a in soup.find_all("a", href=True):
        u = norm_url(a["href"])
        if not u:
            continue
        if "/::cmd/" in u:
            continue
        if "wikiwiki.jp/llocardgame/" in u:
            urls.add(u)
    urls.discard(products_url)
    return sorted(urls)


def extract_card_links_from_product(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    urls: Set[str] = set()
    for a in soup.find_all("a", href=True):
        u = norm_url(a["href"])
        if not u or "/::cmd/" in u:
            continue
        cardno, _ = cardno_name_from_url(u)
        if CARDNO_IN_TEXT.match(cardno):
            urls.add(u)
    return sorted(urls)


def parse_card_page(url: str, html: str, key_set: Set[str], do_normalize: bool) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
    cardno_u, name_u = cardno_name_from_url(url)

    info = parse_info_table(soup, key_set)
    main_text = soup_main_text(soup)
    effect_text = extract_effect_text(main_text)

    card_type_raw = info.get("card_type", "")
    base_raw = info.get("base_hearts", "")
    req_raw = info.get("required_hearts", "")
    bh_raw = info.get("blade_heart", "")

    rec: Dict[str, Any] = {
        "cardnumber": cardno_u,
        "cardname": name_u,
        "page_title": title,
        "card_type_raw": card_type_raw,
        "work_title": info.get("work_title", ""),
        "group": info.get("group", ""),
        "unit": info.get("unit", ""),
        "cost": info.get("cost", ""),
        "blade": info.get("blade", ""),
        "blade_heart_raw": bh_raw,
        "base_hearts_raw": base_raw,
        "required_hearts_raw": req_raw,
        "score": info.get("score", ""),
        "effect_text_raw": effect_text,
        "source_url": url,
    }

    if do_normalize:
        inferred_type, canonical_raw = infer_card_type(
            card_type_raw,
            required_hearts_raw=req_raw,
            score=info.get("score", ""),
            cost=info.get("cost", ""),
            blade=info.get("blade", ""),
            base_hearts_raw=base_raw,
        )
        rec["card_type_raw"] = canonical_raw or card_type_raw
        rec["card_type_norm"] = inferred_type

        base_counts, base_total, base_tags = parse_heart_expr(base_raw)
        req_counts, req_total, req_tags = parse_heart_expr(req_raw)
        bh_counts, bh_total, bh_tags, bh_special = parse_blade_heart_expr(bh_raw)

        rec["base_hearts_counts_json"] = json.dumps(base_counts, ensure_ascii=False)
        rec["base_hearts_total"] = base_total if base_total is not None else sum(base_counts.values())
        rec["base_hearts_tags_json"] = json.dumps(base_tags, ensure_ascii=False)

        rec["required_hearts_counts_json"] = json.dumps(req_counts, ensure_ascii=False)
        rec["required_hearts_total"] = req_total if req_total is not None else sum(req_counts.values())
        rec["required_hearts_tags_json"] = json.dumps(req_tags, ensure_ascii=False)

        rec["blade_heart_counts_json"] = json.dumps(bh_counts, ensure_ascii=False)
        rec["blade_heart_total"] = bh_total if bh_total is not None else sum(bh_counts.values())
        rec["blade_heart_tags_json"] = json.dumps(bh_tags, ensure_ascii=False)
        rec["blade_heart_special_counts_json"] = json.dumps(bh_special, ensure_ascii=False)
        rec["blade_heart_draw_n"] = int(bh_special.get("draw", 0) or 0)
        rec["blade_heart_score_n"] = int(bh_special.get("score", 0) or 0)
        rec["blade_heart_colorless_n"] = int(bh_special.get("colorless", 0) or 0)

        eff_norm = normalize_effect_text(effect_text)
        eff_status = classify_effect_text_status(effect_text, eff_norm)
        rec["effect_text_norm"] = eff_norm
        rec["effect_text_status"] = eff_status
        rec["effect_text_is_no_ability"] = 1 if eff_status == "NO_ABILITY" else 0
        rec["effect_tokens_json"] = json.dumps(extract_effect_tokens(eff_norm), ensure_ascii=False)

    return rec


def load_resume_records(resume_csv: Path, resume_json: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    if resume_json.exists():
        try:
            data = json.loads(resume_json.read_text(encoding="utf-8"))
            if isinstance(data, list):
                records = [r for r in data if isinstance(r, dict)]
        except Exception as e:
            print(f"[WARN] resume JSON load failed: {resume_json} ({e})")

    if not records and resume_csv.exists():
        try:
            df = pd.read_csv(resume_csv)
            records = df.to_dict(orient="records")
        except pd.errors.EmptyDataError:
            records = []
        except Exception as e:
            print(f"[WARN] resume CSV load failed: {resume_csv} ({e})")

    if not records:
        return []

    df = pd.DataFrame(records)
    if "source_url" in df.columns:
        df = df.drop_duplicates(subset=["source_url"], keep="last")
    if "cardnumber" in df.columns:
        df = df.drop_duplicates(subset=["cardnumber"], keep="last")
    return df.to_dict(orient="records")

def load_resume_urls_from_records(records: List[Dict[str, Any]]) -> Set[str]:
    return {
        str(r.get("source_url", "") or "").strip()
        for r in records
        if str(r.get("source_url", "") or "").strip()
    }

def _write_failed_urls(outdir: Path, failed: List[str]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    uniq: List[str] = []
    seen: Set[str] = set()
    for url in failed:
        u = str(url or "").strip()
        if u and u not in seen:
            uniq.append(u)
            seen.add(u)
    (outdir / "failed_urls.txt").write_text("\n".join(uniq), encoding="utf-8")

def _write_scrape_checkpoint(
    outdir: Path,
    records: List[Dict[str, Any]],
    keys_found: Set[str],
    failed: List[str],
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    if records:
        pd.DataFrame(records).to_csv(
            outdir / "cards_min_checkpoint.csv",
            index=False,
            encoding="utf-8-sig",
        )
    if keys_found:
        (outdir / "keys_found.txt").write_text(
            "\n".join(sorted(keys_found)),
            encoding="utf-8",
        )
    _write_failed_urls(outdir, failed)


def finalize_outputs(outdir: Path, records: List[Dict[str, Any]], keys_found: Set[str], failed: List[str], manual_overrides: Optional[Path] = None, field_schema: Optional[Path] = None) -> Tuple[Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    canonicalize_cardnumbers_in_records(
        records,
        outdir=outdir,
        label="scrape_finalize",
    )
    overrides = load_card_text_overrides(manual_overrides)
    apply_card_text_overrides_to_records(records, overrides, label="scrape/finalize")
    apply_field_schema_to_records(records, outdir=outdir, label="scrape_finalize", schema_path=field_schema)
    df = pd.DataFrame(records)
    if "source_url" in df.columns:
        df = df.drop_duplicates(subset=["source_url"], keep="last")
    if "cardnumber" in df.columns:
        df = df.drop_duplicates(subset=["cardnumber"], keep="last")

    out_json = outdir / "cards_min.json"
    out_csv = outdir / "cards_min.csv"
    out_json.write_text(json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2), encoding="utf-8")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    if keys_found:
        (outdir / "keys_found.txt").write_text("\n".join(sorted(keys_found)), encoding="utf-8")
    _write_failed_urls(outdir, failed)
    return out_csv, out_json



# -------------------------
# product release registry
# -------------------------
PRODUCT_RELEASE_REGISTRY_FILENAME = "product_release_registry.json"
PRODUCT_RELEASE_REGISTRY_AUDIT_FILENAME = "product_release_registry_audit.tsv"
_RELEASE_DATE_PATTERNS = [
    re.compile(r"発売日\s*[：:]?\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"),
    re.compile(r"発売日\s*[：:]?\s*(\d{4})[./-](\d{1,2})[./-](\d{1,2})"),
]


def extract_product_page_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)
        if title:
            return title
    title_tag = soup.find("title")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""
    title = re.sub(
        r"\s*-\s*ラブライブ！シリーズ.*$",
        "",
        title,
    ).strip()
    return title


def extract_release_date_from_product_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    for pattern in _RELEASE_DATE_PATTERNS:
        m = pattern.search(text)
        if not m:
            continue
        try:
            value = datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
            ).date()
        except ValueError:
            continue
        return value.isoformat()
    return ""


def _product_category_for_title(title: str) -> str:
    text = str(title or "")
    if "プレミアムブースター" in text:
        return "PB"
    if "ブースターパック" in text:
        return "BP"
    if "スタートデッキ" in text:
        return "SD"
    if "コレクション" in text or "クリアポケット" in text:
        return "CL"
    return ""


def _code_matches_product_category(code: str, category: str) -> bool:
    value = str(code or "").upper()
    if category == "BP":
        return bool(re.fullmatch(r"BP\d{2}", value))
    if category == "PB":
        return value.startswith("PB")
    if category == "SD":
        return bool(re.search(r"SD\d{2}$", value))
    if category == "CL":
        return value.startswith("CL")
    return True


def _code_sequence_number(code: str) -> int:
    m = re.search(r"(\d+)$", str(code or ""))
    return int(m.group(1)) if m else 0


def _established_code_owners(
    previous_entries_by_url: Dict[str, Dict[str, Any]],
) -> Dict[str, Set[str]]:
    owners: Dict[str, Set[str]] = {}
    for url, raw in previous_entries_by_url.items():
        if not isinstance(raw, dict):
            continue
        if str(raw.get("status", "") or "") != "MATCHED":
            continue
        code = str(raw.get("product_code", "") or "").strip().upper()
        if code:
            owners.setdefault(code, set()).add(str(url))
    return owners


def resolve_product_code(
    *,
    product_url: str,
    title: str,
    release_date: str,
    code_counts: Counter[str],
    previous_entries_by_url: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[str, str, str]:
    if not release_date:
        return "", "NO_RELEASE_DATE", "release date not found on product page"
    if not code_counts:
        return "", "NO_PRODUCT_CODE", "no product-code-bearing card links found"

    previous_entries_by_url = previous_entries_by_url or {}
    owners = _established_code_owners(previous_entries_by_url)
    category = _product_category_for_title(title)
    matching = {
        str(code).upper(): int(count)
        for code, count in code_counts.items()
        if _code_matches_product_category(str(code), category)
    }
    if not matching:
        return (
            "",
            "AMBIGUOUS_PRODUCT_CODE",
            f"no card-link expansion matches product category={category or 'unknown'}",
        )

    previous = previous_entries_by_url.get(str(product_url), {})
    previous_code = str(previous.get("product_code", "") or "").strip().upper()
    if previous_code and previous_code in matching:
        other_owners = owners.get(previous_code, set()) - {str(product_url)}
        if not other_owners:
            return (
                previous_code,
                "MATCHED",
                "preserved previously confirmed product code for the same source URL",
            )

    # A new expansion generally introduces at least one card-number series not
    # already owned by another product page. Reprints from old products must not
    # win merely because they are more numerous on an incomplete prerelease page.
    unowned = {
        code: count
        for code, count in matching.items()
        if not owners.get(code)
    }
    if unowned:
        ordered = sorted(
            unowned.items(),
            key=lambda item: (item[1], _code_sequence_number(item[0]), item[0]),
            reverse=True,
        )
        best_code, best_count = ordered[0]
        tied = [
            code for code, count in ordered
            if count == best_count and _code_sequence_number(code) == _code_sequence_number(best_code)
        ]
        if len(tied) == 1:
            return (
                best_code,
                "MATCHED",
                "selected unassigned card-number series matching the product category",
            )

    # Every matching code already belongs to another product. This usually means
    # the page currently contains only reprints or related-card links. Keep it as
    # unresolved until its own card-number series appears rather than overwriting
    # an established product.
    return (
        "",
        "UNRESOLVED_PRODUCT_CODE",
        "all matching card-number series are already assigned to other product pages",
    )


def build_product_registry_entry(
    product_url: str,
    html: str,
    *,
    previous_entries_by_url: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    card_links = extract_card_links_from_product(html)
    cardnumbers: List[str] = []
    code_counts: Counter[str] = Counter()
    for url in card_links:
        cardno, _name = cardno_name_from_url(url)
        cardno = str(cardno or "").strip()
        if not cardno:
            continue
        canonical, _rarity = split_cardnumber_rarity_suffix(cardno)
        code = official_expansion_from_cardno(canonical)
        if not code:
            continue
        cardnumbers.append(canonical)
        code_counts[code.upper()] += 1

    release_date = extract_release_date_from_product_html(html)
    title = extract_product_page_title(html)
    product_code, status, reason = resolve_product_code(
        product_url=product_url,
        title=title,
        release_date=release_date,
        code_counts=code_counts,
        previous_entries_by_url=previous_entries_by_url,
    )

    return {
        "product_code": product_code,
        "release_date": release_date,
        "title": title,
        "source_url": product_url,
        "status": status,
        "reason": reason,
        "card_link_count": len(cardnumbers),
        "product_code_counts": dict(sorted(code_counts.items())),
        "sample_cardnumbers": sorted(set(cardnumbers))[:20],
    }


def write_product_release_registry(
    outdir: Path,
    *,
    products_url: str,
    entries: List[Dict[str, Any]],
) -> Tuple[Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    registry_path = outdir / PRODUCT_RELEASE_REGISTRY_FILENAME
    audit_path = outdir / PRODUCT_RELEASE_REGISTRY_AUDIT_FILENAME

    products: Dict[str, Dict[str, Any]] = {}
    collisions: Dict[str, List[Dict[str, Any]]] = {}

    for entry in entries:
        if entry.get("status") != "MATCHED":
            continue
        code = str(entry.get("product_code", "") or "").strip().upper()
        if not code:
            continue
        candidate = {
            "release_date": entry.get("release_date", ""),
            "title": entry.get("title", ""),
            "source_url": entry.get("source_url", ""),
            "card_link_count": entry.get("card_link_count", 0),
            "product_code_counts": entry.get("product_code_counts", {}),
            "sample_cardnumbers": entry.get("sample_cardnumbers", []),
        }
        if code not in products:
            products[code] = candidate
            continue

        old = products[code]
        old_sig = (str(old.get("release_date", "")), str(old.get("source_url", "")))
        new_sig = (str(candidate.get("release_date", "")), str(candidate.get("source_url", "")))
        if old_sig == new_sig:
            products[code] = candidate
            continue

        collisions.setdefault(code, [dict(old)]).append(dict(candidate))

        def confidence(row: Dict[str, Any]) -> Tuple[int, float, int]:
            counts = row.get("product_code_counts", {})
            own = 0
            total = 0
            if isinstance(counts, dict):
                for raw_code, raw_count in counts.items():
                    try:
                        count = int(raw_count or 0)
                    except (TypeError, ValueError):
                        count = 0
                    total += count
                    if str(raw_code).upper() == code:
                        own += count
            ratio = (own / total) if total else 0.0
            try:
                links = int(row.get("card_link_count", 0) or 0)
            except (TypeError, ValueError):
                links = 0
            return own, ratio, links

        # Keep the higher-confidence owner. A weak prerelease page containing a
        # few reprints can no longer erase a well-established product.
        if confidence(candidate) > confidence(old):
            products[code] = candidate

    # Keep a page-level registry in addition to the product-code registry.
    # Multiple WIKIWIKI product pages may collapse to the same inferred code or
    # remain unmatched; those pages still need incremental scan history so they
    # are not rediscovered as "new_product" on every updater run.
    page_entries = [
        dict(entry)
        for entry in sorted(
            entries,
            key=lambda row: str(row.get("source_url", "") or ""),
        )
        if str(entry.get("source_url", "") or "").strip()
    ]

    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_products_url": products_url,
        "products": dict(sorted(products.items())),
        "page_entries": page_entries,
        "collisions": {
            code: rows for code, rows in sorted(collisions.items())
        },
    }
    registry_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    fields = [
        "product_code",
        "release_date",
        "title",
        "status",
        "reason",
        "card_link_count",
        "product_code_counts",
        "source_url",
    ]
    with audit_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for entry in entries:
            row = {key: entry.get(key, "") for key in fields}
            row["product_code_counts"] = json.dumps(
                entry.get("product_code_counts", {}),
                ensure_ascii=False,
                sort_keys=True,
            )
            writer.writerow(row)

    print(
        f"[PRODUCT-REGISTRY] products={len(products)} "
        f"collisions={len(collisions)} entries={len(entries)} "
        f"path={registry_path}"
    )
    return registry_path, audit_path



def load_existing_product_registry_entries(
    registry_path: Path,
) -> Dict[str, Dict[str, Any]]:
    """Load prior product-page scan rows keyed by exact source URL.

    Schema v2 stores every product-page row in ``page_entries``. For migration
    from the earlier registry, recover the full page list from the sibling audit
    TSV when available, then fall back to the product-code registry.
    """
    payload: Dict[str, Any] = {}
    if registry_path.exists():
        try:
            raw_payload = json.loads(registry_path.read_text(encoding="utf-8"))
            if isinstance(raw_payload, dict):
                payload = raw_payload
        except (OSError, json.JSONDecodeError):
            payload = {}

    out: Dict[str, Dict[str, Any]] = {}

    page_entries = payload.get("page_entries", []) if isinstance(payload, dict) else []
    if isinstance(page_entries, list):
        for raw in page_entries:
            if not isinstance(raw, dict):
                continue
            source_url = str(raw.get("source_url", "") or "").strip()
            if not source_url:
                continue
            out[source_url] = dict(raw)
    if out:
        return out

    # Migration path: schema v1 wrote all 39 page scan rows to the audit TSV
    # even though only unique matched product codes were retained in JSON.
    audit_path = registry_path.with_name(PRODUCT_RELEASE_REGISTRY_AUDIT_FILENAME)
    if audit_path.exists():
        try:
            with audit_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for raw in reader:
                    source_url = str(raw.get("source_url", "") or "").strip()
                    if not source_url:
                        continue
                    counts_raw = str(raw.get("product_code_counts", "") or "").strip()
                    try:
                        counts_obj = json.loads(counts_raw) if counts_raw else {}
                    except json.JSONDecodeError:
                        counts_obj = {}
                    try:
                        card_link_count = int(raw.get("card_link_count", 0) or 0)
                    except (TypeError, ValueError):
                        card_link_count = 0
                    out[source_url] = {
                        "product_code": str(raw.get("product_code", "") or "").strip().upper(),
                        "release_date": str(raw.get("release_date", "") or "").strip(),
                        "title": str(raw.get("title", "") or "").strip(),
                        "status": str(raw.get("status", "") or "").strip(),
                        "reason": "registry_audit_migration",
                        "card_link_count": card_link_count,
                        "product_code_counts": counts_obj if isinstance(counts_obj, dict) else {},
                        "sample_cardnumbers": [],
                        "source_url": source_url,
                    }
        except OSError:
            out = {}
    if out:
        return out

    products = payload.get("products", {}) if isinstance(payload, dict) else {}
    if not isinstance(products, dict):
        return {}
    for code, raw in products.items():
        if not isinstance(raw, dict):
            continue
        source_url = str(raw.get("source_url", "") or "").strip()
        if not source_url:
            continue
        out[source_url] = {
            "product_code": str(code or "").strip().upper(),
            "release_date": str(raw.get("release_date", "") or "").strip(),
            "title": str(raw.get("title", "") or "").strip(),
            "status": "MATCHED",
            "reason": "registry_reuse_legacy_products",
            "card_link_count": int(raw.get("card_link_count", 0) or 0),
            "product_code_counts": raw.get("product_code_counts", {})
            if isinstance(raw.get("product_code_counts"), dict)
            else {},
            "sample_cardnumbers": raw.get("sample_cardnumbers", [])
            if isinstance(raw.get("sample_cardnumbers"), list)
            else [],
            "source_url": source_url,
        }
    return out


def should_fetch_product_page_incremental(
    product_url: str,
    *,
    previous_entries_by_url: Dict[str, Dict[str, Any]],
    today: date,
    released_product_grace_days: int,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    old = previous_entries_by_url.get(str(product_url).strip())
    if not old:
        return True, None, "new_product"

    raw_release = str(old.get("release_date", "") or "").strip()
    if not raw_release:
        # The page has already been scanned and recorded in the page-level
        # registry. Most release-date-less pages are stable auxiliary or
        # archive-style product pages. Re-fetching them on every incremental
        # update is expensive and has repeatedly triggered WIKIWIKI 429s. Treat
        # them as registry entries with no expiry; use --fresh / --full-refresh
        # when such pages need to be audited again.
        return False, old, "release_date_unknown_reused"
    try:
        release_day = date.fromisoformat(raw_release)
    except ValueError:
        # Same policy as unknown dates: keep the last scanned row until an
        # explicit full refresh. This prevents malformed legacy dates from
        # becoming a permanent per-run HTTP fetch target.
        return False, old, "release_date_invalid_reused"

    grace_start = today - timedelta(days=max(0, int(released_product_grace_days)))
    if release_day >= grace_start:
        if release_day > today:
            return True, old, "prerelease_product"
        return True, old, "recently_released_product"

    return False, old, "stable_released_product"


def cmd_scrape(
    products_url: str,
    outdir: Path,
    cache_dir: Path,
    delay: float,
    checkpoint_every: int,
    max_fail: int,
    user_agent: str,
    limit_products: int = 0,
    limit_cards: int = 0,
    no_normalize: bool = False,
    fresh: bool = False,
    fetch_state: Optional[FetchState] = None,
    manual_overrides: Optional[Path] = None,
    released_product_grace_days: int = 7,
    field_schema: Optional[Path] = None,
    product_page_cache_ttl_days: float = 3650.0,
) -> Tuple[Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    if fetch_state is None:
        fetch_state = FetchState(
            outdir / "failed_fetches.csv",
            max_429=CONFIG["max_429"],
        )

    resume_csv = outdir / "cards_min.csv"
    resume_json = outdir / "cards_min.json"
    resume_records = [] if fresh else load_resume_records(resume_csv, resume_json)
    resume_urls = load_resume_urls_from_records(resume_records)

    records: List[Dict[str, Any]] = list(resume_records)
    keys_found: Set[str] = set()
    failed: List[str] = []

    print(
        f"[INFO] scrape mode: {'fresh' if fresh else 'resume'} "
        f"resume_records={len(resume_records)}"
    )

    try:
        prod_html = fetch(
            products_url,
            cache_dir,
            delay=delay,
            user_agent=user_agent,
            stage="products",
            fetch_state=fetch_state,
        )
        product_urls = extract_product_urls(prod_html, products_url)
        if limit_products:
            product_urls = product_urls[:limit_products]
        print(f"[INFO] product pages: {len(product_urls)}")

        # Existing card URLs are already represented by resume records. In
        # incremental mode only product pages that may reveal new cards are
        # fetched: new products, prerelease products, and recently released
        # products. Stable old released products reuse the previous registry.
        card_urls: Set[str] = set(resume_urls)
        product_registry_entries: List[Dict[str, Any]] = []
        previous_registry = (
            {}
            if fresh
            else load_existing_product_registry_entries(
                outdir / PRODUCT_RELEASE_REGISTRY_FILENAME
            )
        )
        product_fetch_count = 0
        product_reuse_count = 0
        product_long_cache_ttl_sec = max(0.0, float(product_page_cache_ttl_days)) * 86400.0
        product_fetch_reasons: Counter[str] = Counter()
        today = date.today()

        for i, pu in enumerate(product_urls, 1):
            should_fetch = True
            reused_entry: Optional[Dict[str, Any]] = None
            reason = "fresh"
            if not fresh:
                should_fetch, reused_entry, reason = (
                    should_fetch_product_page_incremental(
                        pu,
                        previous_entries_by_url=previous_registry,
                        today=today,
                        released_product_grace_days=released_product_grace_days,
                    )
                )

            if not should_fetch and reused_entry is not None:
                product_registry_entries.append(dict(reused_entry))
                product_reuse_count += 1
                product_fetch_reasons[reason] += 1
            else:
                product_fetch_count += 1
                product_fetch_reasons[reason] += 1
                try:
                    h = fetch(
                        pu,
                        cache_dir,
                        delay=delay,
                        user_agent=user_agent,
                        stage="product_page",
                        fetch_state=fetch_state,
                        cache_ttl_sec=None if fresh else product_long_cache_ttl_sec,
                    )
                    card_urls.update(extract_card_links_from_product(h))
                    product_registry_entries.append(
                        build_product_registry_entry(
                            pu,
                            h,
                            previous_entries_by_url=previous_registry,
                        )
                    )
                except FetchSafetyStop:
                    raise
                except Exception as e:
                    failed.append(pu)
                    print(f"[WARN] product fetch failed: {pu} ({e})")
                    if reused_entry is not None:
                        fallback_entry = dict(reused_entry)
                        fallback_entry["reason"] = "registry_reuse_after_fetch_error"
                        product_registry_entries.append(fallback_entry)
                    if len(failed) >= max_fail:
                        raise SystemExit("[ERROR] too many failures")

            if i % 20 == 0:
                print(f"[INFO] processed products {i}/{len(product_urls)}")

        print(
            "[PRODUCT-SCAN] "
            f"total={len(product_urls)} fetch={product_fetch_count} "
            f"reuse={product_reuse_count} "
            f"released_grace_days={max(0, int(released_product_grace_days))} "
            f"reasons={dict(sorted(product_fetch_reasons.items()))}"
        )

        write_product_release_registry(
            outdir,
            products_url=products_url,
            entries=product_registry_entries,
        )

        card_list = sorted(card_urls)
        if limit_cards:
            card_list = card_list[:limit_cards]
        print(f"[INFO] card pages: {len(card_list)}")

        todo = [u for u in card_list if u not in resume_urls]
        print(f"[INFO] to process: {len(todo)}")

        since_ck = 0
        for idx, cu in enumerate(todo, 1):
            try:
                h = fetch(
                    cu,
                    cache_dir,
                    delay=delay,
                    user_agent=user_agent,
                    stage="card_page",
                    fetch_state=fetch_state,
                )
                rec = parse_card_page(
                    cu,
                    h,
                    keys_found,
                    do_normalize=(not no_normalize),
                )
                records.append(rec)
            except FetchSafetyStop:
                raise
            except Exception as e:
                failed.append(cu)
                print(f"[WARN] card fetch failed: {cu} ({e})")
                if len(failed) >= max_fail:
                    raise SystemExit("[ERROR] too many failures")

            since_ck += 1
            if checkpoint_every and since_ck >= checkpoint_every:
                _write_scrape_checkpoint(
                    outdir,
                    records,
                    keys_found,
                    failed,
                )
                since_ck = 0
                print(
                    f"[INFO] checkpoint: records={len(records)} "
                    f"failed={len(failed)}"
                )

            if idx % 200 == 0:
                print(f"[INFO] processed cards {idx}/{len(todo)}")

    except FetchSafetyStop:
        _write_scrape_checkpoint(outdir, records, keys_found, failed)
        print(
            f"[SAFE-STOP] scrape checkpoint preserved: "
            f"records={len(records)} failed={len(failed)} outdir={outdir}"
        )
        raise

    out_csv, out_json = finalize_outputs(
        outdir, records, keys_found, failed, manual_overrides=manual_overrides, field_schema=field_schema
    )
    print("[DONE] records=", len(pd.read_csv(out_csv)))
    print("  CSV :", out_csv)
    print("  JSON:", out_json)
    return out_csv, out_json


# -------------------------
# normalize (postprocess)
# -------------------------
def safe_json_loads(s: Any) -> Tuple[bool, Any]:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return True, None
    if not isinstance(s, str):
        return False, None
    ss = s.strip()
    if ss == "":
        return True, None
    try:
        return True, json.loads(ss)
    except Exception:
        return False, None


def normalize_tag(tag: str) -> str:
    t = tag.strip()
    t = t.translate(FW_DIGITS).translate(PLUS_MINUS_MAP)
    t = re.sub(r"\s+", "", t)
    return t


def process_tokens(obj: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        obj = {}

    tags = obj.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    blade_icon_n = int(obj.get("blade_icon_n", 0) or 0)
    energy_icon_n = int(obj.get("energy_icon_n", 0) or 0)
    all_heart_n = int(obj.get("all_heart_n", 0) or 0)
    score_delta_icon = int(obj.get("score_delta_icon", 0) or 0)

    unknown: List[str] = []
    for raw in tags:
        if not isinstance(raw, str) or not raw.strip():
            continue
        t = normalize_tag(raw)

        if t in KNOWN_SIMPLE:
            key = KNOWN_SIMPLE[t]
            if key == "blade_icon_n":
                blade_icon_n += 1
            elif key == "energy_icon_n":
                energy_icon_n += 1
            elif key == "all_heart_n":
                all_heart_n += 1
            continue

        m = SCORE_TAG_RE.match(t)
        if m:
            sign = m.group(1).translate(PLUS_MINUS_MAP)
            n = int(m.group(2).translate(FW_DIGITS))
            score_delta_icon += (n if sign == "+" else -n)
            continue

        unknown.append(t)

    obj["blade_icon_n"] = blade_icon_n
    obj["energy_icon_n"] = energy_icon_n
    obj["all_heart_n"] = all_heart_n
    obj["score_delta_icon"] = score_delta_icon
    obj["unknown_tags"] = unknown
    obj["tags"] = unknown
    return obj


def cmd_normalize(csv_path: Path, json_path: Optional[Path], outdir: Path, suffix: str, manual_overrides: Optional[Path] = None, field_schema: Optional[Path] = None) -> Tuple[Path, Optional[Path]]:
    df = pd.read_csv(csv_path)
    csv_records = df.to_dict(orient="records")
    canonicalize_cardnumbers_in_records(
        csv_records,
        outdir=outdir,
        label="normalize_csv",
    )
    df = pd.DataFrame(csv_records)
    overrides = load_card_text_overrides(manual_overrides)
    df = apply_card_text_overrides_to_dataframe(df, overrides, label="normalize/csv")
    if "effect_tokens_json" not in df.columns:
        raise SystemExit("[ERROR] effect_tokens_json not found")

    new_tokens_json = []
    tok_blade, tok_energy, tok_all, tok_score_delta, tok_unknown_n = [], [], [], [], []
    blade_heart_counts_json, blade_heart_totals, blade_heart_tags_json = [], [], []
    blade_heart_special_json = []
    blade_heart_draw_n, blade_heart_score_n, blade_heart_colorless_n = [], [], []
    effect_statuses, effect_no_ability_flags = [], []
    repaired_type_norms, repaired_type_raws = [], []
    bad_json = 0

    eff_norm_series = df["effect_text_norm"].tolist() if "effect_text_norm" in df.columns else [""] * len(df)

    req_series = df["required_hearts_raw"].tolist() if "required_hearts_raw" in df.columns else [""] * len(df)
    score_series = df["score"].tolist() if "score" in df.columns else [""] * len(df)
    cost_series = df["cost"].tolist() if "cost" in df.columns else [""] * len(df)
    blade_series = df["blade"].tolist() if "blade" in df.columns else [""] * len(df)
    base_series = df["base_hearts_raw"].tolist() if "base_hearts_raw" in df.columns else [""] * len(df)
    raw_type_series = df["card_type_raw"].tolist() if "card_type_raw" in df.columns else [""] * len(df)
    blade_heart_raw_series = df["blade_heart_raw"].tolist() if "blade_heart_raw" in df.columns else [""] * len(df)

    for s, eff_norm, req_raw, score, cost, blade, base_raw, raw_type, bh_raw in zip(
        df["effect_tokens_json"].tolist(),
        eff_norm_series,
        req_series,
        score_series,
        cost_series,
        blade_series,
        base_series,
        raw_type_series,
        blade_heart_raw_series,
    ):
        ok, obj = safe_json_loads(s)
        if (not ok) or (obj is None) or (not isinstance(obj, dict)):
            bad_json += 1
            obj = {}
        obj2 = process_tokens(obj)

        tok_blade.append(int(obj2.get("blade_icon_n", 0) or 0))
        tok_energy.append(int(obj2.get("energy_icon_n", 0) or 0))
        tok_all.append(int(obj2.get("all_heart_n", 0) or 0))
        tok_score_delta.append(int(obj2.get("score_delta_icon", 0) or 0))
        unk = obj2.get("unknown_tags", [])
        tok_unknown_n.append(len(unk) if isinstance(unk, list) else 0)

        new_tokens_json.append(json.dumps(obj2, ensure_ascii=False))

        bh_counts, bh_total, bh_tags, bh_special = parse_blade_heart_expr(str(bh_raw or ""))
        blade_heart_counts_json.append(json.dumps(bh_counts, ensure_ascii=False))
        blade_heart_totals.append(int(bh_total or 0))
        blade_heart_tags_json.append(json.dumps(bh_tags, ensure_ascii=False))
        blade_heart_special_json.append(json.dumps(bh_special, ensure_ascii=False))
        blade_heart_draw_n.append(int(bh_special.get("draw", 0) or 0))
        blade_heart_score_n.append(int(bh_special.get("score", 0) or 0))
        blade_heart_colorless_n.append(int(bh_special.get("colorless", 0) or 0))

        st = classify_effect_text_status(eff_norm, eff_norm)
        effect_statuses.append(st)
        effect_no_ability_flags.append(1 if st == "NO_ABILITY" else 0)

        inferred_type, canonical_raw = infer_card_type(
            raw_type,
            required_hearts_raw=req_raw,
            score=score,
            cost=cost,
            blade=blade,
            base_hearts_raw=base_raw,
        )
        repaired_type_norms.append(inferred_type)
        repaired_type_raws.append(canonical_raw or str(raw_type or ""))

    df["effect_tokens_json"] = new_tokens_json
    df["blade_heart_counts_json"] = blade_heart_counts_json
    df["blade_heart_total"] = blade_heart_totals
    df["blade_heart_tags_json"] = blade_heart_tags_json
    df["blade_heart_special_counts_json"] = blade_heart_special_json
    df["blade_heart_draw_n"] = blade_heart_draw_n
    df["blade_heart_score_n"] = blade_heart_score_n
    df["blade_heart_colorless_n"] = blade_heart_colorless_n
    df["effect_text_status"] = effect_statuses
    df["effect_text_is_no_ability"] = effect_no_ability_flags
    df["card_type_norm"] = repaired_type_norms
    df["card_type_raw"] = repaired_type_raws
    df["tok_blade_icon_n"] = tok_blade
    df["tok_energy_icon_n"] = tok_energy
    df["tok_all_heart_n"] = tok_all
    df["tok_score_delta_icon"] = tok_score_delta
    df["tok_unknown_tags_n"] = tok_unknown_n

    csv_out_records = df.to_dict(orient="records")
    apply_field_schema_to_records(csv_out_records, outdir=outdir, label="normalize_csv", schema_path=field_schema)
    df = pd.DataFrame(csv_out_records)

    outdir.mkdir(parents=True, exist_ok=True)
    out_csv = outdir / f"{csv_path.stem}{suffix}.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"[DONE] wrote: {out_csv} (bad_json={bad_json})")

    out_json = None
    if json_path and json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                canonicalize_cardnumbers_in_records(
                    data,
                    outdir=outdir,
                    label="normalize_json",
                )
                apply_card_text_overrides_to_records(data, overrides, label="normalize/json")
                for r in data:
                    if not isinstance(r, dict):
                        continue
                    ok, obj = safe_json_loads(r.get("effect_tokens_json", ""))
                    if (not ok) or (obj is None) or (not isinstance(obj, dict)):
                        obj = {}
                    r["effect_tokens_json"] = json.dumps(process_tokens(obj), ensure_ascii=False)
                    bh_counts, bh_total, bh_tags, bh_special = parse_blade_heart_expr(str(r.get("blade_heart_raw", "") or ""))
                    r["blade_heart_counts_json"] = json.dumps(bh_counts, ensure_ascii=False)
                    r["blade_heart_total"] = int(bh_total or 0)
                    r["blade_heart_tags_json"] = json.dumps(bh_tags, ensure_ascii=False)
                    r["blade_heart_special_counts_json"] = json.dumps(bh_special, ensure_ascii=False)
                    r["blade_heart_draw_n"] = int(bh_special.get("draw", 0) or 0)
                    r["blade_heart_score_n"] = int(bh_special.get("score", 0) or 0)
                    r["blade_heart_colorless_n"] = int(bh_special.get("colorless", 0) or 0)
                    inferred_type, canonical_raw = infer_card_type(
                        r.get("card_type_raw", ""),
                        required_hearts_raw=r.get("required_hearts_raw", ""),
                        score=r.get("score", ""),
                        cost=r.get("cost", ""),
                        blade=r.get("blade", ""),
                        base_hearts_raw=r.get("base_hearts_raw", ""),
                    )
                    r["card_type_norm"] = inferred_type
                    r["card_type_raw"] = canonical_raw or str(r.get("card_type_raw", "") or "")
                apply_field_schema_to_records(data, outdir=outdir, label="normalize_json", schema_path=field_schema)
                out_json = outdir / f"{json_path.stem}{suffix}.json"
                out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[DONE] wrote: {out_json}")
        except Exception as e:
            print(f"[WARN] failed to update json: {e}")

    _auto_audit_db_generation_if_applicable(
        outdir,
        label="post_normalize",
    )
    return out_csv, out_json


# -------------------------
# mine templates
# -------------------------
def canonicalize_effect(s: str) -> str:
    if not isinstance(s, str) or not s.strip():
        return ""
    t = s.strip()
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n+", "\n", t)
    t = re.sub(r"<\(([^)]+)\)>\s*(\d+)", r"<(\1)>{n}", t)
    t = re.sub(r"(?<![<{])\b\d+\b", "{n}", t)
    t = re.sub(r"(\D)\d+(\D)", lambda m: f"{m.group(1)}{{n}}{m.group(2)}", t)
    t = t.replace("{n}{n}", "{n}")
    t = t.replace("＋", "+").replace("－", "-")
    return t


def split_trigger_blocks(effect_text_norm: str) -> List[Dict[str, Any]]:
    """
    Robust two-level parsing for abilities.

    Output blocks:
      - ability_type: 自動 / 起動 / 常時 (or UNKNOWN)
      - trigger: 自動の下位カテゴリ（登場時/ライブ開始時/ライブ成功時/…）または "BODY"
      - conditions: センター/ライト/レフト/ターンn回 等の条件ヘッダ（triggerではない）
      - text: ブロック本文

    Key rule (your spec):
      効果カテゴリには「起動」「常時」「自動」「登場時」「ライブ開始時」「ライブ成功時」があり、
      「登場時/ライブ開始時/ライブ成功時」はすべて「自動」に包含される（短縮記法）。
      したがって、イベント系カテゴリ（登場時/ライブ開始時/ライブ成功時/～時）を見たら
      そのブロックは必ず ability_type="自動" として開始する（直前が起動/常時でも上書き）。

    Supported header forms when a line is *only* the header:
      <...> / ＜...＞ / 〈...〉 / 《...》 / 【...】 / [...] / （...）
    """
    if not isinstance(effect_text_norm, str) or not effect_text_norm.strip():
        return []

    # normalize common bracket variants to simplify detection
    t = effect_text_norm
    t = t.replace("＜", "<").replace("＞", ">")
    t = t.replace("〈", "<").replace("〉", ">")
    t = t.replace("《", "<").replace("》", ">")
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]

    ability_headers = {"自動", "起動", "常時"}

    # auto sub-triggers (shorthand categories)
    auto_triggers = {
        "登場時", "登場した時", "登場",
        "ライブ開始時", "ライブ成功時", "ライブ終了時", "ライブ中",
        "ターン開始時", "ターン終了時",
        "アタック時", "アタックした時",
    }

    known_conditions = {"センター", "ライト", "レフト"}
    turn_n_re = re.compile(r"^ターン\s*[0-9０-９]+\s*回$")

    # heuristic for trigger headers
    eventish_re = re.compile(r"(開始時|成功時|終了時|した時|時$)")

    def classify_header(h: str) -> Tuple[str, str]:
        h = h.strip()
        # ability
        if h in ability_headers:
            return ("ability", h)
        if h.startswith("自動"):
            return ("ability", "自動")
        if h.startswith("起動"):
            return ("ability", "起動")
        if h.startswith("常時"):
            return ("ability", "常時")

        # conditions
        if h in known_conditions or turn_n_re.match(h):
            return ("condition", h)

        # triggers (auto shorthand)
        if h in auto_triggers:
            return ("trigger", h)
        if eventish_re.search(h):
            return ("trigger", h)

        return ("condition", h)

    # header line matchers
    header_angle = re.compile(r"^<([^<>]+)>$")
    header_kakko = re.compile(r"^[\[\【\（]([^\]\】\）]+)[\]\】\）]$")
    header_ascii_paren = re.compile(r"^\(([^()]+)\)$")

    def is_known_structural_header(h: str) -> bool:
        h = h.strip()
        return (
            h in ability_headers
            or h.startswith("自動")
            or h.startswith("起動")
            or h.startswith("常時")
            or h in auto_triggers
            or bool(eventish_re.search(h))
            or h in known_conditions
            or bool(turn_n_re.match(h))
        )

    def parse_header_line(ln: str) -> Optional[str]:
        m = header_angle.match(ln)
        if m and not ln.startswith("<("):  # exclude icons like <(桃)>
            return m.group(1).strip()
        m = header_kakko.match(ln)
        if m:
            return m.group(1).strip()
        # New WIKIWIKI rows can expose effect headers as ASCII-parenthesized
        # tokens, e.g. (ライブ開始時) / (自動) / (ターン1回).  Accept only
        # known structural headers so ordinary parenthetical prose is not
        # misclassified as an ability header.
        m = header_ascii_paren.match(ln)
        if m:
            h = m.group(1).strip()
            if is_known_structural_header(h):
                return h
        return None

    blocks: List[Dict[str, Any]] = []
    cur_ability = "UNKNOWN"
    cur_trigger = "BODY"
    cur_conditions: List[str] = []
    cur_lines: List[str] = []

    def flush():
        nonlocal cur_lines
        if cur_lines:
            inferred = cur_ability
            if inferred == "UNKNOWN" and cur_trigger != "BODY":
                inferred = "自動"
            blocks.append({
                "ability_type": inferred,
                "trigger": cur_trigger,
                "conditions": list(cur_conditions),
                "text": "\n".join(cur_lines).strip(),
            })
        cur_lines = []

    for ln in lines:
        h = parse_header_line(ln)
        if h is not None:
            kind, val = classify_header(h)

            if kind == "ability":
                flush()
                cur_ability = val
                cur_trigger = "BODY"
                cur_conditions = []
                continue

            if kind == "trigger":
                flush()
                # IMPORTANT: triggerカテゴリは自動の短縮記法なので必ず自動にする
                cur_ability = "自動"
                cur_trigger = val
                cur_conditions = []
                continue

            # condition
            flush()
            cur_conditions.append(val)
            continue

        cur_lines.append(ln)

    flush()
    return blocks


def split_cost_effect_clauses(block_text: str) -> List[Dict[str, Any]]:
    """
    Split block text into clauses. A clause may contain cost/effect split by '：' or ':'.

    Why a cost sentence may be split into two:
      The wiki often inserts <br> inside one sentence (visual wrap),
      so our line-based splitter treated it as two separate clauses.

    Fix:
      We do a "soft-wrap merge" pass:
        - If a line does NOT contain a separator and
        - The previous line looks unfinished (ends with particles like 'から','を','に','へ','の','と','して' etc.),
          then we concatenate them.

    Also trims leading punctuation artifacts on clause texts.
    """
    if not isinstance(block_text, str) or not block_text.strip():
        return []

    raw_lines = [ln.strip() for ln in block_text.splitlines() if ln.strip()]

    def clean_leading_punct(s: str) -> str:
        if not s:
            return s
        return s.lstrip("、。,.，・ ")

    merge_tail = ("から", "を", "に", "へ", "の", "と", "して", "または", "および", "及び")
    merged: List[str] = []
    for ln in raw_lines:
        if not merged:
            merged.append(ln)
            continue
        prev = merged[-1]
        has_sep_prev = ("：" in prev) or (":" in prev)
        has_sep_ln = ("：" in ln) or (":" in ln)
        if (not has_sep_prev) and (not has_sep_ln) and any(prev.endswith(t) for t in merge_tail) and not ln.startswith("<"):
            merged[-1] = prev + ln
        else:
            merged.append(ln)

    clauses: List[Dict[str, Any]] = []
    for ln in merged:
        sep = "：" if "：" in ln else (":" if ":" in ln else None)
        if sep:
            left, right = ln.split(sep, 1)
            left = left.strip()
            right = right.strip()
            optional = ("してもよい" in left) or ("してもよい" in ln)
            clauses.append({
                "optional": optional,
                "cost_text": clean_leading_punct(left),
                "effect_text": clean_leading_punct(right),
                "raw": ln,
            })
        else:
            clauses.append({
                "optional": ("してもよい" in ln),
                "cost_text": "",
                "effect_text": clean_leading_punct(ln),
                "raw": ln,
            })
    return clauses


# --- filter extraction: group/unit/work/card_kind/cost constraints ---
GROUP_ALIASES = {
    "Aqours": "Aqours",
    "μ's": "Muse",
    "μｓ": "Muse",
    "ミューズ": "Muse",
    "Liella!": "Liella",
    "Liella": "Liella",
    "虹ヶ咲": "Nijigasaki",
    "虹ヶ咲学園": "Nijigasaki",
    "蓮ノ空": "Hasunosora",
    "蓮ノ空女学院": "Hasunosora",
}

UNIT_ALIASES = {
    # Aqours
    "CYaRon!": "CYaRon",
    "AZALEA": "AZALEA",
    "Guilty Kiss": "GuiltyKiss",
    # μ's
    "Printemps": "Printemps",
    "lily white": "lilywhite",
    "BiBi": "BiBi",
    # Liella!
    "CatChu!": "CatChu",
    "KALEIDOSCORE": "KALEIDOSCORE",
    "5yncri5e!": "5yncri5e",
}

CARD_KIND_ALIASES = {
    "ライブカード": "LIVE",
    "ライブ": "LIVE",
    "メンバーカード": "MEMBER",
    "メンバー": "MEMBER",
    "イベントカード": "EVENT",
    "イベント": "EVENT",
    "サポートカード": "SUPPORT",
    "サポート": "SUPPORT",
}

COST_LE_RE = re.compile(r"コスト\s*([0-9]+)\s*以下")
COST_GE_RE = re.compile(r"コスト\s*([0-9]+)\s*以上")

def extract_filters(text: str) -> Dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return {}
    f: Dict[str, Any] = {}

    groups = set()
    for k, v in GROUP_ALIASES.items():
        if k in text:
            groups.add(v)
    if groups:
        f["group"] = sorted(groups)

    units = set()
    for k, v in UNIT_ALIASES.items():
        if k in text:
            units.add(v)
    m = re.search(r"ユニット\s*「([^」]+)」", text)
    if m:
        units.add(m.group(1).strip())
    if units:
        f["unit"] = sorted(units)

    kinds = set()
    for k, v in CARD_KIND_ALIASES.items():
        if k in text:
            kinds.add(v)
    if kinds:
        f["card_kind"] = sorted(kinds)

    m = COST_LE_RE.search(text)
    if m:
        f["cost_le"] = int(m.group(1))
    m = COST_GE_RE.search(text)
    if m:
        f["cost_ge"] = int(m.group(1))

    return f


def cmd_mine(csv_path: Path, outdir: Path, top: int = 150) -> Dict[str, Path]:
    """
    Mine:
      - trigger frequency
      - cost clause templates
      - effect clause templates
    Also generates stub YAML for cost/effect clauses.
    """
    df = pd.read_csv(csv_path)
    if "effect_text_norm" not in df.columns:
        raise SystemExit("[ERROR] effect_text_norm not found")

    outdir.mkdir(parents=True, exist_ok=True)

    trigger_rows = []
    cost_rows = []
    eff_rows = []

    for _, r in df.iterrows():
        cardno = str(r.get("cardnumber", "") or "")
        name = str(r.get("cardname", "") or "")
        ctype = str(r.get("card_type_norm", "") or "")
        url = str(r.get("source_url", "") or "")
        et = r.get("effect_text_norm", "")
        blocks = split_trigger_blocks(et)
        for b in blocks:
            ability = b.get("ability_type","UNKNOWN")
            trig = b.get("trigger","BODY")
            conds = b.get("conditions", []) or []
            conds_s = ";".join([c for c in conds if isinstance(c,str) and c.strip()])
            txt = b["text"]
            trigger_rows.append({"ability_type": ability, "ability_type": ability,
                        "trigger": trig,
                        "conditions": conds_s, "cardnumber": cardno, "cardname": name, "card_type": ctype, "source_url": url})

            clauses = split_cost_effect_clauses(txt)
            for cl in clauses:
                optional = bool(cl.get("optional", False))
                cost_text = str(cl.get("cost_text", "") or "")
                eff_text = str(cl.get("effect_text", "") or "")

                cost_tmpl = canonicalize_effect(cost_text) if cost_text else ""
                eff_tmpl = canonicalize_effect(eff_text) if eff_text else ""

                filters = extract_filters(cost_text + " " + eff_text)
                g = ",".join(filters.get("group", [])) if isinstance(filters.get("group"), list) else ""
                u = ",".join(filters.get("unit", [])) if isinstance(filters.get("unit"), list) else ""
                k = ",".join(filters.get("card_kind", [])) if isinstance(filters.get("card_kind"), list) else ""
                cost_le = filters.get("cost_le", "")
                cost_ge = filters.get("cost_ge", "")

                if cost_tmpl:
                    cost_rows.append({
                        "ability_type": ability,
                        "trigger": trig,
                        "conditions": conds_s,
                        "optional": optional,
                        "cost_template": cost_tmpl,
                        "count": 1,
                        "example_cardnumber": cardno,
                        "example_cardname": name,
                        "example_card_type": ctype,
                        "example_cost_text": cost_text,
                        "filters_group": g,
                        "filters_unit": u,
                        "filters_card_kind": k,
                        "filters_cost_le": cost_le,
                        "filters_cost_ge": cost_ge,
                        "example_source_url": url,
                    })

                if eff_tmpl:
                    eff_rows.append({
                        "ability_type": ability,
                        "trigger": trig,
                        "conditions": conds_s,
                        "optional": optional,
                        "effect_template": eff_tmpl,
                        "count": 1,
                        "example_cardnumber": cardno,
                        "example_cardname": name,
                        "example_card_type": ctype,
                        "example_effect_text": eff_text,
                        "filters_group": g,
                        "filters_unit": u,
                        "filters_card_kind": k,
                        "filters_cost_le": cost_le,
                        "filters_cost_ge": cost_ge,
                        "example_source_url": url,
                    })

    trig_df = pd.DataFrame(trigger_rows)
    if len(trig_df):
        trig_counts = trig_df.groupby(["ability_type", "trigger"], dropna=False).size().reset_index(name="count")
        trig_counts = trig_counts.sort_values("count", ascending=False)
    else:
        trig_counts = pd.DataFrame(columns=["ability_type","trigger","count"])
    trig_out = trig_counts.head(top)
    trig_csv = outdir / f"trigger_top{top}.csv"
    trig_out.to_csv(trig_csv, index=False, encoding="utf-8-sig")

    if cost_rows:
        cdf = pd.DataFrame(cost_rows)
        gcols = ["ability_type", "trigger", "conditions", "optional", "cost_template", "filters_group", "filters_unit", "filters_card_kind", "filters_cost_le", "filters_cost_ge"]
        agg = cdf.groupby(gcols, dropna=False).agg(
            count=("count", "sum"),
            example_cardnumber=("example_cardnumber", "first"),
            example_cardname=("example_cardname", "first"),
            example_card_type=("example_card_type", "first"),
            example_cost_text=("example_cost_text", "first"),
            example_source_url=("example_source_url", "first"),
        ).reset_index()
        agg = agg.sort_values("count", ascending=False).head(top)
        cost_csv = outdir / f"cost_clause_template_top{top}.csv"
        agg.to_csv(cost_csv, index=False, encoding="utf-8-sig")
    else:
        cost_csv = outdir / f"cost_clause_template_top{top}.csv"
        pd.DataFrame([]).to_csv(cost_csv, index=False, encoding="utf-8-sig")

    if eff_rows:
        edf = pd.DataFrame(eff_rows)
        gcols = ["ability_type", "trigger", "conditions", "optional", "effect_template", "filters_group", "filters_unit", "filters_card_kind", "filters_cost_le", "filters_cost_ge"]
        agg = edf.groupby(gcols, dropna=False).agg(
            count=("count", "sum"),
            example_cardnumber=("example_cardnumber", "first"),
            example_cardname=("example_cardname", "first"),
            example_card_type=("example_card_type", "first"),
            example_effect_text=("example_effect_text", "first"),
            example_source_url=("example_source_url", "first"),
        ).reset_index()
        agg = agg.sort_values("count", ascending=False).head(top)
        eff_csv = outdir / f"effect_clause_template_top{top}.csv"
        agg.to_csv(eff_csv, index=False, encoding="utf-8-sig")
    else:
        eff_csv = outdir / f"effect_clause_template_top{top}.csv"
        pd.DataFrame([]).to_csv(eff_csv, index=False, encoding="utf-8-sig")

    def write_stub(kind: str, df_top: pd.DataFrame, template_col: str, example_col: str) -> Path:
        stub = []
        stub.append(f"# {kind}_patterns_stub.yaml")
        stub.append("# Auto-generated. Fill `action` and `params` for each template.")
        stub.append("version: 1")
        stub.append("patterns:")
        for i, row in df_top.reset_index(drop=True).iterrows():
            tmpl = str(row[template_col])
            cnt = int(row["count"])
            ability = str(row.get("ability_type","UNKNOWN"))
            trig = str(row.get("trigger",""))
            conds = str(row.get("conditions",""))
            opt = bool(row.get("optional", False))
            ex = str(row.get(example_col, "") or "")
            stub.append(f"  - id: {kind[:1].upper()}{i+1:03d}")
            stub.append(f"    count: {cnt}")
            stub.append(f"    ability_type: {json.dumps(ability, ensure_ascii=False)}")
            stub.append(f"    trigger: {json.dumps(trig, ensure_ascii=False)}")
            stub.append(f"    conditions: {json.dumps(conds, ensure_ascii=False)}")
            stub.append(f"    optional: {str(opt).lower()}")
            stub.append(f"    template: {json.dumps(tmpl, ensure_ascii=False)}")
            stub.append(f"    example: {json.dumps(ex, ensure_ascii=False)}")
            for fk in ["filters_group", "filters_unit", "filters_card_kind", "filters_cost_le", "filters_cost_ge"]:
                val = row.get(fk, "")
                if isinstance(val, float) and pd.isna(val):
                    val = ""
                stub.append(f"    {fk}: {json.dumps(str(val), ensure_ascii=False)}")
            stub.append("    action: TODO")
            stub.append("    params: {}")
            stub.append("")
        p = outdir / f"{kind}_patterns_stub.yaml"
        p.write_text("\n".join(stub), encoding="utf-8")
        return p

    try:
        cost_top = pd.read_csv(cost_csv) if cost_csv.exists() else pd.DataFrame([])
    except pd.errors.EmptyDataError:
        cost_top = pd.DataFrame([])
    try:
        eff_top = pd.read_csv(eff_csv) if eff_csv.exists() else pd.DataFrame([])
    except pd.errors.EmptyDataError:
        eff_top = pd.DataFrame([])

    cost_stub = write_stub("cost", cost_top, "cost_template", "example_cost_text") if len(cost_top) else (outdir / "cost_patterns_stub.yaml")
    if not len(cost_top):
        cost_stub.write_text("version: 1\npatterns: []\n", encoding="utf-8")

    eff_stub = write_stub("effect", eff_top, "effect_template", "example_effect_text") if len(eff_top) else (outdir / "effect_patterns_stub.yaml")
    if not len(eff_top):
        eff_stub.write_text("version: 1\npatterns: []\n", encoding="utf-8")

    print(f"[DONE] triggers -> {trig_csv}")
    print(f"[DONE] cost clauses -> {cost_csv}")
    print(f"[DONE] effect clauses -> {eff_csv}")
    print(f"[DONE] stubs -> {cost_stub} , {eff_stub}")

    return {
        "trigger_csv": trig_csv,
        "cost_csv": cost_csv,
        "effect_csv": eff_csv,
        "cost_stub": cost_stub,
        "effect_stub": eff_stub,
    }


# -------------------------
# DB generation consistency audit
# -------------------------
CANONICAL_DB_FILENAMES = (
    "cards_min.csv",
    "cards_min.json",
    "cards_min_tokv1.csv",
    "cards_min_tokv1.json",
    "cards_compiled_v7h.json",
)


def _load_db_cardnumber_set(path: Path) -> Tuple[Set[str], int]:
    """Load raw cardnumber values from CSV/JSON without canonicalizing them."""
    rows: List[Dict[str, Any]] = []

    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = [dict(r) for r in csv.DictReader(f)]
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            rows = [r for r in data if isinstance(r, dict)]
        elif isinstance(data, dict) and isinstance(data.get("cards"), list):
            rows = [r for r in data["cards"] if isinstance(r, dict)]
        elif isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(value, dict):
                    continue
                row = dict(value)
                row.setdefault("cardnumber", key)
                rows.append(row)

    cardnumbers = {
        str(r.get("cardnumber", "")).strip()
        for r in rows
        if str(r.get("cardnumber", "")).strip()
    }
    return cardnumbers, len(rows)


def audit_db_generation_consistency(
    dbdir: Path,
    *,
    strict: bool = False,
    label: str = "db_generation",
) -> Dict[str, Any]:
    """Compare cardnumber sets across the canonical five DB artifacts.

    The report intentionally compares raw cardnumber values.  A stale rarity
    suffix or a partial-generation file must remain visible instead of being
    hidden by canonicalization.
    """
    dbdir = Path(dbdir)
    report_json = dbdir / "db_generation_consistency_audit.json"
    report_tsv = dbdir / "db_generation_consistency_audit.tsv"

    loaded: Dict[str, Set[str]] = {}
    row_counts: Dict[str, int] = {}
    errors: Dict[str, str] = {}

    for filename in CANONICAL_DB_FILENAMES:
        path = dbdir / filename
        if not path.exists():
            errors[filename] = "MISSING"
            continue
        try:
            cardnumbers, row_count = _load_db_cardnumber_set(path)
            loaded[filename] = cardnumbers
            row_counts[filename] = row_count
        except Exception as exc:
            errors[filename] = f"READ_ERROR: {type(exc).__name__}: {exc}"

    union_set: Set[str] = set()
    for cardnumbers in loaded.values():
        union_set.update(cardnumbers)

    if loaded:
        intersection_set = set.intersection(*(set(s) for s in loaded.values()))
    else:
        intersection_set = set()

    all_present = len(loaded) == len(CANONICAL_DB_FILENAMES) and not errors
    sets_equal = bool(loaded) and all(s == next(iter(loaded.values())) for s in loaded.values())
    passed = all_present and sets_equal

    rows: List[Dict[str, Any]] = []
    for filename in CANONICAL_DB_FILENAMES:
        cardnumbers = loaded.get(filename, set())
        missing = sorted(union_set - cardnumbers) if filename in loaded else sorted(union_set)
        non_common = sorted(cardnumbers - intersection_set) if filename in loaded else []
        rows.append({
            "filename": filename,
            "status": "OK" if filename in loaded else errors.get(filename, "MISSING"),
            "row_count": row_counts.get(filename, 0),
            "unique_cardnumber_count": len(cardnumbers),
            "missing_from_union_count": len(missing),
            "non_common_cardnumber_count": len(non_common),
            "missing_from_union_sample": missing[:20],
            "non_common_cardnumber_sample": non_common[:20],
        })

    report = {
        "label": label,
        "dbdir": str(dbdir),
        "build_tag": BUILD_TAG,
        "passed": passed,
        "all_present": all_present,
        "sets_equal": sets_equal,
        "union_unique_cardnumber_count": len(union_set),
        "intersection_unique_cardnumber_count": len(intersection_set),
        "errors": errors,
        "files": rows,
    }

    dbdir.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "filename",
        "status",
        "row_count",
        "unique_cardnumber_count",
        "missing_from_union_count",
        "non_common_cardnumber_count",
        "missing_from_union_sample",
        "non_common_cardnumber_sample",
    ]
    with report_tsv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in rows:
            tsv_row = dict(row)
            tsv_row["missing_from_union_sample"] = json.dumps(row["missing_from_union_sample"], ensure_ascii=False)
            tsv_row["non_common_cardnumber_sample"] = json.dumps(row["non_common_cardnumber_sample"], ensure_ascii=False)
            writer.writerow(tsv_row)

    status = "PASS" if passed else "WARN"
    print(
        f"[DBGEN][{status}] files={len(loaded)}/{len(CANONICAL_DB_FILENAMES)} "
        f"union={len(union_set)} intersection={len(intersection_set)} "
        f"sets_equal={sets_equal} ({label})"
    )
    for row in rows:
        if row["status"] != "OK" or row["missing_from_union_count"] or row["non_common_cardnumber_count"]:
            print(
                f"  {row['filename']}: status={row['status']} "
                f"unique={row['unique_cardnumber_count']} "
                f"missing_from_union={row['missing_from_union_count']} "
                f"non_common={row['non_common_cardnumber_count']}"
            )
    print(f"[DBGEN] report -> {report_tsv}")

    if strict and not passed:
        raise SystemExit(2)
    return report


def _auto_audit_db_generation_if_applicable(outdir: Path, *, label: str) -> None:
    """Run a non-strict generation audit in canonical DB directories.

    We trigger when the compiled DB already exists.  This catches the dangerous
    mixed-generation case where normalize is writing into a live DB directory,
    while avoiding false alarms in isolated normalization/recovery directories
    that have not reached the compile step yet.
    """
    if (outdir / "cards_compiled_v7h.json").exists():
        audit_db_generation_consistency(outdir, strict=False, label=label)


# -------------------------
# audit
# -------------------------
def cmd_audit(csv_path: Path, top_unknown: int = 30) -> None:
    df = pd.read_csv(csv_path)
    print("[SUMMARY]")
    print(f"  rows: {len(df)}")
    if "cardnumber" in df.columns:
        print(f"  unique cardnumber: {df['cardnumber'].nunique(dropna=True)}")

    print("\n[MISSING RATE]")
    for col in ["card_type_norm", "cost", "score", "blade", "effect_text_norm", "base_hearts_raw", "required_hearts_raw"]:
        if col in df.columns:
            na = float(df[col].isna().mean())
            empty = float((df[col].astype(str).str.strip() == "").mean())
            print(f"  {col:20s}  na={na:.3f} empty={empty:.3f}")

    if "cardnumber" in df.columns:
        bad = df["cardnumber"].fillna("").astype(str).apply(lambda x: (x.strip() != "" and not AUDIT_CARDNO_RE.match(x.strip())))
        n_bad = int(bad.sum())
        suffix_candidates = []
        for x in df["cardnumber"].fillna("").astype(str).tolist():
            canonical_cn, rarity = split_cardnumber_rarity_suffix(x)
            if rarity:
                suffix_candidates.append((x.strip(), canonical_cn, rarity))
        print("\n[CARDNUMBER FORMAT]")
        print(f"  bad format count: {n_bad}")
        print(f"  known rarity-suffix candidates: {len(suffix_candidates)}")
        for source_cn, canonical_cn, rarity in suffix_candidates[:10]:
            print(f"    {source_cn} -> {canonical_cn} (rarity={rarity})")

    if "effect_text_status" in df.columns:
        print("\n[EFFECT TEXT STATUS]")
        vc = df["effect_text_status"].fillna("").astype(str).value_counts(dropna=False)
        for k, v in vc.items():
            print(f"  {k or '(blank)':20s} {int(v)}")
    elif "effect_text_norm" in df.columns:
        print("\n[EFFECT TEXT STATUS]")
        vc = df["effect_text_norm"].fillna("").astype(str).map(lambda s: classify_effect_text_status(s, s)).value_counts(dropna=False)
        for k, v in vc.items():
            print(f"  {k or '(blank)':20s} {int(v)}")

    # effect-token audit
    #
    # effect_tokens_json is primarily an icon/token stream. Ability/trigger/condition
    # headers such as (自動), (ライブ開始時), and (ターン1回) are parsed by
    # split_trigger_blocks() from effect_text_norm. Older audits mislabeled those
    # structural headers as generic "UNKNOWN TOKENS". Keep the DB payload unchanged
    # for compatibility, but separate structural headers from genuine unknown tokens.
    structural_header_names = {
        "自動", "起動", "常時",
        "登場", "登場時", "登場した時",
        "ライブ開始時", "ライブ成功時", "ライブ終了時", "ライブ中",
        "ターン開始時", "ターン終了時",
        "アタック時", "アタックした時",
        "センター", "ライト", "レフト", "左サイド", "右サイド",
    }
    structural_turn_re = re.compile(r"^ターン[0-9]+回$")
    structural_eventish_re = re.compile(r"(開始時|成功時|終了時|した時|時$)")

    def is_structural_effect_header_token(token: str) -> bool:
        t = normalize_tag(token)
        if len(t) >= 2 and t[0] == "(" and t[-1] == ")":
            bare = t[1:-1]
        else:
            bare = t
        return (
            bare in structural_header_names
            or bool(structural_turn_re.match(bare))
            or bool(structural_eventish_re.search(bare))
        )

    if "effect_tokens_json" in df.columns:
        structural = Counter()
        genuine_unknown = Counter()
        genuine_unknown_rows: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            ok, obj = safe_json_loads(row.get("effect_tokens_json", ""))
            if not ok or not isinstance(obj, dict):
                continue
            tags = obj.get("unknown_tags", obj.get("tags", []))
            if not isinstance(tags, list):
                continue
            for t in tags:
                if not isinstance(t, str) or not t:
                    continue
                if is_structural_effect_header_token(t):
                    structural[t] += 1
                else:
                    genuine_unknown[t] += 1
                    genuine_unknown_rows.append({
                        "cardnumber": str(row.get("cardnumber", "") or ""),
                        "cardname": str(row.get("cardname", "") or ""),
                        "token": t,
                        "effect_text_norm": str(row.get("effect_text_norm", "") or ""),
                    })

        print("\n[STRUCTURAL EFFECT HEADERS in effect_tokens_json]")
        if structural:
            for k, v in structural.most_common(top_unknown):
                print(f"  {k:20s} {v}")
        else:
            print("  (none)")

        print("\n[GENUINE UNKNOWN TOKENS in effect_tokens_json]")
        if genuine_unknown:
            for k, v in genuine_unknown.most_common(top_unknown):
                print(f"  {k:20s} {v}")
        else:
            print("  (none)")

        genuine_unknown_path = csv_path.parent / "effect_token_genuine_unknown_audit.tsv"
        pd.DataFrame(
            genuine_unknown_rows,
            columns=["cardnumber", "cardname", "token", "effect_text_norm"],
        ).to_csv(genuine_unknown_path, index=False, encoding="utf-8-sig", sep="\t")
        print(f"  report: {genuine_unknown_path}")

    # Audit the actual effect-text grammar separately from icon/token recognition.
    # This is the relevant check for new/pre-release card wording.
    if "effect_text_norm" in df.columns:
        source_placeholder_rows: List[Dict[str, Any]] = []
        grammar_unknown_rows: List[Dict[str, Any]] = []
        source_placeholders = {"(不明)", "(未判明)", "(未公開)"}

        for _, row in df.iterrows():
            effect_text = str(row.get("effect_text_norm", "") or "").strip()
            status = str(row.get("effect_text_status", "") or "").strip()
            if not effect_text or status == "NO_ABILITY" or effect_text in NO_ABILITY_MARKERS:
                continue

            if effect_text in source_placeholders:
                source_placeholder_rows.append({
                    "cardnumber": str(row.get("cardnumber", "") or ""),
                    "cardname": str(row.get("cardname", "") or ""),
                    "effect_text_norm": effect_text,
                })
                continue

            blocks = split_trigger_blocks(effect_text)
            if not blocks:
                grammar_unknown_rows.append({
                    "cardnumber": str(row.get("cardnumber", "") or ""),
                    "cardname": str(row.get("cardname", "") or ""),
                    "issue": "NO_TRIGGER_BLOCKS",
                    "trigger": "",
                    "conditions": "",
                    "effect_text_norm": effect_text,
                })
                continue

            for block in blocks:
                if str(block.get("ability_type", "") or "") != "UNKNOWN":
                    continue
                grammar_unknown_rows.append({
                    "cardnumber": str(row.get("cardnumber", "") or ""),
                    "cardname": str(row.get("cardname", "") or ""),
                    "issue": "UNKNOWN_ABILITY_TYPE",
                    "trigger": str(block.get("trigger", "") or ""),
                    "conditions": ";".join(
                        str(x) for x in (block.get("conditions", []) or [])
                        if str(x).strip()
                    ),
                    "effect_text_norm": effect_text,
                })

        grammar_unknown_path = csv_path.parent / "effect_grammar_unknown_audit.tsv"
        placeholder_path = csv_path.parent / "effect_source_placeholder_audit.tsv"
        pd.DataFrame(
            grammar_unknown_rows,
            columns=[
                "cardnumber", "cardname", "issue", "trigger",
                "conditions", "effect_text_norm",
            ],
        ).drop_duplicates().to_csv(
            grammar_unknown_path, index=False, encoding="utf-8-sig", sep="\t"
        )
        pd.DataFrame(
            source_placeholder_rows,
            columns=["cardnumber", "cardname", "effect_text_norm"],
        ).drop_duplicates().to_csv(
            placeholder_path, index=False, encoding="utf-8-sig", sep="\t"
        )

        print("\n[EFFECT GRAMMAR AUDIT]")
        print(f"  source_placeholder_rows: {len(source_placeholder_rows)}")
        print(f"  grammar_unknown_rows: {len(grammar_unknown_rows)}")
        print(f"  unknown_report: {grammar_unknown_path}")
        print(f"  placeholder_report: {placeholder_path}")

    for col in ["tok_energy_icon_n", "tok_all_heart_n", "tok_blade_icon_n", "tok_score_delta_icon"]:
        if col in df.columns:
            print(f"\n[{col}] sum={int(df[col].fillna(0).sum())}")

    for col in ["blade_heart_draw_n", "blade_heart_score_n", "blade_heart_colorless_n"]:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce").fillna(0)
            print(f"\n[{col}] rows_nonzero={int((vals > 0).sum())} sum={int(vals.sum())}")

    print("\n[DONE]")


# -------------------------
# CLI
# -------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llocg_db_tool_v7.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("scrape")
    ps.add_argument("--products-url", default=CONFIG["products_url"])
    ps.add_argument("--outdir", default=CONFIG["outdir"])
    ps.add_argument("--cache", default=CONFIG["cache"])
    ps.add_argument("--delay", type=float, default=CONFIG["delay"])
    ps.add_argument("--cache-ttl-sec", type=float, default=CONFIG["cache_ttl_sec"])
    ps.add_argument("--checkpoint-every", type=int, default=CONFIG["checkpoint_every"])
    ps.add_argument("--max-fail", type=int, default=CONFIG["max_fail"])
    ps.add_argument(
        "--max-429",
        type=int,
        default=CONFIG["max_429"],
        help="maximum consecutive HTTP 429 responses before safe stop",
    )
    ps.add_argument("--user-agent", default=CONFIG["user_agent"])
    ps.add_argument("--limit-products", type=int, default=0)
    ps.add_argument("--limit-cards", type=int, default=0)
    ps.add_argument("--no-normalize", action="store_true")
    ps.add_argument(
        "--fresh",
        action="store_true",
        help="ignore existing cards_min.csv/json and rebuild from fetched pages",
    )
    ps.add_argument("--manual-overrides", default=CONFIG["manual_overrides"])
    ps.add_argument("--field-schema", default=CONFIG["field_schema"])
    ps.add_argument(
        "--released-product-grace-days",
        type=int,
        default=7,
        help="incremental mode: refetch product pages until this many days after release",
    )
    ps.add_argument(
        "--product-page-cache-ttl-days",
        type=float,
        default=3650.0,
        help="incremental mode: reuse cached product-page HTML for this many days",
    )

    pn = sub.add_parser("normalize")
    pn.add_argument("--csv", required=True)
    pn.add_argument("--json", default="")
    pn.add_argument("--outdir", default="")
    pn.add_argument("--suffix", default=CONFIG["normalize_suffix"])
    pn.add_argument("--manual-overrides", default=CONFIG["manual_overrides"])
    pn.add_argument("--field-schema", default=CONFIG["field_schema"])

    pm = sub.add_parser("mine")
    pm.add_argument("--csv", required=True)
    pm.add_argument("--outdir", default="")
    pm.add_argument("--top", type=int, default=120)

    pa = sub.add_parser("audit")
    pa.add_argument("--csv", required=True)
    pa.add_argument("--top-unknown", type=int, default=30)

    pdg = sub.add_parser("db-generation-audit")
    pdg.add_argument("--dbdir", default=CONFIG["outdir"])
    pdg.add_argument(
        "--strict",
        action="store_true",
        help="exit with status 2 when canonical DB files are missing or cardnumber sets differ",
    )

    pim = sub.add_parser("image-manifest")
    pim.add_argument("--json", default="")
    pim.add_argument("--csv", default="")
    pim.add_argument("--outdir", default=CONFIG["outdir"])
    pim.add_argument("--cache", default=CONFIG["cache"])
    pim.add_argument("--delay", type=float, default=CONFIG["delay"])
    pim.add_argument("--user-agent", default=CONFIG["user_agent"])
    pim.add_argument("--timeout", type=float, default=25.0)
    pim.add_argument(
        "--max-429",
        type=int,
        default=CONFIG["max_429"],
        help="maximum consecutive HTTP 429 responses before safe stop",
    )
    pim.add_argument("--no-per-card-fallback", action="store_true")

    pall = sub.add_parser("all")
    pall.add_argument("--products-url", default=CONFIG["products_url"])
    pall.add_argument("--outdir", default=CONFIG["outdir"])
    pall.add_argument("--cache", default=CONFIG["cache"])
    pall.add_argument("--delay", type=float, default=CONFIG["delay"])
    pall.add_argument("--cache-ttl-sec", type=float, default=CONFIG["cache_ttl_sec"])
    pall.add_argument("--checkpoint-every", type=int, default=CONFIG["checkpoint_every"])
    pall.add_argument("--max-fail", type=int, default=CONFIG["max_fail"])
    pall.add_argument(
        "--max-429",
        type=int,
        default=CONFIG["max_429"],
        help="maximum consecutive HTTP 429 responses before safe stop",
    )
    pall.add_argument("--user-agent", default=CONFIG["user_agent"])
    pall.add_argument("--limit-products", type=int, default=0)
    pall.add_argument("--limit-cards", type=int, default=0)
    pall.add_argument("--no-normalize", action="store_true")
    pall.add_argument(
        "--fresh",
        action="store_true",
        help="ignore existing cards_min.csv/json and rebuild from fetched pages",
    )
    pall.add_argument("--suffix", default=CONFIG["normalize_suffix"])
    pall.add_argument("--mine-top", type=int, default=120)
    pall.add_argument("--top-unknown", type=int, default=30)
    pall.add_argument("--no-official-image-manifest", action="store_true")
    pall.add_argument("--official-timeout", type=float, default=25.0)
    pall.add_argument("--no-per-card-fallback", action="store_true")
    pall.add_argument("--manual-overrides", default=CONFIG["manual_overrides"])
    pall.add_argument("--field-schema", default=CONFIG["field_schema"])
    pall.add_argument(
        "--released-product-grace-days",
        type=int,
        default=7,
        help="incremental mode: refetch product pages until this many days after release",
    )
    pall.add_argument(
        "--product-page-cache-ttl-days",
        type=float,
        default=3650.0,
        help="incremental mode: reuse cached product-page HTML for this many days",
    )

    return p


def main() -> None:
    args = build_parser().parse_args()

    if args.cmd == "scrape":
        CONFIG["cache_ttl_sec"] = max(0.0, float(args.cache_ttl_sec))
        outdir = Path(args.outdir)
        fetch_state = FetchState(
            outdir / "failed_fetches.csv",
            max_429=args.max_429,
        )
        cmd_scrape(
            products_url=args.products_url,
            outdir=outdir,
            cache_dir=Path(args.cache),
            delay=args.delay,
            checkpoint_every=args.checkpoint_every,
            max_fail=args.max_fail,
            user_agent=args.user_agent,
            limit_products=args.limit_products,
            limit_cards=args.limit_cards,
            no_normalize=args.no_normalize,
            fresh=args.fresh,
            fetch_state=fetch_state,
            manual_overrides=Path(args.manual_overrides) if args.manual_overrides else None,
            released_product_grace_days=args.released_product_grace_days,
            field_schema=Path(args.field_schema) if args.field_schema else None,
            product_page_cache_ttl_days=args.product_page_cache_ttl_days,
        )
        return

    if args.cmd == "normalize":
        csvp = Path(args.csv)
        jsonp = Path(args.json) if args.json else None
        outdir = Path(args.outdir) if args.outdir else csvp.parent
        cmd_normalize(csvp, jsonp, outdir, args.suffix, manual_overrides=Path(args.manual_overrides) if args.manual_overrides else None, field_schema=Path(args.field_schema) if args.field_schema else None)
        return

    if args.cmd == "mine":
        csvp = Path(args.csv)
        outdir = Path(args.outdir) if args.outdir else csvp.parent
        cmd_mine(csvp, outdir, args.top)
        return

    if args.cmd == "audit":
        cmd_audit(Path(args.csv), args.top_unknown)
        return

    if args.cmd == "db-generation-audit":
        audit_db_generation_consistency(
            Path(args.dbdir),
            strict=args.strict,
            label="cli",
        )
        return

    if args.cmd == "image-manifest":
        outdir = Path(args.outdir)
        fetch_state = FetchState(
            outdir / "failed_fetches.csv",
            max_429=args.max_429,
        )
        db_json = Path(args.json) if args.json else None
        db_csv = Path(args.csv) if args.csv else None
        cmd_official_image_manifest(
            db_json=db_json,
            db_csv=db_csv,
            outdir=outdir,
            cache_dir=Path(args.cache),
            delay=args.delay,
            user_agent=args.user_agent,
            timeout=args.timeout,
            per_card_fallback=(not args.no_per_card_fallback),
            fetch_state=fetch_state,
        )
        return

    if args.cmd == "all":
        CONFIG["cache_ttl_sec"] = max(0.0, float(args.cache_ttl_sec))
        outdir = Path(args.outdir)
        fetch_state = FetchState(
            outdir / "failed_fetches.csv",
            max_429=args.max_429,
        )
        out_csv, out_json = cmd_scrape(
            products_url=args.products_url,
            outdir=outdir,
            cache_dir=Path(args.cache),
            delay=args.delay,
            checkpoint_every=args.checkpoint_every,
            max_fail=args.max_fail,
            user_agent=args.user_agent,
            limit_products=args.limit_products,
            limit_cards=args.limit_cards,
            no_normalize=args.no_normalize,
            fresh=args.fresh,
            fetch_state=fetch_state,
            manual_overrides=Path(args.manual_overrides) if args.manual_overrides else None,
            released_product_grace_days=args.released_product_grace_days,
            field_schema=Path(args.field_schema) if args.field_schema else None,
            product_page_cache_ttl_days=args.product_page_cache_ttl_days,
        )
        norm_csv, norm_json = cmd_normalize(out_csv, out_json, outdir, args.suffix, manual_overrides=Path(args.manual_overrides) if args.manual_overrides else None, field_schema=Path(args.field_schema) if args.field_schema else None)
        cmd_mine(norm_csv, outdir, args.mine_top)
        cmd_audit(norm_csv, args.top_unknown)
        audit_db_generation_consistency(
            outdir,
            strict=False,
            label="all_post_normalize",
        )
        if not args.no_official_image_manifest:
            try:
                cmd_official_image_manifest(
                    db_json=norm_json,
                    db_csv=norm_csv,
                    outdir=outdir,
                    cache_dir=Path(args.cache),
                    delay=args.delay,
                    user_agent=args.user_agent,
                    timeout=args.official_timeout,
                    per_card_fallback=(not args.no_per_card_fallback),
                    fetch_state=fetch_state,
                )
            except FetchSafetyStop:
                raise
            except Exception as e:
                print(f"[WARN] official image manifest generation failed: {e}")
        return


if __name__ == "__main__":
    try:
        main()
    except FetchSafetyStop as e:
        print(f"[SAFE-STOP] {e}")
        raise SystemExit(75)
