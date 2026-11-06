"""Bind a completed direct-menu development build to its actual BDS PCD/PE.

Read-only build inspection; the selected entry is not physical menu acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
APPLICATION = uuid.UUID('9B665204-A133-47A2-9396-9E2B370A4E25')
PROBE = uuid.UUID('AEF8C196-230E-4E19-A306-D62E21E3D780')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build, output = args.build.resolve(), args.output.resolve()
    build.relative_to(ROOT / 'out')
    output.relative_to(ROOT / 'out')
    if output.exists():
        raise ValueError('refusing to overwrite an existing report')
    result = dict(passed=False, physical_menu_verified=False, deployment_ready=False)
    try:
        report = json.loads((build / 'build-result.json').read_text())
        defines = report['firmware_configuration']['defines']
        if not report['complete'] or not report['direct_menu_selected']:
            raise ValueError('not a completed direct-menu build')
        if defines['ENUMA_DIRECT_MENU'] != '1' or defines['ENUMA_DIAG_STAGE'] != '10':
            raise ValueError('entry selection or diagnostic stop changed')
        products = build / 'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64'
        matches = list(products.rglob('UniXNUDxe/DEBUG/AutoGen.c'))
        if len(matches) != 1:
            raise ValueError('ambiguous generated BDS registration module')
        autogen = matches[0]
        match = re.search(r'_gPcd_FixedAtBuild_PcdUniXNUApplicationFile\[16\]\s*=\s*\{([^}]+)\}', autogen.read_text())
        if not match or bytes(int(v.strip(), 0) for v in match[1].split(',')) != APPLICATION.bytes_le:
            raise ValueError('actual generated PCD does not select UniXNU')
        pe = autogen.parent.parent / 'OUTPUT/UniXNUDxe.efi'
        if APPLICATION.bytes_le not in pe.read_bytes() or PROBE.bytes_le in pe.read_bytes():
            raise ValueError('actual PE entry GUID missing or still points at Probe')
        app = list(products.rglob('UniXNU/OUTPUT/UniXNU.efi'))
        if len(app) != 1:
            raise ValueError('actual UniXNU application missing')
        fd = ROOT / report['fd']
        if sha(fd) != report['fd_sha256']:
            raise ValueError('FD hash differs from build result')
        if sha(build / 'source-manifest.json') != report['source_manifest_sha256']:
            raise ValueError('source manifest differs from build result')
        result.update(passed=True, application_guid=str(APPLICATION),
                      early_stop_retained=True, full_UniXNURun_executed=False,
                      inputs={str(p.relative_to(ROOT)): sha(p) for p in
                              [autogen, pe, app[0], fd, build / 'source-manifest.json', Path(__file__)]})
    except Exception as exc:
        result['error'] = str(exc)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
