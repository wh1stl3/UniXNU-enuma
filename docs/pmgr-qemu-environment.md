# Bounded QEMU tool discovery (2026-11-10, self-checked)

**Latest (self-checked): the explicitly approved single Range recovery and official
signature verification succeeded; isolated QEMU9.2.0 is installed and enumerates
cortex-a710. Real mode1 guest stops in original AppleImage4 before the PMGR hook;
all16 PMGR fields are actually zero. Modes2/3 and faults were not repeated across
that shared prerequisite. Runtime/device acceptance remains false. See the final
section below; earlier failed preparation/discovery entries are historical.**

Read-only discovery only: no guest rerun, downloads, installs, system packages,
shared WSL configuration, base edits or nuwa assets. 23r verifier evidence and
candidate contents were not changed by this discovery.

## Actual interface and installed tools

- Base `scripts/qemu-entry/gdb-stop.py:348–352` executes the literal program name
  `qemu-system-aarch64` via subprocess/PATH; TCG CPU is fixed to `cortex-a710` at
  line349. It has no CPU-selector option. HVF is macOS ARM64-only, not an escape
  for this Windows/x86_64 WSL environment. Do not substitute a57/max/another CPU.
- Firmware is selectable with the existing `--firmware` child CLI. Existing
  `/usr/share/AAVMF/AAVMF_CODE.fd` satisfies that input; the default
  `/usr/share/qemu/edk2-aarch64-code.fd` is absent.
- Existing device QEMU wrapper sets its own PATH, so merely prefixing the outer
  shell PATH does **not** select a new QEMU through that wrapper. A future run can
  invoke the already prepared isolated unchanged base probe directly with an
  explicit per-process PATH (the isolated child forwarding wrapper already adds
  the existing AAVMF parameter). No base or global PATH modification is needed.
- Only installed WSL distribution is Ubuntu-22.04. `type -a` finds `/usr/bin` and
  `/bin` names for the **same canonical** `/usr/bin/qemu-system-aarch64`.
  Version: `6.2.0 (Debian 1:6.2+dfsg-2ubuntu6.31)`; binary SHA256
  `0a63468782d096485932acf6aa0a69d358b3e3a6f68f655e960e9f5e3fc578d8`.
- Actual `-cpu help` contains these AArch64 candidates: `a64fx`, `cortex-a53`,
  `cortex-a57`, `cortex-a72`, `max`; **no cortex-a710**. Its remaining ARM CPU
  names are arm1026, arm1136, arm1136-r2, arm1176, arm11mpcore, arm926, arm946,
  cortex-a15, cortex-a7, cortex-a8, cortex-a9, cortex-m0, cortex-m3, cortex-m33,
  cortex-m4, cortex-m55, cortex-m7, cortex-r5, cortex-r5f, pxa250, pxa255, pxa260,
  pxa261, pxa262, pxa270-a0/a1/b0/b1/c0/c5, pxa270,
  sa1100, sa1110, ti925t (the authoritative raw listing is the tool output).
  None is substituted into the reviewed harness.
- No newer binary found in `/opt`, `/usr/local`, user `.local` tool directories,
  `/root/enuma-step10`, Windows command search, enuma workspace or common Windows
  QEMU/MSYS/Scoop/Tools locations. The only apt-cached qemu-system-arm package is
  the same6.2 build. This is a bounded search result, not a claim about every disk.
- Local official `docs/guide/requirements.md:25` only suggests `brew install qemu`
  for the optional QEMU/AAVMF smoke tools; no ready Linux QEMU environment/pinned
  installer was found in the checked official scripts/linux/.github locations.

Reproduce the actual environment gate (does not start a guest):

```sh
/usr/bin/qemu-system-aarch64 --version
/usr/bin/qemu-system-aarch64 -cpu help
```

## Proposed independent installation, NOT authorized/executed

No installed compatible tool was found. Proposed bounded source candidate is
upstream **QEMU9.2.0**, official source
`https://download.qemu.org/qemu-9.2.0.tar.xz` plus its detached release signature.
This is a proposed pinned version, **not a claim that it is the minimum/current
latest version or already locally qualified**. Release authenticity/dependency
checks and actual `-cpu help` must pass before guest use. Websearch metadata lookup
returned HTTP402 and was not retried; no release archive was downloaded and no
unobtained checksum is invented.

