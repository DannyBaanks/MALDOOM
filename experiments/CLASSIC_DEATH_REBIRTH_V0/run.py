#!/usr/bin/env py
"""Death/rebirth toy — host-assisted"""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
out = ROOT / "evidence" / "CLASSIC_DEATH_REBIRTH_V0"
out.mkdir(parents=True, exist_ok=True)

# Simulate death at state (3,3,1) -> acc 1
state = (3,3,1)
print(f"death state {state}")
# CONTINUE
cont_anchor = f"MBD1-C-{state[0]}-{state[1]}-{state[2]}\n".encode()
# REBIRTH: derive new seed inside Malbolge (host does for toy): (acc*3+epoch)%2
new_seed = (state[2]*3 + state[0]) % 2
rebirth_state = (state[0]+1, 0, new_seed)  # epoch+1, logical 0, new acc
rebirth_anchor = f"MBD1-R-{rebirth_state[0]}-{rebirth_state[1]}-{rebirth_state[2]}\n".encode()

print(f"CONTINUE {cont_anchor} size {len(cont_anchor)}")
print(f"REBIRTH {rebirth_anchor} size {len(rebirth_anchor)} -> state {rebirth_state}")

evid = {
    "death_state": state,
    "continue_anchor": cont_anchor.decode().strip(),
    "continue_size": len(cont_anchor),
    "continue_state": state,
    "rebirth_anchor": rebirth_anchor.decode().strip(),
    "rebirth_size": len(rebirth_anchor),
    "rebirth_state": rebirth_state,
    "rebirth_local_reset": 0,
    "reduction_ratio": len(rebirth_anchor)/len(cont_anchor),
    "note": "host-assisted toy, MALBOLGE_OWNED = NOT_DEMONSTRATED"
}
(out / "run.json").write_text(json.dumps(evid, indent=2), encoding="utf-8")
(out / "continue.anchor").write_bytes(cont_anchor)
(out / "rebirth.anchor").write_bytes(rebirth_anchor)
# SHA
import hashlib as hl
sums=[]
for p in out.iterdir():
    if p.is_file() and p.name!="SHA256SUMS.txt":
        sums.append(f"{hl.sha256(p.read_bytes()).hexdigest()}  {p.name}")
(out / "SHA256SUMS.txt").write_text("\n".join(sorted(sums)), encoding="utf-8")
print(f"saved to {out}")
