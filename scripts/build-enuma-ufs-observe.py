#!/usr/bin/env python3
"""Rebuild canonical ShengUfs with both diagnostic-only selection defines."""
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys

tree = Path(__file__).resolve().parents[1]
out = tree / 'build/sheng-ufs'
env = dict(os.environ)
defines = ['NATIVE_UFS_REUSE_DIAGNOSTIC=1', 'NATIVE_UFS_EXTERNAL_STORE_PROVIDER=1', 'NATIVE_UFS_OBSERVATION_ONLY=1']
env['CCC_OVERRIDE_OPTIONS'] = env.get('CCC_OVERRIDE_OPTIONS', '') + ''.join(' +-D' + v for v in defines)
command = [sys.executable, str(tree / 'scripts/build-arm-driver.py'), 'ShengUfs']
out.mkdir(parents=True, exist_ok=True)
result = subprocess.run(command, cwd=tree, env=env)
if result.returncode == 0:
    compile_command = json.loads((out / 'compile-command.json').read_text())
    trace = subprocess.run([*compile_command, '-###'], cwd=tree, env=env, capture_output=True)
    (out / 'effective-compile-command.txt').write_bytes(trace.stdout + trace.stderr)
    lines = (trace.stdout + trace.stderr).decode(errors='replace').splitlines()
    effective = [shlex.split(line) for line in lines if '"-cc1"' in line]
    if trace.returncode or len(effective) != 1 or not all(effective[0].count(v) == 1 and effective[0][effective[0].index(v) - 1] == '-D' for v in defines):
        raise SystemExit('Effective compiler command does not establish both diagnostic defines')
    (out / 'effective-compile-argv.json').write_text(json.dumps(effective[0], indent=2) + '\n')
(out / 'observe-selection.json').write_text(json.dumps({
    'argv': command, 'cwd': str(tree), 'CCC_OVERRIDE_OPTIONS': env['CCC_OVERRIDE_OPTIONS'],
    'defines': defines, 'returncode': result.returncode,
    'status': 'self-checked selection only; final archive/link audits required'}, indent=2) + '\n')
raise SystemExit(result.returncode)
