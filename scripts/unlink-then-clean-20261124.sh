#!/usr/bin/env bash
# DISABLED: manual user action required; agents must not run cleanup scripts.
exit 1
set -u
set -o pipefail

# This is not an authorization to delete; the manifest records incomplete
# preservation scans. Review and preserve every directory before applying.
cd "$(dirname "$0")/.." || exit 1
apply=0
case "${1-}" in
  "") ;;
  --apply) apply=1 ;;
  *) echo "usage: $0 [--apply]" >&2; exit 2 ;;
esac
if (( $# > 1 )) || { (( apply )) && [[ ${CLEANUP_CONFIRM-} != YES ]]; }; then
  echo "apply requires CLEANUP_CONFIRM=YES and no extra arguments" >&2
  exit 2
fi
manifest=out/_retained-manifest-20261124.md
[[ -f $manifest ]] || { echo "missing $manifest" >&2; exit 1; }
mapfile -t names < <(awk -F '|' '/^\| / && /仍不能删/ {gsub(/^ +| +$/, "", $2); print $2}' "$manifest")
[[ ${#names[@]} == 48 ]] || { echo "expected 48 directories" >&2; exit 1; }

processed=0 skipped=0 succeeded=0 failed=0
for name in "${names[@]}"; do
  ((processed+=1))
  if [[ ! $name =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "invalid name: $name" >&2; ((failed+=1)); continue
  fi
  dir="out/$name"
  if [[ -L $dir ]]; then
    echo "linked directory: $dir" >&2; ((failed+=1)); continue
  fi
  if [[ ! -e $dir ]]; then
    echo "SKIP missing $dir"; ((skipped+=1)); continue
  fi
  if [[ ! -d $dir ]]; then
    echo "not a directory: $dir" >&2; ((failed+=1)); continue
  fi
  if ! links=$(find -P "$dir" -type l -printf '%p -> %l\n'); then
    echo "link scan failed: $dir" >&2; ((failed+=1)); continue
  fi
  count=0
  [[ -z $links ]] || count=$(printf '%s\n' "$links" | wc -l)
  printf '%s: links=%s\n' "$dir" "$count"
  [[ -z $links ]] || printf '%s\n' "$links"
  if (( apply )); then
    if ! find -P "$dir" -type l -print -delete; then
      echo "phase 1 failed: $dir" >&2; ((failed+=1)); continue
    fi
    if ! remaining=$(find -P "$dir" -type l -print); then
      echo "phase 2 scan failed: $dir" >&2; ((failed+=1)); continue
    fi
    [[ -z $remaining ]] || { echo "phase 2 links remain: $dir" >&2; ((failed+=1)); continue; }
    if ! rm -rf -- "$dir"; then
      echo "phase 2 removal failed: $dir" >&2; ((failed+=1)); continue
    fi
  else
    printf 'DRY-RUN: unlink links, rescan, then remove %s\n' "$dir"
  fi
  ((succeeded+=1))
done
printf 'SUMMARY processed=%d skipped=%d succeeded=%d failed=%d\n' "$processed" "$skipped" "$succeeded" "$failed"
(( skipped == 0 && failed == 0 ))
