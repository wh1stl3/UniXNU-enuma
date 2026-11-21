#!/usr/bin/env bash
#
# data-seed-vm-run.sh — one-shot runner for docs/data-seed-macos-vm-procedure.md (§1-§5).
#
# Run this INSIDE the macOS 15 VM, as the normal user. It is a host-side script only:
# no device, no fastboot, no git, no build. It must not be executed from WSL/Windows.
#
#   bash ~/data-seed-vm-run.sh
#
# INPUTS (override by exporting before running)
#   UNIXNU  default ~/unixnu   must contain
#                              scripts/make-data-seed.py
#                              scripts/seed-data-grow.py
#                              drivers/DarwinBoot/Test/packed_ramdisk.py
#                              build/            (seed-data-grow.py:99 scratch parent)
#   SEED    default ~/seed     must contain 044-76040-038.dmg (5,157,406,069 B,
#                              sha256 3f99b859…028d) — the pin is checked, not downloaded.
#
# WHAT LANDS IN $SEED
#   044-76040-038.dmg   input, untouched
#   os-window.cdr       6,077,580,800 B (~6.08 GB) raw of the OS window, step 2 (§3.3/§3.4).
#                       Reused when it still matches the pin; otherwise renamed to
#                       os-window.cdr.stale-<ts> (never deleted) and converted again.
#   container.raw       6,077,563,392 B dd slice of os-window.cdr (skip 34 x 512), written only
#                       when attaching the whole os-window.cdr yields no usable volume (§3.5).
#                       Safe to delete once step 4 has detached the OS window.
#   data-3g.raw         restored 3 GiB raw of the first seed (§5.2), truncated by step 9 to
#                       ~2,147,000,000 B. Sparse: physical usage is far below the logical size.
#   data-3g.dbr         the 3 GiB packed seed, archived and no longer used (§5.9)
#   data.dbr            THE PRODUCT: packed seed whose logical size is < 2 GiB (§5.9),
#                       the only file that leaves this script (§7)
#   limits.txt          verbatim `diskutil apfs resizeContainer … limits` output (step 7)
#   resize.txt          verbatim `diskutil apfs resizeContainer … 2147m` output (step 8)
#   mnt-3g/             mountpoint directory, empty again after step 6
#
# FREE SPACE: peak ~12 GB (5.16 GB dmg + 6.08 GB cdr + 3 GiB scratch in $UNIXNU/build), so
# step 1 refuses to start below 20 GiB available on $HOME. If step 3 has to fall back to the dd
# slice, container.raw adds ~6.08 GB on top of that (~18 GB peak); the 20 GiB gate does not
# account for it. Deleting 044-76040-038.dmg and os-window.cdr once step 5 passes frees ~11 GB
# (procedure §8).
#
# RULES
#   * Every step passes or exits 1 with the reason. There is no "continue anyway", no retry
#     loop, no second size, no fallback — except the one documented in §3.5: the OS window is
#     attached as a whole disk first (the mount point is discovered, not assumed), and only
#     when that yields no usable volume is the container sliced with `dd bs=512 skip=34` (size
#     and NXSB at block 0 are then checked before attaching the slice).
#   * A failed check means: record the output and STOP. Do not edit bytes to force a pass —
#     never rewrite block_count, never `dd` zeros, never hand-patch the NXSB, never switch to
#     another requested size (procedure §5.11).
#   * No network access, no sudo, and $UNIXNU is only written by seed-data-grow.py into its
#     own tempfile.TemporaryDirectory under $UNIXNU/build; the three .py files are read-only
#     to this script (their hashes are pinned in step 1 from procedure §2.2).
#
set -u
set -o pipefail
# No `set -e` on purpose: every step inspects its own status and calls fail() with a reason.

UNIXNU="${UNIXNU:-$HOME/unixnu}"
SEED="${SEED:-$HOME/seed}"
export UNIXNU SEED

