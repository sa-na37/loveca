# Cleanup Check Method

1. Save `04_resolved.json` after the final pending resolves.
2. Save `05_after_cleanup.json` at the cleanup checkpoint. For non-temporary effects this is the resolved state.
3. Compare pending, temp modifiers, selection state, public/popup residue, and turn-scoped flags.
4. Any remaining pending or temporary field is a cleanup failure unless explicitly expected.
