"""Read-only R-022 archive/source binding audit; writes only a new output file.

No device, build, historical-path execution, or qualification replacement.
Run with WSL Python from the migrated device checkout; --output must not exist.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def local_path(value):
    """Only repository-relative references; never follow old absolute paths."""
    path = Path(value)
    if path.is_absolute() or ':' in value or '\\' in value:
        raise ValueError('non-relative evidence reference: ' + value)
    resolved = (ROOT / path).resolve()
    resolved.relative_to(ROOT)
    return resolved


def audit():
    qpath = ROOT / 'reports/enuma-native-route-qualification.json'
    q = json.loads(qpath.read_text(encoding='utf-8'))
    archive = local_path(q['archive'])
    failures = []
    checks = []

    def check(label, passed, **details):
        checks.append(dict(check=label, passed=bool(passed), **details))
        if not passed:
            failures.append(label)

    check('qualification equals frozen archive byte for byte',
          qpath.read_bytes() == (archive / 'qualification.json').read_bytes())
    expected = dict(hardware_review='R-022', hold_us=8000000,
                    firmware_commit='8680ea79d6fd14d4526d314f430e9812955cb78a',
                    image_sha256='f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b',
                    roi_width=256, roi_height=96, maximum_framebuffer_reads=73728,
                    framebuffer_writes=49152, maximum_barriers=3,
                    execution_approval_required=True, global_debug=False)
    for key, value in expected.items():
        check('frozen scope ' + key, q.get(key) == value)
    check('frozen FD identity', q['files']['SILICIUM_UEFI.fd']['sha256'] ==
          '7bee85343b6f8837c1081f5cb08db939facfc1ec084c6f498d918ded1e02f035')
    for name, binding in q['files'].items():
        path = local_path(q['archive'] + '/' + name)
        actual = digest(path) if path.is_file() else None
        check('archive/' + name, actual == binding['sha256'] and
              path.stat().st_size == binding['bytes'], sha256=actual)
    check('image pointer resolves inside archive',
          local_path(q['image']) == archive / 'image.img')
    report = json.loads((ROOT / 'reports/enuma-console-readiness.json').read_text(encoding='utf-8'))
    for name, binding in report['sources'].items():
        path = local_path(name)
        actual = digest(path) if path.is_file() else None
        check('console source/' + name, actual == binding['sha256'], sha256=actual)
        if path.is_file():
            lines = path.read_text(encoding='utf-8').splitlines()
            for anchor in binding['anchors']:
                line = anchor['line']
                check('anchor/' + name + ':' + str(line),
                      0 < line <= len(lines) and anchor['text'] in lines[line - 1])
    for module, entries in report['actual_link_bindings'].items():
        for binding in entries:
            path = local_path(binding['path'])
            check('actual link/' + module, path.is_file() and digest(path) == binding['sha256'])
    return dict(scope='migration-time archive integrity and existing source/line/link bindings only',
                checks=checks, failures=failures, passed=not failures,
                firmware_commit=q['firmware_commit'], image_sha256=q['image_sha256'],
                hardware_executed=False, device_action=False, new_firmware_qualified=False,
                screen_log_verified=False, gop_admitted=False, menu_executed=False,
                limitations=['A matching historical qualification is not approval to execute.',
                             'No build, complete firmware source requalification, or live device state check.',
                             'Current staging is not proof of the patched Core compilation inputs.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to((ROOT / 'out').resolve())
    if output.exists():
        parser.error('output exists; preserve prior evidence and choose a new filename')
    result = audit()
    result['audit_script_sha256'] = digest(Path(__file__))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(passed=result['passed'], checks=len(result['checks']),
                          failures=result['failures']), indent=2))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
