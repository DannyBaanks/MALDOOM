# QUINE_OUTWARD_V0 — AUDIT

Date: 2026-09-02 (ISO)
Repo: `DannyBaanks/MALDOOM`
Strategy: exploit existing Malbolge structure ("quine outward"), NOT blind
opcode brute-force. This document records what exists, what each piece does,
what we reuse, and what is missing.

## Goal

Extract a minimal *regeneration/state primitive* from real Classic Malbolge
quine dynamics, make it composable, lift it to a macrocell, and ultimately a
tiny state register for MALDOOM. Every claim is validated against the real
Classic VM. No CA equivalence is asserted — `MALBOLGE_MEMORY_AS_CA_MODEL` is an
experimental model, not a theorem.

## 1. Files found — MALDOOM (this repo)

| Path | Role | Reuse? |
|---|---|---|
| `vendor/malbolge/malbolge.py` | Faithful Classic Malbolge 59049-cell interpreter (crazy, encryption, pointers, I/O). Vendored in-repo; no external dependency. | REUSE (canonical interpreter for all phases) |
| `vendor/quines/quine_lutter.malbolge` | The Lutter Malbolge quine (study specimen), vendored in-repo with provenance. | REUSE (Fase 1 specimen) |
| `vendor/classic_synthesis/autobolge/vm.zig` | Exact Classic 59049 executor (Zig) — local search substrate | REUSE for any Zig search |
| `vendor/classic_synthesis/{branch,stateful,long,state_compare}_search.zig` | Local opcode searchers (P2/P4/P5f1) — honest negatives on 8-opcode grammar len<=7 | Keep as negative controls; not first strategy |
| `vendor/classic/gost.exe` / `oracle.py` | Pinned Classic interpreters (P1/P3 controls), self-contained | REUSE as cross-check for real-VM parity |
| `vendor/classic_synthesis/malpad/truth_machine.mal` | Verified non-echo branch/halt seed (170 chars) | REUSE as small real stateful specimen |
| `evidence/CLASSIC_ANCHOR_SMOKE_V1/P5_STATE_CROSS_READ/` | P5f1 cross-read-state exhaustive negative | Control/context |
| `docs/{MALBODOOM_CLASSIC_DESIGN,CLASSIC_CHECKPOINTS}.md` | MBD1A anchor + 59049 budget contract | Design contract |

## 2. Reused / vendored machinery

The experiment originally needed a Classic Malbolge interpreter and the quine.
Both are now vendored in-repo (see `vendor/malbolge/PROVENANCE.md`) so a clean
clone is self-contained:
- `vendor/malbolge/malbolge.py` — the faithful interpreter (public Malbolge
  semantics; Iizawa 2005 / malbolge.c).
- `vendor/quines/quine_lutter.malbolge` — the quine specimen with provenance.

No private/external tree is required at runtime.

## 3. Known prior observations (do NOT re-derive, but VERIFY)

From the quine README/analysis recorded in this repo:

- quine_lutter: 69,547,437 steps HALTED; 27,250 cells visited; output 59,852 B
  (= source file size → self-replicating); opcode mix NOP 49% / DLOAD 24% /
  ROT 15% / CRAZY 12%; dominant working c≈29357, d≈29454 during output loop.
- "29516 + 29516 = 59032": the quine_4d family (two 29,516-char halves).
- Prior "regeneration/odometer" hypothesis: a region cycles (read cells between
  OUTs) — candidate for a persistent signature.
- Lutter quine is fully robust to representation mutation (all Malbolge
  variants immune to whitespace/comments).

These are prior-art context. Fase 1 re-derives the mechanism from the real
source rather than trusting the box.

## 4. What we reuse

1. `vendor/malbolge/malbolge.py` as the **faithful VM** (real crazy,
   encryption, pointers, memory mutation, I/O). No invented simulation.
2. `vendor/quines/quine_lutter.malbolge` as the **real regeneration specimen**.
3. `vendor/classic_synthesis/malpad/truth_machine.mal` as the **small real
   stateful control**.
4. `vendor/classic/{gost,oracle}` as cross-check interpreters for VM parity.

## 5. What is MISSING (gap we must build)

- A per-step **memory snapshot tool** (which cells read/written, by opcode) for
  the quine — the `on_step` hook of the vendored interpreter gives this.
- An explicit **cell-region classifier** (code / data / workspace / output
  source / self-encryption support) driven by *observed* access patterns.
- A **discrete-ring model harness** treating memory evolution under
  `crazy(mem[i-1],mem[i-2])` + self-encryption, searching *configurations*
  (seeds/regions) for attractors/fixed points/cycles — not programs.
- Duplication / interference / seam / macrocell / regen / input experiments.

## 6. Not duplicated

We do NOT write another Malbolge interpreter (one faithful vendored Python
exists) and we do NOT re-run the blind 8-opcode searchers as a first strategy.

## Verdicts (start)

QUINE_MECHANISM_EXTRACTED = NOT_DEMONSTRATED (pending Fase 1)
DISTINGUISHABLE_CELLULAR_STATE = NOT_DEMONSTRATED (pending Fase 3)
TWO_PRIMITIVES_COEXIST = NOT_DEMONSTRATED (pending Fase 4)
SEAM_PRESERVES_BEHAVIOR = NOT_DEMONSTRATED (pending Fase 5)
MACROCELL_LIFTING = NOT_DEMONSTRATED (pending Fase 6)
REGENERATION_AFTER_DAMAGE = NOT_DEMONSTRATED (pending Fase 7)
INPUT_TO_PERSISTENT_STATE = NOT_DEMONSTRATED (pending Fase 8)
CLASSIC_VM_PARITY = NOT_DEMONSTRATED (pending Fase 9)
MALDOOM_STATE_PRIMITIVE = NOT_DEMONSTRATED (pending Fase 10)