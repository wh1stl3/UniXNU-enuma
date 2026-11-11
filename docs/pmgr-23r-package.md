# 23r guarded PMGR package and real-kernel harness (2026-11-10)

**Independent complete23r host-package gate PASS (parent-relayed final verifier
result). No current23r device authorization or operation. Frozen reviewed images
were not rebuilt. A separate single-use entry is now prepared offline only; see
[first controlled diagnosis](pmgr-23r-diagnostic.md).**

## Independent conclusions supplied by parent

Bound prelink: `bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072`.

- PMGR deep final static review: **PASS WITH CONDITIONS**, permits host packaging
  checks, not device execution. Necessary lifecycle thunks were separately read
  back and found correctly bound. The automated **205 imports check is symbol
  presence only**, not proof of every complete binding or implementation ABI.
- Original observer deep: **PASS WITH CONDITIONS** on all five manual static
  gates: TextMode/Acquire dominance before PID1; actual non-platform SVC source,
  arguments and dispatch; begin/release identity; exit lock ordering; normal
  identity lifetime. Twenty functions have native/prelink instruction equality;
  of the six bound sources only bsd_init gains the PMGR hook. Observer patch
  SHA256 remains `a3c12c0f1d210bb2481ba83fa28023c91fad27ac346f992d7613de7e8ed12109`.
- Verifier already passed finalchecks/hash/record/diff. This round does not rerun
  those tests or the observer. Automatic observer audit remains **exit2 /
  manual-review-required**; its JSON was not rewritten as automatic PASS.
- These are parent-relayed independent conclusions, not new reviews performed
  by this packaging implementer. Real-device/display behavior remains unverified.

Build evidence correction: **there is no**
`/root/enuma-step10/UniXNU/out/enuma/pmgr-selfcheck/target-build-final.log`.
Do not cite it or claim verifier independently confirmed a build exit from it.
The existing build command, `out/enuma/pmgr-selfcheck/build.json`, final hashes
and real artifacts are the retained evidence. No rebuild was done for logging.
The prior host-side `.cache/pmgr-contract/target-build-final.log` is a different
path and is not independent build-exit verification.

## Frozen inputs / implementation limits

Base `693f5d9cae8a408dd18b39f3f9fdc4228c934241`; device HEAD
`7772f75fef46bfeeff899db25554f555ee27670c`, existing uncommitted work preserved.
Official publisher reference remains
`6bc0ce1e8c3a3733110a80dd80ddfb2a1ca46555`. Native SHA256
`5b8fd1811e39d6415550786578c1fb96346df32a0ba2a35efbd3ff50a251a74f`.
Prelink/native sources and binary contents were not modified this round.

Mode1 checks unpublished release back to baseline counts. Mode2 failures stop
and retain state; **no cleanup promise**. Successful provider/nub initial
references remain permanent, no unload. Original internal typed allocation may
Assert before reaching device stage12; this is not arbitrary recoverable OOM.
Nonvirtual original nub interfaces are not comprehensively intercepted: scope
is the reviewed publisher and AON boundary, not all original PMGR operations.

## Real harness result: blocked before guest checkpoint, NOT runtime PASS

Device orchestration `scripts/run-enuma-pmgr-qemu.py` uses unchanged base
`probe-darwinboot-xnu.py` (SHA256
`6ace23a7d1e5aabbb37e97cb9d34bc4f01480e65edd088a806abaff2eac1b0be`), real frozen
prelink with corresponding donor-derived manifest, existing enuma build's
UniXNU/DarwinBoot EFI inputs, and an isolated output/ROOT. No board simulation
or mock was built. The first mode requested was `pmgr=1`.

Actual command (cwd `D:/Code/PortingiOS/enuma`):

```powershell
wsl -d Ubuntu-22.04 -u root -- /home/wh1stl3/.local/bin/python3.11 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/run-enuma-pmgr-qemu.py --base /root/enuma-step10/UniXNU --kernel /root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho --manifest /root/enuma-step10/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.json --loaders /mnt/d/Code/PortingiOS/enuma/uefi-enuma/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64 --firmware /usr/share/AAVMF/AAVMF_CODE.fd --output /root/enuma-step10/UniXNU/out/enuma/pmgr-qemu-23r-aavmf
```

