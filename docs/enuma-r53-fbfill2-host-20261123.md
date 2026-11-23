# r53 small framebuffer blocks — host build, 2026-11-23

Self-checked host build only; no device operation. r52 was rejected by
deep_reviewer for holding the nonpreemptible ticket lock across a full-frame
fill. r53 requires a new deep concurrency review before deployment.

The r52 `vcputc_options` call site, gate and lock order are unchanged. With
the argument enabled and `ep_console_can_write(&enuma_pid1_console,
gc_enabled)` true and a nonzero map, it draws four 256 × 128 rectangles at
x = width / 8 and vertical centers height × (1, 3, 5, 7) / 8. Colors are
white, red, green, blue. Successful total is **131,072 pixel writes**, 3.2%
of the 4,096,000 writes cited for r52, not 1%. Geometry checks reject blocks
outside the screen. Before each block the conservative map check is
`(y0 + 128) * rowbytes + (x0 + 256) * 4 <= avail`, where
`avail = lastVideoMapSize - (base - lastVideoVirt)` after full-width base
and offset checks. Depth other than 32 fails. No new mapping or lock-internal
printing is introduced.

Linear extrapolation of the supplied r52 estimate of 15 ms–1.5 s gives roughly
**0.48–48 ms** for pixel writes; this is not a measurement or a proven upper
bound and excludes fixed overhead and different cache/bus behavior. It can
still be too long for the ticket lock.

| bp report | Meaning |
| --- | --- |
| `st=-1` and `never-gated` | No completed attempt. Gate closed is one cause; disabled argument, unavailable mapping, or no console call are also possible. This line is not proof that the gate alone blocked. |
| `st=0` | Invalid geometry, offset, depth or bounds; earlier blocks can already have been written. |
| `st=1` | All four blocks written, not proof of scanout or visibility. |

The report reads volatile fields independently outside the lock, not as a
coherent snapshot. Mapping validity, alignment, pixel order, visible scanout
and runtime duration are unverified.
The r52 full-frame include is preserved as `EnumaFbFill52Full.inc` for its
historical build script; r53 uses `EnumaFbFill52.inc`.

Read back from the final payload `unixnu.toml` (identical to r52):

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1
```

`boot.img`: 169951232 bytes, SHA-256
`8256c160561ecf427f73c3105b1790915c13df925ccb7c70fe536061e0924137`;
size delta vs r52 zero. Native, prelink, ADT and payload size deltas also zero.
ADT byte-identical; r52 five artifact hashes remained unchanged. Only
`Payloads/kernel.macho` changed in the payload. The other 1004 filelist
inputs and direct archives remained unchanged. Both Mach-Os have zero undefined
symbols including weak, and each has exactly one instance of each diagnostic
format string. Disassembly and source establish the report and console sites;
the compiler may inline the fill.

Object SHA-256 before -> after:

* `kern_exec.o`: `e79ad8237b5aa6b06b74c4aca4a4a5006f0f83a248576962c1acd8d723406c22` -> `601992f74440f8a6f442070f643f386ffe88279dae3d7112bc6c0d30ec20e6f6`
* `video_console.o`: `492123d26e916dd525876cde56c964dd06c8960d511226b378557b78c9f22627` -> `08e6fe1955f0296a3f3ecfec0c5619093b0bbcdf86632241b2d5561c9884f4a9`

Build command: `/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r53-fbfill2.py --r53`.
