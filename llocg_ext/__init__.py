# -*- coding: utf-8 -*-
# BUILD_TAG: llocg_ext_loader_20260625n
"""External extension loader for Loveca UI.

This package is intentionally outside ``llocg_ui`` so future patches can add or
replace extension modules without overwriting the core simulator files.

Default behavior:
- load ``llocg_ext.public_reveal``;
- additionally load comma-separated module names from ``LLOCG_EXT_MODULES``.

Each module may expose ``apply_app_hook(app)``.  The hook receives the live
``App`` instance from ``llocg_ui.server``.
"""
from __future__ import annotations

import importlib
import os
from typing import Any, Iterable

DEFAULT_MODULES = ("llocg_ext.public_reveal", "llocg_ext.effect_matchers")


def _module_names() -> list[str]:
    names = list(DEFAULT_MODULES)
    extra = os.environ.get("LLOCG_EXT_MODULES", "")
    for raw in extra.split(','):
        name = raw.strip()
        if name and name not in names:
            names.append(name)
    return names


def apply_extensions(app: Any) -> None:
    loaded: list[str] = []
    for name in _module_names():
        mod = importlib.import_module(name)
        hook = getattr(mod, "apply_app_hook", None)
        if callable(hook):
            hook(app)
            loaded.append(name)
    try:
        setattr(app, "_llocg_ext_loaded_modules", loaded)
    except Exception:
        pass
