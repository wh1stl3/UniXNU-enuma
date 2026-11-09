#!/usr/bin/env python3
"""Wrap restore trust hashes for DarwinBoot's v2-only TrustCache handoff.

Public layouts: xnu-8796.101.5 EXTERNAL_HEADERS/TrustCache/RawTypes.h:58-99.
The legacy v1 restore module has no launch-constraint category; this host-only
adapter uses category/reserved=0. No hashes, hash types, flags or UUID are added
or changed. This representation conversion is not Apple personalization and
has not been qualified on enuma hardware.
"""
import argparse
import hashlib
import struct
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unixnu.ipsw import im4p_payload

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('input', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
raw = im4p_payload(a.input.read_bytes())
version, = struct.unpack_from('<I', raw)
count, = struct.unpack_from('<I', raw, 20)
if version != 1 or len(raw) != 24 + count * 22:
    raise SystemExit('Expected complete restore v1 trust module')
entries = [raw[24+i*22:24+(i+1)*22] for i in range(count)]
if any(not 1 <= e[20] <= 4 for e in entries) or any(x[:20] >= y[:20] for x,y in zip(entries, entries[1:])):
    raise SystemExit('Invalid or unsorted original hashes')
module = struct.pack('<I', 2) + raw[4:24] + b''.join(e+b'\0\0' for e in entries)
bundle = struct.pack('<II', 1, 8) + module
with a.output.open('xb') as f:
    f.write(bundle)
assert all(bundle[32+i*24:54+i*24] == e for i,e in enumerate(entries))
print(f'PASS: {count} unchanged restore hash/type/flags entries; category=0; {len(bundle)} bytes')
print(hashlib.sha256(bundle).hexdigest())
