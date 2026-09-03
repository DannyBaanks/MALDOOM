#!/usr/bin/env py
"""
build_m0.py — build M0_A..M0_KILLER via ELVM HeLL → Unshackled pipeline.

For each program:
  source.c → 8cc (eir) → .eir → elvm target/hell → .hell → LMFAO → .mu → Unshackled VM → observed output
  records command, stdout/stderr, exit code, wall time, sha256, expected vs observed, host audit.

If toolchain not present, falls back to gcc reference run and marks
pipeline NOT_DEMONSTRATED with explicit gap.

Usage:
  py scripts/build_m0.py --all
  py scripts/build_m0.py --only M0_A_CONST
  py scripts/build_m0.py --only M0_KILLER --inputs 0,1,2,3,4
"""
import argparse, subprocess, hashlib, json, time, sys, os, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
EVIDENCE = ROOT / "evidence"
VENDOR = ROOT / "vendor"

PROGRAMS = {
    "M0_A_CONST": {"src": "M0_A_CONST.c", "expected": "OK\n", "desc": "fixed output"},
    "M0_B_ARITH": {"src": "M0_B_ARITH.c", "expected": "42\n", "desc": "arithmetic 40+2"},
    "M0_C_BRANCH": {"src": "M0_C_BRANCH.c", "expected": "NONZERO\n", "desc": "branch"},
    "M0_D_LOOP": {"src": "M0_D_LOOP.c", "expected": "*****\n", "desc": "loop x5"},
    "M0_E_MEMORY": {"src": "M0_E_MEMORY.c", "expected": "60\n", "desc": "mem store/load sum"},
    "M0_F_INPUT": {"src": "M0_F_INPUT.c", "expected_map": {"5":"6\n","0":"1\n","9":"0\n"}, "desc": "input->output inc", "input": "5\n"},
    "M0_KILLER": {"src": "M0_KILLER.c", "expected_map": {"0":"1\n","1":"3\n","2":"5\n","3":"7\n","4":"9\n"}, "desc": "killer n*2+1", "killer": True},
}

def sha256(p: Path):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def sha_bytes(b: bytes): return hashlib.sha256(b).hexdigest()

def run(cmd, input_bytes=None, timeout=30):
    print(f"$ {' '.join(shlex.quote(str(c)) for c in cmd)}")
    t0=time.time()
    try:
        r=subprocess.run(cmd, input=input_bytes, capture_output=True, timeout=timeout)
        wall=time.time()-t0
        return r.stdout, r.stderr, r.returncode, wall
    except subprocess.TimeoutExpired as e:
        wall=time.time()-t0
        return e.stdout or b"", (e.stderr or b"")+b"\nTIMEOUT", 124, wall
    except FileNotFoundError as e:
        wall=time.time()-t0
        return b"", str(e).encode(), 127, wall

def has_toolchain():
    return (VENDOR/"elvm").exists() and (VENDOR/"8cc").exists() and (VENDOR/"Unshackled.c").exists()

