# r46 boot progress: blocked before implementation

Status: only static inspection; no build or device operation.

The requested `fx ... bits` value is `enuma_fx_bits`, declared `static` in
`package/EnumaFixupReport.inc:3` and compiled in `ubc_subr.c`, while the r45
report point is in `kern_exec.c` (`EnumaBbScan.inc`). It is not accessible at
that report point without cross-translation-unit wiring or modifying its
existing report function, both outside the requested two implementation
locations.

No r46 implementation, candidate image, mechanical evidence, or runtime
validation has been produced. The r45 baseline was not modified.
