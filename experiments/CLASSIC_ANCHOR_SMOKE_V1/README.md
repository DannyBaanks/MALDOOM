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

**V1 Progress (closed, reproducible):**

1. **P1** `CLASSIC_NON_ECHO_INPUT_BRANCH_SEED_DEMONSTRATED` — vendored
   `truth_machine.mal` is a verified non-echo branch (input `0` halts at 136,
   input `1` loops past 200) on both `gost` and `oracle`. Evidence:
   `evidence/CLASSIC_ANCHOR_SMOKE_V1/P1_NON_ECHO_BRANCH/` (run.json + REPORT.md + SHA256SUMS.txt).
2. **P2** `CLASSIC_TERNARY_NON_ECHO_TRANSITION_NOT_DEMONSTRATED` — bounded
   non-echo frontier length 3..5 is negative (0 hits over 37,376 candidates).
   Next: extend local synthesis with control-flow/termination predicates
   seeded by `truth_machine.mal`. Evidence: `.../P2_TERNARY_NON_ECHO_FRONTIER/`.
3. **P3** `CLASSIC_SEED_ANCHOR_REPLAY_DEMONSTRATED` — `truth_machine.mal` as
   control AND anchor; opaque replay of observable behavior reproduces anchors
   for both inputs on both interpreters. Evidence: `.../P3_SEED_AS_ANCHOR/`.
4. **P4** `CLASSIC_TERNARY_STATEFUL_COUNTER_NOT_DEMONSTRATED` — exhaustive
   search up to length 7 finds no 3-state counter looping >=20 steps (first
   2M candidates, 8-opcode grammar). Control proves Classic can loop with
   state but such programs are long and rare. Evidence: `.../P4_TERNARY_STATEFUL_COUNTER/`.
5. **P5 phase 1** `CLASSIC_CROSS_READ_STATE_NOT_DEMONSTRATED` — the minimal
   cross-read-state primitive (output on trailing input depends on leading
   input) has 0 hits over 2,396,736 exhaustive candidates at lengths 2..7 in
   the 8-opcode grammar. This is a stronger negative than P4 (which could be
   satisfied by echo); it isolates genuine input-history dependence. Evidence:
   `.../P5_STATE_CROSS_READ/`.

**Next Steps (V1):**

6. P5 phase 2: guided synthesis seeded by `truth_machine.mal`, or Autobolge
   relational beam search over a wider/templated grammar, to find a
   cross-read-state program; then add `HIGH_WATER` branch + MBD1A
   encoder/decoder/checksum.
7. P6: fresh VM boundary with anchor handoff (`gost` -> `oracle`).
8. Run `V1_01..V1_20` tests (same artifact, fresh PID, >=3 boundaries,
   corruption, cross-interpreter, manual password).
9. Only then claim `CLASSIC_ANCHOR_PRIMITIVE_DEMONSTRATED`.

**Evidence for V1 (currently):**

- `PROTOCOL_FROZEN.md` (this file's parent `evidence/.../PROTOCOL_FROZEN.md`)
- `GENERATOR_AUDIT.md` (generator is stub, honestly labeled)
- `HOST_AUDIT.md` (host is dumb pipe, no semantic parse)
- P1..P5 phase 1 closed with REPORT.md + SHA256SUMS.txt; P2/P4/P5 are honest
  negatives
- No `program_v1.mal` yet → `CLASSIC_ANCHOR_PRIMITIVE_NOT_DEMONSTRATED`
