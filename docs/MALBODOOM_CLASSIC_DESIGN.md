# MALBODOOM Classic Design — DRAFT (frozen after smoke)

> `424fcc8` baseline preserved. This doc maps anchored execution onto Doom, but is **NOT implemented** until `CLASSIC_ANCHOR_SMOKE_V0` and `DEATH_REBIRTH` toy both pass.

## Mantra

```
THE VM MAY DIE.
THE COMPUTATION MAY CONTINUE.
THE HOST MAY REMEMBER BYTES.
THE HOST MAY NOT UNDERSTAND THEM.
NEVER ENLARGE MALBOLGE. MAKE THE COMPUTATION FIT.
```

## Core Rule (Stronger than MALDOOM)

- Host may only: launch Classic interpreter, provide input bytes, capture output bytes, store opaque continuation byte-for-byte, feed to new VM, present framebuffer, record hashes/timing.
- Host may NOT: decide what to save, serialize/deserialize, decide checkpoint timing, compute gameplay/RNG/collision, keep VM alive, inspect anchor fields.

All encode/decode, checkpoint trigger, canonicalization happens **inside Classic Malbolge**.

## Memory Layout (Conceptual, within 59049)

```
CLASSIC MEMORY 59049
┌───────────────────────────────┐
│ program/runtime              │
│ active working state         │
│ temporary state              │
│ ── HIGH_WATER (pre-frozen) ──│
│ checkpoint reserve           │
│  encoder/decoder + stream buf │
└───────────────────────────────┘
```

`HIGH_WATER` is managed, not the last cell. Reserve must fit worst-case encoder + decoder + bootstrap.

## Two Modes

### ANCHOR_CONTINUE (exact)

`working_state >= HIGH_WATER` → Malbolge itself:

```
stop new work → canonicalize live state → discard reconstructible
→ serialize sufficient state → emit MBD1A-… → HALT
→ fresh VM (program + anchor + new input) decodes and continues
```

`epoch_local_step` resets, `logical_total_step` continues (metadata unless needed).

Semantics: `canonical(S_next_without_restart) == canonical(S_next_with_anchor)` for declared preserved state.

### DEATH_REBIRTH

On player death (natural compaction point):

- `CONTINUE` → exact anchor (as above)
- `REBIRTH` → derive new seed inside Malbolge from declared state/RNG/death event, discard transient, `epoch_local_step=0`, emit compact `DEATH CODE`, HALT, new VM

`DEATH_REBIRTH` is **not** exact resume; it is game-defined rebase.

## Anchor Format (Versioned, Opaque to Host)

```
MBD1A-<fixed-width ternary payload><integrity>
```

Logical fields (encoded/decoded only inside Malbolge, host is pipe):

- version, mode, epoch, logical position
- required canonical state (player/world/thinker subset — defined per Doom mapping below)
- RNG/seed where required
- continuation point
- integrity checksum (verified inside Malbolge)

Host may `hash(anchor)` for evidence, never `parse(anchor)` to advance game.

Streaming allowed: output chunk → release workspace → next chunk; restore streams from stdin. External storage != computation.

## Doom Mapping (To Be Frozen After Toy)

| Category | Preserve in `ANCHOR_CONTINUE` | Discard in `REBIRTH` |
|---|---|---|
| player/world state | yes | canonical respawn |
| thinker state | required live | per game respawn rules |
| RNG | yes (or sufficient to reproduce) | re-derived seed |
| inventory | yes | per death rules |
| map progression / switches | yes | depends on CONTINUE vs REBIRTH |
| renderer transient / frame | no (reconstructible) | no |
| ... | ... | ... |

*Anything not proven reconstructible stays in anchor. Do not guess.*

Future renderer may stream `column→stdout→discard→next` without holding full framebuffer.

## Future Behavior

```
PLAYING
  ├── dies → CONTINUE / REBIRTH → death code → HALT → new VM
  └── HIGH_WATER → MEMORY ANCHOR → continuation code → HALT → new VM
```

## Status

- `CLASSIC_ANCHOR_SMOKE_V0` — host-assisted multi-epoch demonstrated; it does
  not transfer checkpoint ownership to Malbolge.
- `DEATH_REBIRTH_V0` toy — host-assisted demonstrated; it does not prove
  Malbolge-owned death semantics.
- `CLASSIC_ANCHOR_SMOKE_V1` — `NOT_DEMONSTRATED`: no `program_v1.mal` yet.
- `MALBODOOM_ARCHITECTURE_FEASIBLE` — `NOT_DEMONSTRATED` until V1 owns
  trigger, encode/decode/integrity and fresh-VM continuation.

See `experiments/CLASSIC_ANCHOR_SMOKE_V0/PROTOCOL_FROZEN.md` for the first proof.
See `docs/CLASSIC_CHECKPOINTS.md` for the frozen semantic contract.
