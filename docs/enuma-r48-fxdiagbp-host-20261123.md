# r48 fixup diagnostic and boot progress: host-only

Status: self-checked; no device run or independent verification.

The r47 candidate's `device/board.toml` supplies `[payload].kernel_args`.
The official `UniXNU/scripts/unixnu/payload.py:113-117,221-225,243`
serializes these into `EFI/UniXNU/unixnu.toml`; `UniXNULib/Boot.c:85`
passes the selected entry's args to DarwinBoot, which copies them into the
kernel command line (`DarwinBoot.c:615-621,753`). The r48 script copies r47
and appends the two arguments only to the existing xnu entry inside its
payload; it does not modify shared board defaults, ADT, kernel or components.
The argument values below were read back from the r48 FAT payload; its
SHA-256 was also checked against the payload bytes embedded in `boot.img`.
Runtime menu selection and handoff remain unobserved.

```
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1
```

The script checks byte-for-byte that this equals the r47 entry plus
` enuma-fx-diag=1 enuma-bp=1`. All FAT member contents were hashed: only
`unixnu.toml` changes. Other than payload bytes, the boot header differs only
in its image ID field. No compilation units or archives were rebuilt.

| File/member | r47 SHA-256 | r48 SHA-256 |
| --- | --- | --- |
| unixnu.toml | 272e2ed556a51d5706f60fcc5daa33c045fcd5d99f03d71cd1b88138d101afee | f95f740eae84893780d17743a9a4a98f5e01ad2cd5f2482555438000c164bde5 |
| payload.img | 82d21511e0fd5a2f67ed05c84152dac04c544cf56d0913fb4d24f719705e60eb | 423ad1a9f9f7bcb06ddc05cd9697b624cef78a4801d663ca4898835290737fc1 |
| boot.img | e1b6a49959aff7d6aa094d3ce47ce061f9621a9f057551ae185b81c4dbfade83 | f0fa42d6330625919bb76827b9fcb2df62cefedfe8c3a84c3d5d098cb39adb2b |

Unchanged SHA-256: ADT `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`
(also directly compared byte-for-byte); native Mach-O
`6e31bc9ae1efbe193e3473f78286e6119021d23c0eb11c9fa4fdd68f344db74a`;
prelink / payload kernel
`caf39743f6e92ed8f39ceac2f1258c992be60b1bd4aebb225a73c5e515b9ccdb`;
scratch Data `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`;
trustcache `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`.
r47's five checked core artifacts were rehashed after packaging and unchanged.
r48 boot image is 169951232 bytes. `llvm-nm -u` found zero undefined symbols,
including weak undefined, in each Mach-O. Full member hashes and readback are
also in the local `candidate-manifest.json`.

| Conditional observation | Interpretation |
| --- | --- |
| `enuma bp r46 t=` | Required when the enabled progress callback actually runs; `r46` is the unchanged format title, expected in r48. |
| `enuma-fxd: sv= ... fx= ... taint= ... novalid= ... nx=` | Required within a completed enabled progress report. |
| `enuma-fxd: vnode= ... range= ... bytes= ... page=` | Required within a completed enabled progress report. |
| Missing report | Does not distinguish absent callback, failure before report, interleaving, wrapping or off-screen output. |

Counters are relaxed, sampled independently, and do not prove target fixups
were applied. See `docs/enuma-r47-fxdiag-host-20261123.md` for exact semantics.
Enabling diagnostics adds counting and periodic console output; cost, visible
screen capacity, timing, runtime argument handoff and hardware behavior remain
unverified. No stage, root or persistence acceptance follows.

Self-check: WSL root `/home/wh1stl3/.local/bin/python3
scripts/build-enuma-r48-fxdiagbp.py` exited 0. Base HEAD
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`; remote HEAD before build
`8542980d02b4d2cc5c32ee3542de1760b2562aac`.
