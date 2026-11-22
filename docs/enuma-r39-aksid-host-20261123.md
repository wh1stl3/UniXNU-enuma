# enuma r39 keystore identity host build

`self-checked`, host only; no device access, independent review or verifier.
r35 already contains a nonzero eight-byte `/chosen/unique-chip-id` and
four-byte `/chosen/chip-id`, so neither ADT nor seed nor board config changes.
The existing seed is not reproduced here. `display-scale=2` remains.

`package/EnumaKeyStoreProbe.cpp` reads the I/O Registry device-tree plane
`/chosen`: it prefers the first eight bytes of nonzero `unique-chip-id` when
length is at least eight, then the first four bytes of nonzero `chip-id` when
length is at least four. It copies at most capacity and returns copied length,
otherwise zero. The consumer supplies a 32-byte buffer. The existing
`enuma-aks: aksid %zu %s` probe remains. Source API follows this tree's
`IORegistryEntry::fromPath` use in UniXNU commit
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`,
`patches/xnu/offline-owner-boot-manifest.patch`; strategy also follows
`UniXNU-sheng@c8f92b20 package/KeyStoreProbe.cpp` (BSD-2-Clause-Patent).

## Host evidence

Run in WSL root with Python 3.11 and the existing r35 dependencies:
`PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin python3 -B scripts/build-enuma-r39-aksid.py`.
Final build exit 0. Initial compile failed because the device-tree plane
declaration header was absent; it was added before the successful build.
Detailed logs and `candidate-manifest.json` are in
`out/ufs-sm8250-launchd-aksid-20261123-r39/`.

| Input/output | r35 SHA-256 | r39 SHA-256 |
|---|---|---|
| EnumaKeyStoreProbe.o | `e7d5910b79926faeab1da4fed6c6a4e2b39aef6ffd57e930c20f98ea0a12018e` | `0536cd232556d034757777f444a0b8378e6f6a2ef5bc0bab324a63f4f0278390` |
| libAppleKeyStoreState.a | `78335b9b7f4ee11daa04fbd3240afbb989a9a2aa7f6f22ef1478b065c533b71b` | `76009e6dba13d0810b8fb813847f6745eb6878e0ab0e219980b11cbefa843325` |
| native.macho | `0352644a06f030608a0889f70f7453eb5fc302fb66a676ae134dc2eb8c2845f0` | `217b433536c136c1e50a73bf3dd7b1e4baa940a975feefe945c017b533811223` |
| prelink.macho | `d974059707e07b77504e38d984c4c3bf5a41b6a39fc4931ecfbcb42ed97cb26a` | `8ca90d32e533e2135d013578560adfc56589e0c911382b7ff9f3ee405ae11ba0` |
| ADT | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | same |
| payload.img | `c1c3e97b19be7c765210a93d61edfc3fc52c524ee8289679e01f0e5eaaf70961` | `aa434989b592137543701de2f38d360388983304fcbadbcb467c7ac45eb83af4` |
| boot.img | `cced335b7aae88bcf0b578a1af2a70c9fe9e8cfa58103f9e2d6cf6f53e6f7463` | `65d896e954e871651cf48bf00614154911e440de477e8f9f0ebb7162a03b83f6` |

Boot images are both 169,951,232 bytes; payloads are both 167,772,160 bytes.
The new native/prelink are each 16,384 bytes larger. The new archive reuses
the original `NativeKeyStoreEvents.late.o`; 1006 distinct filelist inputs
were unchanged across the build. This count does not include every direct
archive. Both linked images have zero undefined symbols including weak, one
`aksid` format string, and a disassembled probe call to the identity callback.
All FAT member bytes match r35 except `Payloads/kernel.macho`; the ADT read
back from the final payload is byte-identical to r35. r35 ADT, payload and boot
hashes were unchanged before/after; the inherited r34 native, prelink and
filelist were likewise unchanged. The host check establishes these measured
boundaries, not byte identity of every component of the Android boot header.
A second self-check using `--out ...-r39-selfcheck2` completed with the same
probe-object and archive hashes but a different native and boot hash
(`34de4d75c978fb36d6f87670f670ad1d3ff8aa32468ee970c46e67b174de8cc9`);
output-path effects are not isolated, so full-image reproducibility is unproven.

## Later observations and limits

| Observation after separate authorization | Interpretation |
|---|---|
| `aksid 8` with nonzero prefix | Expected identity path reached; not proof of working keybag. `aksid 0` or 4 indicates a different path. |
| New keybag/keystore logs | Capture exact messages and context; absence alone is not success. |
| SpringBoard service registration | One observation among several, not a single acceptance criterion. |

Changing the prior zero-length identity changes the stand-in key derivation;
historical blobs dependent on an old identity can fail to unwrap. The Data
fixture is scratch; absence of every historical blob is not verified here.
The fallback chip-id is not established to be per-device unique. This is
software identity, not a hardware secret. Runtime property availability,
keybag behavior, GUI, persistence, independent verifier and review remain
unverified. No stage is promoted.
