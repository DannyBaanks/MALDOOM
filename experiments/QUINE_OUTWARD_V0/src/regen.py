#!/usr/bin/env python3
"""regen.py â€” Fase 7: regeneration after damage / basin of attraction.

Take the microcell STATE_1 = [1,1,1] (signature cell lo+2 = 1) embedded in a
ring. Damage it (flip one cell, or a few) then evolve; measure whether the
signature cell returns to 1 (regeneration) and how many distinct single-cell
and multi-cell perturbations are tolerated (basin size).

Faithful crazy rule. Model = MALBOLGE_MEMORY_AS_CA_MODEL.
"""
import json, itertools
from _common import mi
CRAZY = mi.crazy_op

def evolve(seed, steps):
    n = len(seed); ring = list(seed)
    for _ in range(steps):
        nxt = [CRAZY(ring[(i-1) % n], ring[(i-2) % n]) for i in range(n)]
        ring = nxt
    return ring

# ring with a single microcell at lo, STATE_1 (signature cell lo+2 = 1)
N = 8; LO = 2; SIG = LO+2
base = [0]*N
base[LO]=1; base[LO+1]=1; base[LO+2]=1
SIG_EXPECTED = 1

# 1) single-cell damage over the whole ring
single_recover = []
for i in range(N):
    d = list(base)
    d[i] = (d[i] + 1) % 3   # bump one cell by 1 trit
    f = evolve(d, 300)
    single_recover.append({"cell": i, "sig_after": f[SIG] % 3, "regenerated": (f[SIG]%3)==SIG_EXPECTED})

# 2) multi-cell damage: flip signature cell + one neighbor
multi_recover = []
for i in range(N):
    d = list(base)
    d[SIG] = (d[SIG]+1)%3
    d[i] = (d[i]+1)%3
    f = evolve(d, 300)
    multi_recover.append({"flip2": (SIG, i), "sig_after": f[SIG]%3, "regenerated": (f[SIG]%3)==SIG_EXPECTED})

print(json.dumps({
    "model": "MALBOLGE_MEMORY_AS_CA_MODEL",
    "N": N, "LO": LO, "SIG": SIG, "expected": SIG_EXPECTED,
    "single_cell_damage": single_recover,
    "single_ok": sum(1 for r in single_recover if r["regenerated"]),
    "multi_cell_damage": multi_recover,
    "multi_ok": sum(1 for r in multi_recover if r["regenerated"]),
}, indent=2))