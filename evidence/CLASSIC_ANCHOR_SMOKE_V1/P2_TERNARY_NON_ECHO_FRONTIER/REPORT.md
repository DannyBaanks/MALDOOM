# P2 Ternary Non-Echo Frontier

Target: Classic Malbolge, 59049-cell VM semantics.

Command run from `vendor/classic_synthesis/`:

```powershell
zig build-exe branch_search.zig -O ReleaseFast "-femit-bin=branch_search.exe"
.\branch_search.exe 2 20 A A B B
.\branch_search.exe 3 50 0 1 1 2 2 0
.\branch_search.exe 4 50 0 1 1 2 2 0
.\branch_search.exe 5 50 0 1 1 2 2 0
```

Observed output is preserved in `raw_stdout.txt`; exit status was 0.

Search contract: one fixed Classic source must map all three inputs as
`0 -> 1`, `1 -> 2`, `2 -> 0` within 50 VM steps. Candidate alphabet contains
the eight valid decoded opcodes used by the local synthesis VM.

Control: length 2 finds `ub` for `A -> A` and `B -> B` (64 candidates).

Negative result:

| Length | Candidates | Hits |
| --- | ---: | ---: |
| 3 | 512 | 0 |
| 4 | 4096 | 0 |
| 5 | 32768 | 0 |

`CLASSIC_TERNARY_NON_ECHO_TRANSITION_NOT_DEMONSTRATED` for this bounded
frontier only. This does not prove the relation impossible at larger lengths,
with a wider candidate grammar, or with more steps.

Tool source SHA256: `c975368c3d7f2d80185ae75e1029f3721a92e5f480c461ce5882fbee12c3cda9`.

Next: add control-flow/termination predicates to the local search and search
templates seeded by the verified truth machine. Do not claim V1 checkpoint,
anchor or Doom Classic from this result.
