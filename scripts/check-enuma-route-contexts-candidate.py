#!/usr/bin/env python3
"""Pinned host-only handoff check. No device clients, claims or authorization."""
import hashlib
import subprocess
import sys
from pathlib import Path
delivery=Path(__file__).resolve().parents[1]/'out/smmu-route-contexts-candidate-20261114-r2'
PINS={
    'candidate-manifest.json':'3abcd3c0419f9f460d8acb63ed76ccb8075181bc378a71fa568b049ea71d026a',
    'check-final.py':'8ff878c317916b46965a281186df3af93937d80e117eeba25e4d90a757998c07',
}
for name,expected in PINS.items():
    if hashlib.sha256((delivery/name).read_bytes()).hexdigest()!=expected:
        raise SystemExit(f'{name}: frozen handoff digest mismatch')
raise SystemExit(subprocess.call([sys.executable,str(delivery/'check-final.py'),*sys.argv[1:]]))
