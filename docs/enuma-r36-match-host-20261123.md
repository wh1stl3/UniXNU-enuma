# enuma r36 matching counters — host only

`self-checked`; no device run or independent verification. Deep review of
the new concurrent atomic instrumentation is required before deployment.
Based on r34, with the original osfmk command JSON and ADT injection replayed.
UniXNU local HEAD `693f5d9cae8a408dd18b39f3f9fdc4228c934241`;
device origin HEAD observed `74dc21dd5c323a763a225f98a6eefc3815272046`
before and after build.

## Scope and semantics

The instrumented xnu-10063 MIG server routines (r34 source line numbers,
`source/iokit/Kernel/IOUserClient.cpp`) are:

* `2745`, `2773`: get matching services OOL and binary;
* `2828`, `2856`: get matching service OOL and binary;
* `2992`, `3018`, `3076`, `3102`: notification binary/64 and OOL/64.

The unsupported legacy string routines at `2735`, `2818`, `2964` and `2978`
return unsupported directly and are excluded. Existing-service property-table
tests and any other mechanisms are not covered. Counters record requests at
entry, including invalid arguments; successful return counts use the returned
status, and for OOL routines require both transport and `*result` success.
They do not change either status. OOL copy failures and notification argument
rejections are counted as requests, not successes.

No class names are recorded: the requested simplified scheme omits the
concurrent bounded name table. Global and exact-comm counters are relaxed
atomics sampled separately; ongoing calls and independently sampled values
mean a dump is not a transaction. PID identity and comm synchronization are
not established. The existing r34 timer governs 30-second, at-most-20 dumps:

```
enuma-match: begin all=<n> bb=<n> sb=<n> ok=<all_ok>/<bb_ok>/<sb_ok>
enuma-match: end
```

| Observation | Bounded interpretation |
| --- | --- |
| bb > 0, bb_ok = 0 | Requests entered; none has returned success by the sampled time. In-flight calls may remain. |
| bb > 0, bb_ok > 0 | At least one call returned success. This does **not** prove a service was found or that the same process did not open one: a successful iterator can be empty, and notification registration can succeed before a match. |
| bb = 0 | No backboardd call was observed on these eight entries by the sampled time; other entry paths are not excluded. |

Neither request nor return counts identify a class or establish an actual
matching service. A future diagnostic can observe the iterator results or
single-service results, with a separate review of the instrumentation.

## Build and mechanical evidence

`PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r36-match.py --dtb /root/enuma-step10/inputs/enuma.dtb` exited 0.
The initial compile failed in generated `IOUserClient.cpp:2769`: the
return-rewriter matched a comment. The rewriter was corrected and the failed
output retained separately as `out/ufs-sm8250-launchd-match-20261123-r36-compile-failed/`.

Link completed before prelink; native and prelink undefined checks including
weak symbols were empty. The build checks both new formats once per binary,
and retained r34 `enuma-ipc`, `enuma-att`, and `enuma-ctl` formats. Eight
generated entry hooks and their success checks were inspected in source.
Full build evidence and binary format checks are in the candidate manifest.

| Artifact | bytes | SHA-256 |
| --- | ---: | --- |
| boot.img | 169951232 | a9eacf8558079df90d8e1377106e0936a4c151f8745064b23dfbc3cd672f678f |
| native.macho | 91892080 | 3fe3642174f00243ba8ffa632732d2f73ac0125bf40f1db0643cdfda48caf26b |
| prelink.macho | 124735488 | 1013c0e827c89c1085e51327ffd79c24798da51b178386df7b9f870f79080913 |
| IOUserClient.cpo | 707376 | 82b26c9e65790e1bae5fbdfa599c0dd8ddbc9ca162126b41ab0326a2b0b7262d |
| kern_exec.o | 524288 | 7f07506508035428bab623f6b91bfeea00a4e2dc24e26f372e3c7c490e51748a |
| mach_msg.o | 106320 | f214e3ada7f235d09c6adf419e83969ccd22cd96a3c8cbf5eb85ce7e8354381e |

No device behavior, actual matches, runtime cost, timing, safety under
concurrency, or GUI progress is established.