Minimal scope if separately approved: source/build/install under dedicated enuma
device ignored ext4 `.cache/host-tools/`, target only `aarch64-softmmu`, TCG, docs
and GUI disabled; no apt/sudo system install, no shared PATH, no kernel rebuild,
no new board model. Existing gcc, make, ninja, pkg-config, Python3.11, glib2.72.4
and pixman0.40.0 are present. Meson is not installed in PATH/Python environment;
source-provided build dependencies and dtc/libfdt must be checked explicitly,
not silently fetched by configure. Stop for a missing dependency rather than
install system packages. Existing16 logical CPUs / ample ext4 free space observed.

Estimated cost, not measured: roughly130MiB source download, 2–4GiB scratch,
5–20minutes compilation at bounded8 jobs. Read configure help first, verify release
source/signature and bundled dependencies, then configure with an isolated prefix
and only the AArch64 system target. Any extra dependency download needs explicit
bounded provenance/retry handling; there is no unrestricted network/bootstrap step.

Required post-install gate before any mode1/2/3 attempt:

```sh
"$PREFIX/bin/qemu-system-aarch64" --version
"$PREFIX/bin/qemu-system-aarch64" -cpu help | grep -x '  cortex-a710'
```

Then select that validated binary using per-process PATH when invoking the
existing isolated probe (not the current device wrapper that resets PATH), reuse
the explicit AAVMF forwarding view, frozen kernel/manifest and fresh output.
This would remove only the known CPU prerequisite; it would **not** prove arrival
at PMGR or promise that modes1/2/3 will work. No such installation/run occurred.

## Approved preparation attempt: terminal failure, not a lost running job

Parent approved isolated tool preparation, preserving frozen23r and all system,
base and device boundaries. Only ignored device host-side orchestration was
added: `.cache/prepare-qemu920.py`, `.cache/build-qemu920.py`,
`.cache/run-pmgr-qemu920.py`. The latter two were prepared but **never executed**.

Actual source/preparation command (Windows cwd device workspace):

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/prepare-qemu920.py
```

Original background job `sh_1c5c5f04b001pnED6GPQCjgaj9` ultimately delivered its
completion notification: **preparation exit1**, caused by **curl exit28** at
prepare-qemu920.py:45/51. On the user's explicit progress request, one read-only
snapshot had already found no remaining prepare/curl process and a terminal
`prepare.json`; no timed polling, sleeps, repeated task or status loop was used.
The later original completion notification confirmed that terminal failure.
There is no live process to monitor, so no fictitious exit-event listener was
registered. Earlier notification-routing uncertainty is now resolved.

Exact first error:

```
curl: (28) Operation timed out after 600000 milliseconds with 51281012 out of 135188800 bytes received
```

Source: `https://download.qemu.org/qemu-9.2.0.tar.xz`.
Isolated root:
`/root/enuma-step10/UniXNU-enuma/.cache/host-tools/qemu-9.2.0-isolated/`.
Unmodified original evidence remains:

- `prepare.json`: exact curl argv, returncode28, `signature_verified=false`,
  blocker and elapsed time **600.017166887s**.
- `qemu-9.2.0.tar.xz.attempt1.stdout.txt` / `.stderr.txt`: curl metadata/error.
- `qemu-9.2.0.tar.xz`: **incomplete** 51,281,012 bytes, not a valid source input.
  Partial-file SHA256
  `d90f1a727d55b8b7e7465384b071ed2977b8737f2b4badd7afc8f7c5240550de`.
- New separate `terminal-summary.json`: true preparation/curl exits and explicit
  unexecuted stages. No old record was rewritten. Allocated isolated disk usage
  measured just before adding that summary: **51,302,400 bytes**. It is not the
  originally estimated2–4GiB build cost. Actual build duration/size do not exist.

The official QEMU download page was read and linked the release public key with
primary fingerprint `CEACC9E15534EBABB82D3FA03353C9CEF108B584` at
`https://keys.openpgp.org/vks/v1/by-fingerprint/CEACC9E15534EBABB82D3FA03353C9CEF108B584`.
This establishes the intended verification identity, **not** verification of the
partial tarball. Signature/key downloading was never reached. No unauthenticated
source was extracted or executed. Local dependencies actually found: GCC11.4.0,
Ninja1.10.1, Make4.3, Python3.11.18, glib2.72.4, pixman0.40.0. Bundled Meson/dtc
availability is still unknown because source extraction did not occur.

### Actual result matrix / remaining unblock

