#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

BUILD_TAG = "audit_yell_family_20260604a"

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path


def compact_for_path(p: Path) -> str:
    return str(p.resolve())


def resolve_root(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).expanduser().resolve()
    here = Path(__file__).resolve()
    # expected location: <project>/tools/audit_yell_family_20260604.py
    if here.parent.name == "tools":
        return here.parent.parent.resolve()
    return Path.cwd().resolve()


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit Loveca yell-revealed effect family against current runtime handlers.")
    ap.add_argument("--root", default=None, help="Project root. Default: parent of tools/ or current directory.")
    ap.add_argument("--outdir", default=None, help="Output directory. Default: <root>/loveca_reports")
    args = ap.parse_args()

    root = resolve_root(args.root)
    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else root / "loveca_reports"
    outdir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(root))
    import llocg_ui.engine as eng  # noqa: E402
    from llocg_ui.db import load_cards_db  # noqa: E402

    def compact(s: str) -> str:
        return eng._yell_compact_text(s or "")

    def body_support_kind(eff: str) -> str:
        ec = compact(eff)
        m_icons = re.search(r"ライブ終了時まで、?(?P<icons>(?:<\([^)]+\)>)+)を得る。?", ec)
        if ("同じグループを持つメンバーカードが3枚" in ec) and m_icons:
            return "body_auto_same_group_member3_gain_icons"
        if ("ブレードハートを持たないメンバーカードが" in ec) and m_icons:
            return "body_auto_no_bladeheart_members_gain_icons"
        if ("スコア+1" in ec) and ("ライブカードが1枚以上" in ec) and ("ライブ終了時まで" in ec) and m_icons:
            return "body_auto_score_plus_group_live_gain_icons"
        if ("ライブカードが1枚以上" in ec) and ("ライブ終了時まで" in ec) and m_icons and ("手札が" not in ec):
            return "body_auto_live_exists_gain_icons"
        if ("ライブカードが1枚以上" in ec) and ("手札が" in ec) and ("カードを1枚引く" in ec):
            return "body_auto_live_exists_hand_limit_draw1"
        if ("ライブカード1枚につき" in ec) and ("この能力では" in ec):
            return "body_auto_per_live_gain_icons_cap"
        if ("ブレードハートを持つカードがないとき" in ec) and m_icons:
            return "body_auto_no_bladeheart_cards_gain_icons"
        if ("ブレードハートの中に" in ec) and ("3種類以上" in ec) and m_icons:
            return "body_auto_bladeheart_kind_threshold_gain_icons_score"
        return ""

    cards_db = load_cards_db(root)
    gs = eng.GameState(root=str(root), code="debug", seed=1, debug=True)
    unique = {ci.cardnumber: ci for ci in cards_db.values()}
    rows: list[dict[str, str]] = []
    excluded_unknown = {f"PL!SP-pb2-{i:03d}" for i in range(17, 22)}

    for ci in sorted(unique.values(), key=lambda x: x.cardnumber):
        if ci.cardnumber in excluded_unknown:
            continue
        for ab in ci.abilities or []:
            if not isinstance(ab, dict):
                continue
            for cl in ab.get("clauses") or []:
                if not isinstance(cl, dict):
                    continue
                eff = (cl.get("effect_template") or cl.get("raw") or "").strip()
                raw = cl.get("raw") or ""
                cost = (cl.get("cost_template") or "").strip()
                if "エール" not in (eff + raw + cost):
                    continue

                status = "needs_implementation"
                handler = ""
                if "ウェイト状態のメンバーが持つ" in eff.replace("\n", ""):
                    status = "note_only_rule_text"
                    handler = "no_runtime_effect"
                else:
                    mt = eng._match_effect_template(eff)
                    if mt:
                        status = "implemented"
                        handler = f"effect_template:{mt[0].get('id')}"
                    elif "ライブ成功時" in str(ab.get("trigger", "")):
                        trig = eng._build_live_success_trigger_from_effect(
                            gs, cards_db, eff, ci.cardnumber, f"{ci.cardnumber}[ライブ成功時]", {"source_cn": ci.cardnumber}
                        )
                        if trig and trig.get("kind") != "apply_effect_template_on_live_success":
                            status = "implemented"
                            handler = f"live_success:{trig.get('kind')}"
                        elif trig:
                            status = "needs_audit_unmatched_live_success"
                            handler = str(trig.get("kind"))
                        else:
                            status = "needs_implementation"
                    elif "BODY" in str(ab.get("trigger", "")) or "自分がエール" in eff:
                        bk = body_support_kind(eff)
                        if bk:
                            status = "implemented"
                            handler = bk
                    elif "ライブ開始時" in str(ab.get("trigger", "")):
                        trig = eng._build_live_start_trigger_from_effect(
                            gs, cards_db, eff, ci.cardnumber, f"{ci.cardnumber}[ライブ開始時]", {"source_cn": ci.cardnumber, "set_idx": 0}
                        )
                        if trig:
                            status = "implemented"
                            handler = f"live_start:{trig.get('kind')}"

                rows.append({
                    "cardnumber": ci.cardnumber,
                    "cardname": ci.name,
                    "card_type": ci.type,
                    "ability_type": str(ab.get("ability_type", "")),
                    "trigger": str(ab.get("trigger", "")),
                    "status": status,
                    "handler": handler,
                    "effect": eff.replace("\n", " "),
                    "cost": cost.replace("\n", " "),
                })

    out_csv = outdir / "loveca_yell_revealed_family_audit_20260604a.csv"
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["cardnumber", "cardname", "card_type", "ability_type", "trigger", "status", "handler", "effect", "cost"])
        w.writeheader()
        w.writerows(rows)

    counts = Counter(r["status"] for r in rows)
    implemented = [r for r in rows if r["status"] == "implemented"]
    notes = [r for r in rows if r["status"] == "note_only_rule_text"]
    remaining = [r for r in rows if r["status"].startswith("needs_")]

    out_md = outdir / "loveca_yell_revealed_family_audit_20260604a.md"
    lines: list[str] = []
    lines.append("# Loveca エール公開参照 family 既実装除外・残件再抽出 2026-06-04a")
    lines.append("")
    lines.append("## 集計")
    for k, v in sorted(counts.items()):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 既実装 / 今回共通化対象に入れたもの")
    for r in implemented:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} / {r['handler']} / {r['effect']}")
    lines.append("")
    lines.append("## 注釈のみ")
    for r in notes:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} / {r['effect']}")
    lines.append("")
    lines.append("## 残件")
    for r in remaining:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} / {r['status']} / {r['effect']}")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[OK] root: {root}")
    print(f"[OK] wrote: {out_csv}")
    print(f"[OK] wrote: {out_md}")
    print(dict(counts))


if __name__ == "__main__":
    main()
