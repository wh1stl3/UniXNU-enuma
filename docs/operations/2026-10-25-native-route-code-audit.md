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

## S-031 staging classification, source5d2d3d2

Archive `qualified-native-staging-5d2d3d2`, full disassembly digest
`6c7990d755f68a2d9d06d83509106d259f3fb556f1a674ddb48d550dd10d5b1b`.
Core PE remains a27c5b3f2f58ddfd536a9cdeda722d19482cea2f97c4dae7868e60981d9fa69f.
Provider entry and complete capture/resolve/decode/stability flow reviewed:
metadata1118..11a4, three samples122c/2714..2774, two bounded100ms waits1240..127c,
STATUS-before-FRAME131c/132c. Strict staging1498..166c rejects to2890;
selected SSPP1670..176c and mixer1790..19d0 retain prior admission and read counts.
Resolve1a00..1e3c and Decode1e40..2570 retain layout/address/format restrictions.
Stability2574..2804 compares raw configuration and full timing/enable words,
checks active and nonwrapping frame deltas1..64. Success still requires0x14.

New failure classifier2890..2a80 checks major6000 and exactly one video CTL6,
loops six LM and eight known sources, copies four words to stack at2930..294c,
clears only bit24 in that copy at295c. Stage shape29c8..29d0, exact four-word
comparison2a20..2a40, duplicate source2a44..2a50 and final count2ae8..2afc
are bounded RAM-only operations. No callback or MMIO occurs in this classifier;
the only call is pure Stage2d48. Original captured snapshot is not overwritten.
Return2a84..2aa4 requires zero output requirements and Topology status13;
only reasons21..24 map to codes2..5, all others1. Code5 is a rejection here.
Read2dc8..2e20 checks alignment, offset<=0x6c26c and count<330 before the
single MMIO load2e10 from0xae00000+offset; no MMIO store or pixel access added.

Host sanitizers, fixed baseline callback/status/output parity,64 border masks,
768 field perturbations and12480 selector cases passed. These establish bounded
classification, not physical route validity or visible output. Actual image
414edab9053fc9a87c5661665c81b82ca19577877529c4aa0ac4453f62c55701
is bound to ROUTE1/DETAIL1/STAGING1/MASK0/QUERY0 in qualification.

## S-032 native border view, source c45191c

Archive qualified-native-border-c45191c; full disassembly digest
f06cc3c5f791a45221178345cec2699f34c46099dfeec9b1535e92980b0b55c2.
Core PE remains a27c5b3f2f58ddfd536a9cdeda722d19482cea2f97c4dae7868e60981d9fa69f.
Reviewed full entry1050..274c and new helpers28ec..2ce0. Exact R-004 metadata
1118..119c, three samples1224, two100ms waits1240..1278, STATUS-before-FRAME
1324/1334, CTL/raw staging138c..14a8 remain bounded. Normalize14bc precedes
strict select14e4 and selected SSPP reads159c. Raw capture copy15c0..15d4
remains separate from normalized view; second normalize1618 feeds mixer
selection163c..16ec, selected reads1720..17c8, resolve17f0..1c20 and decode
1c24..22f4. No downstream register or framebuffer access added.

Normalize28ec copies0x42c bytes to local stack, loops six CTLs and six layers,
clears only bit24 at2964 in the copy, then strict-select2994; only successful
selection copies output29a4..29b8. Strict selector29d8..2c04 preserves exact
two sources, one active video CTL6, stage1..12, unknown-field and duplicate
rejection. Raw stability2300..2480 compares original sample arrays, including
all CTL layer words at2468. Activity, timing/enable equality and two1..64
nonwrapping frame deltas2508..2594 remain. Success25e0..2620 requires0x14 and
returns5; detail rejection262c..2670 still requires Topology and zero output
requirements. Read2c88 checks aligned offset<=6c26c/count<330 before load2cd0.
No MMIO stores; stack frame0x2440 plus bounded helpers is ordinary RAM only.

