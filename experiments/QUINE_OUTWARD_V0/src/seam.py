#!/usr/bin/env python3
"""seam.py â€” Fase 5: find the minimal SEAM (gap/padding/phase) that lets two
microcells coexist with preserved signatures.

Microcell = 3 cells, signature cell = lo+2. We place A (sig 1) and B (sig 0)
with an intermediate region S between them, varying:
  - gap distance (number of separator cells)
  - padding pattern (0s vs periodic/mirrored)
  - phase offset
Goal: minimal S such that signature(A|S|B) preserves both A and B signatures.

Faithful crazy rule. Model = MALBOLGE_MEMORY_AS_CA_MODEL.
"""
import json, hashlib
from _common import mi
CRAZY = mi.crazy_op

def evolve(seed, steps):
    n = len(seed); ring = list(seed)
    for _ in range(steps):
        nxt = [CRAZY(ring[(i-1) % n], ring[(i-2) % n]) for i in range(n)]
        ring = nxt
    return ring

def sig_at(ring, idx): return ring[idx] % 3

def build(n, a_lo, b_lo, a_state, b_state, pad_pattern="zero"):
    ring = [0]*n
    for lo, st in ((a_lo, a_state), (b_lo, b_state)):
        ring[lo] = 1; ring[lo+1] = 1; ring[lo+2] = st
    # fill the rest (padding) per pattern
    if pad_pattern == "zero":
        pass
    elif pad_pattern == "periodic":
        for i in range(n):
            if ring[i] == 0:
                ring[i] = (i % 3)
    elif pad_pattern == "mirror":
        # mirror around A end: values descending
        for i in range(a_lo+3, b_lo):
            ring[i] = (b_lo - i) % 3
    return ring

results = []
# fix A at lo=2 (STATE_1), B at varying lo with a gap of 'g' zeros between
# A block ends at a_lo+2; B starts at b_lo = a_lo+3+g
A_STATE, B_STATE = 1, 0
A_LO = 2

for g in range(0, 8):
    for pad in ("zero", "periodic", "mirror"):
        b_lo = A_LO + 3 + g
        n = b_lo + 3 + 1  # room after B, plus wrap slack
        ring = build(n, A_LO, b_lo, A_STATE, B_STATE, pad)
        f = evolve(ring, 300)
        a1 = sig_at(f, A_LO+2); b1 = sig_at(f, b_lo+2)
        ok = (a1 == A_STATE) and (b1 == B_STATE)
        results.append({
            "gap": g, "pad": pad, "n": n,
            "A_after": a1, "B_after": b1, "both_preserved": ok,
            "final_sha": hashlib.sha256(bytes(str(tuple(f)).encode())).hexdigest()[:16],
        })

# find minimal gap per pad that preserves both
min_seam = {}
for pad in ("zero", "periodic", "mirror"):
    ok_rows = [r for r in results if r["pad"] == pad and r["both_preserved"]]
    if ok_rows:
        min_seam[pad] = min(ok_rows, key=lambda r: r["gap"])
    else:
        min_seam[pad] = None

print(json.dumps({
    "results": results,
    "min_seam_per_pad": min_seam,
}, indent=2))