"""Rebuild the four storage core objects using the captured Apple C/C++ records.

Keeps the original provider compiler and historical receipts immutable. Preparation
is available on Linux; compilation and the combined archive require Apple clang.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SHA = 'f64302555534b0c049f6e56dc7bc3e381ceeddd72a1633e9afa4ae8a268a1a71'
NATIVE_PIN = 'af785c1777161a62931425c2faaa536ce0bebd5b'
SOURCES = ('drivers/EnumaPlatform/EnumaUfsSmmu.c',
           'drivers/EnumaPlatform/EnumaUfsRead.c',
           'drivers/EnumaPlatform/EnumaRootRead.cpp',
           'experiments/root-transport/EnumaRootTransport.c')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invocation(record, old_root, tree, source, output, includes):
    """Only rebase captured paths and replace the input/output operands."""
    args = [s.replace(old_root, str(tree)) for s in record['arguments'][1:]]
    language = '-xc++' if source.suffix == '.cpp' else '-xc'
    if language not in args:
        raise ValueError('compile record language mismatch')
    args[args.index(language) + 1] = str(source)
    args[args.index('-o') + 1] = str(output)
    return ['-I' + str(p) for p in includes] + args


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native-ufs', type=Path, required=True)
    parser.add_argument('--provider', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    options = parser.parse_args()
    out = options.output.resolve()
    out.relative_to(ROOT / 'out')
    out.mkdir(parents=True, exist_ok=False)
    package = ROOT / 'out/ci-single-crypto-41016592491/driver-inputs'
    manifest_path = package / 'manifest.json'
    assert sha(manifest_path) == MANIFEST_SHA
    manifest = json.loads(manifest_path.read_text())
    tree = package / 'tree'
    for name, digest in manifest['files'].items():
        assert sha(tree / name) == digest, name
    native = options.native_ufs.resolve()
    header = native / 'RootWindowRead.h'
    expected = subprocess.check_output(['git', '-C', str(native), 'show',
                                        NATIVE_PIN + ':RootWindowRead.h'])
    assert header.read_bytes() == expected, 'NativeUfs source drift'
    lock = ROOT / 'config/sources.lock.json'
    assert json.loads(lock.read_text())['sources']['UniXNU']['gitlinks']['drivers/NativeUfs'] == NATIVE_PIN
    includes = [ROOT / 'drivers/EnumaPlatform', ROOT / 'experiments/root-transport', native]
    inputs = [Path(__file__), manifest_path, lock, header]
    inputs += [ROOT / s for s in SOURCES]
    inputs += [ROOT / s for s in (
        'drivers/EnumaPlatform/EnumaUfsSmmu.h', 'drivers/EnumaPlatform/EnumaUfsRead.h',
        'drivers/EnumaPlatform/EnumaRootRead.h', 'experiments/root-transport/EnumaRootTransport.h')]
    bindings = {str(p): sha(p) for p in inputs}
    plans = []
    for source_name in SOURCES:
        source = ROOT / source_name
        language = '-xc++' if source.suffix == '.cpp' else '-xc'
        record = next(r for r in manifest['compile_records'] if language in r['arguments'])
        output = out / (source.stem + '.o')
        args = invocation(record, manifest['source_root'], tree, source, output, includes)
        plans.append(dict(source=source_name, record=record['record'], language=language,
                          arguments=args, cwd=str(tree / record['directory_relative']), output=str(output)))
    report = dict(prepared=True, compiled=False, kernel_linked=False,
                  hardware_executed=False, manifest_sha256=MANIFEST_SHA,
                  native_pin=NATIVE_PIN, plans=plans, bindings=bindings)
    (out / 'plan.json').write_text(json.dumps(report, indent=2) + '\n')
    if options.prepare_only:
        print('PASS: four plans, original C/C++ flags, 2259 input bindings; not compiled')
        return
    compiler = subprocess.check_output(['xcrun', '--find', 'clang'], text=True).strip()
    version = subprocess.check_output([compiler, '--version'], text=True)
    assert 'Apple clang version 17.0.0' in version
    assert subprocess.check_output(['xcrun', '--sdk', 'iphoneos', '--show-sdk-version'], text=True).strip() == '18.5'
    sdk = Path(subprocess.check_output(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path'], text=True).strip())
    bindings[str(sdk / 'usr/include/TargetConditionals.h')] = sha(sdk / 'usr/include/TargetConditionals.h')
    provider_dir = options.provider.resolve()
    provider_report = json.loads((provider_dir / 'result.json').read_text())
    assert provider_report['returncode'] == 0 and provider_report['apple_recorded_flags']
    assert provider_report['compiler'] == version, 'provider compiler mismatch'
    for name, digest in provider_report['bindings'].items():
        assert sha(Path(name)) == digest, name
    provider = provider_dir / 'EnumaBlockDevice.o'
    bindings[str(provider)] = sha(provider)
    bindings[str(provider_dir / 'result.json')] = sha(provider_dir / 'result.json')
    completed = []
    for plan in plans:
        command = [compiler, *plan['arguments'], '-idirafter', str(sdk / 'usr/include')]
        result = subprocess.run(command, cwd=plan['cwd'], capture_output=True, text=True)
        stem = Path(plan['source']).stem
        (out / (stem + '.stdout.txt')).write_text(result.stdout)
        (out / (stem + '.stderr.txt')).write_text(result.stderr)
        completed.append(dict(command=command, returncode=result.returncode))
        (out / 'commands.json').write_text(json.dumps(completed, indent=2) + '\n')
        if result.returncode:
            print(result.stderr[-6000:])
        result.check_returncode()
    assert bindings == {p: sha(Path(p)) for p in bindings}, 'source changed during build'
    objects = [Path(plan['output']) for plan in plans] + [provider]
    archive = out / 'libEnumaStorageProvider.apple.a'
    subprocess.run(['xcrun', 'libtool', '-static', '-o', str(archive), *map(str, objects)], check=True)
    symbols = subprocess.check_output(['xcrun', 'nm', '-g', str(archive)], text=True)
    (out / 'symbols.txt').write_text(symbols)
    for name in ('_enuma_smmu_plan', '_enuma_smmu_apply', '_enuma_ufs_capacity10',
                 '_enuma_ufs_prepare_read', '_enuma_root_read', '_enuma_root_transport_read',
                 '_enuma_storage_publish_readonly'):
        definitions = [line for line in symbols.splitlines() if line.endswith(' T ' + name)]
        assert len(definitions) == 1, (name, definitions)
    report.update(compiled=True, compiler=version, matching_c_and_cpp_records=True,
                  bindings=bindings, object_hashes={p.name: sha(p) for p in objects},
                  archive_sha256=sha(archive), provider_instantiated=False)
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: same-compiler provider/core archive, seven unique exports; final kernel link pending')


if __name__ == '__main__':
    main()
