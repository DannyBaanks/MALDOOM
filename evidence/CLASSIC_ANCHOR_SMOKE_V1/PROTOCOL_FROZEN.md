# CLASSIC_ANCHOR_SMOKE_V1 — Malbolge-Owned Checkpoint (Design + Generator Stub)

**Status:** `NOT_DEMONSTRATED` for fully Malbolge-owned anchor. This directory contains the **frozen protocol** for V1 and a **generator stub** that will produce the real `program_v1.mal`.

**Gap from V0:**

- V0: `HOST` decided checkpoint, `HOST` encoded `MBD1-epoch-logical-acc`
- V1: `MALBOLGE` must decide `HIGH_WATER`, update `acc/rng/logical/local`, encode `MBD1A-<trit_payload><check>`, decode and validate on resume

**Why Trit Format `MBD1A`?**

- Malbolge is ternary-ish (`crazy` is tritwise). Decimal `MBD1-10-20` requires expensive `divmod 10` loops. Trit payload `0/1/2` maps directly to `crazy` trit operations and `OUT` of `'0'+trit`.
- Payload: 6 trits `epoch(1) logical(2) acc(1) rng(1) local(1)` as chars `'0'/'1'/'2'`, plus 1 trit check `sum(payload)%3` as `'0'/'1'/'2'`, framed as `MBD1A-<payload><check>\n` (13 B total, 6 payload +1 check +6 framing). Host stores opaque bytes, never parses.

**State Machine (Small, Compilable):**

```
acc' = t[acc*3+input]  where t=[1,1,2,0,0,2,0,2,1] (crazy low trit)
rng' = (rng+1)%3
logical' = logical+1
local' = local+1
HIGH_WATER = local==2
```

- Input alphabet `'0','1','2'` (trits)
- `NEW` mode (`N\n`): `epoch=0,logical=0,acc=0,rng=0,local=0`
- `RESUME` mode (`R\n` + `MBD1A-...`): Malbolge reads anchor, verifies `MBD1A-` prefix, verifies `check`, decodes 6 trits into state, then continues.

**Host `v1_anchor_pipe.py` (dumb):**

```
Popen(gost, program_v1.mal)
detect "INPUT\n" -> write one input byte ('0'/'1'/'2')
detect "ANCHOR\n" + next line -> store opaque anchor, wait for HALT
detect "STATE:<trits>\n" -> capture candidate canonical bytes for verifier
detect "REJECT\n" -> corruption rejected
```

Host never `split("-")`, never `int(anchor_field)`, never `crazy`. Static audit will grep for `anchor_decode`, `state`, etc.

**Artifact Purity:**

- `program_v1.mal` generated **before** runtime inputs, single frozen `SHA256`, used for every epoch/input/interpreter
- `COMPILER_ASSISTED_CLASSIC_RUNTIME` — generator runs before, artifact is fixed, runs unchanged on `gost` and `oracle` (59049)

**Current Stub Generator:**

`generator.py` in this dir is a **stub** that demonstrates the *search* for `p` with large `K` via `j` + `crazy` fill. It can generate `INPUT` prompt (`INPUT\n`) as `encode(['<',...])` and shows how `p` at position where `d` points beyond program (via `j`) can get large `K`. Full state machine generation requires cycle search for ~100-instruction program (estimated hours, not done in this checkpoint).

**Next Steps (V1):**

1. Extend `generator.py` to brute-force `j`/`p` sequences for each transition (27 states ×3 inputs =81 transitions, each needs `p` with large `K` via `j`).
2. Encode full automaton via `XLAT1` cycles (like `hello.mal` was found via search).
3. Run `V1_01..V1_20` tests (same artifact, fresh PID, >=3 boundaries, corruption, cross-interpreter, manual password).
4. Only then claim `CLASSIC_ANCHOR_PRIMITIVE_DEMONSTRATED`.

**Evidence for V1 (currently):**

- `PROTOCOL_FROZEN.md` (this file's parent `evidence/.../PROTOCOL_FROZEN.md`)
- `GENERATOR_AUDIT.md` (generator is stub, honestly labeled)
- `HOST_AUDIT.md` (host is dumb pipe, no semantic parse)
- No `program_v1.mal` yet → `CLASSIC_ANCHOR_PRIMITIVE_NOT_DEMONSTRATED`

