#!/usr/bin/env python3
"""Run the pinned isolated host/ARM64 check, never build or boot a device image."""
import hashlib
import subprocess
import sys
from pathlib import Path
delivery=Path(__file__).resolve().parents[1]/'out/smmu-route-contexts-20261114-r1'
for name,expected in {
    'sourcepin.json':'9b7293b7dca566182f3fd882001632c73b76fad6bbdf452837f365fa932e9ccd',
    'minimal.patch':'dc33b132fd238053c27c40b46f2b0addee3b909f182f450c205715e6bb5b3bde',
}.items():
    if hashlib.sha256((delivery/name).read_bytes()).hexdigest()!=expected:
        raise SystemExit(f'{name}: isolated delivery digest mismatch')
raise SystemExit(subprocess.call([sys.executable,str(delivery/'check.py'),*sys.argv[1:]]))
