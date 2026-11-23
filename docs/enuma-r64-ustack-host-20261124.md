# enuma r64 user-stack diagnostic — host build (2026-11-24)

`self-checked`; no device access or cleanup/retention scripts.

## Source baseline and rebuild decision

Cleanup removed the staged sources and intermediate inputs referenced by the
incremental r63 link recipe. The new plan is to rebuild the required units in
one pass from the current r63-equivalent source and flags, then record the
SHA-256 of every new object. The historical r47 hashes identify old artifacts;
they are not the acceptance test for a build from the reconstructed current
source and new staging paths. Reused unaffected r63 inputs and two intact
r4 archives (`libRamBlock.a`, `libVerifiedRootDependencies.a`) whose bytes
match the r63 input pins; the missing diagnostic objects were recompiled
rather than copied back into deleted historical directories.

r63 is a boot-argument-only repack of r62 and has no `source/` tree. The
pinned `.cache/xnu-work` used by the r62 compiler exists at
`d8b80295118ef25ac3a784134bcf95cd8e88109f`; UniXNU HEAD is
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`. The XNU tree is not the
complete instrumented tree: the four checked prior probes are split across
r62 `source/bsd/kern/` (`EnumaBootProgress2.inc`, `EnumaBootProgress62Cpu.inc`),
r57 `source/` (`EnumaThreadSnapshot56.c`) and r58 `source/`
(`EnumaTxPeer58.inc`). Each also has a device `package/` source.
The new `EnumaUserStack64.c` exists in `package/`.

## Source generation and link-input preflight

The seven base XNU translation units below and their Clang command fragments
exist. The historical staged copies at the selected paths do not. This is the
initial missing-input inventory.

| r63 filelist line | Missing object | Staged source and reconstruction |
| ---: | --- | --- |
| 199 | `vm_fault.o` | r47 `source/osfmk/vm/vm_fault.c`. The retained source-generation block of `build-enuma-r42-matchcnt.py:202–222` ran in memory against the pinned XNU source, SHA-256 `85e9a0d331c2fcf94d9ef23032a97dbf917220fedfd44e9204475efc9c73d74e`. |
| 565 | `bsd_init.o` | r40 `source/bsd_init.c`. Apply the timebase and r11 keystore patches to the r13 audit copy to reproduce the r11 source; then run the r40 insertion. The regenerated source SHA-256 is `fe380be5b4dc4573b47455bb4264964cfd831a2bd4c56ac7e7b7679af59d4978`. |
| 586 | `kern_exit.o` | r21 staged `bsd/kern/kern_exit.c`. Applied the documented r21 `proc_prepareexit()` diagnostic to the pinned base, without the superseded r17 tail hook. |
| 678 | `vm_unix.o` | r15 staged `bsd/vm/vm_unix.c`. Base source and `enuma-r15-shared-region-probe.patch` survive. |
| 807 | `OSKext.cpo` | r11 staged `libkern/c++/OSKext.cpp`. Base source and `enuma-r11-board-classes.patch` survive. |
| 935 | `IOUserClient.cpo` | r43 `source/iokit/Kernel/IOUserClient.cpp`. The r46-initial staged copy contains the six r43 M/N/O/P/I hooks; the r43 compile command survives. |
| 956 | `IOKitBSDInit.cpo` | r10 display-selected `iokit/bsddev/IOKitBSDInit.cpp`; recompiled with the surviving r4 command for this same input. |

`mach_msg.o`, the eighth object in the earlier inventory, was already present
at this scan and was rebuilt anyway. `kern_exec.o` and the new
`EnumaUserStack64.o` were also compiled.

Root WSL checked all 1,007 filelist entries: **7 missing**, plus **8 missing
direct linker inputs**: `libShengUfs.a`, `libRamBlock.a`,
`libVerifiedRootDependencies.a`, `EnumaUfsOwnerQuery.o`, `libEnumaGopLegacy.a`,
`libAppleKeyStoreState.a`, `libEnumaBootWatchdogPolicy.a` and
`libShengHidInputStandin.a`. The prelink donor exists. The final pre-link
check found **0 missing** across 1,008 filelist entries, direct inputs,
the resolved firehose archive and the prelink donor.

The follow-up source scan found the exact source input of the r40
`NativeUfs.cpp` generator under startroot-WIP
`self-check/resume-20261118-r11/merged-source/`, plus the matching RamBlock
headers. This is a separate component source, not recoverable from
`.cache/xnu-work` plus XNU patches alone. Running the r40 insertion against
that source produced SHA-256
`7ec57752896a57621ba02a14449a8b81fd15a79a8e0b5a92576c8b2548dfab6b`.
The initial compile stopped at `BootWatchdogPolicy.o` because the inherited
r62 `-include` pointed into the deleted r10 `owner-data-volume.h`. The r4
header was recovered and its three UUID literals were cross-checked against
r63 native before enabling a path-only substitution.

## Rebuilt inputs

SHA-256 below is from this build, not verification against r47. The local
`candidate-manifest.json` and `commands.json` have the machine-readable
inventory and the actual compiler, linker and prelink invocations.

| Unit | SHA-256 |
| --- | --- |
| `mach_msg.o` | `2352cd45263853bacf75680ea236397b0dd54b8c3369518362e94053cb42b7fe` |
| `vm_fault.o` | `6d809be0b456c88bdd07561b8b1d91714136e0ff52045a7bd0738ab14b2878e5` |
| `bsd_init.o` | `89a4686f8afc413db138449daf383501ab8b88b42a350c6c116d5a0db7a28176` |
| `kern_exit.o` | `24511f185e69fb0ed92cb4e5a6ee504658f634482f14d63f3cac474b5ccbebc3` |
| `vm_unix.o` | `8d0115b386fb1d1843f25c5f891061222cc85819a81fa349323fa8481cbab3b2` |
| `OSKext.cpo` | `dba81e5c8128c772010a88a84a18fb2aeddb36da67a7aaf2192fbd1e17ba8dba` |
| `IOUserClient.cpo` | `a00ae92e9827f540342687af8b1286a948d49bcc164a7ee851e9a379e013bfc7` |
| `IOKitBSDInit.cpo` | `09d4a807c6a51ac44182a38588604a1b7ae410b50908e3de2057f0163f031d4b` |
| `NativeUfs.o` | `c7acc3659d54138c6eb2a2fec3f421b165fc2909a612ade0bbebee4ae7f4ee32` |
| `libShengUfs.a` | `cef82e0a3093f5e5dd563b328cc140c5a66847183a2ca3c90d1b22282a098b89` |
| `EnumaUfsOwnerQuery.o` | `768ba0c391e8276fcf6a565a70eeb0b0c996d3f8561408f18105ee05c10a64ae` |
| `BootWatchdogPolicy.o` | `a72890e6a15ae5be7418e74203575021c555d01d0e8a3c2502d8ec4e9b7f0736` |
| `libEnumaBootWatchdogPolicy.a` | `997e24f94eaa916b189d35ec7ff276b0d90609565a9b03e5482c423c63b3168d` |
| `NativeKeyStoreEvents.o` | `fee2e51ef9ea69e6a4f157a6296e86f324a09eb988da1a65a78954afc449d2a2` |
| `EnumaKeyStoreProbe.o` | `0536cd232556d034757777f444a0b8378e6f6a2ef5bc0bab324a63f4f0278390` |
| `NativeKeyStoreEvents.late.o` | `5959cb2f2cadbe3e81177725ca886a885702c4b7cf7afaeb4e4deba2502ded4e` |
| `libAppleKeyStoreState.a` | `dfb7eacc06c335d926e12cb68ee00ec55bd20217a3d66be45c9a84594c464149` |
| `NativeLegacyDisplay.o` | `995a92a0c1b75b7de7660fb8d11c50078741cd3c036a69858f1d450185917b09` |
| `NativeLegacyDisplay.late.o` | `fa0ed24b20655a5299e10c4098befd5a11ab9994885c0594cd14109f051827d7` |
| `libEnumaGopLegacy.a` | `ac7f0124b28711c24c9ede4dc437e4100514ce42ca3c246574d661bbbd7bdb96` |
| `NativeHidInput.o` | `f775e330c17e57b3168f59e72fcdc635ffff1b3908b0a897a4285245cc955f90` |
| `EnumaHidStandin.o` | `6476eee54d2852d47a62f412992c161302153f1675b34af4a93dce281f903d27` |
| `hid-original-bindings.o` | `d6290d09b1830369a8b4f637ef73357a8c1272a8d7136a15fdc2c7f4a2be7d6b` |
| `NativeHidInput.late.o` | `162f84fc68e8b8114ed57aaed4082498a56844113218ee46402df29d4fa55e36` |
| `libShengHidInputStandin.a` | `71bf25bc334a931097003b2236af215de11d11f2417931ded1fd0a42742fa1ec` |
| `kern_exec.o` | `18930a3213bffb6ae2bc63e3512a1cf4f90b32183079a1cc0b10dfa9d10710f1` |
| `EnumaUserStack64.o` | `be54932bbca23da57919c53c0b31555e96006b09bd9e3430b0eefdd5e821be45` |

## Mechanical evidence

The second WSL root run from `UniXNU-enuma` exited 0:

```sh
/home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r64-ustack.py --r64
```

Output `out/ufs-sm8250-ustack-20261124-r64/`: `boot.img` is 169,951,232 bytes,
SHA-256 `8a80bfde1891495102bee30326de230735ad1499c6cd1130dd641031ec29b446`.
Only `Payloads/kernel.macho` changed within the FAT; its bytes match r64
`prelink.macho`. The boot prefix differs only in its image ID. The r64 ADT
extracted from that boot image is byte-identical to r63's ADT.

All five existing r63 artifact hashes match its manifest, including
`boot.img` (169,951,232 bytes):
`f94c738c9b04b8edaec46775c00bd99d239b4a72a1f2fcf2c46a709b096eaa64`.
The ADT is 14,128 bytes, SHA-256
`1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`.
Both r64 Mach-O images have zero undefined symbols, including weak
(`llvm-nm -u` and raw `nlist`). All five new `enuma-stk:` formats occur
exactly once per image; a separate NUL-terminated `enuma` string scan found
no r63 strings removed and exactly five added. Both images have the same
`_enuma_bp_repeat` → `_enuma_stk_submit` instruction `0xfffffff00bd155bc`
and `_enuma_stk_capture` → `_vm_map_read_user` instruction
`0xfffffff00bfc6500`. Other call edges are recorded in the manifest.

Full args read back from the **r64 boot image**, identical to r63:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 dk=0 sheng-smp=1 cpus=2 armcpu-diagnostics=1 enuma-bp=1 armcpu-self-ipi=1
```