| Stage | Actual result |
|---|---|
| Official tarball download | timeout28, incomplete; preparation wrapper1 |
| Release signature verification | **not run** |
| Configure / compile / isolated install | **not run** |
| New QEMU version/cortex-a710 check | **not run**, no new executable |
| New real-kernel guest checkpoint | **none observed; no new guest run** |
| PMGR mode1 / mode2 / mode3 | **not run with new QEMU** |
| PMGR stage / 16 fields | **unknown/not read**, not0 or3 or23 |
| Owned-boundary fault checks | **not run**, no fault interface added |

System QEMU remains6.2.0, with the previously documented CPU limitation. No CPU,
ADT, AMFI, frozen23r/native/manifest, global PATH or system package was changed.
Parent separately relays **independent23r host-package PASS** (checker, real
contained bindings, import tests and actual-FAT negatives); that result is not a
QEMU/runtime/device PASS. `device_authorized` and `release_allowed` remain false;
no packaging rerun or manifest edit was made in this preparation task.

No repeat/full download or resume was performed. The precise remaining source
extent is **83,907,788 bytes**. A smallest proposed unblock is one bounded HTTP
Range continuation into a new private copy, preserving this original partial
file and failed-run evidence, followed by the official detached-signature gate.
It is not a replay of the old preparation job or use of unverified bytes. Under
the current explicit no-repeat instruction this proposal is not executed here.
If specifically cleared, the continuation must require HTTP206 and the expected
total length, stop on range/provenance/quota errors, and never restart from zero
or switch mirrors. Build/runtime remain blocked until complete-source signature
verification succeeds. No ongoing-monitor task is claimed.

## Approved single recovery -> verified tool -> real guest result

The tool gate is now **PASS as parent supplied**; captured guest results remain
limited pre-PMGR failure evidence, not PMGR runtime qualification. Parent also
supplied independent23r **host-package PASS**; no packaging check, image rebuild
or manifest update was repeated for this documentation/entry preparation.

### Source authenticity and private dependencies

Tool root `R`:
`/root/enuma-step10/UniXNU-enuma/.cache/host-tools/qemu-9.2.0-isolated/attempt2`.
The original failed-run directory/partial/logs remain unchanged. One Range request
to the same official URL returned **HTTP206**, exact
`Content-Range: bytes 51215476-135188799/135188800`; first65,536 overlapping bytes
matched the preserved partial. The request delivered the remaining83,907,788 new
bytes plus that overlap. HTTP/body-length/range/overlap checks preceded splicing
into a new copy, not the old partial. Actual Range time **454.738s**, curl **0**.

- Complete source135,188,800 B, SHA256
  `f859f0bc65e1f533d040bbe8c92bcfecee5af2c921a6687c652fb44d089bd894`.
- Official signature from `https://download.qemu.org/qemu-9.2.0.tar.xz.sig`,
  SHA256 `ddbf173454dbce1eea04a98e04c6ee383f1194eb717006c518ebd0d0e9c1d758`.
- Downloaded official-linked key primary fingerprint exactly
  `CEACC9E15534EBABB82D3FA03353C9CEF108B584`. GPG isolated under `R/gnupg`:
  key inspection/import/signature verify each **0**, expected **VALIDSIG** present.
  GPG's unknown ownertrust warning was not represented as a web-of-trust proof;
  fingerprint provenance is the official HTTPS download page. No extraction
  occurred until the complete archive signature passed.
- First safe extraction rejected the upstream EDK2 absolute symlink
  `roms/edk2/EmulatorPkg/Unix/Host/X11IncludeHack -> /opt/X11/include`.
  A fresh `source-view/` retained Python's data safety filter and skipped **only
  that exact unused ROM-host link**; no other checks were disabled and no host
  absolute link was followed. The authenticated archive was not changed.
- Initial configure **1**: pip26 no longer vendors distlib, required by upstream
  mkvenv.py:91–106. Copied existing
  `/usr/lib/python3/dist-packages/pip/_vendor/distlib` into `R/private-python-deps`,
  used only explicit configure-child PYTHONPATH. Per-file hashes and origin in
  `continuation2.json`; no system Python/pip mutation or dependency download.
- QEMU's signed `subprojects/dtc.wrap` pins
  `https://gitlab.com/qemu-project/dtc.git` commit
  `b6910bec11614980a21e46fbccc35934b671bd81`; fetched exactly that commit once
  (**0**, 5.473s) into the isolated source subproject, verified HEAD. No source
  from an unrelated version was substituted.
