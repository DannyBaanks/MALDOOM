#!/usr/bin/env python3
"""macrocell.py â€” Fase 6: lifting. Treat (A|S|B) as one unit C with a macro
signature, then compose two such units C1+C2 and test whether a structural
property survives the lift.

Model = MALBOLGE_MEMORY_AS_CA_MODEL. Faithful crazy rule.
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

# Build a macrocell C from two microcells with a SEAM of g between them.
# A at lo, B at lo+3+g. Macro signature = (sigA, sigB) => a 2-trit state.
def macrocell(n, lo, g, a_state, b_state):
    ring = [0]*n
    ring[lo]=1; ring[lo+1]=1; ring[lo+2]=a_state
    b_lo = lo+3+g
    ring[b_lo]=1; ring[b_lo+1]=1; ring[b_lo+2]=b_state
    return ring, lo, b_lo

SEAM_G = 1  # minimal working seam from Fase 5

def macro_sig(f, a_lo, b_lo):
    return (sig_at(f, a_lo+2), sig_at(f, b_lo+2))

results = {}
# Single macrocell C = (A=STATE_1, B=STATE_0) with seam 1
n_C = 12
C, a_lo, b_lo = macrocell(n_C, 2, SEAM_G, 1, 0)
C0 = macro_sig(C, a_lo, b_lo)                 # signature before
Cf = evolve(C, 300)
C_after = macro_sig(Cf, a_lo, b_lo)
results["C_alone"] = {"before": list(C0), "after": list(C_after),
                      "preserved": C0 == C_after}

# Now lift: two macrocells C1, C2, each = (A=1,B=0) with seam, separated by gap G
def place_ring(n, lo1, lo2, g):
    ring = [0]*n
    for lo, a_state, b_state in ((lo1, 1, 0), (lo2, 1, 0)):
        ring[lo]=1; ring[lo+1]=1; ring[lo+2]=a_state
        b = lo+3+g
        ring[b]=1; ring[b+1]=1; ring[b+2]=b_state
    return ring

for G in (1, 2, 3, 4):
    lo1 = 2
    span = 3 + SEAM_G + 3     # A(3) + seam + B(3)
    lo2 = lo1 + span + G
    n = lo2 + span + 2
    ring = place_ring(n, lo1, lo2, SEAM_G)
    a1, b1 = lo1, lo1+3+SEAM_G
    a2, b2 = lo2, lo2+3+SEAM_G
    f = evolve(ring, 300)
    c1_after = macro_sig(f, a1, b1)
    c2_after = macro_sig(f, a2, b2)
    both = c1_after == (1,0) and c2_after == (1,0)
    results[f"two_macrocells_G{G}"] = {
        "C1_after": list(c1_after), "C2_after": list(c2_after),
        "both_preserved": both,
        "final_sha": hashlib.sha256(bytes(str(tuple(f)).encode())).hexdigest()[:16],
    }

print(json.dumps(results, indent=2))