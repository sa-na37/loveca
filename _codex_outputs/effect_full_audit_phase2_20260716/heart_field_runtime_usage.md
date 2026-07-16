# Heart field runtime usage

- runtime state/UI primarily uses `CardInfo.base_hearts`, `CardInfo.required_hearts`, `CardInfo.blade_hearts`, and helper-derived current heart counts.
- `server.py /cardinfo` serializes `base_hearts` and `required_hearts` from loaded CardInfo, not the audit CSV `*_counts_json` columns directly.
- `engine.py` live/heart checks call helper functions such as `_slot_current_heart_color_counts`, `_stage_member_current_heart_total_count`, and related group predicates.
- The audit-only `base_hearts_counts_json`, `required_hearts_counts_json`, and tag columns are therefore evidence, not an unconditional runtime source of truth.

## grep evidence

```text
llocg_db_tool_v7.py:439:    "ブレードハート": "blade_heart",
llocg_db_tool_v7.py:440:    "基本ハート": "base_hearts",
llocg_db_tool_v7.py:441:    "必要ハート": "required_hearts",
llocg_db_tool_v7.py:455:    ("ブレードハート", "blade_heart"),
llocg_db_tool_v7.py:457:    ("基本ハート", "base_hearts"),
llocg_db_tool_v7.py:458:    ("必要ハート", "required_hearts"),
llocg_db_tool_v7.py:1312:    if out.get("blade_heart", "") == "効果テキスト":
llocg_db_tool_v7.py:1313:        out["blade_heart"] = ""
llocg_db_tool_v7.py:1371:def _normalize_blade_heart_token(raw_token: str) -> str:
llocg_db_tool_v7.py:1384:def parse_blade_heart_expr(
llocg_db_tool_v7.py:1416:        normalized = _normalize_blade_heart_token(raw_token)
llocg_db_tool_v7.py:1497:def infer_card_type(raw: Any, required_hearts_raw: Any = "", score: Any = "", cost: Any = "", blade: Any = "", base_hearts_raw: Any = "") -> Tuple[str, str]:
llocg_db_tool_v7.py:1504:    has_live_signals = _has_text_value(required_hearts_raw) or _has_text_value(score)
llocg_db_tool_v7.py:1505:    has_member_signals = _has_text_value(cost) or _has_text_value(blade) or _has_text_value(base_hearts_raw)
llocg_db_tool_v7.py:1596:    base_raw = info.get("base_hearts", "")
llocg_db_tool_v7.py:1597:    req_raw = info.get("required_hearts", "")
llocg_db_tool_v7.py:1598:    bh_raw = info.get("blade_heart", "")
llocg_db_tool_v7.py:1610:        "blade_heart_raw": bh_raw,
llocg_db_tool_v7.py:1611:        "base_hearts_raw": base_raw,
llocg_db_tool_v7.py:1612:        "required_hearts_raw": req_raw,
llocg_db_tool_v7.py:1621:            required_hearts_raw=req_raw,
llocg_db_tool_v7.py:1625:            base_hearts_raw=base_raw,
llocg_db_tool_v7.py:1632:        bh_counts, bh_total, bh_tags, bh_special = parse_blade_heart_expr(bh_raw)
llocg_db_tool_v7.py:1634:        rec["base_hearts_counts_json"] = json.dumps(base_counts, ensure_ascii=False)
llocg_db_tool_v7.py:1635:        rec["base_hearts_total"] = base_total if base_total is not None else sum(base_counts.values())
llocg_db_tool_v7.py:1636:        rec["base_hearts_tags_json"] = json.dumps(base_tags, ensure_ascii=False)
llocg_db_tool_v7.py:1638:        rec["required_hearts_counts_json"] = json.dumps(req_counts, ensure_ascii=False)
llocg_db_tool_v7.py:1639:        rec["required_hearts_total"] = req_total if req_total is not None else sum(req_counts.values())
llocg_db_tool_v7.py:1640:        rec["required_hearts_tags_json"] = json.dumps(req_tags, ensure_ascii=False)
llocg_db_tool_v7.py:1642:        rec["blade_heart_counts_json"] = json.dumps(bh_counts, ensure_ascii=False)
llocg_db_tool_v7.py:1643:        rec["blade_heart_total"] = bh_total if bh_total is not None else sum(bh_counts.values())
llocg_db_tool_v7.py:1644:        rec["blade_heart_tags_json"] = json.dumps(bh_tags, ensure_ascii=False)
llocg_db_tool_v7.py:1645:        rec["blade_heart_special_counts_json"] = json.dumps(bh_special, ensure_ascii=False)
llocg_db_tool_v7.py:1646:        rec["blade_heart_draw_n"] = int(bh_special.get("draw", 0) or 0)
llocg_db_tool_v7.py:1647:        rec["blade_heart_score_n"] = int(bh_special.get("score", 0) or 0)
llocg_db_tool_v7.py:1648:        rec["blade_heart_colorless_n"] = int(bh_special.get("colorless", 0) or 0)
llocg_db_tool_v7.py:2516:    blade_heart_counts_json, blade_heart_totals, blade_heart_tags_json = [], [], []
llocg_db_tool_v7.py:2517:    blade_heart_special_json = []
llocg_db_tool_v7.py:2518:    blade_heart_draw_n, blade_heart_score_n, blade_heart_colorless_n = [], [], []
llocg_db_tool_v7.py:2525:    req_series = df["required_hearts_raw"].tolist() if "required_hearts_raw" in df.columns else [""] * len(df)
llocg_db_tool_v7.py:2529:    base_series = df["base_hearts_raw"].tolist() if "base_hearts_raw" in df.columns else [""] * len(df)
llocg_db_tool_v7.py:2531:    blade_heart_raw_series = df["blade_heart_raw"].tolist() if "blade_heart_raw" in df.columns else [""] * len(df)
llocg_db_tool_v7.py:2542:        blade_heart_raw_series,
llocg_db_tool_v7.py:2559:        bh_counts, bh_total, bh_tags, bh_special = parse_blade_heart_expr(str(bh_raw or ""))
llocg_db_tool_v7.py:2560:        blade_heart_counts_json.append(json.dumps(bh_counts, ensure_ascii=False))
llocg_db_tool_v7.py:2561:        blade_heart_totals.append(int(bh_total or 0))
llocg_db_tool_v7.py:2562:        blade_heart_tags_json.append(json.dumps(bh_tags, ensure_ascii=False))
llocg_db_tool_v7.py:2563:        blade_heart_special_json.append(json.dumps(bh_special, ensure_ascii=False))
llocg_db_tool_v7.py:2564:        blade_heart_draw_n.append(int(bh_special.get("draw", 0) or 0))
llocg_db_tool_v7.py:2565:        blade_heart_score_n.append(int(bh_special.get("score", 0) or 0))
llocg_db_tool_v7.py:2566:        blade_heart_colorless_n.append(int(bh_special.get("colorless", 0) or 0))
llocg_db_tool_v7.py:2574:            required_hearts_raw=req_raw,
llocg_db_tool_v7.py:2578:            base_hearts_raw=base_raw,
llocg_db_tool_v7.py:2584:    df["blade_heart_counts_json"] = blade_heart_counts_json
llocg_db_tool_v7.py:2585:    df["blade_heart_total"] = blade_heart_totals
llocg_db_tool_v7.py:2586:    df["blade_heart_tags_json"] = blade_heart_tags_json
llocg_db_tool_v7.py:2587:    df["blade_heart_special_counts_json"] = blade_heart_special_json
llocg_db_tool_v7.py:2588:    df["blade_heart_draw_n"] = blade_heart_draw_n
llocg_db_tool_v7.py:2589:    df["blade_heart_score_n"] = blade_heart_score_n
llocg_db_tool_v7.py:2590:    df["blade_heart_colorless_n"] = blade_heart_colorless_n
llocg_db_tool_v7.py:2624:                    bh_counts, bh_total, bh_tags, bh_special = parse_blade_heart_expr(str(r.get("blade_heart_raw", "") or ""))
llocg_db_tool_v7.py:2625:                    r["blade_heart_counts_json"] = json.dumps(bh_counts, ensure_ascii=False)
llocg_db_tool_v7.py:2626:                    r["blade_heart_total"] = int(bh_total or 0)
llocg_db_tool_v7.py:2627:                    r["blade_heart_tags_json"] = json.dumps(bh_tags, ensure_ascii=False)
llocg_db_tool_v7.py:2628:                    r["blade_heart_special_counts_json"] = json.dumps(bh_special, ensure_ascii=False)
llocg_db_tool_v7.py:2629:                    r["blade_heart_draw_n"] = int(bh_special.get("draw", 0) or 0)
llocg_db_tool_v7.py:2630:                    r["blade_heart_score_n"] = int(bh_special.get("score", 0) or 0)
llocg_db_tool_v7.py:2631:                    r["blade_heart_colorless_n"] = int(bh_special.get("colorless", 0) or 0)
llocg_db_tool_v7.py:2634:                        required_hearts_raw=r.get("required_hearts_raw", ""),
llocg_db_tool_v7.py:2638:                        base_hearts_raw=r.get("base_hearts_raw", ""),
llocg_db_tool_v7.py:3357:    for col in ["card_type_norm", "cost", "score", "blade", "effect_text_norm", "base_hearts_raw", "required_hearts_raw"]:
llocg_db_tool_v7.py:3541:    for col in ["blade_heart_draw_n", "blade_heart_score_n", "blade_heart_colorless_n"]:
llocg_ui/engine_base.py:25:    _hearts_from_counts_json, _parse_tags_json, _count_draw_icons,
llocg_ui/engine_base.py:1213:def owned_base_hearts(gs: GameState, cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
llocg_ui/engine_base.py:1225:            orig_total = sum(int(v) for v in (c.base_hearts or {}).values())
llocg_ui/engine_base.py:1229:            for k, v in (c.base_hearts or {}).items():
llocg_ui/engine_base.py:1333:        for k, v in (c.blade_hearts or {}).items():
llocg_ui/engine_base.py:1336:            txt = str(getattr(c, 'blade_heart_tags_json', '') or '')
llocg_ui/engine_base.py:1607:        req = _effective_live_required_hearts(cn, c, globals().get('_CURRENT_GS_FOR_ATTEMPT'))
llocg_ui/engine_base.py:1624:        reqs.append((cn, _effective_live_required_hearts(cn, ci, globals().get('_CURRENT_GS_FOR_ATTEMPT'))))
llocg_ui/engine_base.py:1929:        for k, v in ((getattr(ci, 'base_hearts', None) or {}) or {}).items():
llocg_ui/engine.py:22:    _hearts_from_counts_json, _parse_tags_json, _count_draw_icons,
llocg_ui/engine.py:654:    for attr in ('base_hearts', 'blade_hearts'):
llocg_ui/engine.py:662:    raw = str(getattr(ci, 'base_hearts_raw', '') or '') + ' ' + str(getattr(ci, 'blade_heart_raw', '') or '')
llocg_ui/engine.py:670:        val = int((getattr(ci, 'required_hearts', {}) or {}).get(col, 0) or 0)
llocg_ui/engine.py:675:    raw = str(getattr(ci, 'required_hearts_raw', '') or '')
llocg_ui/engine.py:682:        total = sum(int(v or 0) for v in (getattr(ci, 'required_hearts', {}) or {}).values())
llocg_ui/engine.py:687:    raw = str(getattr(ci, 'required_hearts_raw', '') or '')
llocg_ui/engine.py:814:    Blade-heart icons are also heart icons by rule, so include both base_hearts
llocg_ui/engine.py:815:    and blade_hearts. Ignore any/all/non-colored tags for this effect.
llocg_ui/engine.py:820:    for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:1230:            has_bh = bool(_ci_blade_heart_raw_text(ci).strip()) and str(_ci_blade_heart_raw_text(ci)).strip() not in ('なし', '-', '0')
llocg_ui/engine.py:1824:            if _ci_blade_heart_has_tag(ci, '<スコア+1>'):
llocg_ui/engine.py:1979:        req = getattr(ci, 'required_hearts', None)
llocg_ui/engine.py:1997:        base = getattr(ci, 'base_hearts', None)
llocg_ui/engine.py:2366:    if _ci_has_blade_heart_payload(ci):
llocg_ui/engine.py:2792:                or (group2 and _ci_matches_group_or_unit(ci, group2) and _ci_has_blade_heart_payload(ci))
llocg_ui/engine.py:5631:            is_no_bh = bool(ci_disc and not _ci_has_blade_heart_payload(ci_disc))
llocg_ui/engine.py:6374:                for attr in ('base_hearts', 'blade_hearts'):
llocg_ui/engine.py:6382:                counts = getattr(ci0, 'required_hearts', {}) or {}
llocg_ui/engine.py:6771:        req = dict(getattr(ci_live, 'required_hearts', {}) or {})
llocg_ui/engine.py:6950:        req = dict(getattr(ci_live, 'required_hearts', {}) or {})
llocg_ui/engine.py:7629:        req = dict(getattr(ci_live, 'required_hearts', {}) or {})
llocg_ui/engine.py:7983:        if ci_top and _is_member_ci(ci_top) and not _ci_has_blade_heart_payload(ci_top):
llocg_ui/engine.py:8175:            for mp in (getattr(ci2, 'base_hearts', {}) or {}, getattr(ci2, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:8413:            for mp in (getattr(ci2, 'base_hearts', {}) or {}, getattr(ci2, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:9008:            if not _ci_has_blade_heart_payload(ci0):
llocg_ui/engine.py:11683:                raw = str(getattr(ci, 'blade_heart_raw', '') or '')
llocg_ui/engine.py:11687:                tags = str(getattr(ci, 'blade_heart_tags_json', '') or '')
llocg_ui/engine.py:11701:    Some card DB exports leave ``blade_heart_tags_json`` empty even when
llocg_ui/engine.py:11702:    ``blade_heart_raw`` contains tokens such as ``<ドロー+1>``.  Rule processing
llocg_ui/engine.py:11710:        tag_n = int(_count_draw_icons(getattr(ci, 'blade_heart_tags_json', '') or '') or 0)
llocg_ui/engine.py:11715:        raw = _normalize_icon_token_text(str(getattr(ci, 'blade_heart_raw', '') or ''))
llocg_ui/engine.py:11748:            raw = str(getattr(ci, 'blade_heart_raw', '') or '')
llocg_ui/engine.py:11969:            if ci is not None and not _ci_has_blade_heart_payload(ci):
llocg_ui/engine.py:12273:                for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:12283:                for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:12319:            for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:12326:            for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:12352:        for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:13336:            if _ci_blade_heart_has_tag(ci, '<スコア+1>'):
llocg_ui/engine.py:13366:        if _ci_blade_heart_has_tag(ci, tag):
llocg_ui/engine.py:13383:        if _ci_blade_heart_has_tag(ci, tag):
llocg_ui/engine.py:13387:def _ci_blade_heart_score_icon_bonus(ci: Optional[CardInfo]) -> int:
llocg_ui/engine.py:13394:        txt = _ci_blade_heart_raw_text(ci)
llocg_ui/engine.py:13413:            total += int(_ci_blade_heart_score_icon_bonus(ci) or 0)
llocg_ui/engine.py:13721:def _has_body_always_2member_blade_heart(ci: Optional[CardInfo]) -> bool:
llocg_ui/engine.py:13960:        if has_exactly2 and _has_body_always_2member_blade_heart(c):
llocg_ui/engine.py:14134:def owned_base_hearts(gs: GameState, cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
llocg_ui/engine.py:14149:            orig_total = sum(int(v) for v in (c.base_hearts or {}).values())
llocg_ui/engine.py:14153:            for k, v in (c.base_hearts or {}).items():
llocg_ui/engine.py:14160:        if has_exactly2 and _has_body_always_2member_blade_heart(c):
llocg_ui/engine.py:14223:        for k, v in (c.blade_hearts or {}).items():
llocg_ui/engine.py:14229:            txt = str(getattr(c, 'blade_heart_tags_json', '') or '')
llocg_ui/engine.py:14235:            # blade_hearts and blade_heart_tags_json.  Count it once per card.
llocg_ui/engine.py:14469:        req = _effective_live_required_hearts(cn, c, globals().get('_CURRENT_GS_FOR_ATTEMPT'), cards_db, set_idx=_set_idx)
llocg_ui/engine.py:14485:        reqs.append((cn, _set_idx, _effective_live_required_hearts(cn, ci, globals().get('_CURRENT_GS_FOR_ATTEMPT'), cards_db, set_idx=_set_idx)))
llocg_ui/engine.py:14944:        for k, v in ((getattr(ci, 'base_hearts', None) or {}) or {}).items():
llocg_ui/engine.py:17858:            if _ci_blade_heart_has_tag(ci2, tag):
llocg_ui/engine.py:17963:        is_no_bh_member = bool(ci_top and _is_member_ci(ci_top) and not _ci_has_blade_heart_payload(ci_top))
llocg_ui/engine.py:20598:            req = dict(getattr(ci, 'required_hearts', {}) or {})
llocg_ui/engine.py:20610:        for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
llocg_ui/engine.py:20676:def _effective_live_required_hearts(cn_live, ci, gs: GameState, cards_db: Optional[Dict[str, CardInfo]] = None, set_idx: Optional[int] = None) -> Dict[str, int]:
llocg_ui/engine.py:20677:    req = dict((getattr(ci, 'required_hearts', {}) if ci else {}) or {})
llocg_ui/engine.py:20807:        for k, v in ((getattr(ci, 'base_hearts', None) or {}) or {}).items():
llocg_ui/engine.py:20842:def _ci_blade_heart_raw_text(ci: Optional[CardInfo]) -> str:
llocg_ui/engine.py:20846:    raw = str(getattr(ci, 'blade_heart_raw', '') or '').strip()
llocg_ui/engine.py:20850:        tags = _parse_tags_json(str(getattr(ci, 'blade_heart_tags_json', '') or '[]'))
llocg_ui/engine.py:20855:        for k, v in (getattr(ci, 'blade_hearts', {}) or {}).items():
llocg_ui/engine.py:20864:def _ci_has_blade_heart_payload(ci: Optional[CardInfo]) -> bool:
llocg_ui/engine.py:20865:    txt = _ci_blade_heart_raw_text(ci)
llocg_ui/engine.py:20873:def _ci_blade_heart_has_tag(ci: Optional[CardInfo], tag_text: str) -> bool:
llocg_ui/engine.py:20877:    txt = _ci_blade_heart_raw_text(ci)
llocg_ui/engine.py:20888:        for k, v in (getattr(ci, 'base_hearts', {}) or {}).items():
llocg_ui/engine.py:20893:    raw = _normalize_icon_token_text(str(getattr(ci, 'base_hearts_raw', '') or ''))
llocg_ui/engine.py:20917:        if _ci_blade_heart_has_tag(ci, tag):
llocg_ui/engine.py:21009:def _card_has_blade_heart(ci: Optional[CardInfo]) -> bool:
llocg_ui/engine.py:21010:    return _ci_has_blade_heart_payload(ci)
llocg_ui/engine.py:21020:        if not _ci_has_blade_heart_payload(ci):
llocg_ui/engine.py:21033:        if not _ci_has_blade_heart_payload(ci):
llocg_ui/engine.py:21049:        txt = _ci_blade_heart_raw_text(ci)
llocg_ui/engine.py:21170:                        if _ci and _ci_has_blade_heart_payload(_ci):
llocg_ui/engine.py:21271:                        if _ci_blade_heart_has_tag(ci2, '<スコア+1>'):
llocg_ui/engine.py:21763:        req = _effective_live_required_hearts(cn, ci, gs, cards_db, set_idx=set_idx)
llocg_ui/engine.py:21783:    base_hearts: Dict[str, int],
llocg_ui/engine.py:21806:        original_req = dict((getattr(ci, 'required_hearts', {}) if ci else {}) or {})
llocg_ui/engine.py:21807:        effective_req = _effective_live_required_hearts(cn, ci, gs, cards_db, set_idx=set_idx)
llocg_ui/engine.py:21842:    stage_full = _live_attempt_full_heart_counts(base_hearts, include_all=True)
llocg_ui/engine.py:21865:            'required_hearts_total': {
llocg_ui/engine.py:21964:    base = owned_base_hearts(gs, cards_db)
llocg_ui/engine.py:21984:            req = _effective_live_required_hearts(cn, c, gs, cards_db, set_idx=_set_idx)
llocg_ui/engine.py:21996:            req = _effective_live_required_hearts(cn, c, gs, cards_db, set_idx=_set_idx)
llocg_ui/engine.py:22014:                    req = _effective_live_required_hearts(cn, c, gs, cards_db, set_idx=_set_idx)
llocg_ui/engine.py:22070:            base_hearts=base,
llocg_ui/engine.py:24114:                    if ci0 and _is_member_ci(ci0) and not _ci_has_blade_heart_payload(ci0):
llocg_ui/engine.py:25611:        if wait_if_bh and _ci_has_blade_heart_payload(ci_pick):
llocg_ui/server.py:118:    return _parse_yell_heart_counts_from_raw(getattr(ci, 'blade_heart_raw', '') or '')
llocg_ui/server.py:124:    tags = str(getattr(ci, 'blade_heart_tags_json', '') or '').strip()
llocg_ui/server.py:130:        raw_n = int(_sum_named_icon_bonus_from_raw(getattr(ci, 'blade_heart_raw', '') or '', 'ドロー') or 0)
llocg_ui/server.py:139:    return _sum_named_icon_bonus_from_raw(getattr(ci, 'blade_heart_raw', '') or '', 'スコア')
llocg_ui/server.py:1838:        from .engine import _compute_attempt_score_breakdown, _effective_live_required_hearts, _ordered_heart_counts
llocg_ui/server.py:1860:                    base_req = dict((getattr(ci0, 'required_hearts', {}) if ci0 else {}) or {})
llocg_ui/server.py:1861:                    eff_req = _effective_live_required_hearts(str(r.get('cn', '') or ''), ci0, self.gs, self.cards_db, set_idx=idx)
llocg_ui/server.py:2349:                bh = getattr(ci, 'base_hearts', None) or {}
llocg_ui/server.py:2354:            required_hearts = {}
llocg_ui/server.py:2356:                rh = getattr(ci, 'required_hearts', None) or {}
llocg_ui/server.py:2357:                required_hearts = _ordered_heart_counts({k: v for k, v in rh.items() if v and int(v) > 0})
llocg_ui/server.py:2375:                "required_hearts": required_hearts,
llocg_ui/server.py:3205:      if(info.required_hearts && Object.keys(info.required_hearts).length){
llocg_ui/server.py:3207:        const rStr = '必要: ' + orderedHeartEntries(info.required_hearts).map(([k,v])=>`${jpMap[k]||k}×${v}`).join(' ');
llocg_ui/server.py:5575:    const reqTotal = mkCounts(summary.required_hearts_total);
llocg_ui/effects/helpers.py:209:            req = getattr(info, 'required_hearts', None)
llocg_ui/effects/helpers.py:211:                req = info.get('required_hearts')
llocg_ui/effects/helpers.py:238:            base = getattr(info, 'base_hearts', None)
llocg_ui/effects/helpers.py:240:                base = info.get('base_hearts')
llocg_ui/effects/helpers.py:653:def _card_required_hearts(card: Any, cards_db: Dict[str, Any]) -> Dict[str, int]:
llocg_ui/effects/helpers.py:657:            d = getattr(info, 'required_hearts', None)
llocg_ui/effects/helpers.py:659:                d = info.get('required_hearts')
llocg_ui/effects/helpers.py:674:            req = _card_required_hearts(card, cards_db)
llocg_ui/effects/green_search.py:92:                req = _card_required_hearts(card, cards_db)
llocg_ui/db.py:49:def _hearts_from_counts_json(counts_json: str) -> Dict[str, int]:
llocg_ui/db.py:50:    if not counts_json:
llocg_ui/db.py:53:        d = json.loads(counts_json)
llocg_ui/db.py:86:    only trusted *_counts_json, so LIVE required hearts could become req={}.  This
llocg_ui/db.py:196:def _looks_like_live_payload(required_hearts: Dict[str, int], score: int, cost: int = 0, blade: int = 0, base_hearts: Optional[Dict[str, int]] = No
```
