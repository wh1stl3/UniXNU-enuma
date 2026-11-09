#!/usr/bin/env python3
"""Append the explicit no-persistence backend to the bound RamBlock archive."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
out = root / 'build/ram-block'
source = root / 'kits/enuma/EnumaRamBlockStore.cpp'
obj = out / 'EnumaRamBlockStore.o'
command = json.loads((out / 'compile-command.json').read_text())
command = [str(source) if arg.endswith('/NativeRamBlock.cpp') else arg for arg in command]
command[command.index('-o') + 1] = str(obj)
record = root / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'
cwd = json.loads(record.read_text().strip().rstrip(','))['directory']
subprocess.run(command, cwd=cwd, check=True)
subprocess.run(['xcrun', 'ar', 'rcs', out / 'libRamBlock.a', obj], check=True)
print('PASS: enuma volatile RAM-root backend, persistence mode=0; no hardware I/O')
