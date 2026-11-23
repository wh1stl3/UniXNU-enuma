#!/usr/bin/env bash
# DISABLED: manual user action required; agents must not run cleanup scripts.
exit 1
# Manual use only. Stop builds and verify backups before applying.
set -euo pipefail
export LC_ALL=C
mode=${1:-}
if [[ $# -gt 1 || ( -n $mode && $mode != --apply ) ]]; then
    echo "Usage: bash scripts/cleanup-enuma-out.sh [--apply]" >&2; exit 2
fi
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
out=$repo/out
report=$repo/docs/disk-cleanup-review-20261123.md
[[ -d $out && ! -L $out ]] || { echo "Unsafe out root" >&2; exit 1; }
EXCLUDE=(
ufs-sm8250-launchd-keystore-20261122-r21
ufs-sm8250-launchd-keystore-20261122-r20
ufs-sm8250-launchd-keystore-20261122-r19
ufs-sm8250-launchd-keystore-20261122-r17
ufs-sm8250-launchd-keystore-20261122-r16
ufs-sm8250-launchd-keystore-20261122-r15
ufs-sm8250-launchd-keystore-20261122-r14
ufs-sm8250-launchd-keystore-20261122-r13
ufs-sm8250-launchd-keystore-20261121-r11
ufs-sm8250-launchd-display-20261121-r10
ufs-sm8250-launchd-display-20261121-r9
ufs-sm8250-launchd-display-20261120-r8
ufs-sm8250-launchd-display-20261120-r7
ufs-sm8250-launchd-display-20261119-r6
ufs-sm8250-launchd-cache-20261119-r3
ufs-sm8250-policy-20261118-r3
ufs-sm8250-launchd-cache-20261119-r2
ufs-sm8250-policy-20261117-r2
ufs-sm8250-startroot-mode0-20261118-r2
ufs-sm8250-launchd-cache-20261119-r1
ufs-sm8250-launchd-data-20261119-r1
ufs-sm8250-launchd-display-20261119-r1
ufs-sm8250-policy-20261116-r1
ufs-sm8250-startroot-mode0-20261118-r1
)
declare -A excluded=()
for name in "${EXCLUDE[@]}"; do excluded["$name"]=1; done
mapfile -t a < <(sed -n 's/^| `\([^`\/\\]*\)` | A | [0-9]* |$/\1/p' "$report")
mapfile -t b < <(sed -n 's/^| `\([^`\/\\]*\)` | B | [0-9]* |$/\1/p' "$report")
[[ ${#a[@]} == 77 && ${#b[@]} == 50 && ${#excluded[@]} == 24 ]] || { echo "Unexpected allowlist" >&2; exit 1; }
paths=() roots=() sizes=() broots=()
add() {
    local path=$1 root=$2 size
    if [[ -L $path ]]; then echo "SKIP symlink-path $path"; return; fi
    size=$(du -sb -- "$path"); size=${size%%$'\t'*}
    paths+=("$path"); roots+=("$root"); sizes+=("$size")
    printf 'WOULD REMOVE %s %s bytes\n' "$path" "$size"
}
for name in "${a[@]}"; do
    path=$out/$name
    if [[ -L $path ]]; then echo "SKIP symlink-path $path"; continue; fi
    [[ -d $path ]] && add "$path" ""
done
for name in "${b[@]}"; do
    [[ ${excluded[$name]+yes} ]] && { echo "SKIP excluded $out/$name"; continue; }
    root=$out/$name
    if [[ -L $root ]]; then echo "SKIP symlink-path $root"; continue; fi
    [[ -d $root && -f $root/boot.img && ! -L $root/boot.img ]] || { echo "SKIP missing boot.img $root"; continue; }
    # Fail closed on newly discovered links in B, including links in selected trees.
    if [[ -n $(find -P "$root" -type l -print -quit) ]]; then echo "SKIP symlink-containing $root"; continue; fi
    broots+=("$root")
    while IFS= read -r -d '' path; do
        rel=${path#"$root"/}; base=${path##*/}; lower=${base,,}
        [[ /$rel/ == */.git/* ]] && continue
        case "$lower" in manifest*|*.img|*.raw|*.dmg|*.md|*.json|*.toml|*.trustcache|*.key|*.pem|*.p12|*.cer|*.module|*.crt|*.pfx|*.sig|*.signature) continue;; esac
        selected=0
        case "/$rel" in /self-check/*|/build/*|/objects/*|/obj/*|/source/*|/*-selfcheck/*|*.dSYM/*) selected=1;; esac
        case "$lower" in *.o|*.macho|prelink.*|*.prelink) selected=1;; esac
        [[ $selected == 1 ]] || continue
        if head -c 10 -- "$path" | grep -aFq -- '-----BEGIN'; then continue; fi
        add "$path" "$root"
    done < <(find -P "$root" -type f -print0)
done
total=0
for size in "${sizes[@]}"; do ((total+=size)) || :; done
printf 'TOTAL %s items %s logical bytes\n' "${#paths[@]}" "$total"
[[ $mode == --apply ]] || exit 0
[[ ${CLEANUP_CONFIRM:-} == YES ]] || { echo 'Refused: set CLEANUP_CONFIRM=YES' >&2; exit 1; }
for i in "${!paths[@]}"; do
    path=${paths[i]}
    if [[ -L $path ]]; then echo "SKIP symlink-path $path"; continue; fi
    rm -rf -- "$path"
done
for root in "${broots[@]}"; do
    [[ -f $root/boot.img && ! -L $root/boot.img ]] || echo "WARNING missing boot.img $root"
    [[ -n $(find -P "$root" -mindepth 1 -print -quit) ]] || echo "WARNING empty $root"
done