- Second configure **1**: offline auto-fdt disables fallback despite available
  local dtc (`meson.build:2041–2066,3371`). Final configure uses existing upstream
  `--enable-fdt=internal`, with `--disable-download`, pip no-index and child-only
  blocked network proxies. The signed release already bundles Meson1.5.0 and
  pycotap1.3.1 wheels. No QEMU, kernel, base or harness code was patched.

### Actual final build and costs

Commands and true subprocess returns are in `R/continuation3.json`:

| Phase | Returncode | Actual elapsed |
|---|---:|---:|
| final configure, aarch64-softmmu only | 0 | 9.031s |
| `ninja -j8 qemu-system-aarch64` | 0 | 57.895s |
| `ninja -j8 install`, isolated prefix | 0 | 11.239s |
| installed `--version` | 0 | 0.016s |
| installed `-cpu help` | 0 | 0.016s |

Installed executable `R/install/bin/qemu-system-aarch64`: **9.2.0**, actual CPU
listing includes **cortex-a710**, SHA256
`d3d432b3bcfdd19fbb03f2d2998ad1ad2e98db9944d96b0a2fee5f96d55e8449`.
Installation allocated438,382,592 B; build4 allocated1,328,529,408 B; wholeattempt
allocated3,281,670,144 B immediately before `latest-result.json` was added,
including preserved extraction/configuration failures and source copies. These
are measured sizes, not the earlier estimates. `continuation3` total88.822s
includes build/install/tool checks and the first real guest orchestration; the
454.738s Range and earlier setup/inspection intervals are separate, not hidden
inside a claimed compile duration.

