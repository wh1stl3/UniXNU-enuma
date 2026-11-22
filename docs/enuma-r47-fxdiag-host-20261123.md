# r47 diagnostic: blocked at specification conflict

Status: static inspection and hash self-checked; no r47 implementation, build,
device operation, or independent verification.

The requested `slow` counter is defined as calls to `cs_text_fixup_page()`.
In the r46 XNU source `osfmk/vm/vm_fault.c:7805-7806`, however, that call is
short-circuited unless `validated == VMP_CS_ALL_TRUE` and
`tainted == VMP_CS_ALL_FALSE`. It is inside
`vm_page_validate_cs_mapped_slow()` (starting at line 7756). Therefore
`slow=0` does **not** establish that the slow validation path was not entered:
every invocation might have been rejected by either gate. Similarly, `slow>0`
is not a prerequisite for a nonzero taint rejection count. A separate counter
at entry to `vm_page_validate_cs_mapped_slow()` would measure that path;
the requested `slow` would instead measure calls reaching the fixup matcher.
The requested interpretation table cannot be asserted as written.

The matcher in r46 `source/bsd/kern/ubc_subr.c:6217-6227` checks range
before vnode and then bytes. Rejection counts are per entry evaluated, not
independent per-page causes. A page counter after both range and vnode checks
would mean a matching entry was encountered, not that an arbitrary target page
was never reached when earlier validation gates failed.

`package/EnumaFixupReport.inc:8-22` loads counters and prints; it sets no
one-shot flag. `package/EnumaBootProgress.inc:15-19` prints the header, then
match counts, fixup report, process report, and exec report in that order.
The requested two additional gated lines would follow the existing fixup
lines and precede the process report. The supplied 36 + 2 = 38-line budget is
arithmetic only; a target-screen line-capacity basis has not been established.

The current `package/EnumaBootProgress.inc` and the copy in
`out/ufs-sm8250-bp-20261123-r46/source/bsd/kern/EnumaBootProgress.inc`
both hash to `132aafc0a62e162cef6f832bf083cecd4a59ce9d3a6d80ae104013b4308dd720`
(SHA-256). The r46 boot image hashes to
`17170fd082347513d3824053eade802fc0b558ccb4bc18fbafee233e5ce0ac09`.
No r47 image or comparison exists.

Resolution needed: distinguish slow-validation entry from matcher entry in the
counter names and interpretation, and state the actual scope of `page=0`.
All requested counters, formatting, build, final mechanical evidence and
independent verification remain outstanding.
