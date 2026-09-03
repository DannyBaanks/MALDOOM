"""Malbolge interpreter (Classic, 3^10 / 59049-cell memory), self-contained.

A faithful implementation of the reference Malbolge semantics. The algorithm
follows the public-language description: Iizawa (2005) Appendix C, itself a
transcription of the reference interpreter that has circulated publicly since
1998 (`malbolge.c`). No external dependency.

API:
  run(source, max_steps, stdin_data, on_step) -> (text, steps, status)
  load_memory(source) -> list[int] (59049 cells, crazy-filled tail)
  crazy_op(x, y) -> int   (ternary "crazy" op, tritwise)
  _ENC                    (self-encryption table)
  MEM_SIZE = 3 ** 10 = 59049

This module is MALDOOM-local tooling: it runs experiments over Classic
Malbolge memory. It is NOT game semantics and never computes Doom state.
"""
from __future__ import annotations

MEM_SIZE = 3 ** 10

_ORIGINAL = r"""!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"""
_TRANSLATED = r"""5z]&gqtyfr$(we4{WP)H-Zn,[%\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G"i@"""
assert len(_ORIGINAL) == 94 and len(_TRANSLATED) == 94
_ENC = {ord(o): ord(t) for o, t in zip(_ORIGINAL, _TRANSLATED)}

_CRAZY = (
    (1, 0, 0),
    (1, 0, 2),
    (2, 2, 1),
)


def crazy_op(x: int, y: int) -> int:
    res = 0
    p = 1
    for _ in range(10):
        res += _CRAZY[y % 3][x % 3] * p
        x //= 3
        y //= 3
        p *= 3
    return res


def load_memory(source: str) -> list:
    chars = [c for c in source if not c.isspace()]
    mem = [0] * MEM_SIZE
    for i, c in enumerate(chars):
        v = ord(c)
        if not (33 <= v <= 126):
            raise ValueError("non-printable source char at %s: %s" % (i, v))
        mem[i] = v
    for i in range(len(chars), MEM_SIZE):
        mem[i] = crazy_op(mem[i - 1], mem[i - 2])
    return mem


def run(source: str, max_steps: int = 2000000, stdin_data: str = "", on_step=None):
    try:
        mem = load_memory(source)
    except ValueError as e:
        return "", 0, "INVALID:%s" % e

    a = 0
    c = 0
    d = 0
    out = []
    stdin_iter = iter(stdin_data)
    steps = 0

    while steps < max_steps:
        steps += 1
        cell = mem[c]
        op = (cell + c) % 94
        if on_step is not None:
            on_step(steps, a, c, d, op, cell)
        jumped = False
        c_target = 0

        if op == 4:
            c_target = mem[d]
            jumped = True
        elif op == 5:
            out.append(a % 256)
        elif op == 23:
            ch = next(stdin_iter, None)
            a = -1 if ch is None else ord(ch)
        elif op == 39:
            v = mem[d]
            mem[d] = (v // 3) + (v % 3) * (3 ** 9)
            a = mem[d]
        elif op == 40:
            d = mem[d]
        elif op == 62:
            mem[d] = crazy_op(a, mem[d])
            a = mem[d]
        elif op == 68:
            pass
        elif op == 81:
            return bytes(out).decode("latin-1"), steps, "HALTED"
        else:
            pass

        if jumped:
            c = c_target
        if 33 <= mem[c] <= 126:
            mem[c] = _ENC[mem[c]]
        c = (c + 1) % MEM_SIZE
        d = (d + 1) % MEM_SIZE

    return bytes(out).decode("latin-1"), steps, "MAX_STEPS"


HELLO_WORLD_SRC = r"""(=<`#9]~6ZY327Uv4-QsqpMn&+Ij"'E%e{Ab~w=_:]Kw%o44Uqp0/Q?xNvL:`H%c#DD2^WV>gY;dts76qKJImZkj"""


if __name__ == "__main__":
    text, steps, status = run(HELLO_WORLD_SRC)
    print("status=%s steps=%s" % (status, steps))
    print("output=%r" % text)
    ok = status == "HALTED" and "Hello" in text and "world" in text.lower()
    raise SystemExit(0 if ok else 1)