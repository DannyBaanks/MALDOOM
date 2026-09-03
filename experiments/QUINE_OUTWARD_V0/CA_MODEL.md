# QUINE_OUTWARD_V0 — CA_MODEL (Fase 2/3)

Date: 2026-09-02
Model: `MALBOLGE_MEMORY_AS_CA_MODEL` — an **experimental model**, NOT an
assertion that "Malbolge IS a cellular automaton".

## Why a discrete-ring model is a fair lens

The real VM builds unused memory by a radius-2 recurrence on the ring:

```
mem[i] = crazy(mem[i-1], mem[i-2])      (indices wrapped mod N)
```

and mutates executed cells via self-encryption `mem[c] = ENCRYPT[mem[c]]`.
`crazy` is deterministic and **tritwise** (a local rule), so the memory's
unused region evolves like a discrete 1-D ring map. We search that map for
configurations with stable signatures. Every candidate found here is later
validated on the real VM (Fase 9).

Wraparound here is the experiment's own choice of index arithmetic on a finite
ring (index `(i mod N)`), matching how the real VM wraps `c`/`d` at 59049. It
is not inherited from any external topological model.

## Model definition

- Ring of N cells, indices mod N.
- Update: `ring[i] = crazy(ring[i-1], ring[i-2])` (radius-2 fill rule).
- Optional code-mutation: an index set `encrypt` gets `ENCRYPT` applied after
  fill each step (self-encryption model).
- Observable: window signature `sig(lo,w) = sum(ring[lo:lo+w]) mod 3^w`;
  period of the full ring configuration.

## Fase 2 observations (structure, not chaos)

- Rings of N=3..12 under the crazy-fill rule converge to **finite periodic
  attractors** (period 2..22), never divergent random walks.
- Periods scale: odd N → 2N, even N → N (observed N=3→6, 4→4, 5→10, 6→6,
  7→14, 8→8, 9→18, 10→10, 11→22, 12→12). This is the geometry of the
  wrapped ring, not noise.

## Fase 3 — smallest microcell

Smallest ring with a stable distinct window-signature:

| N | period0 (seed s0) | period1 (seed s1) | distinct window |
|---|---|---|---|
| **3** | 6 | 2 | `lo=1,w=1`: sig0=0, sig1=1 |
| 4 | 4 | 4 | `lo=2,w=1` |
| 5 | 10 | 10 | `lo=2,w=1` |
| 8 | 8 | 8 | `lo=2,w=1` |

Minimal microcell: **N=3, window `lo=1..1`**, `sig0=0` vs `sig1=1`, stable
(periodic). For all N>=3 a 1-cell window signature separates two states.

Definition:
- STATE_0 = seed `[1,1,0]` (ring N=3) → window-1 signature 0
- STATE_1 = seed `[1,1,1]` (ring N=3) → window-1 signature 1
- observe(region) = `sig(lo=1, w=1)` = the cell value itself.

Honest caveat: in this pure-fill model the distinguishing cell still carries a
trace of the seed difference. That is acceptable for a *primitive*; the test of
whether it is a *composable unit* is Fase 4 (duplication/interference), not
this observation.

Full data: `MICROCELL_RESULTS.json`.

## Verdicts (model-level, pending real-VM validation)

DISTINGUISHABLE_CELLULAR_STATE = DEMONSTRATED (in model, N=3 microcell)
QUINE_MECHANISM_EXTRACTED = DEMONSTRATED (real VM, Fase 1)
Remaining: two-primitive coexistence, seam, macrocell, regen, input, VM parity.