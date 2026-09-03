"""P1: verify a local Classic non-echo branch/halt seed on pinned controls."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASSIC = ROOT / "vendor" / "classic"
PROGRAM = ROOT / "vendor" / "classic_synthesis" / "malpad" / "truth_machine.mal"
GOST = CLASSIC / "gost.exe"
ORACLE = CLASSIC / "oracle.py"
OUT = ROOT / "evidence" / "CLASSIC_ANCHOR_SMOKE_V1" / "P1_NON_ECHO_BRANCH"
MAX_STEPS = 200


def run_gost(value: str) -> dict:
    process = subprocess.run(
        [str(GOST), str(PROGRAM), str(MAX_STEPS)],
        input=value.encode("ascii"),
        capture_output=True,
        timeout=5,
    )
    return {
        "stdout": process.stdout.decode("ascii", "replace"),
        "stderr": process.stderr.decode("ascii", "replace"),
        "exit_code": process.returncode,
    }


def run_oracle(value: str) -> dict:
    sys.path.insert(0, str(CLASSIC))
    from oracle import Oracle

    machine = Oracle()
    machine.load_ascii(PROGRAM.read_text(encoding="ascii"))
    machine.provide_input(value)
    result = machine.run(MAX_STEPS)
    return {
        "stdout": result.output,
        "halted": result.halted,
        "halt_reason": result.halt_reason,
        "steps": result.steps,
    }


def main() -> None:
    if not GOST.exists() or not ORACLE.exists() or not PROGRAM.exists():
        raise SystemExit("missing pinned Classic control or vendored seed")

    cases = []
    for value, expected_halt, expected_prefix in (("0", True, "0"), ("1", False, "1" * 10)):
        gost = run_gost(value)
        oracle = run_oracle(value)
        assert gost["stdout"].startswith(expected_prefix), (value, gost)
        assert oracle["stdout"].startswith(expected_prefix), (value, oracle)
        assert oracle["halted"] is expected_halt, (value, oracle)
        cases.append({"input": value, "expected_halt": expected_halt, "gost": gost, "oracle": oracle})

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "program.mal").write_bytes(PROGRAM.read_bytes())
    result = {
        "schema": "maldoom.classic_anchor_v1.p1_non_echo_branch/1",
        "target": "B2_CLASSIC_59049",
        "program_sha256": hashlib.sha256(PROGRAM.read_bytes()).hexdigest(),
        "max_steps": MAX_STEPS,
        "cases": cases,
        "claim": "CLASSIC_NON_ECHO_INPUT_BRANCH_SEED_DEMONSTRATED",
        "exclusion": "This seed is not program_v1.mal and does not encode, decode, checkpoint, or resume an anchor.",
    }
    (OUT / "run.json").write_text(json.dumps(result, indent=2), encoding="ascii")
    sums = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="ascii")
    print("P1 PASS: non-echo branch/halt seed agrees on gost and oracle")


if __name__ == "__main__":
    main()
