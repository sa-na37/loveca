# -*- coding: utf-8 -*-
from __future__ import annotations

"""llocg_ui.images

`<root>/card_images/*/<cardnumber>-<rarity>.png` から画像を引くためのローカル解決。

- `db._cardno_variants()` で揺れを吸収
- 同一カードが複数レアリティで存在するため、優先順で 1 枚選ぶ
"""

from pathlib import Path
from typing import Dict, List, Optional
import re

from .db import _cardno_variants

RARITY_PREF = ["N", "R", "R2", "L", "L2", "SD", "PR", "SEC", "SECL", "AR", "RM", "P", "P2"]


class ImageLocator:
    def __init__(self, root: Path):
        self.root = Path(root)
        # Folder naming drift across runs:
        #   - legacy:  <root>/card_images/
        #   - current: <root>/card_image/
        # Support both without creating/renaming folders.
        self.bases: List[Path] = []
        for name in ("card_images", "card_image"):
            p = self.root / name
            if p.exists() and p.is_dir():
                self.bases.append(p)
        # Keep previous behaviour if neither exists yet.
        if not self.bases:
            self.bases = [self.root / "card_images"]
        self.cache: Dict[str, Path] = {}

    def _choose_best(self, paths: List[Path]) -> Optional[Path]:
        if not paths:
            return None
        scored = []
        for p in paths:
            m = re.match(r"^(.*?)-([A-Za-z0-9\+]+)\.png$", p.name)
            rarity = m.group(2).upper() if m else ""
            try:
                r_rank = RARITY_PREF.index(rarity)
            except ValueError:
                r_rank = 999
            scored.append((r_rank, len(str(p)), p))
        scored.sort(key=lambda x: (x[0], x[1]))
        return scored[0][2]

    def find(self, cardnumber: str) -> Optional[Path]:
        # Try all supported bases (plural/singular) in order.
        bases = [b for b in self.bases if b.exists()]
        if not bases:
            return None
        cn = (cardnumber or "").strip()
        if not cn:
            return None
        if cn == "__BACK__":
            for fn in ("back.jpeg","back.jpg","back.png"):
                for base in bases:
                    p = base / fn
                    if p.exists():
                        return p
            return None
        cands = _cardno_variants(cn)
        for key in cands:
            if key in self.cache and self.cache[key].exists():
                return self.cache[key]
        hits: List[Path] = []
        for key in cands:
            for base in bases:
                hits.extend([p for p in base.glob(f"*/{key}-*.png") if p.is_file()])
        best = self._choose_best(hits)
        if best:
            for key in cands:
                self.cache[key] = best
        return best


# ----------------------------
