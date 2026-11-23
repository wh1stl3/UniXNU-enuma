# r54 row-stepped framebuffer diagnostic — 2026-11-23

Self-checked host build only; no device operation. r53 was rejected by
deep_reviewer for the full 131,072-write lock hold. r54 requires its own deep
concurrency review before deployment.

The existing `vcputc_options` site calls `enuma_fb_fill_step` with the console
lock held, before character drawing. Each eligible call writes at most one
256-pixel row; four blocks of 128 rows require 512 calls. Each call recomputes
base, full-width offset, available mapped bytes and geometry. No mapping
pointer is retained; no printing occurs inside the lock.

The existing `ep_console_can_write(&enuma_pid1_console, gc_enabled)` gate
requires started, eligible, not revoked, no transition and enabled.
Closed gate or zero mapping size does not set done; later calls may retry.
Invalid geometry, depth or bounds set failure and done. Only 32 bpp is written.
Besides width and mapping bounds, `(x0 + 256) * 4 <= rowbytes` is required,
which is stricter than checking only the 256-pixel span.

The supplied r52 estimate (15 ms–1.5 s for 4,096,000 pixels) scales linearly
to approximately **0.00094–0.094 ms for 256 writes**. This is not a measurement
or a bound: argument parsing, gate and arithmetic, bus behavior and lock
overhead are excluded. The ≤1 ms budget is not verified.

| `st` / `rows` | Meaning |
| --- | --- |
| `-1 / 0` | No row completed: disabled argument, closed gate, no mapping, or no eligible console call. |
| `-1 / 1..511` | Fill in progress; `-1` alone does not mean unstarted. |
| `0 / 0..511` | Failed; earlier rows may already have been written. |
| `1 / 512` | All rows written over 512 calls; no proof of visible scanout. |

The report samples independently updated volatile fields outside the lock and
is not a coherent snapshot. A mapping or geometry can change between calls:
the gate protects each call, but success does not establish all rows belong
to the same mapping. Character rendering can overwrite earlier rows. Runtime
timing, scanout, alignment, pixel order and visible result remain unverified.

Final payload `unixnu.toml` readback, identical to r53:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1
```

`boot.img`: 169951232 bytes, SHA-256
`c4069bfa4e40fd3f20a497b0e4d15f6126897e9455ee8e1d5a7560d57c7e7504`;
size delta vs r53 zero. Native Mach-O +304 bytes; prelink, ADT and payload
size deltas zero. ADT byte-identical; r53 five artifact hashes unchanged.
Only the payload kernel member changed. Other 1004 link-filelist inputs and
direct archives unchanged. Both Mach-Os have zero undefined symbols including
weak and exactly one new report format string. The copied source has one
console call; disassembly contains `vcputc_options` and bp report functions.

Object SHA-256 before -> after:

* `kern_exec.o`: `601992f74440f8a6f442070f643f386ffe88279dae3d7112bc6c0d30ec20e6f6` -> `33efd3758c7c80458dcdb772a08fdc6638998163c6e66c9caa32e4d1d9ece1f6`
* `video_console.o`: `08e6fe1955f0296a3f3ecfec0c5619093b0bbcdf86632241b2d5561c9884f4a9` -> `66b79b41dd044fe3cdbe5fcf510bccc6bbdf8c8b2b5dfcb440df18939510b264`

Build: `/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r54-fbfill3.py --r54`.
