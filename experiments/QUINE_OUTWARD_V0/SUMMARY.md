# QUINE_OUTWARD_V0 — SUMMARY

Date: 2026-09-02
Repo: `DannyBaanks/MALDOOM`
Approach: exploit existing Malbolge structure ("quine outward"), NOT blind
opcode brute-force. All model claims validated against the real Classic VM.
`MALBOLGE_MEMORY_AS_CA_MODEL` is an experimental model, not an assertion that
"Malbolge IS a CA".

## Verdicts

```
QUINE_MECHANISM_EXTRACTED        = DEMONSTRATED
DISTINGUISHABLE_CELLULAR_STATE   = DEMONSTRATED   (model, N=3 microcell)
TWO_PRIMITIVES_COEXIST           = DEMONSTRATED   (with SEAM gap)
SEAM_PRESERVES_BEHAVIOR          = DEMONSTRATED   (min gap = 1 cell)
MACROCELL_LIFTING                = DEMONSTRATED   (G2 works; G1/G3/G4 fail)
REGENERATION_AFTER_DAMAGE        = NOT_DEMONSTRATED (passive-fill: 3/8 single, 0/8 double)
INPUT_TO_PERSISTENT_STATE        = PARTIAL        (distinct at 1000 steps, not at 100)
CLASSIC_VM_PARITY                = DEMONSTRATED   (passive region 12/13)
MALDOOM_STATE_PRIMITIVE          = PARTIAL        (mechanism on real VM; robust unit pending)
```

## What was actually found (observed, not interpreted)

### 1. Real quine mechanism (real VM) — QUINE_MECHANISM_EXTRACTED = DEMONSTRATED

The Lutter quine is NOT one homogeneous blob. It is a **reader + source tape**:

- **Region A (tape/source)**: cells `29516..~58999` hold the program's own
  bytes, read sequentially.
- **Region B (executing code)**: cells `~29200..29505` control the loop.
- **Source cursor**: each emitted byte is loaded by op 62 (CRAZY) from
  `29516+k`, advancing by 1 per OUT. `a` is the moving data register.
- **Perturbation causality** (real VM): perturbing tape cell `29516+k` changes
  exactly output byte `k+1` and no others — causal sequential read, no lateral
  propagation.

Specimen: `quine_lutter.malbolge`, clean source 59,032 chars,
SHA256(file)=`DCA8476F...`, SHA256(clean)=`6812b7c1...`.

### 2. Cellular model & microcell — DISTINGUISHABLE_CELLULAR_STATE = DEMONSTRATED (model)

The crazy-fill rule on a ring (N=3..12) converges to finite periodic
attractors (period 2..22), never divergent chaos. Minimal microcell: **N=3,
window `lo=1`**, signature 0 vs 1, stable. (Model-level.)

### 3. Composition — SEAM / COEXIST / MACROCELL

- Two microcells **destruct** when adjacent/shared-boundary; independent only
  with a gap (Fase 4).
- A **SEAM of 1 cell** (zero or mirror padding) preserves both signatures
  (Fase 5). Non-monotonic across gaps (resonances), but a working gap exists.
- **Lifting**: the pair (A|S|B) is a stable unit (macro signature (1,0)
  preserved); two such macrocells coexist at G=2 (Fase 6). G1/G3/G4 fail —
  the lifting is real but not robust to arbitrary separation.

### 4. Regeneration — NOT_DEMONSTRATED (passive fill)

The passive crazy-fill does NOT repair: single-cell damage regenerates only
3/8 positions, double-cell damage 0/8. The fill rule is an *attractor*, not a
*repairer*. Real regeneration (like the quine's) comes from **directed code
rewrites** (self-encryption + crazy on targeted cells), which the passive
model does not capture.

### 5. Input → persistent state — PARTIAL

In the model, input 0 vs 1 as the initial state bit yields distinguishable
signatures at 1000 steps (sig 2 vs 3) but NOT at 100 steps (both 0). There is
a transient collapse before re-divergence — the state register must be read at
the right horizon.

### 6. Model ↔ real VM parity — DEMONSTRATED (passive region)

In the quine's passive fill region `[59032, 59049)`, untouched cells evolve by
exactly `crazy(mem[i-1],mem[i-2])`: 12/13 match; the single violation is the
fill-boundary cell. The model is a faithful projection of the real VM **where
the code is not writing**. The gap: the model omits directed code mutation.

## The honest wall(s)

1. **Passive fill cannot regenerate** (Fase 7). Any regeneration primitive must
   come from directed code rewrites, not the ring map.
2. **Composition is real but fragile**: coexistence requires a specific SEAM
   (gap=1) and lifting requires a specific inter-unit gap (G=2). Not a general
   "any two cells compose".
3. **Input persistence has a horizon**: distinguishable at 1000, not at 100.
   A real state register must define *when* to read.

## What this means for MALDOOM

- The **reader/tape** mechanism of the quine is the strongest real-VM primitive:
  a sequential stateful reader (`a` moving, `d` advancing) — the exact
  "persistent state between reads" that P5 could not find by blind opcode
  search. It exists in the real quine.
- The cellular/seam/macrocell results are **model-level demonstrations** of
  composability and distinguishable state; they are honest intermediate
  evidence, NOT yet a program running in Classic.
- Next concrete step (not done here): take the reader/tape mechanism and build
  a **minimal stateful reader program** on the real VM (Fase 10 target: tiny
  FSM = read bit → persist → re-read → emit), validating input→persistence→read
  end-to-end on gost/oracle.

## Files

- `AUDIT.md`, `HYPOTHESIS.md`, `QUINE_MECHANISM.md`, `CA_MODEL.md`
- `MICROCELL_RESULTS.json`, `DUPLICATION_RESULTS.json`, `SEAM_RESULTS.json`,
  `MACROCELL_RESULTS.json`, `REGEN_RESULTS.json`, `INPUT_STATE_RESULTS.json`,
  `CLASSIC_VM_VALIDATION.json`
- `src/{regions,mechanism,odometer,src_pointer,perturb,ca_model,microcell,
  duplicate,seam,macrocell,regen,input_state,vm_parity}.py`

## Honesty notes

- `MALBOLGE_MEMORY_AS_CA_MODEL` is a model; "Malbolge IS a CA" is not claimed.
- Fixed-output generators are not runtimes.
- P5 is not declared solved; the distinguishable attractors are model-level
  and the input persistence is partial.
- All negatives (regen, G1/G3/G4, 100-step indistinguishability) are recorded.