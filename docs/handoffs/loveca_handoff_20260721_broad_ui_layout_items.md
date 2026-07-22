# Loveca handoff 20260721 - broad UI layout items

## Scope

This file is only for broad UI/layout work. Do not mix these items with card-effect runtime acceptance or individual visual confirmation.

## Items

- Global responsive layout and window-resize behavior.
- Large-scale simulator screen composition changes.
- Shared popup/card-list layout redesign that affects many pending kinds at once.
- Public/private window layout restructuring.
- General card image renderer sizing rules if they require changing shared layout contracts rather than a single broken pending view.

## Notes

- The old window-resize/global layout hold in `docs/debug/loveca_debug_commands_20260623.md` belongs here.
- These items should be planned as UI work with browser/screenshot verification across viewport sizes.
- Runtime effects should not be changed merely to satisfy layout concerns.
- If a visual check finds a single broken pending view, fix that pending/UI path directly. Escalate here only when the issue is systemic.

## Suggested verification style

- Run the simulator in a real browser session.
- Capture desktop and narrow viewport screenshots.
- Verify that cards, buttons, popups, counters, and overlays do not overlap.
- Keep findings separate from effect-resolution state diffs.
