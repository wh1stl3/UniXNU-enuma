# enuma BootProgress 2x host-only candidate

Based on `../bootprogress-upstream-20261126` (sources and provenance documented there). No device operation or authorization. Same source fields and colors; existing field formatting limits are unchanged.

At 1600x2560 the 119-column grid is 1428 pixels wide. Seven original console lines become 24, inserted after the heading; the original 48 rows plus 17 new console rows and eight relocated side rows total 73 rows, 2044 pixels high. Top/left margin zero; right 172 pixels, bottom 516 pixels. Bounding rectangle occupies 71.26% of the screen. Scale is 2 only when 1428x2044 fits; otherwise 1.

The existing nonblocking msgbuf lock copies up to min(ring capacity, 4096) bytes instead of 1024, in at most two memcpy calls, then releases before parsing or painting. Actual ring capacity, lock duration, and available history on device are unknown. A 4096-byte snapshot covers 24 119-character lines plus newlines if those bytes remain in the ring; longer raw lines, ring overwrite, or lock contention can yield fewer complete lines. Existing per-line 119-character clipping is unchanged. No extra lines are fabricated.

`refresh.inc`, writer gate and lease protocol are unchanged. At 2x a changed single cell writes 1344 bytes across 28 row leases; a worst-case all-cells-changed refresh writes 10,901,184 raster bytes, excluding the first full-screen clear of 16,384,000 bytes and barriers. Actual time and bandwidth are not measured. ASan/UBSan tests compare maximal original 48+8 row pixels against 1x, verify padded stride and incremental versus fresh output, and check numbered long/short logs in order; existing r6 host gate/lease tests run unchanged.

Build in WSL as root, from device repository:

```
/home/wh1stl3/.local/bin/python3.11 candidates/bootprogress-upstream-2x-20261126/build.py out/bootprogress-upstream-2x-20261126-r1
```

Self-checked boot.img: 169951232 bytes, SHA-256 `dba0cc40ab8f139d0d3359f5409bafa13d62521c633986d955f6a7aa68f878f9`. Independent verifier and hardware output remain unverified.
