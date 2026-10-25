# Native mask field1 actual-code audit

Source `2bb165fa0dd882da1f79b9919435f00f3a4e36d8`; archive `out/inherited-gop/qualified-native-mask-2bb165f-field1`. Full provider and Core disassemblies stay local and are digest-bound in the qualification/code reports.

- Provider `_ModuleEntryPoint` RVA1050..1514 retains constructor checks, validates the exact MDP record and Splash metadata before reads (1110..118c). PCD width/height are compile-time constants from the pinned source/configuration.
- 11ac..11e4 and1468..149c bound and validate initial/final revision. Three-sample loop1220 and two100000us gBS Stall calls1230..126c remain bounded. Read helper1588..160c rejects count>=26 and every offset except revision0, each6b800/6c000 base plus0/a8/ac/26c. Only the accepted address is loaded; stores target local state/output, no MMIO stores.
- 131c..1364 tests STATUS bit0 before FRAME. Inactive clears the active/moving bit. Timing/Enable/Frame comparisons remain independent; no exactEnable3 admission gate. 14d4 loads ActiveThroughoutMask; successful completed observation and mask<4 yield mask+1; metadata/collection failure returns5. No framebuffer access or GOP installation.
- CoreDispatcher104a4 calls CoreStartImage c314, then passes returned status, point13, and the driver's actual GUID to f90c at104b8. The checkpoint rejects NULL, any point other than13, and unsigned statuses outside1..5 atf918..f92c. Full64-bit GUID halves compare against4ffc788ddcfd1e6d and921a65752fca1b8e before delay.
- f974..f984 computes `5000000*status-3000000`, equivalent to2/7/12/17/22 million us for the already-bounded five codes. f988 calls MicroSecondDelay1b7d8; f98c ResetCold16f4; f990 CpuDeadLoop13b8. There is no dispatcher-completion fallback. Compiler retains the ordinary stage gate after CpuDeadLoop; it cannot be reached in normal execution unless a debugger changes the dead-loop sentinel. It does not introduce a second timed automatic return.
- ResetCold16f4..171c passes PSCI SYSTEM_RESET0x84000009 through ArmCallSmc1d990 (SMC at1d9c0). MicroSecondDelay1b7d8..1b854 splits into1-second nanosecond waits; NanoSecondDelay1b738..1b7d4 uses the existing counter loop. This is cold reset, not warm/reset2. The whole Core is newly built and differs from S-010; no whole-Core byte-equivalence claim.

Real-header ASan/UBSan covers504 hook/status/GUID cases,53 mask/error selector cases; prior dispatch-detail suite passed. This audit establishes the packaged implementation and finite requested delays, not execution, timer availability, guaranteed recovery, or visible display. Fixed boot-origin windows and75-second host observation remain separate gates.

## S-024 field4 comparison

`qualified-native-mask-2bb165f-field4` has identical Core PE SHA256 `0d3c9f5b162baf032163d5fc247101c9637b9f4dd83b6928539e99e907f26594`. The full provider executable disassembly differs at exactly RVA14d4: `ldr w9,[x9,#0xda0]` becomes `ldr w9,[x9,#0xdac]`, selecting MovingMask at observation offset0x7c instead of ActiveThroughoutMask at0x70. Every sampling, metadata, bounds, wait and return-code instruction remains identical. Full disassembly digest `948335f72f21276f090a1a6c06699b6aa950715918410faa920131f9163795ee` was reviewed; no inference from build flags alone.

## S-025 field5 comparison

`qualified-native-mask-2bb165f-field5` retains the same Core PE. Full provider disassembly differs from field1 only at RVA14d4: offset0xda0 becomes0xdb0, selecting ExactEnable3Mask at observation offset0x80. Full reviewed disassembly digest `2754c8b673d331aaab680202170a4561c0a325814ee15bfca74ebc9f8639419c`; collection and all other instructions are unchanged. A zero result means neither interface satisfied low-two-bits==3 across all samples, not that the full Enable register was observed to equal0.