# ---- pins (procedure §2.2, §3.1, §3.4, §5.5, §5.7) --------------------------------
DMG_NAME='044-76040-038.dmg'
DMG_BYTES=5157406069
DMG_SHA256='3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d'
CDR_BYTES=6077580800
CDR_SHA256='e5634d04a8ac35f024845f583394e0a35deb26a04cb0c00286a8674e25a9a4f2'
OS_OFFSET=17408
BUILD_ID='21H461'
GIB=3
SEED_BYTES=3221225472                       # 3 GiB, make-data-seed.py --gib 3 (§4.1 judgment 2)
TARGET_BYTES=2147000000                     # `2147m`, decimal (§5.5)
ISBIG_LIMIT=$((2 * 1024 * 1024 * 1024))     # 2147483648, NativeRamBlock isBig threshold (§5.1)
SIZE_TOLERANCE=$((64 * 1024 * 1024))        # ± 64 MiB (§5.7 judgment 2)
ENCODED_LIMIT=$((64 * 1024 * 1024))         # packed size sanity bound (§4.1 judgment 4, §5.9)
MAKE_DATA_SEED_SHA256='a10a818ae19e2853b8a2e04ac56f9af2ea555c47ef6abaf85e0ee4da2865df0b'
SEED_GROW_SHA256='507bce30053936608ebf4d5b7de75397d7e544934a9949a071a244cc0a3c810c'
PACKED_RAMDISK_SHA256='2291ff803553ee6e5431a4ce3770a36dab0a09f0d1fe036d3e1264ee5dd2a3b3'

# ---- helpers ----------------------------------------------------------------------
say() { printf '\n== %s\n' "$*"; }

fail() {
    printf '\n[STOP] %s\n' "$*" >&2
    printf '[STOP] nothing was patched to work around it; record the output above (procedure §5.11 / §8)\n' >&2
    exit 1
}

sha_of() {
    local line
    line=$(shasum -a 256 "$1") || return 1
    printf '%s' "${line%% *}"
}

size_of() { stat -f%z "$1"; }

# ---- step 1/11: preflight ---------------------------------------------------------
say 'step 1/11 preflight'

df -h "$HOME"
avail_gib=$(df -k "$HOME" | awk 'NR==2 {print int($4 / 1048576)}')
[ -n "$avail_gib" ] || fail "could not read available space for $HOME from df -k"
[ "$avail_gib" -ge 20 ] || fail "only ${avail_gib} GiB available on \$HOME, need >= 20 GiB (peak ~12 GB, procedure §1.1)"

sw_vers
os_version=$(sw_vers -productVersion)
if [ "${ALLOW_UNPINNED_MACOS:-0}" != '1' ]; then
    case "$os_version" in
        15.*) : ;;
        *) fail "macOS $os_version: every pinned byte value below is for 15.x (newfs_apfs 2332.140.13.704.3, procedure §1.2/§9.5). Re-running on another version yields a different APFS metadata layout and a different volume UUID; export ALLOW_UNPINNED_MACOS=1 to run anyway with unvalidated expectations" ;;
    esac
fi

python3 --version
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
    || fail "python3 is older than 3.9 (procedure §1.3)"

for tool in hdiutil diskutil shasum awk; do
    command -v "$tool" >/dev/null 2>&1 || fail "missing required tool: $tool"
done
command -v hdiutil diskutil shasum awk

for script in "$UNIXNU/scripts/make-data-seed.py" "$UNIXNU/scripts/seed-data-grow.py" \
              "$UNIXNU/drivers/DarwinBoot/Test/packed_ramdisk.py"; do
    [ -f "$script" ] || fail "missing $script (copy the three files keeping the scripts/ + drivers/DarwinBoot/Test/ layout, procedure §2)"
done
[ -d "$UNIXNU/build" ] || fail "missing directory $UNIXNU/build: seed-data-grow.py:99 builds its 3 GiB scratch image there and does not create it (procedure §1.6)"
[ -w "$UNIXNU/build" ] || fail "$UNIXNU/build is not writable"

