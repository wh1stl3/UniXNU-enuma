"""Read-only source/donor/FDT audit. Outputs evidence, never board values or images."""
import argparse
import hashlib
import json
import plistlib
import struct
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def hashes(path):
    sha256, sha384 = hashlib.sha256(), hashlib.sha384()
    with path.open('rb') as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            sha256.update(chunk)
            sha384.update(chunk)
    return {'path': path.as_posix(), 'bytes': path.stat().st_size,
            'sha256': sha256.hexdigest(), 'sha384': sha384.hexdigest()}


def parse_fdt(data):
    """Bounded FDT v17 reader; retain raw property bytes, no address translation."""
    if len(data) < 40:
        raise ValueError('truncated FDT header')
    magic, total, off_struct, off_strings, off_reserve, version, compatible, _, strings_size, struct_size = struct.unpack_from('>10I', data)
    if magic != 0xD00DFEED or total > len(data) or total < 40 or version != 17 or compatible > 17:
        raise ValueError('unsupported FDT header')
    spans = [(off_struct, off_struct + struct_size), (off_strings, off_strings + strings_size)]
    if any(a < 40 or b > total or a > b for a, b in spans) or max(a for a, _ in spans) < min(b for _, b in spans):
        raise ValueError('invalid FDT block bounds')
    if off_struct % 4 or off_reserve % 8 or not 40 <= off_reserve < total:
        raise ValueError('invalid FDT block alignment')
    nodes, stack, at = {}, [], off_struct
    end = off_struct + struct_size
    strings = data[off_strings:off_strings + strings_size]
    while at + 4 <= end:
        token = struct.unpack_from('>I', data, at)[0]
        at += 4
        if token == 1:
            stop = data.find(b'\0', at, end)
            if stop < 0:
                raise ValueError('unterminated node name')
            name = data[at:stop].decode('ascii')
            if '/' in name or (not stack and (name or nodes)):
                raise ValueError('invalid root/node name')
            path = '/' if not stack else stack[-1].rstrip('/') + '/' + name
            if path in nodes:
                raise ValueError('duplicate node')
            nodes[path] = {}
            stack.append(path)
            at = (stop + 4) & ~3
        elif token == 2:
            if not stack:
                raise ValueError('unbalanced END_NODE')
            stack.pop()
        elif token == 3:
            if not stack or at + 8 > end:
                raise ValueError('property outside node or truncated')
            size, nameoff = struct.unpack_from('>II', data, at)
            at += 8
            stop = strings.find(b'\0', nameoff)
            if nameoff >= len(strings) or stop < 0 or at + size > end:
                raise ValueError('invalid property bounds')
            name = strings[nameoff:stop].decode('ascii')
            if name in nodes[stack[-1]]:
                raise ValueError('duplicate property')
            nodes[stack[-1]][name] = data[at:at + size]
            at = (at + size + 3) & ~3
        elif token == 4:
            pass
        elif token == 9:
            if stack or '/' not in nodes:
                raise ValueError('unbalanced tree')
            return nodes
        else:
            raise ValueError(f'unknown FDT token {token}')
    raise ValueError('missing FDT_END')


def strings(value):
    return value.rstrip(b'\0').decode('ascii').split('\0')


def cells(value):
    if len(value) % 4:
        raise ValueError('non-cell property')
    return list(struct.unpack(f'>{len(value) // 4}I', value))


def fdt_inventory(path):
    nodes = parse_fdt(path.read_bytes())
    selected = []
    text_keys = {'compatible', 'status', 'device_type', 'model', 'method', 'reg-names',
                 'clock-names', 'novatek,fw-name', 'novatek,mp-name'}
    cell_keys = {'reg', 'interrupts', 'interrupt-parent', 'iommus', 'clocks',
                 '#address-cells', '#size-cells', 'clock-frequency', 'qcom,chipid',
                 'novatek,irq-gpio', 'novatek,reset-gpio', 'qcom,mdss-dsi-panel-width',
                 'qcom,mdss-dsi-panel-height', 'qcom,dsi-default-panel', 'phandle'}
    for name, props in nodes.items():
        compat = props.get('compatible', b'').lower()
        if not (name in ('/', '/soc') or name.startswith(('/memory', '/cpus/', '/reserved-memory/', '/psci'))
                or any(x in compat for x in (b'gic', b'armv8-timer', b'ufshc', b'ufs-phy', b'smmu', b'kgsl', b'novatek'))
                or 'dsi_k81' in name or 'mdss_dsi' in name or 'novatek@' in name):
            continue
        properties = {}
        for key, value in props.items():
            if key in text_keys:
                properties[key] = strings(value)
            elif key in cell_keys:
                properties[key] = [hex(x) for x in cells(value)]
            elif key == 'ranges':
                properties[key] = [hex(x) for x in cells(value)]
        parent = name.rsplit('/', 1)[0] or '/'
        parent_props = nodes.get(parent, {})
        selected.append({'path': name, 'properties': properties,
                         'parent_address_cells': cells(parent_props.get('#address-cells', struct.pack('>I', 2))),
                         'parent_size_cells': cells(parent_props.get('#size-cells', struct.pack('>I', 1)))})
    return {'input': hashes(path), 'node_count': len(nodes), 'selected_nodes': selected,
            'scope': 'historical Android FDT; reg cells are bus-relative, not translated physical addresses; presence is not driver binding',
            'excluded': ['chosen bootargs', 'serial-number', 'unique identifiers']}


