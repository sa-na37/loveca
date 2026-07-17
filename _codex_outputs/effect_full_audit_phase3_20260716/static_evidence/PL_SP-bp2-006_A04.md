# Static Evidence PL!SP-bp2-006#A04

- audit_id: PL!SP-bp2-006#A04
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
- `llocg_ui/effects/stage_triggers.py:7:登場・BODY・leave-stage 近辺の ext apply 正本。`
- `llocg_ui/effects/stage_triggers.py:31:    # PL!HS-bp2-002 村野さやか (登場)`
- `llocg_ui/effects/stage_triggers.py:91:    # PL!HS-bp2-017 徒町小鈴 (登場)`

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