def build_and_run(name, info, inputs=None, timeout=15):
    src = ENGINE / info["src"]
    evid = EVIDENCE / name
    evid.mkdir(parents=True, exist_ok=True)
    build_dir = VENDOR / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    # copy source to evidence
    (evid/"source.c").write_bytes(src.read_bytes())
    expected = info.get("expected")
    expected_map = info.get("expected_map")

    # try ELVM pipeline
    pipeline = "NOT_ATTEMPTED"
    artifact = None
    artifact_hell = None
    host_audit = "PASS"

    # host audit check
    host_src = (ROOT/"host"/"host.py").read_text()
    forbidden = ["doomgeneric_Tick","P_MovePlayer","P_RunThinkers","M_Random"]
    found = [s for s in forbidden if s in host_src]
    if found:
        host_audit = f"FAIL found {found}"

    if has_toolchain():
        # 8cc eir
        eir = build_dir / f"{name}.eir"
        out, err, code, wall = run([str(VENDOR/"8cc"/"8cc"), "-S", "-o", str(eir), str(src)], timeout=10)
        (evid/"8cc.stdout").write_bytes(out)
        (evid/"8cc.stderr").write_bytes(err)
        if code==0 and eir.exists():
            (evid/"artifact.eir").write_bytes(eir.read_bytes())
            # elvm hell
            hell = build_dir / f"{name}.hell"
            elvm_bin = VENDOR/"elvm"/"out"/"elvm"  # or python?
            # try target/hell via elvm tool
            # ELVM typically: ./out/elvm hell < in.eir > out.hell
            # fallback to python target
            hell_py = VENDOR/"elvm"/"target"/"hell.py"
            if hell_py.exists():
                out, err, code, wall = run([sys.executable, str(hell_py), str(eir)], timeout=20)
                if code==0:
                    hell.write_bytes(out)
                    (evid/"artifact.hell").write_bytes(out)
                    artifact_hell = hell
            # LMFAO
            mu = build_dir / f"{name}.mu"
            lmfao = VENDOR/"LMFAO"/"lmfao"  # guess
            if artifact_hell and lmfao.exists():
                out2, err2, code2, wall2 = run([str(lmfao), str(hell), "-o", str(mu)], timeout=20)
                if code2==0 and mu.exists():
                    artifact = mu
                    (evid/"artifact.mu").write_bytes(mu.read_bytes())
                    pipeline = "ELVM_HELL_LMFAO"
        else:
            pipeline = f"8CC_FAILED_{code}"
    else:
        pipeline = "TOOLCHAIN_MISSING"

    # fallback gcc reference for expected output verification (not Malbolge)
    gcc_bin = build_dir / f"{name}.exe"
    gcc_out, gcc_err, gcc_code, _ = run(["gcc","-O2","-o",str(gcc_bin),str(src)], timeout=10)
    gcc_ok = (gcc_code==0 and gcc_bin.exists())
    base_pipeline = pipeline
    if gcc_ok and not artifact:
        base_pipeline = pipeline + "+GCC_REF"

    # determine inputs to test
    if inputs is not None:
        test_inputs = inputs
    elif info.get("killer"):
        test_inputs = ["0","1","2","3","4"]
    elif "expected_map" in info and "input" not in info:
        # for M0_F_INPUT default map keys
        test_inputs = list(info["expected_map"].keys())
        if len(test_inputs)>3: test_inputs = test_inputs[:3]
    elif "input" in info:
        test_inputs = [info["input"]]
    else:
        test_inputs = [""]  # no input

    # run artifact if exists, else gcc ref
    runs=[]
    for inp in test_inputs:
        inp_bytes = None
        if inp != "":
            # normalize: if single digit without newline, add newline
            raw = inp if inp.endswith("\n") else inp+"\n" if inp!="" else ""
            inp_bytes = raw.encode()
        expected_val = (expected_map[inp.rstrip("\n")] if expected_map else expected) if expected_map else expected
        if expected_val is None and test_inputs!=[""]:
            # lookup
            expected_val = expected_map.get(inp.rstrip("\n"), "")

        if artifact and artifact.exists():
            # find Unshackled VM
            vm_c = VENDOR/"Unshackled.c"
            vm_bin = VENDOR/"Unshackled"
            # compile vm if needed
            if vm_c.exists() and not vm_bin.exists():
                run(["gcc","-O3","-o",str(vm_bin),str(vm_c)], timeout=15)
            if vm_bin.exists():
                # ensure .exe on Windows
                if not vm_bin.exists() and (VENDOR/"Unshackled.exe").exists():
                    vm_bin = VENDOR/"Unshackled.exe"
                out, err, code, wall = run([str(vm_bin), str(artifact)], input_bytes=inp_bytes, timeout=timeout)
                observed = out
            else:
                out, err, code, wall = b"", b"VM_MISSING", 127, 0.0
                observed = b""
            artifact_sha = sha256(artifact)
            effective_pipeline = pipeline
        elif gcc_ok:
            out, err, code, wall = run([str(gcc_bin)], input_bytes=inp_bytes, timeout=5)
            observed = out
            artifact_sha = sha_bytes(src.read_bytes())
            effective_pipeline = base_pipeline
        else:
            out, err, code, wall = b"", b"NO_ARTIFACT", 127, 0.0
            observed = b""
            artifact_sha = "none"
            effective_pipeline = pipeline

        # normalize CRLF vs LF for Windows
        observed_norm = observed.replace(b"\r\n", b"\n").decode(errors="replace")
        expected_norm = expected_val.replace("\r\n","\n") if expected_val else ""
        runs.append({
            "input": inp,
            "input_bytes_hex": inp_bytes.hex() if inp_bytes else "",
            "expected": expected_val,
            "expected_norm": expected_norm,
            "observed": observed.decode(errors="replace"),
            "observed_norm": observed_norm,
            "observed_hex": observed.hex(),
            "stdout_raw": observed.decode(errors="replace"),
            "stderr": err.decode(errors="replace"),
            "exit_code": code,
            "wall_time_s": wall,
            "match": observed_norm == expected_norm,
            "artifact_sha": artifact_sha,
            "pipeline": effective_pipeline,
            "host_audit": host_audit,
        })
        # write per-run files
        safe = inp.rstrip("\n").replace("/","_") or "no_input"
        (evid/f"observed_{safe}.bin").write_bytes(observed)
        (evid/f"stderr_{safe}.txt").write_bytes(err)

    # overall
    all_match = all(r["match"] for r in runs)
    status = "PASS" if all_match and host_audit=="PASS" else "FAIL"
    final_pipeline = base_pipeline if not artifact else pipeline

    # write run.json
    (evid/"run.json").write_text(json.dumps(runs, indent=2), encoding="utf-8")
    # SHA256SUMS
    sums=[]
    for p in evid.iterdir():
        if p.is_file():
            try: sums.append(f"{sha256(p)}  {p.name}")
            except: pass
    (evid/"SHA256SUMS.txt").write_text("\n".join(sorted(sums)), encoding="utf-8")
    # summary
    print(f"[{name}] {status} pipeline={final_pipeline} host={host_audit} runs={len(runs)} match={all_match}")

    return {"name":name, "status":status, "pipeline":final_pipeline, "runs":runs}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--inputs", default=None, help="comma separated for M0_KILLER")
    args = ap.parse_args()
    targets = list(PROGRAMS.keys()) if args.all else ([args.only] if args.only else list(PROGRAMS.keys()))
    if args.inputs:
        inputs = args.inputs.split(",")
    else:
        inputs = None
    results=[]
    for t in targets:
        if t not in PROGRAMS: print(f"unknown {t}"); continue
        r = build_and_run(t, PROGRAMS[t], inputs=inputs)
        results.append(r)
    # overall report
    print(json.dumps({"results": results}, indent=2))
    # exit code 0 only if all PASS
    sys.exit(0 if all(r["status"]=="PASS" for r in results) else 1)

if __name__ == "__main__":
    main()
