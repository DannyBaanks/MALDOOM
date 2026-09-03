# MALDOOM

> A research project attempting to build progressively richer interactive
> state inside Classic Malbolge (3^10 / 59049-cell memory).

The project treats Malbolge itself as the computational substrate. Host code
may run experiments, feed input, collect traces and render evidence, but it
must not implement the game semantics being claimed.

**Evidence before narrative.**

---

## First Law

$$\boxed{\text{IF THE HOST COMPUTES A DOOM GAMEPLAY TRANSITION, THE DEMONSTRATION FAILS.}}$$

The host may **only** do I/O: present a framebuffer, transport keyboard input,
keep timing, and move WAD bytes (no semantic WAD parsing). It may NOT compute
gameplay, position, AI, collisions, RNG, or produce `S_t → S_{t+1}`.
`grep doomgeneric_Tick host/` must return 0 hits, or the host stole the
computation.

---

## Why this exists

Doom has run on calculators, pregnancy tests and potatoes. Can it be made to
run *on* Malbolge semantics — with the host reduced to a dumb framebuffer — and
not merely *print* "Doom" from Malbolge?

Classic Malbolge is **bounded-storage** (59049 cells) and famously hostile: the
code self-encrypts as it runs, `crazy` is a tritwise operation, and pointers
`c`/`d` advance each step. Building even a tiny stateful unit inside it is the
hard problem. That is the actual research question.

---

## Classic Malbolge constraints

- Memory: exactly `3^10 = 59049` cells. Unused cells are filled by
  `mem[i] = crazy(mem[i-1], mem[i-2])`.
- Self-encryption: each executed code cell is rewritten via the encryption
  table.
- `crazy(a,b)`: deterministic, tritwise (ternary) operation.
- Pointers: `c` (code) and `d` (data) advance by 1 each step, wrapping mod 59049.
- I/O: `mod 256`. Not Turing-complete (bounded storage).

`MALBOLGE_MEMORY_AS_CA_MODEL` is an *experimental model* used in the quine
experiment to study observed memory dynamics; it is **not** a claim that
"Malbolge is a cellular automaton".

---

## Milestone ladder

We stop at the first `NOT_DEMONSTRATED`; no skipping.

```
M0  Malbolge backend executes arbitrary EIR arithmetic/control flow
M1  WAD header parsed inside Malbolge semantics
M2  Doom game state S_0 initializes inside
M3  one deterministic Doom tick  H(S_{t+1}) == H(S_t)_C
M4  player input changes game state
M5  one correct framebuffer (pixel hash vs C)
M6  repeated ticks without reset/recompilation
M7  E1M1 technically playable
```

Two targets, never conflated:

| Target | Variant | Memory | Status |
|---|---|---|---|
| TARGET_A | Malbolge Unshackled | unbounded, Turing-complete | full-Doom candidate |
| TARGET_B | Classic Malbolge | 59049 fixed, bounded | `FULL_DOOM = NOT_DEMONSTRATED` |

---

## Quine-outward experiment

`experiments/QUINE_OUTWARD_V0/` studies the real Lutter Malbolge quine
(vendored at `vendor/quines/`, interpreter at `vendor/malbolge/`) to extract a
composable state primitive:

1. **Mechanism** — the quine is a *reader + source tape*: code block ~29.2–29.5k
   reads its own bytes at `29516+k` sequentially; each tape cell maps to exactly
   one output byte (causal, verified by perturbation).
2. **Discrete-ring model** — a finite wrapped ring under the real `crazy` fill
   rule; searches *configurations* (not programs) for stable, distinguishable
   signatures.
3. **Microcell** — smallest ring (N=3) whose window signature distinguishes two
   states stably.
4. **Composition** — two microcells destroy each other unless separated by a
   seam; a 1-cell seam preserves both. Lifting to a macrocell works at one
   specific inter-unit gap.
5. **Regeneration** — passive fill does not repair (3/8 single-cell, 0/8
   double-cell). Real regeneration must come from directed code rewrites.
6. **Input → state** — a 0/1 input bit yields distinguishable signatures at
   long horizon (1000 steps) but not short (100 steps).
7. **VM parity** — the discrete-ring model matches the real VM in the passive
   fill region (12/13, one fill-boundary exception).

Full honest verdicts in `experiments/QUINE_OUTWARD_V0/SUMMARY.md`.

---

## Demonstrated

- Real quine reader/tape mechanism (on the real VM, perturbation-verified).
- Passive-fill rule parity between the ring model and the real VM (12/13).
- Smallest distinguishable microcell in the model (N=3).
- A 1-cell seam that lets two microcells coexist in the model.
- Macrocell lifting at one inter-unit gap in the model.

## Not demonstrated

- Robust regeneration after damage (passive fill).
- Input → persistent state at short horizon.
- `FULL_DOOM_ON_CLASSIC_MALBOLGE`.
- Any "Malbolge is a cellular automaton" equivalence.

---

## Reproduce

From a clean clone (self-contained; no external/private dependency):

```bash
# vendored interpreter self-test (Wikipedia Hello World -> HALTED)
py vendor/malbolge/malbolge.py

# quine-outward experiments (from experiments/QUINE_OUTWARD_V0/src/)
py microcell.py        # smallest distinguishable microcell
py seam.py             # minimal seam for coexistence
py macrocell.py        # lifting
py regen.py            # regeneration / basin
py input_state.py      # input -> persistent state
py vm_parity.py        # model vs real VM parity (passive region)
```

Each script writes its evidence JSON next to it (or prints). Tools run with
`py <script>.py` from the `src/` directory so the vendored `_common.py` resolves
the repo root.

---

## Evidence

- `experiments/QUINE_OUTWARD_V0/` — docs + results JSON + scripts.
- `evidence/CLASSIC_ANCHOR_SMOKE_V1/` — Classic checkpoint/search evidence
  (P1–P5, honest negatives for cross-read state).
- `evidence/M0*/` — Unshackled/HeLL pipeline evidence.
- `evidence/DOOM_NATIVE_BASELINE/` — native Doom reference runs.

Raw evidence is historical and is never rewritten to fit a narrative.

---

## Limitations

- The quine-outward microcell/macrocell/seam results are **model-level**; they
  are validated against the real VM only in the passive-fill region, not yet as
  a running Classic program.
- No Doom game state has been produced inside Malbolge.
- Classic Malbolge is bounded-storage; `FULL_DOOM` on Classic is not claimed.

---

## References

- `ozkl/doomgeneric` — 5-function porting layer (`DG_Init, DG_DrawFrame,
  DG_SleepMs, DG_GetTicksMs, DG_GetKey`).
- `shinh/elvm` + `shinh/8cc` (eir) — `C → EIR → HeLL` pipeline.
- HeLL / LMFAO — Malbolge/Unshackled assembly and assembler.
- Malbolge Unshackled — `oerjan.nvg.org/esoteric/Unshackled.hs`,
  `lutter.cc/unshackled/`.
- Classic Malbolge — Iizawa (2005) / reference `malbolge.c` (public language).

---

*If the host computes a Doom gameplay transition, the demonstration fails. Not
a slogan — a gate.*