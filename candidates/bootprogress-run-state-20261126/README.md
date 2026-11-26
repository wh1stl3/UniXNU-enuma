# Enuma two-instance run state (host candidate)

**Status: `self-checked`, no device operation or verification.** Local review
bundle: `out/bootprogress-run-state-20261126-r9/`. `boot.img` is 169951232 bytes,
SHA-256 `0a7df79d01478eb96ccf5932a3e13891deb8ca886e855a000527491bb25994e0`.

The r5 `exec_mach_imgact` records the TID of `imgp->ip_new_thread` in its
temporary observation only for backboardd/SpringBoard. Both r5 successful
exec predicates and the original exit publisher are unchanged. The existing
recorder spin lock covers the identity, count and TID; its r4 display snapshot
ABI is unchanged. A matching exit is sticky for the same exec identity,
including across re-publication of the same tuple. The last exit is checked
at exec publication as well. Exec counts distinguish publication changes
even when a re-exec reuses the identity tuple.

One dispatch on the **fourth 30-second callback after the launchd report
arm**, under the existing `boot-progress=2` mode. This is not the old tick 2
or a wall-clock deadline. The existing launchd arm is once-only, the
thread-call uses `THREAD_CALL_OPTIONS_ONCE` and the other report returns
before reaching the increment. There is no extra worker, allocation,
polling or retry. The two recorded r5 frames show publication between
roughly 8 and 149 seconds on the screen clock, not whether the pair is
available at report 4. Earlier observations are not captured; a later
publication does not change the result.

The worker copies recorder metadata with try-lock and drops that lock before
any proc/task/thread operation. It looks up the full `proc_ident`, retains
the task while a proc reference is held, and releases the proc before
`task_findtid`/`thread_info`. Zero and current TID are rejected before the
lookup. One `THREAD_BASIC_INFO` per target at most; validate both return and
count. A second identified proc lookup checks shadow, exit, teardown and task
identity, followed by a second recorder snapshot. Result semantics:

- `no-sample:pre:*` rejects the entire pair before Mach sampling (busy,
  incomplete pair, matching exit or saturation).
- `no-sample:post:*` discards the entire pair after attempts (busy, changed
  record, matching exit or saturation).
- `no-sample:target:*` is a failure for one target only, if the recorder
  recheck succeeds. A post or target failure does **not** imply `thread_info`
  was never called.

Once all references are released, the worker writes the two scalar results
and release-publishes one ready flag. Main-page rows 13 and 14 (zero-based)
show `pending` until an acquire read sees that publication, then show the
stable state or reason. The refresh copies before any pixel lease; it does
not query Mach, wait or resample. Each success is the initial exec thread's
scheduling classification at its own sample time, not simultaneous state,
wait ownership, process liveness or whole-service state.

Source reuse: r5 proc-events and r4 display-events (device-repo local artifacts,
hashes in `build.py`; board code BSD-2-Clause-Patent). Kernel APIs are from
XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f` (APSL): `kern_proc.c`
`proc_find_ident`, `vm_unix.c:992–1005`, `task.c:7861–7899` and
`thread_act.c` `thread_info`. Packaging and display gates reuse the existing
candidate recipes and pinned UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

## Review and reproduce

From a WSL root shell in the device repository with the same local inputs:

```sh
/home/wh1stl3/.local/bin/python3.11 \
  candidates/bootprogress-run-state-20261126/build.py \
  "$PWD/out/bootprogress-run-state-20261126-independent"
```

The output directory must not exist. This runs 23 ASan/UBSan cases against
the generated recorder and real sampling/row-formatting logic with stubbed
references. It exercises repeated refresh, both rows, full integer values,
row boundaries, final glyph visibility and pitch padding on the board-size
raster. It recompiles the target exec and video console objects,
relinks/re-prelinks, rebuilds the package and checks the Mach-O extracted
from `boot.img`. No device tools are run.
Review `source.diff`, `commands.json`, `link.filelist`, `native-link.map`,
`run-edge*.log`, `event*.log`, `final-abi.json` and `run-state-verified.json`.
The pinned link drops both `EnumaUserStack64.o` and
`EnumaThreadSnapshot56.o`. The old allocation and submissions are excised.
The r4 display archive, r5 exit object, r4 boot configuration and scanout
gates are reused. The extracted Mach-O shows the single report-4 sampling
edge, single release store, one refresh edge to the leaf acquire reader
before interrupt masking, and all existing proc/display gates. The worker's
release block is shared by early-rejection and sampled paths (including
backward branches from post-validation in the final layout). Independent
review/reproduction and availability by report 4 on-device remain pending.
