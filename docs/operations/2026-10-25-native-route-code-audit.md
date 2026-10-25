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

## S-035 independent structural observation, source6da0a2a

Full-input archive qualified-native-structure-6da0a2a; disassembly digest
7d79b07ffb4df20947df75eedf0dcee1ad1311c77eb01a02e77e4e55b350086d.
Image a27d52effd2126e1e444babf5b3ce91fe8b581d83eb72bf189c7291e8c690f95;
FD959b7e6a82785fabb242236d6b753766b64cd0298d8cb372d8ec7843728aaea8.
Core SHAa27c5b3f2f58ddfd536a9cdeda722d19482cea2f97c4dae7868e60981d9fa69f
is unchanged. An earlier RAM_PAYLOAD0 offline build was discarded before
packaging/qualification; only rebuilt RAM_PAYLOAD1 is this candidate.

Reviewed complete entry1050..2664 and pure route/normalization/result/read
helpers2804..2c70. Metadata112c..1194 binds exact R-004 MDP type/attributes and
Splash base/size. Entry1218 bounds three samples; wait1228..1264 bounds two
100000us calls. Revision read1268..1290 and all remaining Read2c18 calls retain
count<330, aligned offset<=0x6c26c before the sole load2c60 at0xae00000.
STATUS130c gates FRAME1320. Six CTLs and selected source/mixer capture remain
bounded1374..17d0. Normalize2804 copies RAM, clears onlybit24 at287c and strict
selects28ac before exposing the copy; raw arrays remain separately saved.

Structural geometry17f8..1b90 preserves revision, exact single video CTL6,
known single source/stage/owner, height2560, nonzero width, bit31 left/right,
source fills local mixer and total1600 width. Blend/dim/other Mode tests are
deliberately absent from this narrower diagnostic; no replacement values are
written. Decoder1b94..2268 retains geometry/secure/multirect/RGBX0x236ff,
opmode/unpack, address containment, common base/stride/pattern and coverage
checks. Raw stability2274..23f0 compares mixer0x240 bytes, source words,
scope/revision and raw CTL staging. Interface2460..24e8 requires both active,
complete Timing/Enable equality and nonwrapping frame delta1..64 per window.

Only all three successful samples reach2540: writes requirements0x16=22
before evidence copy, then complete reason12. Selector2ba0..2c14 admits
structural code5 only status0/reason12/requirements22. Failures preserve empty
output; native reasons14..19 become pipeline8 for existing five categories.
Old selectors still reject requirements22 as a complete blend-qualified
candidate. ASan/UBSan330 failures/two waits/raw blend mutation/stalled frame,
768 geometry/side perturbations and17280 structural selector cases passed.
Actual RAM_PAYLOAD1/STRUCTURE1/ROUTE1 and DETAIL/STAGING/LAYOUT/BLEND/MASK/QUERY0
are checked in both generated compilation files and the full packaged image.
No GOP publication, pixel access, MMIO store, new mapping or composition claim.

## S-036 stability-first geometry detail, source7ea366f

Archive qualified-native-geometry-7ea366f; combined disassembly digest
2672dcc9f19ecd6fe67d9d3c8dbbcee8d5f6f2760f24850fccdadf65c4bd7a61.
Image b6193cc5d757f3cfe9a9dbbc3761ce15dd279018038208e34e50d433533eb9b8;
FD fbe01654c0b1f51f1a15552f828fab609e67e14c4d48252ec4c761165277c030.
Core whole bytes match S-035. Staged/RowCovered/Normalize/Select/Stage/Equal
instructions26d8..2ba0 in S-035 match this provider2840..2d08 exactly after
the0x168 relocation of internal branch targets; no operand differences.

Manually reviewed entry1050..27cc. Exact R-004 metadata1124..1190, three
sample loop11fc, two100000us waits1208..124c and STATUS-before-FRAME12f0..130c
retain bounds. CTL1364..13e8, staging1414..14ec, selected SSPP14f8..159c and
selected mixer1734..17e4 preserve capture preconditions and register kinds.
Raw snapshots saved15c8/1818, then configuration1830..1994 compares complete
scope/revision/pipes/mixer0x240 bytes/CTL top-active-staging;19a8..1a18 checks
both interfaces active, full Timing/Enable equality and frame deltas1..64.
Only after all three iterations does1a90 normalize sample0 and run geometry.
Any collection/wait/raw change/frame failure returns before classification.

