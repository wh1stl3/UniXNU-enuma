# enuma r35 display-scale host experiment

`self-checked`, host-only; no device access or independent verifier. r35 is
r34 plus the experimental ADT `/chosen/display-scale = 2`. The rationale is
the **reported** nuwa relationship in `docs/display-config-diff-20261123.md`:
its display-scale and artwork-scale-factor match. Enuma's own
`/product/artwork-scale-factor` is 2, so 2 is selected experimentally, not as
a demonstrated hardware or OS requirement.

The change is in `scripts/build-enuma-r35-scale.py` where the script appends
`[adt.chosen.u32]` and `display-scale = 2` to the isolated r34 board copy.
The common generator `UniXNU/scripts/unixnu/devicetree.py:335` consumes the
typed property; neither UniXNU nor the tracked default board is changed.
The script retains the r34 random seed to make the ADT property delta exact.
No XNU object is compiled or linked. The same seed is therefore reused; it is
not newly generated for this candidate.

## Mechanical evidence

Command, in WSL as root with mtools, the existing build inputs and Python 3.11:

```
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin python3 -B scripts/build-enuma-r35-scale.py
/chosen/display-scale = 2
== bootimg
== bootimg: .../out/ufs-sm8250-launchd-scale-20261123-r35/boot.img (169951232 bytes)
kernel.macho.adt 14128 1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457
native.macho 91891824 0352644a06f030608a0889f70f7453eb5fc302fb66a676ae134dc2eb8c2845f0
prelink.macho 124735488 d974059707e07b77504e38d984c4c3bf5a41b6a39fc4931ecfbcb42ed97cb26a
payload.img 167772160 c1c3e97b19be7c765210a93d61edfc3fc52c524ee8289679e01f0e5eaaf70961
boot.img 169951232 cced335b7aae88bcf0b578a1af2a70c9fe9e8cfa58103f9e2d6cf6f53e6f7463
r34 frozen artifacts unchanged; link inputs unchanged: 1011
```

Exit 0. The printed property is parsed from the ADT read **back from final
payload** with `mtype`; the script asserts the raw value is `02000000`.
r34 ADT: 14088 bytes,
`5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5`.
The script compares every decoded ADT property and asserts only the new key
differs, checks all FAT member bytes except ADT, and checks Android boot bytes
outside the payload and 20-byte boot image ID are unchanged. It hashes 1011
unique link inputs before and after and writes the complete path/hash list in
`out/ufs-sm8250-launchd-scale-20261123-r35/r34-link-inputs.sha256`.
It separately snapshots r34 ADT, payload, boot, native, prelink, manifest and
filelist before/after; this is not a full r34 directory snapshot.

The eight r34 objects/archive are directly reused, not copied or recompiled:

```
EnumaLegacyDisplay.o       612b2f98bfd89669066b365391159c6bcba89372f4f0208e5321259b34847101
IOUserClient.cpo           455ebd7abc178922efeb1faed7020b828fa56a300cef023c3639de58dd397568
kern_exec.o                ca1370c29397c93f86ad1399a62dbe1020d419b7a3b485b429896ca0fd61c79d
libEnumaGopLegacy.a        e13468f9555ae40b01a6564caf5cd8237be770d8fe3149860cccbe63220f14e2
mach_msg.o                 2352cd45263853bacf75680ea236397b0dd54b8c3369518362e94053cb42b7fe
NativeLegacyDisplay.late.o 4aeb4c7da1c3a1dd5485c8d97858ecfd5fd50da3d9741d027281de0f859ea33e
NativeLegacyDisplay.o      4d33bee8439a169a48271a6d568d52c9a063b22a1578785d3f879f0ece9b97e7
original-bindings.o        3650732909f83fc31951f9dfea24eae435e89004d7a5c391ee2888f11fad5773
```

The first attempt reached payload readback and packaging but failed at the
capacity check because historical r34 board lacks `boot_partition_bytes`.
It is retained as `...-r35-incomplete`; the final script reads the existing
limit from the current board instead, without changing the package recipe.

## Later device interpretation (not observed)

| Inspect after separately authorized run | Interpretation boundary |
| --- | --- |
| Whether `AXSpringBoardServer` starts registering | Registration alone does not prove a working UI. |
| Whether `enuma-fb` refresh/kick/scanout/swap become nonzero | Nonzero counters indicate activity on the measured paths, not visible pixels. |
| SpringBoard display-related failure logs | Record exact messages; absence is not proof of successful display. |

`display-scale` can change UI layout; if unsuitable it may conflict with artwork.
Runtime effects, actual GUI output, persistence, independent review and verifier
remain unverified. No stage is promoted.
