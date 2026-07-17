# Empty String As Zero Watch Item

- status: `ALLOWED_WITH_MONITORING`
- pending kind: `opponent_wait_notify`
- resolver: `llocg_ui/engine.py` `cmd_resolve_pending`, branch `if kind == 'opponent_wait_notify'`
- code behavior: `int(str(choice_str or '0').strip())` makes an empty string resolve as `0`.
- UI reachability: normal UI buttons send explicit numeric options `0`, `1`, `2`, `3`; empty string is not the intended UI path.
- legality: `0` is legal for the current aggregate opponent-wait input model.
- reuse risk: monitor if this resolver is reused for a future 1-or-more mandatory count.
- future review triggers: empty UI submission, transport omission hiding user choice, or use on a count where `0` is not legal.
