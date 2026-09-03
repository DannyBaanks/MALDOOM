#!/usr/bin/env python3
"""mechanism.py — Fase 1: isolate the quine's regeneration/output mechanism.

Focused analysis on the REAL Lutter quine:
  - which distinct low cells (0..4096) are used and as what
  - the output-loop working region (~29k) and the distant low cell(s) (~154)
  - periodicity of the output loop (steps between OUTs, cell-access pattern)
  - whether two complementary regions exist (structure that can be composed)

Reuses the canonical interpreter. Bounded steps; loop is periodic.
"""
import sys
import json
import hashlib
from collections import Counter, defaultdict

from _common import mi, load_quine_src

src = load_quine_src()
MAX_STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 300000

mem = mi.load_memory(src)
a = c = d = steps = 0
out = []
read_lo = Counter(); write_lo = Counter(); code_lo = Counter()   # cells < 4096
read_hi = Counter(); write_hi = Counter(); code_hi = Counter()   # cells >= 4096
out_events = []
# region working around the dominant code block
hi_range_min, hi_range_max = None, None

def note(region_counter, i):
    pass

while steps < MAX_STEPS:
    steps += 1
    cell = mem[c]
    op = (cell + c) % 94
    jumped = False
    c_target = 0
    if c < 4096:
        code_lo[c] += 1
    else:
        code_hi[c] += 1
        if hi_range_min is None or c < hi_range_min: hi_range_min = c
        if hi_range_max is None or c > hi_range_max: hi_range_max = c
    if op == 4:
        if d < 4096: read_lo[d] += 1
        else: read_hi[d] += 1
        c_target = mem[d]; jumped = True
    elif op == 5:
        out.append(a % 256)
        out_events.append((steps, c, d, mem[d], a % 256))
    elif op == 23:
        a = -1
    elif op == 39:
        if d < 4096: read_lo[d] += 1; write_lo[d] += 1
        else: read_hi[d] += 1; write_hi[d] += 1
        mem[d] = (mem[d] // 3) + (mem[d] % 3) * (3 ** 9); a = mem[d]
    elif op == 40:
        if d < 4096: read_lo[d] += 1
        else: read_hi[d] += 1
        d = mem[d]
    elif op == 62:
        if d < 4096: read_lo[d] += 1; write_lo[d] += 1
        else: read_hi[d] += 1; write_hi[d] += 1
        mem[d] = mi.crazy_op(a, mem[d]); a = mem[d]
    elif op == 68:
        pass
    elif op == 81:
        break
    if jumped:
        c = c_target
    if 33 <= mem[c] <= 126:
        mem[c] = mi._ENC[mem[c]]
    c = (c + 1) % mi.MEM_SIZE
    d = (d + 1) % mi.MEM_SIZE

# ---- periodic output loop ----
out_steps = [e[0] for e in out_events]
gaps = [out_steps[i+1]-out_steps[i] for i in range(len(out_steps)-1)]
gap_counter = Counter(gaps)

# dominant low cells
low_all = set(read_lo) | set(write_lo) | set(code_lo)
lo_buckets = defaultdict(int)
for i in low_all:
    lo_buckets[(i // 100) * 100] += 1

result = {
    "source_len": len(src),
    "clean_sha256": hashlib.sha256(src.encode()).hexdigest(),
    "steps_run": steps,
    "num_outputs": len(out),
    "out_interval_counter_top": gap_counter.most_common(10),
    "out_first_10": out_events[:10],
    "out_last_5": out_events[-5:],
    "low_region_buckets_100": dict(sorted(lo_buckets.items())),
    "top_low_read": read_lo.most_common(10),
    "top_low_write": write_lo.most_common(10),
    "top_low_code": code_lo.most_common(10),
    "hi_range": [hi_range_min, hi_range_max],
    "top_hi_read": read_hi.most_common(8),
    "top_hi_write": write_hi.most_common(8),
    "top_hi_code": code_hi.most_common(8),
}
print(json.dumps(result, indent=2))