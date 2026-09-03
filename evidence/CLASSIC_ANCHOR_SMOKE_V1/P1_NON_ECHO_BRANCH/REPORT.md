# P1 Non-Echo Branch/Halt Seed

Target: Classic Malbolge, 59049-cell VM semantics.

Command (reproducible, exit 0):

```powershell
py experiments/CLASSIC_ANCHOR_SMOKE_V1/run_p1_non_echo_branch.py
```

Observed output preserved in `run.json`. Program is the vendored
`truth_machine.mal` seed
(`vendor/classic_synthesis/malpad/truth_machine.mal`),
SHA256 `3d58a7f9e0addbbbace2f2809e4a8c9e0c50888e8c91483169618db14816aa37`,
cross-checked on two pinned interpreters:

| Input | gost (stdout / steps) | oracle (stdout / halted) |
| --- | --- | --- |
| `0` | `0\n` / 136 | `0` / true (halt_opcode) |
| `1` | `1`*11 / 200 (timeout) | `1`*11 / false (max_steps) |

The seed is a verified non-echo branch: input `0` halts, input `1` loops, both
interpreters agree on observable output and step counts (gost 136/200, oracle
136/200).

Claim: `CLASSIC_NON_ECHO_INPUT_BRANCH_SEED_DEMONSTRATED`.

Exclusion: this seed is `program.mal` for the smoke, NOT `program_v1.mal`. It
does not encode, decode, checkpoint, or resume an anchor. It is a control
seed used as the substrate for P3/P4/P5.

Artifact hashes in `SHA256SUMS.txt`.