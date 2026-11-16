# GOP legacy r5 first device run — device result

## Latest: one GOP r5 boot; no failure criterion hit; the display path is frozen (self-checked record)

2026-11-16. Under a per-round user authorisation exactly one `fastboot boot` of
the sealed GOP legacy production package was issued and it returned 0. The facts
in this document are parent-relayed (execution, timeline, on-screen lines) plus
independent `vision` reads of the screen photographs, as described under
"Evidence sources". They are **not** an independent device re-run by this
repository, and no host tooling here re-read the image.

### Execution and timeline

Serial is deliberately withheld; the device was identified by model, not by
connection order. A second device (nuwa) was present during the round and
received one read-only `getvar product` for identification only; it was not
booted, flashed or otherwise touched.

1. The enuma device was confirmed as the target before booting.
2. Single boot of the already-sealed candidate, no flash, no `continue`, no
   retry:

```
fastboot boot out/enuma-gop-production-20261114-r5/boot.img
```

| Time | Event |
| --- | --- |
| 23:35:20 | single `fastboot boot` issued, returned 0 |

No `STOP:` line, no client timeout, no second boot, no partition write, no
`fastboot continue`, no claim-marker access in this round.

### Candidate identity

| Item | Value |
| --- | --- |
| boot image | `out/enuma-gop-production-20261114-r5/boot.img`, 203505664 B, SHA-256 `fd97c13571b1001f1c6910c2df509da23af82504cddaf94cf659f35bf1bb5600` |
| candidate manifest | `out/enuma-gop-production-20261114-r5/candidate-manifest.json`, 450624 B, SHA-256 `bb2f75967e3dc60a8ebd31a8c8696f5e11407daf3c46e59ed3a304d4d52e5cb1` |
| base pin | `693f5d9cae8a408dd18b39f3f9fdc4228c934241` (not uprevved) |
| display archive | `display/libEnumaGopLegacy.a`, 598792 B, SHA-256 `c88510ae599cd678d2b0f83a98034d61a5e5e167e05295cb9c58085672cbb1b5` |
| prelink | 124665856 B, SHA-256 `4d7eb65c6c57d23ee31caafa7750983c7c28f26f089667a089184c3c70bbdeb8` |
| package status | `self-checked`, `release_allowed=false`, `hardware_tested=false` before this run |

The boot image and manifest hashes are the ones recorded in the sealed package
(`DELIVERY.md:101-109`, rebuilt manifest 2026-11-16). The boot args baked into
the package's `device/board.toml:59` enable the display path
(`offline-mobile-graphics-load=1`, `offline-legacy-register=1`,
`offline-legacy-phase=4`, `offline-legacy-gop=1`, `offline-legacy-pm=1`,
`offline-legacy-validate=1`, `offline-legacy-transfer=1`,
`offline-legacy-cpu-present=1`) alongside `-v`, `serial=3`,
`native-ufs-root=1`, `pmgr=2`, `sheng-pmgr=2`, `sheng-data-persist=2`,
`sheng-log-reserve=1024`, `sheng-vsync=60`.

### Screen lines (verbatim)

The boot ran verbose (`-v`), so kernel `IOLog` output is on the same screen as
the failure log described below. The lines below are the parent's transcription
of the final screen, independently re-read from the photographs by `vision`.

```
virtual bool IOMobileFramebufferLegacy::start(IOService *)
IOMFB: driver commit:
provider was not AppleARMIODDevice.
```

The boot then stopped on rootwait with this line, character for character:

```
Waiting on <dict ID="0"><key>IOProviderClass</key><string ID="1">IOMedia</string><key>IOPropertyMatch</key><dict ID="2"><key>UUID</key><string ID="3">04769D26-2CA0-4825-B443-E2E5F88300F2</string></dict></dict>
```

File and line references below resolve against the frozen package: bare
`EnumaLegacyDisplay.cpp` is
`out/enuma-gop-legacy-20261114-r2/package/EnumaLegacyDisplay.cpp` (SHA-256
`04b8fbfd5d932ed1e78cd6e2ee5bc2a00f933ad0afe671f13bd93cd970fe04a2`, identical
to its `patch-replay/` copy), `display/source/NativeLegacyDisplay.cpp` is the
official core copy the package built against, and `device/board.toml` /
`DELIVERY.md` / `HANDOFF.md` are inside
`out/enuma-gop-production-20261114-r5/`.

The UUID equals `root_match_volume_uuid` in the package's own
`out/enuma-gop-production-20261114-r5/device/board.toml:70`
(`04769D26-2CA0-4825-B443-E2E5F88300F2`) character for character. That is the
UUID the sealed package was built with; the current working-tree `board.toml`
carries a different value, so this match binds the screen to the r5 package, not
to the present repository state, and it says nothing about whether a volume with
that UUID exists on the device.

