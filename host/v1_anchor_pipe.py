#!/usr/bin/env py
"""
v1_anchor_pipe.py — dumb pipe for V1

Allowed: Popen, read stdout, detect framing, write stdin, store opaque bytes, SHA, PID, timing
Forbidden: anchor_decode, anchor_encode, epoch, acc, rng, reference_step, split("-"), int(anchor), checksum, state
"""
import subprocess, hashlib
from pathlib import Path
# This is a stub — will be implemented when program_v1.mal exists
# Static audit must find 0 hits for forbidden helpers
# forbidden = ["anchor_decode", "anchor_encode", "epoch", "acc", "rng", "reference_step", "split", "int(", "checksum", "state"]

def run():
    print("v1_anchor_pipe stub — program_v1.mal not yet generated")
    print("HOST_PARSES_ANCHOR=no (when implemented)")

if __name__ == "__main__":
    run()
