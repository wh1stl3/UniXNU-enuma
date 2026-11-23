# r56 one-shot thread snapshot — 2026-11-23

Host build `self-checked`; no device operation. r56 changes the r55 kernel
and appends ` enuma-th=1` to the r55 payload entry arguments. No default
recipe, ADT, firmware, framebuffer or UFS changes.

## Implementation and review conditions

1. **Independent call object.** `scripts/build-enuma-r56-thsnap.py:94–115`
   wires the r54 BP source copy inherited by r55. BP allocates the distinct
   call only when `enuma-th=1`; if absent, it does not allocate, submit, look
   up, sample or log this probe. BP's existing `enuma-bp=1` is still needed
   to reach the trigger. It submits once after the round-2 BP report
   (`source/bsd/kern/EnumaBootProgress2.inc:35` in the output); no worker wait.
   The worker frees its own call; BP frees an unused call if BP allocation
   fails. Round 2 is nominally 120 kernel seconds after BP starts, plus BP
   report/scheduling delays. `t` is the worker's entry time in whole kernel
   seconds, not wall time, print time or a per-thread timestamp.
2. **Read-only saved-state sampling.** The worker calls
   `package/EnumaThreadSnapshot56Bsd.inc:7`, which uses `proc_find`, with no
   caller-held proc-list lock, checks `p_comm` for PID 34 `backboardd` and
   PID 5 `SpringBoard`, and takes a task ref before `proc_rele`. The OSFMK
   unit tries the task lock, takes at most eight thread refs and releases
   the task lock before per-thread locking. In pinned XNU `d8b80295118e`
   (`osfmk/kern/thread.c:1440–1461,1550,1068`), TIDs increase and threads are
   appended under the task lock; removing a thread preserves order. The
   sampled prefix is thus the eight lowest TIDs still on the task queue.
   Each thread uses `thread_mtx_try` → `splsched` → `thread_lock`, then the
   reverse unlock sequence. No printing, allocation or user-memory access
   in the locked sections. A failed thread mutex yields one `why=busy` row
   with immutable TID only.

`package/EnumaThreadSnapshot56.c:33` reads `upcb` once; the held thread ref
pins its allocation (`osfmk/kern/thread.c:751–773,838`,
`osfmk/arm64/pcb.c:263–274,379–391`). Separate relaxed scalar loads read
`flavor`, `count`, CPSR, PC and LR, with no flavor-asserting state accessor.
Only non-null PCB, `ARM_SAVED_STATE64`, `ARM_SAVED_STATE64_COUNT`,
`PSR64_IS_USER64(cpsr)` and `pc != 0` admit PC/LR; LR may be zero. Output
labels them `saved=possibly-stale/non-atomic`: the reference protects
lifetime, not a live or coherent register pair. There is no
`thread_get_state`; its hold/stop/release path can start a not-yet-started
thread (`osfmk/kern/thread_act.c:387–402,612–649`). `ct=NA` deliberately
omits the kernel continuation; a user saved PC is not a substitute for it.

| Output | Supports | Does not establish |
| --- | --- | --- |
| `n` / `shown` | Task queue size and referenced prefix; `shown` includes busy rows. `n=NA` means no task-lock snapshot. | All live threads, PID stability across boots or activity beyond the sampled prefix. |
| `st`, `we` | Per-thread scheduler-state bits at lock acquisition; `TH_WAIT` (`0x1`) supports a wait, `TH_RUN` (`0x4`) means running or runnable, `TH_UNINT` (`0x8`) means uninterruptible wait. `we` is the raw event token; with `TH_WAIT` it can be compared within a boot. | Wait duration, blocker ownership, user call stack or deadlock. Interpret bit combinations, not an enum. |
| `pc`, `lr` | Candidate ARM64 user saved addresses for offline symbolication against the matching mapping. | Current instruction, a backtrace, simultaneous values, or the location/cause of a wait. `NA` is rejection/unavailability, not proof of no user execution. |
| `slide` | PID 34's task-cached shared region slide; `UINT32_MAX` or unavailable → `NA`. | PID 5's mapping, attribution to a particular image, or proof of successful userland startup. |

The batch is at most **19 logical lines** (one header + two summaries +
16 rows), not necessarily 19 display rows. `proc_find` can wait for exec,
but only in the snapshot worker. The scheduler spin lock can contend after
the mutex try succeeds. Rows and processes are sampled sequentially and
console output can perturb scheduling; later BP reports can scroll it off.
Pointer-like event tokens and saved addresses are diagnostic data, not
production logging. Actual sample arrival, duration, targets, field values,
and no-argument parity on device are unverified. No new review of the
inherited r54 framebuffer path or independent verifier run.

## Readback and mechanical evidence

`boot.img` payload extracted at offset `2179072`, hashed against the FAT
image, then parsed from its embedded `unixnu.toml`:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1 dk=0 enuma-th=1
```

| Artifact | Bytes | Delta vs r55 | SHA-256 |
| --- | ---: | ---: | --- |
| `boot.img` | 169951232 | 0 | `e22e05438d199d1feedcbcccdbf8248bb2402cf107196660c8745eb7cbcc58f8` |
| `payload.img` | 167772160 | 0 | `2ad11201ab9028c9f9c6bbe86261f88a5ddd6725207b01d5c79b783664b36f8a` |
| `native.macho` | 91930776 | +17288 | `48dd256a21d2dd12100fc3d8fbfd5ce1fb23e75e03410d563c9c54e7976a13d9` |
| `prelink.macho` | 124776448 | +20480 | `942644cb5b62462c51293d94df52e88d1621a4d0588b19feb7bee62f0352af24` |
| `kernel.macho.adt` | 14128 | 0 | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` |

* Recompiled `kern_exec.o`: `33efd3758c7c80458dcdb772a08fdc6638998163c6e66c9caa32e4d1d9ece1f6`
  → `7f7b3104afcf7fd7040ee9107c334f83e3912273079d79f2341a48f1540d8560`.
  New `EnumaThreadSnapshot56.o`: `494b876f2c52ba361c068ab31c3fda911538cafc10054cfe98c991403f66f8a3`.
  Other 1005 filelist inputs, 15 direct archives and the prelink donor
  checked against the recorded r54/r55 link provenance and unchanged.
* Both Mach-Os: zero undefined including weak (`llvm-nm -u` and raw
  nlist checks); exactly one of each of the five format strings and the
  boot-arg key. Disassembly shows one BP `thread_call_enter1` and one
  `proc_find` callsite in the worker-only BSD bridge. The output logs
  record the final callsites and build commands.
* Only `Payloads/kernel.macho` and `unixnu.toml` changed in FAT. ADT
  byte-identical; trust cache and scratch image identical. All five r55
  artifact hashes unchanged, including r55 `boot.img`
  `e288d0f1759769b945c6fa347e52a546cbd0010e0979a95a76f35b9e1f863b01`.

Independent replay (WSL root, from the device repo, unused output path):

```sh
/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r56-thsnap.py --r56 --out out/r56-verifier
```

The replay uses a different output path; debug/link metadata can embed paths.
Compare the assertions and readback; the table above identifies the original
candidate at `out/ufs-sm8250-thsnap-20261123-r56/`.
