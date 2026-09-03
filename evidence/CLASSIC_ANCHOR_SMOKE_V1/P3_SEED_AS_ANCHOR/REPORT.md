# P3 Seed-as-Anchor (Opaque Replay)

Target: Classic Malbolge, 59049-cell VM semantics.

Command (reproducible, exit 0):

```powershell
py experiments/CLASSIC_ANCHOR_SMOKE_V1/run_p3_seed_anchor.py
```

Observed output preserved in `run.json`. Program is the same vendored
`truth_machine.mal` seed as P1 (SHA256
`3d58a7f9e0addbbbace2f2809e4a8c9e0c50888e8c91483169618db14816aa37`), now used
in two non-crossing roles:

1. CONTROL: verifies input-dependent behavior on pinned interpreters.
2. ANCHOR: the observable outcome (steps, halted, output prefix) is used as an
   opaque continuation token. Resume = re-run same seed with same input; the
   anchor is reproduced iff observable behavior reproduces.

| Input | anchor_first | anchor_resume | reproduced |
| --- | --- | --- | --- |
| `0` | gost 136 / oracle 136 halt | identical | true |
| `1` | gost 200 / oracle 200 no-halt | identical | true |

`anchor_reproduced=true` for both inputs on both interpreters.

Claim: `CLASSIC_SEED_ANCHOR_REPLAY_DEMONSTRATED`.

Exclusion: the anchor is an opaque replay of observable behavior only. There
is no MBD1A encode/decode, no internal-state serialization, and no fresh-VM
boundary with cross-interpreter handoff yet. This demonstrates that a fixed
Classic artifact can act as a deterministic continuation token, which is a
necessary precondition for P5/P6, not the checkpoint primitive itself.

Artifact hashes in `SHA256SUMS.txt`.