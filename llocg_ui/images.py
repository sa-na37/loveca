from __future__ import annotations
import pathlib
from typing import Dict, List, Optional

IMG_EXTS = (".png",".jpg",".jpeg",".webp")

def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("＋","+")
    while s.endswith("-"):
        s = s[:-1]
    return s

class ImageLocator:
    def __init__(self, card_images_dir: pathlib.Path):
        self.card_images_dir = card_images_dir
        self.by_basename: Dict[str, pathlib.Path] = {}
        self.all_files: List[pathlib.Path] = []
        if card_images_dir.exists():
            for p in card_images_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in IMG_EXTS:
                    self.all_files.append(p)
                    self.by_basename[p.stem.lower()] = p

    def resolve(self, card_no: str, rarity: str = "") -> Optional[pathlib.Path]:
        cn = _norm(card_no)
        rr = _norm(rarity)
        if not cn:
            return None

        if cn in self.by_basename:
            return self.by_basename[cn]

        if rr:
            for c in (f"{cn}_{rr}", f"{cn}-{rr}", f"{rr}_{cn}", f"{rr}-{cn}"):
                if c in self.by_basename:
                    return self.by_basename[c]

        toks = [t for t in cn.replace("!","-").split("-") if t]
        best = None
        best_score = -1
        for p in self.all_files:
            stem = p.stem.lower()
            ok = True
            score = 0
            for t in toks:
                if t in stem:
                    score += 2
                else:
                    ok = False
                    break
            if not ok:
                continue
            if rr and rr in stem:
                score += 3
            if score > best_score:
                best_score = score
                best = p
        return best
