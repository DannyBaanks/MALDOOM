#!/usr/bin/env python3
"""regions.py — per-step memory access tracker for the Lutter quine.

Fase 1: identify which memory cells participate in regeneration, classify
code/data/workspace/output-source/self-encryption-support regions, and detect
periodicity/complementarity — by OBSERVED access patterns, not assumptions.

Reuses the vendored interpreter (`_common.mi`, `vendor/malbolge/malbolge.py`).
Run with a bounded step count; the quine's output loop is periodic, so a
bounded window captures the mechanism.
"""
import sys
import hashlib
import json
from collections import defaultdict, Counter
from pathlib import Path

from _common import mi, load_quine_src

src = load_quine_src()
clean_sha = hashlib.sha256(src.encode()).hexdigest()
print(f"source len={len(src)} sha256={clean_sha}", file=sys.stderr)

MAX_STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
window = int(sys.argv[2]) if len(sys.argv) > 2 else MAX_STEPS  # track this window

# Access logs (bounded to window for memory)
reads = Counter()      # cell index -> how many times READ via mem[d] (op 4,39,40,62)
writes = Counter()     # cell index -> how many times WRITTEN (op 39,62, + self-encrypt)
code_use = Counter()   # cell index -> how many times executed as instruction (mem[c])
encrypted = Counter()  # cell index -> self-encrypted after execution
outs = []              # (step, a, c, d, memd, out)
step_by_op = Counter()

mem = mi.load_memory(src)
a = 0
c = 0
d = 0
steps = 0
out = []
first_out_step = None
last_out_step = None

# Pre-record the pristine initial memory hash (first 4096 cells + full checksum)
def mem_digest(m, n=4096):
    h = hashlib.sha256()
    for i in range(n):
        h.update(m[i].to_bytes(4, "little"))
    return h.hexdigest()

init_hash = mem_digest(mem)

while steps < MAX_STEPS:
    steps += 1
    cell = mem[c]
    op = (cell + c) % 94
    code_use[c] += 1
    step_by_op[op] += 1
    jumped = False
    c_target = 0
    if op == 4:
        reads[d] += 1
        c_target = mem[d]
        jumped = True
    elif op == 5:
        out.append(a % 256)
        if first_out_step is None:
            first_out_step = steps
        last_out_step = steps
        outs.append({"step": steps, "a": a, "c": c, "d": d, "memd": mem[d], "out": a % 256})
    elif op == 23:
        a = -1  # quine has no stdin
    elif op == 39:
        reads[d] += 1
        v = mem[d]
        mem[d] = (v // 3) + (v % 3) * (3 ** 9)
        a = mem[d]
        writes[d] += 1
    elif op == 40:
        reads[d] += 1
        d = mem[d]
    elif op == 62:
        reads[d] += 1
        mem[d] = mi.crazy_op(a, mem[d])
        a = mem[d]
        writes[d] += 1
    elif op == 68:
        pass
    elif op == 81:
        break
    else:
        pass  # NOP (invalid opcode)

    if jumped:
        c = c_target
    if 33 <= mem[c] <= 126:
        mem[c] = mi._ENC[mem[c]]
        encrypted[c] += 1
    c = (c + 1) % mi.MEM_SIZE
    d = (d + 1) % mi.MEM_SIZE

    # Track only within window to bound memory
    if steps >= window:
        break

final_hash = mem_digest(mem)

# ---- Analysis ----
read_set = set(reads)
write_set = set(writes)
code_set = set(code_use)
enc_set = set(encrypted)

# Classification by observed role:
#   code cells: executed as instruction
#   data cells: read via mem[d] but never executed
#   write cells: written by crazy/rot
#   encrypt-support: executed then self-encrypted (both code + encrypt)
roles = Counter()
for i in range(0, 4096):  # classify low window (program lives low)
    is_code = code_use[i] > 0
    is_data = reads[i] > 0
    is_written = writes[i] > 0
    is_enc = encrypted[i] > 0
    if is_code and is_enc:
        roles["code_selfencrypt"] += 1
    elif is_code:
        roles["code_only"] += 1
    elif is_data and is_written:
        roles["data_rw"] += 1
    elif is_data:
        roles["data_readonly"] += 1
    elif is_written:
        roles["write_only"] += 1
    else:
        roles["untouched"] += 1

# Range stats (min/max active cell)
all_active = (read_set | write_set | code_set)
if all_active:
    amin = min(all_active)
    amax = max(all_active)
else:
    amin = amax = None

result = {
    "source_len": len(src),
    "clean_sha256": clean_sha,
    "max_steps": MAX_STEPS,
    "window": window,
    "steps_run": steps,
    "init_mem_hash_4k": init_hash,
    "final_mem_hash_4k": final_hash,
    "num_outputs": len(out),
    "first_out_step": first_out_step,
    "last_out_step": last_out_step,
    "active_cells_total": len(all_active),
    "active_cell_min": amin,
    "active_cell_max": amax,
    "step_by_opcode": dict(sorted(step_by_op.items())),
    "roles_in_low_4k": dict(roles),
    "top_read_cells": reads.most_common(10),
    "top_write_cells": writes.most_common(10),
    "top_code_cells": code_use.most_common(10),
    "output_bytes_head": bytes(out[:40]).decode("latin-1", "replace"),
}

print(json.dumps(result, indent=2))