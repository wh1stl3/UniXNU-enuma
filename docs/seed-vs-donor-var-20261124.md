# Seed versus donor `/private/var` (2026-11-24)

`self-checked`; offline read-only comparison, no build or device. This is an
image comparison, not a measurement of the runtime mounted Data volume.

## Method

`which` and `command -v` did not find `apfs-fuse` as the default WSL user
or root. `find / -maxdepth 4 -iname 'apfs-fuse*'` found the source tree;
its usable executable is
`/home/wh1stl3/apfs-work/apfs-fuse-66b86bd525e8cb90f9012543be89b1f092b75cf3/build/apfs-fuse`
(`sgan81/apfs-fuse` at that revision). `-h` prints usage but exits nonzero;
that does not mean the binary is missing. Both mounts succeeded as
`wh1stl3`, without root, using `-o ro`.

A is `out/data-seed-macos-20261119/data.dbr`, unpacked with the existing
`UniXNU/drivers/DarwinBoot/Test/packed_ramdisk.py` `regions()` into a
temporary sparse raw image (logical 2,146,996,224 bytes, 10 extents).
Its mounted `root/` is the Data volume root corresponding to `/private/var`.
B is `out/userdata-clean-20261112/OS.raw`, mounted `root/private/var/`.
Both mounts were unmounted with `fusermount -u`, exit 0. The temporary raw
remains at `/tmp/seed-var-ixrlRX/seed.raw`.

## Top-level

Common: `Keychains`, `Managed Preferences`, `MobileAsset`, `MobileDevice`,
`MobileSoftwareUpdate`, `OOPJit`, `audit`, `buddy`, `datamigrator`, `db`,
`dextcores`, `empty`, `folders`, `hardware`, `installd`, `log`, `logs`,
`mobile`, `msgs`, `networkd`, `preferences`, `protected`, `root`, `run`,
`select`, `tmp`, `vm`, `wireless`.

Only A: `.fseventsd`, `containers`, `keybags`. Only B:
`staged_system_apps` (nonempty staged application tree).

## Requested paths

| Relative path | A | B |
|---|---|---|
| `vm/` | yes | yes |
| `db/com.apple.xpc.launchd/` | yes | yes |
| `db/com.apple.xpc.launchd/disabled.plist` | no | no |
| `db/com.apple.xpc.launchd/disabled.migrated` | no | no |
| `db/.AppleSetupDone` | no | no |
| `db/MobileIdentityData` | no | no |
| `db/DataMigration` | no | no |
| `mobile/Library/Preferences/` | yes | yes |
| `root/` | yes | yes |
| `tmp/` | yes | yes |
| `logs/` | yes | yes |

Preference files, all names (fewer than 30):

- A: `.GlobalPreferences.plist`, `backboardd.plist`,
  `com.apple.managedconfiguration.notbackedup.plist`,
  `com.apple.migration.plist`, `com.apple.purplebuddy.notbackedup.plist`,
  `com.apple.purplebuddy.plist`, `com.apple.springboard.plist`.
- B: `.GlobalPreferences.plist`.

## Numeric metadata

These are values reported by this FUSE reader, not independently verified
Darwin mount results; A root is a Data volume root, B is an OS directory.

| Logical path | A uid:gid mode | B uid:gid mode |
|---|---|---|
| `/private/var` | 501:20 0755 | 0:0 0755 |
| `/private/var/mobile` | 99:99 0711 | 501:501 0711 |
| `/private/var/db` | 99:99 0755 | 0:0 0755 |

## Missing nonempty donor paths

Recursive path-set comparison, not content comparison: excluding
`staged_system_apps`, A had 226 entries, B had 205, B-only **zero**, and
the walk reported no errors. The only B-only top-level nonempty directory
is `staged_system_apps/`; it contains 29 staged app directories, e.g.
`VoiceMemos.app/` and `Weather.app/`. Its app subtree was not individually
ranked here: no evidence links it to launchd, keystore, or swap. No missing
launchd/keystore/swap path was found in the compared donor tree. This is
not a comparison of file contents, ACLs, xattrs, APFS firmlinks, or runtime
state.

The 11 specifically listed path checks contain **zero** items present in B
and absent in A. The uid/gid differences and B-only staged apps are factual
leads, but a causal connection to launchd `0x320` is **evidence insufficient,
weak**; receiver semantics and runtime mount metadata are not established.
