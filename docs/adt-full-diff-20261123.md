# enuma r34 / nuwa logo candidate: full ADT property difference

Host-only **self-checked** comparison; no build, device access, or ADT edit.
This separate document extends `display-config-diff-20261123.md`. Inputs are
the two FAT payload ADTs identified by SHA-256 in that document. The nuwa
logo observation is a parent transcription, not independent verification.

Using `member()` and `parse()` from
`scripts/compare-display-config-20261123.py`, compare the union of property
paths and raw `(value, flag)` tuples without the display-name filter:

```python
e = m.parse(m.member(m.ENUMA, 'Payloads/kernel.macho.adt'))
n = m.parse(m.member(m.NUWA, 'Payloads/kernel.macho.adt'))
nuwa_only = n.keys() - e.keys()
changed = {k for k in e.keys() & n.keys() if e[k] != n[k]}
enuma_only = e.keys() - n.keys()
```

Result: **5 nuwa-only, 28 changed, 9 enuma-only**. All listed flags are 0;
`E` and `N` are lengths in bytes, `—` means absent. The ADT root appears as
`:property`. Values are optional: opaque IDs, unique IDs, root UUIDs, random
seeds, security material and hardware register bytes are not reproduced.
Even for equal lengths, entries in the changed table have different raw
values; no difference here is flag-only. Full per-device path/length lists
remain in `enuma-adt-properties-20261123.txt` and
`nuwa-adt-properties-20261123.txt`.

The last column answers whether **OS version alone** explains the difference:
**No/H** = hardware/board-specific; **No/P** = donor device/profile identity
(iPad vs iPhone), not established to be the OS version; **No/C** = packaging,
boot policy, or configuration; **Unknown** = no source sufficient to say.
Possible impact means a potential path, not a demonstrated causal diagnosis.

## nuwa only

| Property | E | N | Category; possible user/display/service impact | Version alone |
|---|---:|---:|---|---|
| `/chosen/manifest-properties:BNCH` | — | 48 | security; Image4/boot authentication may affect service launch | No/C |
| `/chosen:boot-manifest-hash` | — | 48 | security/storage; boot-set identity can affect mount/launchd | No/C |
| `/chosen:display-scale` | — | 4 | display; MobileGestalt scale may affect display-mode consumers; N u32 LE 3 | Unknown |
| `/chosen:mix-n-match-prevention-status` | — | 4 | security; Image4 policy may affect authentication and startup; N u32 LE 0 | No/C |
| `/defaults:no-effaceable-storage` | — | 4 | storage/security; potentially changes storage/security consumers; N u32 LE 1 | Unknown |

`boot-manifest-hash` is a boot-set identity, not a generic dummy setting:
UniXNU `docs/zh/porting/device-tree.md:178`; another board's mount failure is
documented in `docs/zh/devices/marble-milacy.md:219,237`, not evidence of this
failure on enuma. nuwa's `docs/image4-firmware-evaluate-20261110.md:70`
describes its experimental BNCH as session-generated. Do not transfer
either value or infer authentication from their presence.

## Present on both, value differs

