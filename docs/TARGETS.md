# Targets — A vs B

## TARGET_A — Malbolge Unshackled (candidate for full Doom)

- Memory: unbounded trits (3-adic integers, first trit repeats), dynamic rotation width ≥10, grows when `j` widens `D` beyond half width.
- I/O: Unicode codepoints, `...21` = newline (auto-converted), `...22` = EOF.
- Computational class: **Turing-complete** (proven via brainfuck interpreter `lutter.cc/unshackled/brainfuck.html` + MalbolgeLisp 2020 Lisp interpreter in Unshackled).
- File extension: `.mu`.
- VM: `Unshackled.c` (C, fast, `UINTMAX_MAX` width) or `Unshackled.hs` (Haskell reference). `Unshackled-20.c` fixed 20 trits is faster for low-width programs.
- Claim scope: everything up to `M7 PLAYABLE` is **in scope** — but only after evidence.

## TARGET_B — Classic Malbolge (59049, constrained)

- Memory: exactly 59049 words (3¹⁰), init `mem[i]=crazy(mem[i-1],mem[i-2])`, execution self-modifies via `XLAT1[(mem[c]-33+c)%94]` / `XLAT2`.
- I/O: `mod 256`.
- Computational class: **Bounded-storage machine, NOT Turing-complete** (Esolang + Wikipedia). Variants `Malbolge20` (20 trits, ~3.4GB) or `Malbolge-T` are theoretical.
- File extension: `.mal`.
- VM: `gost.c` / `malbolge-oracle` / `Malbolge-Engine` (see `DannyBaanks/MalboGost`).
- Claim scope: `FULL_DOOM = NOT_DEMONSTRATED` until memory problem solved honestly. Valid claims: constrained VM, Doom-like demo (subset of state, limited WAD, limited ticks). Must never be marketed as "Doom on Classic Malbolge" with full WAD.

### TARGET_B1 — Classic Single VM

- Exactly one standard finite VM, no continuation.
- `FULL_DOOM = NOT_DEMONSTRATED`.

### TARGET_B2 — MALBODOOM / Classic Anchored Execution

- **NEVER ENLARGE MALBOLGE. MAKE THE COMPUTATION FIT.**
- Each individual VM is **still ordinary Classic Malbolge** (59049, finite, standard interpreter, no hidden RAM).
- Long computation is carried by a **sequence of fresh VMs** linked by **self-generated continuation codes** (`MBD1A-…`). The anchor is opaque data; every epoch executes the same frozen `.mal` artifact, never a host-generated state-specific program.
- VM may halt and a new VM receives the opaque code + new input only. Host is dumb pipe: launch, feed bytes, capture bytes, store opaque code, feed to new VM, present framebuffer.
- Two modes:
  - `ANCHOR_CONTINUE` — exact declared continuation when managed `HIGH_WATER` reached (canonicalize live state, discard reconstructible, serialize, HALT; fresh VM decodes and continues; `epoch_local_step=0`, `logical_total_step` continues).
  - `DEATH_REBIRTH` — at Doom death, `CONTINUE` (exact anchor) vs `REBIRTH` (derive new seed inside Malbolge, discard transient, `epoch_local_step=0`, compact `DEATH CODE`).
- Memory model: managed working region + pre-frozen `HIGH_WATER` threshold + `checkpoint reserve` (encoder/decoder workspace, streaming allowed). `HIGH_WATER` is a Malbolge-owned memory budget, **not** a host timer and not an assumed "59049 step" limit. Malbolge itself decides when to checkpoint, what to save, how to encode.
- Host may **NOT** decide checkpoint timing, inspect/serialize state, compute RNG/gameplay, or keep VM alive between epochs. For verification host may hash, but hash must not influence candidate.
- `SEED_ONLY_RESUME = NOT_DEMONSTRATED` until proven; anchor must contain sufficient state to reproduce declared continuation.
- File extensions: `.mal` (program), anchor opaque text (e.g., `MBD1-…`), max `A_min` measured but not yet optimized.
- Claim scope: `FULL_DOOM = NOT_DEMONSTRATED` until anchor primitive + death/rebirth + Doom mapping all demonstrated. Allowed intermediate: `FRESH_VM_RESUME_DEMONSTRATED`, `MULTI_EPOCH_CLASSIC_EXECUTION_DEMONSTRATED`, etc.

See `docs/CLASSIC_CHECKPOINTS.md` for the frozen password, memory and death-mode contract.

## Why Split Matters

A video showing `M7` on Unshackled **is not** `DOOM_ON_CLASSIC_MALBOLGE`. The README must show the table above prominently. Every `evidence/` dir declares `target: A|B`. Verifier compares only within same target's reference build.

## File Discrimination

- `engine/*.hell` = HeLL assembly (source for LMFAO)
- `engine/*.mu` = assembled Unshackled (TARGET_A)
- `engine/*.mal` = Classic (TARGET_B, via MalboGost future)
- `host/` never generates `.mu` per input for killer test — same artifact for many inputs.
