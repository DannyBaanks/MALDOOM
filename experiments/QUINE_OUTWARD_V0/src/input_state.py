#!/usr/bin/env python3
"""input_state.py â€” Fase 8: INPUT -> persistent distinguishable state.

Show that injecting a 0/1 input as the starting state bit of a microcell leads
to two persistent, distinguishable signatures after long evolution â€” WITHOUT
editing the result (input only fixes the initial state, observation is of the
final evolved state). Faithful crazy rule.

Also demonstrates that the signature is readable by a third party who does NOT
know what was injected (it emerges from the observed state).
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

def sig(ring, lo, w=3): return sum(ring[lo:lo+w]) % (3**w)

N = 8; LO = 2
def seed_for(inp):
    s = [0]*N
    s[LO]=1; s[LO+1]=1; s[LO+2]=inp   # input 0 or 1 as the state bit
    return s

result = {}
for inp in (0, 1):
    ring = seed_for(inp)
    before = sig(ring, LO)
    f0 = evolve(ring, 100)
    f1 = evolve(ring, 1000)
    result[f"input_{inp}"] = {
        "state_bit": inp,
        "sig_before": before,
        "sig_after_100": sig(f0, LO),
        "sig_after_1000": sig(f1, LO),
        "final_sha": hashlib.sha256(bytes(str(tuple(f1)).encode())).hexdigest()[:16],
    }

# distinguishability at each horizon
dist_100 = result["input_0"]["sig_after_100"] != result["input_1"]["sig_after_100"]
dist_1000 = result["input_0"]["sig_after_1000"] != result["input_1"]["sig_after_1000"]
print(json.dumps({
    "model": "MALBOLGE_MEMORY_AS_CA_MODEL",
    "N": N, "LO": LO,
    "results": result,
    "distinguishable_at_100": dist_100,
    "distinguishable_at_1000": dist_1000,
}, indent=2))