for pair in "$UNIXNU/scripts/make-data-seed.py:$MAKE_DATA_SEED_SHA256" \
            "$UNIXNU/scripts/seed-data-grow.py:$SEED_GROW_SHA256" \
            "$UNIXNU/drivers/DarwinBoot/Test/packed_ramdisk.py:$PACKED_RAMDISK_SHA256"; do
    path=${pair%:*}
    want=${pair##*:}
    got=$(sha_of "$path") || fail "shasum failed on $path"
    [ "$got" = "$want" ] \
        || fail "$(basename "$path") sha256 is $got, procedure §2.2 pins $want: the base scripts drifted and every expected value below is invalid"
done
printf 'base scripts match procedure §2.2 pins\n'

mkdir -p "$SEED" || fail "cannot create $SEED"
DMG="$SEED/$DMG_NAME"
[ -f "$DMG" ] || fail "missing $DMG (the script does not download it)"
dmg_bytes=$(size_of "$DMG") || fail "stat failed on $DMG"
[ "$dmg_bytes" = "$DMG_BYTES" ] \
    || fail "$DMG is $dmg_bytes bytes, pinned 5157406069 (procedure §3.1: stop, do not convert)"
dmg_sha=$(sha_of "$DMG") || fail "shasum failed on $DMG"
[ "$dmg_sha" = "$DMG_SHA256" ] \
    || fail "$DMG sha256 is $dmg_sha, pinned 3f99b859…028d (procedure §3.2: stop)"
printf 'dmg ok: %s bytes, sha256 %s\n' "$dmg_bytes" "$dmg_sha"

# ---- step 2/11: decompress the OS window to raw -----------------------------------
say 'step 2/11 hdiutil convert -format UDTO (raw OS window, 1-3 min; reused if already pinned)'
CDR="$SEED/os-window.cdr"
# Reuse an existing os-window.cdr when it still matches the §3.4 pin (a previous run may have
# stopped later, e.g. in step 3). Anything else is MOVED ASIDE, never deleted: `hdiutil convert`
# would otherwise refuse an existing output or need an interactive overwrite answer.
CONVERT_MODE='fresh'
cdr_needs_convert=1
if [ -f "$CDR" ]; then
    cdr_bytes=$(size_of "$CDR") || fail "stat failed on $CDR"
    cdr_sha=$(sha_of "$CDR") || cdr_sha=''
    if [ "$cdr_bytes" = "$CDR_BYTES" ] && [ "$cdr_sha" = "$CDR_SHA256" ]; then
        printf 'reusing existing os-window.cdr (%s bytes, sha256 %s, matches the §3.4 pin)\n' \
            "$cdr_bytes" "$cdr_sha"
        CONVERT_MODE='reuse'
        cdr_needs_convert=0
    else
        stamp=$(date +%Y%m%d-%H%M%S)
        stale="$CDR.stale-$stamp"
        suffix=1
        while [ -e "$stale" ]; do
            stale="$CDR.stale-$stamp-$suffix"
            suffix=$((suffix + 1))
        done
        printf 'existing os-window.cdr is %s bytes / sha256 %s, pinned %s / e5634d04…a4f2: renaming it to %s and converting again (nothing is deleted, procedure §3.4)\n' \
            "$cdr_bytes" "${cdr_sha:-<unreadable>}" "$CDR_BYTES" "$stale"
        mv "$CDR" "$stale" \
            || fail "could not rename $CDR to $stale; refusing to convert on top of it (nothing was deleted)"
    fi
fi
if [ "$cdr_needs_convert" -eq 1 ]; then
    hdiutil convert "$DMG" -format UDTO -o "$SEED/os-window" || fail "hdiutil convert failed"
    [ -f "$CDR" ] || fail "hdiutil convert returned success but $CDR does not exist"
fi
cdr_bytes=$(size_of "$CDR") || fail "stat failed on $CDR"
[ "$cdr_bytes" = "$CDR_BYTES" ] \
    || fail "$CDR is $cdr_bytes bytes, pinned 6077580800 (procedure §3.4)"
cdr_sha=$(sha_of "$CDR") || fail "shasum failed on $CDR"
[ "$cdr_sha" = "$CDR_SHA256" ] \
    || fail "$CDR sha256 is $cdr_sha, pinned e5634d04…a4f2: hdiutil convert is lossless, so the source dmg was not the pinned one (procedure §3.4). Stop."
printf 'raw os window ok: %s bytes, sha256 %s\n' "$cdr_bytes" "$cdr_sha"

# ---- step 3/11: attach the OS window read-only ------------------------------------
say 'step 3/11 hdiutil attach whole disk (read-only; dd slice only if no usable volume)'
SLICE_RAW="$SEED/container.raw"
FALLBACK_MP='/Volumes/OSX'
OSX_MOUNT=''
ATTACH_MODE=''

mount_ok() { [ -d "$1/private/var" ] && [ -e "$1/sbin/launchd" ]; }

# Primary path: hand the whole raw to hdiutil and let it read the GPT, then discover the
# mount point instead of assuming a name. The `-offset` attach form used by earlier revisions
# is ABANDONED: this macOS build rejects it outright ("unknown option"), so it is never tried —
# only the whole-disk attach and, if that yields no usable volume, the dd slice remain.
volumes_before=$(ls /Volumes 2>/dev/null)
attach_whole_out=$(hdiutil attach -readonly -nobrowse -owners off "$CDR" 2>&1)
attach_whole_rc=$?
[ -z "$attach_whole_out" ] || printf '%s\n' "$attach_whole_out"
new_mounts=''
if [ "$attach_whole_rc" -eq 0 ]; then
    volumes_after=$(ls /Volumes 2>/dev/null)
    new_mounts=$(awk 'NR==FNR { seen[$0] = 1; next } !($0 in seen)' \
        <(printf '%s\n' "$volumes_before") <(printf '%s\n' "$volumes_after"))
fi
new_count=0
new_name=''
while IFS= read -r cand; do
    [ -n "$cand" ] || continue
    new_count=$((new_count + 1))
    new_name="$cand"
done <<EOF
$new_mounts
EOF

if [ "$attach_whole_rc" -eq 0 ] && [ "$new_count" -eq 1 ] && mount_ok "/Volumes/$new_name"; then
    OSX_MOUNT="/Volumes/$new_name"
    ATTACH_MODE='whole'
    printf 'whole-disk attach mounted %s (exactly one new volume, private/var is a dir, sbin/launchd present)\n' \
        "$OSX_MOUNT"
else
    if [ "$attach_whole_rc" -ne 0 ]; then
        printf 'whole-disk attach exited %d; falling back to a dd slice of the container (procedure §3.5)\n' \
            "$attach_whole_rc"
    elif [ "$new_count" -ne 1 ]; then
        printf 'whole-disk attach added %d entries under /Volumes, expected exactly 1; falling back to a dd slice (procedure §3.5)\n' \
            "$new_count"
    else
        printf 'whole-disk attach mounted /Volumes/%s but private/var or sbin/launchd is missing; falling back to a dd slice (procedure §3.5)\n' \
            "$new_name"
    fi
    while IFS= read -r cand; do
        [ -n "$cand" ] || continue
        hdiutil detach "/Volumes/$cand" >/dev/null 2>&1 \
            || printf 'warning: could not detach /Volumes/%s before the dd slice (procedure §8)\n' "$cand"
    done <<EOF
$new_mounts
EOF
    if [ -e "$FALLBACK_MP" ] && [ -n "$(ls -A "$FALLBACK_MP" 2>/dev/null)" ]; then
        fail "$FALLBACK_MP is not empty; unmount whatever is there first (procedure §8). Not creating or reusing a busy mountpoint"
    fi
    [ "$((OS_OFFSET % 512))" -eq 0 ] \
        || fail "OS_OFFSET $OS_OFFSET is not a multiple of 512; bs=512 skip would land off the container"
    cdr_now=$(size_of "$CDR") || fail "stat failed on $CDR"
    expected_slice=$((cdr_now - OS_OFFSET))
    printf 'note: %s will take %d bytes on top of the cdr; the 20 GiB floor from step 1 does not cover it (procedure §3.5/§8)\n' \
        "$SLICE_RAW" "$expected_slice"
    dd if="$CDR" of="$SLICE_RAW" bs=512 skip=$((OS_OFFSET / 512)) \
        || fail "dd bs=512 skip=$((OS_OFFSET / 512)) $CDR -> $SLICE_RAW failed"
    slice_bytes=$(size_of "$SLICE_RAW") || fail "stat failed on $SLICE_RAW"
    [ "$slice_bytes" = "$expected_slice" ] \
        || fail "$SLICE_RAW is $slice_bytes bytes, expected $cdr_now - $OS_OFFSET = $expected_slice"
    magic_out=$(python3 - "$SLICE_RAW" <<'PY'
import sys

with open(sys.argv[1], 'rb') as handle:
    head = handle.read(36)
print('MAGIC_AT_32=%r' % head[32:36])
sys.exit(0 if head[32:36] == b'NXSB' else 1)
PY
)
    magic_rc=$?
    printf '%s\n' "$magic_out"
    [ "$magic_rc" -eq 0 ] \
        || fail "$SLICE_RAW does not hold NXSB at block 0 offset 32: the slice start is not 17408 or the raw is not the pinned OS window (procedure §3.5)"
    printf 'container slice ok: %s bytes, NXSB at block 0 offset 32\n' "$slice_bytes"

    attach_dd_out=$(hdiutil attach -imagekey diskimage-class=CRawDiskImage \
        -readonly -nobrowse -owners off -mountpoint "$FALLBACK_MP" "$SLICE_RAW" 2>&1)
    attach_dd_rc=$?
    if [ "$attach_dd_rc" -ne 0 ]; then
        printf '%s\n' "$attach_dd_out"
        fail "both attach forms failed. (1) whole disk exit $attach_whole_rc: $attach_whole_out  (2) dd slice exit $attach_dd_rc: $attach_dd_out  -- see procedure §8: hdiutil info | grep -iE 'os-window|container', then hdiutil detach /dev/disk<N> -force"
    fi
    OSX_MOUNT="$FALLBACK_MP"
    ATTACH_MODE='dd'
fi
[ -d "$OSX_MOUNT/private/var" ] \
    || fail "$OSX_MOUNT/private/var is not a directory: the volume was not mounted owners off (procedure §3.5/§3.6)"
[ -e "$OSX_MOUNT/sbin/launchd" ] \
    || fail "$OSX_MOUNT/sbin/launchd is missing: this is not an IPSW OS volume (make-data-seed.py:41 would reject it)"
printf 'OS window attached at %s (attach mode %s, private/var is a dir, sbin/launchd present)\n' \
    "$OSX_MOUNT" "$ATTACH_MODE"

# ---- step 4/11: build the 3 GiB seed ----------------------------------------------
say 'step 4/11 make-data-seed.py --gib 3 --build 21H461 --skip-setup (1-2 min)'
if [ -e "$SEED/data.dbr" ]; then
    hdiutil detach "$OSX_MOUNT" >/dev/null 2>&1 || true
    fail "$SEED/data.dbr already exists and make-data-seed.py:43 refuses to overwrite an installation seed. Keep the old one (it may be the only copy bound downstream): mv \"$SEED/data.dbr\" \"$SEED/data.prev.dbr\" (procedure §8), then rerun"
fi
( cd "$UNIXNU" && python3 scripts/make-data-seed.py "$OSX_MOUNT" "$SEED/data.dbr" \
      --gib "$GIB" --build "$BUILD_ID" --skip-setup )
seed_rc=$?
if [ "$seed_rc" -ne 0 ]; then
    hdiutil detach "$OSX_MOUNT" >/dev/null 2>&1 || true
    fail "make-data-seed.py exited $seed_rc (its output is above; procedure §8 has one-line remedies)"
fi
hdiutil detach "$OSX_MOUNT" || fail "hdiutil detach $OSX_MOUNT failed"
[ -f "$SEED/data.dbr" ] || fail "make-data-seed.py exited 0 but $SEED/data.dbr does not exist"

# ---- step 5/11: restore the 3 GiB raw ---------------------------------------------
say 'step 5/11 restore data.dbr -> data-3g.raw (must be exactly 3 GiB)'
RAW="$SEED/data-3g.raw"
restore_out=$(python3 - <<'PY'
import os
import sys
sys.path.insert(0, os.path.join(os.environ['UNIXNU'], 'drivers', 'DarwinBoot', 'Test'))
import packed_ramdisk as pr

src = os.path.join(os.environ['SEED'], 'data.dbr')
dst = os.path.join(os.environ['SEED'], 'data-3g.raw')
logical, extents = pr.regions(open(src, 'rb').read())
if logical != 3 * 1024 ** 3:
    sys.exit('logical size is %d, not 3 GiB (3221225472): --gib 3 did not take effect' % logical)
if os.path.exists(dst):
    os.unlink(dst)
with open(dst, 'wb') as handle:
    handle.truncate(logical)
    for offset, data in extents:
        handle.seek(offset)
        handle.write(data)
print('raw_bytes %d logical %d extents %d' % (os.path.getsize(dst), logical, len(extents)))
PY
)
restore_rc=$?
[ "$restore_rc" -eq 0 ] || fail "restoring $RAW failed (message above); data.dbr is left untouched"
printf '%s\n' "$restore_out"
raw_bytes=$(size_of "$RAW") || fail "stat failed on $RAW"
[ "$raw_bytes" = "$SEED_BYTES" ] || fail "$RAW is $raw_bytes bytes, expected 3221225472"

# ---- step 6/11: the pre-shrink volume UUID ----------------------------------------
say 'step 6/11 read UUID_BEFORE from data-3g.raw (read-only mount)'
MP3="$SEED/mnt-3g"
mkdir -p "$MP3" || fail "cannot create $MP3"
hdiutil attach -imagekey diskimage-class=CRawDiskImage -readonly -owners off -nobrowse \
    -mountpoint "$MP3" "$RAW" || fail "hdiutil attach $RAW failed (procedure §8: a dirty container may need the -readonly removed)"
info_out=$(diskutil info -plist "$MP3" | python3 -c '
import plistlib
import sys
info = plistlib.loads(sys.stdin.buffer.read())
print("# volume: uuid=%s name=%r" % (info.get("VolumeUUID"), info.get("VolumeName")))
print("UUID_BEFORE=%s" % (info.get("VolumeUUID") or ""))
print("VOLUME_NAME=%s" % (info.get("VolumeName") or ""))
')
info_rc=$?
if [ "$info_rc" -ne 0 ]; then
    hdiutil detach "$MP3" >/dev/null 2>&1 || true
    fail "diskutil info -plist $MP3 failed"
fi
hdiutil detach "$MP3" || fail "hdiutil detach $MP3 failed"
printf '%s\n' "$info_out"
eval "$info_out"
[ -n "$UUID_BEFORE" ] || fail "no VolumeUUID on $MP3: the restored raw is not a mountable APFS volume"
[ "$VOLUME_NAME" = 'Data' ] || fail "volume name is '$VOLUME_NAME', expected Data (make-data-seed.py:52 -volname Data)"
printf 'UUID_BEFORE=%s (must still match after the shrink, procedure §5.3/§5.10)\n' "$UUID_BEFORE"

# ---- step 7/11: container, then the shrink floor ----------------------------------
say 'step 7/11 locate the APFS container and ask for its limits'
attach_out=$(hdiutil attach -imagekey diskimage-class=CRawDiskImage -nomount -nobrowse "$RAW") \
    || fail "hdiutil attach -nomount $RAW failed"
DISK=$(printf '%s\n' "$attach_out" | awk 'NR==1 {print $1}')
case "$DISK" in
    /dev/disk[0-9]*) : ;;
    *) fail "no /dev/diskN device in the attach output: $attach_out" ;;
