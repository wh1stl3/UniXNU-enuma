# Dry-run only. Snapshot sizes are logical bytes from WizTree, not free space.
# First complete and verify Step 0A/0B and inspect reparse points for EVERY target.
# Usage: pwsh -File scripts/prepare-cleanup-enuma-out.ps1 [--prune-b]
$ErrorActionPreference = 'Stop'
if ($args -contains '--apply') { throw 'Deletion disabled; use the WSL script manually.' }
if (@($args | Where-Object { $_ -notin @('--apply', '--prune-b') }).Count -or @($args | Select-Object -Unique).Count -ne $args.Count) { throw 'Only --apply and --prune-b are accepted, once each' }
$apply = $args -contains '--apply'
$pruneB = $args -contains '--prune-b'
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
    Write-Host ("A  {0}  {1:N0} B (snapshot)" -f $item.Path, $item.Bytes)
}
$bCandidates = [System.Collections.Generic.List[object]]::new()
if ($pruneB) {
    # The reviewed classification table is the explicit 50-directory allowlist.
    $report = Join-Path $PSScriptRoot '../docs/disk-cleanup-review-20261123.md'
    $lines = Get-Content -LiteralPath $report -Encoding UTF8
    $names = @($lines | Where-Object { $_ -match '^\| `([^`\\]+)` \| B \| \d+ \|$' } | ForEach-Object {
        if ($_ -match '^\| `([^`\\]+)` \| B \| \d+ \|$') { $Matches[1] }
    })
    if ($names.Count -ne 50 -or @($names | Select-Object -Unique).Count -ne 50) { throw 'B allowlist must contain exactly 50 distinct directories' }
    $out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../out'))
    foreach ($name in $names) {
        $root = Join-Path $out $name
        $boot = Join-Path $root 'boot.img'
        if (-not (Test-Path -LiteralPath $boot -PathType Leaf)) { Write-Warning "B-prune skipped (boot.img missing): $root"; continue }
        $rootItem = Get-Item -LiteralPath $root -Force
        if ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { Write-Warning "B-prune skipped (reparse root): $root"; continue }
        $pending = [System.Collections.Generic.Stack[object]]::new()
        $pending.Push(@($rootItem, $false))
        $local = [System.Collections.Generic.List[object]]::new()
        $unsafe = $false
        while ($pending.Count) {
            $entry = $pending.Pop()
            $dir = $entry[0]
            $selected = [bool]$entry[1]
            foreach ($child in @(Get-ChildItem -LiteralPath $dir.FullName -Force -ErrorAction Stop)) {
                if ($child.Attributes -band [IO.FileAttributes]::ReparsePoint) { $unsafe = $true; continue }
                if ($child.PSIsContainer) {
                    if ($child.Name -ieq '.git') { continue }
                    $matchDir = ($dir.FullName -ieq $root -and ($child.Name -in @('self-check','build','objects','obj','source') -or $child.Name -like '*-selfcheck')) -or $child.Name -like '*.dSYM'
                    $pending.Push(@($child, ($selected -or $matchDir)))
                } else {
                    $n = $child.Name
                    if ($n -like 'manifest*' -or $n -match '(?i)\.(img|raw|dmg|md|json|toml|trustcache|key|pem|p12|cer|module)$') { continue }
                    if (-not ($selected -or $n -like '*.o' -or $n -like '*.macho' -or $n -like 'prelink.*' -or $n -like '*.prelink')) { continue }
                    $stream = [IO.File]::Open($child.FullName, 'Open', 'Read', 'Read')
                    try {
                        $header = [byte[]]::new(10)
                        $read = $stream.Read($header, 0, 10)
                        if ($read -eq 10 -and [Text.Encoding]::ASCII.GetString($header) -ceq '-----BEGIN') { continue }
                    } finally { $stream.Dispose() }
                    $local.Add([pscustomobject]@{ Path = $child.FullName; Bytes = [long]$child.Length; Root = $root })
                }
            }
        }
        if ($unsafe) { Write-Warning "B-prune skipped (reparse point): $root"; continue }
        foreach ($candidate in $local) { $bCandidates.Add($candidate) }
    }
}
$bTotal = [long]0
foreach ($item in $bCandidates) {
    $bTotal += $item.Bytes
    Write-Host ("B-prune  {0}  {1:N0} B" -f $item.Path, $item.Bytes)
}
Write-Host ("SUMMARY: A={0:N6} GiB (snapshot); B-prune={1:N6} GiB (live); total={2:N6} GiB; mode={3}" -f ($total / 1GB), ($bTotal / 1GB), (($total + $bTotal) / 1GB), $(if ($apply) { 'APPLY' } else { 'DRY-RUN' }))
return # Dry-run only.