| Property | E | N | Category; possible user/display/service impact | Version alone |
|---|---:|---:|---|---|
| `/arm-io/intc:redistributor-stride` | 8 | 8 | CPU/hardware; interrupt delivery can indirectly affect all startup | No/H |
| `/arm-io/intc:reg` | 32 | 32 | CPU/hardware; interrupt controller resources affect all startup | No/H |
| `/arm-io:ranges` | 24 | 24 | other/hardware; MMIO translation affects drivers and startup | No/H |
| `/chosen:chip-id` | 4 | 4 | device identity; consumers may choose platform behavior | No/H |
| `/chosen:darwinboot-memory-size` | 8 | 8 | memory; ownership capacity can affect allocations and startup; E `0xaa000000`, N `0x130000000` | No/C |
| `/chosen:dram-base` | 8 | 8 | memory; physical placement affects whole system | No/H |
| `/chosen:dram-size` | 8 | 8 | memory; RAM capacity affects whole system | No/H |
| `/chosen:random-seed` | 256 | 256 | security; randomness can indirectly affect processes | No/C |
| `/chosen:root-matching` | 171 | 171 | storage; selects root volume and thus userland | No/C |
| `/chosen:unique-chip-id` | 8 | 8 | device identity/security; identity consumers may affect services | No/C |
| `/cpus/cpu0:compatible` | 15 | 16 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/cpus/cpu1:compatible` | 15 | 16 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/cpus/cpu2:compatible` | 15 | 16 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/cpus/cpu3:compatible` | 15 | 16 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/cpus/cpu4:compatible` | 15 | 16 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/cpus/cpu5:compatible` | 15 | 16 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/cpus/cpu6:compatible` | 15 | 16 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/cpus/cpu7:compatible` | 15 | 14 | CPU; hardware discovery may indirectly affect startup | No/H |
| `/product:artwork-device-idiom` | 4 | 6 | display/device identity; UI may choose tablet vs phone behavior; E `pad`, N `phone` | No/P |
| `/product:artwork-device-subtype` | 4 | 4 | display/device identity; artwork selection may affect UI; E u32 2732, N u32 2436 | No/P |
| `/product:artwork-scale-factor` | 4 | 4 | display; artwork scale may affect UI assets; E 2, N 3 | No/P |
| `/product:compatible-device-fallback` | 8 | 10 | device identity; compatibility decisions may affect services/UI | No/P |
| `/product:product-description` | 38 | 9 | device identity; descriptive user-facing consumers possible | No/P |
| `/product:product-id` | 20 | 20 | device identity; product consumers may select different behavior | No/P |
| `/product:product-name` | 38 | 9 | device identity; descriptive user-facing consumers possible | No/P |
| `:compatible` | 25 | 30 | device identity/hardware; matching affects drivers and startup | No/H |
| `:model` | 8 | 11 | device identity; model-specific userland behavior possible | No/P |
| `:target-type` | 5 | 4 | device identity; target-specific matching/services possible | No/P |

## enuma only

| Property | E | N | Category; possible user/display/service impact | Version alone |
|---|---:|---:|---|---|
| `/arm-io/ufshc:compatible` | 29 | — | storage/hardware; UFS binding can affect root and all userland | No/H |
| `/arm-io/ufshc:name` | 6 | — | storage/hardware; UFS node identity may affect matching | No/H |
| `/arm-io/ufshc:reg` | 16 | — | storage/hardware; UFS registers may affect root and userland | No/H |
| `/chosen:ephemeral-storage` | 4 | — | storage; temporary Data policy may affect services; E u32 LE 1 | No/C |
| `/chosen:text-fixups` | 232 | — | other/boot; configured user-space binary fixups may change affected services; exact execution not established here | No/C |
| `/defaults:sleep-disabled` | 4 | — | CPU/power; suspend policy may indirectly affect uptime/services; E u32 LE 1 | No/C |
| `/defaults:vmm-present` | 4 | — | other/platform; virtual-machine reporting can affect watchdogd and services; E u32 LE 1 | No/C |
| `/product/audio:name` | 6 | — | other/audio; audio subtree may affect audio service, not established for display | Unknown |
| `/product/audio:wireless-splitter` | 4 | — | other/audio; audio capabilities may affect audio services; E u32 LE 1 | Unknown |

UniXNU `docs/zh/devices/evb10.md:52` records another board's watchdogd
dependency on `vmm-present`; it does not prove the same failure here.
`docs/zh/porting/device-tree.md:234` describes `sleep-disabled` as a bring-up
mechanism when suspend is not implemented. Do not remove enuma-specific
settings merely to match nuwa.

## Requested high-risk audit

| Key or family | Result |
|---|---|
| `/chosen/display-scale` | nuwa-only; see table |
| `artwork-scale-factor` | different; see table |
| `vmm-present`, `sleep-disabled` | enuma-only; see table |
| `kern.maxvnodes` | **not different**: both `/defaults:kern.maxvnodes` length 4, flag 0, `00040100` (u32 LE 66560) |
| `ephemeral-storage` | enuma-only; see table |
| `boot-manifest-hash` | nuwa-only; see table |
| `restore-ramdisk`, `secure-boot` | neither literal name occurs in either ADT; this does not establish equivalent semantics or runtime state |
| `memory`/`dram` | differing `darwinboot-memory-size`, `dram-base`, `dram-size` above; `/chosen/memory-map` properties `name` (11 bytes), `PackedRAMDisk` and `TrustCache` (16 bytes each) are byte-identical, flag 0 |

## Priority, not a proposed copy operation

Beyond `display-scale`, the strongest userland-relevant differences for
investigation are `boot-manifest-hash` (mount/service boot identity),
`artwork-scale-factor` (profile/UI), and `vmm-present` (watchdog/service
policy). OS version alone does not explain these: the first and third are
boot configuration, the second differs in both product class and profile.
Do **not** add nuwa boot-manifest-hash to enuma, overwrite enuma's artwork
profile, or alter enuma's existing vmm-present in the next display-scale
candidate. A missing property is not proof of a missing runtime value or a
diagnosed blocker; r34 runtime interpretation and independent verification
remain unverified.

## Three-way inventory: sheng configuration inference only

Source: `UniXNU/UniXNU-sheng` commit `c8f92b208068eeaa4cd2b0f592671f04ee70076e`, retained as a Git object database at `nuwa/UniXNU-nuwa/out/sheng-display-reference/.git`, no checked-out worktree there. Read without checkout using `git -C <path> show HEAD:board.toml`. Its default is iPadOS **27**, not 17. This table instead assumes explicit selection of its 17.7.11 override and merges the pinned UniXNU 21H461 OS profile with the board. `UniXNU/scripts/unixnu/profiles.py:45-57` defines merge order, but the SoC/architecture profiles, DT and packaging overlays also matter. This does not prove any sheng 17 build or runtime state.

Union of both actual ADTs and explicitly configured sheng OS-profile/board ADT properties: E/N are actual `(length, flag)` and `same` tests raw value and flag. S `cfg:length` is an explicitly typed config value (flag 0 in this generator); `?` means **unknown**, not absent. S `=E`, `=N` compares configured bytes with actual bytes, not actual sheng output. Other board/SoC inputs could affect this inference. This is not a complete sheng ADT. Sensitive values and IDs are not printed.

| Property | E length, flag | N length, flag | E=N | S configuration |
|---|---:|---:|---|---|
| `/arm-io/intc:#interrupt-cells` | 4, 0 | 4, 0 | yes | ? |
| `/arm-io/intc:compatible` | 11, 0 | 11, 0 | yes | ? |
| `/arm-io/intc:interrupt-controller` | 0, 0 | 0, 0 | yes | ? |
| `/arm-io/intc:name` | 5, 0 | 5, 0 | yes | ? |
| `/arm-io/intc:phandle` | 4, 0 | 4, 0 | yes | ? |
| `/arm-io/intc:redistributor-stride` | 8, 0 | 8, 0 | no | ? |
| `/arm-io/intc:reg` | 32, 0 | 32, 0 | no | ? |
| `/arm-io/ufshc:compatible` | 29, 0 | — | — | ? |
| `/arm-io/ufshc:name` | 6, 0 | — | — | ? |
| `/arm-io/ufshc:reg` | 16, 0 | — | — | ? |
| `/arm-io:#address-cells` | 4, 0 | 4, 0 | yes | ? |
| `/arm-io:#size-cells` | 4, 0 | 4, 0 | yes | ? |
| `/arm-io:device_type` | 7, 0 | 7, 0 | yes | ? |
| `/arm-io:name` | 7, 0 | 7, 0 | yes | ? |
| `/arm-io:ranges` | 24, 0 | 24, 0 | no | ? |
| `/buttons:button-names` | — | — | — | cfg:19, 0 ≠ known E/N |
| `/buttons:compatible` | — | — | — | cfg:8, 0 ≠ known E/N |
| `/buttons:device_type` | — | — | — | cfg:8, 0 ≠ known E/N |
| `/buttons:home-button-type` | — | — | — | cfg:4, 0 ≠ known E/N |
| `/chosen/manifest-properties:BNCH` | — | 48, 0 | — | ? |
| `/chosen/manifest-properties:name` | 20, 0 | 20, 0 | yes | ? |
| `/chosen/memory-map:PackedRAMDisk` | 16, 0 | 16, 0 | yes | ? |
| `/chosen/memory-map:TrustCache` | 16, 0 | 16, 0 | yes | ? |
| `/chosen/memory-map:name` | 11, 0 | 11, 0 | yes | ? |
| `/chosen:amfi-only-platform-code` | 4, 0 | 4, 0 | yes | cfg:4, 0 =E =N |
| `/chosen:boot-manifest-hash` | — | 48, 0 | — | ? |
| `/chosen:certificate-production-status` | 4, 0 | 4, 0 | yes | cfg:4, 0 =E =N |
| `/chosen:certificate-security-mode` | 4, 0 | 4, 0 | yes | cfg:4, 0 =E =N |
| `/chosen:chip-id` | 4, 0 | 4, 0 | no | ? |
| `/chosen:crypto-hash-method` | 9, 0 | 9, 0 | yes | cfg:9, 0 =E =N |
| `/chosen:darwinboot-memory-size` | 8, 0 | 8, 0 | no | ? |
| `/chosen:display-scale` | — | 4, 0 | — | ? |
| `/chosen:dram-base` | 8, 0 | 8, 0 | no | ? |
| `/chosen:dram-size` | 8, 0 | 8, 0 | no | ? |
| `/chosen:effective-production-status-ap` | 4, 0 | 4, 0 | yes | cfg:4, 0 =E =N |
| `/chosen:effective-security-mode-sep` | 4, 0 | 4, 0 | yes | cfg:4, 0 =E =N |
| `/chosen:ephemeral-storage` | 4, 0 | — | — | ? |
| `/chosen:kernel-ctrr-to-be-enabled` | — | — | — | cfg:4, 0 ≠ known E/N |
| `/chosen:mix-n-match-prevention-status` | — | 4, 0 | — | ? |
| `/chosen:name` | 7, 0 | 7, 0 | yes | ? |
| `/chosen:nvram-bank-count` | 4, 0 | 4, 0 | yes | ? |
| `/chosen:nvram-bank-size` | 4, 0 | 4, 0 | yes | ? |
| `/chosen:nvram-current-bank` | 4, 0 | 4, 0 | yes | ? |
| `/chosen:nvram-proxy-data` | 8192, 0 | 8192, 0 | yes | ? |
| `/chosen:osenvironment` | 5, 0 | 5, 0 | yes | cfg:5, 0 =E =N |
| `/chosen:random-seed` | 256, 0 | 256, 0 | no | ? |
| `/chosen:root-matching` | 171, 0 | 171, 0 | no | ? |
| `/chosen:text-fixups` | 232, 0 | — | — | ? |
| `/chosen:unique-chip-id` | 8, 0 | 8, 0 | no | ? |
| `/cpus/cpu0:compatible` | 15, 0 | 16, 0 | no | ? |
| `/cpus/cpu0:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu0:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu0:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu0:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu0:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu1:compatible` | 15, 0 | 16, 0 | no | ? |
| `/cpus/cpu1:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu1:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu1:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu1:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu1:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu2:compatible` | 15, 0 | 16, 0 | no | ? |
| `/cpus/cpu2:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu2:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu2:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu2:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu2:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu3:compatible` | 15, 0 | 16, 0 | no | ? |
| `/cpus/cpu3:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu3:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu3:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu3:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu3:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu4:compatible` | 15, 0 | 16, 0 | no | ? |
| `/cpus/cpu4:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu4:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu4:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu4:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu4:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu5:compatible` | 15, 0 | 16, 0 | no | ? |
| `/cpus/cpu5:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu5:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu5:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu5:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu5:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu6:compatible` | 15, 0 | 16, 0 | no | ? |
| `/cpus/cpu6:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu6:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu6:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu6:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu6:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu7:compatible` | 15, 0 | 14, 0 | no | ? |
| `/cpus/cpu7:device_type` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu7:name` | 5, 0 | 5, 0 | yes | ? |
| `/cpus/cpu7:reg` | 4, 0 | 4, 0 | yes | ? |
| `/cpus/cpu7:state` | 8, 0 | 8, 0 | yes | ? |
| `/cpus/cpu7:timebase-frequency` | 4, 0 | 4, 0 | yes | ? |
| `/cpus:name` | 5, 0 | 5, 0 | yes | ? |
| `/defaults:kern.maxvnodes` | 4, 0 | 4, 0 | yes | cfg:4, 0 ≠ known E/N |
| `/defaults:name` | 9, 0 | 9, 0 | yes | ? |
| `/defaults:no-effaceable-storage` | — | 4, 0 | — | ? |
| `/defaults:sleep-disabled` | 4, 0 | — | — | cfg:4, 0 =E  |
| `/defaults:vmm-present` | 4, 0 | — | — | cfg:4, 0 =E  |
| `/options:name` | 8, 0 | 8, 0 | yes | ? |
| `/product/audio:name` | 6, 0 | — | — | ? |
| `/product/audio:wireless-splitter` | 4, 0 | — | — | cfg:4, 0 =E  |
| `/product:artwork-device-idiom` | 4, 0 | 6, 0 | no | cfg:4, 0 =E  |
| `/product:artwork-device-subtype` | 4, 0 | 4, 0 | no | cfg:4, 0 =E  |
| `/product:artwork-display-gamut` | 3, 0 | 3, 0 | yes | cfg:5, 0 ≠ known E/N |
| `/product:artwork-scale-factor` | 4, 0 | 4, 0 | no | cfg:4, 0 =E  |
| `/product:compatible-device-fallback` | 8, 0 | 10, 0 | no | cfg:8, 0 =E  |
| `/product:model` | — | — | — | cfg:7, 0 ≠ known E/N |
| `/product:name` | 8, 0 | 8, 0 | yes | ? |
| `/product:product-description` | 38, 0 | 9, 0 | no | cfg:38, 0 =E  |
| `/product:product-id` | 20, 0 | 20, 0 | no | cfg:20, 0 =E  |
| `/product:product-name` | 38, 0 | 9, 0 | no | cfg:38, 0 =E  |
| `/product:thin-bezel` | — | — | — | cfg:4, 0 ≠ known E/N |
| `/psci:compatible` | 13, 0 | 13, 0 | yes | ? |
| `/psci:method` | 4, 0 | 4, 0 | yes | ? |
| `/psci:name` | 5, 0 | 5, 0 | yes | ? |
| `:#address-cells` | 4, 0 | 4, 0 | yes | ? |
| `:#size-cells` | 4, 0 | 4, 0 | yes | ? |
| `:compatible` | 25, 0 | 30, 0 | no | cfg:7, 0 ≠ known E/N |
| `:model` | 8, 0 | 11, 0 | no | cfg:8, 0 =E  |
| `:name` | 12, 0 | 12, 0 | yes | ? |
| `:target-type` | 5, 0 | 4, 0 | no | cfg:5, 0 =E  |

