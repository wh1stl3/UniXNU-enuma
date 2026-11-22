# r49 periodic boot progress — host build

Status: **self-checked**, no device run or independent review.
Build: WSL root, `/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r49-bp2.py --r49`,
exit 0; UniXNU HEAD `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.
Output: `out/ufs-sm8250-bp2-20261123-r49/`.

## Mechanism and default-off evidence

The isolated generated `source/bsd/kern/EnumaBbScan.inc:141` calls
`enuma_bp_start()` at the existing one-shot report point. The generated
include is `package/EnumaBootProgress2.inc`. Lines 37–51 parse `enuma-bp`,
return unless it equals 1, print `i=0`, allocate a thread call, then
schedule its first firing. Lines 22–33 print `i=1..10`, reschedule only
when `i<10`, and free the call on the last firing. Each deadline is 60
kernel seconds after the previous report; this does not establish wall
clock duration. Lines 6–19 print 40 newlines and reread time and the four
report helpers for every print. Allocation failure leaves only `i=0`.

Built native disassembly `logs/calls-native.macho.log:816-854` shows
`_PE_parse_boot_argn` at `0xfffffff00bd15284`, the parse-result/value
comparison and `b.ne` at `0xfffffff00bd15294` to the return at
`0xfffffff00bd152e8`, before `_enuma_bp_print`, allocation and
`_thread_call_enter1_delayed` at `0xfffffff00bd152e4`. Thus an absent
argument does not print or enqueue this diagnostic. The prelink disassembly
contains the corresponding calls and unique argument string. The generated
report site calls `_enuma_bp_start` at `0xfffffff00bd137d8`; repeat calls
`_enuma_bp_print` at `0xfffffff00bd154dc`, tests the limit and either
requeues or frees at `0xfffffff00bd1550c/0xfffffff00bd15530`.
Both images contain exactly one `enuma bp r49 i=%u t=%lu\\n` format and
one `enuma-bp` argument string. These addresses are for this build.

## Build evidence

The r48 payload `unixnu.toml` is byte-identical, including both
`enuma-fx-diag=1 enuma-bp=1`. Only `Payloads/kernel.macho` differs among
payload files. The r48-to-r49 link filelist substitutes only `kern_exec.o`;
1005 other filelist inputs, 15 direct archives and the prelink donor were
hashed before and after and remained unchanged. `kern_exec.o` SHA-256:
The unchanged inputs shared with r47's recorded input manifest match its
hashes; r47's two replacement objects match its recorded new hashes
(`ubc_subr.o` `923b0687fda748236efd3e79cd39f4f0b0a8dc3f14dbc5c8c8c39f5b761ab355`,
`vm_fault.o` `245af83fc1cc4b16f36daa86125b634fdd5fff766184cd406dcb359b5670463c`).

* r48: `156e2a3dcda0a516c4f8f17b83bdb6dbcc3363e6d033af712b7ecbf93584417d`
* r49: `0aeba58e498ee3d3ea918114658e19c79f6faed30f6f3ceb1a19180fc91f4336`

| Artifact | r48 SHA-256 | r49 SHA-256 | r49 bytes / delta |
|---|---|---|---|
| kernel.macho.adt | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | same, byte-identical | 14128 / 0 |
| native.macho | `6e31bc9ae1efbe193e3473f78286e6119021d23c0eb11c9fa4fdd68f344db74a` | `da48be65d4521f6e15668f0abc4b80221f40a809a4bec0db98a9d141fcac9fed` | 91912680 / +304 |
| prelink.macho | `caf39743f6e92ed8f39ceac2f1258c992be60b1bd4aebb225a73c5e515b9ccdb` | `92459435089bca227bfb263ec6fdf095e265a689629a3ccb0cdf042a0aa2ce19` | 124755968 / 0 |
| payload.img | `423ad1a9f9f7bcb06ddc05cd9697b624cef78a4801d663ca4898835290737fc1` | `b479be86a41a411d1268e39be2fad113ac201b28c93032ae953d32fc8401feb6` | 167772160 / 0 |
| boot.img | `f0fa42d6330625919bb76827b9fcb2df62cefedfe8c3a84c3d5d098cb39adb2b` | `1180a2c7b2c7f903cf412791a704a3051dbf6335f696f0183896a4c3b1f9d3f5` | 169951232 / 0 |

All five r48 artifact hashes were checked unchanged after the build.
`llvm-nm -u` and raw Mach-O nlist inspection found zero undefined,
including weak, in both r49 Mach-O images. The output manifest contains
the individual input hashes and generated command logs.

## Limits

Repeated reports increase log volume and may affect timing or crowd out
other lines. Actual callback timing, output, counter consistency,
allocation behavior and absence of panic are not device-verified.
The callback lifetime and reused report helpers need deep review;
the build is not deployment authorization or stage acceptance.
