#!/bin/sh
set -eu
# Use the complete r64 ShengUfs archive: it contains NativeUfsBlock::authenticatesVolume
# and native_ufs_block_authenticates, which the feed archive lacks.
SRC="$UNIXNU_DEVICE/out/ufs-sm8250-ustack-20261124-r64/objects/libShengUfs.a"
DST="build/sheng-ufs/libShengUfs.a"
test -f "$SRC"
test -f "$DST"
cp -- "$SRC" "$DST"
sha256sum "$SRC" "$DST"
EXPECTED=cef82e0a3093f5e5dd563b328cc140c5a66847183a2ca3c90d1b22282a098b89
ACTUAL=$(sha256sum build/sheng-ufs/libShengUfs.a | cut -d' ' -f1)
test "$ACTUAL" = "$EXPECTED"
