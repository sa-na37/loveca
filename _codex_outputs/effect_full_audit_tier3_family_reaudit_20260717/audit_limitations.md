# Audit Limitations

- Runtime and DB were not modified.
- Browser UI was not counted as passed for any Tier 3 row in this pass.
- `cleanup_checked=false` where no resolver mutation was reached; this is intentional and prevents false PASS.
- `NOT_IMPLEMENTED_CONFIRMED` remains 0 because the instruction prohibits classifying mere non-reachability as confirmed non-implementation.
- Rows with rule/capability dependency are separated from implementation backlog where appropriate.
