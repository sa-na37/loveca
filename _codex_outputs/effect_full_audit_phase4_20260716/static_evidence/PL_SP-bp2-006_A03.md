# Static Evidence PL!SP-bp2-006#A03

- audit_id: PL!SP-bp2-006#A03
- cardnumber: PL!SP-bp2-006
- cardname: 桜小路きな子
- effect_text: 
- previous_classification: UNREACHABLE_TRIGGER_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- not found

## compiled_db_entry

```json
{}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:3699:    if(kind.includes('enter') || kind.includes('on_enter')) return '登場時';`
- `llocg_ui/server.py:7145:      setRichText(elModalText, pendText || '手札から登場させるメンバーを選んでください。');`
- `llocg_ui/server.py:7667:          choices.push({choice:pos, title:`${posLabel}に登場させる`, body:`メンバーのいない${posLabel}に ${cardDisplayText(cardCn)} を登場させます。`});`
- `llocg_ui/engine.py:50:    {"id": "draw2_discard1_if_entry_from_waiting", "pattern": r"^控え室から登場している場合、カードを(?P<n>\d+)枚引き、手札を(?P<m>\d+)枚控え室に置く。$", "op": "draw_discard_if_entry_origin", "entry_origin": "green"},`
- `llocg_ui/engine.py:51:    {"id": "draw2_discard2_if_entry_not_from_hand", "pattern": r"^このメンバーが手札以外からステージに登場している場合、カードを(?P<n>\d+)枚引き、手札を(?P<m>\d+)枚控え室に置く。$", "op": "draw_discard_if_entry_origin", "entry_origin": "not_hand"},`
- `llocg_ui/engine.py:52:    {"id": "draw_then_discard_unless_baton_from_group", "pattern": r"^カードを(?P<n>\d+)枚引く。その後、このメンバーが『(?P<group>[^』]+)』のメンバーからバトンタッチして登場していないかぎり、手札を(?P<m>\d+)枚控え室に置く。$", "op": "draw_then_discard_unless_baton_from_group"},`

## pending_creation_route

- not found

## resolver_route

- not found

## ui_route

- not found

## reachable_from_runtime

Route candidate exists or text matched, but previous reachable flag is not YES; trigger collection path is not proven

## conflicting_routes

none found in this static pass

- final_classification: NOT_IMPLEMENTED_WITH_EVIDENCE
- confidence: medium
- reason: No card-specific route, no compiled op, and feature-term searches found no matching generic route in inspected runtime files.