esac
container_out=$(python3 - "$(basename "$DISK")" <<'PY'
import plistlib
import subprocess
import sys

store = sys.argv[1]
listing = plistlib.loads(subprocess.check_output(['diskutil', 'apfs', 'list', '-plist']))
refs = [entry['ContainerReference'] for entry in listing['Containers']
        if any(store_entry.get('DeviceIdentifier') == store
               for store_entry in entry.get('PhysicalStores', []))]
if len(refs) != 1:
    sys.exit('expected exactly one APFS container backed by %s, found %d' % (store, len(refs)))
print('CONTAINER=%s' % refs[0])
PY
)
container_rc=$?
if [ "$container_rc" -ne 0 ]; then
    hdiutil detach "$DISK" >/dev/null 2>&1 || true
    fail "APFS container lookup failed (message above); refusing to guess diskNsY from diskN (procedure §5.4)"
fi
printf '%s\n' "$container_out"
eval "$container_out"
[ -n "$CONTAINER" ] || fail "empty container reference for $DISK"

LIMITS_LOG="$SEED/limits.txt"
printf '\n-- diskutil apfs resizeContainer %s limits (prints constraints only; its exit status is not a gate, procedure §5.4)\n' "$CONTAINER"
diskutil apfs resizeContainer "$CONTAINER" limits > "$LIMITS_LOG" 2>&1 || true
cat "$LIMITS_LOG"

