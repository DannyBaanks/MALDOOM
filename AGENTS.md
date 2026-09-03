# MALDOOM — Agent Contract

> First law is frozen. Everything else is subordinate.

## 0. Read First

1. Read `README.md` law: `IF THE HOST COMPUTES A DOOM GAMEPLAY TRANSITION, THE DEMONSTRATION FAILS.`
2. Read this file.
3. Read `TOOLCHAIN_LOCK.json` — pinned commits are truth, not `main`.
4. Never claim `WORLD_FIRST` / `FULL_DOOM_ON_CLASSIC` without hashed evidence + exhaustive prior-art search.

## 1. What This Repo Is

- **TARGET_A** = Malbolge Unshackled (unbounded, Turing-complete) → FULL DOOM candidate.
- **TARGET_B** = Classic Malbolge (59049) → `FULL_DOOM = NOT_DEMONSTRATED`. Keep them separate in every claim.
- Minimal path is `C → 8cc/EIR → ELVM → HeLL → Malbolge Unshackled → VM → host I/O bridge`. Do NOT replace HeLL with MalboGost until `M0→M3` passes on the existing chain.
- This repo is standalone. Do NOT integrate with any external/private
  research tree or its `workspace/assembly`, nor with `MalboGost`, yet.
- Do NOT attempt full Doom before `M0` is green.

## 2. Execution Hierarchy

```
operational Doom tick:  Unshackled VM runs .mu artifact, host only pumps bytes
toolchain build:        8cc (eir branch) builds EIR, ELVM target/hell emits HeLL, LMFAO assembles
verification:           verifier/ compares H(S_Malbolge) vs H(S_C) — verifier never computes gameplay either
```

`host/` is dumb I/O. `verifier/` is dumb hash compare. The only place where `S_t → S_{t+1}` may happen is **inside the Malbolge VM**.

## 3. Host Contract — Allowed / Forbidden

Allowed in `host/`:
- `DG_Init` / window & framebuffer allocation
- `DG_DrawFrame` blit `DG_ScreenBuffer` → screen
- `DG_GetKey` / `DG_SleepMs` / `DG_GetTicksMs`
- WAD **byte transport**: `read(path) → bytes` delivered to engine
- logging, hashing, timing

Forbidden in `host/` (instant FAIL):
- any `doomgeneric_Tick`, `P_*`, `WI_*`, `ST_*`, `G_Ticker`, `P_MovePlayer`, `P_RunThinkers`, `M_Random`, collision, AI, RNG, WAD lump semantic interpretation, framebuffer synthesis, expected-answer injection.

Audit: `grep -R "doomgeneric_Tick\|P_MovePlayer\|P_RunThinkers\|M_Random" host/` must be empty. `tests/test_engine_does_the_work.py` enforces it in CI.

## 4. Evidence Discipline

Every milestone/seam produces:

- source C/EIR, generated HeLL, generated `.mu`/`.mal`
- exact command, raw stdout/stderr, exit code, wall time
- SHA-256 of every artifact
- expected vs observed (hash for M3+)
- `host_computation_audit.log`
- `NOT_DEMONSTRATED` section with exclusions

No hash = not canonical. Overwriting `evidence/` without new hash = chain broken.

Naming: `evidence/M0_A_CONST/`, `evidence/M0_KILLER/` each with `artifact.mu`, `artifact.hell`, `source.c`, `run.json`, `SHA256SUMS.txt`.

## 5. Toolchain Provenance

- Do NOT copy giant repos blindly. Use `scripts/fetch_toolchain.py --lock TOOLCHAIN_LOCK.json` which clones at pinned commit into `vendor/`.
- Document real path in `docs/TOOLCHAIN.md` **before** compiling. If `C → HeLL` is broken at some edge, say so.
- `TOOLCHAIN_LOCK.json` fields: `{repo, url, commit, sha256|tag, license, role}` per entry. Update only by bumping commit field + re-hashing.

Pinned today:

- `shinh/elvm` (HeLL backend)
- `shinh/8cc` (eir branch, C frontend)
- `ozkl/doomgeneric` (Doom port)
- `lutter.cc/Unshackled.c` + `Unshackled-20.c` / `oerjan/Unshackled.hs`
- `LMFAO` (HeLL assembler)

## 6. Milestone Gates

- `M0_*` + `M0_KILLER` must all pass with `RUNTIME_STATEFUL_EXECUTION_DEMONSTRATED` before touching WAD.
- `M1` needs `M0` green. `M2` needs `M1`. `M3` needs `M2`. No auto-advance.
- Each `M*_REPORT.md` declares claim status explicitly: `DEMONSTRATED` / `PARTIAL` / `NOT_DEMONSTRATED`.
- `M3` requires normalizing only pre-declared nondeterministic fields — list them in `verifier/config.json` before running.

## 7. Malbolge vs Unshackled

- Never write `.mal` when you mean `.mu` or vice versa without stating target.
- I/O: Classic uses `mod 256`, Unshackled uses Unicode codepoints + `...21`=newline, `...22`=EOF. ELVM backend already reverts newlines + `mod 256` but warns to limit to ASCII.
- Rotation width: Unshackled starts ≥10, grows when `j` widens `D` beyond half width — non-deterministic, must be probed (hence killer test matters).

## 8. Before Editing Checklist

- Which target (A/B)? Which milestone gate?
- Am I touching `host/` gameplay logic? → forbidden.
- Am I regenerating `.mu` per input? → forbidden for killer test.
- Have I pinned the toolchain commit I'm building against?
- Will my change invalidate a recorded SHA? Then bump evidence version, don't overwrite silently.

## 9. After Editing — Required

- Run smallest relevant verifier: `py scripts/build_m0.py --only M0_A` then `py -m pytest tests/test_engine_does_the_work.py`
- Keep raw output + SHA.
- Update `TOOLCHAIN_LOCK.json` only if you actually bumped a vendor.
- Never upgrade a claim label without new `evidence/` run.

## 10. Commands

```powershell
# fetch pinned toolchain (no build yet)
py scripts/fetch_toolchain.py --lock TOOLCHAIN_LOCK.json

# build & run M0 smoke (each program isolated)
py scripts/build_m0.py --all
py scripts/build_m0.py --only M0_KILLER --inputs 7,13,42

# verify host didn't cheat
py -m pytest tests/test_engine_does_the_work.py -v
py -m pytest tests/test_killer_input.py -v

# hash artifacts
Get-FileHash vendor/build/*.mu -Algorithm SHA256
```

If a command is not listed, document it in `docs/TOOLCHAIN.md` with real output before using in evidence.
