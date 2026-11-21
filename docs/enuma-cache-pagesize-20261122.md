# enuma cache page size investigation, 2026-11-22

Status: self-checked; offline byte inspection and disassembly only. No build, volume change or device access.

## Cache bytes

In `out/userdata-clean-20261112/044-76034-038.dmg`, candidate header at physical image offset `0x17a6000` starts `dyld_v1   arm64\0`. This raw image candidate is not yet tied to a live cache inode or r14's chosen file.

Structure reference: Apple dyld `include/mach-o/dyld_cache_format.h` on its [main branch](https://github.com/apple-oss-distributions/dyld/blob/main/include/mach-o/dyld_cache_format.h), APSL 2.0; this is a layout reference, not a proven version match to the donor. The magic says cache format v1; `formatVersion` is the low byte at header offset `0xdc`, raw `0x00000000` (formatVersion 0), not a slide-info version. `mappingOffset` at `0x10` is `0x200`, `mappingCount` at `0x14` is 1. Header `mappingWithSlideOffset` at `0x138` is `0x238`, count at `0x13c` is 1. These offsets are within the header area.

The sole legacy mapping at `0x200` has address `0x180000000`, size `0x74000`, fileOffset `0x0`, maxProt/initProt 5/5. All three numbers are divisible by 4096.

The sole 56-byte mapping-and-slide entry at `0x238`, decoded little-endian `<QQQQQQII`, is `(0x180000000, 0x74000, 0x0, 0x0, 0x0, 0x0, 0x5, 0x5)`. Its slideInfoFileOffset and slideInfoFileSize are both zero. The reference mapping-and-slide structure has **no pageSize field**: slide-info versions 2–5 carry a `page_size` at offset +4 of the separate slide-info structure. Here there is no slide-info blob for this mapping, so there is no raw pageSize value to report, not even zero. Header legacy slideInfoOffset/Size at `0x38/0x40` are also zero. Subcache count at `0x18c` is `0x34`; this one text mapping cannot establish page size for other subcaches. Alternative: resolve the actual cache/subcache file extents and identity, then inspect each nonzero slideInfoFileOffset/Size and its version and page_size, checking bounds and physical extent translation. Do not add a cache-relative offset blindly to this DMG header: APFS file extents are not established contiguous.

## r14 binary

`llvm-nm` and `llvm-objdump -d` on `out/ufs-sm8250-launchd-keystore-20261122-r14/self-check/build-final/native.macho` identify `_dyld_pager_data_request` at `0xfffffff00b9bb644`; standalone `_fixup_page` is not present, consistent with inlining. At `0xfffffff00b9bbef0` the code subtracts a segment start from the user address in `w8`; at `0xfffffff00b9bbefc` it loads the shift from `0xfffffff00b75d120`, symbol `_PAGE_SHIFT_CONST`, and at `0xfffffff00b9bbf00` performs `lsr w5, w8, w10` before the bounds comparison and fixup-format dispatch. This indexes using kernel PAGE_SHIFT rather than a slide-info page-size field. At `0xfffffff00b9bb858`–`0xfffffff00b9bb860` the request loop similarly uses `1 << _PAGE_SHIFT_CONST` as its increment. The project identifies this candidate as a 4 KiB kernel; the instruction uses a loaded kernel constant, not an immediate 12. Runtime constant and path execution were not checked here.

`llvm-nm -an` and `strings` searches found no literal `mwli_page_size`. That is only indirect negative evidence: field accesses can be compiled to offsets and names omitted. It does not prove the absence of all equivalent behavior.

## Conclusion

**Missing:** page_size of a real slide-info blob in the cache/subcache actually used by r14, plus its live inode/extent identity. The proposed 16 KiB versus 4 KiB mismatch is neither confirmed nor disproved. The first shared-region mapping being empty and slow user space are not causally explained by this static evidence; a page fixup path also does not by itself establish mapping failure.
