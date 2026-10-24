"""Compatibility adapter; firmware build implementation lives in uefi-enuma."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'firmware'


def _backend():
    # Validate the fixed checkout before executing any firmware-owned Python.
    pin = json.loads((ROOT/'config/uefi-source.lock.json').read_text())
    def git(*args):
        return subprocess.check_output(['git','-c','safe.directory='+SOURCE.as_posix(),'-C',str(SOURCE),*args],text=True).strip()
    if git('rev-parse','HEAD') != pin['commit'] or git('status','--porcelain','--ignore-submodules=all'):
        raise ValueError('firmware checkout must be clean and match the device lock')
    for name, wanted in pin['file_sha256'].items():
        if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() != wanted:
            raise ValueError('firmware source hash mismatch: '+name)
    relative = 'Resources/Scripts/build_enuma_firmware.py'
    if relative not in pin['file_sha256']:
        raise ValueError('firmware build entry is not hash-locked')
    spec = importlib.util.spec_from_file_location('enuma_firmware_build',SOURCE/relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def diagnostic_guid_defines(value):
    return _backend().diagnostic_guid_defines(value)


def source_helper():
    return _backend().source_helper()


def apply_patch_series(patches):
    return _backend().apply_patch_series(patches)


if __name__ == '__main__':
    # The preflight expects the staged Mu tree with every diagnostic patch
    # reversed. A build that stopped between the apply and the reversion, or a
    # patch that was removed after it had been applied, leaves the tree in a
    # state the preflight rejects, so restore it before building.
    subprocess.run([sys.executable, str(ROOT / 'scripts/restore_mu_baseline.py'),
                    '--device-root', str(ROOT)], cwd=ROOT, check=True)
    _backend().main(device_root=ROOT)
