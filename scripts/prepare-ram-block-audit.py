#!/usr/bin/env python3
"""Install the device-local static storage ABI audit into the build tree.

The interface-audit.json consumed by scripts/build-virtio-mmio-bindings.py normally comes from
scripts/audit-storage-interface.py, which needs a macOS host and a live-gdb observation. enuma
commits the static equivalent (scripts/data/ram-block-interface-audit.json), derived from the
public Darwin 23 IOStorageFamily source and the prelinked kernel.macho by
scripts/gen-ram-block-audit.py, with the live-only fields recorded from the marble/fuxi
ipados-17.7.11-21H461 record. This script copies that file to the path the base binding script
reads, so the base repository and its scripts stay unmodified.
"""
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent          # {tree}/scripts
TREE = SCRIPT_DIR.parent                              # {tree}
source = SCRIPT_DIR / 'data' / 'ram-block-interface-audit.json'
destination = TREE / 'build/storage-abi/interface-audit.json'

if not source.is_file():
    raise SystemExit(f'missing device-local storage ABI audit: {source}')
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, destination)
print(f'PASS: interface-audit.json -> {destination}')
