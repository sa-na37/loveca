# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_facade_split_20260413a
from __future__ import annotations

"""llocg_ui.engine_effect

薄い effect 拡張入口。

役割:
- engine.py との接続点だけを維持する
- matcher は effects.registry に委譲する
- apply は effects.apply に委譲する

注意:
- runtime の挙動は変えない
- このファイル自体は小さく保ち、Claude に渡す主編集対象から外す方向にする
- 新規実装は原則として llocg_ui/effects/ 配下へ追加する
"""

from typing import Any, Dict, Optional, Tuple

from .effects.registry import EXTRA_EFFECT_RULES, try_match_effect_template_ext
from .effects.apply import try_apply_effect_by_rule_ext

__all__ = [
    "EXTRA_EFFECT_RULES",
    "try_match_effect_template_ext",
    "try_apply_effect_by_rule_ext",
]
