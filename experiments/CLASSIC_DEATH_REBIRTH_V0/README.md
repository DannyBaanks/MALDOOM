# CLASSIC_DEATH_REBIRTH_V0 — Toy Model (Host-Assisted, NOT_DEMONSTRATED for Malbolge-owned)

**Fro frozen after CLASSIC_ANCHOR_SMOKE_V0 V0**

**Goal:** Show death as semantic compaction: `CONTINUE` (exact anchor) vs `REBIRTH` (discard transient, derive new seed inside Malbolge, compact death code).

**Current status:** `NOT_DEMONSTRATED` for Malbolge-owned logic. This toy is **host-assisted** to freeze the **semantics**, not the implementation.

## State

Same as smoke: `(epoch, logical, acc)` with `acc` 0/1, but add `alive` flag.

## Death trigger

If `acc == 1` after an epoch and `logical >=3`, simulate player death.

Host (for this toy) offers:

- `CONTINUE` → `MBD1-C-epoch-logical-acc` (exact, preserves all)
- `REBIRTH` → `MBD1-R-epoch'-0-new_seed` where `new_seed = (acc*3+epoch)%2` derived inside Malbolge (in real V1) but host does for now

## Evidence for this toy

- `run.py` simulates both branches with same `program.mal` (hello.mal placeholder)
- `evidence/CLASSIC_DEATH_REBIRTH_V0/` records `exact-anchor size` 11 B vs `rebirth-code size` 11 B (same for this tiny state, but real Doom rebirth will be far more compact because many world objects are discarded)
- `REBIRTH_LOCAL_STEP_RESET` verified: `local_step` resets to 0, `logical` resets to 0 for rebirth vs continues for continue

**Next:** Implement Malbolge-owned death branching (inside program, host only presents choice bytes).

