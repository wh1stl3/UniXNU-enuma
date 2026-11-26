# enuma BootProgress: Legacy service open

Local candidate only, based on HID r2 at `cf29ecd04e9d05cb894a3d4903ec6fc7908e5112`.
The host recipe reuses the actual r6 compiler record and r2 link/prelink/package
inputs and the repository's BSD-2-Clause-Patent host checks at that revision.
It replaces filelist entries 238 (`video_console.o`), 585 (`kern_exec.o`),
and 935 (`IOUserClient.cpo`). It does not replace `IOUserClient.iig.cpo` or any archive.

```sh
/home/wh1stl3/.local/bin/python3.11 \
  <candidate-checkout>/candidates/bootprogress-legacy-open-20261126/build.py \
  --device . out/bootprogress-legacy-open-20261126-verify
```

Run from the active enuma device root under the existing WSL root build
environment; `--device` points to that checkout and its existing `out`.
All generated sources and Apple-derived objects stay under fresh local
`out`; `source.diff`, `commands.json`, final link map and extracted-kernel
disassemblies are there for review.

## Reading the page

- `BB exec for open` is the one attributed generation. Before attribution
  the page can show the independent latest exec and labels it as such.
- `Legacy open` starts immediately before the original five-argument service
  open for the exact `NativeLegacyDisplay` metaclass. It distinguishes
  pending from the raw `newUserClient` return and bounded actual client class
  obtained only on the pre-existing valid-client path.
- `Legacy server final` shows server `err`, out-result and a nonnull bit
  after the original output assignments. It does not prove receipt of a reply.
- `First observed dispatch` is the first successfully observed method for
  the same exec generation and nonzero kernel registry-object ID. It is
  after the existing optional filter and before dispatch. It is not a
  connection ID, dispatch completion, or async completion. Selector 0 and
  absence are distinct. A zero key, no match, contention or an unsampled point
  can leave the result unknown. No arguments, payloads, IPC contents, user
  memory, or object addresses are collected.
- `registered`, `validate`, and `prepare` remain independent sticky
  milestones, not corroboration of one connection. The normal GUI STOP
  path is unchanged, so an earlier frame can be stale; seeing the GUI
  is the observation, not a reason to add another reader.

The page removes MMU/IRQ/PC and framebuffer-address rows, duplicate aggregate
proc/client and refresh rows, GIC/CPU/SMP/clock details, memory/ramdisk,
unneeded UFS telemetry and side panel diagnostics/placeholders. It keeps
boot time/stage, UFS/root error context, eight recent kernel log rows and loss count,
HID event, existing run-state rows and their launchd callback/sampling,
and the minimum display states. Existing exec and display producers, HID
matching/publication, and the 119-column raster path are not changed.

The host fixture uses the r9 proc recorder and r4 page code with a trylock
stand-in. It checks absent, mismatch, busy, exit, saturation, changed
generation, raw/final failure, selector zero, and concurrent one-shot winners,
plus row bounds and stage/run/log sentries. This does not test kernel
scheduling or device behavior.

## Host result (`self-checked`)

- `out/bootprogress-legacy-open-20261126-r4/boot.img`: 169,951,232 B,
  SHA-256 `cd76efaa275bd07f834938d79d833e1d3d8e74eb84eaae1361134c6267a3dbf5`;
  embedded kernel SHA-256
  `1a24a9da79e4936ceb9ee0c5db03fb0867e22aabc15394223598012581c3179f`.
- ASan/UBSan fixture, three object compiles and include guards, link/prelink
  (zero undefined), extracted boot checks, display ABI comparison and
  existing HID, run-state and GUI handoff edges passed. The original and
  candidate each contain one five-argument virtual call at vtable byte
  offset 1120. Original MAC and properties rejection precede claim; the
  original out-argument writes precede final publication.
- All three dispatch probes follow the original success-only filter edge.
  The compiled getter has two loads and no calls, writes or locks. The
  wrapper skips zero keys and compares the live client's ID before calling
  the BSD probe. `record.inc` rechecks current exec generation under the
  existing trylock. This proves emitted edges, not runtime attribution.
- HID r2 boot SHA and all ten active untracked inputs were rechecked. In the
  preparation control, an original-path rebuild and an isolated copy with
  a DWARF path map both reproduced the full-link r6 `IOUserClient.cpo`
  byte-for-byte (`27a8ebd5c1ae6fa793d3e7d586666d9553f3145e2a58ff78750d57fa8e5252db`).
  Android extraction, embedded TOML and unrelated payload members matched.
- Astra design gate: `ses_de808f308ffeXxjMivBd9246Sb`, PASS WITH CONDITIONS.
  No independent final verifier or device run.
- The record gate is scoped to the parent's `cf29ecd` baseline. Comparing
  the parent itself with `origin/feat/step10-ramblock-probe` already fails
  on the inherited `package/EnumaHidStandin.cpp` cellular-area ownership
  record; this candidate does not modify either.
