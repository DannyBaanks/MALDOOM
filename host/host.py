#!/usr/bin/env py
"""
host/host.py — DUMB I/O bridge. Must NOT compute Doom gameplay.

Allowed: framebuffer blit, input transport, timing, WAD byte transport.
Forbidden: gameplay tick, player movement, thinker runner, random (see AGENTS.md).
           No collision, AI, RNG, WAD semantic parsing, S_t -> S_{t+1}.

This file is audited by tests/test_engine_does_the_work.py via grep.
If you add gameplay logic here, the demonstration fails by definition.
"""
import argparse, sys, time, hashlib
from pathlib import Path

# ALLOWED surface — if you need anything else, it belongs in engine/*.mu

def dg_init(width=320, height=200, title="MALDOOM"):
    # create window / allocate framebuffer — stub for M0 (no window yet)
    print(f"[host] DG_Init {width}x{height} title={title}", file=sys.stderr)
    return {"width": width, "height": height, "buffer": bytearray(width*height*4)}

def dg_draw_frame(screen_buffer: bytes):
    # in M0, just hash the buffer; in M5+, blit to window
    h = hashlib.sha256(screen_buffer).hexdigest()[:16]
    print(f"[host] DG_DrawFrame hash={h} size={len(screen_buffer)}", file=sys.stderr)

def dg_sleep_ms(ms: int):
    time.sleep(ms/1000.0)

def dg_get_ticks_ms() -> int:
    return int(time.time()*1000) & 0x7fffffff

def dg_get_key():
    # transport only — read from stdin queue in tests
    return None

def dg_set_window_title(title: str):
    print(f"[host] title={title}", file=sys.stderr)

def wad_byte_transport(path: Path) -> bytes:
    # strictly I/O — deliver raw bytes to engine, no parsing
    data = Path(path).read_bytes()
    print(f"[host] WAD bytes {len(data)} from {path} sha256 {hashlib.sha256(data).hexdigest()[:16]}", file=sys.stderr)
    return data

def main():
    ap = argparse.ArgumentParser(description="MALDOOM dumb host — I/O only")
    ap.add_argument("artifact", nargs="?", help=".mu to run via Unshackled VM")
    ap.add_argument("--verify-audit", action="store_true", help="check host contains no gameplay symbols")
    args = ap.parse_args()
    if args.verify_audit:
        src = Path(__file__).read_text(encoding="utf-8")
        # reconstruct to avoid literal self-match
        forbidden = ["doomgeneric"+"_"+"Tick","P_"+"MovePlayer","P_"+"RunThinkers","M_"+"Random","P_"+"CheckPosition","WI_"+"Ticker"]
        found = [s for s in forbidden if s in src]
        # exclude this audit block itself from search
        if found:
            # check if found only inside this audit literal reconstruction — already excluded by split
            print(f"HOST_STOLE_COMPUTATION: found {found} in host/host.py", file=sys.stderr)
            sys.exit(2)
        print("host audit PASS — no gameplay symbols", file=sys.stderr)
        sys.exit(0)
    if args.artifact:
        # delegate to VM — host does not interpret WAD or tick
        print(f"[host] would exec Unshackled VM on {args.artifact}", file=sys.stderr)
        # actual exec is done by scripts/build_m0.py via vendor/Unshackled
        sys.exit(0)
    ap.print_help()

if __name__ == "__main__":
    main()
