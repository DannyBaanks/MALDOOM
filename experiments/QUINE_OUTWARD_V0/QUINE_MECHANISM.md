# QUINE_OUTWARD_V0 — QUINE_MECHANISM (Fase 1)

Date: 2026-09-02
Specimen: `vendor/quines/quine_lutter.malbolge` (vendored in-repo)
Clean source: 59,032 chars; SHA256(clean)=`6812b7c10679f571887e84238d02ed1c2e0b4f013b8299a60f9ff5e3e9162543`
SHA256(file)=`DCA8476F8B70C8462C32F661F63C5F8B1AD6C33946B3C7A9A35186C824117D98`
Interpreter: vendored `vendor/malbolge/malbolge.py` (faithful VM). Tools:
`src/regions.py`, `src/mechanism.py`, `src/odometer.py`, `src/src_pointer.py`.

## How the quine actually regenerates (OBSERVED, not assumed)

Run window = 300,000 steps (the output loop is periodic; full run is 69.5M).

### 1. Two complementary regions (answers Q4/Q5)

- **Region A — the SOURCE (data)**: cells `29516 .. ~58999`. These hold the
  program's own bytes. Read sequentially, one cell per emitted byte.
- **Region B — the EXECUTING code**: cells `~29200 .. 29505`
  (`29201` executed 32,215×, `29400..29404` 8,341× each). This block owns the
  loop that advances the source cursor and drives OUT.
- **Low workspace**: cell `154` holds a fixed base value `29509` (a constant
  data register), read/written heavily but constant at OUT time.

So the quine is NOT one homogeneous blob: it is a **reader (B) + a source
tape (A)**. The source is at `29516+k`; code lives just below it. This is the
"two-region complementarity" we hypothesized.

### 2. The cursor / odometer (answers Q1/Q3/Q6)

Every emitted byte is loaded by **opcode 62 (CRAZY)** from a cell whose index
advances by exactly 1 per OUT:

```
OUT#   a_src(op, cell, value)
  1    (62, 29516, 184)
  2    (62, 29517, 220)
  3    (62, 29518, 73)
  4    (62, 29519, 46)
  ...
 36    (62, 29551, 57)
 37    (62, 29552, 225)
```

- The **source cursor** is a data pointer that walks the tape `29516 → …`.
- `a` (the accumulator) is set by `op62` to `crazy(a, mem[d])`, i.e. `a` is the
  **moving data register**.
- At the OUT instant `d=29454, memd=124` fixed — that is a *staging* cell; the
  actual byte came from `29516+k` a few steps earlier via op62.

### 3. Periodic output loop (answers Q3)

OUT intervals are dominated by `1137` (×115), `1217` (×52), `1139` (×32),
`1297` (×17) — i.e. the loop is quasi-periodic, not fixed-step. The first OUT
is at step 28,316.

### 4. Which cells are causally necessary (Q5/Q6/Q7)

- Code block B is necessary (it is the controller).
- The source tape A is the *payload*: perturbing a tape cell changes that
  emitted byte (propagates to output) but the loop continues.
- Cell `154=29509` is a fixed base constant; its value at OUT does not track
  the output (constant), so it is a workspace constant, not the cursor.

## The extracted REGENERATION PRIMITIVE (candidate unit)

```
READER(d):  a = crazy(a, mem[d]);  d = d + step   # advance source cursor
```

This is a **sequential stateful reader**: `d` carries state across reads and
`a` is the moving value. It is exactly the "persistent state between reads"
that P5 could not find by blind 8-opcode search — here it *exists* in the real
quine, driven by the code block, reading a long tape.

## Candidacy for the CA model (Fase 2)

The tape read `mem[29516+k]` is a **1-D ordered scan**. If we treat the tape
region as a ring and the cursor as a travelling position, the dynamics is a
simple moving read-head over a static-ish tape — a candidate configuration for
attractor/cycle analysis. We will model this explicitly as
`MALBOLGE_MEMORY_AS_CA_MODEL` (experimental model, NOT an assertion that
"Malbolge IS a CA").

## Verdict (this phase)

QUINE_MECHANISM_EXTRACTED = DEMONSTRATED
- The reader/tape two-region mechanism and the advancing source cursor are
  observed on the real VM with reproducible hashes/tools.

Remaining honest caveats:
- This is the mechanism of *this* quine, not proof that the primitive is
  portable or composable yet (Fases 3-6 test that).
- No claim that crazy is random; it is deterministic and tritwise.