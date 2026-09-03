# Claims Registry

| Claim | Gate | Status |
|---|---|---|
| `MALBOLGE_UNSHACKLED_EIR_PIPELINE_DEMONSTRATED` | M0_A–F + KILLER all PASS, host audit PASS | NOT_DEMONSTRATED (until M0_REPORT) |
| `RUNTIME_STATEFUL_EXECUTION_DEMONSTRATED` | M0_KILLER same `.mu` gives correct output for 3+ unseen `n` without recompilation | NOT_DEMONSTRATED |
| `WAD_HEADER_PARSE_IN_MALBOLGE_DEMONSTRATED` | M1 bytes→fields inside VM hash vs C parser | NOT_DEMONSTRATED |
| `DOOM_STATE_INIT_DEMONSTRATED` | M2 S_0 hash vs C | NOT_DEMONSTRATED |
| `DOOM_TICK_IN_MALBOLGE_DEMONSTRATED` | M3 H(S_{t+1}) equality vs C reference | NOT_DEMONSTRATED |
| `FRAMEBUFFER_EQUIVALENCE_DEMONSTRATED` | M5 pixel hash | NOT_DEMONSTRATED |
| `MULTITICK_EXECUTION_DEMONSTRATED` | M6 N ticks stable | NOT_DEMONSTRATED |
| `PLAYABLE_DEMONSTRATED` | M7 E1M1 technically playable | NOT_DEMONSTRATED |
| `FULL_DOOM_ON_CLASSIC_MALBOLGE` | — | NOT_DEMONSTRATED (TARGET_B) |
| `WORLD_FIRST / FIRST_DOOM_ON_MALBOLGE` | exhaustive prior-art search | FORBIDDEN until published search |

Initial search (2026-09-01): `NO PRIOR MALBOLGE DOOM PORT FOUND IN INITIAL SEARCH` — via web search ELVM/Malbolge/Unshackled/Doom combos. Not a world-first claim.

Promotion rule: a claim moves from `NOT_DEMONSTRATED` → `DEMONSTRATED` only with `evidence/` dir containing source, artifact, HeLL, command, stdout/stderr, exit code, wall time, SHA-256, expected vs observed, host audit.

Forbidden: `REALTIME`, `PLAYABLE` before M7, `TURING_COMPLETE_CLASSIC_MALBOLGE`.
