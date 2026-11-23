# enuma r51 receive counter: host investigation

Status: **blocked; static inspection only**. No r51 kernel, build script,
image, or device observation was produced.

## Baseline

The r49 `boot.img` is 169,951,232 bytes, SHA-256
`1180a2c7b2c7f903cf412791a704a3051dbf6335f696f0183896a4c3b1f9d3f5`
(self-checked). The UniXNU checkout HEAD is
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

## Blocking mismatch

The requested trap-entry and trap-exit counts do not establish the requested
blocked-receive state:

* In the r34 source used by the r49 link,
  `out/ufs-sm8250-launchd-ipc-20261123-r34/source/osfmk/ipc/mach_msg.c:938`
  starts `mach_msg2_trap`; it calls `mach_msg_trap_send` at line 1014,
  before `mach_msg_trap_receive` at line 1056. A combined send/receive
  invocation counted at trap entry can still be in the send phase. A failed
  send skips receive (lines 1017–1018).
* `mach_msg_overwrite_trap` is explicitly described as unsupported on
  embedded (lines 825–837); instrumenting it alone does not cover the modern
  entry. Both entries call the receive helper.
* Counts aggregated by PID represent all concurrent threads, not a single
  thread. Independent atomic reads also do not give a simultaneous snapshot.
  Counter wrap or PID reuse would further complicate interpretation.
* Even a helper entry without its matching exit describes an invocation in
  progress, not necessarily a thread sleeping for a message: it can be
  running or blocked in another part of the receive path. Neither hook alone
  identifies the sender or awaited message.

Consequently `enter - exit == 1` cannot be reported as “currently blocked
on a receive”, and `== 0` cannot be reported as a reliable instantaneous
absence of receive activity when sampled independently. No format strings,
gating, runtime behavior, or no-panic property have been implemented or
verified.

## Next decision

Choose whether to accept a weaker **in-flight receive-helper invocation**
metric, with concurrency and snapshot limitations, or specify a reviewed
thread-wait-state observation that can distinguish actual message waiting
from other execution. The latter touches concurrency-sensitive kernel paths
and requires deep review. A new candidate still needs the requested build,
binary and baseline comparisons, record check, independent final validation,
and separate device authorization.