Geometry1ab8..1e38 retains source/stage/owner/height/width/bit31/local fill/
total width checks. On rejection1e3c..1e78 strict-selects again and classifier
1ec8..2010 reads only retained sample0 words: six mixer/eight source loops,
size1f34..1f50 ->reason36, duplicate/missing sides1f64..1f7c/1fb0 ->reason38,
source OutXy/OutSize1f80..1f9c ->reason37, total width1fe0..200c ->reason39;
other cases reason35. No new hardware reads or synthetic mixer values.
Selector1e80..1ea0 requires status13/zero requirements/reasons36..39 before
code2..5, otherwise1. Decoder2014..278c retains original source/format/secure/
address/coverage predicates. Complete2790..27c4 writes requirements22 and
reason12, which remains unclassified1 in this geometry-only transport.

Read2d08..2d60 limits aligned offset<=0x6c26c/count<330 before sole load2d50
at0xae00000; revision126c has the same count cap1250..1264. Stack0x22e0 plus
bounded existing helpers; no pixel access, MMIO stores, new map or GOP install.
Full FAT/RAM_PAYLOAD1, STRUCTURE1/STRUCTURE_DETAIL1/ROUTE1 and remaining
detail/layout/blend/staging/mask/query0 compilation is bound to packaged PE.
ASan/UBSan330 failed reads/two waits/raw mutation and frame failure priority,
768 classifier/resolver perturbations and19680 geometry selector cases pass.
Code2..5 implies stable captured configuration/two moving windows, never a
numeric register dump, physical panel route or visual composition proof.

## S-037 exact global-output view, sourceb37e2cc

Archive qualified-native-global-output-b37e2cc-v2; disassembly digest
dcf9a11f9397eeb333a32f52b3d7ff960423bc155aaac998a2c6549effb1c2b4.
Image2d860389875dc054be30dc5c04575f903a85b1ab509cd6c0c196ab0483b4e51a;
FDd0fb82f054ac31f06f6b3b7483b5045f0e4c26daaca784372125be63599561ca.
Core bytes unchanged. Staged/RowCovered/Normalize/Select/Stage old S-036
2840..2cdc match new2598..2a34 exactly after internal branch relocation
-0x2a8. Equal2dd8..2e00 was separately reviewed. The first archive attempt
stopped before qualification because Evidence.h host-test binding was stale;
terminal tests were rerun and only this v2 complete archive is qualified.

Reviewed entire entry1050..2524, geometry helper2a34..2dd4, selector2e04..2e78
and Read2e7c..2ed4. Metadata1130..1198 binds R-004 MDP/Splash. Three sample
loop1220, two100000us waits122c..1270, count cap1274..1288 before revision1290
and STATUS1314 before FRAME1328 preserve bounds. Safe CTL1388..140c,
staging1438..1504, selected SSPP1510..15b4 and mixer1748..17f8 capture gates
remain. Raw source/mixer words are saved15e0/182c. Configuration1844..19a8
compares all source/mixer/CTL staging words; interface19bc..1a2c checks both
active, full Timing/Enable equality and nonwrapping frame delta1..64. Only
three successful iterations reach sample0 geometry analysis1ab4.

Exact global model1ae4..1ce4 checks revision/video/nonzero panel, strict route,
six mixers/eight source bounds, each source OutSize==LM Size, full panel
height/nonzero widths, unique bit31 left/right, total width, left OutXy0 and
right OutXy==left width (no Y bits). Any mismatch returns topology at1b28.
Copy1ce8..1d04 is ordinary stack RAM; only right Pipe.OutXy is cleared1d28.
Geometry2a34 is called1d2c before exposing the view, and again1d64 on the
analysis copy. It retains full route/owner/local-fill/size/sides/total checks.
No raw snapshot, blend/alpha, source address, format or stride is changed.

Decoder1d6c..24e4 retains secure/multirect/RGBX0x236ff/opmode/unpack,
geometry/stride/address containment/shared base-pattern and coverage checks.
Complete24e8..251c writes requirements22 before evidence copy. Selector2e04
admits code5 only status0/reason12/requirements22; native pipeline reasons
14..19 map to8, with topology3 versus other decode4. Read2e7c checks aligned
offset<=0x6c26c/count<330 before sole MMIO load2ec4 at0xae00000.
Stack0x2330 plus bounded existing helpers, no new map/GOP/pixel/MMIO store.
RAM_PAYLOAD1/ROUTE1/STRUCTURE1/GLOBAL_OUTPUT1 and STRUCTURE_DETAIL/old detail/
staging/layout/blend/mask/query0 are bound to both actual compile files.
Sanitizer330 failures/two waits/raw XY changes,768 mixer/128 source-output
mutations and old sampler rejection support review. Stable logical coordinate
view retains blend/address/downstream obligations and is not visible output.
