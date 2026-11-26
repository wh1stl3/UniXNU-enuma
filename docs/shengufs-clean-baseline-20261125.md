# ShengUfs clean baseline comparison — 2026-11-25

Status: `self-checked` inventory, not a candidate patch or a build.

## First blocker: revision identity

The documented `UniXNU/ShengUfs@38c19c2b` is not established as a Git
commit. The surviving feed checkout named `ShengUfs-38c19c2b` at
`/root/enuma-step10/UniXNU/out/enuma-ufs-version-package-20261112-a/out/enuma/feeds/`
is a clean shallow Git checkout at
`99d8bcd3e43dd24fc3c8437c67b5d4cc71ab94d0`, origin
`https://github.com/UniXNU/ShengUfs.git`; `git rev-parse 38c19c2b^{commit}`
fails there. The GitHub commit API returned HTTP 422 for that prefix on this
repository. The directory name alone therefore cannot identify a commit or
prove the intended pin. No ancestry between that checkout and the 11-18
source is established.

The exact r11 input is
`out/ufs-sm8250-startroot-wip-20261118/self-check/resume-20261118-r11/merged-source/`;
its `NativeUfs.cpp` SHA-256 is
`6ee5fb866c9bcdc5b1c50268ede8dc86f3eef1526c3784b3e8f0664da27ccb69`.
The source licence is BSD-2-Clause-Patent; the retained
`ObservedSmmu-LICENSE` is separate.

## Reproducible comparison, not a replay candidate

Exporting the verified Git tree at `99d8bcd3` and comparing it with the r11
tree yields 54 changed paths, 8,168 additions and 564 deletions. The full
mechanical comparison is
`out/shengufs-baseline-audit-20261125/full-comparison.diff` (SHA-256
`3a8ab9f45417044e75fc9918614acf307e8564a7c98b35aa332ae536a4fddcd5`);
`diff-stat.txt` lists every changed file. It uses absolute paths and is a
review artifact, **not** a patch to apply. Unlisted paths compare equal.
Because the baseline identity is unresolved, none of its hunks is asserted
to be an upstream change or a necessary local change.

File-level triage against this *comparison* baseline:

| Files | Area to review; not a proven origin or necessity |
| --- | --- |
| `NativeUfs.cpp` | Mixed host bring-up, root publication, verification, store gates and diagnostics; cannot separate safely by filename. |
| `RootCommands.h`, `RootQueue.h` | Transport, queue and ownership-sensitive changes; inspect with warm adoption. |
| `RootLayout.h`, `tests/RootLayout.cpp` | Root/GPT/manifest layout and tests. |
| `RootWarmAdopt.h`, `RootWarmCapture.h`, `RootWarmInput.h`, `RootWarmTarget.h` | Warm adoption and target mechanics; ownership/DMA review required. |
| `RootWarmDiagnostic.h`, `RootWarmReport.h` | Warm diagnostic and reporting code. |
| `UfsPlatformEntry.h`, `UfsPlatformResources.h` | Platform selection and SM8250 policy; board match and default refusal need review. |
| `UfsBypassExtent.h`, `UfsEnumaReadContract.h`, `UfsEnumaReadEntry.h`, `UfsEnumaReadPackets.h`, `UfsEnumaReadTransport.h`, `UfsReuseAdmission.h`, `UfsReuseReport.h`, `UfsTakeoverGates.h` | Read-contract and admission infrastructure; do not equate these with authorization. |
| `UfsObservationContract.h`, `UfsObservedSmmu.h`, `UfsObservedSmmuCapture.h`, `UfsThreeIdDiagnostic.h`, `UfsVersionDiagnostic.h`, `UfsVisibleRouteFields.h`, `UfsVisibleRoutesDiagnostic.h`, `UfsVisibleRoutesReport.h` | Observation/diagnostic infrastructure; retain licence when applicable. |
| `README.md`, `ObservedSmmu-LICENSE`, other added `tests/*` | Documentation, licence and test evidence; individual test paths are in `diff-stat.txt`. |

## Specific unresolved conflicts

* `NativeUfsBlock::configureVerification`, r11 `NativeUfs.cpp:2063`:
  `99d8bcd3` contains header-only policy/hash-table loading via
  `readPolicyTable`, while r11 copies the supplied envelope directly and calls
  `vr_open`. The two source snapshots support different input forms; do not
  claim equivalent authentication or remove either path without establishing
  the intended upstream baseline and policy input contract.
* `NativeUfs.cpp:1659–1701,1747–1754,1810–1834`: r11's
  `ownerVerified`/`storeBound` and epoch-based revoke are intertwined with
  store windows and concurrent access. The r11 rationale explicitly records
  unresolved reviewer questions about in-flight window checks. Preserve the
  fail-closed mode-2 constraint; do not reconstruct the concurrency logic by
  selectively copying this comparison.
* `UfsPlatformResources.h:118–120` and `NativeUfs.cpp:1523,2567`:
  SM8250 warm selection and host entry are coupled to DMA/ownership policy.
  A build or past single boot does not establish continuous ownership. Their
  origin and exact necessary hunk boundaries remain to be established.

The comparison was not compiled: compiling a guessed hybrid would not establish
the requested baseline and could conceal the authentication conflict. No old
object/archive was used, no device was contacted, and no clean package is
claimed. Next input required: the full Git object ID and source checkout or
authoritative pin metadata for the intended `38c19c2b` baseline, followed by
per-hunk classification and deep review of the DMA/ownership and concurrency
diff before any replay candidate is accepted.
