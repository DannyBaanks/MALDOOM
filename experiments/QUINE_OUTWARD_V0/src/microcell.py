#!/usr/bin/env python3
"""microcell.py â€” Fase 3: find the smallest ring whose window-signature
distinguishes two states stably (periodic attractor), and record the minimal
microcell. Faithful crazy rule. Model = MALBOLGE_MEMORY_AS_CA_MODEL."""
import sys, json, hashlib
from _common import mi
CRAZY = mi.crazy_op

def evolve(seed, steps):
    n = len(seed); ring = list(seed)
    for _ in range(steps):
        nxt = [CRAZY(ring[(i-1) % n], ring[(i-2) % n]) for i in range(n)]
        ring = nxt
    return ring

def period(ring, cap=2000):
    seen = {}; cur = list(ring); n = len(ring)
    for t in range(cap):
        h = tuple(cur)
        if h in seen: return t - seen[h]
        seen[h] = t
        cur = [CRAZY(cur[(i-1) % n], cur[(i-2) % n]) for i in range(n)]
    return None

def sig(ring, lo, w): return sum(ring[lo:lo+w])

def main():
    results = []
    best = None
    # seeds: single pulse (s0) vs double pulse (s1), differ in one cell
    for n in range(3, 13):
        s0 = [0]*n; s0[0]=1; s0[1]=1
        s1 = [0]*n; s1[0]=1; s1[1]=1; s1[2]=1
        f0 = evolve(s0, 200); f1 = evolve(s1, 200)
        p0 = period(f0); p1 = period(f1)
        # find minimal window w where sig differs and is stable
        distinct_window = None
        for w in range(1, n):
            for lo in range(0, n-w+1):
                if sig(f0, lo, w) != sig(f1, lo, w):
                    distinct_window = {"w": w, "lo": lo,
                                       "sig0": sig(f0, lo, w), "sig1": sig(f1, lo, w)}
                    break
            if distinct_window: break
        row = {"n": n, "period0": p0, "period1": p1,
               "min_distinct_window": distinct_window}
        results.append(row)
        if distinct_window and p0 and p1:
            if best is None or n < best["n"]:
                best = {"n": n, **row}
    print(json.dumps({
        "results": results,
        "smallest_microcell": best,
        "note": "microcell = (n, window lo..lo+w) with stable distinct signature",
    }, indent=2))

if __name__ == "__main__":
    main()