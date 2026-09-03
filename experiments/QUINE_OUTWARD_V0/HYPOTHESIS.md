# QUINE_OUTWARD_V0 — HYPOTHESIS (operational, not asserted)

Date: 2026-09-02

## The operating notation

```
A + B -> C
C(A) + C(B) -> C(C)
microstructure -> macrostructure -> superstructure -> machine
```

This is NOT assumed mathematically correct. It is a **search heuristic**: look
for structure that already exists in Malbolge and lift it, instead of treating
the memory as pseudo-random ternary.

## Concrete hypotheses under test

- H1 (regeneration primitive): the Lutter quine contains a sub-mechanism that
  *regenerates* a region from other regions — a "repair" that is not just the
  whole-quine box. If extractable, it is a unit that can be damaged and
  restored.
- H2 (distinguishable state): a configuration/region has a signature
  (checksum, sum mod 3^k, period, attractor id) that is observable from the
  state itself, not from what we injected.
- H3 (composability): two such primitives can coexist (separate / adjacent /
  shared boundary / offset) without one destroying the other; else a SEAM
  region S restores `signature(A|S|B)`.
- H4 (lifting): the pair C=compose(A,B) behaves as a unit whose own signature
  survives a second lifting (C(A)+C(B)->C(C)).
- H5 (input→persistent state): a perturbation derived from input (0 vs 1)
  leads to two persistent distinguishable attractors.

## Falsification discipline

- A negative at any phase is recorded, not hidden.
- If two primitives cannot coexist in any tested configuration, H3 fails *in
  that form* — we say so.
- "Malbolge IS a CA" is NOT claimed. Only `MALBOLGE_MEMORY_AS_CA_MODEL` is used
  as a model to *find* candidate configurations, which are then validated on
  the real VM.
- A fixed-output generator is not a "runtime".

## What is NOT a hypothesis

- Not brute-force first.
- Not assuming crazy is random (it is deterministic, tritwise).
- Not declaring P5 solved because attractors exist.
- Not declaring stateful until input -> persistence -> re-read is shown on the
  real VM.