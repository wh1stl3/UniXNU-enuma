# r69b ShengUfs archive integration

The feed archive lacks the authentication implementation needed by the build.
The candidate source depends on the deleted `RootWarmInput.h`, so it cannot
currently be rebuilt. The recipe replaces the feed archive with the complete
r64 archive as the last recipe in the archives list.

- Source: `out/ufs-sm8250-ustack-20261124-r64/objects/libShengUfs.a`
- SHA-256: `cef82e0a3093f5e5dd563b328cc140c5a66847183a2ca3c90d1b22282a098b89`
- External dependencies: `_verified_root_*`, `_vr_*`,
  `_native_ram_block_bytes`, `_native_ram_block_ready`.

The r64 archive ABI's compatibility with the official build chain has not
been finally verified. This replacement requires independent deep review.

- `XNU_NATIVE_UFS=1` must be explicitly set; otherwise the archive is not
  included in the final link.
- `CONFIG_XNU_NATIVE_UFS=y` in defconfig has not been shown to set that
  environment variable.
- The actual `.config` takes precedence over the wrapper environment variable.
- Ensure the actual `.config` contains `CONFIG_XNU_NATIVE_UFS=y`.

## Safe downgrade

- HID standin is removed from the link and injection source to avoid
  `__mod_init_func` and late explicit construction as two entry points.
  The read-only build-tree `xnu-work` copy still requires synchronization
  before this downgrade is ready to build.
- `original-bindings.o` binds the original IOStorageFamily without introducing
  a second `IOBlockStorageDevice` implementation.
- Data uses `/dev/md0` as temporary scratch, not UUID-based disk selection;
  the seed digest is not checked.
- The replacement recipe is the last UFS archive writer in the recipe list;
  it asserts the copied archive SHA-256 before linking.

## r69c Data branch correction

- r69b encountered panic 22 on device.
- The typed Data branch was not enabled, so the build took the `/dev/md0` path.
- r69c sets `XNU_NATIVE_RAM_BLOCK=1` and retains the Data UUID
  `62F1BC9E-4868-4CFF-BF7E-59AFCD474B4F`. The correction is not yet built
  or tested on device.
