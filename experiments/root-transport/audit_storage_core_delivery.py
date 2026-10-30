"""Bind a downloaded Apple core/provider build to local source and kernel imports."""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--abi', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    out.relative_to(ROOT / 'out')
    out.mkdir(parents=True, exist_ok=False)
    artifact = a.artifact.resolve()
    core = artifact / 'apple-core'
    provider = artifact / 'apple-build'
    report = json.loads((core / 'result.json').read_text())
    assert report['compiled'] and report['matching_c_and_cpp_records']
    assert report['kernel_linked'] is False and report['hardware_executed'] is False
    prefix = '/Users/runner/work/UniXNU-enuma/UniXNU-enuma/'
    checked = {}
    for name, digest in report['bindings'].items():
        if name.startswith('/Applications/Xcode_16.4.app/'):
            continue  # SDK bytes are not redistributed; CI version and digest retained.
        assert name.startswith(prefix), name
        relative = name[len(prefix):]
        if relative.startswith('out/storage-provider-20261030/apple-build/'):
            path = provider / relative.split('apple-build/', 1)[1]
        elif relative == 'out/storage-provider-20261030/NativeUfs/RootWindowRead.h':
            path = ROOT / 'out/sources/UniXNU/drivers/NativeUfs/RootWindowRead.h'
        else:
            path = ROOT / relative
        assert sha(path) == digest, name
        checked[str(path)] = digest
    abi_path = a.abi.resolve()
    abi = json.loads(abi_path.read_text())
    for name, digest in abi['source_bindings'].items():
        assert sha(Path(name)) == digest, name
    sys.path.insert(0, str(ROOT / 'out/sources/UniXNU/kits/NativePrelink'))
    import native_prelink as np

    def symbols(path):
        data = path.read_bytes()
        m = np.macho(data)
        assert m['kind'] == 1
        at = next(at for cmd, at, _ in m['commands'] if cmd == 2)
        sy, count, st, _ = struct.unpack_from('<4I', data, at + 8)
        defined, undefined = set(), set()
        for i in range(count):
            ix, kind, _, _, _ = struct.unpack_from('<IBBHQ', data, sy + i * 16)
            if kind & 0xe0:
                continue
            name = data[st + ix:data.index(b'\0', st + ix)].decode()
            if kind == 1:
                undefined.add(name)
            elif kind & 1 and kind & 0xe:
                defined.add(name)
        return defined, undefined

    archive = core / 'libEnumaStorageProvider.apple.a'
    assert sha(archive) == report['archive_sha256']
    members = subprocess.check_output(['/usr/bin/llvm-ar', 't', str(archive)], text=True).splitlines()
    expected = report['object_hashes']
    assert len(members) == 5 and set(members) == set(expected), members
    defined, undefined = set(), set()
    for name in members:
        obj = out / name
        obj.write_bytes(subprocess.check_output(['/usr/bin/llvm-ar', 'p', str(archive), name]))
        assert sha(obj) == expected[name], name
        if name == 'EnumaBlockDevice.o':
            assert sha(obj) == sha(provider / name)
        d, u = symbols(obj)
        assert not (d & defined), sorted(d & defined)
        defined |= d
        undefined |= u
    kernel = ROOT / 'out/platform-single-crypto-20261030/fixture1/kernel.macho'
    data = kernel.read_bytes()
    exports = {name: va for va, names in np.exports(data, np.macho(data)).items() for name in names}
    storage = abi['required_storage_bindings']
    external = undefined - defined
    missing = external - exports.keys() - storage.keys()
    assert not missing, sorted(missing)
    checked.update({str(archive): sha(archive), str(core / 'result.json'): sha(core / 'result.json'),
                    str(abi_path): sha(abi_path), str(kernel): sha(kernel), str(Path(__file__)): sha(Path(__file__))})
    result = dict(passed=True, archive_sha256=sha(archive), same_apple_c_cpp_records=True,
                  source_kernel_imports={n: hex(exports[n]) for n in sorted(external & exports.keys())},
                  original_storage_imports={n: storage[n] for n in sorted(external & storage.keys())},
                  unclassified_imports=[], bindings=checked, kernel_linked=False,
                  provider_instantiated=False, hardware_executed=False, root_mounted=False)
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: five archive members verified; {len(external)} classified imports; no final kernel link')


if __name__ == '__main__':
    main()
