# P4 Ternary Stateful Counter — Exhaustive Search Negative Result

Target: Classic Malbolge, 59049-cell VM semantics.

Commands run from `vendor/classic_synthesis/`:
```powershell
zig build-exe stateful_search.zig -O ReleaseFast "-femit-bin=stateful_search.exe"
.\stateful_search.exe 7 1000 012
.\stateful_search.exe 7 2000 012
zig build-exe long_search.zig -O ReleaseFast "-femit-bin=long_search.exe"
.\long_search.exe 7 2000 012
```

Search contract: find a Classic program that on single execution with input "012":
- Reads 3 inputs (ternary)
- Maintains internal state (local counter 0→1→2)
- Runs for ≥20 steps (indicating loop/stateful behavior)
- Produces 3+ distinct outputs corresponding to state transitions

Results:

| Length | Candidates | Hits (≥3 distinct outputs) | Hits (≥20 steps) | Notes |
| --- | ---: | ---: | ---: | --- |
| 7 | 2,097,152 | 3,884 | 0 | All 3,884 terminate in 7-9 steps |
| 7 (long_search) | 2,097,152 | N/A | 0 | No program runs ≥50 steps |

The 3,884 hits at length 7 all terminate in 7-9 steps. They read the three inputs and halt immediately (likely hitting an encrypted instruction outside 33-126). None exhibit looping or persistent state.

Control: `truth_machine.mal` (170 chars) runs 2000+ steps on input '1', demonstrating that Classic looping programs exist but are long and rare.

Negative result: `CLASSIC_TERNARY_STATEFUL_COUNTER_NOT_DEMONSTRATED` for exhaustive search up to length 7.

This does not prove impossibility — `truth_machine.mal` proves Classic can loop with state — but it establishes a concrete lower bound: a 3-state counter program is not found in the first 2M candidates of the 8-opcode grammar.

Next step: guided synthesis via Autobolge relational beam search seeded by `truth_machine.mal`, or manual construction.

Tool sources: `vendor/classic_synthesis/stateful_search.zig`, `long_search.zig` (SHA256 in `SHA256SUMS.txt`).