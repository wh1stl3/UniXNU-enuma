# r57 Mach send peer trace — 2026-11-23

r57 is an isolated derivative of r56 for PID 5 and 34. No device
operation or stage change. This is diagnostic logging, not a default
recipe or production feature.

## Hook and concurrency

The generated `source/ipc_kmsg.c:5266` records the original header ID and
the copyin-translated remote `ipc_port_t` in `ipc_kmsg_send`, after the
existing `IP_VALID` assertion and before `ip_mq_lock`. The original
source is UniXNU's patched XNU worktree at `d8b80295118e` (the source
file is APSL 2.0); it is not edited in place. `mach_msg2_trap` →
`mach_msg_trap_send` copies in the user message and then calls this
function (`osfmk/ipc/mach_msg.c:731`). Internal sends in a matching PID
context can also appear; a kernel reply generated and forwarded inside
the original call does not reenter the hook. Copyin failures and circular
messages rejected before the hook do not appear.

`enuma-txpeer=1` enables recording via the existing startup tunable
mechanism; the branch does not read the PID or write the rings when
disabled. `proc_selfpid()` resolves `current_proc()` to its PID without
lookup, ref acquisition or lock. `enuma-th=1` with the inherited BP
trigger is still required for the one-shot dump
(`source/EnumaThreadSnapshot56.c:147`). The added hot-path code
does not acquire a lock, allocate, log, dereference the destination or
affect a send result. The inactive kernel is not byte-identical to r56.

Each PID has eight slots. A relaxed 64-bit fetch-add reserves a ticket.
A lock-free 128-bit compare-exchange publishes the ticket's low 32 bits,
the full 32-bit ID and the full 64-bit port as one unit. The circular
tag comparison prevents an older, delayed writer from overwriting a slot
already published by a newer writer. It assumes same-slot competitors
are less than half the 32-bit tag space apart. The reader takes one
head sample per PID and reads those eight tickets **newest reservation
first** (PID 5, then 34). It reports `id=NA port=NA` for a hole or an
already overwritten slot instead of printing a mixed or stale tuple.
The two rings and the preceding thread-snapshot rows are not sampled as
one transaction. The port is an integer token, not a retained reference.

`owner=NA` is unconditional. An outstanding port right does not establish
a stable kobject association for arbitrary destination ports.
`ipc_kobject_get_locked` requires a held port lock or a type with a
stable association (`osfmk/kern/ipc_kobject.c:890–937`); a safe
kobject → task → BSD process walk also needs a lifetime contract.
Many service ports are not task kobjects, and a port set is not a
send destination or a task. The probe does not attempt this walk.

| Observation | What it supports | What it does not establish |
| --- | --- | --- |
| Known `msgh_id`, same port token | Repeated attempts with the same ID and destination address in this boot; a matching subsystem map can suggest a request family. | Message delivery, server dispatch, port ownership or a unique RPC interface from ID alone. |
| Same ID, different token | The observed attempts used different destination addresses. | Different owning processes or the identity of either recipient. |
| Last recorded send before a receive wait | A candidate peer to correlate with independent message/thread evidence. | Same thread, receive port, pending reply, causal link, or that the wait is not an idle receive. |
| `NA`/no rows | No usable tuple for that reservation/no reservations sampled for that PID. | No IPC, no receive, or that the expected process always held the sampled PID. |

Port addresses can be reused within a boot and are not comparable across
boots. Restrict raw pointer output to this diagnostic image. Extra atomic
operations and up to 16 logical console lines may perturb timing; later
BP output can scroll them off. Runtime timing, PID assignment, log
visibility and functional parity with the option disabled are unverified.
The new concurrent ring requires deep review before device use.

## Host verification

Build and readback `self-checked`. The boot payload was extracted at
byte offset `2179072`, verified against the FAT image, then parsed for
the complete XNU entry arguments:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1 dk=0 enuma-th=1 enuma-txpeer=1
```

| r57 artifact | Bytes | Byte delta vs r56 | SHA-256 |
| --- | ---: | ---: | --- |
| `boot.img` | 169951232 | 0 | `e669e3bdf2f7f5315d9eb28e1231bdd02fe5f6245c2a961b88e0fa1ebf071169` |
| `payload.img` | 167772160 | 0 | `ca11ee82ea16ab2d21a63ab8220ac89fa84e70af4e7ba722e7b300a217e8759a` |
| `native.macho` | 91931504 | +728 | `c69c79a19254389062b4f70938b2f78220a466186a9d14679eccb0f12ac2d3c6` |
| `prelink.macho` | 124776448 | 0 | `4ec89325fbbc400f8914e5e5676b73735bbc604e149bd33e1dd3f9f7c4ca87d8` |
| `kernel.macho.adt` | 14128 | 0 | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` |

| Recompiled link input | r56 SHA-256 | r57 SHA-256 |
| --- | --- | --- |
| `ipc_kmsg.o` | `a0b59cbdd40ef31abdc4765683d843c6f04f59388f58c18cefd6733b15c43995` | `200c19f3349b66b30878903de25396e907742c34708f44bf4430bad8965b8b71` |
| `EnumaThreadSnapshot56.o` | `494b876f2c52ba361c068ab31c3fda911538cafc10054cfe98c991403f66f8a3` | `7f9964a56f362f60df2ddab9974368579052754e32a8c014846b4b376c0e3022` |

- The other 1005 filelist inputs, 15 direct archives and the prelink
  donor matched r54/r56 provenance and did not change. Both Mach-Os
  had zero undefined symbols including weak (nm plus raw nlist).
- Both Mach-Os contain each new output format and both option keys
  exactly once, with one linked send → record and one snapshot worker
  → dump callsite each. The record helper calls only `proc_selfpid`
  and implements atomics inline with exclusive load/store pairs.
- Only `Payloads/kernel.macho` and `unixnu.toml` changed inside FAT.
  ADT was identical byte for byte; the trust cache and scratch image
  hashes matched. Firmware/DTB hashes matched r56, as did the boot
  prefix outside the boot header ID.
- All five frozen r56 artifact hashes were unchanged after build,
  including r56 `boot.img`
  `e22e05438d199d1feedcbcccdbf8248bb2402cf107196660c8745eb7cbcc58f8`.
  Full details are in `out/ufs-sm8250-txpeer-20261123-r57/`:
  `candidate-manifest.json`, `commands.json` and `logs/`.

Independent replay, WSL root from the device repo with an unused output:

```sh
/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r57-txpeer.py --r57 --out out/r57-verifier
```

Different replay paths can affect debug/link metadata.
