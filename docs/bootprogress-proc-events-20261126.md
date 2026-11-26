# BootProgress proc events — r4 provenance and r5 review fixes

`self-checked`: the r64 `kern_exit.o` replay blocker was resolved in r4.
r5 addresses the two final review findings and passes the extracted-kernel
checks on the host. No device, claim, stage change, independent verification,
commit or push.

Inputs: device `2a5f404981e448f3010f1dfff433333a1e2707b2`, UniXNU
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`, XNU work
`d8b80295118ef25ac3a784134bcf95cd8e88109f`. The existing wrapped page is
derived from UniXNU/UniXNU-sheng `c8f92b208068eeaa4cd2b0f592671f04ee70076e`
(MIT). The new recorder uses the static spin lock declaration pattern from
the r64 `EnumaProcExecReport.inc` (`12c24d55…`, BSD-2-Clause-Patent); source
reconstruction reuses the device's r64 recipe at `a05d60c6908834fae9f7eb8f2c46b6ecd169a0ad`.

## Static call-chain review

Line numbers below refer to stock inputs in
`out/bootprogress-proc-events-20261126-r3/stock/`.

- Spawn: `kern_exec.c:3983,4045,4073` uses the process of the child thread
  created by `fork1(PROC_CREATE_SPAWN)` and binds that thread into the VFS
  context. `exec_mach_imgact` at 1193/1196 takes that process; `set_proc_name`
  at 2004 precedes the reached point at 2124. The new fields copy only the
  selected name slot and `proc_ident` scalars. Publication is after failure
  merging (`4836–4840`), gated by reached, not failed, zero error, `exec_done`,
  the local bit after the existing `NOTE_EXEC` call and non-shadow.
- SETEXEC has the additional `task_did_exec(old_task)` predicate, as does
  execve. The old flag is set only in the replacement arm at 5031 and the
  new process must also have had its shadow bit cleared at 5074. The abort
  arm at 5092–5094 terminates the new task and still returns `new_proc` at
  5120; neither API's return is treated as an installation witness.
  `badtoolate` calls `enuma_ex_failure` before suppressing the returned
  error for exec (`2134–2154`), so zero alone cannot publish.
- Execve/PID 1: `load_init_program_at_path` calls `execve` (8161), which
  calls `__mac_execve`. Its new publication follows the failure merge at
  5446–5451, not the earlier NOTE_EXEC branch, and inherits the same
  predicate. No PID 1 special path, changes to `process_signature`,
  notification, locks/releases, `FINAL_WAIT`, or failure handling in
  `proc-source.diff`.
- Exit: normal path releases the proc lock at 1620, then calls
  `proc_prepareexit` at 1622. The fallback at 2180 passes literal zero,
  after releasing the proc lock as well. Publish once beside the original
  log inside the existing non-shadow guard (1889), before critical exit
  handling; no changes to the separate PID 1 callback or panic.
- Counters record events from all same-name instances, without pairing. A
  different unique ID distinguishes PID reuse. Same-process re-exec retains
  PID and unique ID. Although the clone initially copies `idversion`, this
  path calls `exec_handle_sugid` and updates it before sampling the new
  image (`r4/kern_exec.c:1630,6918–6920,2124–2129`). That version is not a
  consecutive success count and must not be used to pair events. Latest exec
  and exit are independent; neither the record order nor their order relative
  to the console proves causality, liveness or userspace entry.
- `panel_sample` attempts one snapshot before any draw/interrupt gate. The
  writer lock body changes only count and scalars; the reader lock body
  only copies the three slots before unlocking. A missed acquisition gives
  `busy`, not stale data or a fabricated `not observed`. No new worker,
  census, callback or process pointer persists; existing r56/r65 diagnostics
  are not part of the collector.

## Earlier blocked replay (r1–r3)

- WSL root: `/home/wh1stl3/.local/bin/python3.11 candidates/bootprogress-wrap-20261126/build.py out/bootprogress-proc-events-20261126-r3` exited 1 at
  `build.py:246`. The generated stock exit replay's `.text` first differs
  within `_wait4_nocancel` (stock source starting at `kern_exit.c:2897`,
  machine offset `0x4078`). The difference is in the **no-telemetry**
  comparison; the retained source and recorded argv do not reproduce the
  r64 exit object. `control-kern_exit-{original,replay}-text.log` is the
  witness. Do not bypass this gate for an exit-only build.
- Earlier r1 compiled the three objects and passed screen, framebuffer,
  page and event host tests (all exit 0). Its link exited 1 because the
  stale r64 staged include omitted the old snapshot bridge; r2/r3 restore
  the manifest-pinned `EnumaBootProgress2.inc` (`2007b690…`) from the
  original r62 recipe, without touching old output. In r3 the control
  exec `.text` and text relocations match; candidate video, candidate exec
  and stock exit compiles exit 0. No r3 candidate exit compile, link,
  prelink, package or final extracted-kernel check ran.
- Review artifacts in r3: `commands.json` (argv, cwd, exit),
  `proc-source.diff` (`4ccd796f5b3c8adc4f7c331b89a75b000bf5d5941d1bc49f3a6eb8447e8bb332`),
  generated sources/includes and `object-*-edges*.log`. The unlinked
  relocation evidence is two exec writes (`0x3c80`, `0x72cc`), one exit write
  in the r1 diagnostic object (`0x25b0`), and one try-snapshot via inlined
  `panel_sample` (`0x9578`). These are **not** final image edges. Artifact
  SHA-256: r3 exec `c21e9f6fbc561f8e1bbe9282f4a2daa502afd65d943b44818404313f499ef6cd`;
  r3 video `1230fe2b692fae70b2bc3d01677842e16c3fde4132f6ac5ff2a0801ff3a0c8ca`;
  r3 stock exit control `fdf3c096d96fa85a88506ae255bf302843a1f4eb9150129ed2683915dd5ed7ac`;
  r1 diagnostic exit `ac15dc70a339ad9a146308c2952ee9f99c51381b3cb14dcb89af53b5ab1981d1`.
- Final ASan/UBSan `test-proc.c` against the real recorder using host mutex
  shims: compile and run exit 0. Samples in `test-proc-final.log`:
  `not observed` in both columns initially; `backboardd` raw `rv=9` and
  then `rv=0` with no exec record; `launchd` short-lived two-event sample
  followed by same-identity re-exec and PID reuse without pairing; busy;
  max-count/max-identity display with no neighboring row writes. Four
  writers × 20,000 events per column checked coherent snapshots and counts,
  including saturation with latest fields still updating. These are host
  tests, not proof of the actual kernel's lock context or lifecycle.

## r64 exit replay resolution and r4 result

- r64, r65 and r6 select the same r64 object at filelist line 586; the
  earlier `r64-missing-header` attempt has the same object and staged
  source hashes. DWARF agrees with the original recorded source, cwd and
  Clang revision `58c46bae…` (live compiler SHA-256 `ef33ad67…`).
  Recorded argv at the exact original source path, changing only the
  object output path, gave identical repeat objects `5e059c9f…` but not
  the r64 object. The relocated build gives the same preprocessed token
  hash after removing line directives (`93ab7a0d…`) and the same mismatch
  without a prefix map. Path remapping and run-to-run variation are not
  the cause. Current generated headers were enumerated and hashed from
  the compiler's dependency output (571 files, including
  `meta_features.h` `d1488167…`).
- In the mismatched control, disassembly first differs at
  `_wait4_nocancel+0x20` (`__TEXT,__text+0x4078`, Mach-O file offset `0x4940`).
  Raw `.text` sizes were `0x4dec` original and `0x4e28` replay, and its
  relocation counts were 1128 and 1132 respectively. The recorded
  generated config in `ios-obj` is now zero bytes and its mtime
  (2026-11-25) postdates r64. The same tree's `obj` input shares SHA-256
  `06bd0c2b7af9fdc2553aba899a5238d0b6e284bd359750f4630fa2d4835f115e`
  with the 2026-11-11 and retained 24r `ios-obj` copies.
- Original r64 argv/cwd and exact staged source, changing only the output
  path and selecting that intact, hashed input, compiled with exit 0 and
  reproduced the **entire original object** SHA-256
  `24511f185e69fb0ed92cb4e5a6ee504658f634482f14d63f3cac474b5ccbebc3`.
  Exact bytes, `.text`, and its relocations all match; the r4 recipe still
  independently checks `.text` and its relocations before compiling the
  telemetry exit object. No XNU source was reconstructed from machine
  code, and no baseline object, setting values or checks were edited.
  Audit: `out/bootprogress-proc-exit-replay-audit-20261126/commands.json`,
  `dependencies.json` and the paired disassembly/relocation dumps.
- r4 command under WSL root:
  `/home/wh1stl3/.local/bin/python3.11 out/bootprogress-proc-exit-replay-audit-20261126/continue-build.py`
  (exit 0). The continuation runs the patched recipe with the unchanged
  r3 video/exec objects and r1/r3 host test results carried forward, not
  re-executed; see `commands.json` and `reused-host-checks.json`.
  The exit control, exit compile, native link, prelink, undefined-symbol
  and ABI checks all exited 0. The exact source diff is unchanged at
  `4ccd796f5b3c8adc4f7c331b89a75b000bf5d5941d1bc49f3a6eb8447e8bb332`.
- Against r6 only filelist lines 238, 585 and 586 change; r65
  `EnumaUserStack64.o` stays in place. Firmware/DTB, embedded args/config
  and unrelated payload members checked unchanged. The actual kernel
  extracted from the packaged boot matches `prelink.macho` byte-for-byte.
  Map and final disassembly (`event-edges*.log` and `leaf-*.log`) show:

  | Final caller | Call site | Target |
  | --- | --- | --- |
  | `_posix_spawn` | `0xfffffff00bd0fd9c` | `_enuma_bp_record_exec` |
  | `___mac_execve` | `0xfffffff00bd133e8` | `_enuma_bp_record_exec` |
  | `_proc_prepareexit` | `0xfffffff00bd1e30c` | `_enuma_bp_record_exit` |
  | `_enuma_bp_refresh` (inlined `panel_sample`) | `0xfffffff00b9e1a88` | `_enuma_bp_proc_snapshot` |

  Writers call only spin lock/unlock; snapshot calls only spin try-lock
  and unlock. On the selected caller paths, old NOTE_EXEC, signature,
  proc unlock/release, return-wait, and PID 1/prepare call counts agree
  with r6; source diff leaves their branches and panic path intact. No
  new worker or process walk. This is not runtime or liveness evidence.

  | r4 artifact | Bytes | SHA-256 |
  | --- | ---: | --- |
  | `boot.img` | 169951232 | `8c0c337fa056c2f08113606a5d87403099b4796a945f3e29dd541195e52b88a4` |
  | `payload.img` | 167772160 | `760c6ab90bc16b259013a3dfd879da03b130e28179f1485a642f890001de25b4` |
  | `native.macho` | 91935736 | `5785a3ef924b4d4bb227e62c47b9e47245ab8fbb2e12886bc92ff42a349db0a1` |
  | `prelink.macho` / `embedded-kernel.macho` | 124780544 | `f1589ca5af59598b3f6630b5ca04a3959048c8e1e6c7313cc0e6e6e14e771d30` |
  | `kern_exit.o` | 234296 | `db64be8feb6c92fd69a5e51d4e6d6a077eedf502ee6626eaf4c2e43213fec0d8` |

## r5 — two final review findings

Review: `deep_reviewer` `ses_dea374797ffeU3COiycUn0HPu2`. Lifecycle sites,
the recorder/lock protocol and r4 machine-code scope were accepted. The
two low-severity findings were display of saturated totals and the
re-exec identity explanation above.

- Each column independently displays `SAT` instead of a precise number
  at `UINT32_MAX`, in the same width as a ten-digit count. The header
  defines it as at least 4294967295. The max-width host sample has 117
  columns (119 visible): both identities are full-width and the exit
  column ends in `rv=ffffffff`. The sanitizer-backed test also checks
  `4294967294` in one column with `SAT` in the other, in both directions,
  the busy title with rows 25–28 blank, and untouched rows 23 and 29.
- Build command under WSL root:
  `/home/wh1stl3/.local/bin/python3.11 out/bootprogress-proc-events-20261126-r5-audit/build-r5.py`
  (exit 0). Target `video_console.o`, ASan/UBSan page and proc compiles
  and runs, link, prelink, undefined-symbol and ABI checks all exited 0;
  packing/extraction and the final four edge checks also passed.
  The driver reuses the fixed r4 exec/exit objects and control evidence
  under the original gates; it reruns the affected page checks only.
  Exact argv/exit records are in r5 `commands.json`.
- r4 and r5 have identical generated exec/exit TUs, generated hook diff,
  recorder/API, sample/refresh includes, and `kern_exec.o` / `kern_exit.o`
  bytes. Only the video object changed contents. The boot's extracted
  kernel retained all four call sites and targets in the table above
  at the same addresses. This delta does not reopen lifecycle or locking
  review. Firmware/DTB and embedded config match r4; non-kernel payload
  contents are unchanged. Exact formatter delta:
  `out/bootprogress-proc-events-20261126-r5/formatter-only.diff`
  SHA-256 `4a9968c6f6e37e8ec0337e0ff94d82f4dbf83fc8e4f5832b8841105638c7fcbd`.

| r5 artifact (under `out/bootprogress-proc-events-20261126-r5/`) | Bytes | SHA-256 |
| --- | ---: | --- |
| `boot.img` | 169951232 | `50bb81c21b0b56e08aad6a1f8a99e3f57d04e3eeea40914efc19baf5f5680fa2` |
| `payload.img` | 167772160 | `b09e2b572ec7ef64a65313a4bd82694b1396f5bdeb33e8781a6fd04802521384` |
| `native.macho` | 91935824 | `4c0c124cbcd0047b56995b207219eb8e5f3320b14dfa50ab059f49fd6cf15e2b` |
| `prelink.macho` / `embedded-kernel.macho` | 124780544 | `118de3551651cbb8da9f6a575dcd1f7d4cbbac89301b2c3a96c9ef5e20ca091d` |
| `video_console.o` | 333328 | `d84914c63e006345d2f9adb9d7d1de045627db256e02dcdbb1aaae2d3b3a22d0` |

If separately tasked, an independent verifier can run the candidate
`build.py` CLI in a fresh `out/` and check both the page tests and the
extracted-kernel evidence. No verifier was started for this round.
