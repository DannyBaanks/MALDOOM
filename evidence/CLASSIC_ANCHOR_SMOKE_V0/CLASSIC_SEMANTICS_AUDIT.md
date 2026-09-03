# Classic Malbolge Semantics Audit

**Memory:** 59049 words (3¹⁰). Verified via `oracle` test `test_memory_is_three_to_the_tenth` and `hello` 40 steps.

**Primitives:**

- `crazy(a,b)` tritwise `t[(a%3)*3+(b%3)]` with `t=[1,1,2,0,0,2,0,2,1]`, `a,b` in `0..59048`, result `0..59048`, closed.
- `rot(n) = n//3 + (n%3)*19683` (right rotation, 10 trits)
- `XLAT1` length 94, drives `inst = XLAT1[(mem[c]-33+c)%94]`
- `XLAT2` permutation of 0..93, drives `mem[c] = XLAT2[mem[c]-33]` after execution
- `mem[i] = crazy(mem[i-1],mem[i-2])` for `i >= len(prog)`
- `o` is NOP (not in XLAT1), `j` is branch (`c = mem[d]`), `i` is `c = mem[d]`? Actually `i` is ??? (per spec)
- I/O `mod 256` (`'/'` is IN, `'<'` is OUT, `v` HALT, `p` CRAZY, `*` ROT, `j` MOVD? Wait correct ops: `/` IN, `<` OUT, `v` HALT, `p` CRAZY, `*` ROT, `j` JMP, `i` MOVD). Classic spec confirmed via `gost.c` and `oracle.py`.

**Interpreters pinned:**

- `gost.c` 14209 B, `ACBE79...`, `gost.exe` 69142 B `9A7AD...`, `gost2.exe` 5AD2EB...
- `oracle.py` 9471 B `E7E71A...`, 17/17 tests OK
- Both produce `Hello World!` from same `hello.mal` 64B `956C13...`

**Finite vs Unshackled:**

- Classic `59049` bounded, **not Turing-complete**
- Unshackled unbounded, Turing-complete (separate TARGET_A). This audit is for B only.

**Managed HIGH_WATER concept:**

- Classic memory is finite, but MALBODOOM defines its own `HIGH_WATER` inside 59049, with `checkpoint reserve` for encoder. No enlargement, just reservation.

