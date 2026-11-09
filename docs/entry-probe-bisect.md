# Entry-probe bisect images (stage 5)

Binary search for "how far the kernel gets" after the stage-5 entry probe (green → blue →
magenta bars, then the MMU-on reset) confirmed the XNU entry and the MMU enable. Each image
below places the PSCI reset after the Nth `bl <symbol>` in a chosen function, so a reset back
into fastboot means the kernel reached **and returned from** that call; no reset means it
stopped before, or inside, that call.

## Probe semantics (`scripts/patch-xnu-entry-probe.py`)

- `entry_probe_reset_delay = 6` is required: it both triggers the probe and sets the 6 s wait.
- With `entry_probe_reset_after = "<symbol>"` (plus `entry_probe_reset_in`/`entry_probe_reset_occurrence`),
  stage 3 (the MMU-on reset) is replaced by stage 4: at the Nth `bl <symbol>` in
  `entry_probe_reset_in` (default `_arm_init`), the branch is redirected to a cave that re-executes
  `bl <symbol>`, then waits `entry_probe_reset_delay` (6 s) **after the call returns**, then issues
  PSCI `SYSTEM_RESET` (`smc #0`, `w0=0x84000009`). The reset is therefore after the call returns,
  not immediately, and still waits the full delay.
- Stage 1 (blue bar) and stage 2 (magenta bar) are always installed; the panic screen is omitted
  (its code is 2607 B, exceeding this kernel's `__text` padding 2512 B by 95 B).
- Every checkpoint below is inside `_arm_init`/`_kernel_bootstrap`, which run after the MMU is
  enabled, so the PSCI reset returns to fastboot (verified in the stage-5 run, bootreason=bootloader).

## Checkpoints (all `entry_probe_reset_delay = 6`, occurrence 1)

| # | in | after | question it answers | image (`out/enuma/stage5-bisect/`) | boot.img sha256 | payload.img sha256 |
|---|---|---|---|---|---|---|
| 01 | `_arm_init` | `_PE_init_platform` | did early platform init return? | `01-PE_init_platform` | `278cea60d46765cfb7358a4e2148bf7d481fb0ac8b5acaa358c7cd550ce96b94` | `07cfa28da5a61e570748e07ce8f996cdb737730a39666a03882907a96270305f` |
| 02 | `_arm_init` | `_arm_vm_init` | did arm_vm_init (VM/pmap bootstrap) return? | `02-arm_vm_init` | `f3cd541a6006f6b6a5d6a25ac56db4bfacca6dcbebb8460f18bdbd2100001f52` | `d94f3b0804abf6a3b1ebf36ce0dbe03d3cabeede363b5b890d4f4f33a8fd2fb7` |
| 03 | `_arm_init` | `_PE_init_printf` | did console printf come up (-v visible)? | `03-PE_init_printf` | `07a5ac50ed1ea7a32b3f8403c38de4bd25462f122f9beb4bf34295a95a363c4d` | `c6114a4ac4fbee2888c7c8ed070952cb641f2e2e80b3cce98a5d80676bdb58e6` |
| 04 | `_arm_init` | `_early_random` | did it reach the end of arm_init (just before machine_startup)? | `04-early_random` | `742d5d69cb8fb256b61f092575f9a095b62930e40e66170d3cdc650974e4732b` | `f067e30231e7389139b0ad1d63f1fc964ed355f7838773d90b7f4c0e703134ea` |
| 05 | `_kernel_bootstrap` | `_vm_mem_bootstrap` | did vm_mem_bootstrap (VM memory) return? | `05-vm_mem_bootstrap` | `0cb63a9fb4f39d6432bd40da9cafabb98fdc24f52f39b82fdbb506ffd2ba94f0` | `efafc25bf88d8013b3629a8174075ce1eaeebb4692ff5a50c5cd6f7a7b424712` |
| 06 | `_kernel_bootstrap` | `_sched_init` | did scheduler init return? | `06-sched_init` | `35d0bb0a881e5d1655ad12e5612ad1e52f7e7bcb7647cb3faa853f567c6e58c8` | `363ad803e9f7d19e6326267d59662416f12d9a87d5a0006531b288d4afb6c780` |

Each payload carries the patched kernel (the patched `payload_kernel_sha256` in `payload.json`
differs from the source `39cecb2e…`); the source `kernel.macho` is copied, not modified.

## Expected read-out

- **Reset into fastboot** (~6 s after the checkpoint) = the call returned → the kernel passed that
  point.
- **No reset / hangs on a colour bar** = the kernel stopped before, or inside, that call.

Bisect by walking the table in order: the last checkpoint that resets is the last confirmed
progress; the first one that does not reset is the first unconfirmed step.

## Device results (user observation, filmed; the reset instant is not captured on video)

- 01–03 (`_PE_init_platform`, `_arm_vm_init`, `_PE_init_printf`): **passed** (transitive via 04).
- 04 (`_early_random`): **passed** (three colour bars, ~6 s auto-reset into fastboot).
- 05 (`_vm_mem_bootstrap`): **passed**.
- 06 (`_sched_init`): **passed**.
- 07 (`_kernel_thread_create`), 08 (`_sched_startup`): **passed** (transitive via 09).
- 09 (`_PE_init_iokit`): **passed** (three colour bars, ~6 s auto-reset).
- 10 (`_bsd_init`, reset-**after**), 11 (`_vfs_mountroot`, reset-**after**): **stuck / no reset** — by
  design they cannot pass: `reset_after` fires only after the call returns, and on a storage-less
  board `_bsd_init` ends in `_vfs_mountroot`, which never returns. 11 showed the three colour bars,
  then stuck 20–30 s with no reset (not reset by the firmware watchdog; manual long-press back to
  fastboot). Not evidence of a kernel fault.
- 12 (`_bsd_init`), 13 (`_IOKitInitializeTime`), 14 (`_IOKitBSDInit`), all reset-**before**:
  **passed** (transitive via 15).
- 15 (`_IOFindBSDRoot`, reset-**before**): **passed** (three colour bars, then immediate reset into
  fastboot).
- 16 (`_vfs_mountroot`, reset-**before**): **stuck / no reset** (three colour bars, waited 10+ s, no
  reset; manual long-press back to fastboot). ⇒ inferred: the kernel is stuck **inside
  `_IOFindBSDRoot`** waiting for the root device — the expected endpoint without a storage driver.
  Not direct evidence, as the other `bl`s between 15 and 16 were not tested individually.

### Log observation

After an auto (PSCI) reset into fastboot the pstore has **no `console-ramoops-0`** (checkpoints
04/05/06/09/15); after a manual long-press back it is present (11/16, same as stages 3/4: 15732 B /
279 lines, firmware log only, up to `DARWINBOOT: hand-off` / `Exiting boot services`). The earlier
"XNU zeroed ramoops" hypothesis does not hold; more likely the kernel's PSCI reset path does not
preserve that log (cause unverified).

### Conclusion boundary

No blocking point was found on the kernel side before the root-device wait; stage 6 (storage / root
volume) has not started. Evidence strength = user screen observation.

## Checkpoints 07–11 (larger steps)

`_kernel_bootstrap` creates the first kernel thread (`_kernel_thread_create`) then switches to it via
`_load_context` (which does not return); that thread is `_kernel_bootstrap_thread`, whose body calls
`_sched_startup` → … → `_PE_init_iokit` → … → `_bsd_init`, and `_bsd_init` calls `_vfs_mountroot`
(the mountroot stage where IOKit waits for a root device when there is no storage driver). All
targets below are direct `bl` calls (verified with llvm-objdump; `_kernel_bootstrap_thread` has no
`blr`), so `reset_after` can place the reset on them. All run after the MMU is enabled.

| # | in | after (occ 1) | question it answers | image | boot.img sha256 | payload.img sha256 |
|---|---|---|---|---|---|---|
| 07 | `_kernel_bootstrap` | `_kernel_thread_create` | was the first kernel thread created (end of _kernel_bootstrap, just before _load_context)? | `07-kernel_thread_create` | `d2ef97caf16848bc1e7b52ef1b6457dfb0ec28b22ae67fe614aaefa0604048bb` | `b6b6e2453e6d1e9168f2ac47be67e9447fd7d281d3645dcc8857173ab67f293d` |
| 08 | `_kernel_bootstrap_thread` | `_sched_startup` | did the scheduler start (kernel_bootstrap_thread entered)? | `08-sched_startup` | `4dba6d3bd9136ea08c2b8fb3d0cf2313c2e4c7e71e9149072eadf58e7637ea91` | `cc74955c30d2720e8e3a2bb02ff18ea181460dbbbae784f8d42230455b693451` |
| 09 | `_kernel_bootstrap_thread` | `_PE_init_iokit` | did IOKit initialise? | `09-PE_init_iokit` | `c8bad961a1f3f7f61128ff37f76d8a438b35946f1a9af47e95c39281aa8e881f` | `b4febdc012baf4190b2f38543e013d5e6d497067784931accdc643f11130a433` |
| 10 | `_kernel_bootstrap_thread` | `_bsd_init` | did BSD init enter? | `10-bsd_init` | `26a6e4c97cc9d19b684e5426af194e811262f40a9aec944eea3d9b497935cf1e` | `3d3d007f96dd0d2cb5bebe45938da2d85c42004f35864b468b4ca1d620859c4d` |
| 11 | `_bsd_init` | `_vfs_mountroot` | did it reach mountroot (just before the root-device wait)? | `11-vfs_mountroot` | `6ba764382ab348846c32477b7b2957dbe32c08265704cd31e3b60f9edb5278ab` | `74c5a65536215d166873d71fca04b56c44fc96e114dfe45fcb8901df136ab91d` |

Note: the PSCI reset (`smc #0`, `0x84000009`) is a synchronous trap to EL3, independent of the
kernel's thread/exception state, and the MMU-on reset was already verified on device; the deep
checkpoints (10/11, where interrupts and threads are fully active) are still unverified on device,
so whether the reset still returns to fastboot there is **pending device confirmation**.

## `reset_before` semantics

`entry_probe_reset_before = true` (used together with `entry_probe_reset_delay` and
`entry_probe_reset_after`) redirects the Nth `bl <symbol>` in `entry_probe_reset_in` to a cave that
issues PSCI `SYSTEM_RESET` **immediately — without executing the `bl` and without waiting the
delay**. The delay is still required to trigger the probe and to select the reset-after path, but it
is not waited. It answers "did the kernel reach the call site", not "did the call return", so it
works for callees that never return (`_bsd_init`, `_vfs_mountroot`). `--reset-before` without
`--reset-after` is refused by the probe script.

## Checkpoints 12–16 (reset **before** the call)

| # | in | after (occ 1, before) | question it answers | image | boot.img sha256 | payload.img sha256 |
|---|---|---|---|---|---|---|
| 12 | `_kernel_bootstrap_thread` | `_bsd_init` | reached the bsd_init call site? | `12-before-bsd_init` | `6d91afd12dec1bf7effe4736a8134a68a3fe17142739165771d1c9fa68a0a5a5` | `ac080c6bc35058da607c82bb3633ee1d76368212700d2760e21a8518d2d01181` |
| 13 | `_bsd_init` | `_IOKitInitializeTime` | reached IOKitInitializeTime (+0x458)? | `13-before-IOKitInitializeTime` | `6e335251bd7079ba6b629fcec2a727a5fc35eeef1367ceea923bbbdd0f546548` | `93ab066beaf3b3d58ca5e5b6f1ece2bb2508e7a9975435b38bd23abd7b1dda32` |
| 14 | `_bsd_init` | `_IOKitBSDInit` | reached IOKitBSDInit (+0x64c)? | `14-before-IOKitBSDInit` | `1dfc686030106bb3f73c2447076c8851c374e5abcab14af742b12897f80d3ef9` | `c29dab7f04c6e6abf67041f996e590c9c3b6ef2148f3fb8d781eeb8cdf7bdb94` |
| 15 | `_bsd_init` | `_IOFindBSDRoot` | reached IOFindBSDRoot (+0x6e0, the root-device wait)? | `15-before-IOFindBSDRoot` | `582c241eca45c5be97aa89d951c613cc38ff0a5c48b072fe74c1a3b9df422527` | `ebd67558d419fef172c14e1fa9caea3e0bbb42f31e10970d12e3ab650e2283b8` |
| 16 | `_bsd_init` | `_vfs_mountroot` | reached vfs_mountroot (+0x724), past IOFindBSDRoot? | `16-before-vfs_mountroot` | `4028ecc586d856cfd1bf82a8ec4d34d4958b71b21e501db35eb9ca1abd392fe3` | `74b79f4a3600d1b6560a4bc4199a34c41ba2e5f4bb6b21f958718de15832efab` |

Read-out for 12–16: reset into fastboot = the kernel **reached** that call site (the call was not
made); no reset = it stopped before that call site. If 15 resets but 16 does not, the kernel is
stuck inside `_IOFindBSDRoot` (the root-device wait).
