# -*- coding: utf-8 -*-
# BUILD_TAG: effect_matchers_green_recovery_aru_phrase_20260629w
"""External effect-template matchers for Loveca UI.

Adds conservative generic matcher(s) without editing ``llocg_ui.effects.registry``.

Current scope:
- simple green-room recovery effects that move exactly one own green-room card to hand;
- filters: card type, group/unit label, cost <= N, score <= N / >= N,
  required-heart color count >= N;
- both 「控え室から...」 and 「控え室にある...」 wording.

The matcher returns existing ext_key ``green_pick_filtered_to_hand`` so
``llocg_ui.effects.green_search`` handles candidate display and green->hand move.
"""
from __future__ import annotations

import importlib
import re
from typing import Any, Dict, Optional, Tuple

WRAP_ATTR = "__loveca_effect_matchers_ext_wrapped__"

_HEART_COLOR_TO_KEY = {
    "桃": "pink",
    "赤": "red",
    "黄": "yellow",
    "緑": "green",
    "青": "blue",
    "紫": "purple",
    "任意": "any",
    "ALL": "all",
}


def _norm_ws_local(text: str) -> str:
    s = str(text or "")
    try:
        reg = importlib.import_module("llocg_ui.effects.registry")
        fn = getattr(reg, "_norm_ws", None)
        if callable(fn):
            return str(fn(s))
    except Exception:
        pass
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"\s+", "", s)
    return s.strip()


def _jp_kind_to_norm(kind: str) -> str:
    k = str(kind or "")
    if "メンバー" in k:
        return "MEMBER"
    if "ライブ" in k:
        return "LIVE"
    return ""


def _parse_simple_green_recovery_desc(desc: str) -> Optional[Dict[str, str]]:
    """Parse the descriptor before ``...カードを1枚手札に加える``.

    Accept only simple filters. Reject unsupported relational descriptors like
    「これにより公開したカード名がすべて含まれるライブカード」 to avoid
    false positives.
    """
    original = str(desc or "").strip()
    if not original:
        return None

    kind_norm = ""
    if "メンバーカード" in original:
        kind_norm = "MEMBER"
    elif "ライブカード" in original:
        kind_norm = "LIVE"
    elif original.endswith("カード") or "カード" in original:
        kind_norm = ""
    else:
        return None

    gd: Dict[str, str] = {"want_kind": kind_norm}
    rest = original

    # Remove target kind words.
    rest = rest.replace("メンバーカード", "")
    rest = rest.replace("ライブカード", "")
    # Remove bare カード only after more-specific kinds were removed.
    rest = re.sub(r"カード$", "", rest)

    m = re.search(r"『([^』]+)』の", rest)
    if m:
        gd["want_group"] = m.group(1).strip()
        rest = rest.replace(m.group(0), "", 1)

    for pat in (r"コスト(\d+)以下の", r"(\d+)コスト以下の"):
        m = re.search(pat, rest)
        if m:
            gd["cost_max"] = m.group(1).strip()
            rest = rest.replace(m.group(0), "", 1)
            break

    m = re.search(r"スコア(\d+)以下の", rest)
    if m:
        gd["score_max"] = m.group(1).strip()
        rest = rest.replace(m.group(0), "", 1)

    m = re.search(r"スコア(\d+)以上の", rest)
    if m:
        gd["score_min"] = m.group(1).strip()
        rest = rest.replace(m.group(0), "", 1)

    m = re.search(r"必要ハートに<([^>]+)>を(\d+)以上含む", rest)
    if m:
        color = m.group(1).strip().strip("()（）")
        gd["req_heart_color"] = _HEART_COLOR_TO_KEY.get(color, color)
        gd["req_heart_min"] = m.group(2).strip()
        rest = rest.replace(m.group(0), "", 1)

    # Only simple particles may remain. Anything semantic means unsupported.
    rest_clean = rest.replace("の", "").replace("、", "").strip()
    if rest_clean:
        return None

    return gd


def _generic_green_pick_one_to_hand(effect_text: str) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """Match simple public-zone recovery effects from green room to hand.

    Covered examples:
      - 自分の控え室からコスト2以下のメンバーカードを1枚手札に加える。
      - 自分の控え室から4コスト以下の『蓮ノ空』のメンバーカードを1枚手札に加える。
      - 自分の控え室から『μ's』のライブカード1枚を手札に加える。
      - 自分の控え室から、スコア6以上のライブカードを1枚手札に加える。
      - 控え室から必要ハートに<黄>を3以上含むライブカードを1枚手札に加える。
      - 自分の控え室にあるライブカードを1枚手札に加える。

    Not covered:
      - 2枚まで / 複数枚 / optional variants;
      - relational filters such as 「これにより公開したカード名がすべて含まれる」;
      - moving cards from green room to zones other than hand.
    """
    t = _norm_ws_local(effect_text)
    m = re.fullmatch(
        r"(?:自分の)?控え室(?:から|にある)、?"
        r"(?P<desc>.+?カード)"
        r"(?:(?:を1枚)|(?:1枚を))手札に加える。",
        t,
    )
    if not m:
        return None

    gd = _parse_simple_green_recovery_desc(m.group("desc") or "")
    if gd is None:
        return None

    gd["source_name"] = "控え室回収"
    gd["effect_text"] = t

    kind_norm = str(gd.get("want_kind") or "")
    label_parts = ["控え室から"]
    if gd.get("cost_max"):
        label_parts.append(f"コスト{gd['cost_max']}以下の")
    if gd.get("score_min"):
        label_parts.append(f"スコア{gd['score_min']}以上の")
    if gd.get("score_max"):
        label_parts.append(f"スコア{gd['score_max']}以下の")
    if gd.get("req_heart_color") and gd.get("req_heart_min"):
        label_parts.append(f"必要ハート条件を満たす")
    if gd.get("want_group"):
        label_parts.append(f"『{gd['want_group']}』の")
    if kind_norm == "MEMBER":
        label_parts.append("メンバーカード")
    elif kind_norm == "LIVE":
        label_parts.append("ライブカード")
    else:
        label_parts.append("カード")
    label_parts.append("を1枚選んでください")
    gd["pending_label"] = "".join(label_parts)

    return (
        {
            "id": "generic_green_pick_one_to_hand",
            "op": "__ext__",
            "ext_key": "green_pick_filtered_to_hand",
        },
        gd,
    )


def _wrap_try_match_effect_template_ext(fn):
    if getattr(fn, WRAP_ATTR, False):
        return fn

    def wrapped(eng: Dict[str, Any], effect_text: str):
        res = fn(eng, effect_text)
        if res is not None:
            return res
        res2 = _generic_green_pick_one_to_hand(effect_text)
        if res2 is not None:
            return res2
        return None

    setattr(wrapped, WRAP_ATTR, True)
    setattr(wrapped, "__wrapped__", fn)
    return wrapped


def apply_app_hook(app: Any) -> None:
    try:
        reg = importlib.import_module("llocg_ui.effects.registry")
        fn = getattr(reg, "try_match_effect_template_ext", None)
        if callable(fn):
            setattr(reg, "try_match_effect_template_ext", _wrap_try_match_effect_template_ext(fn))
            try:
                app.gs.log.append("[EXT] effect matchers active: broad generic green pick one to hand")
            except Exception:
                pass
    except Exception as e:
        try:
            app.gs.log.append(f"[EXT][ERR] effect_matchers load failed: {e}")
        except Exception:
            pass