floor_out=$(python3 - "$LIMITS_LOG" <<'PY'
import re
import sys

text = open(sys.argv[1], 'r', errors='replace').read()
UNITS = {'': 1, 'b': 1, 'byte': 1, 'bytes': 1,
         'k': 10 ** 3, 'kb': 10 ** 3, 'm': 10 ** 6, 'mb': 10 ** 6,
         'g': 10 ** 9, 'gb': 10 ** 9, 't': 10 ** 12, 'tb': 10 ** 12,
         'ki': 1024, 'kib': 1024, 'mi': 1024 ** 2, 'mib': 1024 ** 2,
         'gi': 1024 ** 3, 'gib': 1024 ** 3, 'ti': 1024 ** 4, 'tib': 1024 ** 4}
CONNECTORS = {'and', 'or', 'to', 'is', 'was', 'of', 'at'}


def numbers(line):
    # A quantity, not part of a device name or a block count: nothing alphanumeric may
    # precede the digits, and the word after them must be a known unit or a connector,
    # so "disk9s2" and "524,169 blocks" are skipped instead of being read as bytes.
    found = []
    for match in re.finditer(r'(?<![0-9A-Za-z])([0-9][0-9,\.]*)', line):
        try:
            value = float(match.group(1).replace(',', ''))
        except ValueError:
            continue
        word = re.match(r'\s*([A-Za-z]+)', line[match.end():])
        if word:
            unit = word.group(1).lower()
            if unit in UNITS:
                value *= UNITS[unit]
            elif unit not in CONNECTORS:
                continue
        found.append(int(value))
    return found


candidates = []
for line in text.splitlines():
    lowered = line.lower()
    if 'minimum' in lowered or 'between' in lowered or re.search(r'\bmin\b', lowered):
        candidates.extend(numbers(line))
print('# limits lower-bound candidates (bytes): %s' % sorted(set(candidates)))
print('LIMIT_FLOOR=%s' % (min(candidates) if candidates else ''))
PY
)
floor_rc=$?
if [ "$floor_rc" -ne 0 ]; then
    hdiutil detach "$DISK" >/dev/null 2>&1 || true
    fail "parsing $LIMITS_LOG failed; refusing to attempt the shrink blind"
