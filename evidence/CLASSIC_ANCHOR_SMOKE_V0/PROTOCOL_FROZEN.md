# PROTOCOL_FROZEN — Classic Anchor Smoke V0

**Fro frozen 2026-09-01, based on 424fcc8 baseline**

## Goal

Prove stateful computation across **3+ completely fresh Classic Malbolge VMs** (59049, standard interpreter, no memory enlargement) linked only by **self-generated opaque continuation code** (`MBD1-…`).

## Managed Memory Model (within 59049)

- Classic memory 59049, Harvard? No — Malbolge self-modifies.
- Define `HIGH_WATER = after N inputs` (managed, not last cell). Reserve ensures encoder fits.
- This smoke uses `N=2` inputs per epoch for demonstration (small working state, easy to brute-force).

## Anchor Format (Versioned, Opaque to Host)

```
MBD1-<epoch>-<logical>-<acc>
```

Example: `MBD1-0-1-65` (epoch 0, logical 1, acc 65)

- `version = MBD1`
- `epoch` = local VM count
- `logical` = total steps across epochs
- `acc` = accumulator (sum of inputs mod 256, stored as decimal string)
- Integrity: simple checksum `sum(bytes) % 256` appended as `*<chk>`? For smoke we use no checksum yet; corruption test will flip a payload trit and expect Malbolge decoder to reject via `branch` failure (see below).

All fields are **encoded/decoded inside Classic Malbolge** via `crazy(K)` chains. Host is dumb pipe.

## Lifecycle

```
VM0 (fresh, no anchor) — input 'A' (65)
  → acc=65, logical=1, local=1
  → local < HIGH_WATER (2) → no anchor, need second input
  VM0 reads 'B' (66) → acc=131, logical=2, local=2 → HIGH_WATER reached
    → canonicalize (acc 131 fits)
    → serialize → output "MBD1-1-2-131\n" → HALT
  PID 100 dies, VM memory discarded

VM1 (fresh) — receives "MBD1-1-2-131\n" as anchor on stdin, then input 'C' (67)
  → decode anchor (epoch 1, logical 2, acc 131) via crazy K's inside Malbolge
  → acc=198, logical=3, local=1 → no anchor yet
  VM1 reads 'D' (68) → acc=266%256=10, logical=4, local=2 → HIGH_WATER
    → output "MBD1-2-4-10\n" → HALT
  PID 200 dies

VM2 (fresh) — receives "MBD1-2-4-10\n" + input 'E' (69)
  → acc=79, logical=5
  → etc. across 3 epochs = 6 inputs total

Reference (Python) does same arithmetic: `acc = (acc + ord(c)) % 256` and `logical++`.

## Killer Test

Inputs are runtime-unknown (e.g., sequence `A,B,C,D,E,F` vs `X,Y,Z`). Same artifact must produce correct anchors for any input without recompilation. No per-answer generation.

## Verification

- `state_hash_reference = hash((epoch,logical,acc))` via Python
- `state_hash_anchored = hash(anchor_decoded)` via Malbolge VM output
- Must match at each boundary. Host only compares hashes, never computes acc.

## Corruption Test

Flip one payload char in anchor (e.g., `131` → `132`), feed to fresh VM. Malbolge decoder's `branch` should take reject path (output `REJECT\n` vs `ACCEPT`). Host does not detect.

## Cross-Interpreter

Anchor emitted by `gost.exe` must resume on `oracle.py` and vice versa, both on 59049 Classic semantics.

## Files

- `program.mal` — fixed Classic artifact (generated before runtime, SHA pinned)
- `anchors/*.anchor` — opaque codes
- `run.json` — per-epoch PID, anchor hash, input hash, state hash

