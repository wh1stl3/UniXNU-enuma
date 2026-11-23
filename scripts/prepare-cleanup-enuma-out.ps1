# Manual execution only. Snapshot sizes are logical bytes from WizTree, not free space.
# First complete and verify Step 0A/0B and inspect reparse points for EVERY target.
# Usage: pwsh -File scripts/prepare-cleanup-enuma-out.ps1 [--apply]
$ErrorActionPreference = 'Stop'
if ($args.Count -gt 1 -or ($args.Count -eq 1 -and $args[0] -ne '--apply')) { throw 'Only --apply is accepted' }
$apply = $args.Count -eq 1
$items = @(
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-fbfill2-20261123-r53-selfcheck'; Bytes = 580657322 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-fbfill-20261123-r52-failed1'; Bytes = 879155 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-fbfill-20261123-r52-failed2'; Bytes = 1882681 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-fbfill-20261123-r52-failed3'; Bytes = 242470388 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-fxdiag-20261123-r47-incomplete1'; Bytes = 551816 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-fxdiag-20261123-r47-incomplete2'; Bytes = 1267456 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-ps-20261123-r45-audit-attempt1'; Bytes = 245244272 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-matchcnt-20261123-r42-audit-attempt1'; Bytes = 245515413 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-storegeom-20261123-r40-audit-attempt1'; Bytes = 242114905 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-aksid-20261123-r39-compile-failed'; Bytes = 136795 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-aksid-20261123-r39-selfcheck2'; Bytes = 578689951 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-match-20261123-r36-compile-failed'; Bytes = 2227880 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-scale-20261123-r35-incomplete'; Bytes = 337746782 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-ipc-20261123-r34-failed-compile'; Bytes = 1682800 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-ipc-20261123-r34-failed-compile2'; Bytes = 1677022 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-ipc-20261123-r34-failed-json'; Bytes = 1352462 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-attempt-20261123-r32'; Bytes = 585421185 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-attempt-20261123-r32-intermediate'; Bytes = 585412630 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-control-20261123-r30-interrupted'; Bytes = 247344394 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-bbscan-20261123-r29-interrupted'; Bytes = 2592107 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261123-r28-format-check-failed'; Bytes = 246027710 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261123-r27-audit-map-failed'; Bytes = 242956922 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261123-r27-audit-stab-failed'; Bytes = 242629267 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261123-r27-dtb-cr-argv-failed'; Bytes = 410752557 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261123-r27-patch-context-failed'; Bytes = 504043 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261123-r27-patch-context2-failed'; Bytes = 504043 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261122-r26-ar-check-failed'; Bytes = 2439789 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261122-r26-ar-padding-failed'; Bytes = 2439789 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261122-r26-compile-cwd-failed'; Bytes = 1258816 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261122-r26-late-link-failed'; Bytes = 3475067 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-fbcount-20261122-r26-patch-dry-run-failed'; Bytes = 413034 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\r25-failed-patch-context'; Bytes = 446387 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\r25-failed-patch-offset'; Bytes = 446338 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\r25-failed-private-callout'; Bytes = 750863 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\r23-failed-audit1'; Bytes = 248188003 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\r23-failed-compile1'; Bytes = 105462 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-keystore-20261122-r19-incomplete-headers'; Bytes = 501923 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-keystore-20261122-r17-incomplete-sidecar'; Bytes = 469773082 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-keystore-20261122-r16-incomplete-audit'; Bytes = 251742564 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-keystore-20261122-r15-incomplete-width'; Bytes = 246077858 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-keystore-20261122-r14-incomplete-prev'; Bytes = 6092830 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-sm8250-launchd-keystore-20261122-r13-failed-first'; Bytes = 501554 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\smmu-route-contexts-candidate-r2-readonly-selfcheck-20261114'; Bytes = 136069320 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-r2-selfcheck-20261114'; Bytes = 0 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-r2-selfcheck02-20261114'; Bytes = 26868 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-r2-selfcheck03-20261114'; Bytes = 2173 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-r2-selfcheck04-20261114'; Bytes = 1437471 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-r2-selfcheck05-20261114'; Bytes = 1437471 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-r2-selfcheck06-20261114'; Bytes = 2173 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-r2-selfcheck07-20261114'; Bytes = 1441236 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-r2-selfcheck-20261114'; Bytes = 5944868 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-r2-selfcheck02-20261114'; Bytes = 5948897 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-r2-selfcheck03-20261114'; Bytes = 5954121 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-prepublish-rollback-artifact-selfcheck-20261114-r2'; Bytes = 187 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\smmu-route-contexts-rebuild-stage-selfcheck-20261114-r1'; Bytes = 555722 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\smmu-route-contexts-rebuild-stage-selfcheck-20261114-r1-empty'; Bytes = 0 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-final-selfcheck-20261114-r1'; Bytes = 16223883 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-identity-selfcheck-20261114-r1'; Bytes = 5047704 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-final-selfcheck-20261114-r1'; Bytes = 17278850 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-prepublish-rollback-artifact-selfcheck-20261114-r1'; Bytes = 187 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck10-20261114'; Bytes = 16442115 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-selfcheck-20261114-07'; Bytes = 15920593 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-selfcheck-20261114-05'; Bytes = 15853182 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck08-20261114'; Bytes = 14107682 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck07-20261114'; Bytes = 11717561 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck05-20261114'; Bytes = 8493842 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-selfcheck-20261114-04'; Bytes = 6725787 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-selfcheck-20261114-03'; Bytes = 6203758 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck09-20261114'; Bytes = 6117537 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck03-20261114'; Bytes = 5973152 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck06-20261114'; Bytes = 5939623 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck04-20261114'; Bytes = 5922641 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck02-20261114'; Bytes = 5826532 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-iommu-live-selfcheck01-20261114'; Bytes = 5823762 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-selfcheck-20261114-01'; Bytes = 3159608 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-selfcheck-20261114-06'; Bytes = 1285126 }
    @{ Path = 'D:\Code\PortingiOS\enuma\UniXNU-enuma\out\ufs-allocation-facts-selfcheck-20261114-02'; Bytes = 1279655 }
 )
$total = [long]0
foreach ($item in $items) {
    $total += [long]$item.Bytes
    Write-Host ("{0}  {1:N6} GiB (snapshot)" -f $item.Path, ($item.Bytes / 1GB))
}
Write-Host ("TOTAL: {0:N6} GiB; {1} directories; mode={2}" -f ($total / 1GB), $items.Count, $(if ($apply) { 'APPLY' } else { 'DRY-RUN' }))
if (-not $apply) { return }
Write-Host 'Manual prerequisite: no active builds; Step 0A and 0B completed and SHA-256 verified for each directory; inspect links and references.'
foreach ($item in $items) {
    $answer = Read-Host ("Type DELETE to confirm prerequisites and delete exactly: " + $item.Path)
    if ($answer -cne 'DELETE') { Write-Host 'Skipped'; continue }
    if (-not (Test-Path -LiteralPath $item.Path -PathType Container)) { Write-Host 'Missing; skipped'; continue }
    Remove-Item -LiteralPath $item.Path -Recurse -Force -ErrorAction Stop
}
