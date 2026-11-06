"""Build an offline experimental payload through pinned upstream payload.build.

Run under WSL; never changes board.toml, source trees, partitions or firmware.
"""
import ast
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from make_enuma_adt import ROOT, hardware


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pinned(base, commit, relative):
    raw = (base / relative).read_bytes()
    original = subprocess.check_output(['git', '-c', 'safe.directory=' + str(base), '-C', str(base), 'show', commit + ':' + relative])
    if raw != original:
        raise ValueError('modified upstream file: ' + relative)
    return hashlib.sha256(raw).hexdigest()


def main():
    board_before = sha(ROOT / 'board.toml')
    if 'UNIXNU_UNIQUE_CHIP_ID' in __import__('os').environ:
        raise ValueError('this offline recipe intentionally has no private identity input; unset UNIXNU_UNIQUE_CHIP_ID')
    base = ROOT / 'out/sources/UniXNU'
    commit = '5fdbd5d08518bc2d5c196264c56a377dd80cf5ca'
    sources = {r: pinned(base, commit, r) for r in
               ('scripts/unixnu/payload.py', 'scripts/unixnu/util.py', 'scripts/unixnu/__init__.py',
                'scripts/build-original-system-trust.py')}
    sys.path.insert(0, str(base / 'scripts'))
    from unixnu import payload
    out = ROOT / 'out/full-boot'
    if (out / 'payload/payload.img').exists():
        raise ValueError('payload already exists; archive it explicitly before rebuilding (ADT contains fresh entropy)')
    kernel = out / 'system-components.experimental.macho'
    if sha(kernel) != 'be83a7ec0c11132c13b9581d8784a1775584bb97ff5c66484bcbb2e7bef0879e':
        raise ValueError('experimental system prelink changed')
    # Reuse the upstream DER function without executing its fixture-specific CLI.
    syntax = ast.parse((base / 'scripts/build-original-system-trust.py').read_text())
    node = next(n for n in syntax.body if isinstance(n, ast.FunctionDef) and n.name == 'der')
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'pinned-upstream-der', 'exec'), namespace)
    der = namespace['der']
    donor = Path('/mnt/d/Code/PortingiOSLegacy/common/cache/donor-ipados17/components')
    inputs = [('044-76040-038.dmg.trustcache', '4563bdbf6ed8f72237d45dbba3ccde432634338f95c10d79d5d4631678a97c7c'),
              ('044-76034-038.dmg.trustcache', '9742f3d566369e6c48f63b3dc0740b06c243d13c6650e25bbf44616e13d6d097')]
    modules = []
    for name, expected in inputs:
        path = donor / name
        if sha(path) != expected:
            raise ValueError('donor trust cache hash mismatch')
        raw = path.read_bytes()
        tag, sequence, end = der(raw, 0)
        fields, cursor = [], 0
        while cursor < len(sequence):
            kind, data, cursor = der(sequence, cursor)
            fields.append((kind, data))
        if tag != 0x30 or end != len(raw) or [k for k, _ in fields] != [0x16, 0x16, 0x16, 4] or fields[0][1] != b'IM4P':
            raise ValueError('expected complete original IM4P')
        module = fields[3][1]
        if len(module) < 24 or struct.unpack_from('<I', module)[0] != 2 or len(module) != 24 + struct.unpack_from('<I', module, 20)[0] * 24:
            raise ValueError('incomplete version-2 trust cache')
        modules.append(module)
    expected_modules = ['da88460e6e513438d5307e5c526f76497a74754476a24da29f239f0c90120fc2',
                        'd121ba89167e03aafd00fa687c30cd8ebc4ccafd10c1408adb2ba3de12403651']
    if [hashlib.sha256(m).hexdigest() for m in modules] != expected_modules:
        raise ValueError('original module identity mismatch')
    trust = out / 'original-static-system.bundle'
    trust.write_bytes(struct.pack('<III', 2, 12, 12 + len(modules[0])) + b''.join(modules))
    # Ephemeral composition context: observed DRAM information is not board allocation approval.
    total = sum(b['size'] for b in hardware(ROOT / 'out/device/live-fdt.bin')['memory_banks'])
    ctx = SimpleNamespace(tree=ROOT, work=out, logs=out / 'logs', uefi=None,
        args=SimpleNamespace(trust_cache=trust, data_ramdisk=None, gpu_addon=None),
        board={'payload': dict(dram_size=total, size_mib=96, volume='ENUMAEXP', timeout=3,
            title='enuma experimental system input', kernel_args=['-v'],
            adt=dict(tool='scripts/make_enuma_adt.py', ipad_identity=True, owned_memory_size='0x20000000'))})
    image = payload.build(ctx, kernel=kernel)
    # Read actual FAT files back through mtools, independently of staging files (removed upstream).
    entries = {}
    for relative, expected in [('kernel.macho', sha(kernel)), ('kernel.macho.trustcache', sha(trust))]:
        content = subprocess.check_output(['mtype', '-i', str(image), '::/EFI/UniXNU/Payloads/' + relative])
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError('FAT read-back differs: ' + relative)
        entries[relative] = expected
    for relative in ['Payloads/kernel.macho.adt', 'unixnu.toml']:
        content = subprocess.check_output(['mtype', '-i', str(image), '::/EFI/UniXNU/' + relative])
        (out / ('payload-readback.adt' if relative.endswith('.adt') else 'payload-readback.toml')).write_bytes(content)
        entries[relative] = hashlib.sha256(content).hexdigest()
    adt_report = subprocess.check_output(['mtype', '-i', str(image), '::/EFI/UniXNU/Payloads/kernel.macho.adt.json'])
    (ROOT / 'reports/enuma-full-adt.json').write_bytes(adt_report)
    if sha(ROOT / 'board.toml') != board_before:
        raise ValueError('board changed during offline composition')
    report = dict(scope='offline real FAT system-input bundle; not a complete boot image',
                  sources=sources, payload_sha256=sha(image), payload_bytes=image.stat().st_size,
                  fat_readback=entries, trust_original_module_sha256=expected_modules,
                  original_modules_modified=False, hardware_tested=False, full_boot_ready=False,
                  board_unchanged=True, board_sha256=board_before, owned_memory_request=0x20000000,
                  missing=['boot-v3 FDT/initrd transport and SFS discovery', 'visible error output',
                           'native UFS/PMGR/root volume and Data', 'private platform identity seed'])
    (ROOT / 'reports/enuma-full-payload.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: original trust modules and system kernel read back from real FAT; no device action')


if __name__ == '__main__':
    main()