The explicit `:compatible` config is **only a prefix**: the generator appends
hardware-DTS compatible strings (`UniXNU/scripts/unixnu/devicetree.py:381-384`).
Its row is not a predicted complete sheng value.

### Three-way interpretation and limits

* **sheng and nuwa both present, enuma missing:** none is established.
  `display-scale`, `boot-manifest-hash`, `BNCH`, `mix-n-match-prevention-status`
  and `no-effaceable-storage` are present in the actual nuwa ADT and absent
  from enuma, but their final sheng ADT status is unknown. No explicit sheng
  board/OS-profile property is evidence of absence from a final ADT.
* **sheng explicitly configured, enuma actual ADT missing:** the four
  `/buttons` properties listed above (`button-names`, `compatible`,
  `device_type`, `home-button-type`); `/chosen:kernel-ctrr-to-be-enabled=0`;
  `/product:model=J120AP`; `/product:thin-bezel=1`. They are also absent from
  the nuwa *ADT*. Button geometry and thin bezel are board/product choices,
  not proven enuma omissions; CTRR is an early kernel/hardware security policy,
  not a display metadata patch. The product model is a profile/board identity,
  not sufficient reason to copy it. All require separate enuma evidence.
* **Known differing values:** sheng configuration specifies
  `/product:artwork-display-gamut=sRGB` vs actual `P3` in both others;
  `/defaults:kern.maxvnodes=78848` vs actual 66560 in both others. These
  are board/configuration choices even when sheng is hypothetically built with
  the same iPadOS 17 profile; sheng's board comment ties vnode sizing to its
  larger memory and xsmall kernel and its generator's historical comment
  ties sRGB to its display/rendering path (`HEAD:board.toml`,
  `HEAD:scripts/make-sheng-adt.py`). They are not proven universal fixes.
  `/product:artwork-scale-factor` is enuma 2, nuwa 3 and sheng configured 2:
  consistent with donor profile/device class, not proof of an OS-version effect.
  There is **no established property whose three final ADT values are all
  different**, because no sheng final ADT is available.
