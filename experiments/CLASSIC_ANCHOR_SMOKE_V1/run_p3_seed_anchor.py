"""P3: truth_machine.mal as control AND anchor.

The seed is used in two roles without crossing them:

1. CONTROL: verifies the program's input-dependent behavior on pinned interpreters.
2. ANCHOR: the observable outcome (steps, halted, output prefix) serves as an
   opaque continuation token. Resume = re-run same seed with same input;
   anchor matches iff observable reproduces.

No MBD1A encode/decode, no internal state serialization. The "state" is
the input itself; the "continuation" is deterministic replay.
"""
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
OUT = ROOT / "evidence" / "CLASSIC_ANCHOR_SMOKE_V1" / "P3_SEED_AS_ANCHOR"
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


def make_anchor(gost: dict, oracle: dict) -> dict:
    """Opaque anchor derived ONLY from observable output."""
    return {
        "gost": {"steps": gost["stderr"], "exit_code": gost["exit_code"]},
        "oracle": {"steps": oracle["steps"], "halted": oracle["halted"], "halt_reason": oracle["halt_reason"]},
        "output_prefix": gost["stdout"][:12],  # first 12 chars
    }


def main() -> None:
    if not GOST.exists() or not ORACLE.exists() or not PROGRAM.exists():
        raise SystemExit("missing pinned Classic control or vendored seed")

    OUT.mkdir(parents=True, exist_ok=True)
    program_bytes = PROGRAM.read_bytes()
    program_sha = hashlib.sha256(program_bytes).hexdigest()

    anchors_first = {}
    anchors_resume = {}
    cases = []

    for value, expected_halt, expected_prefix in (("0", True, "0"), ("1", False, "1" * 10)):
        # First run (CONTROL + create anchor)
        gost1 = run_gost(value)
        oracle1 = run_oracle(value)
        assert gost1["stdout"].startswith(expected_prefix), (value, gost1)
        assert oracle1["stdout"].startswith(expected_prefix), (value, oracle1)
        assert oracle1["halted"] is expected_halt, (value, oracle1)

        anchor = make_anchor(gost1, oracle1)
        anchors_first[value] = anchor

        # Resume run (same seed, same input) -> reproduce anchor
        gost2 = run_gost(value)
        oracle2 = run_oracle(value)
        assert gost2["stdout"].startswith(expected_prefix), (value, gost2)
        assert oracle2["stdout"].startswith(expected_prefix), (value, oracle2)
        assert oracle2["halted"] is expected_halt, (value, oracle2)

        anchor2 = make_anchor(gost2, oracle2)
        anchors_resume[value] = anchor2

        # Anchor reproduction check: opaque equality
        anchor_match = anchor == anchor2
        print(f"input={value} anchor_match={anchor_match} anchor={anchor}")

        cases.append({
            "input": value,
            "expected_halt": expected_halt,
            "anchor_first": anchor,
            "anchor_resume": anchor2,
            "anchor_reproduced": anchor_match,
            "gost_first": gost1,
            "oracle_first": oracle1,
            "gost_resume": gost2,
            "oracle_resume": oracle2,
        })

    # All anchors must reproduce
    assert all(c["anchor_reproduced"] for c in cases), "anchor reproduction failed"

    result = {
        "schema": "maldoom.classic_anchor_v1.p3_seed_as_anchor/1",
        "target": "B2_CLASSIC_59049",
        "program_sha256": program_sha,
        "max_steps": MAX_STEPS,
        "cases": cases,
        "claim": "CLASSIC_SEED_ANCHOR_REPLAY_DEMONSTRATED",
        "exclusion": "Anchor is opaque replay of observable behavior. No encode/decode, no internal state, no fresh VM boundary yet.",
    }
    (OUT / "program.mal").write_bytes(program_bytes)
    (OUT / "run.json").write_text(json.dumps(result, indent=2), encoding="ascii")

    sums = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="ascii")
    print("P3 PASS: seed-as-anchor replay reproduces opaque anchors")


if __name__ == "__main__":
    main()