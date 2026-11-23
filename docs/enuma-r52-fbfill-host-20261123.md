# r52 framebuffer fill — host build, 2026-11-23

Status: self-checked host build; no device operation. Independent verification
and deep concurrency review pending; not approved for deployment.

`vcputc_options` invokes the isolated fill after `VCPUTC_LOCK_LOCK` and before
character drawing. It performs no printing while locked. The existing bp report
prints the global status outside that lock. The locked gate is
`ep_console_can_write(&enuma_pid1_console, gc_enabled)`: its existing logic
requires started, eligible, not revoked, no transitions, and console enabled.
An unset boot argument, closed gate, or zero mapping size does not set done.
Failure and successful completion set done.

The virtual base must be at or above `lastVideoVirt` and its full-width
offset must be less than `lastVideoMapSize`; available bytes equal map size
minus that offset. Only 32 bpp is written. Each row is checked with 64-bit
`y * rowbytes + width * 4 <= avail` before its pixels are written. Bands use
64-bit height multiplication. The diagnostic reports available bytes as
unsigned; the bounds check retains the full `vm_size_t`.

Read back from the produced payload's `unixnu.toml`:

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1
```

| Status | Meaning |
| --- | --- |
| -1 | no attempt; includes disabled argument or closed gate |
| 0 | bad offset, non-32-bit depth, or a row outside the map |
| 1 | all rows written; not proof of visible scanout |

Build: `python3 scripts/build-enuma-r52-fbfill.py --r52`.
`boot.img`: 169951232 bytes, SHA-256
`96b8c8981b2b191af4faa5c75d5bfc49c0287cf42e4184b5ecfef7589d5a2ef2`;
size delta versus r49 zero. Native Mach-O +504 bytes; prelink, payload, ADT
and boot size deltas zero. ADT byte-identical. r49 five packaged input hashes
were unchanged after build. Only `unixnu.toml` and `Payloads/kernel.macho`
changed inside payload. Both Mach-Os have zero undefined symbols including weak;
each contains one new format string. The build checks disassembly for
`vcputc_options` and bp report functions.

Object SHA-256 before -> after:

* `kern_exec.o`: `0aeba58e498ee3d3ea918114658e19c79f6faed30f6f3ceb1a19180fc91f4336` -> `e79ad8237b5aa6b06b74c4aca4a4a5006f0f83a248576962c1acd8d723406c22`
* `video_console.o`: `9394e2950c80eca52f359b41a8b6276e82caf3afbd604aff75e1abd241b6cf02` -> `492123d26e916dd525876cde56c964dd06c8960d511226b378557b78c9f22627`

The other 1004 link-filelist inputs and direct archives were checked unchanged.
Gate eligibility can prevent the test from ever running. Filling the full
framebuffer under the console lock may hold it for a long time; reporting reads
multiple volatile fields without a coherent snapshot. Mapping validity,
alignment, pixel format/channel ordering, scanout, visual result and runtime
behavior remain unverified. The bounds check can fail after earlier rows have
already been written.
