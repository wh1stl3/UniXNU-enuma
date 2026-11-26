# enuma BootProgress: Legacy display discovery and open

## Display-chain extension of Legacy open r4

This is a separate local diagnostic based on the r4 bytes pinned below. It
preserves the r4 open/dispatch capture and GUI STOP. Three more page rows show
the current attributed BB exec generation and:

1. **DT inline paths:** nonnull or empty server returns for the literal
   `IODeviceTree:/arm-io` and `IODeviceTree:/arm-io/enuma-gop-display`.
   The latter is the enuma nub name, set before attaching to `/arm-io` in
   the frozen display source `package/EnumaLegacyDisplay.cpp:95–105`.
   Both `is_io_registry_entry_from_path` and the inline branch of
   `is_io_registry_entry_from_path_ool` are covered. The former can return a
   compatibility match; the nonnull bit alone does not prove object identity.
   This is **direct query coverage** only, not DT child-iterator coverage,
   a `Ref_FB` observation, a private property lookup, or client receipt.
   Other path spellings, mapped OOL path bytes and generic DT iterator results
   are explicitly uncovered. On the pinned XNU, `getName(plane)` takes a
   registry lock and returns a registry-owned name after unlocking, so this
   candidate does not add name reads to generic iterator returns.
2. **First-match vs. returned service:** the actual server result from
   `internal_io_service_add_notification` for the first-match symbol and exact
   `IOProviderClass=IOMobileFramebuffer` in its already parsed dictionary.
   This covers the binary inline and mapped wrappers after their original
   checks/parser; it does not read serialized matching or wake references.
   Separately, the successful `is_io_iterator_next` out-object is observed
   only when its exact class is `NativeLegacyDisplay`. Empty and other-object
   iterator results cannot identify a target registration, and are not counted.
   There is no safe iterator key in this scope: registration/return pairing
   and user-space receipt remain unknown.
3. **Early open vs. sample loss:** only the existing MAC and unsupported
   properties early returns after a valid service and owning task are covered.
   Bad service/task inputs are not classified as board-service rejections.
   The optional `same`/`different` comparison is between the two live
   objects' registry IDs previously sampled in this BB generation. Zero is
   unknown. The IDs are not displayed; equality is kernel object identity,
   not an iterator registration, a userspace request pair or a connection.
   Lock-loss bits are sticky across the boot, not attributed to BB and
   never stored as a rejection or stage event. In the recorder, wrong task,
   unmatched identity, matched exit and saturated generation reject attribution.

Each cell retains first positive evidence where available; before it, it may
show the first failed/empty observation. Generation is checked under the
existing trylock at each sample point; the r4 one-shot open may still show a
separately labeled older generation. The new rows displace only the three
stage-history rows to a later part of the same page; current stage, original
display, HID, run-state and log rows remain.

From the active enuma root in WSL, rerun:

```sh
/home/wh1stl3/.local/bin/python3.11 \
  out/bootprogress-display-chain-20261126-src/candidates/bootprogress-legacy-open-20261126/build.py \
  --device . out/bootprogress-display-chain-20261126-verify
```

The recipe
asserts that its r4 generator inputs reproduce the pinned r4 IOKit and sample
sources, then generates the bounded overlay and checks the final extracted
edges. `source.diff` is for generated units; the code and page include changes
are in the local commit.

Host result (`self-checked`), `out/bootprogress-display-chain-20261126-r2/`:

- `boot.img`: 169,951,232 B; SHA-256
  `6533f27e784037cd479d905dff5d732ad01e0398770b90a7ecf59006fe3533af`;
  `boot_b` budget 201,326,592 B, remaining 31,375,360 B.
- Extracted `embedded-kernel.macho`: SHA-256
  `bc6d2d39d5bd119c5cc89623260a8f774c64251d1ab4fdb05daca0f9b5bc9d0f`.
  Source/commands hashes and package details are available in the output;
  `source.diff` SHA-256 is
  `8922a51445b9ed883a56faefd44040260fb98bfe3c4120c21b9ae6ad68873b5a`.
  `r4-to-chain-generated.diff` isolates the two generated files that differ
  from r4 (`IOUserClient.cpp` and `sample.inc`); the other eight generated
  files, embedded config and payload member list matched r4 byte-for-byte.
- ASan/UBSan host recorder/page fixture: empty and successful DT, failed
  and successful registration, other identities/IDs, original rejection,
  unattributed contention, replacement generation, overflow, and inherited
  r4 one-shot/client/dispatch cases. This exercises the recorder and page,
  not running IOKit or device scheduling.
- Extracted-kernel logs cover both DT RPCs (OOL excludes the mapped path),
  the notifier's success/unsupported branches, the iterator's actual returned
  object, and both original early-open branches feeding the shared recorder
  edge. Inherited r4 dispatch/filter, display ABI/GUI STOP, HID/run-state,
  three-object link map, zero undefined and extracted boot/payload checks passed.
  Boot config and pinned r4 artifacts plus the ten active untracked inputs
  were rechecked. No device run or independent verifier.

## Legacy open r4 baseline

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