Other screen facts recorded in the same run:

- `AMFI: queried model name from device tree: iPad7,1`
- `enuma-pmgr: stage=3 ...` and `enuma-pmgr: stage=23 ...`, both with `code=0x0`
- `apfs_root_start` reported `could not retrieve system-volume-auth-blob from device tree`
  followed by `No such file or directory (2)`, consistent with a boot that has no
  root volume

The earlier reads of this UUID that saw `4025` instead of `4825` came from a
downscaled image and are withdrawn; the 1:1 native and 3× enlarged reads agree.

### Failure criteria and verdicts

Four strings would mark a display failure in this candidate. None of them
appears anywhere on the final screen:

| Criterion | What a hit would have looked like | Observed | Verdict |
| --- | --- | --- | --- |
| the consumer's own failure log | any `IOLog` line prefixed `EnumaLegacyDisplay:` | absent | not hit |
| the failure reason text | `refused stage=<n> reason=<m>` | absent | not hit |
| an unqualified backend slot | `EnumaLegacyDisplay: unqualified backend slot <n>` panic | absent | not hit |
| any panic at all | a `panic(...)` banner | absent | not hit |

The first two are the same line: `failure()` at `EnumaLegacyDisplay.cpp:38-41`
sets `enuma_legacy_error` and prints
`IOLog("EnumaLegacyDisplay: refused stage=%u reason=%u\n", ...)`. The third is
the backend guard panic at `EnumaLegacyDisplay.cpp:179-181`, which fires only if
the original family reaches a vtable leaf this backend does not implement. The
specific `failure(13)` exit — `displayObject->probe()` returning something other
than the object, or `displayObject->start(nub)` returning false — would have
produced the first two strings at stage 4 and did not.

`NativeUfs` and `persistent store` text is also absent from the screen. That is
consistent with a boot that never reaches native UFS ownership or a store, but
absence of console text is not by itself a proof about those paths, and this run
did not test them.

### `provider was not AppleARMIODDevice.` is the expected non-IOD branch

The three lines above are not a failure. `IOMobileFramebufferLegacy::start` in
the unchanged original family expects an `AppleARMIODevice` provider; this
candidate attaches the original class to a generic `IOPlatformDevice`
(`EnumaGOPFramebuffer`, `EnumaLegacyDisplay.cpp:84-105`) instead. The backend
source records that same assumption for a neighbouring selector: "The original
slot-188 caller ... assumes an AppleARMIODevice provider. Query our actual
generic provider instead" (`display/source/NativeLegacyDisplay.cpp:810-812`).
So the message is the original `start` reporting the non-IOD provider it was
handed, on the path that this candidate deliberately chose.

The enuma-side evidence that this branch did not abort registration is the stage
machine. `enuma_legacy_stage` is written at `EnumaLegacyDisplay.cpp:48` (1),
`:61` (2), `:69` (3) and `:116` (4); stage 4 is only reached after
`displayObject->probe(nub, &score) == displayObject`,
`displayObject->start(nub)` returning true and `registerService()`
(`:106-117`). Any failure in that block takes `failure(13)` and returns before
stage 4, which would have printed the rejected line above.

**Stage 4 is a static inference, not an observed value.** The candidate keeps
`enuma_legacy_stage` in kernel memory and this build prints nothing on the
success path; the screen was never asked to report it. What the screen directly
establishes is the absence of the failure line; from that plus the stage machine
above, the late probe completed through `registerService()`. Nothing more.

### Why there was no pixel output

`startHardware()` only builds and validates the mapping
(`display/source/NativeLegacyDisplay.cpp:833-860`): it checks the console
geometry, maps `PE_current_console.rowBytes * height` of the provider, verifies
owner/VA/PA/length/geometry through `native_legacy_gop_mapping_observed`, and
installs the boot dimensions. It writes no pixels.

The first write to the framebuffer happens on the transfer path, and that path
is gated on a validated original swap request:
`const OriginalLegacySwapRequest *request=pendingSwapRequest();` and
`if(!request || !isValidated(request)){stat(4);return;}`
(`display/source/NativeLegacyDisplay.cpp:557-558`). Every
`native_legacy_prepare_scanout()` call — the only place that releases the text
console through `initialize_screen(nullptr, kPEReleaseScreen)` and checks the
real `disableConsoleOutput` (`EnumaLegacyDisplay.cpp:150-160`) — sits behind
that gate (`:578`, `:612`, `:640`, `:658`).

