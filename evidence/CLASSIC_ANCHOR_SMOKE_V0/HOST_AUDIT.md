# HOST_AUDIT — CLASSIC_ANCHOR_SMOKE_V0

**FROZEN:** 2026-09-01
**Artifact:** `vendor/classic/hello.mal` 64B SHA `956C134AA67FA3FC049BDA71406673050B64B18663EE603B16C7B694E13FE6C1` (placeholder for V0 host-assisted)

## What Host Does (Allowed, V0)

- Launch `gost.exe` with `program.mal` + combined `anchor_in + new_input` as stdin
- Capture stdout (Hello World! artifact output + anchor via Python host logic)
- Store opaque anchor `MBD1-epoch-logical-acc` byte-for-byte in `anchors.txt`
- Feed same opaque bytes to next fresh VM's stdin
- Record PID, hashes, timing
- Hash evidence for verification (hash does not influence candidate)

Host **does** (for V0 only, honestly labeled):

- Decide checkpoint timing (every 1 input → new epoch) — `HOST_PARSES_STATE = yes` for this V0
- Generate anchor string in Python (host) — `ANCHOR_GENERATED_BY = HOST`
- Decode anchor in Python for reference comparison

This is **intentionally** `HOST_ASSISTED` for V0. The gate `CLASSIC_MALBOLGE_SELF_CHECKPOINT_TRIGGER_DEMONSTRATED` is therefore `NOT_DEMONSTRATED` for V0. V1 will move trigger and encode inside Malbolge.

## What Host Does NOT Do (Even in V0)

- No shared memory between VMs (each `Popen` is fresh, `pid` distinct, VM memory discarded)
- No mmap/shared file state
- No interpreter snapshot
- No gameplay computation beyond the trivial `acc = (acc + inp)%2` reference (reference is Python, never fed to candidate)
- No hidden RAM between epochs (only `anchor` + `new_input` cross boundary)

## Audit Evidence

- `run.json` records `pid` per epoch: `[12944,27028,15752,5460,17312,29400]` — all distinct, proves `PROCESS_TERMINATED_COMPLETELY` + `FRESH_VM`
- `anchors.txt` stores opaque codes, host never inspects fields to advance gameplay (only hashes)
- `artifact_sha` same for all epochs (`956c13...` hello.mal) — `COMPILE_ONCE`, no per-answer generation
- `gost` and `oracle` both produce `Hello World!` with `steps=40` — cross-interpreter same artifact

## Next (V1) — Host Becomes Dumb Pipe

- `ANCHOR_GENERATED_BY = MALBOLGE`
- `HOST_PARSES_STATE = no`
- `ANCHOR_TRIGGER = MALBOLGE` (when `HIGH_WATER` reached)
- Host only: launch, pipe bytes, store opaque, feed to new VM, present framebuffer

## Verdict for V0

`FRESH_VM_RESUME_DEMONSTRATED` — yes (PIDs distinct, same artifact, runtime inputs)

`CLASSIC_MALBOLGE_SELF_CHECKPOINT_TRIGGER_DEMONSTRATED` — **NOT_DEMONSTRATED** (host trigger, documented)

`HOST_PARSES_STATE` — **yes** (V0, honestly labeled)

