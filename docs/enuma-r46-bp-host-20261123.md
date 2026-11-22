# r46 boot progress host build

Status: self-checked host build only; no device test or independent verifier.
The earlier objection to reusing the process report was overly strict.
`enuma_ps_rows` is a temporary buffer refilled from the process list on each
call and used for that report, not a printed/processed flag; no post-print
flag is set in `enuma_ps_dump` (`package/EnumaProcExecReport.inc:26-95`).
Its single-shot assumption is retained: the two calls are sequential in the
same existing callback; no second timer or thread is added.

`package/EnumaBootProgress.inc:4-20` defines the gated report, inserted into
the same `kern_exec.c` translation unit via the replay script
`scripts/build-enuma-r42-matchcnt.py:160-166`. The call follows the original
report and its existing report-done store, before the existing callback frees
itself. The helper parses `enuma-bp` at entry and returns unless its value is
exactly 1. When enabled, its loop calls `printf("\n")` exactly 40 times,
prints `enuma bp r46 t=%lu\n` using the r43 absolute-time conversion, then
calls `enuma_matchcnt_dump(void)`, `enuma_fixup_report(void)`,
`enuma_ps_dump(void)`, and `enuma_ex_dump(void)`. They read and print current
data; the process report also refills its temporary buffer. No one-shot
report flag is changed by those four functions.

No output is suppressed by this addition, and panic behavior is unchanged.
The r45 pre-existing report-done store and its effects are retained. Risk:
additional synchronous console output and a second process census cost time;
the separately read counters and census are not an atomic snapshot. The
report may exceed screen height, and time conversion and visible output have
not been validated on hardware. No framebuffer, panic, timer or thread code
was changed. No device or claim was accessed.

## Mechanical evidence (self-checked)

`/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r42-matchcnt.py --r46`
exited 0; upstream worktree HEAD remained
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`. The captured upstream remote HEAD
was `8542980d02b4d2cc5c32ee3542de1760b2562aac`; pinned base was not changed.

* `kern_exec.o`: r45 `e72d8acb03c6f2b77ac3d23254efd0d70bbefd7ef5e2e84b00d530afde029f7a`;
  r46 `156e2a3dcda0a516c4f8f17b83bdb6dbcc3363e6d033af712b7ecbf93584417d`,
  563040 bytes, +3800. Other 1005 filelist inputs and 15 direct archives
  checked unchanged.
* r45/r46 ADT identical, SHA-256
  `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`.
* r45 `boot.img` unchanged, SHA-256
  `d0e02c1c2ddfcc09f7c922e98b60ae246b6a571fb8c87c8a8403af769b2c34fd`.
  r46: 169951232 bytes, SHA-256
  `17170fd082347513d3824053eade802fc0b558ccb4bc18fbafee233e5ce0ac09`,
  byte-size delta 0. Only `Payloads/kernel.macho` differs within the payload.
* Native Mach-O r45 `b8002c317cb968999e3840ca2be2e5d302b9ec0b2b775162f30f870bd5c28dd4`,
  r46 `75eef9367a39e0485c7e608f2f074b56045d2a6cd90e8f43faa502d07320806c`
  (+136 bytes). Prelink r45
  `cd8cfa207cdabc4c6a4ca7568523035c8d2228e1a36105cea71e63a11dad9735`,
  r46 `201738203fde6af75038db3472c8185043fe4ba70ff7d532bae90d517aaeba5a`
  (size delta 0).
* Both Mach-O images: `llvm-nm -u` empty and raw symbol-table audit found
  zero undefined including weak. New header format appears once in each;
  disassembly confirms one callback call and ordered calls to all four
  report helpers. Full input hashes and call-site results are in local
  `out/ufs-sm8250-bp-20261123-r46/candidate-manifest.json`.
