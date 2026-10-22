"""Read immutable upstream file evidence through gh; store hashes and selected lines."""
import base64
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('Project-Silicium/Mu-Silicium', '42fe563791e51bf5500c2e470ed294ca0c94b97c', [
        'LICENSE', 'Platforms/Xiaomi/aliothPkg/alioth.dsc',
        'Platforms/Xiaomi/aliothPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c',
        'Silicon/Qualcomm/KonaPkg/KonaPkg.dsc.inc', 'Resources/Configs/alioth.toml']),
    ('MiCode/Xiaomi_Kernel_OpenSource', '52a2f180865f8368828985d6384130acd093fa93', [
        'COPYING', 'drivers/input/touchscreen/nt36523/nt36xxx.c',
        'drivers/input/touchscreen/nt36523/nt36xxx.h',
        'drivers/input/touchscreen/nt36523/nt36xxx_mem_map.h']),
]


def main():
    results = []
    env = dict(os.environ, GODEBUG='http2client=0')
    for repo, commit, paths in SOURCES:
        for path in paths:
            command = ['gh', 'api', f'repos/{repo}/contents/{path}?ref={commit}']
            response = json.loads(subprocess.check_output(command, env=env))
            data = base64.b64decode(response['content'])
            text = data.decode('utf-8')
            matches = [{'line': index, 'text': line} for index, line in enumerate(text.splitlines(), 1)
                       if re.search(r'SPDX|license|License|Kona|SM8250|sm8250|NVT-ts-spi|novatek|spi_sync|spi_setup|request.*irq|input_report|CHIP_ID|NT36523|Ufs|UFS|Gic|GIC|SerialPort|Display|Framebuffer', line)]
            results.append({'repository': repo, 'commit': commit, 'path': path,
                            'url': f'https://github.com/{repo}/blob/{commit}/{path}',
                            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                            'selected_lines': matches[:60], 'total_matching_lines': len(matches)})
    report = {'scope': 'source reuse candidates only; no firmware built or device tested', 'files': results}
    (ROOT / 'reports/reuse-source-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Pinned {len(results)} upstream file references; no source tree copied')


if __name__ == '__main__':
    main()