Image4bc3fb98f20d1ea7780556652203be17dd02b5c27b5e1e08b029bf1fb3283243
binds ROUTE1/DETAIL1/STAGING0 and native_border_view=true. Host64 border masks,
330 failures and raw-border-change rejection passed. No physical or visible
success is inferred from this review.

## S-033 first layout rejection, source60dd3d9

Archive qualified-native-layout-60dd3d9; full disassembly digest
d9bd1a2dfa6051fa454c375dd93e42430f369e12f9a464274a495fe27409e053.
Core whole bytes equal S-032. Provider helpers Normalize28ec,Select29d8,
Stage2c08,Equal2c5c and Read2c88 retain their addresses and instructions.
Compared complete provider instruction stream against S-032:27 normalized
operand change groups, plus all changed branch destinations, manually reviewed.
Branch normalization is only a navigation aid, not equivalence proof.
Changes outside layout are return-register allocation, shifted labels and the
new selector; metadata bounds, capture order,330-read cap, two100ms waits,
normalized-view separation and raw stability logic retain prior semantics.

Pure resolver checks now branch to first-category labels: dim/blend1a3c,
1a70,1a9c ->26ac (reason26); mode1ac4 ->26f0 (reason27); height/width1af4,
1afc ->26b0 with class3, local geometry1b54/1b70 and total width1bec ->26cc
(reason28); duplicate/missing sides1b14/1b20/1bb4 ->26dc (reason29).
Contract/source-owner failures go26a4 (reason25). No additional data loads or
reads are required for classification. Selector262c..264c requires status13,
zero output requirements and reason26..29, then returns2..5; otherwise1.
Success still carries requirements0x14 but returns unclassified1 in this
diagnostic profile, never the left/right rejection code5.

Imagef6cf178d1dff01b6ace9767d08dbdc7e7d87bb842d29315a152b4d82ccc1982b
binds actual ROUTE1/DETAIL1/LAYOUT1/STAGING0/MASK0/QUERY0 compilation. Fixed
resolver4608 mutations and14880 selector cases support the review; no new
admission, pixel operation, mapping or physical display claim.

## S-034 blend rejection classification, source b915308

Archive qualified-native-blend-b915308; full disassembly digest
2b4053306fc3a82bad907ffd5971c7ff315a27d2faf3bc2fae410a514672cfa2.
Core bytes are identical to S-033. Reviewed 95 normalized operand-change
groups and all unmatched branch targets against S-033; normalization was
only navigation. Register allocation and shifted labels preserve capture,
raw stability, activity/frame checks and existing layout predicates.

Original dim scan 1a28..1a40, operation comparison 1a70..1a74 and alpha
comparison 1a9c..1aa0 alone enter the new pure classifier at 26b8. It calls
strict Select2b50 on the normalized RAM snapshot, bounds six mixers, eight
source stages and eleven captured blend words; stage encoding is 1..12.
Bit16 classification 2770..2790/27f0..2828 distinguishes selected-stage dim
from other-stage dim without treating the latter as inactive. Operation
27a4..27ac still compares 0x100, alpha27c0..27c8 still compares0x00ff0000.
Labels emit reasons31/32/33/34, otherwise30. There are no new MMIO reads,
waits, stores, admission paths or sampling continuation after rejection.

Selector2630..2650 requires zero output requirements, status13 and reasons
31..34 before returning2..5, otherwise1. Successful sampling still requires
0x14 and is not mistaken for alpha rejection. Read2e00..2e58 checks aligned
offset<=0x6c26c and count<330 before the sole MMIO load2e48 at base0xae00000.
Remaining helpers and cold terminal retain prior semantics. Image
bc43b96a4894ac52754442666957d26d5473f350e1721303c9d4e5d80dc37ea1 binds
ROUTE1/DETAIL1/LAYOUT1/BLEND1/STAGING0/MASK0/QUERY0. Host 11x11 dim cases,
four actual sampler branches and17280 selector cases support this review;
no register value or visible display success is inferred.
