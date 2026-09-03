# Vendored Provenance — self-contained Classic Malbolge tooling

These are vendored so a clean clone of MALDOOM reproduces the QUINE_OUTWARD_V0
experiments without any external/private dependency. Both pieces are derived
from the *public* Malbolge language description, not from private research.

## `malbolge/malbolge.py` — Classic Malbolge interpreter

- Role: faithful Classic Malbolge (3^10 / 59049-cell) interpreter used by the
  QUINE_OUTWARD_V0 experiment scripts.
- Derivation: public-language semantics — Iizawa (2005) Appendix C, itself a
  transcription of the reference interpreter that has circulated publicly
  since 1998 (`malbolge.c`). Same semantics as `vendor/classic/oracle.py`.
- License: public-domain language semantics; this file is MIT (see repo
  LICENSE).
- Validation: `py vendor/malbolge/malbolge.py` runs the Wikipedia Hello World
  and must print `status=HALTED` with "Hello world".

## `quines/quine_lutter.malbolge` — Lutter quine (specimen)

- Role: a known Classic Malbolge self-replicating program used as the study
  specimen for the quine-outward experiment.
- Source: publicly circulated Lutter Malbolge quine (lutter.cc Malbolge page).
- File SHA256: `DCA8476F8B70C8462C32F661F63C5F8B1AD6C33946B3C7A9A35186C824117D98`
- Clean source (whitespace stripped): 59,032 chars;
  clean SHA256: `6812b7c10679f571887e84238d02ed1c2e0b4f013b8299a60f9ff5e3e9162543`
- It emits its own source bytes (output == source file size, 59,852 B incl
  newline) after ~69.5M steps.
- License: the quine's own distribution terms apply (public Malbolge specimen).

## Integrity

`SHA256SUMS.txt` in this directory records file hashes. Update it if the
vendored set changes.