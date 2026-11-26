# r9 HID digitizer-property observation — 2026-11-26

The existing `TOUCH HID` row keeps the report count and adds `digitizer
properties: observed` or `not observed`. Only the success path that logs
`digitizer properties=1` sets the boot-local bit. The original short circuits,
one-shot `published` gate and timer call remain; the bit does not report HID
readiness, a touch, or delivery of input. The sampler runs before the pixel lease.
The independent relaxed word follows the r4 display event pattern in this repo
(`38d06d85`, BSD-2-Clause-Patent).

## Reproduce in WSL

From the device repo, as the existing WSL build user with access to `/root/enuma-step10`
(the reference build ran as root):

```sh
/home/wh1stl3/.local/bin/python3.11 candidates/bootprogress-hid-event-20261126/build.py \
  out/bootprogress-hid-event-20261126-r2-verify
```

The actual successful invocation used `out/bootprogress-hid-event-20261126-r2`;
the recipe requires a fresh output directory. In that directory `commands.json`
records the exact subprocess argv, cwd and exit status. `source.diff` records
the two local edits to the generated sampler (declaration/read and row).
The compile log records `-H` include resolution. The original compiler
arguments are retained, apart from the output/source redirection and the
video compile's `-H`. The r9 `kern_exec.o` is not recompiled. The HID archive
keeps its member order and its other two members byte-identical. No generated
page sources are added to Git.

## Host results (`self-checked`)

- Ten ASan/UBSan cases: fresh zero, missing driver followed by a later match,
  missing interface, each of the eight individual property failures, success,
  and repeat checkpoints without additional property calls. The longest
  32-bit-count text fits in the r9 120-byte row.
- Recompiled both changed objects, linked, prelinked, packaged and extracted
  the kernel back from the Android boot image. Native and prelink undefined
  symbol lists were empty. The r9 run-state and r4 display edge checks, display
  ABI comparison, payload member checks and unchanged boot config passed.
- In the extracted Mach-O, `NativeHidInput::tick` calls the original checkpoint.
  Its missing-parent and eight failure branches skip `str w8` at
  `0xfffffff00bfef2a0`; the success block stores `1` to the four-byte BSS
  symbol at `0xfffffff00c155f60`, distinct from `published` at `…5f64`.
  The sampler's `ldr w0` reads the same word at `0xfffffff00bfef12c`.
  The refresh calls the sampler at `0xfffffff00b9e1a64`, before the first
  interrupt-disable call at `0xfffffff00b9e2250`. These are r2 link addresses.
- `out/bootprogress-hid-event-20261126-r2/boot.img`: **169,951,232 bytes**,
  SHA-256 `e278d568b7c59fb9dafffbfe3617159d6f062421ebbad5e4447703c9732f13eb`.
  Embedded kernel SHA-256 `4e8ed4eb2be36ed976c28f2960b350cf47dcb62c107b5211c68b85a4bae575c8`.
- First attempt (`…-r1`) failed in host C++ compilation (exit 1, `--64`
  rejected by the cross-toolchain assembler on `PATH`). The successful r2
  uses the host environment for the sanitizer fixture, matching r9's split
  between host tests and cross-build tools.

No device run, deployment, or independent verifier run.