No swap request was made in this boot: no render server existed, because no root
volume existed. Therefore the console was never released, `prepare_scanout` was
never called, and no pixels were produced — the whole screen is the text console.
This is a mechanism statement about this candidate, not a defect found in it.

### Evidence sources

Two sources agree on the screen lines: the parent's transcription and two
independent `vision` reads of the same region (1:1 native and 3× enlarged).
Agreement between a transcription and its own re-transcription is weaker than a
second independent reading, so only the `vision` reads are independent; nothing
in this repository re-read the images.

- No video was recorded for this run.
- Photo original: 490549 B SHA-256
  `5babaaadf5155d0eb2939ebfa7512c434915bd476b8df9673dd6603e655ae575`,
  2000×1500.
- Crop read by `vision`: 169798 B SHA-256
  `8a168529bcf091d759e0fe7927bff31428705a14e2d9f21ffc88bc3eece58b8a`,
  1400×578.
- Native two-line crop: 151721 B SHA-256
  `25f09881eb6092e8463d062eb7f9da913228554d571aaa6fc1b70282fe294b45`,
  2000×49.
- 3× enlarged crop: 331516 B SHA-256
  `3b36a079b2a617d182c9090fe7e3927b53c2570454289bc0fbd5efc1f42bfaeb`,
  1140×138.
- All images exist only in a host temporary directory; they are not in Git and
  are not uploaded anywhere. This document carries hashes and conclusions only.

### Freeze decision

A `deep_reviewer` direction on 2026-11-16 (user-named) froze this line:

- The GOP package stays exactly as sealed in
  `out/enuma-gop-production-20261114-r5/` and is **immediately frozen**: no
  further builds, no deployment, no new device round on this line.
- The display code does **not** enter the tracked default recipe or
  `patches/xnu/series`. It remains reachable only through the package's
  `offline-legacy-*` boot args.
- Pixel-output validation waits until the UFS root volume and userland exist.

Reasons, in the order they bound the decision:

1. **Without a render server there is no swap.** The official alioth record
   states the ordering directly: "Get backboardd to start before investigating
   frame submission: with no render server there is no client that could call
   Swap." (`UniXNU/docs/zh/devices/alioth.md:338`). The swap gate in this
   candidate's own transfer path is the same rule
   (`NativeLegacyDisplay.cpp:557-558`). First-pixel validation therefore cannot
   be produced by any amount of further display-side work; it needs a root
   volume and a userland client first.
2. **One isolated problem per round.** This round isolated display
   registration and it is answered: the late path was reached, registration
   completed, no failure line fired. Adding UFS root bring-up to the same image
   would confound the attribution of any next failure.
3. **Cost of merging into the default build.** The consumer needs the frozen
   archive plus two rebuilt objects, and it is only active under
   `offline-legacy-*` boot args. Merging it into the default recipe would put an
   unverified display path into every image while the acceptance-blocking line is
   the UFS root volume, and would keep a non-default configuration in the tree
   with no way to validate it until userland exists.

Freezing also means the sealed manifest is untouched: the five target artifacts
and the 429-entry `candidate-manifest.json` listed above are unchanged by this
round, and no tracked configuration, recipe or series was modified.

### Not established

- Any actual pixel output, first frame, or swap. None was requested and none
  occurred.
- That `enuma_legacy_stage` held 4 while running — it is a static inference from
  the missing failure line, as stated above.
- That the registered display service became visible to, or usable by, any
  userland client. There was no userland.
- Anything about the swap, copy, retire or vsync paths: `offline-legacy-transfer=1`
  was set but never exercised.
- Persistent root volume, Data volume or any persistent store.
- SMMU ownership, vendor DMA retirement, or any UFS admission step.
- Any formal bring-up stage promotion; the stage record is unchanged and
  `hardware_tested` stays false for the package.
- That a repeat boot would behave the same; this was a single run with no retry.
- Default NoAccessPolicy / NoContract: unchanged.

### Reproduction conditions

- Host side: the sealed package can be re-checked read-only with
  `audit.py --verify` under WSL root and Python 3.11, with
  `https_proxy=http://172.17.144.1:7890` for the `git ls-remote` inside
  `audit.py`; command sequence and limitations are in that directory's
  `DELIVERY.md` and `HANDOFF.md`. A full rebuild needs a new output directory;
  the frozen directory is not to be rebuilt in place.
- Device side: one enuma, confirmed as the target before booting, a new
  per-round user authorisation for a single `fastboot boot`, and no flash or
  `continue`. Serial stays out of the record.
- Without a new authorisation there is no reproduction path; this document does
  not grant one, and the freeze above means none is planned on this line.
