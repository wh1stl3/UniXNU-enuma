# SM8250 native UFS root — first root volume mount, device result

## Latest: one `userdata` write plus one mode 0 boot; OS root volume mounted, SystemOS not mounted, launchd failed (self-checked record)

2026-11-18. Two device actions were authorized and issued in this round: one
`fastboot flash userdata` of a prepared root image, and one `fastboot boot` of the
`ufs-sm8250-startroot-mode0-20261118-r2` candidate afterwards. Both returned 0.

Everything below is parent-relayed: execution, timings, claim state and the final
screen are the parent's transcription, **not** an independent device re-run by
this repository. The screen was **not** independently re-read by `vision` — that
channel was unavailable this round — and no video or still from the run is in Git
or anywhere else. This record was built without building, packaging, touching the
device or modifying `out/`.

### Execution and timeline

Serial is deliberately withheld; the device was identified by model. A second
device (nuwa) did not appear in any list this round and received no command.

| Time (+08:00) | Event |
| --- | --- |
| 22:37:23 → 22:37:27 | `fastboot boot boot_enuma.img` (TWRP) sent and returned 0 |
| 22:37:27 → (gates) | TWRP environment gates run; **stopped at the device-mapper gate**, nothing written |
| (untimed) | two raw `fastboot flash userdata` attempts fail in the client, no transfer started |
| 22:42:45 | claim marker `.cache/ufs-userdata-sparse-flash-20261118.claimed` atomically created |
| 22:42:50 → 22:46:41 | `fastboot flash userdata <sparse>` — 12/12 segments `OKAY`, `Finished`, exit 0, 230.396 s |
| 22:46:54 | one `fastboot boot out/ufs-sm8250-startroot-mode0-20261118-r2/boot.img`, exit 0 |

No `STOP:` line, no client timeout, no retry, no `fastboot continue`, and no
second boot of either image. The three intervals are wall-clock from the host, not
device-side timing.

Boot arguments carried in the payload: `-v serial=3 rd=md0-ramblock pmgr=2
native-ufs-root=1 sheng-pmgr=2`. No `sheng-data-persist` (store mode 0), no
`native-ufs-probe`, no initrd — the same argument set as the 2026-11-18 r1 run.

### What was written, and what was not

Written: `userdata` only.

| Item | Value |
| --- | --- |
| command | `fastboot flash userdata <sparse>` (partition name resolved from the LUN 0 GPT) |
| sparse container | 8,811,031,268 B, SHA-256 `ee3bb0eb6f4a8ff2a7807d2549585c9590bde3e04d069505612911a65f7095ae` |
| expanded image | 9,382,658,048 B, content SHA-256 `fd43ee7035ce185ce4215ac93fdc006fd784a54b3b7442e21457c226cbe03093` |
| transport | 12/12 segments `OKAY`, `Finished`, exit 0, 230.396 s |
| host read-back | **none** — the device was not read back this round |

The content hash and size match the image's own receipt,
`out/userdata-prepare-20261112-b/run-1/userdata/userdata-root.json`
(`image_bytes` 9382658048, `image_sha256` `fd43ee70…cbe03093`, `windows`: `OS`
offset 1,048,576 size 6,077,580,800, `SystemOS` offset 6,079,643,648 size
3,303,014,400). The sparse container itself was a host-side temporary artifact and
is not retained.

Boundary facts:

- The write starts at the partition's offset 0 and its extent is the image. Against
  the recorded partition size of 242,455,916,544 B, the untouched remainder is
  233,073,258,496 B — so **the tail of `userdata` was outside this write**, which
  is also where a mode 2 store window would live.
- Only `userdata` was addressed. No other partition, and no `boot`/`vendor_boot`
  slot, was written or read; this round was `fastboot boot`, which does not write a
  slot.
- Because there was no read-back, what is on the device is evidenced only
  indirectly, by the next boot's behaviour (see "Field interpretation": the
  published SystemOS container size equals the image's SystemOS window exactly).
- The overwritten range is Android's `/data`. D7 already records that the user
  confirmed that data is disposable; that decision is a precondition for a write,
  not an authorization for one, and this round's write was separately authorized.

### TWRP attempt, and the device-mapper gate that stopped it

Before the `fastboot flash` path, an in-recovery write was attempted so the target
block device could be checked directly.

- Image: `boot_enuma.img`, 134,217,728 B, SHA-256
  `69a4dd4379c1834fb51524cf2cf0587a3ba93aa1ca1771dd5903dfc2b82ff0e0`, TWRP
  `3.7.1_12-15.0`; `ro.twrp.device.name` = `enuma`.
