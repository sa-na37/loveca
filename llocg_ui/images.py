# -*- coding: utf-8 -*-
# BUILD_TAG: rm_rarity_image_resolution_20260721a
from __future__ import annotations

"""llocg_ui.images

ローカルカード画像の解決。

優先順位:
1. ``<root>/llocg_db_out_full/card_images`` / ``<root>/card_images`` / legacy ``card_image`` の正規画像
2. ``<root>/preview_card_images`` の発売前preview画像
3. ``NoImage.PNG``

- ``db._cardno_variants()`` でcardnumber表記揺れを吸収
- 同一カードが複数レアリティで存在する場合は優先順で1枚選ぶ
- 正規画像はpreviewより常に優先する
"""

from pathlib import Path
from typing import Dict, Iterable, List, Optional
import re

from .db import _cardno_variants

BUILD_TAG = "rm_rarity_image_resolution_20260721a"

RARITY_PREF = [
    "N", "R", "R2", "L", "L2", "SD", "CL",
    "PR", "PR2", "SEC", "SEC2", "SECL", "SRL",
    "DUO", "AR", "RM", "RE", "PE", "PE2",
    "SECE", "LLE", "P", "P2",
]
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


class ImageLocator:
    def __init__(self, root: Path):
        self.root = Path(root)

        # Canonical images. Keep legacy singular folder support.
        self.canonical_bases: List[Path] = []
        for p in (
            self.root / "llocg_db_out_full" / "card_images",
            self.root / "card_images",
            self.root / "card_image",
        ):
            if p.exists() and p.is_dir() and p not in self.canonical_bases:
                self.canonical_bases.append(p)
        if not self.canonical_bases:
            self.canonical_bases = [self.root / "card_images"]

        # Preview images are intentionally separate from canonical images.
        self.preview_bases: List[Path] = [self.root / "preview_card_images"]

        # Compatibility alias for code/tests that still inspect ``bases``.
        self.bases = self.canonical_bases

        # Cache only the resolved fallback path. Canonical files are checked
        # before this cache so a newly downloaded official image immediately
        # supersedes a cached preview without restarting the server.
        self.cache: Dict[str, Path] = {}

    def _no_image_path(self) -> Optional[Path]:
        for base in self.canonical_bases:
            for fn in ("NoImage.PNG", "NoImage.png", "noimage.png", "noimage.PNG"):
                p = base / fn
                if p.exists() and p.is_file():
                    return p
        return None

    def _rarity_from_name(self, path: Path) -> str:
        stem = path.stem
        # Preview naming:
        #   <cardno>-<RARITY>-PREVIEW.jpg
        #   <cardno>-<RARITY>-PREVIEW-02.webp
        #   <cardno>-PREVIEW.jpg
        m = re.search(r"[-_\s]([A-Za-z0-9＋+]+)[-_\s]PREVIEW(?:[-_\s]\d+)?$", stem, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        m = re.search(r"[-_\s]([A-Za-z0-9＋+]+)$", stem)
        return m.group(1).upper() if m else ""

    def _normalize_rarity(self, value: str) -> str:
        text = str(value or "").strip().upper()
        return text.replace("＋", "+").replace("+", "2")

    def _choose_best(self, paths: List[Path], rarity: str = "") -> Optional[Path]:
        if not paths:
            return None
        wanted = self._normalize_rarity(rarity)
        if wanted:
            exact = [p for p in paths if self._normalize_rarity(self._rarity_from_name(p)) == wanted]
            if exact:
                paths = exact
        scored = []
        for p in paths:
            rarity = self._normalize_rarity(self._rarity_from_name(p))
            try:
                r_rank = RARITY_PREF.index(rarity)
            except ValueError:
                r_rank = 999
            scored.append((r_rank, len(str(p)), str(p), p))
        scored.sort(key=lambda x: (x[0], x[1], x[2]))
        return scored[0][3]

    def _find_hits(self, bases: Iterable[Path], cands: List[str]) -> List[Path]:
        hits: List[Path] = []
        for key in cands:
            for base in bases:
                if not base.exists() or not base.is_dir():
                    continue
                for ext in IMAGE_EXTENSIONS:
                    for pattern in (
                        f"*/{key}-*{ext}",
                        f"*/{key}_*{ext}",
                        f"*/{key} *{ext}",
                        f"{key}-*{ext}",
                        f"{key}_*{ext}",
                        f"{key} *{ext}",
                    ):
                        hits.extend(p for p in base.glob(pattern) if p.is_file())
        return hits

    def find(self, cardnumber: str, rarity: str = "") -> Optional[Path]:
        cn = (cardnumber or "").strip()
        if not cn:
            return None

        if cn == "__BACK__":
            for fn in ("back.jpeg", "back.jpg", "back.png", "back.webp"):
                for base in self.canonical_bases:
                    p = base / fn
                    if p.exists():
                        return p
            return None

        cands = _cardno_variants(cn)
        rarity_key = self._normalize_rarity(rarity)
        cache_keys = [f"{key}|rarity={rarity_key}" for key in cands] if rarity_key else list(cands)

        # Canonical images are always resolved first, even when a preview path
        # is already cached. This preserves card_images > preview_card_images.
        canonical = self._choose_best(self._find_hits(self.canonical_bases, cands), rarity=rarity_key)
        if canonical:
            for key in cache_keys:
                self.cache[key] = canonical
            return canonical

        # No canonical image exists. A cached preview/fallback may be reused.
        for key in cache_keys:
            cached = self.cache.get(key)
            if cached and cached.exists():
                return cached

        preview = self._choose_best(self._find_hits(self.preview_bases, cands), rarity=rarity_key)
        if preview:
            for key in cache_keys:
                self.cache[key] = preview
            return preview

        fallback = self._no_image_path()
        if fallback:
            for key in cache_keys:
                self.cache[key] = fallback
            return fallback

        return None


# ----------------------------