Device record check (25 areas, exit 0), from `UniXNU/`:

```sh
/home/wh1stl3/.local/bin/python3 -B scripts/porting-record.py check \
  --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe
```

Independent verifier: rerun the build command above with
`--out out/ufs-sm8250-ustack-20261124-r64-verifier`, then rerun the device
record check. The manifest includes explicit link, prelink, FAT and boot
readback checks; distinct output paths can change object/Mach-O hashes.

## Probe design (runtime unverified)

1. The existing `enuma-bp=1` callback submits a one-shot worker at
   `ENUMA_TH_TICK`. The worker targets two PID/name pairs (`5/SpringBoard`
   and `34/backboardd`), taking at most eight thread references per target.
2. A candidate must be a waiting, non-running, non-terminating AArch64 user
   thread with a saved PC at the donor trap return PC plus the task's
   shared-region slide. Multiple observed matches suppress the sample.
3. The worker holds task, map and thread references, but no lock or raised
   IPL across the single `vm_map_read_user` call. It reads 64 words (512
   bytes) from the saved SP and does not write target memory.
4. Map/slide and waiting PC/SP checks bracket the copy. A failed check or
   copy suppresses stack-word output, and acquired references are released.

The bounded scan can miss a thread. Equal PC/SP before and after does not
make the read atomic, establish the Mach IPC wait reason, or unwind the
stack. The copy may fault or stall; emitted words can contain raw user data.
An all-strings comparison and preserved call sites do not prove behavior of
rebuilt code is instruction-identical to r63.
Callout execution, lock/reference behavior, live PC matching and on-device
output remain unverified. Deep review and independent verification were not run.
