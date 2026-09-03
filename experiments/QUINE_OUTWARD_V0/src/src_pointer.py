#!/usr/bin/env python3
"""src_pointer.py Ã¢â‚¬â€ Fase 1: find WHICH cell feeds 'a' before each OUT.

The QUINE emits its source one byte at a time. d at OUT is fixed (29454) and
memd fixed, but 'out' changes => 'a' must be loaded from a moving cell by an
op 62/39/23 in the steps just before OUT. We record the last cell that set 'a'
via op 39/62/23 and its index, across the output loop, to reveal the source
cursor (the "odometer" that advances through the 59032-byte source).
"""
import sys, json, hashlib
from _common import mi, load_quine_src
src = load_quine_src()
MAX_STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 300000

mem = mi.load_memory(src)
a = c = d = steps = 0
last_a_src = None      # (op, cell_index, cell_value) that last set a
a_history = []         # (step, op, cell_idx, value, a_after)

while steps < MAX_STEPS:
    steps += 1
    cell = mem[c]
    op = (cell + c) % 94
    jumped = False
    if op == 4:
        c_target = mem[d]; jumped = True
    elif op == 5:
        a_history.append({
            "step": steps, "out": a % 256, "a_src": last_a_src,
            "c": c, "d": d, "memd": mem[d],
        })
    elif op == 23:
        a = -1
        last_a_src = (23, None, None)
    elif op == 39:
        v = mem[d]
        mem[d] = (v // 3) + (v % 3) * (3 ** 9)
        a = mem[d]
        last_a_src = (39, d, v)
    elif op == 40:
        d = mem[d]
    elif op == 62:
        v = mem[d]
        mem[d] = mi.crazy_op(a, mem[d])
        a = mem[d]
        last_a_src = (62, d, v)
    elif op == 81:
        break
    if jumped:
        c = c_target
    if 33 <= mem[c] <= 126:
        mem[c] = mi._ENC[mem[c]]
    c = (c + 1) % mi.MEM_SIZE
    d = (d + 1) % mi.MEM_SIZE

# Show first 40 outs with their a_src
print(json.dumps({
    "steps": steps, "num_outs": len(a_history),
    "sample": a_history[:40],
}, indent=2))