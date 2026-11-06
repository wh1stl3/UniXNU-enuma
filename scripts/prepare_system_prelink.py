"""Reuse fixed NativePrelink to emit an offline enuma system-component image.

No device I/O, physical-address selection, board edits or runtime qualification.
Virtual slide is selected from actual image overlap checks, not another board.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
ROOTS = ['com.apple.filesystems.apfs', 'com.apple.driver.AppleMobileFileIntegrity',
         'com.apple.security.AppleImage4', 'com.apple.kext.CoreTrust',
         'com.apple.security.sandbox', 'com.apple.iokit.IOHIDFamily',
         'com.apple.iokit.IOSurface', 'com.apple.iokit.IOMobileGraphicsFamily',
         'com.apple.AppleFSCompression.AppleFSCompressionTypeZlib']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(path, *args):
    return subprocess.check_output(['git', '-c', 'safe.directory=' + path.as_posix(),
                                    '-C', str(path), *args], text=True).strip()


def main():
    source = ROOT / 'out/sources/UniXNU'
    locks = json.loads((ROOT / 'config/sources.lock.json').read_text())['sources']
    kit = source / 'kits/NativePrelink'
    pin = locks['UniXNU']['gitlinks']['kits/NativePrelink']
    if git(source, 'rev-parse', 'HEAD') != locks['UniXNU']['commit'] or git(kit, 'rev-parse', 'HEAD') != pin:
        raise ValueError('Native source pin changed')
    sources = {}
    for name in ['native_prelink.py', 'emit_prelink.py']:
        data = (kit / name).read_bytes()
        tracked = subprocess.check_output(['git', '-C', str(kit), 'show', pin + ':' + name])
        if data != tracked:
            raise ValueError('NativePrelink source changed: ' + name)
        sources[name] = sha(data)
    sys.path.insert(0, str(kit))
    import native_prelink
    import emit_prelink
    kernel_path = ROOT / 'out/ci-runs/39927966148/enuma-macos-platform-39927966148/platform-kernel.macho'
    donor_path = ROOT / 'out/donor-audit/kernelcache.decompressed'
    kernel, donor = kernel_path.read_bytes(), donor_path.read_bytes()
    if sha(kernel) != 'b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d':
        raise ValueError('Platform kernel differs from qualified CI input')
    if sha(donor) != 'f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7':
        raise ValueError('Same-donor Mach-O changed')
    ref = locks['UniXNU-sheng']
    ref_path = Path(ref['path'])
    if git(ref_path, 'rev-parse', 'HEAD') != ref['commit']:
        raise ValueError('Same-donor initializer reference changed')
    board_data = (ref_path / 'board.toml').read_bytes()
    if sha(board_data) != ref['file_sha256']['board.toml']:
        raise ValueError('Initializer source differs from reference pin')
    spec = tomllib.loads(board_data.decode())['kernel']['prelink']
    if spec['kernelcache_sha256'] != sha(donor):
        raise ValueError('Initializer reference is not the identical donor')
    identifier, initializer = spec['early_security_init'].split('=')
    early = {identifier: int(initializer, 0)}
    attempts = []
    chosen = None
    for slide in range(0, -0x2000001, -0x200000):
        try:
            native_prelink.plan(kernel, donor, ROOTS, slide)
            chosen = slide
            attempts.append({'slide': hex(slide), 'binding_plan': 'passed'})
            break
        except ValueError as error:
            attempts.append({'slide': hex(slide), 'binding_plan': 'rejected', 'reason': str(error)})
            if 'collid' not in str(error).lower() and 'overlap' not in str(error).lower():
                raise
    if chosen is None:
        raise ValueError('No non-overlapping virtual placement within the bounded search')
    image, details = emit_prelink.emit(kernel, donor, ROOTS, chosen, early)
    out = ROOT / 'out/full-boot'
    out.mkdir(exist_ok=True)
    target = out / 'system-components.experimental.macho'
    if target.exists():
        raise ValueError('Refuse to overwrite experimental prelink')
    parsed = native_prelink.macho(image)
    occupied = [segment for segment in parsed['segments'] if segment['size']]
    minimum = min(s['va'] for s in occupied)
    maximum = max(s['va'] + s['size'] for s in occupied)
    target.write_bytes(image)
    target.with_suffix('.json').write_text(json.dumps(details, indent=2) + '\n')
    report = {'scope': 'offline actual NativePrelink emission; not a boot image or runtime-qualified kernel',
              'tool_commit': pin, 'tool_sha256': sources,
              'source_kernel_sha256': sha(kernel), 'donor_sha256': sha(donor),
              'roots': ROOTS, 'selected_components': details['components'],
              'early_initializer_reference': {'repository': ref['repository'], 'commit': ref['commit'],
                                              'identical_donor': sha(donor), 'original_va': hex(early[identifier])},
              'virtual_slide_search': attempts, 'selected_virtual_slide': hex(chosen),
              'physical_address_selected': False, 'board_memory_fields_changed': False,
              'path': str(target.relative_to(ROOT)), 'bytes': len(image), 'sha256': sha(image),
              'virtual_min': hex(minimum), 'virtual_end': hex(maximum), 'virtual_span_bytes': maximum - minimum,
              'original_executable_sha256': details['original_executable_sha256'],
              'instruction_inventory': {key: details[key] for key in details if 'instruction' in key or 'dataflow' in key},
              'early_security_initializers': details['early_security_initializers'],
              'limits': ['upstream emitter explicitly leaves runtime_qualified/loadable false',
                         'class/dependency inclusion is not a Qualcomm hardware driver adaptation',
                         'complete ADT, FAT/initrd transport, native root storage, PMGR/security dependencies and error output remain open',
                         'kernel virtual span alone is not proof that the 512MiB entry budget fits complete iPadOS'],
              'device_operations': False}
    (ROOT / 'reports/enuma-system-prelink.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: experimental system prelink emitted ' + str(len(image)) + ' bytes; no boot/runtime claim')


if __name__ == '__main__':
    main()
