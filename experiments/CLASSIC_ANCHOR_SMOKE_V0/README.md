# CLASSIC_ANCHOR_SMOKE_V0 — Minimal Host-Assisted Multi-Epoch

**Status:** `COMPILER_ASSISTED_CLASSIC_RUNTIME` — host generates anchor, Malbolge does per-epoch transform. `SELF_CHECKPOINT` is `NOT_DEMONSTRATED` (next step is Malbolge-owned checkpoint).

**Goal:** Prove 3+ fresh Classic VMs can be chained via opaque code, with same artifact, runtime inputs, no shared memory.

**Artifact:** `program.mal` — classic Malbolge single-char transform (IN p OUT HALT) where `p` does `crazy(input, K=36)` mapping `'0'→'1', '1'→'2'` etc. For smoke we use `K=36` gives `'0'(48)→'1'(49)?` Actually K=36 gave `33→54` etc. We will generate a `+1` increment program for digits `0..4`.

**Host (for this smoke only):**

- launches `gost.exe program.mal` with `anchor + new_input` as stdin
- captures output (new anchor)
- stores opaque code byte-for-byte
- feeds to new VM
- decides checkpoint after every 1 input (HOST decides). This is **intentionally** `HOST_PARSES_STATE=yes` for this V0. Next V1 will move checkpoint inside Malbolge.

**Why this is still useful:**

- Proves `FRESH_VM_RESUME_DEMONSTRATED` (PID changes, no mmap, no interpreter snapshot)
- Proves `MULTI_EPOCH_CLASSIC_EXECUTION_DEMONSTRATED` (3 epochs, same artifact)
- Proves `CORRUPTED_ANCHOR_REJECTED` can be tested (flip char, Malbolge still outputs but host detects mismatch vs reference)
- Cross-interpreter: same `program.mal` runs on `gost` and `oracle`

**Next:** V1 will replace host anchor generation with Malbolge-owned `HIGH_WATER` and `MBD1-…` format.

