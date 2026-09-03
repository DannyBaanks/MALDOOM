#!/usr/bin/env py
"""
fetch_toolchain.py — clone pinned toolchain into vendor/

Uses TOOLCHAIN_LOCK.json, clones at exact commit, records SHA-256 of
Unshackled.c/hs files. No host gameplay computation.

Usage:
  py scripts/fetch_toolchain.py --lock TOOLCHAIN_LOCK.json [--vendor vendor]
  py scripts/fetch_toolchain.py --verify  # check existing vendor matches lock
"""
import argparse, json, hashlib, subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_DEFAULT = ROOT / "TOOLCHAIN_LOCK.json"

def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr, file=sys.stderr)
    if r.returncode != 0:
        raise SystemExit(f"command failed {r.returncode}: {' '.join(cmd)}")
    return r

def sha256(p: Path):
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()

def clone_at(url, commit, dest: Path):
    if dest.exists():
        print(f"vendor exists: {dest} — verifying commit")
        r = subprocess.run(["git","rev-parse","HEAD"], cwd=dest, capture_output=True, text=True)
        got = r.stdout.strip()
        if got == commit:
            print(f"  ok {got}")
            return
        else:
            print(f"  mismatch {got} != {commit}, re-cloning")
            import shutil; shutil.rmtree(dest)
    run(["git","clone", url, str(dest)])
    run(["git","checkout", commit], cwd=dest)
    # verify no extra changes
    run(["git","status","--porcelain"], cwd=dest)

def fetch_file(url, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"exists {dest} hash {sha256(dest)[:12]}")
        return
    print(f"fetch {url} -> {dest}")
    import urllib.request
    urllib.request.urlretrieve(url, dest)
    print(f"  sha256 {sha256(dest)}  size {dest.stat().st_size}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", default=str(LOCK_DEFAULT))
    ap.add_argument("--vendor", default="vendor")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    lock = json.loads(Path(args.lock).read_text(encoding="utf-8"))
    vendor = ROOT / args.vendor
    vendor.mkdir(parents=True, exist_ok=True)

    for e in lock["toolchain"]:
        name = e["name"]
        if name in ("Unshackled.c","Unshackled.hs"):
            # file fetch
            url = e["url"]
            dest = vendor / ("Unshackled.c" if name=="Unshackled.c" else "Unshackled.hs")
            if not args.verify:
                fetch_file(url, dest)
                if dest.exists():
                    h = sha256(dest)
                    print(f"  {name} sha256 {h}")
            else:
                if not dest.exists():
                    print(f"MISSING {dest}")
                    sys.exit(1)
                print(f"{name} {sha256(dest)[:16]} {dest}")
        else:
            url = e["url"]; commit = e["commit"]
            dest = vendor / name
            if not args.verify:
                clone_at(url, commit, dest)
            else:
                if not dest.exists():
                    print(f"MISSING {dest}")
                    sys.exit(1)
                r = subprocess.run(["git","rev-parse","HEAD"], cwd=dest, capture_output=True, text=True)
                got = r.stdout.strip()
                status = "OK" if got==commit else f"MISMATCH got={got} want={commit}"
                print(f"{name:12} {status}")

    # integrity manifest
    manifest = []
    for p in vendor.rglob("*"):
        if p.is_file() and p.suffix in (".c",".hs",".py",".sh"):
            if p.stat().st_size < 5_000_000:
                try:
                    manifest.append({"path": str(p.relative_to(ROOT)), "sha256": sha256(p), "size": p.stat().st_size})
                except: pass
    out = vendor / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {out} {len(manifest)} entries")

if __name__ == "__main__":
    main()