- `fastboot boot` of it returned 0 and TWRP came up; `adb` reported the target in
  state `recovery` and `adbd` already running as root.
- Gates that passed: identity (`ro.twrp.device.name`, `ro.product.device` =
  `enuma`), `by-name/userdata` → the expected LUN 0 partition node,
  `blockdev --getsize64` = 242,455,916,544 B on both paths, `/dev` on tmpfs with
  ~3.6 GiB free, and the `/data`/`/sdcard` mounts cleared by `umount`
  (rc 0, no matching entry left in `/proc/mounts`).
- Gate that failed: a device-mapper device named `userdata` (`dm-7`) lists the
  `userdata` block node as its direct `slave` and remains as a holder of that node
  **after** unmounting. The image ships no `dmsetup`/`dmctl`, and the mapping's
  table is not readable, so the mapping could not be removed from inside TWRP.
- Outcome: hard gate reached → **stop, no forced `dd`, no retry, no claim, no
  write, no read-back, no reboot**. The device was left in TWRP with `/data` and
  `/sdcard` unmounted and the disk unchanged.

Evidence: `.cache/ufs-userdata-twrp-write-20261118/STOPPED-gate1-dm-mapping.log`
(4,181 B, ignored, not tracked). The log's own `NOT DONE` block records that this
attempt wrote nothing.

### The two raw `fastboot flash` attempts

Between the TWRP stop and the sparse write, `fastboot flash userdata` of the
expanded image was tried twice, including with `-S 64M` sparsing. Both failed in
the **client** after 1.8 s with `std::bad_alloc`, and neither printed a `Sending`
line. **No transfer ever started**, so `userdata` was not affected by either
attempt. Only after that did the host sparsed the image and the third attempt
succeeded.

### Candidate identity

Values are from the candidate directory as built; nothing was rebuilt or re-sealed
for this record, and the `boot.img` hash was re-read on this host.

| Item | Value |
| --- | --- |
| boot image | `out/ufs-sm8250-startroot-mode0-20261118-r2/boot.img`, 169,951,232 B, SHA-256 `7819c2ab18e9325ca984f5e89bac88720ea7a6cb8454a2c1fe214a670ff4ee66` |
| payload | `payload.img`, 167,772,160 B, SHA-256 `f667c2c94640a8fa1ca4951c2e5105a9069342b2fde91d63fea64fa7e38af872` |
| kernel (inherited from r1, not rebuilt) | `prelink.macho`, 124,596,224 B, SHA-256 `21f326137359240259b6b4c238238082942d01f5d5fa37837d45adcedb74a73f` |
| base pin | `693f5d9cae8a408dd18b39f3f9fdc4228c934241` |

