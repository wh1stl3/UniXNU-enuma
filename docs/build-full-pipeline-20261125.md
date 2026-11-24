# Full build pipeline: assembled-source hook gate

Before compiling any assembled stage-2 source tree, compare its hook markers
against the r64 baseline. A plain `xnu-work` checkout is not a valid substitute:
the `package/*.inc` hooks are injected into source files during assembly.

## r64 baseline (2026-11-25)

Baseline: `out/ufs-sm8250-ustack-20261124-r64/source/`

The requested marker grep produced **157 matching lines**. Each baseline
`file:line:matched text` entry is recorded in
[`build-full-pipeline-20261125-hooks-r64.txt`](build-full-pipeline-20261125-hooks-r64.txt).
The search was case-insensitive and used the marker list specified for this
gate (including `ArmCpu`).

## Stage-2 comparison result

**BLOCKED — no assembled stage-2 output tree was present/discoverable in this
workspace at verification time.** Therefore no per-entry comparison was
possible; this is not a pass and does not establish that any hook is missing.
Compilation must not proceed until the assembled tree is identified and every
baseline entry is matched by source file, containing function, and marker
(allow line-number shifts). Require equal counts and zero missing entries.

For each build, regenerate the baseline list from its pinned r64 source tree,
generate the same listing from the completed assembly tree, and compare
semantically by file/function/marker. Stop before compilation on any mismatch;
record hit count, total, and missing entries here or in that build's linked
verification record.