## S-026 field6 combined observation

Source9600b19, archive `qualified-native-mask-9600b19-field6`. Core executable sections are byte-identical to reviewed S-023; the whole PE hash differs, so only executable equivalence is asserted. Provider is not a one-instruction variant: its changed entry1050..1544 was independently reviewed.

Metadata1110..118c remains exact. Initial/final revision count guards11ac..11e8 and1468..14a0 reject at count26 or mismatch. Sample loop1218 and wait1224..1274 retain three samples/two100000us stalls. Reads12d8/12fc/1320 fetch Timing/Enable/STATUS; bit0 branch1338 gates FRAME1370. Independent mask updates and frame1..64 checks1388..143c remain bounded; next interface/sample1440..1464. Read helper15b8..163c enforces the same count/offset allowlist and has no MMIO store.

After complete observation copy14a4..14cc, loads14d4/14e4/14f4/1504 select the four masks at0xda0/da4/da8/dac. Each must be<=3; otherwise1510 returns5. AND chain1534..153c and add1 at1540 generate warning1..4. ExactEnable3 at0xdb0 is not part of this conjunction. Failure branches reach1510 without using partial masks. No new read/wait/call/GOP/pixel path.

The helper tail shifts by0x30. Byte comparison differs only at helper offset0x54 (BL to the unchanged CpuPause1038) and0xadc (ADRP encoding crosses a code page but still targets3000); remaining helper bytes equal the original tail. Full reviewed disassembly digest `5822c1c77fca73484b64c6b308fa9cb954c48032f41edd405d62636927528439`. Actual-header tests now cover504 terminal,53 individual and521 combined/error selector cases. Old field2 was built and archived offline only, not issued or consumed.

## S-027 field2 on9600b19

Current-source `qualified-native-mask-9600b19-field2` retains the same Core PE as S-026. Relative to independently reviewed S-023 provider, full executable disassembly differs only at RVA14d4: offset0xda0 becomes0xda4, selecting TimingStableMask at observation offset0x74. Reviewed full disassembly digest `4c4ea0a70b7a3f53a3ee7be2678a3db2968b6f0da58fecda606f30916c537277`. Mask requires every sample nonzero AND equality between windows; rejection alone cannot distinguish zero from changing timing. The older2bb165f field2 remains unissued, distinct from this newly pinned candidate.

## S-028 zero-Timing runtime conjunction

Source5712c00, archive `qualified-native-mask-5712c00-field7`; full reviewed disassembly digest `fdeca59205a792732c61ac82130d422d2a360c92126cd76d733ab34a08dd762c`. Core executable sections remain byte-identical to S-023; whole-PE hash differs. Provider entry1050..1580 was reviewed independently, including exact metadata1110..118c, revision/count bounds11ac..11e8 and1468..14a0, two100000us waits1224..1274, STATUS-before-FRAME1338..1370, three-sample loop1218..1464 and unchanged independent comparisons.

Completed observation copy14a4..14cc precedes three mask loads14d4/14e4/14f4 (ActiveThroughout/EnableStable/Moving), each<=3. AND1524/152c combines them. The bounded2-interface loop153c and3-sample loop1550 read only observation RAM: starting4d34, interface stride0x10, sample stride0x24, stop at0x6c. Any nonzero Timing clears that interface bit;157c returns mask+1. Failures return5 at1500. No extra MMIO, wait, GOP or pixel access.

Read helper15f4..1678 retains26-read cap and exact R-004 offset allowlist, with only a load from accepted MMIO. Helper tail shifts by0x6c; byte differences only at offsets0x54 (BL still CpuPause1038),0xaac and0xadc (ADRP still targets3000 after crossing code-page boundary). Other helper bytes equal S-023. Tests:504 terminal,53 individual,521 combined,525 zero-ready selector cases;48 original collector boundary and257 actual-collector/selector integration cases, ASan/UBSan; collector AArch64 object has no undefined helpers.
