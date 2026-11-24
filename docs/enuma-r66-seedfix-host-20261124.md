# enuma r66 seed ownership correction: host evidence (2026-11-24)

`self-checked`; no device access, claim, or stage change. r66 reuses r65's
kernel and ADT and substitutes the corrected packed seed only; it is not
evidence of runtime Data ownership or persistence.

The r65 payload was copied, `Payloads/scratch-data.img` replaced with
`out/data-seed-macos-20261119/data.fixed.dbr`, and the r65 `bootimg.build`
chain rebuilt the image. All five r65 artifacts were hashed before and after
and matched r65's manifest. The embedded payload was read back from boot.img;
its SHA-256 matches the standalone payload. The embedded ADT is byte-identical
to r65. `llvm-nm -u` produced no undefined symbols (including weak) in the
reused r65 native and prelinked Mach-O images.

| Payload member | r65 SHA-256 | r66 SHA-256 |
| --- | --- | --- |
| `unixnu.toml` | `c1c89624ed35670f5e5d112d1a01d4e07530799720ef4d448c735fca5286f2b8` | same |
| `Payloads/kernel.macho` | `d0868a4f0146578bbae7397ce4814e999b617ac3a7627fd7fef4d0e012b92db3` | same |
| `Payloads/kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | same |
| `Payloads/kernel.macho.trustcache` | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` | same |
| `Payloads/scratch-data.img` | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` | `baba5f74d442d55301442f3f879518a05f081e04b03dba37aa08209c446087e2` |

r66 `boot.img`: 169,951,232 bytes, SHA-256
`192e1ad3482a3eed9175ad5e1dd7c005b3fea292e443aa234857d6e43c7c49c2`;
size delta from r65 is 0 bytes, r65 SHA-256
`56267f02fab8c3712faeb77436e9d6eaa1e2bcf45bd2387875282ff6d5e56a34`.
r66 payload SHA-256 `01fb6099dbecdddf24232ed6eb6d5450cc469bdf6a7478eb19a4fca1ed144e94`.
Full hashes and before/after inventory are also in the ignored output's
`candidate-manifest.json`.

Read back from the boot image's embedded `unixnu.toml`, byte-identical to r65:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 dk=0 sheng-smp=1 cpus=2 armcpu-diagnostics=1 enuma-bp=1 armcpu-self-ipi=1
```

The packed seed was expanded using upstream `packed_ramdisk.py` `regions()`;
expanded SHA-256 is
`9a4f85a1a1e88b4ef7a1b4728725d86d0e25ff12160a2ddb9412ba2e732c836b`.
Read-only `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3`
mount returned volume root `0:0`, `mobile` `501:501`; unmount exit 0.
