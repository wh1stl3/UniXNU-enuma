# Native route actual-code review

Source fafb8a388837d002a51e7723f643058e74180548; immutable archive
`out/inherited-gop/qualified-native-route-fafb8a3`. Full provider/Core disassembly
digest `cec436953e179a6844bf5827020b12556ceef98090c4347c3bc3d233c62af5a9`.
This review is of packaged instructions, not a hardware execution trace.

- Entry RVA1050..28bc: constructor checks, MDP and Splash descriptor checks at
  1118..11a4. Exact0xae00000/0x85000, device/uncacheable/HOB attributes and
  0x9c000000/0x2400000 preserved. PCD1600x2560 are folded constants.
- Three-sample loop1214, 2694..26d0. Wait1224..1270 executes only after sample0,
  count<=1 before increment, existing gBS Stall100000, failure returns code1.
- Revision load1294 has shared330-read cap1274..128c; major0x6000 checked1298.
  Interface loop12c8..134c covers6b800/6c000. Reads Timing, Enable, STATUS;
  STATUS test1320 precedes FRAME callback1330. No nonzero Timing or exact3 gate.
- Read helper2adc..2b34 checks output, offset<=6c26c, alignment, count<=329
  before increment. Sole helper MMIO load2b24 uses0xae00000+offset; following
  store2b28 targets caller RAM. Other direct display load is revision1294.
- CTL capture138c..14a4 checks six active words, exactly one value6 and video
  top, then24 route words. Selection14a8..1684 retains exactly two distinct
  single-source mixers. SSPP1690..1760 reads11 fields only for selected pipe bits.
- Routed mixer validation17d0..1888 precedes reads18c4..199c: only selected
  two mixers, Mode/Size and11 blend/alpha pairs each. No idle mixer reads.
  Resolve19c0..1e00 retains no-border/unknown staging, no dim, exact non-base
  blend, known mode/right flag, dimensions and local output coverage.
- Decode1e04..2530 is RAM-only: route, mode, geometry/stride, secure/virtual,
  format/unpack, Splash bounds, base agreement and coverage requirements remain.
  Stability2534..2670 compares scope/config;26d4..2754 checks both active,
  full Timing/Enable equality and unsigned nonwrapping increments1..64.
- Success279c..27dc sets Requirements0x14 and copies evidence only on completion,
  then returns5. Failures2758..2798/27e0..2858 map collection/contract1,
  refresh/stability2, topology3, other capture/layout4. No partial output success.
- No pixel access, GOP install, new MMIO store or display-enable operation in
  this provider path. Temporary stack frame0x1bf0 and evidence RAM are not
  framebuffer accesses. Existing assert/deadloop helpers remain as before.

All Core executable sections, including RVAs, are byte-identical to reviewed
S-023 five-code terminal. Whole PE hashes differ; no whole-image equality claim.
CoreDispatcher104a4 calls CoreStartImagec314 and checkpointf90c at104b8 with
point13/status/actual GUID. Unsigned1..5 and both64-bit GUID halves gate
2/7/12/17/22-second delay, PSCI cold reset and deadloop. No dispatcher fallback.
The original review remains in `2026-10-25-native-mask-code-audit.md`.

FD/module extraction verifies these exact provider/Core bytes are packaged;
generated provider and Core compiler flags include ROUTE1/MASK0/QUERY0,
TERMINAL1/FALLBACK0 and exact GUID. R-004 table and full96MiB FAT/Bootv3 match.
Host sanitizers and fixed strict baseline comparisons passed. These establish
code and bounds, not timer availability, guaranteed recovery or visible output.

## S-030 detailed location, source876d151

Archive `qualified-native-route-detail-876d151`, full disassembly digest
`a463b1d681d59c17cf7126f2ae4096d4c2ecd0a6f269faf6da7eb6ba5589687b`.
Core whole PE equals S-029 (SHA256a27c5b3f2f58ddfd536a9cdeda722d19482cea2f97c4dae7868e60981d9fa69f).
Provider register allocation/layout changed; it is not a single-instruction diff.
The new entry and failure branches were reviewed independently:

- Metadata1118..11a4 unchanged in meaning. Three samples1224/2730..2750;
  bounded two100ms waits1238..127c. Revision1294 and STATUS-before-FRAME1320/1330.
  Read helper2ba8..2c00 retains330 cap/alignment/offset and only MMIO load2bf0.
- CTL1384..1494 first failures carry reason14 at2804/2808. Strict staging
  1498..1684 carries reason15 at286c/2870; no source/mixer gates relaxed.
  Selected SSPP read1710..1760 still11 fields; failed read reason16 at28e8.
- Mixer selection17dc..18a4 carries reason17; selected reads18dc..199c still
 24 words per mixer. Resolve19c8..1e24 carries reason18 at2908/290c and retains
  source ownership, dim/alpha/mode, left/right, dimensions and local coverage.
  Decode1e28..2554 is RAM-only, reason19 at2930; original format/address/coverage
  restrictions remain. Stability2558..27d4 retains full config and frame checks.
- Success281c..285c copies evidence with requirements0x14, returns5. Failure
  selector2874..28b8 first requires status13 and output Requirements0; reason14
  returns2,15 returns3,17..19 returns4, all others1. Runtime/collection errors
  cannot masquerade as topology locations. No extra read or wait to classify.

Host fixed fafb8a3 native callback/output parity at all330 failure boundaries,
original strict baseline, three first-location fixtures and10080 detailed
selector cases pass. Actual macros ROUTE1/DETAIL1/MASK0/QUERY0 were verified in
both provider and Core compilation; original complete FAT and R-004 bounds hold.
