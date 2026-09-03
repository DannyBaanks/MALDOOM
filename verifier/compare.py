#!/usr/bin/env py
"""
verifier/compare.py — dumb hash compare. Does not compute gameplay.

Compares H(engine_output) vs H(reference_output). The only allowed
computation is hashing / diffing bytes.

Usage:
  py verifier/compare.py --expected evidence/M0_A_CONST/expected.bin --observed evidence/M0_A_CONST/observed.bin
"""
import argparse, hashlib, json, sys
from pathlib import Path

def sha256(b: bytes): return hashlib.sha256(b).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected", required=True)
    ap.add_argument("--observed", required=True)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()
    exp = Path(args.expected).read_bytes() if Path(args.expected).exists() else b""
    obs = Path(args.observed).read_bytes() if Path(args.observed).exists() else b""
    he, ho = sha256(exp), sha256(obs)
    ok = he == ho
    print(f"expected sha256 {he} size {len(exp)}")
    print(f"observed sha256 {ho} size {len(obs)}")
    print(f"match={ok}")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps({"expected_sha":he,"observed_sha":ho,"match":ok,"expected_size":len(exp),"observed_size":len(obs)}, indent=2))
    sys.exit(0 if ok else 1)

if __name__=="__main__": main()