r2 differs from r1 in exactly one packaging input: `[payload.adt]
root_match_volume_uuid`, `9071148B-B025-402D-AD7A-48464D8B5FFF` →
`04769D26-2CA0-4825-B443-E2E5F88300F2` (the signed OS policy's volume UUID). That
is the only ADT difference apart from the per-build `random-seed`. The image is
31,375,360 B under the `boot_a`/`boot_b` capacity; the slot was not exercised.

### Final screen (verbatim, not independently re-read)

Transcribed by the parent from the last screen. `…` marks a transcription cut, not
literal output. The prompt line the run stopped at (`Waiting on …`) leads the
frame, which is the second of two frames covering the same boot.

```
Waiting on <dict ID="0">…<key>UUID</key><string ID="3">04769D26-2CA0-4825-B443-E2E5F…
NativeUfs: warm bring-up ready (dma=0xc8e0b000 len=0x22000 contig=0x22000 owned=0xc007c000+0x20000000 usable=0xc8700000 check=PASS old_utrl=0x99ff3000 old_utmrl=0x99ff4000 excl=4
NativeUfs: published SystemOS
dev_init:306: disk0 device_handle block size 4096 block count 806400 features 0 internal
nx_mount:1617: disk0 checkpoint search: largest xid 14, best xid 14 @ 9
apfs_extract_root_hash_arm:13275: could not retrieve system-volume-auth-blob from device tree
import_iboot_forwarded_roothash:3496: apfs_extract_root_hash_and_manifest failed with error: No such file or directory (2)
NativeUfs: SystemOS volume 8846FE78-2910-4297-AF97-D59BB6F8FC16 ready
NativeUfs: published OS
dev_init:306: disk3 device_handle block size 4096 block count 1483776 features 0 internal
nx_mount:1617: disk3 checkpoint search: largest xid 410, best xid 410 @ 3
apfs_vfsop_mount:2714: disk3s1 mount volume DawnUpdate21H461.J120J121J207J208OS …
handle_mount:817: disk3s1 vol-uuid: 04769D26-2CA0-4825-B443-E2E5F88300F2 block size: 4096 block count: 1483776 (unencrypted…)
apfs_log_wp_proc:3091: disk3s1 mount-complete volume DawnUpdate…
NativeUfs: OS volume 04769D26-2CA0-4825-B443-E2E5F88300F2 ready
Load_init_program: attempting to load /usr/appleInternal/sbin/launchd.development
libignition!: failed to lookup preboot: 2
preadboot: failed to get preboot device: 2
libignition!: ignition failed: 2
Launchd(1) exited -- exit reason namespace 6 subcode 0x1 description: Library not loaded: /usr/lib/libSystem.B.dylib
panic(cpu 0 caller …): Intriguing: failed to start -- … /usr/lib/libSystem.B.dylib
```

### Field interpretation

- `NativeUfs: warm bring-up ready (…)` — same success terminal as the r1 run, with
  `native-ufs-root=1` in effect. `dma=0xc8e0b000` differs from r1's `0xc8a10000` and
  the 2026-11-17 probe's `0xc8e10000` because the base is allocated, not fixed;
  `owned=0xc007c000+0x20000000` and `usable=0xc8700000` are unchanged, and
  `dma_end=0xc8e32000 ≤ owned_end=0xe007c000` and `usable ≤ dma` both hold.
  `excl=4` and the predecessor queue bases are unchanged.
- `NativeUfs: published SystemOS` / `NativeUfs: published OS` — **both** windows
  were published. The 2026-11-18 r1 run rejected at the manifest gate and never
  reached this point, so this is the first run of the series that publishes a
  window at all.
- `disk0 … block count 806400` = 3,303,014,400 B, which is exactly the `SystemOS`
  window size in the flashed image's receipt — the published SystemOS window is the
  one this round wrote.
- `disk3 … block count 1483776` = 6,077,556,736 B, not exceeding the `OS` window's
  6,077,580,800 B; the APFS container is smaller than the window it lives in.
- `nx_mount:1617: disk0/disk3 checkpoint search` — both APFS containers were
  recognised and their checkpoints located (`xid 14` for SystemOS, `xid 410` for
  OS). This is a container-level step, not a mount.
- `apfs_extract_root_hash_arm:13275: could not retrieve system-volume-auth-blob
  from device tree` + `import_iboot_forwarded_roothash:3496: … failed with error:
  No such file or directory (2)` — the root-hash import looked for
  `system-volume-auth-blob` in the **device tree** and found no such property. This
  is a missing boot-input, not a property of the written `userdata`: nothing in the
  flashed image supplies this DT node. The same pair was already reported by the
  2026-11-16 GOP r5 run (`docs/enuma-gop-r5-device-observation.md:94-96`), where it
  was read as consistent with a boot that has no root volume; here a root volume
  does mount, so that earlier reading does not generalise and the input's real
  source remains untraced.
- `NativeUfs: SystemOS volume 8846FE78-2910-4297-AF97-D59BB6F8FC16 ready` /
  `NativeUfs: OS volume 04769D26-… ready` — the driver's own "this window is
  usable" report. It is **not** a mount (see "SystemOS is not mounted").
- `apfs_vfsop_mount:2714 … disk3s1 mount volume DawnUpdate21H461.J120J121J207J208OS`
  → `handle_mount:817: disk3s1 vol-uuid: 04769D26-2CA0-4825-B443-E2E5F88300F2` →
  `apfs_log_wp_proc:3091: disk3s1 mount-complete` — an actual APFS volume mount of
  `disk3s1`, with the volume UUID the boot was waiting on. This is the first
  observed root-volume mount on this board over the native UFS path.
- `Load_init_program: attempting to load /usr/appleInternal/sbin/launchd.development`
  — the boot got as far as trying to load PID 1. That is further than any earlier
  run of this series.
- `libignition!: failed to lookup preboot: 2` → `preadboot: failed to get preboot
  device: 2` → `libignition!: ignition failed: 2` — the ignition chain could not
  find a preboot device; `2` is the ENOENT errno value.
- `Launchd(1) exited -- exit reason namespace 6 subcode 0x1 description: Library
  not loaded: /usr/lib/libSystem.B.dylib` then `panic(…): Intriguing: failed to
  start -- … /usr/lib/libSystem.B.dylib` — launchd started and immediately died
  because `libSystem.B.dylib` could not be loaded, and PID 1's failure panics the
  kernel. The final screen is therefore a launchd-start failure, not a root-mount
  failure.

### The volume UUID: user-confirmed on screen, not image-verified

`handle_mount:817` reports
`vol-uuid: 04769D26-2CA0-4825-B443-E2E5F88300F2`. The user magnified that line on
the screen and confirmed the third group is **`4825`**, i.e. the full value is
identical character for character to the signed OS policy UUID
(`out/verify-fresh-20261113/os/result.json`; `scripts/enuma-production-recipe.py:17`)
and to the r2 `root_match_volume_uuid`.

Independent confirmation status:

- **Not** independently re-read by `vision` — that channel was unavailable.
- One earlier cropped-image read reported the third group as `8443`. That read is
  **withdrawn**; the user's magnified read of the screen is the authority here.
- So: user-confirmed by eye, missing an independent image read. This is a
  transcription-grade confirmation, one step below the two-source agreement that
  the 2026-11-16/17 records achieved, and it is recorded as such.

### Criteria and verdict

Judged against the criteria fixed before the boot. The OS-root-mount criterion is
**conditionally met**; the stage-6 criteria as a whole are **not** met.

| Criterion | Observed | Verdict |
| --- | --- | --- |
| `NativeUfs` publishes the SystemOS window | `NativeUfs: published SystemOS` | hit |
| `NativeUfs` publishes the OS window | `NativeUfs: published OS` | hit |
| SystemOS container recognised | `disk0 … block count 806400`, checkpoint `xid 14` | hit |
| **SystemOS volume mounted** | no `disk0s1 mount volume` / `mount-complete` line | **not hit** |
| OS container recognised | `disk3 … block count 1483776`, checkpoint `xid 410` | hit |
| OS volume mounted | `disk3s1 mount volume` + `mount-complete` | hit |
| mounted UUID equals the signed OS policy UUID | `04769D26-2CA0-4825-B443-E2E5F88300F2` (user-confirmed) | hit (see UUID section) |
| preboot device available | `failed to lookup preboot: 2`, `failed to get preboot device: 2` | **not hit** |
| `system-volume-auth-blob` obtained | `could not retrieve … from device tree`, ENOENT | **not hit** |
| **launchd starts** | `Launchd(1) exited … Library not loaded: /usr/lib/libSystem.B.dylib`, then panic | **not hit** |
| no unintended panic | panic present, but it is the direct consequence of PID 1 dying | hit as a consequence, not as a defect in the root path |
| **bring-up stage 6 as a whole** | mount ok, launchd not started | **not passed** |

The official stage-6 criterion set includes "the configured volume mounts and
launchd starts" (`porting.toml` storage `completion`). The mount half is now
evidenced; the launchd half is not, so the stage record stays where it was
(stages 1–2 formally accepted, later single observations not promoted).

### SystemOS is not mounted, and what preboot / the auth blob need

- **No SystemOS mount evidence.** `NativeUfs: SystemOS volume … ready` is the
  driver's window report; the mount lines exist only for `disk3s1`. There is no
  `disk0s1 …mount volume` and no `mount-complete` for `disk0`, and no
  `handle_mount` line for it. The SystemOS APFS container was located
  (`checkpoint search`) but nothing in its tree was mounted.
- **`system-volume-auth-blob` is a device-tree input that is absent.** The lookup
  that fails is against `/chosen`-style device tree content, so no `userdata`
  layout change can supply it; a future run needs a DT node (or the component that
  would create it) carrying the blob. Where that node comes from has **not** been
  traced.
- **preboot is not resolvable, and `0x18` is unconfirmed.** The reviewer reads the
  `0x18` selector used on this path as the standard `VM|PREBOOT` constant; the
  semantics of the private function it is passed to were **not** confirmed, and the
  container lookup for it returned ENOENT. Treat "preboot is missing" as observed
  behaviour of the lookup, not as a diagnosis of where preboot should live.
- **Do not hand-supply `libSystem.B.dylib`.** Adding the missing dylib by hand
  would mask the preboot/ignition failure that produced the ENOENT and would make
  the next run's evidence unattributable. The reviewer's position, and this
  record's, is that the single highest-priority next item is to make
  SystemOS/cryptex actually mount and to trace where `system-volume-auth-blob` must
  come from — not to patch around the launchd error.

### Established

- The authorized write happened as intended: 12/12 segments `OKAY`, `Finished`,
  exit 0, `userdata` only, no host read-back, and the two earlier raw-image
  attempts transferred nothing.
- On the next boot the warm takeover reached `gHost.ready` again
  (`dma=0xc8e0b000`, `check=PASS`, `excl=4`), this time continuing past the
  manifest gate instead of stopping there.
- **Both** `SystemOS` and `OS` windows were published by `NativeUfs`, and both APFS
  containers were recognised with their checkpoints located.
- **The `OS` volume `disk3s1` mounted over the native UFS path**, with
  `vol-uuid: 04769D26-2CA0-4825-B443-E2E5F88300F2` — matching the signed OS policy
  UUID and the r2 `root_match_volume_uuid` — reached by aligning that UUID in r2.
  The alignment correction recorded on 2026-11-18 therefore did what it was meant
  to do.
- The boot proceeded to `Load_init_program` and attempted to load
  `/usr/appleInternal/sbin/launchd.development`.

### Not established

- **Bring-up stage 6**: launchd did not start, so the stage criterion is not met.
- **SystemOS mounted / cryptex started**: no mount evidence for `disk0`.
- The source and correct value of `system-volume-auth-blob`, or that supplying it
  would fix the root-hash import.
- Why launchd could not load `libSystem.B.dylib` beyond the observed preboot
  ENOENT — the causal link between the two is the reviewer's reading, and this run
  does not prove it.
- **Persistence**: the payload was booted from the host; nothing was written to a
  boot slot this round, and no cold boot was attempted. The root volume now mounts,
  which is a prerequisite for persistence, not evidence of it.
- Any write capability, Data volume, persistent store or store window; store mode
  stayed 0 and the tail of `userdata` was not written.
- That the **backup** GPT is valid — only the primary table's values were consumed.
- Long-term DMA ownership across `ExitBootServices` and `UfsDxe` retirement
  completeness (2026-11-14 accepted residual risk unchanged).
- Repeatability: one write and one boot, no retry, no second observation.
- What is actually on the device: no host read-back of `userdata` was performed.
- Any formal stage promotion; the stage record is unchanged. mode 1 and mode 2
  remain unreleased, and default NoAccessPolicy/NoContract is unchanged.

### Next single highest priority

Make `SystemOS`/cryptex actually mount, and trace where `system-volume-auth-blob`
must come from. Everything downstream of launchd depends on the volumes that
`ignition` is failing to find; the root-mount half of stage 6 is now evidenced, so
that is no longer the open question. Adding `libSystem.B.dylib` by hand is
explicitly rejected as a next step. Reviewer recommendation: escalate this to a
deep review before any further device round.

### Evidence limits

- **Not independently reviewed**: neither the candidate (r2 packaging) nor this
  observation record has an independent reviewer or verifier rerun; one reviewer
  read of the transcription was provided by the parent, via a non-Gemini channel.
- **One transcription, no independent image read**: the screen was transcribed by
  the parent, and the UUID's third group was confirmed by the user magnifying the
  screen. There was no `vision` re-read of any image, no video and no still in Git.
  For absence criteria a transcription is weaker than a video, and no still can be
  produced afterwards.
- The write's transport result (12/12, `Finished`, exit 0, 230.396 s) is the
  client's report. With no read-back, "written" means "the client reported success
  and the next boot behaved consistently with it".
- Claim marker size and creation time are from the parent's transcription.

### Claim state

| Marker | State |
| --- | --- |
| `.cache/ufs-userdata-sparse-flash-20261118.claimed` | created 22:42:45 (before the write), **consumed** — retained, must not be opened, deleted or replayed |
| `.cache/ufs-userdata-root-write-20261118.claimed` | earlier polluted attempt, untouched — must not be reused, deleted or replayed |
| `.cache/ufs-userdata-root-write-20261118-retry1.claimed` | earlier polluted attempt, untouched — must not be reused, deleted or replayed |
| `.cache/ufs-userdata-root-write-20261118-retry2-sparse.claimed` | **never created** |
| `.cache/ufs-sm8250-startroot-mode0-probe-device-attempt.claimed` | 2026-11-18 r1 round, consumed — must not be replayed |

The TWRP attempt created no claim, by its own log.

### Reproduction conditions

- Host side: the r2 candidate directory can be re-checked with the commands in
  `out/ufs-sm8250-startroot-mode0-20261118-r2/CHECKPOINT.md` §5. Rebuilding rewrites
  `payload.img`/`boot.img` and the ADT carries a 256 B `random-seed`, so **the
  hashes above are not reproducible** — only the current directory's bytes match
  them. The sparse container was a temporary artifact and no longer exists.
- Device side: one enuma identified by model, a new per-round authorization for
  each write and each boot, and a new round name. Every claim listed above is
  consumed or reserved, so this round cannot be replayed.
- Without a new authorization there is no reproduction path; this document does
  not grant one.
