# Enuma one-shot Data seed — run failed before Apple download

## Authorized execution result, 2026-11-13 — self-checked

Reviewer `ses_e2c81eb0dffeiu4QVQVscDypRs` closed both limited changes and verifier
`ses_e2c77b04fffeCzXpW2xGxHHwvN` independently passed the audited source HEAD
`8fee93f8eb85c45237764bbd24853958d95a848f` (parent-provided results). That exact
HEAD was pushed once, without force, to `ci/enuma-data-seed-20261113` in
`wh1stl3/UniXNU-enuma`. No default branch or dirty original worktree was pushed.

Run [43377485430](https://github.com/wh1stl3/UniXNU-enuma/actions/runs/43377485430),
attempt 1, matches that head SHA. Push exit 0; managed `gh run watch --exit-status`
exit 1. First failure is the UniXNU checkout, workflow line 22: git exit 128,
`remote error: upload-pack: not our ref 693f5d9cae8a408dd18b39f3f9fdc4228c934241`.
The required revision is not fetchable from that configured official remote.
No pin/workflow edits or rerun were attempted after this failure.

Apple download, APFS generation/permissions/filesystem checks, packing,
encryption and upload were all skipped. The run artifact API returned zero
artifacts. Receiver/decryption were not run; no seed, UUID, public seed hash or
receipt exists, and no artifact needed deletion. Full payload fit cannot be
assessed without the seed. r3 and its historical auto215GiB plan are unchanged.

Before push, receiver prerequisites passed: OpenSSL 3.0.2, certificate validity
and pinned fingerprint, local dedicated transfer-key/certificate public-key
match, protected ACL limited to the local administrator and SYSTEM, and about
706 GB local free space. The original CRLF checkout was left untouched.
An independent local sparse Git clone under the original board's ignored
`out/data-seed-transfer-20261113/receiver-tools/drivers/DarwinBoot` checks out
`3c75734014cdab0acd9541e88057b7606ee7ae08`, Test directory, with autocrlf=false
and eol=lf. Its clean raw writer blob is
`87501abdcfb4f1abf7cc6eb0746ff26060b0b7c5`, SHA-256
`efb5fac21ae94dcb1aecd47da2b73a7112b487e43692ac6396858552d27a0e48`.
The audited receiver's real `--unixnu` argument can point at that receiver-tools
root; no `--darwinboot` option or modified receiver is needed. The tool was
imported and its exact hash gate passed from the valid LF clone's working
directory, avoiding WSL's incompatible Windows-worktree gitdir.

Local evidence stays in the original board's ignored, ACL-restricted
`out/data-seed-transfer-20261113/`: `receiver-preflight.json`,
`run-watch.exit`, `run-43377485430-result.json` and
`run-43377485430-error.txt` (one bounded root-cause log line). These runtime
results are self-checked, not independently verified by the earlier source
verifier. No owner-key/device action occurred. This record is local only;
execution is stopped pending a newly reviewed source-access solution.

## Authorization, 2026-11-13

The user explicitly authorized this one Data creation transit exception: a
GitHub-hosted macOS job may fetch the specified 21H461 original from Apple CDN,
verify it, create Data, and upload **only encrypted** Data with its necessary
manifest. Retrieve and validate locally, then delete the remote artifact.
Retention is one day. This does not permit other Apple asset publication,
Releases, owner private keys or device identifiers on CI, or any device writes.
Only a minimal dedicated branch may be pushed; no default-branch changes.
The shared general asset restriction is otherwise unchanged.

## Evidence and fixed sources

- Local `out/userdata-clean-20261112` actually contains both original DMGs,
  `OS.raw`, `BuildManifest.plist`, download/provenance and APFS reports. Existing
  verified hashes are reused; no repeat multi-GB local hash and no re-signing.
- Source URL and product/build are read from the pinned official
  `profiles/os/ipados-17.7.11-21H461/profile.toml`, then checked against explicit
  iPad7,1 / j120ap / 21H461 / chip 0x8011 / board 12 assertions.
- `scripts/data-seed/source.json` pins the BuildManifest hash, ZIP metadata,
  original OS member hash/length, UniXNU revision and DarwinBoot writer revision
  plus blob. Only the OS member is downloaded, by strict bounded range reads;
  no full IPSW, SystemOS, kernelcache, identity or donor files are committed.
- UniXNU stays at `693f5d9cae8a408dd18b39f3f9fdc4228c934241`; its observed
  upstream HEAD was `dff276535db3ac394f628cec58a718cd46c20ac2` (not adopted).
- Reference only: `Asultop/UniXNU-NX769J@2a265afdbd95d45e4a90664157e793c3bfee3755`,
  `.github/workflows/data-seed.yml` and `scripts/build-data-seed.py`. The useful
  pattern is final-size APFS creation before packing. None of its iOS 16.5
  assets, donor identity, UUIDs, optional plaintext upload or passphrase flow
  is reused.

## Size, format and identity

This creates the official minimum supported **3 GiB logical first-install**
seed, not a 215 GiB final Data plan. Direct `hdiutil create -layout NONE -type
UDTO -size 3g -fs APFS` avoids the pinned official make-data-seed's 32 MiB
copy-before-grow limitation. Copy rules, empty directories and framebuffer
preferences match that official script, using its `merge` routine; setup is
not skipped. The official DarwinBoot writer packs DBRDISK1 and enforces its
256 MiB encoded bound. The job checks full-size NXSB and `diskutil verifyVolume`.

The UUID is generated once by macOS and preserved in the encrypted manifest.
Preserve this seed for future builds: regeneration changes the installation.
Above 2 GiB, official SHNGSEED2 identity hashes logical size plus nonzero pages;
growth preserves volume UUID but changes seed/store identity. No grow is needed
for this chosen initial size. If a later 215 GiB target is actually selected,
it requires a separate macOS growth/verification step and an explicit new store
budget/reinitialization decision; this job does not pretend to complete it.
`out/production-recipe-r3` and its historical auto215GiB plan are untouched.
Before integration, derive a new recipe/store budget for this 3 GiB seed from
its actual encoded size/identity and the real root/policy/reserve sizes. Runtime
capacity/first-boot sufficiency is not established by offline seed creation.

## Resource bound (not a compression-ratio estimate)

Concurrent disk upper bound: original OS DMG 5,157,406,069 B + full non-sparse
3 GiB raw 3,221,225,472 B + DBR 256 MiB + tar 256 MiB plus small headers + CMS
256 MiB plus small overhead = approximately **8.56 GiB**, plus checkout/tooling
and filesystem overhead. The pre-download free-space gate requires **11 GiB**.
The OS DMG is mounted read-only, not converted into another 6 GB raw file.
Nothing depends on 215 GiB sparsity or a guessed compression ratio. Only
finite 3 GiB raw is created. Official packing above 2 GiB uses SEEK_DATA/SEEK_HOLE;
macOS support, hdiutil and diskutil are exercised in the job, not claimed as
locally tested. A failed dependency/size/format check stops without uploading.

## Encryption and lifecycle

OpenSSL 3 CMS AuthEnvelopedData, AES-256-GCM and an ephemeral dedicated RSA-3072
certificate; no invented envelope or shared password secret. Public certificate
only is in Git, fingerprint bound in source.json. The private key is isolated
from owner signing keys under ACL-restricted ignored
`out/data-seed-transfer-20261113/` in the original board checkout. Local OpenSSL
3.0.2 CMS encrypt/decrypt of synthetic bytes was self-checked before preparation.
No UUID is printed by helpers; command output containing UUIDs is captured.

Only `data.dbr` and `manifest.json` enter a whitelist tar; only `data-seed.cms`
enters upload-artifact. No cache, failure upload, plaintext fallback or debug
archive. TemporaryDirectory removes only job-created files; APFS attachments
have finally cleanup. Encryption completes before the upload path is populated.

The push event is restricted to `ci/enuma-data-seed-20261113`. This avoids a
default-branch workflow registration change. **Do not push until parent review
and independent static verification approve this exact tree.** Then push once,
identify the run bound to the pushed SHA and use a managed background
`gh run watch RUN --repo wh1stl3/UniXNU-enuma --exit-status` (no polling/sleep).
Do not auto-rerun jobs. HTTP download retries are zero, so access/region/quota
errors cannot be retried accidentally.

## Local receipt and deletion

Run `receive.py` under WSL with the existing authenticated Windows gh executable;
WSL's separate `/usr/bin/gh` is not authenticated. No credentials are copied.
The receiver converts only the download directory to Windows form. Example:

```sh
python3.11 -B scripts/data-seed/receive.py --run RUN --commit PUSHED_SHA \
  --gh '/mnt/c/Program Files/GitHub CLI/gh.exe' \
  --unixnu /mnt/d/Code/PortingiOS/UniXNU \
  --key /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/data-seed-transfer-20261113/transfer-key.pem \
  --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/data-seed-transfer-20261113/received-RUN
```

Receiver requires a successful run at the exact branch/SHA, one exact artifact,
and a fresh local output. It verifies CMS GCM authentication before parsing,
archive whitelist, encrypted manifest pins/run/commit, official packed bounds,
encoded SHA-256 and SHNGSEED2 identity, NXSB checksum/geometry and presence of a
checksummed APSB matching the new UUID. These are not a local macOS fsck/mount.
Only after all checks does it write receipt.json and DELETE that artifact via
GitHub API, recording success. Keep the local seed/manifest/key; do not delete
the key until independent verification is complete. If the receiver fails, stop
and notify the parent immediately; the artifact still expires after one day.

## Verification at this checkpoint

Authentication was checked without exposing token contents: wh1stl3 account,
repo/workflow scopes; remote is `wh1stl3/UniXNU-enuma` (public), repository API
reports admin/push permission, Actions enabled and all actions allowed.
Workflow billing/quota and actual runner execution remain untested until the
approved push. Original dirty worktree is preserved. No push/run/device action.

Independent verifier should rerun:

1. `python3.11 -B scripts/data-seed/test_tools.py` under Linux/WSL.
2. Python AST/compile, YAML syntax, pin/certificate checks and inspect the exact
   Git diff/whitelist. Exercise CMS synthetic roundtrip and tamper rejection.
3. Official record check from the pinned UniXNU checkout, using Windows Git:
   this Windows-created worktree has a Windows absolute gitdir, so stock WSL
   Git cannot open it. For WSL Python, load the official module with runpy and
   replace only its `git(device, *args)` command adapter with Windows git.exe
   and `wslpath -w device`; run its unmodified `check(path, 'origin/main')`.
   Before commit, the same official `check_changes` is also run against staged
   paths (the normal CLI compares HEAD rather than the index).
4. After the approved job, independently check the final seed and receipt and
   rerun relevant format/identity checks; acceptance belongs to the parent.

Preparation self-checks: six offline tests, Python AST/YAML/TOML syntax,
certificate fingerprint, the small original BuildManifest SHA-256 and source
pin correspondence; OpenSSL CMS GCM synthetic roundtrip **and tamper rejection**.
Official record schema and staged ownership checks passed through the above
Windows Git adapter. macOS execution and independent verifier remain pending.

## Limited review follow-up to 755d43e (2026-11-13)

Only two reviewer changes are addressed. The workflow's outer umask077 stays
unchanged. Actual seed population (copy, generated directories and the pinned
official `merge` calls) uses umask022 in a try/finally restoring the caller's
umask. Before verifyVolume/detach/pack, the mounted seed checks all newly added
parent directories are 0755, tmp is 01777, and copied source directory modes
and symlink targets remain unchanged; no recursive chmod. Plaintext files
outside the mounted seed are still created under the outer umask077.

Failed subprocesses now report stage/exit code and at most 768 characters of
diagnostic reason from bounded stderr/stdout windows. UUIDs, absolute paths,
credential assignments and bearer strings are redacted; non-diagnostic content
and successful output are not dumped. No debug artifact is added.

Nine offline tests self-checked: the real make_seed population path with the
actual pinned official merge and initially missing generated directories,
umask077 restoration on success/failure, source mode/link preservation, three
tool failure reasons/redaction/bounds, and main's failed encryption leaving the
upload directory empty, plus the six original tests. APFS creation/tool calls
are mocked locally; real macOS permission assertions remain unexecuted. The
old independent verifier result is not acceptance of this follow-up. No push,
cloud run, key/certificate regeneration or Apple asset changes. Same-reviewer
limited re-review and a fresh verifier are required before push authorization.
