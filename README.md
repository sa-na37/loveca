# LLOCG Pattern Seeds v1

This folder contains **seed** pattern tables generated from template mining outputs.

## Files
- `cost_patterns_seed_v1.yaml`: cost-clause templates -> suggested ops
- `effect_patterns_seed_v1.yaml`: effect-clause templates -> suggested ops

## Notes
- Some frequent templates are fragments (e.g., `<(ブレード)>` and `を得る。`). These should later be merged at compile time.
- `op=TODO` means manual mapping needed.
- `confidence` is a rough heuristic to prioritize manual review.

## Next step
1) Edit YAML: fill `op/params` for the top ~30 TODOs that occur in your target archetype.
2) Compile cards: map normalized clause templates to ops.
3) Simulate: execute ops in a minimal engine to collect play logs.