fi
printf '%s\n' "$floor_out"
eval "$floor_out"
if [ -z "$LIMIT_FLOOR" ]; then
    hdiutil detach "$DISK" >/dev/null 2>&1 || true
    fail "no lower bound could be parsed out of $LIMITS_LOG; not attempting a blind shrink (procedure §5.11: record the output and stop)"
fi
if [ "$LIMIT_FLOOR" -gt "$TARGET_BYTES" ]; then
    hdiutil detach "$DISK" >/dev/null 2>&1 || true
    fail "the container cannot shrink below $LIMIT_FLOOR bytes, which is above the 2147m request ($TARGET_BYTES B). Stopping without trying another size (procedure §5.11)"
fi
printf 'shrink floor %s bytes <= %s requested\n' "$LIMIT_FLOOR" "$TARGET_BYTES"

# ---- step 8/11: shrink the container ----------------------------------------------
say 'step 8/11 diskutil apfs resizeContainer <container> 2147m'
RESIZE_LOG="$SEED/resize.txt"
diskutil apfs resizeContainer "$CONTAINER" 2147m > "$RESIZE_LOG" 2>&1
RESIZE_EXIT=$?
cat "$RESIZE_LOG"
if [ "$RESIZE_EXIT" -ne 0 ]; then
    hdiutil detach "$DISK" >/dev/null 2>&1 || true
    fail "resizeContainer exited $RESIZE_EXIT; its verbatim output is above and in $RESIZE_LOG. Do not patch block_count, do not dd zeros, do not retry another size (procedure §5.11)"
