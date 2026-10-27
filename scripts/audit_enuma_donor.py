"""Audit the fixed iPadOS donor and binding plans; never emit a bootable image.

Run with Windows Python. The existing read-only Linux LZFSE decoder is invoked
through Ubuntu-22.04; all generated data stays in this repository's out/.
The sheng slide/roots are comparison inputs, not adopted board configuration.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
UNIXNU = '5fdbd5d08518bc2d5c196264c56a377dd80cf5ca'
SHENG = 'a599a1a8a92093b5077543e071b72130769eb325'
PRELINK = '2b6ffb50117eee820b98aca9bd51b5c7dfb2970e'
DECODER_SHA = 'f89442c9e68063b115df9fcc6defa96c9f5affedc44fa6751dc4d67d3c18c4d4'
KERNEL_SHA = 'b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(path, *args):
    return subprocess.check_output(['git', '-c', 'safe.directory='+path.as_posix(), '-C', str(path), *args])


def locked_file(path, commit, name):
    if git(path, 'rev-parse', 'HEAD').decode().strip() != commit:
        raise ValueError('Source revision changed: '+str(path))
    data = git(path, 'show', commit+':'+name)
    if (path/name).read_bytes().replace(b'\r\n', b'\n') != data.replace(b'\r\n', b'\n'):
        raise ValueError('Source file changed: '+name)
    return data


def linux(path):
    path = path.resolve()
    if path.drive.lower() != 'd:':
        raise ValueError('This local decoder workflow expects the D: workspace')
    return '/mnt/d/'+path.as_posix()[3:]


def write_report(name, data):
    (ROOT/'reports'/name).write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')


def main():
    source = ROOT/'out/sources/UniXNU'
    parser_data = locked_file(source, UNIXNU, 'scripts/unixnu/ipsw.py')
    reference = Path('D:/Code/PortingiOSLegacy/common/sources/UniXNU-sheng')
    reference_data = locked_file(reference, SHENG, 'board.toml')
    spec = tomllib.loads(reference_data.decode())['kernel']['prelink']
    inputs = json.loads((ROOT/'reports/input-audit.json').read_text(encoding='utf-8'))
    component = inputs['donor']['components']['KernelCache']
    raw = Path(component['path']).read_bytes()
    if sha(raw) != component['sha256'] or hashlib.sha384(raw).hexdigest() != component['manifest_digest']:
        raise ValueError('Donor container no longer matches audited manifest input')
    decoder = Path('D:/Code/PortingiOSLegacy/common/tools/apfs-fuse-linux/bin/lzfse')
    if sha(decoder.read_bytes()) != DECODER_SHA:
        raise ValueError('Decoder binary changed')
    sys.path.insert(0, str(source/'scripts'))
    from unixnu.ipsw import im4p_payload
    out = ROOT/'out/donor-audit'
    out.mkdir(parents=True, exist_ok=True)
    packed, fat_path = out/'kernelcache.lzfse', out/'kernelcache.fat'
    packed.write_bytes(im4p_payload(raw))
    subprocess.run(['wsl', '-d', 'Ubuntu-22.04', '--', linux(decoder), '-decode',
                    '-i', linux(packed), '-o', linux(fat_path)], check=True, timeout=60)
    data = fat_path.read_bytes()
    fat_sha = sha(data)
    slices = []
    if data[:4] == b'\xca\xfe\xba\xbe':
        count = struct.unpack_from('>I', data, 4)[0]
        if count > 32 or 8+count*20 > len(data):
            raise ValueError('Invalid FAT table extent')
        slices = [struct.unpack_from('>5I', data, 8+20*i) for i in range(count)]
        arm64 = [s for s in slices if s[0] == 0x100000c]
        if len(arm64) != 1:
            raise ValueError('Expected one ARM64 slice')
        _, _, offset, size, _ = arm64[0]
        if offset < 8+count*20 or offset+size > len(data):
            raise ValueError('ARM64 slice outside FAT')
        data = data[offset:offset+size]
    if sha(data) != spec['kernelcache_sha256']:
        raise ValueError('Decoded bytes differ from the fixed same-donor reference pin')
    kit = source/'kits/NativePrelink'
    locked_file(kit, PRELINK, 'native_prelink.py')
    module_spec = importlib.util.spec_from_file_location('enuma_donor_parser', kit/'native_prelink.py')
    native = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(native)
    macho = native.macho(data)
    (out/'kernelcache.decompressed').write_bytes(data)
    write_report('enuma-donor-decompression.json', dict(
        scope='offline donor decompression and pinned ordinary ARM64 parser; no prelink or device execution',
        product='iPad7,1', build='21H461', device_class='j120ap', container_sha256=sha(raw),
        manifest_sha384_match=True, im4p_parser_sha256=sha(parser_data), decoder_path=str(decoder),
        decoder_binary_sha256=DECODER_SHA,
        decoder_source_provenance='existing local tool; source revision not independently established in this run',
        fat_sha256=fat_sha, slices=slices, macho_sha256=sha(data), macho_bytes=len(data),
        macho_kind=macho['kind'], segment_names=[s['name'] for s in macho['segments']],
        native_prelink_commit=PRELINK, prelink_ready=False,
        matches_fixed_sheng_same_donor_pin=True, reference_commit=SHENG))
    info = next(s for s in macho['segments'] if s['name'] == '__PRELINK_INFO')
    at = native.backed_offset(macho['segments'], info['va'], info['filesize'], len(data))
    metadata = native.unserialize_xml(data[at:at+info['filesize']])['_PrelinkInfoDictionary']
    entries = {entry['CFBundleIdentifier']:entry for entry in metadata}
    if len(entries) != len(metadata):
        raise ValueError('Duplicate donor module identifiers')
    kernel_path = ROOT/'out/ci-runs/39927966148/enuma-macos-platform-39927966148/platform-kernel.macho'
    kernel = kernel_path.read_bytes()
    if sha(kernel) != KERNEL_SHA:
        raise ValueError('Source platform kernel differs from audited CI artifact')
    cases = []
    for label, roots in [('AMFI dependency inspection', ['com.apple.driver.AppleMobileFileIntegrity']),
                         ('APFS dependency inspection', ['com.apple.filesystems.apfs']),
                         ('reference roots comparison only', spec['roots'])]:
        todo, seen = list(roots), set()
        while todo:
            name = todo.pop()
            if name in seen:
                continue
            if name not in entries:
                raise ValueError('Missing donor dependency: '+name)
            seen.add(name)
            todo.extend(entries[name].get('OSBundleLibraries') or {})
        case = dict(label=label, roots=roots, dependency_closure=sorted(seen),
                    comparison_slide=spec['slide'], board_configuration_changed=False)
        try:
            plan = native.plan(kernel, data, roots, int(spec['slide'], 0))
            case.update(binding_plan_passed=True, components=plan['components'],
                        pointer_counts=plan['pointer_counts'], runtime_qualified=False)
            (out/(label.split()[0].lower()+'-plan.json')).write_text(json.dumps(plan, indent=2)+'\n')
        except ValueError as error:
            case.update(binding_plan_passed=False, error=str(error))
        cases.append(case)
    write_report('enuma-donor-closure-audit.json', dict(
        scope='offline dependency/binding comparison, reference slide is not adopted or authorized as enuma placement',
        donor_sha256=sha(data), native_sha256=sha(kernel), donor_module_count=len(entries), cases=cases,
        images_emitted=False, device_operations=False))
    print('PASS: fixed donor decoded and parsed; binding cases='+str([c['binding_plan_passed'] for c in cases]))


if __name__ == '__main__':
    main()
