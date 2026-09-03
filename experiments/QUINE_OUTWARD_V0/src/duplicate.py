#!/usr/bin/env python3
"""duplicate.py â€” Fase 4: two microcells, measure coexistence (v2).

Microcell = N=3 block. STATE_0 = [1,1,0] (window-lo1 sig 0), STATE_1 = [1,1,1]
(window-lo1 sig 1). Place TWO blocks A,B on a ring under crazy-fill in several
configurations; evolve; measure whether each block's signature cell is
preserved (independence), synced (coupling), or destroyed.

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

# A block = 3 cells starting at a_lo; its signature cell is a_lo+2.
# STATE_1 => signature 1 (cell a_lo+2 = 1); STATE_0 => signature 0.
def place(n, a_lo, b_lo, a_state, b_state):
    ring = [0]*n
    for lo, st in ((a_lo, a_state), (b_lo, b_state)):
        ring[lo] = 1; ring[lo+1] = 1; ring[lo+2] = st
    return ring

cases = [
    ("separated",         place(12, 1, 8, 1, 0), 1, 8),
    ("adjacent",          place(9,  1, 5, 1, 0), 1, 5),
    ("shared_boundary",   place(8,  1, 4, 1, 0), 1, 4),
    ("offset_A0_B1",      place(12, 2, 8, 0, 1), 2, 8),
    ("close_A1_B1",       place(9,  1, 5, 1, 1), 1, 5),
]

def classify(a0, a1, b0, b1):
    """a0/a1 = A sig before/after; b0/b1 = B sig before/after."""
    Aok = (a0 == a1); Bok = (b0 == b1)
    if Aok and Bok:
        kind = "INDEPENDENCE" if a1 != b1 else "SYNCHRONIZED"
    elif not Aok and not Bok:
        kind = "DESTRUCTION"
    else:
        kind = "PARTIAL"
    return kind

results = []
for name, ring, a_lo, b_lo in cases:
    a_sig0 = sig_at(ring, a_lo+2); b_sig0 = sig_at(ring, b_lo+2)
    f = evolve(ring, 300)
    a_sig1 = sig_at(f, a_lo+2); b_sig1 = sig_at(f, b_lo+2)
    results.append({
        "name": name, "n": len(ring),
        "A_sig_before": a_sig0, "A_sig_after": a_sig1,
        "B_sig_before": b_sig0, "B_sig_after": b_sig1,
        "kind": classify(a_sig0, a_sig1, b_sig0, b_sig1),
        "final_sha": hashlib.sha256(bytes(str(tuple(f)).encode())).hexdigest()[:16],
    })

print(json.dumps({"results": results}, indent=2))