def donor_audit(cache, board):
    manifest_path = cache / 'BuildManifest.plist'
    manifest = plistlib.loads(manifest_path.read_bytes())
    expected = board['ipsw']
    if (manifest['ProductVersion'], manifest['ProductBuildVersion']) != (expected['version'], expected['build']):
        raise ValueError('donor version/build mismatch')
    if expected['product'] not in manifest['SupportedProductTypes']:
        raise ValueError('donor product mismatch')
    candidates = [(i, identity) for i, identity in enumerate(manifest['BuildIdentities'])
                  if identity['Info']['DeviceClass'] == expected['device_class']
                  and identity['Info']['RestoreBehavior'] == 'Erase'
                  and int(identity['ApChipID'], 0) == expected['chip_id']
                  and int(identity['ApBoardID'], 0) == expected['board_id']]
    if len(candidates) != 1:
        raise ValueError('ambiguous or missing donor identity')
    index, identity = candidates[0]
    components = {}
    for name in ('KernelCache', 'DeviceTree', 'StaticTrustCache', 'Cryptex1,SystemTrustCache', 'OS', 'Cryptex1,SystemOS'):
        item = identity['Manifest'][name]
        member = item['Info']['Path']
        path = cache / 'components' / Path(member).name
        result = hashes(path)
        result['member'] = member
        result['manifest_digest'] = item['Digest'].hex()
        result['digest_match'] = result['sha384'] == result['manifest_digest']
        if not result['digest_match']:
            raise ValueError(f'{name} SHA384 mismatch')
        pin = expected.get('sha256', {}).get(member)
        if pin and pin != result['sha256']:
            raise ValueError(f'{name} reference SHA256 mismatch')
        result['reference_sha256_match'] = result['sha256'] == pin if pin else None
        components[name] = result
    return {'manifest': hashes(manifest_path), 'product': expected['product'],
            'version': expected['version'], 'build': expected['build'], 'device_class': expected['device_class'],
            'identity_index': index, 'variant': identity['Info']['Variant'], 'components': components,
            'apple_signature_status': 'not_checked', 'kernelcache_format': 'IPSW container; not decompressed Mach-O',
            'scope': 'static content digest checks, no restore/installation operation'}


def source_audit(base):
    inputs = {
        'UniXNU': ['LICENSE', 'feeds.toml', 'scripts/unixnu/config.py', 'drivers/NativeUfs/NativeUfs.cpp',
                   'drivers/NativeAdreno/NativeAdrenoService.cpp'],
        'UniXNU-sheng': ['LICENSE', 'board.toml', 'scripts/make-sheng-adt.py', 'configs/sheng_defconfig'],
        'xnu-ios17-full': ['EXTERNAL_HEADERS/Availability.h'] if (base / 'xnu-ios17-full/EXTERNAL_HEADERS/Availability.h').exists() else ['README.md'],
        'micode-enuma-devicetree': ['qcom/enuma-sm8250.dtsi'],
        'micode-enuma-kernel': ['COPYING', 'Makefile'],
        'uefi-sheng': ['Resources/Configs/sheng.toml'],
    }
    results = {}
    for name, paths in inputs.items():
        path = base / name
        def git(*args):
            return subprocess.check_output(['git', '-c', f'safe.directory={path.as_posix()}', '-C', str(path), *args], text=True).strip()
        results[name] = {'path': path.as_posix(), 'commit': git('rev-parse', 'HEAD'),
                         'repository': git('remote', 'get-url', 'origin'),
                         'tracked_changes': git('diff', 'HEAD', '--name-only').splitlines(),
                         'files': {relative: hashes(path / relative) for relative in paths}}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-root', type=Path, default=Path('D:/Code/PortingiOS'))
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/input-audit.json')
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(ROOT):
        parser.error('output must stay inside the enuma workspace')
    board = tomllib.loads((ROOT / 'board.toml').read_text('utf-8'))
    old = args.reference_root
    cpu_path = old / 'common/reports/enuma-cpu-cache-execution.json'
    cpu = json.loads(cpu_path.read_text('utf-8-sig'))
    result = {'evidence_level': 'static_only', 'device_accessed': False,
              'sources': source_audit(old / 'common/sources'),
              'donor': donor_audit(old / 'common/cache/donor-ipados17', board),
              'fdt': fdt_inventory(old / 'enuma/backups/android-root/20261021T124813939334Z/android-root-fdt.stdout'),
              'historical_cpu': {'input': hashes(cpu_path), 'origin': cpu['origin'],
                                 'decoded': cpu['decoded'], 'status': 'inherited_only_not_rerun'}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(args.output), 'components': len(result['donor']['components']),
                      'fdt_nodes': result['fdt']['node_count'], 'evidence_level': 'static_only'}))


if __name__ == '__main__':
    main()
