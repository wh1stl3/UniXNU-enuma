# enuma dyld cache layout: offline investigation

Status: **self-checked; target layout and rejection hypothesis undetermined**.
No device access, downloads, IPSW extraction, or volume modifications.

Recursive filename searches of this device repository's `out/` and `.cache/`
found no extracted `dyld_shared_cache_arm64` or numbered sibling. The
read-only input `out/userdata-clean-20261112/044-76034-038.dmg` is an APFS
image of 3,303,014,400 bytes. A raw byte scan found the target filename and
numbered names including `.01` and `.52`, so the image contains evidence of a
split cache; the directory records have not been resolved to a complete live
file set, and the aggregate size is unknown.

The scan also found plausible arm64 cache headers on APFS block boundaries.
For example, image offset `0x17a6000` has magic `dyld_v1   arm64\0`,
mappingOffset `0x200`, mappingCount 1, and a mapping at header offset `0x200`:
address `0x180000000`, size `0x74000`, fileOffset `0`, maxProt `5`, initProt
`5`. A second plausible header at image offset `0x181e000` has mappingOffset
`0x200`, mappingCount 1 and mapping address `0x180074000`, size `0x6d30000`,
fileOffset `0`, maxProt `5`, initProt `5`. Both addresses and sizes are
16 KiB aligned, hence also 4 KiB aligned. These are raw candidate headers:
the APFS inode-to-extent mapping was not resolved, so neither is proven to
belong to the target live pathname, and their logical file sizes, platform,
and version fields are not established. No complete target file bytes were
obtained. Raw matches can include stale or unrelated APFS objects.

The official `UniXNU/docs/zh/xnu/four-k-page-tables.md:80` states the 4 KiB
userspace layout requirement. However, divisibility by `0x4000` alone does not
show incompatibility with 4 KiB: every `0x4000` multiple is `0x1000` aligned.
Even established mapping alignment alone would not prove the cache's page
semantics or that a particular runtime mapping was rejected. The hypothesis
that a 16 KiB cache caused empty `sr_first_mapping` and slow userspace is
therefore neither proven nor disproven here.

Search method: WSL `find` over both directories, followed by a read-only
Python `mmap` scan of the entire image for arm64 cache magic and filenames;
mapping fields decoded little-endian from plausible aligned headers. No APFS
inode/extent traversal or target-side mapping failure was verified.
