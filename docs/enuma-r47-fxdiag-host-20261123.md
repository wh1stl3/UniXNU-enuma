# r47 fixup diagnostic host build

Status: self-checked host build; no device run or independent verification.
This isolated r47 replay retains r46 and adds diagnostic counts only. No
signature decision, return value, applied count, or hit bitmap was changed.

## Counters and limitations

Locations are in `out/ufs-sm8250-fxdiag-20261123-r47/source/`:

* `osfmk/vm/vm_fault.c:7768` `sv`: entry to slow mapped-page validation.
* `bsd/kern/ubc_subr.c:6219` `fx`: entry to the fixup matcher after gates.
* `vm_fault.c:7808-7810` `taint` and `novalid`: independent failed validation
  predicates. `nx` counts nonzero NX returned by validation, **not an NX
  rejection**: the existing fixup call has no NX gate.
* `ubc_subr.c:6224,6228,6234`: `range`, `vnode`, `bytes`, respectively, count
  rejected entries. Checks are ordered range, vnode, bytes; counts are not
  independent per-page diagnoses.
* `ubc_subr.c:6231` `page`: entries whose offset falls in the page and whose
  vnode name matches, regardless of the byte comparison. Multiple entries can
  increment it for one page. It is not a unique page count.
* `fast` omitted: the format has no fast counter; `sv=0` cannot distinguish
  a fast return from no validation request.

`cs_text_fixup_init` parses `enuma-fx-diag` at `ubc_subr.c:6167-6171`; only
value 1 enables increments and reporting. The counters use relaxed atomics;
disabled operation still pays a conditional load/branch but performs no
counter atomics or diagnostic printing. The r47 ADT is identical to r46, so
this image's existing boot arguments do not themselves enable the diagnostic.
No lock, allocation, or new hot-path print is added. The existing report
calls `enuma_fxd_report()` at `EnumaFixupReport.inc:23`; format strings:

```
enuma-fxd: sv=%u fx=%u taint=%u novalid=%u nx=%u\n
enuma-fxd: vnode=%u range=%u bytes=%u page=%u\n
```

`enuma_fixup_report()` has no one-shot flag. bp order is header, match,
fixup including fxd, process, exec; `EnumaBootProgress.inc` is unchanged.
Its package and r46/r47 source copies have SHA-256
`132aafc0a62e162cef6f832bf083cecd4a59ce9d3a6d80ae104013b4308dd720`.
The planned 36+2=38 lines excludes interleaved output and wrapping. The old
DarwinBoot record (README) gives 1600x2560 but current console font scaling
and usable geometry are not established: target visible row capacity is
**unconfirmed**.

## Interpretation, only while enabled

| Observation | Interpretation |
| --- | --- |
| `sv=0` | No slow validation counted since enablement; fast return or no validation request cannot be distinguished. |
| `sv>0 && fx=0` | Slow validation entered but no matcher call counted; completed calls may have failed `taint`/`novalid`. Check those counters. |
| `fx>0 && applied=0 && (vnode+range+bytes)>0` | Some matcher entries were rejected; the aggregate does not identify which target entry. |
| `fx>0 && page=0` | No target entry matched both vnode and page offset at the matcher; this does not establish whether a target page reached validation and was rejected by its gates. |

Reports read independent relaxed counters while activity continues: an
in-flight slow call can increment `sv` before any gate result, and a snapshot
is not atomic. Counter wrap and calls before startup enablement are not
distinguished. Execution time, console wrapping, screen capacity, and
hardware behavior remain unverified; the gate load has nonzero cost.

## Mechanical evidence (self-checked)

`/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r42-matchcnt.py --r47`
completed exit 0. The first compile attempt failed because the boot argument
declaration header was missing; the include was added before the successful
rebuild. Base HEAD before and after is `693f5d9cae8a408dd18b39f3f9fdc4228c934241`;
upstream remote HEAD after build `8542980d02b4d2cc5c32ee3542de1760b2562aac`.

* `ubc_subr.o`: `1b510846e44bf7136011c52b23801fe77f6b1302f1affacded28de3c2ca3f930`
  → `923b0687fda748236efd3e79cd39f4f0b0a8dc3f14dbc5c8c8c39f5b761ab355`;
  `vm_fault.o`: `fa67a5d3ffbb9811331a37af91f23d5da048f390ac68b17a3bec8e0204c462c9`
  → `245af83fc1cc4b16f36daa86125b634fdd5fff766184cd406dcb359b5670463c`.
  The remaining 1004 link-file inputs and 15 direct archives were unchanged.
* ADT byte-identical to r46: SHA-256
  `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`.
  r46 boot image unchanged:
  `17170fd082347513d3824053eade802fc0b558ccb4bc18fbafee233e5ce0ac09`.
* r47 `boot.img`: 169951232 bytes, delta 0, SHA-256
  `e1b6a49959aff7d6aa094d3ce47ce061f9621a9f057551ae185b81c4dbfade83`.
  Payload differs only in `Payloads/kernel.macho`.
* Native Mach-O `6e31bc9ae1efbe193e3473f78286e6119021d23c0eb11c9fa4fdd68f344db74a`
  (+632 bytes); prelink `caf39743f6e92ed8f39ceac2f1258c992be60b1bd4aebb225a73c5e515b9ccdb`
  (size delta 0). Both have zero undefined symbols including weak, both new
  strings occur once per image, and disassembly checks report call ordering.
  Full input hashes are in the local candidate manifest.
