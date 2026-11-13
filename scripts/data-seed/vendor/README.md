# Exact public source snapshot for the one-shot Data job

This is not a UniXNU mirror or a new kernel/base revision. Eight raw files
(38,664 bytes including both licenses) are exported using `git show REV:PATH`
from the original fixed commits. No CRLF worktree source, local dirty change,
Apple binary, private key or device identity is included. `.gitattributes`
keeps this subtree LF on every checkout. `SOURCES.json` gives every original
revision/path, Git blob, SHA-256 and official public blob API URL.

## Copyright and license

The six files under the UniXNU source entry are covered by the unmodified
`unixnu/LICENSE`: Copyright (c) 2026, UniXNU contributors. All rights reserved.
SPDX: **BSD-2-Clause-Patent**. The two files under the DarwinBoot source entry
are covered by the unmodified `unixnu/drivers/DarwinBoot/LICENSE`: Copyright
(c) 2026, DarwinBoot contributors. All rights reserved. SPDX:
**BSD-2-Clause-Patent**. Full notices, conditions, patent grant and disclaimer
are retained in those files, not substituted by this summary. No vendored file
has a conflicting file-specific license notice.

The UniXNU commit itself cannot be fetched from the configured official remote;
that is why the first job stopped before Apple download. However, each of its
six selected raw blobs, including LICENSE, was fetched through that official
public repository's blob API and byte-compared successfully. This independently
establishes public provenance without claiming that the whole local commit is
published. The DarwinBoot commit and both selected blobs also resolve through
the official public API. CI does not need either remote checkout anymore.

## Closed runtime dependency paths

| Entry | Non-stdlib dependencies / use |
| --- | --- |
| `build.fetch_os` | `unixnu` package init, `unixnu.ipsw` and its `.util` import; the unchanged OS profile is read as TOML |
| `build.make_seed` | loads unchanged `scripts/make-data-seed.py`, calls only `merge`; its top-level import loads `drivers/DarwinBoot/Test/packed_ramdisk.py` |
| pack and verify | the same unchanged packed writer; only Python standard library dependencies |
| `build` preflight | checks original revision metadata plus every raw source/license SHA-256 and Git blob before Apple download |

The official make-data-seed `main()` is **not called**: therefore its
`seed-data-grow.py` subprocess and 32 MiB creation path are not part of this
job's closure. Similarly, unused ipsw functions for kernelcache, AEA and trust
cache are not called and execute no imports/tools at module load. No build
driver, native component, compiler, kernel or additional submodule is needed.
The source files are retained whole and byte-identical rather than extracting
or rewriting individual functions. Actual macOS dependencies remain hdiutil,
diskutil and the already-selected OpenSSL 3; encryption/receive behavior is
unchanged. The existing source.json and its Apple/profile/manifest/3 GiB pins
remain unchanged.

Review checkpoint only: no second push/run. Re-run `test_tools.py` to check
dependency imports, all snapshot pins and the nine existing offline tests.
