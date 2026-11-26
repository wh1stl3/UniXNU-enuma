# enuma r69d Data stage diagnostic — 2026-11-25

Status: `self-checked`; packaged only, not flashed or booted.

## Diagnostic and build

- Compared with r69c, the scratch Data mount failure diagnostic includes
  `stage=%d ready=%d`: `offline scratch Data mount failed: %d stage=%d ready=%d @%s:%d`.
- The supplied successful build reports a 124,571,648-byte kernel, SHA-256
  `b98fae19eaab242782d7a4e1b9c78d8ce981408feff9f0dc794fb0083e8006e6`.
- `strings` found that format in the built kernel. `llvm-nm` found
  `native_owner_data_stage`, `native_ram_block_ready`,
  `native_ram_block_volume_seed`, and `enuma_ipc_record`. The undefined-symbol
  check on `kern_exec.o` found `native_ram_block_volume_seed`, but not
  `mdevlookup` or `mdevgetrange`; the typed reference remains in the object.

## Package

- `.cache/r69d-package.sh` used r69c as `REF` and r69d as `DEST`; exit 0.
- `out/ufs-sm8250-full-20261125-r69d/boot.img`: 169,951,232 bytes;
  SHA-256 `3839025f42a837a471f4a2e3088834d23ef6a9b3325775540cb167511426b8da`.
- Payload SHA-256:
  `2fae0daee42de5ad526bc2556859481972b747ae568ad2aed42175c9d566359d`.
  The kernel extracted via `mtype` hashes to
  `b98fae19eaab242782d7a4e1b9c78d8ce981408feff9f0dc794fb0083e8006e6`.
- The generated `candidate-manifest.json` records identical boot arguments,
  Android header command line, non-kernel payload members, and firmware/DTB
  against the r69c reference. Its historical `r66_*` keys refer to that
  configured r69c reference, not a separate r66 comparison.

No device operations were performed; runtime diagnostic behavior is unverified.
