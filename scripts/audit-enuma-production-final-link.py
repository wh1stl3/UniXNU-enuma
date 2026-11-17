#!/usr/bin/env python3
"""Read final MachO bytes, not provider source bytes. No runtime protection claim."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[1] / 'UniXNU'
sys.path.insert(0, str(BASE / 'kits/XnuPrelink'))
from native_prelink import macho, backed_offset

OWNERS = {'_verified_root_key': 'provider.o', '_verified_root_policies': 'provider.o',
          '_verified_root_policy_count': 'provider.o', '_vr_open': 'verified_root.o',
          '_vr_verify_block': 'verified_root.o', '_vr_xnu_crypto': 'xnu_crypto.o'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def symbols(data, image):
    tables = [at for cmd, at, _ in image['commands'] if cmd == 2]
    require(len(tables) == 1, 'expected one LC_SYMTAB')
    symoff, count, stroff, size = struct.unpack_from('<4I', data, tables[0] + 8)
    require(symoff + count * 16 <= len(data) and stroff + size <= len(data), 'symbol table out of bounds')
    result = {}
    for i in range(count):
        strx, kind, sect, desc, value = struct.unpack_from('<IBBHQ', data, symoff + 16 * i)
        if kind & 0xe0 or not kind & 1:
            continue
        require(strx < size, 'string offset out of bounds')
        end = data.index(b'\0', stroff + strx, stroff + size)
        name = data[stroff + strx:end].decode()
        result.setdefault(name, []).append({'value': value, 'kind': kind, 'section': sect, 'desc': desc})
    return result


def audit_image(path, expected_hash, reports):
    data = path.read_bytes()
    require(digest(data) == expected_hash, 'final image identity mismatch: ' + str(path))
    image = macho(data)
    names = symbols(data, image)
    undefined = subprocess.check_output(['llvm-nm', '-u', str(path)], text=True)
    require(not undefined.strip(), 'undefined (including weak) in ' + str(path) + ': ' + undefined)
    for name in OWNERS:
        require(len(names.get(name, [])) == 1 and names[name][0]['kind'] & 0xe == 0xe,
                'missing/nonunique section-defined final symbol: ' + name)
    segments = image['segments']
    def read(va, length):
        offset = backed_offset(segments, va, length, len(data))
        return data[offset:offset + length], offset
    def address(name):
        return names[name][0]['value']
    count_blob, count_offset = read(address('_verified_root_policy_count'), 8)
    count, = struct.unpack('<Q', count_blob)
    require(count == 2, 'final policy count not 2')
    table_blob, table_offset = read(address('_verified_root_policies'), count * 16)
    pointers = struct.unpack('<4Q', table_blob)
    key, key_offset = read(address('_verified_root_key'), 395)
    require(digest(key) == reports[0]['anchor_sha256'] == reports[1]['anchor_sha256'], 'final anchor hash mismatch')
    policies = []
    for index, record in enumerate(reports):
        pointer, length = pointers[2 * index:2 * index + 2]
        expected_bytes = 544 + record['blocks_verified'] * 32
        require(length == expected_bytes, 'final policy length mismatch')
        blob, offset = read(pointer, length)
        require(digest(blob) == record['policy_sha256'], 'final embedded policy hash mismatch')
        require(blob[:8] == b'VROOT01\0', 'bad embedded policy magic')
        volume = str(uuid.UUID(bytes=blob[40:56])).upper()
        generation, = struct.unpack_from('<Q', blob, 152)
        image_bytes, blocks = struct.unpack_from('<QQ', blob, 24)
        require(volume == record['volume_uuid'] and generation == record['generation'] and
                image_bytes == record['raw_bytes'] and blocks == record['blocks_verified'],
                'final embedded signed header differs from verified report')
        require(blob[120:152].hex() == digest(key), 'embedded signed anchor binding mismatch')
        segment = next(s for s in segments if s['va'] <= pointer < s['va'] + s['filesize'])
        policies.append({'va': pointer, 'fileoff': offset, 'bytes': length, 'sha256': digest(blob),
                         'uuid': volume, 'generation': generation, 'image_bytes': image_bytes,
                         'segment': segment['name']})
    configure = '__ZN14NativeUfsBlock21configureVerificationEv'
    require(len(names.get(configure, [])) == 1, 'normal consumer missing from final image')
    start = names[configure][0]['value']
    end = min(v['value'] for entries in names.values() for v in entries if v['value'] > start and v['kind'] & 0xe == 0xe)
    code, _ = read(start, end - start)
    vr_calls = []
    for i in range(0, len(code) - 3, 4):
        word, = struct.unpack_from('<I', code, i)
        if word & 0xfc000000 == 0x94000000:
            delta = word & 0x3ffffff
            if delta & 0x2000000:
                delta -= 0x4000000
            if start + i + delta * 4 == address('_vr_open'):
                vr_calls.append(start + i)
    require(vr_calls and len(code) > 8, 'final configureVerification lost its real vr_open call')
    fixups = []
    table_relocs = []
    for cmd, at, length in image['commands']:
        if cmd in (0x22, 0x80000022, 0x80000034, 0xb):
            fixups.append({'command': hex(cmd), 'fileoff': at,
                           'payload_words': list(struct.unpack_from('<' + 'I' * ((length - 8) // 4), data, at + 8))})
        if cmd == 0xb:
            words = struct.unpack_from('<18I', data, at + 8)
            reloff, nrel = words[16:18]
            require(reloff + 8 * nrel <= len(data), 'local reloc table out of bounds')
            base = next(s['va'] for s in segments if s['name'] == '__TEXT')
            slots = {address('_verified_root_policies') - base + i * 16 for i in range(2)}
            for i in range(nrel):
                r_address, info = struct.unpack_from('<II', data, reloff + i * 8)
                if r_address in slots:
                    table_relocs.append({'fileoff': reloff + i * 8, 'r_address': r_address, 'r_info': info})
    return {'path': str(path), 'bytes': len(data), 'sha256': digest(data), 'undefined': [],
            'symbols': {n: names[n][0] for n in OWNERS}, 'count': count, 'count_fileoff': count_offset,
            'table_fileoff': table_offset, 'table_raw_hex': table_blob.hex(), 'policies': policies,
            'anchor': {'va': address('_verified_root_key'), 'fileoff': key_offset, 'bytes': len(key), 'sha256': digest(key)},
            'segments': [{k: s[k] for k in ('name', 'va', 'size', 'fileoff', 'filesize', 'maxprot', 'initprot')}
                         for s in segments], 'fixup_load_commands': fixups,
            'table_local_relocations_matching_TEXT_relative_slots': table_relocs,
            'configureVerification_va': start, 'configureVerification_calls_vr_open': vr_calls}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-json', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    require(not a.output.exists(), 'refuse to overwrite audit evidence')
    build = json.loads(a.build_json.read_text())
    out = a.build_json.parent
    for path, identity in build['inputs'].items():
        require(digest(Path(path).read_bytes()) == identity['sha256'], 'build input changed after recording: ' + path)
    reports = [json.loads((ROOT / f'out/verify-fresh-20261113/{s}/result.json').read_text()) for s in ('os', 'systemos')]
    result = {'status': 'self-checked', 'runtime_protection_verified': False,
              'validation': 'final MachO byte extraction and inherited verified-input hashes, not signature revalidation'}
    text = (out / 'native-link.map').read_text(errors='replace')
    owners = dict(re.findall(r'^\[\s*(\d+)\]\s+(.+)$', text, re.M))
    archive_paths = sorted({m[1] for owner in owners.values() if (m := re.match(r'(.+\.a)\(', owner))})
    result['contributing_archive_identities'] = {path: {'bytes': Path(path).stat().st_size,
                                                       'sha256': digest(Path(path).read_bytes())}
                                                for path in archive_paths}
    for path, identity in result['contributing_archive_identities'].items():
        require(identity['sha256'] == build['inputs'][path]['sha256'], 'unbound contributing archive: ' + path)
    active = text.split('# Symbols:', 1)[1].split('# Dead Stripped Symbols:', 1)[0]
    attribution = {}
    for name, member in OWNERS.items():
        matches = re.findall(r'^\s*(0x[0-9A-Fa-f]+)\s+0x[0-9A-Fa-f]+\s+\[\s*(\d+)\]\s+' + re.escape(name) + r'\s*$', active, re.M)
        require(len(matches) == 1, 'missing/duplicate live map symbol: ' + name)
        va, index = matches[0]
        owner = owners[index]
        require(owner == str(out / 'libVerifiedRootProduction.a') + '(' + member + ')', 'wrong archive member: ' + owner)
        attribution[name] = {'va': int(va, 16), 'owner': owner}
    result['archive_extraction_owners'] = attribution
    member_hashes = {}
    for name in ('verified_root.o', 'xnu_crypto.o', 'provider.o'):
        path = ROOT / 'out/provider-rebuild-20261113' / name
        blob = subprocess.check_output(['llvm-ar', 'p', str(out / 'libVerifiedRootProduction.a'), name])
        require(digest(blob) == build['inputs'][str(path)]['sha256'], 'archive member differs from bound provider object')
        member_hashes[name] = digest(blob)
    result['archive_member_input_hashes'] = member_hashes
    result['map_sha256'] = digest((out / 'native-link.map').read_bytes())
    result['provider_archive_sha256'] = digest((out / 'libVerifiedRootProduction.a').read_bytes())
    result['native'] = audit_image(out / 'native.macho', build['native_sha256'], reports)
    result['prelink'] = audit_image(out / 'prelink.macho', build['prelink_sha256'], reports)
    for name, entry in attribution.items():
        require(result['native']['symbols'][name]['value'] == entry['va'] ==
                result['prelink']['symbols'][name]['value'], 'native/prelink/map VA mismatch: ' + name)
    result['consumer'] = {'sha256': build['consumer_sha256'], 'patch_sha256': build['consumer_patch_sha256'],
                           'configureVerification': 'nonconstant; retained verification imports checked by runner',
                           'runtime_copy_bytes_each': [((544 + r['blocks_verified'] * 32 + 4095) // 4096) * 4096 + 4096 for r in reports],
                           'lifecycle_scope': 'source allocates copied policy/key, calls vm_map_protect then vr_open; runtime success and lifelong immutability not established'}
    result['budget'] = {'limit_bytes': 192 * 1024 * 1024,
                        'native_file_bytes': result['native']['bytes'],
                        'prelink_file_bytes': result['prelink']['bytes'],
                        'embedded_envelope_bytes': sum(p['bytes'] for p in result['prelink']['policies']),
                        'production_data_seed_bytes': None, 'complete_payload_fits': None,
                        'note': 'measured existing diagnostic ADT/restore trust are reference costs, not production identity/trust qualification; no restore scratch counted as seed'}
    assets = []
    for label, path in (
            ('existing_diagnostic_adt_reference', ROOT / '.cache/ufs-adt-equivalence-24r-20261111/enabled.adt'),
            ('existing_restore_only_trust_reference', Path('/root/enuma-step10/UniXNU/out/ipsw/21H461/restore-trust.bundle'))):
        blob = path.read_bytes()
        assets.append({'role': label, 'path': str(path), 'bytes': len(blob), 'sha256': digest(blob),
                       'production_input': False})
    budget = result['budget']
    budget['existing_reference_assets'] = assets
    budget['kernel_plus_existing_reference_assets_bytes'] = result['prelink']['bytes'] + sum(x['bytes'] for x in assets)
    budget['headroom_after_existing_reference_assets_before_seed_and_packaging'] = budget['limit_bytes'] - budget['kernel_plus_existing_reference_assets_bytes']
    budget['production_OS_trust_bytes'] = None
    budget['production_trust_status'] = 'two OS trust hashes pinned in profile; actual OS trust assets not supplied to this isolated runner; restore trust is not substituted'
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print('self-checked: native/prelink zero undefined; six live archive owners; final policy/anchor bytes bound')


if __name__ == '__main__':
    main()