* `vmm-present=1` and `sleep-disabled=1` are explicit sheng board settings
  matching enuma; nuwa's actual ADT lacks them. `ephemeral-storage=1` is
  present on enuma and absent on nuwa; sheng configuration requests
  `persistent_data=true`, but final ramdisk inputs are not established and
  hence its actual property remains unknown. `secure-boot` has no literal
  property in enuma or nuwa; sheng final state is unknown. All three
  memory/DRAM differences above are hardware or allocated-window choices,
  not values to port. sheng requests `owned_memory_size=0x130000000`.
* The sheng iPadOS-17 override explicitly uses
  `offline-legacy-unit-scale=2` (`HEAD:board.toml:185`);
  `HEAD:package/LegacyDisplayProbe.cpp:455-473` shows a runtime path which
  publishes or matches `display-scale`. That is **not** proof the packaged
  ADT has the property or that enuma's compiled driver implements this path.

### Minimal next-candidate recommendation

Only consider `/chosen/display-scale=2`, pending parent confirmation: it
matches enuma's iPad artwork profile and the sheng 17 *configured runtime*
scale, while the nuwa logo linkage is a parent-transcribed observation.
It may change logical layout; its consumer ABI and real behavior on enuma
remain unverified. Do not also add `thin-bezel`, CTRR, button identities,
boot manifest, or change gamut/vnode policy without an enuma-specific
consumer and evidence. This is a one-property diagnostic, not a claim of
required property pairs.
