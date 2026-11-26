# r5 Legacy display observations — 2026-11-26

**`self-checked`, host only.** `out/bootprogress-display-events-20261126-r4/boot.img`, 169,951,232 bytes, SHA-256 `5849e9c67ebce4440544cee96d5d54a37b6c0f9c2705a6389a513e0807086183`.

Neon selected r5 rows 31–34. This is the service-only fallback accepted in Astra deep `ses_de9dacd0bffeIpjlMN7R5c2Tcm` (PASS WITH CONDITIONS on design, not on the final image). BB1 would require changing the r5 recorder, excluded by the object identity gate. No task identity, proc lookup or correlation with a recent exec, PID or comm.

| Row | Observation | Not established |
| --- | --- | --- |
| 31 | `registered` after the existing service `registerService()` returns | Matching or a client connection |
| 32 | Legacy validator entry and its `accepted` result; reason 5 blank is accepted | All user submissions or a presented frame |
| 33 | CPU prepare entry and false return; false includes no display object and may occur without `gui_take` | A `gui_take` refusal in particular, or GUI presentation |
| 34 | Four-argument `newUserClient` entry and its one synchronous parent call's success/error | Final `IOServiceOpen` result or caller identity (`caller/BB unknown`) |

Each indicator is a separately sampled relaxed sticky word. Two set bits need not describe the same call. Zero means not observed in the sample, never proof that backboardd did not open a service. Refresh can stop on successful handoff; its last frame is not a success/failure verdict. GUI take/drain, STOP, existing volatile counters and return values are unchanged.

## Verification

From the device repo in WSL as root, with a fresh output:

```sh
/home/wh1stl3/.local/bin/python3.11 candidates/bootprogress-display-events-20261126/build.py out/bootprogress-display-events-20261126-verify
```

Reuses local r5 command records and packaging gates (UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241`, BSD-2-Clause-Patent), r6 Legacy archive sources and ABI recipe (GopFramebuffer `e47c1b8de169cd2bd0b885c7d85e433010e3cdf2`; Enuma CPU backend BSD-2-Clause-Patent), and the existing row/raster precedent (UniXNU/UniXNU-sheng `c8f92b208068eeaa4cd2b0f592671f04ee70076e`, MIT). `display-source.diff` shows exact source edits; `commands.json` records argv, cwd and exit.

- ASan/UBSan: production callback excerpts with mocks exercised reason-5 blank acceptance, reason-2 rejection, open calling its parent once and returning success/error unchanged, prepare null-object short circuit and false/true, nine concurrent sticky writers with a simultaneous reader, row width/neighbors, and no sample/raster/reschedule after STOP. The adapted r5 sampler and page also ran under ASan/UBSan, including 2x incremental raster equivalence and 1x clipping. This does not test XNU scheduling or hardware.
- Native/prelink zero undefined. Actual subclass relocations matched all 358 r6 slot symbols (`compiled-slots.json`); ABI gate matched 31 original instruction checks and 358 slots (`final-abi.json`). New TU imports are only in-image mark/sample. ARM64 marker/sampler use one aligned 32-bit store and nine separate 32-bit loads respectively, no lock or helper. The r5 exec/exit objects are linked in place and retain hashes `c21e9f6fbc561f8e1bbe9282f4a2daa502afd65d943b44818404313f499ef6cd` and `db64be8feb6c92fd69a5e51d4e6d6a077eedf502ee6626eaf4c2e43213fec0d8`; all four proc edges remain.
- Boot-extracted branches: one original parent call (slot offset 1144), status classified and returned unchanged; validator classifies its returned acceptance; `registered` follows `registerService` (slot offset 672). Blank, half and BGRA each call prepare and branch on its return. Null object and false GUI result join the false branch; true skips it. Refresh tests STOP before sampling and samples before IRQ/row lease, not inside raster. See `events*.log`.
- Non-kernel payload member bytes and embedded arguments matched r5; FD/DTB and boot → FAT → kernel extraction gates passed. Prelink SHA-256 `1c679b18c3c792530397ef3f92976ddc0eddf96a2ab577dfe3576c71c6b96113`; payload SHA-256 `fde23fa46d9d820d83fa03403b56a002f93d361521d185ce2d8316db95bbd738`.

No device action, claim access, stage promotion or independent verifier. Actual display events, caller attribution, final open success and first GUI presentation remain unverified.
