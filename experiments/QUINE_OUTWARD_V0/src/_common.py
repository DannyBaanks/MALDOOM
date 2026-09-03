"""_common.py — repo-local path resolution for QUINE_OUTWARD_V0 scripts.

Resolves the MALDOOM repo root from this file's location so the experiment is
fully self-contained (no absolute / private paths).
"""
from pathlib import Path
import importlib.util

# repo root = experiments/QUINE_OUTWARD_V0/src/ -> up 3 -> MALDOOM
ROOT = Path(__file__).resolve().parents[3]
VENDOR_MB = ROOT / "vendor" / "malbolge" / "malbolge.py"
QUINE = ROOT / "vendor" / "quines" / "quine_lutter.malbolge"

_SPEC = importlib.util.spec_from_file_location("malbolge_local", str(VENDOR_MB))
mi = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mi)


def load_quine_src():
    return "".join(c for c in QUINE.read_text(encoding="utf-8") if not c.isspace())