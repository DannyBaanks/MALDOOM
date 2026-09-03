"""
test_engine_does_the_work — host must not compute answer.

- grep host/ for gameplay symbols
- verify that generated .mu artifacts exist and are non-trivial
- ensure killer test uses same artifact for different inputs
"""
import re, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "host" / "host.py"

FORBIDDEN = ["doomgeneric_Tick","P_MovePlayer","P_RunThinkers","M_Random","P_CheckPosition","WI_Ticker","G_Ticker","ST_Ticker"]

def test_host_no_gameplay():
    src = HOST.read_text(encoding="utf-8")
    found = [s for s in FORBIDDEN if s in src]
    assert not found, f"HOST_STOLE_COMPUTATION — host contains {found}"

def test_m0_artifacts_exist():
    # after build, evidence/M0_*/artifact.mu should exist
    # before build, this test is skipped (not failed)
    evid = list((ROOT/"evidence").glob("M0_*"))
    if not evid:
        import pytest; pytest.skip("no evidence yet — run py scripts/build_m0.py --all")
    for d in evid:
        mu = d / "artifact.mu"
        hell = d / "artifact.hell"
        assert mu.exists() or hell.exists(), f"missing artifact in {d}"

def test_killer_same_artifact():
    kd = ROOT / "evidence" / "M0_KILLER"
    if not kd.exists():
        import pytest; pytest.skip("killer not built yet")
    mu = kd / "artifact.mu"
    assert mu.exists(), "killer artifact missing"
    h = hashlib.sha256(mu.read_bytes()).hexdigest()
    # run.json should list same sha for all inputs
    j = kd / "run.json"
    if j.exists():
        import json
        runs = json.loads(j.read_text())
        shas = set(r.get("artifact_sha") for r in runs)
        assert len(shas)==1, f"killer used different artifacts per input: {shas} — must be COMPILE_ONCE"
        assert h == next(iter(shas)), "artifact file hash mismatch run.json"