Actual Windows commands (workspace cwd, no background polling or repeated fetch):

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/recover-qemu920-chain.py
# outer1 after successful Range/signature0: safe extraction rejected absolute link
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/continue-qemu920-build.py
# outer1: safe extraction completed, configure1 missing distlib
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/continue-qemu920-dependencies.py
# outer1: local distlib + pinned dtc prepared; configure1 fdt auto disabled
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/.cache/finish-qemu920-build.py
# configure/compile/install/tool checks0; runtime child2 -> outer1
```

These were completed foreground bounded chains, not jobs left awaiting a route.
Each specific failure was inspected before the next reversible local correction.
The old system QEMU binary remains SHA256
`0a63468782d096485932acf6aa0a69d358b3e3a6f68f655e960e9f5e3fc578d8`.
No apt/system install, global PATH, shared WSL configuration or other-device
asset was changed.

### Actual guest boundary (not PMGR lifecycle qualification)

Runtime output `T`:
`/root/enuma-step10/UniXNU/out/enuma/pmgr-qemu920-runtime-23r-attempt2`.
`T/result.json` records exact command/cwd/local PATH, tool/kernel hashes and all16
actual PMGR fields. `R/runtime-runner.py` selects the installed binary via
child-only PATH and the **unchanged** already prepared official probe/AAVMF
forwarding view; no CPU model, DT construction, security setting or base file was
modified. Uses frozen prelink and its corresponding donor-derived report.

Selected actual command is the existing probe with:
`--kernel <frozen kernel.macho> --prelink-report <kernel.json> --timeout 60
--armvirt --armdt-platform --armcpu --kernel-extra-args pmgr=1
--inspect-sheng-pmgr --break-symbol _sheng_pmgr_run --finish-function`.
It uses the existing read/finish/panic-fallback interfaces, not a mocked service.

Observed:

- Real UART confirms UEFI -> UniXNU -> DarwinBoot inputs validated/exiting boot
  services -> kernel execution. First captured kernel trace PC
  **`0xfffffff004a7f330`** at5.728s; no invented function name assigned to it.
- Actual terminal stop **`_panic=0xfffffff0079e6134`**. Primary PMGR entry event
  and finished-function entry are **null**: `_sheng_pmgr_run` was not reached.
- Saved exception **ELR `0xfffffff004a92828`**, ESR `0x96000005`, FAR `0x0`,
  savedx0 `0x0`; unmodified final-image instruction **`0xf9400008` = `ldr x8,[x0]`**.
  Exact manifest extent maps this PC to **com.apple.security.AppleImage4**.
  Native frames include OSKext start/load -> KLDBootstrap loadSecurityExtensions
  -> mac_policy_initmach. This identifies a pre-PMGR null read, not its missing
  upstream runtime object/property cause. It is not the22r AMFI nub wait panic.
- PMGR diagnostic storage, resolved from the frozen symbol table, was read:
  **stage/status/mode and all other13 fields are0**. No provider/nub was created;
  instance-count baselines are not qualified. Stage0 here is observed memory,
  unlike the older QEMU6.2 attempt where fields could not be read at all.
- Probe outer return **1** at unchanged probe-darwinboot-xnu.py:1233,
  `KeyError: SCTLR_EL1`, because that key is absent from its captured system
  register map. The underlying real panic and saved state are already preserved
  in `T/mode1/gdb-stop.json`; postprocessing failure is separate from guest cause.
  No fallback register value or disabled audit is used to turn it into PASS.
- Mode orchestrator returns **2** because qualification failed. Final build-chain
  wrapper returns1 after that child2, **not a failed compile/install**. The QEMU
  process's natural exit status is not exported in the successful debugger-stop
  JSON; do not invent QEMUexit0 from it.
- **Mode2/mode3 not run**: same Image4 failure occurs before mode parsing/hook,
  so changing only pmgr would repeat a known shared prerequisite with no added
  information. No return-register fault interface was added. Owned-boundary
  load/type/pre/post/attach/start/matching fault tests **not run**. Existing
  generic allocator fixtures are not substituted for PMGR failure proof.

`R/latest-result.json` is a separate final summary; original `chain.json`,
continuation records, gdb-stop and failed-run logs are preserved. Kernel after
the attempt remains exactly
`bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072`;
no frozen candidate/manifest/package script or evidence was changed. Independent
23r host-package PASS remains separate. **PMGR runtime gate is open;
device_authorized=false, release_allowed=false.** No boot/flash/continue/claim/push.

### Historical tool verification references (tool gate completed)

These commands retain provenance; they are not instructions to repeat tool or
guest/fixture work in the current documentation/entry preparation task. The
later task boundary and necessity decision below supersede the old next-action plan.

Under explicit WSL root, no network or rebuild is needed to verify the ready tool:

```sh
R=/root/enuma-step10/UniXNU-enuma/.cache/host-tools/qemu-9.2.0-isolated/attempt2
GNUPGHOME="$R/gnupg" gpg --batch --verify "$R/qemu-9.2.0.tar.xz.sig" "$R/qemu-9.2.0.tar.xz"
sha256sum "$R/qemu-9.2.0.tar.xz" "$R/install/bin/qemu-system-aarch64"
"$R/install/bin/qemu-system-aarch64" --version
"$R/install/bin/qemu-system-aarch64" -cpu help
```

Verifier should independently read `T/result.json` and `T/mode1/gdb-stop.json`.
If runtime reproduction is requested, use the exact recorded mode1 command and
environment with a **fresh explicit output directory**, not a rerun of recovery,
install scripts or old output names. Expect an unqualified result, not mode1PASS.
Next reviewer task is bounded analysis of the existing original AppleImage4
saved-state/caller context and offline fixture prerequisites; do not bypass its
security behavior, mutate ADT/AMFI or invoke PMGR manually out of its approved
startup context. Any new PMGR fault interface or high-risk fix needs deep brief.
Final integration/acceptance remains with parent; no new device authority follows.

## Task boundary / first diagnostic necessity ruling

Parent's later reviewer analysis identified absent `/options` as the original
offline fixture prerequisite, consistent with the captured original AppleImage4
null context; it did not prove missing nonce values. The follow-up fixture task
received **two platform refusals without usable execution results**. Preserve the
original guest failure and refusal history; do not claim any new fixture/guest
result or resume/reproduce/work around that task. Current work is solely normal
host documentation and offline single-use entry preparation.

Parent relays deep's necessity decision for frozen prelink
`bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072`:
static lifecycle/fail-stop/340 necessary thunks plus independent full23r package
and observer manual gates are enough for **limited first controlled diagnostic
preparation**. Mode1 unpublished cleanup, mode3 refusal and boundary faults remain
unverified, but are not required to pass dynamically before that first diagnosis.
Mode2 actual stage23 publisher publication/matching and subsequent AMFI progression
are its goals, not existing results. Stage3 is not stage23; stage23 is not proof
of AMFI/whole userspace progress. No runtime or device acceptance is implied.

See `docs/pmgr-23r-diagnostic.md` for the offline-only entry and source log prefixes.
Historical manifest release_allowed=false and audit JSON stay unchanged. There is
**no current23r authorization**: parent final confirmation and new explicit user
round authorization remain mandatory. Record before execution; panic/stall/reset
are risks; failure stops without retry/changed arguments/continue or userdata write.
