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

## Device results (user observation, filmed)

- 01–03 (`_PE_init_platform`, `_arm_vm_init`, `_PE_init_printf`): **passed** (transitive — 04 reset
  means the kernel reached `_early_random`, which is after all three).
- 04 (`_early_random`): **passed**.
- 05 (`_vm_mem_bootstrap`): **passed**.
- 06 (`_sched_init`): **pending**.

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
