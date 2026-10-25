"""Host sanitize the production pure decoder/capture; no device I/O or physical access."""
import hashlib
import json
from pathlib import Path
from check_enuma_drivers import run
ROOT=Path(__file__).resolve().parents[1]


def main():
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
    out=ROOT/'out/inherited-scanout'; out.mkdir(exist_ok=True)
    sources=[lib/'Decode.c',lib/'Capture.c']
    flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fno-builtin','-I'+str(lib)]
    checks=[run([*flags,'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',
                 *sources,ROOT/'tests/inherited_scanout.c','-o',out/'host-test'])]
    checks.append(run([out/'host-test']))
    for source in sources:
        checks.append(run([*flags,'-target','aarch64-none-elf','-ffreestanding','-O2','-c',source,'-o',out/(source.stem+'.o')]))
        undefined=run(['llvm-nm','--undefined-only',out/(source.stem+'.o')])
        if undefined['stdout'].strip():
            raise ValueError('Unexpected freestanding dependency: '+undefined['stdout'])
        checks.append(undefined)
    report=dict(scope='production decoder/capture with synthetic snapshots and callbacks only',
                sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*sources,lib/'InheritedScanout.h',ROOT/'tests/inherited_scanout.c']},
                checks=checks,hardware_tested=False,gop_published=False,pixel_or_mmio_access=False,
                capture_read_limit=267,required_external_checks=['activity','blend/occlusion','CPU address relationship','refresh','dual-link/global coordinate topology'])
    (ROOT/'reports/enuma-inherited-scanout-host.json').write_text(json.dumps(report,indent=2)+'\n')
    print(checks[1]['stdout'].strip())


if __name__=='__main__':
    main()
