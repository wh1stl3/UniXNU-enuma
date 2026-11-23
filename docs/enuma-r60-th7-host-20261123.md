# r60 seven-process snapshot — 2026-11-23

Host build self-checked; no device operation. Isolated r58 derivative, default
off unless `enuma-th=1`, with inherited BP trigger and transmit ring. No plist,
boot-argument, default recipe, ADT or UFS changes.

Targets in order: 1 `launchd`, 5 `SpringBoard`, 34 `backboardd`,
58 `distnoted`, 60 `notifyd`, 82 `securityd`, 26 `amfid`. The inherited BSD
bridge checks PID and `p_comm`, references the task, and balances references.
Each task reports at most eight threads; identity failures report `why=`.
`thread_mtx_try` failure reports a busy row. No printing under locks.
The existing five saved-state checks, `ct=NA`, and PID 34 slide are unchanged.

Pinned XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f`:
`osfmk/kern/thread.h:392-395` defines `wait_event` and `waitq_t waitq`;
`osfmk/kern/waitq.h:129-133` defines union member `wq_q`.
The new code copies `(uintptr_t)thread->waitq.wq_q` under the existing
`thread_lock`, without dereferencing it. `waitq.c:1380-1386` locks the thread
before `waitq_thread_insert` sets `wait_event` and `waitq` at `:568-570`;
`:834-839` locks it before clearing wait state. Rows are sampled sequentially.

| Observation | Interpretation and limits |
| --- | --- |
| `TH_WAIT` (`st & 1`), nonzero `wq` | At this thread's capture it was waiting with that raw waitq pointer. `we` is the event token; neither identifies a handler or owner by itself. |
| Same nonzero `wq` in two rows | Same waitq address at two sampling instants; this does not prove the same higher-level object or simultaneous waiting. Queues can serve multiple events; compare `we` too. |
| `wq=0x0` | No waitq pointer at this capture; not proof the thread never waited. |
| `why=busy`, `wq=NA`, or process `why=` | Capture unavailable, not evidence of a wait or absence of one. |
| `pc` / `lr` | Best-effort possibly stale and non-atomic user saved state, not a current kernel stack; `ct` remains unavailable. |

Maximum snapshot is **64 logical lines** (one header + seven summaries + 56
thread rows); inherited tx dump adds at most 16 lines, and the separate BP
report approximately six, about 86 total. Display wrapping and other output
can exceed this and scroll the snapshot. Frame size in the built worker is
3120 bytes including saved registers; increased stack and sampling overhead,
the inherited potentially blocking `proc_find` and contended scheduler spin
lock require deep review. No claim of panic impossibility or runtime timing.
PID reuse, absent tasks, truncation to eight, saved-register staleness, console
visibility and device behavior remain unverified. No independent verifier run.

## Mechanical evidence (self-checked)

`out/ufs-sm8250-th7-20261123-r60/`: `candidate-manifest.json`,
`commands.json`, `logs/`. Base UniXNU HEAD before/after
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

| Artifact | bytes | delta vs r58 | SHA-256 |
| --- | ---: | ---: | --- |
| boot.img | 169951232 | 0 | `532e2776041bfbcc6b1772048b499dd79419bfa9143d1b82c4ad45b2dce725a7` |
| payload.img | 167772160 | 0 | `6dff78c138820fb5bc6913393227cdd538d8d54b2ca217171a7b69ae7e6291b8` |
| native.macho | 91931608 | +24 | `18c391eb947ba005dd6d418883141aaf4d69080470aa51e25567f90265d25b92` |
| prelink.macho | 124776448 | 0 | `0731ae64ec49099cc8e3ae1297cc3f9fb6f05f3bbd3d3fc89faee24aa5f8710c` |
| kernel.macho.adt | 14128 | 0 | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` |

Only `EnumaThreadSnapshot56.o` changed:
`7f9964a56f362f60df2ddab9974368579052754e32a8c014846b4b376c0e3022`
→ `0798e43da3fa6f59eaf70cdf240234a864c29c87c38f2ba509aa9026fdb2755e`.
The other 1006 filelist inputs, 15 direct archives, donor and five r58 artifact
hashes are unchanged; r58 boot SHA-256
`e65ad679a1f13adb22012cb825e85deacb741be7cddd8cdc46737e7d838ea285`.
ADT is byte-identical; only FAT member `Payloads/kernel.macho` changes.
Native/prelink have zero undefined including weak; transmit formats, both
new thread-row formats are unique, and worker-to-dump and send-to-recorder
callsites are each one. Full commands and disassemblies are in `logs/`.
From the boot image's extracted FAT, readback equals r58 byte for byte:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1 dk=0 enuma-th=1 enuma-txpeer=1
```

Independent replay, WSL root from device repo with a new output path:
`/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r57-txpeer.py --r60 --out out/r60-verifier`.
Link metadata may contain output paths.
