"""Host ABI/provider checks using the real current map and helper functions."""
import hashlib
import json
from pathlib import Path
from check_enuma_drivers import run

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'firmware'
    cfg = source / 'Platforms/Xiaomi/enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c'
    helper = source / 'Silicon/Qualcomm/QcomPkg/Library/ConfigurationMapHelperLib/ConfigurationMapHelperLib.c'
    out = ROOT / 'out/full-boot/display-thread-policy'; out.mkdir(exist_ok=True)
    for p, name in [(cfg, 'ConfigMap.inc'), (helper, 'ConfigHelper.inc')]:
        raw = p.read_text()
        (out / name).write_text('\n'.join(line for line in raw.splitlines() if not line.startswith('#include')) + '\n')
    package = source / 'Silicon/Qualcomm/QcomPkg'
    flags = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
             '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-I' + str(out),
             '-I' + str(package / 'Include/Library'), '-I' + str(package / 'Library/PlatformPeiLib/ShimLibraries')]
    records = [run([*flags, ROOT / 'tests/display_config_contract.c', '-o', out / 'config-test'])]
    records.append(run([out / 'config-test']))
    report = dict(scope='actual production map/helper and ABI header with host adapters; no firmware/device execution',
                  source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [cfg, helper]},
                  checks=records, hardware_tested=False)
    (ROOT / 'reports/enuma-display-config-contract.json').write_text(json.dumps(report, indent=2) + '\n')
    print(records[-1]['stdout'].strip())


if __name__ == '__main__': main()