fi
hdiutil detach "$DISK" || fail "hdiutil detach $DISK failed"

# ---- step 9/11: verify NXSB/Fletcher64/size, truncate ------------------------------
say 'step 9/11 verify block 0 (NXSB, Fletcher64, block_count) and truncate data-3g.raw'
block_out=$(python3 - "$SIZE_TOLERANCE" <<'PY'
import os
import struct
import sys
import uuid

path = os.path.join(os.environ['SEED'], 'data-3g.raw')
TARGET = 2147000000
LIMIT = 2 * 1024 ** 3
TOLERANCE = int(sys.argv[1])            # SIZE_TOLERANCE from the pins block above


def valid(block):                       # same fletcher64 as procedure §5.7 / apfs-check.py:18-25
    a = c = 0
    for word in struct.unpack('<' + 'I' * ((len(block) - 8) // 4), block[8:]):
        a = (a + word) % 0xffffffff
        c = (c + a) % 0xffffffff
    lo = 0xffffffff - (a + c) % 0xffffffff
    hi = 0xffffffff - (a + lo) % 0xffffffff
    return struct.unpack_from('<Q', block, 0)[0] == hi << 32 | lo


with open(path, 'rb') as handle:
    header = handle.read(4096)
if header[32:36] != b'NXSB':
    sys.exit('block 0 magic is %r, not NXSB' % header[32:36])
if not valid(header):
    sys.exit('block 0 Fletcher64 checksum is broken')
blocksize = struct.unpack_from('<I', header, 36)[0]
blocks = struct.unpack_from('<Q', header, 40)[0]
chosen = blocks * blocksize
container_uuid = str(uuid.UUID(bytes=header[72:88])).upper()
print('# magic NXSB cksum_ok True block_size %d block_count %d' % (blocksize, blocks))
print('# container_bytes %d container_uuid %s' % (chosen, container_uuid))
if blocksize != 4096:
    sys.exit('block size is %d, not 4096' % blocksize)
if abs(chosen - TARGET) > TOLERANCE:
    sys.exit('container is %d bytes, not %d +- %d (did the shrink reach block 0?)'
             % (chosen, TARGET, TOLERANCE))
if chosen >= LIMIT:
    sys.exit('container is %d bytes, still at or above the 2 GiB isBig threshold (%d)' % (chosen, LIMIT))
before = os.path.getsize(path)
if before < chosen:
    sys.exit('raw is %d bytes, shorter than the %d-byte container it holds' % (before, chosen))
with open(path, 'r+b') as handle:
    handle.truncate(chosen)
print('# raw_bytes %d -> %d' % (before, os.path.getsize(path)))
print('BLOCK_COUNT=%d' % blocks)
print('CONTAINER_BYTES=%d' % chosen)
print('CONTAINER_UUID=%s' % container_uuid)
PY
)
block_rc=$?
[ "$block_rc" -eq 0 ] || fail "block-0 verification failed (reason above); the raw was not truncated and data-3g.dbr still holds the 3 GiB seed"
printf '%s\n' "$block_out"
eval "$block_out"
truncated=$(size_of "$RAW") || fail "stat failed on $RAW"
[ "$truncated" = "$CONTAINER_BYTES" ] \
    || fail "$RAW is $truncated bytes after truncation, expected $CONTAINER_BYTES"

# ---- step 10/11: repack ------------------------------------------------------------
say 'step 10/11 archive the 3 GiB seed and pack data-3g.raw -> data.dbr'
if [ -e "$SEED/data-3g.dbr" ]; then
    fail "$SEED/data-3g.dbr already exists: the 3 GiB archive is never overwritten. Move it away first"
fi
mv "$SEED/data.dbr" "$SEED/data-3g.dbr" || fail "mv data.dbr -> data-3g.dbr failed"
[ -f "$SEED/data.dbr" ] && fail "$SEED/data.dbr still exists; packed_ramdisk.py:142 opens the output with 'xb' and would fail"
pack_out=$(python3 "$UNIXNU/drivers/DarwinBoot/Test/packed_ramdisk.py" "$RAW" "$SEED/data.dbr")
pack_rc=$?
[ "$pack_rc" -eq 0 ] || fail "packed_ramdisk.py exited $pack_rc (the 3 GiB archive is intact at $SEED/data-3g.dbr; fix and rerun from step 10, not step 5)"
printf '%s\n' "$pack_out"
json_out=$(printf '%s\n' "$pack_out" | python3 -c '
import json
import sys
report = json.load(sys.stdin)
for key in ("bytes", "sha256", "encoded_bytes", "encoded_sha256"):
    if key not in report:
        sys.exit("packed_ramdisk.py output has no %r" % key)
print("# packed json: %s" % json.dumps({key: report[key] for key in
      ("bytes", "sha256", "encoded_bytes", "encoded_sha256")}))
print("LOGICAL_BYTES=%d" % report["bytes"])
print("ENCODED_BYTES=%d" % report["encoded_bytes"])
print("SEED_IDENTITY=%s" % report["sha256"])
')
json_rc=$?
if [ "$json_rc" -ne 0 ]; then
    fail "could not parse the packed_ramdisk.py JSON report (data.dbr exists; do not repack blindly)"
fi
printf '%s\n' "$json_out"
eval "$json_out"
[ "$LOGICAL_BYTES" = "$CONTAINER_BYTES" ] \
    || fail "packed logical size $LOGICAL_BYTES does not match the container $CONTAINER_BYTES"
[ "$LOGICAL_BYTES" -lt "$ISBIG_LIMIT" ] \
    || fail "packed logical size $LOGICAL_BYTES is not below 2 GiB ($ISBIG_LIMIT): the seed would take the isBig path (procedure §5.1)"
[ "$ENCODED_BYTES" -le "$ENCODED_LIMIT" ] \
    || fail "encoded_bytes $ENCODED_BYTES exceeds 64 MiB: the 3 GiB raw did not stay sparse. Redo from step 5, do not delete data to force it under the bound (procedure §5.9/§5.11)"
encoded_on_disk=$(size_of "$SEED/data.dbr") || fail "stat failed on $SEED/data.dbr"
[ "$encoded_on_disk" = "$ENCODED_BYTES" ] \
    || fail "$SEED/data.dbr is $encoded_on_disk bytes on disk, JSON says $ENCODED_BYTES"

# ---- step 11/11: final hash ---------------------------------------------------------
say 'step 11/11 final hash'
shasum -a 256 "$SEED/data.dbr" || fail "shasum failed on $SEED/data.dbr"
DATA_DBR_SHA256=$(sha_of "$SEED/data.dbr") || fail "shasum failed on $SEED/data.dbr"

printf '\nseed identity (packed_ramdisk sha256, the value downstream binds stores to): %s\n' "$SEED_IDENTITY"
printf 'next: copy %s to the shared out/data-seed-macos/ (procedure §7) - it must not be committed\n' "$SEED/data.dbr"

cat <<EOF

===SEED-SUMMARY===
ATTACH_MODE=$ATTACH_MODE
CONVERT_MODE=$CONVERT_MODE
BLOCK_COUNT=$BLOCK_COUNT
CONTAINER_BYTES=$CONTAINER_BYTES
CONTAINER_UUID=$CONTAINER_UUID
UUID_BEFORE=$UUID_BEFORE
ENCODED_BYTES=$ENCODED_BYTES
LOGICAL_BYTES=$LOGICAL_BYTES
DATA_DBR_SHA256=$DATA_DBR_SHA256
RESIZE_EXIT=$RESIZE_EXIT
===END===
EOF
