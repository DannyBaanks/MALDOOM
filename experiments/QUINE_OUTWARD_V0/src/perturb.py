#!/usr/bin/env python3
"""perturb.py Ã¢â‚¬â€ Fase 1b: causality of the tape cells (Q6/Q7).

Run the QUINE to step S (>= first OUT), then flip ONE tape cell (in 29516..)
and continue. Compare output vs an unperturbed control:
  - does the perturbation change only the corresponding emitted byte(s)?
  - does the loop continue (regeneration) or die?
  - does it propagate or stabilize?
Reuses canonical interpreter. Faithful VM.
"""
import sys, json, hashlib
from _common import mi, load_quine_src
src = load_quine_src()

def run(perturb_cell=None, perturb_at=0, flip=0, max_steps=40000):
    mem = mi.load_memory(src)
    a = c = d = steps = 0
    out = []
    while steps < max_steps:
        steps += 1
        if perturb_cell is not None and steps == perturb_at:
            mem[perturb_cell] = mem[perturb_cell] ^ flip  # flip a bit
        cell = mem[c]
        op = (cell + c) % 94
        jumped = False
        if op == 4:
            c_target = mem[d]; jumped = True
        elif op == 5:
            out.append(a % 256)
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
    return bytes(out).decode("latin-1", "replace")

PERTURB_AT = 30000  # after first few OUTs
# control
ctrl = run(max_steps=40000)
print(json.dumps({
    "source_len": len(src),
    "perturb_at": PERTURB_AT,
    "control_len": len(ctrl),
    "control_tail": ctrl[-30:],
}, indent=2))

# perturb each of first 6 tape cells
for k in range(6):
    cell = 29516 + k
    r = run(perturb_cell=cell, perturb_at=PERTURB_AT, flip=1, max_steps=40000)
    # find first divergence from control
    diverge = None
    for i, (a, b) in enumerate(zip(ctrl, r)):
        if a != b:
            diverge = i
            break
    print(json.dumps({
        "perturbed_cell": cell,
        "out_len": len(r),
        "first_diverge_byte_index": diverge,
        "matches_control_len": len(r) == len(ctrl),
        "loop_survived": len(r) >= 100,  # still emitting after perturbation
    }))