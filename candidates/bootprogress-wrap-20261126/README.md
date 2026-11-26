# enuma BootProgress 2x wrapped-log and proc-event recipe

Independent candidate derived from `bootprogress-upstream-2x-20261126`.
The 2x font and layout are unchanged; this is not firmware-font alignment.
The title background covers the visible width, not pitch padding. Incremental
updates repaint the extension when the title background changes.

The process-event variant is host-only. r64 `kern_exit.o` was reproduced
byte-for-byte before the r4 candidate was built and checked on the host.
See [the offline record](../../docs/bootprogress-proc-events-20261126.md).
This recipe is not a rebuild instruction for the historical wrapped-log image.

The existing lock and 4096-byte snapshot copy are unchanged. After unlocking,
records are sanitized and wrapped to the framebuffer's visible column count
(at most 119), with `> ` continuation markers. Up to 24 physical rows are
available: complete newest logical records take priority over older ones. If
the newest record alone exceeds the area, its tail is shown with `... ` on
the first visible row; that marker replaces the first four characters of that
row. The snapshot may itself begin in a record; the heading explicitly says
the boundary is a snapshot and ring overwrite is unknown. A snapshot cannot
prove whether the ring overwrote older content. A 4096-byte snapshot also
cannot recover earlier bytes of a longer record.

Build from the device repository under WSL root into a fresh output directory:

```
/home/wh1stl3/.local/bin/python3.11 candidates/bootprogress-wrap-20261126/build.py out/bootprogress-proc-events-20261126-next
```

Self-check covers padded stride, visible-width title including a partial cell,
incremental background repaint versus fresh raster, 40-column wrapping with
errno and UUID across continuation rows, exactly-one-row boundary, oversized
record tail, and priority of a newer complete record. Existing host gate/lease
tests remain part of the build. No device operation or independent verifier.

Rows 24–28 contain the latest per-name exec and prepare-exit records and their
independent saturating counters, or `PROC snapshot busy`. Identity and raw
status are printed as hex. No process enumeration, inferred liveness, event
pairing, respawn detection or claim of user-mode execution.

Firmware menu source uses 8x19 glyphs and automatic portrait scale width/270;
at 1600x2560 and automatic portrait settings that would be 40x95 pixels, but
the actual menu's GOP mode, active layout and effective scale/config need
runtime evidence. The 2x 12x28 page font is not aligned with that menu. A
future optional compact mode could preserve this 2x layout while a separate
menu-sized mode trades diagnostic rows for font size.
