#!/usr/bin/env python3
"""ca_model.py â€” Fase 2/3: MALBOLGE_MEMORY_AS_CA_MODEL (experimental model).

NOT an assertion that "Malbolge IS a CA". A discrete-ring model used to search
*configurations* (seeds/regions) for structure that we then validate on the
real VM.

Model for a ring of N cells with the SAME rules the real VM uses for memory.
Cell indices wrap around (index `(i mod N)`), which is how a finite ring is
indexed in this experiment:
  - fill/expansion:   mem[i] = crazy(mem[i-1], mem[i-2])   (radius-2, wraparound)
  - self-encryption:  executed code cell -> ENCRYPT[cell]   (mutation)
  - crazy op:         mem[d] = crazy(a, mem[d])
  - rotate op:        mem[d] = rotate3(mem[d])

We search small seed configurations for:
  - cycles / fixed points / attractors
  - a *region signature* (e.g. sum mod 3^w of a window, or period) that is
    stable and distinguishes two states.

Faithful: uses the canonical crazy/rotate/encrypt definitions.
"""
import sys, json, hashlib
from _common import mi
CRAZY = mi.crazy_op
ROT3 = lambda v: (v // 3) + (v % 3) * (3 ** 9)

def crazy_fill(a, b):
    return CRAZY(a, b)

def evolve_ring(seed, steps, encrypt=None):
    """Evolve a ring under radius-2 crazy fill. `encrypt` is a set of indices
    that get self-encrypted each step (code mutation model)."""
    n = len(seed)
    ring = list(seed)
    if encrypt is None:
        encrypt = set()
    snapshots = [tuple(ring)]
    for _ in range(steps):
        nxt = [0] * n
        for i in range(n):
            nxt[i] = crazy_fill(ring[(i-1) % n], ring[(i-2) % n])
        for i in encrypt:
            if 33 <= nxt[i] <= 126:
                nxt[i] = mi._ENC[nxt[i]]
        ring = nxt
        snapshots.append(tuple(ring))
    return ring, snapshots

def find_period(ring, steps=1000):
    seen = {}
    cur = list(ring)
    for t in range(steps):
        h = tuple(cur)
        if h in seen:
            return t - seen[h]
        seen[h] = t
        cur = [crazy_fill(cur[(i-1) % len(cur)], cur[(i-2) % len(cur)]) for i in range(len(cur))]
    return None

def region_sig(ring, lo, hi):
    return sum(ring[lo:hi]) % (3 ** (hi - lo))

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="symmetric")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--window", type=int, default=3)
    a = ap.parse_args()

    n = a.n
    # two seed families: single pulse vs double pulse
    seeds = {
        "s0": [0]*n, "s1": [0]*n,
    }
    seeds["s0"][0] = 1; seeds["s0"][1] = 1
    seeds["s1"][0] = 1; seeds["s1"][1] = 1; seeds["s1"][2] = 1

    out = {}
    for name, seed in seeds.items():
        ring, snaps = evolve_ring(seed, a.steps)
        period = find_period(ring)
        out[name] = {
            "seed": seed,
            "final": ring,
            "period": period,
            "final_sha": hashlib.sha256(bytes(str(tuple(ring)).encode())).hexdigest()[:16],
        }
    # distinguishability of window signatures across the two seeds
    s0 = out["s0"]["final"]
    s1 = out["s1"]["final"]
    w = a.window
    distinct = {}
    for lo in range(0, n - w + 1):
        distinct[str(lo)] = region_sig(s0, lo, lo+w) != region_sig(s1, lo, lo+w)
    print(json.dumps({
        "model": "MALBOLGE_MEMORY_AS_CA_MODEL",
        "n": n, "steps": a.steps, "window": w,
        "seeds": out,
        "window_signatures_distinct": distinct,
        "any_distinct": any(distinct.values()),
    }, indent=2))

if __name__ == "__main__":
    main()