#!/usr/bin/env py
"""
generator.py — stub for V1 Malbolge-owned anchor program

Shows how to generate Classic Malbolge via XLAT1 encoding and J+large-K.

For V1, full automaton needs ~100 instructions with J to get large K via fill.
This stub generates a minimal INPUT prompt and a single CRAZY that would
transform input trit '0'/'1'/'2' via large K, demonstrating the technique.

The full search is not run in this checkpoint — honestly labeled NOT_DEMONSTRATED.
"""
XLAT1 = "+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA\"lI.v%{gJh4G\\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha"

def enc(inst, pos):
    return chr((XLAT1.index(inst) - pos) % 94 + 33)

def dec(ch, pos):
    return XLAT1[(ord(ch)-33+pos)%94]

# Example: generate "INPUT\n" prompt as OUT sequence
prompt = "INPUT\n"
ops = []
for ch in prompt:
    # For each char to output, we need to have 'a' contain that char then OUT
    # In real program, 'a' would be set via CRAZY from state, here we just demonstrate encoding
    ops.append('<')  # OUT
# Encode
prog = ''.join(enc(op, i) for i, op in enumerate(ops))
print(f"prompt INPUT\\n as {len(ops)} OUTs -> prog len {len(prog)}")
for i, ch in enumerate(prog):
    print(f" pos {i}: mem={ord(ch)} -> {dec(ch,i)!r}")

# Demonstrate J+large-K idea:
# To get large K, we need mem[d] beyond program.
# If program len is L, mem[L] = crazy(mem[L-1], mem[L-2]) is large.
# J does d = mem[d], so after J with d pointing to L, d becomes large, next P uses mem[d] large.
# This stub shows the concept without full search.

print("\nV1 generator stub — full state machine requires cycle search for ~100 ops")
print("Next: brute-force J/P sequences for 27 states x 3 inputs, each with K via large mem[d]")
print("Estimated: hours of search on this host, not run in this checkpoint")
print("CLASSIC_ANCHOR_PRIMITIVE_NOT_DEMONSTRATED for V1 (host-assisted V0 is current best)")