Actual wrapper/harness returncode **1**, gdb-stop **1**, QEMU **1**. Evidence under
that output: `result.json`, `mode1.stderr.txt`, `mode1/gdb-failure.json`,
`mode1/gdb-stderr.log`. The real first QEMU error is:

```
qemu-system-aarch64: unable to find CPU model 'cortex-a710'
```

Host QEMU is `6.2.0 (Debian 1:6.2+dfsg-2ubuntu6.31)`; base gdb-stop.py:349 hardcodes
cortex-a710 for TCG. `gdb-failure.json` records `qemu_exit_code=1`,
`checkpoint_observed=false`, `trace_events=[]`, `partial_report={}`. No PMGR
field bytes were read: **stage is unknown, not zero, 3, 16 or 23**.

An earlier default-FD attempt under `out/enuma/pmgr-qemu-23r` returned harness1 /
gdb-stop2 at gdb-stop.py:383, missing default `edk2-aarch64-code.fd`. The second
attempt forwarded the existing child's supported `--firmware` option to existing
AAVMF via an isolated device-owned exec wrapper; no base file or CPU was changed.
After the actual CPU prerequisite failure no further modes/retries were run.

Mode1 create/free counts, mode2 stage23/genuine matching, mode3 refusal, and
load/type/pre/post/attach/start/matching fault cases are all **not qualified**.
Fault injection did not run; no formal implementation interface was added.
Next runtime prerequisite is a compatible existing harness/QEMU environment for
the same CPU, not changing ADT/AMFI or substituting an invented board.

## 23r package (no execution entry)

Both target directories were absent before creation:

- ext4 `/root/enuma-step10/UniXNU/out/enuma/stage6-ramblock-probe/23r-pmgr-publisher`
- Windows `D:/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/23r-pmgr-publisher`

Command: WSL Python3.11 absolute path above with device
`.cache/package-pmgr-23r.py`. It invokes only existing payload and bootimg
packaging commands with `--kernel <frozen prelink>`, **not kernel build**.
`commands.json` records full argv/cwd and native subprocess returncodes:
payload **0**, bootimg **0**, initial package selfcheck **0**.
`copy-validation.json` records ext4/Windows copy hashes equal.

| Asset | SHA256 |
|---|---|
| boot.img | `1f4574a1dcdcc9a7a551a07ac79565b2a5a0274546952ddd3f3fe24ae4e47207` |
| payload.img | `1b4a12f49135937e965bc4413df67a7c87d069c3e1b9fbfec9b5b8fa21336f76` |
| manifest.json | `ad0c3bc7b55c9b228c22c55465844060b4a9c22c435b7786e9217d009fd08690` |
| actual contained kernel | `bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072` |

Actual contained config is exactly `-v serial=3 rd=md0-ramblock pmgr=2`.
Checker hashes the actual contained kernel, checks archive/final linked hook and
340 pointers, and hashes the actual Android boot ramdisk extent back to payload.
It does not infer these from symbols or payload.json alone.

22r firmware/DTB/shim/trust/RAM-root image hashes, 192MiB payload size, root UUID
`9071148B-B025-402D-AD7A-48464D8B5FFF`, DRAM8GiB and owned window512MiB remain
unchanged. The regenerated ADT is not byte-identical: property-byte delta found
**only `/device-tree/chosen:random-seed`**. Both contained ADT hashes are checked
against their reports and every other property is byte-identical. No full
FAT/trust/ADT hardware audit was repeated.

Actual FAT-config negatives in isolated copied payload (release image unchanged):
`.cache/check-pmgr-23r-negatives.py`, outer exit **0**, evidence
`out/enuma/pmgr-package-negatives-23r/result.json`. Positive exact pmgr2 **0**;
missing, duplicate, wrong-mode1, alias-alone, valid-plus-alias each **1**, with
specific parameter-gate failure text. No mock substitutes for contained parsing.

