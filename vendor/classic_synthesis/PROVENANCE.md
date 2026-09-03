# Classic Synthesis Provenance

This is a deliberately small vendored set. MALDOOM does not require a clone
of Autobolge or MALPAD to build or run the local search primitive.

## Autobolge VM

- Source: `https://github.com/DannyBaanks/Autobolge`
- Commit: `edb9ae0877dab0daeca95c50e9f32852ede792c5`
- Copied file: `autobolge/vm.zig`
- License: MIT, reproduced in `autobolge/LICENSE`.
- Role: exact Classic 59049-cell executor for local bounded synthesis.
- Upstream credit: Danny Baanks / Autobolge.

`branch_search.zig` is MALDOOM-local glue using the
vendored VM. It searches one immutable Classic source against two independent
input/output cases. It is a V1 primitive search tool, not gameplay code.

`stateful_search.zig`, `long_search.zig` and `state_compare.zig` are
MALDOOM-local search tools on the same vendored VM: they look for stateful /
long-running / cross-read-state Classic programs respectively. `state_compare`
is the P5 primitive probe. None are gameplay code; all are evidence tools.

## MALPAD Truth Machine

- Source: `https://github.com/DannyBaanks/MALPAD`
- Commit: `31d9d7e69eb1e2110c521a0d804728802d2227ba`
- Copied file: `malpad/truth_machine.mal`
- Upstream evidence: `MALPAD/tests/test_m2_state.py` specifies `0 -> halt`
  and `1 -> loop` on independent Classic runtimes.
- License status: no top-level license file was present at this pinned source
  commit. It is retained with source, commit and author credit; do not export
  it as third-party licensed material without resolving that status.
- Role: verified non-echo branch/halt seed for the next search specification.

## Integrity

The source commits and file SHA256 values are recorded in
`vendor/classic_synthesis/SHA256SUMS.txt`. Update this document and hashes if
the vendored set changes. No external repository is a runtime dependency.
