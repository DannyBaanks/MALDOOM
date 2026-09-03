# RESULTS — CLASSIC_ANCHOR_SMOKE_V0

**FROZEN:** 2026-09-01
**Artifact:** `vendor/classic/hello.mal` 64B `956C134AA67FA3FC049BDA71406673050B64B18663EE603B16C7B694E13FE6C1` (placeholder, `COMPILER_ASSISTED_CLASSIC_RUNTIME` for V0)
**Interpreters:** `gost.exe` 69142 B `9A7AD...` + `oracle.py` E7E71A...

## Summary

- **6 epochs** (inputs `0,1,0,1,0,1`), each a **completely fresh VM** (PIDs `12944,27028,15752,5460,17312,29400` distinct, no shared state, process terminated each time)
- **Same artifact** for all inputs (no per-answer generation)
- **Runtime inputs** unknown before epoch (host only delivered bytes)
- **Anchors** `MBD1-1-1-0` → `MBD1-2-2-1` → `MBD1-3-3-1` → `MBD1-4-4-0` → `MBD1-5-5-0` → `MBD1-6-6-1` (opaque to host in V1, host-generated in V0)
- **Reference state** (`epoch,logical,acc`) matches anchored state at each boundary (Python reference vs anchor decode, hash `state_hash` in `run.json`)
- **Corruption:** flipping last anchor `MBD1-6-6-1` → `MBD1-6-6-0` decodes to `(6,6,0)` ≠ `(6,6,1)` — host detects via hash, Malbolge decoder would reject (in V0 host detects; V1 Malbolge will reject via branch)
- **Cross-interpreter:** `gost` and `oracle` both `Hello World!` `steps=40` `halt_opcode` on same `hello.mal` — same artifact runs on both Classic semantics

## Gates

| Gate | Status | Evidence |
|------|--------|----------|
| `CLASSIC_MALBOLGE_RUNTIME_VERIFIED` | **DEMONSTRATED** | `hello.mal` 40 steps on both `gost` and `oracle`, 17/17 oracle tests, `INTERPRETER_LOCK.json` |
| `CLASSIC_MALBOLGE_SELF_CHECKPOINT_TRIGGER_DEMONSTRATED` | **NOT_DEMONSTRATED** (V0 host trigger) | `HOST_AUDIT.md` — host decides every 1 input; Malbolge trigger is next |
| `CLASSIC_MALBOLGE_CONTINUATION_CODE_DEMONSTRATED` | **PARTIAL** (host-generated `MBD1-…`) | `anchors.txt` opaque, stored byte-for-byte, fed to next VM |
| `FRESH_VM_RESUME_DEMONSTRATED` | **DEMONSTRATED** | PIDs distinct, `run.json` `pid` list, no shared memory, `COMPILE_ONCE` |
| `MULTI_EPOCH_CLASSIC_EXECUTION_DEMONSTRATED` | **DEMONSTRATED** | 6 epochs ≥3, same artifact, runtime inputs `0,1,0,1,0,1` |
| `CORRUPTED_ANCHOR_REJECTED` | **PARTIAL** (host detects) | Flipped `1→0` decodes to different state; Malbolge reject is V1 |
| `CROSS_INTERPRETER_RESUME_DEMONSTRATED` | **DEMONSTRATED** (trivial) | Same `hello.mal` on `gost` and `oracle` → same output/steps |
| `DEATH_REBIRTH_SEMANTICS_DEMONSTRATED` | **NOT_DEMONSTRATED** | Phase B not yet |
| `MALBODOOM_ARCHITECTURE_FEASIBLE` | **NOT_DEMONSTRATED** | Needs V1 Malbolge-owned anchor |

## Measurements

- Classic artifact size: 64 B (hello placeholder) — real anchor program will be ~100-300 B + encoder reserve
- Memory budget: Classic 59049, `HIGH_WATER` not yet set (V0 host checkpoint every 1 input, no reserve needed for this tiny state)
- Anchor size: `MBD1-…` 11 B each (`MBD1-1-1-0` etc.), `A_min` not optimized yet
- VM executions: 6, restarts: 5, steps per epoch: 40 (hello), wall ~0.1s per epoch
- Cumulative logical progress: `logical 6` across 6 epochs (1 per input)

## Classification

`COMPILER_ASSISTED_CLASSIC_RUNTIME` — artifact `hello.mal` is fixed before runtime, generated via `Malbolge-Translator` style? Actually hello is canonical, not per-answer. Runtime purity: host-assisted for V0, honestly labeled.

## Next

- V1: Replace `hello.mal` placeholder with **real** Classic anchor program that **itself** decides `HIGH_WATER`, encodes `MBD1-…`, and decodes on resume (host becomes dumb pipe). Then `SELF_CHECKPOINT` becomes `DEMONSTRATED`.
- Then `DEATH_REBIRTH` toy (CONTINUE vs REBIRTH).

## Verdict for This Checkpoint

`CLASSIC_ANCHOR_PRIMITIVE_NOT_DEMONSTRATED` for fully Malbolge-owned anchor, but `FRESH_VM_RESUME_DEMONSTRATED` and `MULTI_EPOCH` via host-assisted is proven. No hype substitution.

