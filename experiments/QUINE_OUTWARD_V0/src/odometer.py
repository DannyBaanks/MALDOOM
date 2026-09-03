#!/usr/bin/env python3
"""odometer.py Ã¢â‚¬â€ Fase 1: track cell 154 (and neighbors) across OUT events.

Hypothesis: cell ~154 is a low "odometer"/data-pointer that advances the
source byte being emitted by the high code region. We record mem[154], mem[155],
mem[d] and the emitted byte at each OUT, to see the coupling.
"""
import sys, json, hashlib
from _common import mi, load_quine_src
src = load_quine_src()
MAX_STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 300000

mem = mi.load_memory(src)
a = c = d = steps = 0
out_events = []

while steps < MAX_STEPS:
    steps += 1
    cell = mem[c]
    op = (cell + c) % 94
    jumped = False
    if op == 4:
        c_target = mem[d]; jumped = True
    elif op == 5:
        out_events.append({
            "step": steps, "c": c, "d": d, "memd": mem[d], "out": a % 256,
            "m154": mem[154], "m155": mem[155], "m152": mem[152],
            "m153": mem[153], "a": a,
        })
    elif op == 23:
        a = -1
    elif op == 39:
        mem[d] = (mem[d] // 3) + (mem[d] % 3) * (3 ** 9); a = mem[d]
    elif op == 40:
        d = mem[d]
    elif op == 62:
        mem[d] = mi.crazy_op(a, mem[d]); a = mem[d]
    elif op == 81:
        break
    if jumped:
        c = c_target
    if 33 <= mem[c] <= 126:
        mem[c] = mi._ENC[mem[c]]
    c = (c + 1) % mi.MEM_SIZE
    d = (d + 1) % mi.MEM_SIZE

# Show first 30 and check if m154 maps to emitted byte
print(json.dumps({
    "steps": steps,
    "num_outs": len(out_events),
    "sample": out_events[:30],
    "note": "check whether emitted 'out' correlates with m154/memd/pointer",
}, indent=2))