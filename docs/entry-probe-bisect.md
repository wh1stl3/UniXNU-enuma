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
