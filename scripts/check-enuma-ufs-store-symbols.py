#!/usr/bin/env python3
"""Offline LLVM nm audit: all duplicate strong definitions, plus store ownership.

Candidate mode additionally requires native/prelink and the actual native link
map. Pass EVERY final force-loaded archive, not just ShengUfs/RamBlock.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess

STORE = {'_native_ufs_store_' + s for s in ('mode', 'open', 'read', 'write', 'sync', 'gpt_check')}


def definitions(paths):
    result = defaultdict(list)
    for path in paths:
        run = subprocess.run(['llvm-nm', '-A', '-g', '--defined-only', str(path)],
                             capture_output=True, text=True, check=True)
        for line in run.stdout.splitlines():
            match = re.fullmatch(r'(.+):\s*(?:[0-9a-fA-F]+\s+)?([A-Za-z])\s+(\S+)', line)
            if not match:
                raise ValueError('Unparsed nm definition: ' + line)
            owner, kind, symbol = match.groups()
            if kind.isupper() and kind not in ('U', 'W', 'V'):
                result[symbol].append(owner)
    return dict(result)


def audit(archives, native=None, prelink=None, link_map=None):
    defs = definitions(archives)
    duplicates = {s: owners for s, owners in defs.items() if len(owners) > 1}
    assert not duplicates, json.dumps(duplicates, indent=2)
    stores = {s: defs.get(s, []) for s in sorted(STORE)}
    assert all(len(owners) == 1 and owners[0].endswith(':EnumaRamBlockStore.o')
               for owners in stores.values()), stores
    report = {'validation': 'self-checked', 'archives': [str(p) for p in archives],
              'duplicate_strong_definitions': duplicates, 'store_owners': stores}
    if native is not None:
        for image in (native, prelink):
            image_defs = definitions([image])
            assert all(len(image_defs.get(s, [])) == 1 for s in STORE), str(image)
        text = link_map.read_text(errors='replace')
        # Apple ld map: object file index table, followed by address/size/index/symbol.
        owners = {}
        for index, name in re.findall(r'^\[\s*(\d+)\]\s+(.+)$', text, re.M):
            owners[index] = name
        mapped = {}
        for symbol in sorted(STORE):
            matches = re.findall(r'^\S+\s+\S+\s+\[\s*(\d+)\]\s+' + re.escape(symbol) + r'\s*$', text, re.M)
            assert len(matches) == 1, (symbol, matches)
            owner = owners[matches[0]]
            assert re.search(r'(?:\(|:)EnumaRamBlockStore\.o\)?$', owner), owner
            mapped[symbol] = owner
        report['final_images'] = [str(native), str(prelink)]
        report['link_map_store_owners'] = mapped
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', action='append', required=True, type=Path)
    parser.add_argument('--native', type=Path)
    parser.add_argument('--prelink', type=Path)
    parser.add_argument('--link-map', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert all((args.native, args.prelink, args.link_map)) or not any((args.native, args.prelink, args.link_map))
    report = audit(args.archive, args.native, args.prelink, args.link_map)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('self-checked: no duplicate strong definitions; six stores from EnumaRamBlockStore.o')


if __name__ == '__main__':
    main()
