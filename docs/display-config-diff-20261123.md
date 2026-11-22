# enuma r34 vs nuwa resume display-scale: host-only configuration comparison

Status: self-checked; no build, device access, or ADT change. This record is
the requested comparison instead of `enuma-r35-scale-host-20261123.md`; r35
does not exist as a result of this work.

## Inputs and method

* enuma r34: `out/ufs-sm8250-launchd-ipc-20261123-r34/payload.img`,
  member `EFI/UniXNU/Payloads/kernel.macho.adt`, SHA-256
  `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5`.
* nuwa: `nuwa/worktree-display-dsp/out/nuwa-resume-display-scale-audit-20261122/actual-vendor-ramdisk.img`,
  same member, SHA-256
  `ae717c64726d95b0edddf6a3316edc897f2e8a61ca9d3c9c29db2e72f649ec2d`,
  matching `nuwa-resume-display-scale-20261122.md:24-27`.
* The source of the logo and disappearance of the FBSDisplayMode crash is the
  parent's transcription, not an independent device observation:
  `nuwa/worktree-display-dsp/docs/nuwa-logo-milestone-20261122.md:3-7`.
  The original consumer diagnosis is also parent-reported
  (`nuwa-resume-display-scale-20261122.md:3-8,15-19`).
* Complete property inventories are `enuma-adt-properties-20261123.txt`
  (114 properties) and `nuwa-adt-properties-20261123.txt` (110). Each lists
  the path, property name, byte length and high flag bit; lengths rather than
  raw values prevent device identifiers and random seeds entering Git. Display
  values are printed below. `/` is the ADT root, not a missing node name.
* From the device repository on WSL with Python 3.11 and mtools:

  ```
  /home/wh1stl3/.local/bin/python3 -B scripts/compare-display-config-20261123.py
  ```

  The script reads both FAT members using `mtype`, checks node/property bounds,
  rejects duplicates, writes the inventories, and compares raw property bytes
  and flag. It also reads each FAT's `unixnu.toml` xnu args. Results:

  ```
  enuma sha256 5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5 properties 114
  nuwa sha256 ae717c64726d95b0edddf6a3316edc897f2e8a61ca9d3c9c29db2e72f649ec2d properties 110
  ```

  Earlier, `mtype -i out/ufs-sm8250-launchd-ipc-20261123-r34/payload.img
  ::/EFI/UniXNU/Payloads/kernel.macho.adt | sha256sum` gave the same enuma
  digest as the r34 standalone `kernel.macho.adt`.

## ADT display-family comparison

Filtering checks the full node path and property name against display, panel,
screen, refresh, vsync, scale, rotation, color/colour, gamma, backlight,
brightness, frame-buffer/framebuffer, backboard, iop, gpu, dp, dsi and dpu.
This is a **name-based** inventory, not proof that differently named properties
or runtime-created registry nodes have no display role. LE means little-endian.

| Category | Path and property | enuma | nuwa |
| --- | --- | --- | --- |
| nuwa only | `/chosen:display-scale` | absent | `03000000`, 4 bytes, flag 0 (u32 LE 3) |
| different | `/product:artwork-scale-factor` | `02000000`, 4 bytes, flag 0 (u32 LE 2) | `03000000`, 4 bytes, flag 0 (u32 LE 3) |
| enuma only | none | — | — |
| identical | `/product:artwork-display-gamut` | `503300`, 3 bytes, flag 0 (`P3\0`) | same |

The generation side has no literal `display-scale`/`display_scale` in enuma
`board.toml` or pinned `UniXNU/scripts/unixnu/devicetree.py`. The generator
accepts generic typed chosen properties at `devicetree.py:300,335`; the
board's only explicit ADT table is `board.toml:106` (`defaults.u32`). The
donor profiles set the differing artwork values:
`UniXNU/profiles/os/ipados-17.7.11-21H461/profile.toml:85` and
`UniXNU/profiles/os/ios-16.7.16-20H392/profile.toml:88`.

## Boot arguments

The display-name filter additionally includes `boot-progress`, because nuwa's
console implementation documents it. Lists compare explicit arguments, not
their effective compiled defaults.

| Category | enuma | nuwa |
| --- | --- | --- |
| nuwa only | absent | `boot-progress=2`, `boot-progress-scale=3` |
| different | none | none |
| enuma only | `sheng-vsync=60` | absent |
| identical | `offline-mobile-graphics-load=1`, `offline-legacy-register=1`, `offline-legacy-phase=4`, `offline-legacy-gop=1`, `offline-legacy-pm=1`, `offline-legacy-validate=1`, `offline-legacy-transfer=1`, `offline-legacy-cpu-present=1` | same |

Other arguments can indirectly affect display without matching these names;
for example nuwa has `nuwa-mg-reset=1`. This comparison neither establishes
its enuma equivalent nor recommends copying it.

## Interpretation and proposed candidate, awaiting parent confirmation

| nuwa-only item | Role and SpringBoard relevance | Same candidate? |
| --- | --- | --- |
| `/chosen/display-scale=3` | UniXNU `docs/zh/guide/mobilegestalt.md:32` describes this as the scale read by MobileGestalt; its effect on enuma's FBSDisplayMode is not established. Parent-transcribed nuwa evidence makes it a plausible probe. | Yes, as the **only** added property, but recommend testing **2**, matching enuma's existing donor artwork scale, rather than copying the different iPhone donor's 3. This matching is a hypothesis, not an established pairing contract; 3 remains the original proposed alternative. |
| `boot-progress=2` | nuwa-specific early boot progress display selection; the exact enuma implementation/effect is unestablished. No evidence it supplies SpringBoard's display mode. | No; avoid introducing a separate code path. |
| `boot-progress-scale=3` | nuwa `package/boot-progress-r12/SOURCE-r12.md:22` describes console display scaling, not MobileGestalt. No evidence of an FBSDisplayMode dependency. | No; not a required pair with ADT display-scale. |

`artwork-scale-factor` is already present, not a missing property. UniXNU
`docs/zh/guide/mobilegestalt.md:22` calls it artwork scaling; no evidence
requires changing its iPad profile value to 3. `sheng-vsync` is enuma-only;
UniXNU `docs/zh/porting/display.md:45` describes selecting refresh policy
from the actual panel, so do not remove it to imitate nuwa.

If the parent authorizes a candidate, generate a fresh ADT using r22's
generator path and r34 inputs, preserve the old random-seed to keep the
property delta isolated, and compare every payload member and boot prefix;
do not recompile the kernel. Neither the numeric scale nor any pairing is
validated for enuma. nuwa uses iOS 16 `20H392`, enuma iPadOS 17.7.11
`21H461`; do not assume identical consumer ABI or behavior.

| Future observation | Interpretation |
| --- | --- |
| SpringBoard registers `AXSpringBoardServer` | Positive evidence of progress, not full UI or persistence. |
| `enuma-fb` refresh/kick/scanout/swap becomes nonzero | Evidence of the corresponding instrumented path, not by itself a visible usable desktop. |
| Both remain absent/zero | No demonstrated progress at those points; cause remains open. |

Independent verifier, runtime behavior, pixel output and persistent interactive
boot remain unverified.