Final copied Windows candidate checker exit **0**, including ADT delta and actual
boot/payload binding. Command/result captured in device ignored
`.cache/pmgr-contract/package-23r-selfcheck.json` retains the implementer's original
selfcheck result. Parent subsequently relayed independent full checker0,
five import-path tests passing, fresh actual-FAT positive0/five negatives1 and
final package binding0, with candidate unchanged: **independent host-package PASS**.
That later conclusion is separate; this historical selfcheck JSON was not edited.

### Short independent packaging rerun (explicit WSL identity/cwd)

```powershell
wsl -d Ubuntu-22.04 -u root --cd /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma -- /home/wh1stl3/.local/bin/python3.11 -I scripts/check-enuma-pmgr-package.py --candidate /mnt/d/Code/PortingiOS/UniXNU/out/enuma/stage6-ramblock-probe/23r-pmgr-publisher --manifest-sha256 ad0c3bc7b55c9b228c22c55465844060b4a9c22c435b7786e9217d009fd08690
```

The previous shortened WSL command omitted the required execution identity.
Independent verifier encountered `audit-enuma-pmgr-prelink.py:31`,
`ModuleNotFoundError: native_prelink`. Read-only diagnosis found default WSL user
uid1000 cannot traverse `/root` (mode700), where the frozen manifest's explicit
base/tree/native inputs reside. Earlier selfchecks used `-u root`; the failure
was an access boundary, not evidence that native_prelink was absent or that
PYTHONPATH should point at another copy. No permissions or manifest paths changed.

Import-only hardening in the device audit now reads the helper at explicit
absolute `base/kits/XnuPrelink/native_prelink.py`, verifies the already pinned base
revision and normalized source hash, and executes those verified bytes in a
separate module without sys.path/cwd/cache fallback or a base __pycache__ write.
Permission denial is reported explicitly; it is not silently replaced by another
module. ABI/image/acceptance checks are unchanged. New path tests use small import
fixtures only, never mock donor ABI behavior. Fresh verification evidence is
separate under `out/enuma/pmgr-import-fix-checks/`; no old candidate or evidence
file is overwritten. Use the explicit-root command above, not an implicit login
environment or arbitrary PYTHONPATH.

Import-fix selfcheck actual results: full specified package checker from device
cwd **0**, from separate cwd **0**, both without PYTHONPATH and with Python `-I`;
five new import-location tests **0**; five real FAT parameter negatives each **1**
with the intended pmgr/alias rejection text. Fresh `checks.json` records complete
argv/cwd/uid/environment/returncodes; `result.json` records before/after identical
manifest `ad0c3bc7...fd08690`, boot `1f4574a1...e47207`, payload
`1b4a12f4...336f76`. Full digests remain in the asset table above. Independent
verifier subsequently reran the corrected command and passed as parent relayed;
the old ModuleNotFoundError remains a historical failure, not rewritten as PASS.

Historical discovery and later successful isolated QEMU9.2 preparation/tool PASS
are in [QEMU environment](pmgr-qemu-environment.md). The original real mode1
stopped in AppleImage4 before PMGR; subsequent fixture attempts have no usable
result after two platform refusals. That task is not resumed or bypassed here.

Do not rerun completed packaging/build/observer gates. Parent relays deep's
necessity ruling: static lifecycle/fail-stop/340 necessary-thunk evidence and
independent packaging/observer gates allow **first bounded diagnostic preparation**
for this frozen hash without requiring mode1/3/fault dynamic completion first.
Those dynamic items remain unverified; mode2 stage23 and AMFI progression are
diagnostic goals, not prior results. Stage23 is publisher selfcheck only. No
runtime/display/userspace or stage7 acceptance is established. Historical manifest
release_allowed=false stays intact; new device authorization is still required.
The separate entry needs only its offline incremental verification; details and
recording/failure policy are in pmgr-23r-diagnostic.md. Parent retains acceptance.
