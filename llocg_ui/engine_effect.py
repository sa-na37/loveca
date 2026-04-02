# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_position_change_20260331b
from __future__ import annotations

"""llocg_ui.engine_effect

Claude向けの軽量効果拡張ファイル。

目的
----
- 現 runtime の正本は engine.py のまま維持する。
- 日常の新規効果実装は、できるだけこの小さいファイルだけで完結させる。
- server.py は .engine しか import しないため、engine.py 側 API は壊さない。

運用原則
--------
1. まずこのファイルだけを Claude に渡す。
2. handout / prompt も併せて渡すが、コード変更対象は原則このファイルのみ。
3. engine.py を編集するのは次の場合だけ:
   - 新しい pending kind を engine.py 側で UI/解決対応まで増やす必要がある。
   - 既存 helper / cmd / phase 遷移では表現できない。
   - 新しい dataclass field や state_json 契約の追加が必要。
4. UI の一時ブレード/ハート表示は StageSlot.temp_blade / temp_hearts が基本契約。
5. このファイルは engine.py を import しないこと。循環 import 防止のため、
   engine.py から globals() が渡される。

engine.py 側接続点
------------------
- _match_effect_template() の先頭で try_match_effect_template_ext() を呼ぶ。
- _apply_effect_by_rule() の先頭で try_apply_effect_by_rule_ext() を呼ぶ。
- このファイルは「拡張ルールがヒットした時だけ処理する」。
- 未対応なら None / False を返し、engine.py の既存巨大実装へフォールバックする。

Claude に渡す 3 点
------------------
- engine_effect.py   : このファイル（コード本体）
- handout            : runtime truth / UI 契約 / debug ルール / 対象カード最小DB
- prompt             : 今回の effect_template / 禁止事項 / 出力形式

最小 API 契約
-------------
try_match_effect_template_ext(eng, effect_text) -> Optional[(rule_dict, gd_dict)]
    - eng は engine.py の globals() dict
    - マッチしたら (rule, groupdict) を返す
    - 未対応なら None

try_apply_effect_by_rule_ext(eng, gs, rng, cards_db, rule, gd, ctx) -> bool
    - 自分の拡張ルールなら処理して True
    - 未対応なら False

実装方針
--------
- effect_template は exact match を第一選択にする。
  理由: 既存 regex 群と衝突しにくく、Claude 作業でも安全。
- 必要になった時だけ regex を使う。
- rule dict は最小限のキーだけ持つ:
    {"id": ..., "op": "__ext__", "ext_key": ...}
- helper はこのファイル内に小さく置く。共通化しすぎない。
- engine.py の既存 helper は eng["helper_name"] で使う。

注意
----
- このファイルに handout 相当の要点を残しておくが、長文化しすぎない。
- 対象カードの詳細 DB は handout 側に置く。ここには常設しない。
- 既存 UI 契約:
    slot.temp_blade: int
    slot.temp_hearts: {pink/red/yellow/green/blue/purple/all: int}
  を守る。
"""

from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Extension rule table
# ---------------------------------------------------------------------------
# 通常の新規効果実装はここへ追加する。
# 形式:
#   {
#       "id": "human_readable_id",
#       "effect_template": "完全一致で扱う effect_template",
#       "ext_key": "dispatch key",
#   }
#
# 例:
# EXTRA_EFFECT_RULES.append({
#     "id": "body_stage_exactly_2_get_blue_blade",
#     "effect_template": "自分のステージにいるメンバーがちょうど2人であるかぎり、<(青)><(ブレード)>を得る。",
#     "ext_key": "body_stage_exactly_2_get_blue_blade",
# })
#
# try_apply_effect_by_rule_ext() の dispatch に同じ ext_key を追加する。
EXTRA_EFFECT_RULES = [
    {
        "id": "position_change_optional",
        "effect_template": "このメンバーをポジションチェンジしてもよい。",
        "ext_key": "position_change_optional",
    },
]


def try_match_effect_template_ext(
    eng: Dict[str, Any],
    effect_text: str,
) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """Match extension-owned effect templates.

    Returns:
        (rule, gd) if matched, else None.
    """
    s = (effect_text or "").strip()
    if not s:
        return None

    for r in EXTRA_EFFECT_RULES:
        tpl = str(r.get("effect_template", "") or "").strip()
        if tpl and s == tpl:
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})
    return None


def _add_temp_blade(eng: Dict[str, Any], slot: Any, n: int) -> None:
    if not slot or n <= 0:
        return
    try:
        slot.temp_blade = int(getattr(slot, "temp_blade", 0) or 0) + int(n)
    except Exception:
        pass


def _add_temp_hearts(eng: Dict[str, Any], slot: Any, hearts: Dict[str, int]) -> None:
    if not slot or not hearts:
        return
    try:
        cur = dict(getattr(slot, "temp_hearts", {}) or {})
    except Exception:
        cur = {}
    for k, v in (hearts or {}).items():
        try:
            iv = int(v or 0)
        except Exception:
            iv = 0
        if iv <= 0:
            continue
        cur[str(k)] = int(cur.get(str(k), 0) or 0) + iv
    try:
        slot.temp_hearts = cur
    except Exception:
        pass


def _active_stage_slots(gs: Any) -> list:
    out = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                v = st.get(pos)
                if v is not None and bool(getattr(v, "active", False)):
                    out.append(v)
    except Exception:
        pass
    return out


def try_apply_effect_by_rule_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, str],
    ctx: Dict[str, Any],
) -> bool:
    """Apply extension-owned effect rules.

    Return True only if this module handled the rule completely.
    Return False to fall back to engine.py legacy implementation.
    """
    if str(rule.get("op") or "") != "__ext__":
        return False

    ext_key = str(rule.get("ext_key") or "").strip()

    # ------------------------------------------------------------------
    # Add new dispatch blocks here.
    # ------------------------------------------------------------------
    # Example skeleton:
    # if ext_key == "body_stage_exactly_2_get_blue_blade":
    #     src_pos = str((ctx or {}).get("src_pos") or "")
    #     slot = (getattr(gs, "stage", {}) or {}).get(src_pos)
    #     if slot and len(_active_stage_slots(gs)) == 2:
    #         _add_temp_hearts(eng, slot, {"blue": 1})
    #         _add_temp_blade(eng, slot, 1)
    #         try:
    #             gs.log.append("[AUTO_EXT] stage exactly 2 -> +blue +blade")
    #         except Exception:
    #             pass
    #     return True
    if ext_key == "position_change_optional":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        if src_pos not in ("L", "C", "R"):
            try:
                gs.log.append(f"[WARN] position_change_optional: invalid src_pos='{src_pos}'")
            except Exception:
                pass
            return True
        options = [p for p in ("L", "C", "R") if p != src_pos] + ["skip"]

        payload = {
            "kind": "position_change",
            "src_pos": src_pos,
            "optional": True,
            "options": options,
            "source_cn": str((ctx or {}).get("source_cn") or ""),
        }
        try:
            getattr(gs, 'pending').append(payload)
            gs.log.append(f"[PENDING] position_change src={src_pos}")
        except Exception:
            pass
        return True


    return False
