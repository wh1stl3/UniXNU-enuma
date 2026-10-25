"""Review actual DisplayDxe config consumer and same-SoC reference policy."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import uuid
from audit_display_handoff import named_pe, DISPLAY_SHA, PINS, pe_evidence

ROOT = Path(__file__).resolve().parents[1]
REL = 'Platforms/Xiaomi/umiPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-path', type=Path)
    a = p.parse_args()
    if a.tool_path: sys.path.insert(0, str(a.tool_path.resolve()))
    lock = json.loads((ROOT / 'config/system-reuse-sources.lock.json').read_text())
    ref = lock['references'][1]
    base = ROOT / ref['local'].replace('\\', '/')
    umi = subprocess.check_output(['git', '-C', str(base), 'show', ref['evaluation_commit'] + ':' + REL])
    if hashlib.sha256(umi).hexdigest() != ref['files'][REL]['sha256']:
        raise ValueError('tested umi configuration blob changed')
    if not re.search(rb'\{"EnableDisplayThread",\s*0\}', umi):
        raise ValueError('reference does not disable display thread')
    raw = (ROOT / 'out/device/xbl_a.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINS['out/device/xbl_a.bin']:
        raise ValueError('XBL backup changed')
    blob = named_pe(raw, 'DisplayDxe', DISPLAY_SHA)
    checks = {0x1be4: ('bl', '#0x3874'), 0x1bf8: ('ldr', 'w8, [x19, #0x9b8]'),
              0x1bfc: ('cbz', 'w8, #0x1c60'), 0x1c38: ('bl', '#0x5f78'),
              0x1c5c: ('bl', '#0x5f98'), 0x1c60: ('mov', 'x20, xzr'),
              0x37ec: ('add', 'x0, x0, #0x96'), 0x38a4: ('ldr', 'x2, [x8, #0x18]'),
              0x38bc: ('br', 'x2'), 0x22cbc: ('add', 'x0, x0, #0x68'),
              0x22cc0: ('bl', '#0x5e34'), 0x22cc8: ('ldr', 'x0, [x0, #0x18]')}
    pe, code = pe_evidence(blob, [(0x1bd8, 0x1c68), (0x37cc, 0x38d8), (0x22cb0, 0x22cd4)], checks)
    if pe.get_data(0x3e068, 16) != uuid.UUID('bedaeabc-5e70-4d66-9733-213d072b9d04').bytes_le:
        raise ValueError('actual shim HOB GUID differs from PlatformPei provider')
    for rva, text in [(0x2da98, b'EnableDisplayThread'), (0x2e096, b'UEFI Config Lib')]:
        if pe.get_data(rva, len(text) + 1) != text + b'\0':
            raise ValueError('consumer string changed')
    sources = {}
    for rel in ['Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/ShimLoader.c',
                'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/PlatformPei.c',
                'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/ShimLibraries/EFIUefiConfig.h',
                'Silicon/Qualcomm/QcomPkg/Library/ConfigurationMapHelperLib/ConfigurationMapHelperLib.c']:
        sources[rel] = hashlib.sha256((ROOT / 'firmware' / rel).read_bytes()).hexdigest()
    report = dict(scope='actual OEM PE and pinned source contract, no new device action',
                  display_pe_sha256=DISPLAY_SHA, tested_umi_commit=ref['evaluation_commit'],
                  tested_umi_configuration_sha256=hashlib.sha256(umi).hexdigest(), code=code, sources=sources,
                  policy='change only EnableDisplayThread 1->0, retain full FAT and existing driver implementation',
                  interpretation='real GetCfgInfoVal slot0x18; zero branches to entry return without ThreadCreate/Resume; this is not proof of mode initialization or visible pixels',
                  alternative='if the runtime kernel interface was already missing, old code could clear the flag and return too; policy may not affect the actual failure',
                  hardware_tested=False)
    (ROOT / 'reports/enuma-display-thread-policy.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: fixed OEM consumer/slot/zero branch and tested same-SoC policy; no runtime success claimed')


if __name__ == '__main__': main()
