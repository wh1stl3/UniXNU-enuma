# Enuma bounded GOP screen diagnostics

Independent diagnostic backend; not linked into the firmware or enabled on a
device. The existing `82ce8a5` evening candidates and their source lock remain
unchanged. This module does not establish GOP, initialize a panel, read MMIO,
collect a memory map, reset the device or call ExitBootServices.

`EnumaScreenInit` accepts a caller-owned scratch buffer and a rectangle within
the current GOP mode. A zero/false write-enable leaves all Blt calls disabled.
An explicit true value is the caller's assertion that the provider, actual
scanout and pixel rectangle were checked; mode metadata alone cannot establish
that. It is not a hardware verification flag or an automatic readiness test.

`EnumaScreenLine` renders bounded ASCII into scratch and submits one
`EfiBltBufferToVideo` call. It never casts or dereferences FrameBufferBase and
does not assume physical pixel format, pitch or cache policy. `PixelBltOnly`
works through the protocol; this does not relax DarwinBoot's separate BGRX32
video contract. Unknown characters become `?`. An empty line explicitly clears
that line; there is no scrolling or whole-screen clearing.

`EnumaScreenHex` preserves all 64 bits, including the EFI error bit.
`EnumaScreenPage` displays a caller-supplied snapshot in twelve rows: header,
build label, stage, EFI status, dimensions/stride/format/base/span, GetMap status
and largest free span. It collects none of these values itself and cannot
certify their origin. Stage codes must be defined by the future caller; the
synthetic preview is not a Dispatcher trace.

The maximum line is 40 columns at 12x28 pixels per cell. Scratch needs 13,440
GOP pixels (53,760 bytes) at that width, owned/allocated by the caller; there is
no large automatic firmware stack buffer or fixed physical storage address.
The caller must provide scratch disjoint from the context, GOP and input text.
Use one context at application TPL before EBS. Busy blocks callback reentry,
not concurrent CPU access. Mode/protocol pointer changes and Blt errors latch
the context closed. A hanging Blt cannot be recovered by this synchronous
module; recovery is the caller's separately tested responsibility.

The font is the hash-locked AOSP BSD-licensed `DiagFont.h` from pinned
DarwinBoot `d099354d0eab34df5088ca1ba89c9c88bc3260bb`. Its two packed six-row
halves are decoded as in DarwinBoot, without reusing its raw framebuffer write
path. The checker stages the complete header and its original copyright/license
under ignored out/. Preserve that notice when distributing an integrated binary.

Run under WSL with the firmware-tools Python:

```text
python -B scripts/check_screen_diagnostics.py
```

The checker validates the pinned Mu archive/font, compiles using real archived
UEFI headers on host (ASan/UBSan) and as an AArch64 COFF object, and produces
`out/screen-diagnostics/host-preview.png`. This is a synthetic preview. It is
not a device screenshot or a complete firmware link. The optimized object
currently imports `memset`; resolve compiler runtime/library dependencies and
verify the full image before integrating.

Before firmware integration, the caller still needs unique GOP/provider
selection, actual display/rectangle evidence, caller-buffer lifetime checks,
explicit disabled-by-default selection, safe fallback and full build/audit.
Keep current SimpleFb metadata/Blt and EnumaProbe early-return guards until
those conditions are met. Never use display/DFPS tails or R-002 RAM as scratch.
GetMemoryMap observations made while drawing cannot be reused as an EBS map key;
the actual loader must obtain its own fresh map at the transition.
