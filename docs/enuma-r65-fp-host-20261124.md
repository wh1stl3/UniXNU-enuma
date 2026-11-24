# enuma r65: ARM64 FP probe host evidence (2026-11-24)

`self-checked`; no device access, claim, cleanup scripts, or stage change.

## Why FP records, not payload ASCII

The [r64 symbolization review](ustack-symbols-r64-20261124.md) identifies
`__xpc_pipe_routine` as a candidate, not a caller chain: candidate addresses
in the raw stack words need not be saved return addresses. The
[r64 capture review notes](enuma-r64-ustack-host-20261124.md#probe-design-runtime-unverified)
also explain that raw stack words can contain user data and are not an
unwind. Dumping more payload as ASCII could expose IPC/application data
without identifying the caller. r65 adds only raw LRs from ARM64 frame
records, not message/payload decoding. The existing r64 stack words are
unchanged; this is not a removal of that diagnostic.

## Probe and failure semantics

- The r64 worker remains opt-in via `enuma-bp=1` at `ENUMA_TH_TICK=2`,
  sampling `5/SpringBoard` and `34/backboardd`. There is no new IPC hook,
  callout, suspension, write to target memory, or diagnostic panic.
- `package/EnumaUserStack64.c:29–54` snapshots `ss_64.fp` with `sp` only
  after the existing saved-state, user-mode and wait-PC checks. The
  FP walk at `:78–114` runs after the existing 512-byte SP sample succeeds.
  It checks nonzero 16-byte-aligned FP and that **all 16 bytes** fit in
  `[vm_map_min(map), min(vm_map_max(map), MACH_VM_MAX_ADDRESS))`, using
  subtraction rather than overflowing `fp + 16`. It reads `{next_fp, lr}`
  via `vm_map_read_user` on the referenced target map and follows only
  `next_fp > fp`. It reads at most 16 records per target; no retries.
- Task/map/thread references stay live across each read. `thread_lock`,
  `thread_mtx`, task lock, and raised IPL do not: the checks complete and
  release them before `vm_map_read_user`, since its `copyin` may fault or
  block. Before and after each read, the worker rechecks map/slide and the
  saved wait/PC/SP/starting FP; a failed check or read excludes that record.
  A validated current record's LR is retained even if its next FP fails
  the monotonicity check. Failure prints `why` and whatever prefix was
  accepted, grouped four LRs per row (short final row, no padding).
- **引用不等于冻结栈，栈不稳时不能拼接。** The target may resume and
  return to the same saved state, or another thread in the same map may
  change a record between reads. A detected change stops the walk; the
  printed prefix is diagnostic only, not an atomic backtrace. Do not
  splice it with another tick/run or with the separate SP words to fill gaps.
- A read can fault or stall, and raw LRs expose addresses; the 16-frame
  count bounds reads, not elapsed time. Frame-pointer omission, hand-written
  frames, and unstripped signed LRs may limit symbolization. No live
  callout/copy behavior, usable `backboardd` caller, or panic-free runtime
  has been established. No independent verifier or deep review ran here.

## Mechanical evidence

WSL root, from `UniXNU-enuma`, exit 0:

```sh
/home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r64-ustack.py --r65
```

Only `EnumaUserStack64.o` was recompiled, using the recorded r64 compiler
command; only its entry in the 1,008-entry filelist was substituted.
The `link-input-sha256.json` inventory confirms the other 1,030 link/donor
inputs retained their paths and before/after bytes, with the 16 applicable
r64 rebuilt link inputs checked against their manifest pins. The recorded
link and prelink commands changed only the output/filelist paths. All five
r64 artifacts below were rehashed before/after and still equal their r64
manifest. Source pin: UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241`,
XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f`.

| Unit | r64 SHA-256 | r65 SHA-256 |
| --- | --- | --- |
| `EnumaUserStack64.c` | `bf00961fcf59a39489265894b805c637f0467e152a1d2bb8cf77a5ba714c845f` | `2da358cc5f52c000d0a411614a13de2770a53174ac60d4e6899c89dae53bcce1` |
| `EnumaUserStack64.o` | `be54932bbca23da57919c53c0b31555e96006b09bd9e3430b0eefdd5e821be45` | `834a280e2ccbe30185ade12dfd6fe4577608ee47a54a68fc1022572831d7e91f` |

| Artifact | r65 bytes | Delta vs r64 | r64 SHA-256 | r65 SHA-256 |
| --- | ---: | ---: | --- | --- |
| `kernel.macho.adt` | 14,128 | 0 | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | same |
| `native.macho` | 91,914,928 | +320 | `b6047562c6a08bed7fafd19d2e11546f231a33ab8f7874f6fb06bf5d130199cc` | `7c4cee3d227e255be059b82eec3e12b10247cd130dcf935c2868cf891732a7d4` |
| `prelink.macho` | 124,760,064 | 0 | `8dee8cd908b8ef6a7e9ea49bf46cbc3a99efccfd8b1fa35683ff6e5247b11c1f` | `d0868a4f0146578bbae7397ce4814e999b617ac3a7627fd7fef4d0e012b92db3` |
| `payload.img` | 167,772,160 | 0 | `08718fc9f2f9758759a07bcede3689070c0c68a629ebb68c7e6cc5f2396367c1` | `85b8a4031150f3d9cebdfda0ac0f8a4f528c4e7aa19e1e482ef1aa77f6e85313` |
| `boot.img` | 169,951,232 | 0 | `8a80bfde1891495102bee30326de230735ad1499c6cd1130dd641031ec29b446` | `56267f02fab8c3712faeb77436e9d6eaa1e2bcf45bd2387875282ff6d5e56a34` |

Output: `out/ufs-sm8250-fp-20261124-r65/`. The boot prefix differs only
in the image ID; the embedded FAT changes only `Payloads/kernel.macho`.
Extracted ADT and `unixnu.toml` are byte-identical to r64. Both Mach-O
images have zero undefined including weak (`llvm-nm -u` and raw `nlist`),
one copy of each FP format, and the same checked branch sites:
repeat → submit `0xfffffff00bd155bc` (also equal to r64),
capture → walk `0xfffffff00bfc678c`, walk → read `0xfffffff00bfc6a3c`.
The output manifest also records link inputs and FAT member hashes. The
host ASan/UBSan harness used the actual walker/printer with mocked map,
status checks, and read: 14 cases covered alignment, interval edges,
read failure, equal/decreasing links, sample change, the 16-frame cap,
and 1–4-address output rows (`tmp/fp-host-test.c`, `logs/fp-host-test.log`).

Full XNU arguments read back from **r65 boot.img**, equal to r64:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 dk=0 sheng-smp=1 cpus=2 armcpu-diagnostics=1 enuma-bp=1 armcpu-self-ipi=1
```

Device record check from `UniXNU/`, exit 0:

```sh
/home/wh1stl3/.local/bin/python3 -B scripts/porting-record.py check \
  --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe
```

Independent replay: rerun the build with
`--out out/ufs-sm8250-fp-20261124-r65-verifier`, then rerun the record
check. Compare the manifest's object scope, FAT delta, ADT, boot args,
and imports; a different output path can change binary hashes.
