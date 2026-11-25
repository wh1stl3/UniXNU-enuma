# enuma r69b IPC sampling — 2026-11-25

Status: self-checked; no independent verifier or device observation.

## Defect and change

`enuma_ipc_record()` had a definition but no caller, so the IPC counters
remained zero. The `xnu-work` copy exports the existing recorder and the
`enuma_ipc_s`/`enuma_ipc_r` arrays. `mach_msg.c` now records a successful
send in the shared trap-send helper, and successful receives after
`mach_msg_receive_results(NULL)` on both the immediate and blocked
continuation paths. Failed sends and receives do not increment these hooks.
The two modified files are synchronized to the r64 injection source.
The historical `package/EnumaIpc.inc` was not changed for this fix.

## Host precheck

The first precheck failed because the command metadata contains extra data
after its first JSON object. `JSONDecoder.raw_decode` now reads that object.
The script uses `/usr/bin/llvm-nm`, since system GNU `nm` cannot read Mach-O.
Using the recorded compile arguments, with `XNU_OWNER_DATA_MOUNT=0` for
`kern_exec.c`, both unit compiles returned 0 and emitted zero `error:` lines.
`kern_exec` has `T _enuma_ipc_record` and `S _enuma_ipc_s`/`_enuma_ipc_r`;
`mach_msg` has `U _enuma_ipc_record`. Both source pairs compared identical.
These object checks do not establish final linkage or runtime sampling.

Re-run: `wsl -u root -- bash -lc '/home/wh1stl3/.local/bin/python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/r69c-ipc-backup/precheck.py'`.

## Limits

The three numeric buckets are fixed to PID 1, 5 and 34. If process PIDs differ,
these buckets represent different processes and must not be attributed to the
expected ones. Counts are not a transactional snapshot; no runtime result is
claimed. Final linkage, independent verification and device behavior are untested.
