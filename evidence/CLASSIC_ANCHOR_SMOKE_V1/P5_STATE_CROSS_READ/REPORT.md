# P5 Phase 1 — Cross-Read State Primitive (Exhaustive Search Negative)

Target: Classic Malbolge, 59049-cell VM semantics.

## Question

The MBD1A checkpoint primitive needs a Classic program that carries state
across multiple input reads (so `HIGH_WATER`/`local` can persist between
`OUT`/`INPUT`), then branch and emit an anchor. Before building the
encoder/decoder we must first prove such a program exists in the local
8-opcode grammar at all.

The minimal falsifiable property is **cross-read state**: run the SAME
immutable program with two input sequences that share the trailing input but
differ in the leading input (`"01"` vs `"21"`). If the full output differs
between the two runs, then the trailing `'1'` was processed differently
depending on the leading input, i.e. the program kept state across reads.
A pure per-input echo/transducer cannot do this.

## Command

```powershell
zig build-exe vendor/classic_synthesis/state_compare.zig -O ReleaseFast
state_compare.exe <length> 100
```

Tool source: `vendor/classic_synthesis/state_compare.zig` (search tool, never
gameplay code). Raw output in `raw_stdout.txt`.

## Result

| Length | Candidates | Hits (cross-read) |
| --- | ---: | ---: |
| 2 | 64 | 0 |
| 3 | 512 | 0 |
| 4 | 4,096 | 0 |
| 5 | 32,768 | 0 |
| 6 | 262,144 | 0 |
| 7 | 2,097,152 | 0 |
| **Total** | **2,396,736** | **0** |

`CLASSIC_CROSS_READ_STATE_NOT_DEMONSTRATED` for the exhaustive 8-opcode
grammar up to length 7.

## Interpretation (honest)

- This is a stronger negative than P2/P4: P4 looked for "3 distinct outputs"
  which can be satisfied by an echo; this search isolates genuine
  input-history dependence.
- It does NOT prove impossibility. `truth_machine.mal` (170 chars) proves
  Classic can branch on input, so stateful programs exist; they are simply
  not reachable by the 8-opcode grammar at length <= 7.
- Consequence for P5: the MBD1A HIGH_WATER/local-counter primitive is not
  synthesizable by blind 8-opcode search at these sizes. The documented path
  forward (from P2/P4) is guided synthesis seeded by `truth_machine.mal`,
  or Autobolge relational beam search over a wider/templated grammar.

## Exclusion

This result is a search-tool negative for one grammar and length bound. It is
NOT a claim about Autobolge-guided synthesis, longer programs, or the
existence of the checkpoint primitive in general.

Artifact hashes in `SHA256SUMS.txt`.