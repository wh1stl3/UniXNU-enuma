#!/usr/bin/env python3
"""Pure cached-data parser. No collector, protocol calls, device access or activation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'scripts/data/enuma-ufs-identity.schema.json'
CONTRACT = json.loads(SCHEMA.read_text())
END = b'\x7f\xff\x04\x00'
REVISIONS = (0x10000, 0x20001, 0x2001f)


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def fields(value, allowed, required, name):
    need(type(value) is dict and not (set(value) - set(allowed)) and set(required) <= set(value),
         'invalid/unsupported fields: ' + name)


def uint(value, bits=64):
    need(type(value) is int and 0 <= value < 1 << bits, 'invalid unsigned integer')
    return value


def raw_hex(text, maximum=16384):
    need(type(text) is str and re.fullmatch(r'(?:[0-9a-fA-F]{2})+', text) is not None,
         'invalid raw hex')
    need(len(text) <= maximum * 2, 'input bytes exceed bound')
    return bytes.fromhex(text)


def device_path(text):
    data = raw_hex(text)
    at = 0; nodes = []; transport = []; hd = None; unknown = []
    while at < len(data):
        need(len(nodes) < 128 and at + 4 <= len(data), 'truncated/bounded device path')
        typ, sub, length = struct.unpack_from('<BBH', data, at)
        need(length >= 4, 'illegal node length')
        need(at + length <= len(data), 'truncated device path node')
        node = data[at:at + length]
        if typ == 0x7f:
            need(sub == 0xff and length == 4 and at + length == len(data),
                 'unsupported multi-instance/end or trailing path bytes')
            return {'bytes': data, 'transport': transport, 'hd': hd, 'unknown_nodes': unknown}
        if (typ, sub) == (3, 0x19):
            need(length == 6, 'invalid UFS node length')
            transport.append({'kind': 'UFS', 'pun': node[4], 'lun': node[5]})
        elif (typ, sub) == (3, 2):
            need(length == 8, 'invalid SCSI node length')
            pun, lun = struct.unpack_from('<HH', node, 4)
            transport.append({'kind': 'SCSI', 'pun': pun, 'lun': lun})
        elif (typ, sub) == (4, 1):
            need(length == 42 and hd is None, 'invalid/duplicate HD node')
            number, start, count, signature, mbr, sigtype = struct.unpack_from('<IQQ16sBB', node, 4)
            need(count > 0 and start + count <= 1 << 64, 'HD geometry overflow/empty')
            need(sigtype in (0, 1, 2) and mbr in (1, 2), 'unsupported HD signature format')
            need(sigtype != 0 or signature == bytes(16), 'nonzero absent signature')
            need(sigtype != 1 or signature[4:] == bytes(12), 'invalid MBR signature padding')
            hd = {'number': number, 'start': start, 'count': count, 'signature': signature,
                  'mbr': mbr, 'signature_type': sigtype, 'parent_bytes': data[:at] + END,
                  'last_node': at + length + 4 == len(data)}
        else:
            unknown.append({'type': typ, 'subtype': sub})
        nodes.append((typ, sub)); at += length
    raise ValueError('missing complete device path end')


def media_fields(record):
    revision = record['block_io_revision']
    need(type(revision) is int and revision in REVISIONS, 'unsupported BlockIo Revision')
    media = record['media']; definition = CONTRACT['$defs']['media']
    fields(media, definition['properties'], definition['required'], 'media')
    for name, value in media.items():
        if definition['properties'][name].get('type') == 'boolean':
            need(type(value) is bool, 'invalid BOOLEAN')
        else:
            uint(value, 64 if name in ('LastBlock', 'LowestAlignedLba') else 32)
    for name in ('LowestAlignedLba', 'LogicalBlocksPerPhysicalBlock'):
        need(name not in media or revision >= REVISIONS[1], 'Revision insufficient for ' + name)
    need('OptimalTransferLengthGranularity' not in media or revision >= REVISIONS[2],
         'Revision insufficient for OptimalTransferLengthGranularity')
    block = media['BlockSize']; align = media['IoAlign']
    need(block > 0 and (align in (0, 1) or align & (align - 1) == 0), 'invalid block size/alignment')
    need((media['LastBlock'] + 1) * block < 1 << 64, 'cached capacity overflow')
    return media


def parse(snapshot):
    fields(snapshot, CONTRACT['properties'], CONTRACT['required'], 'snapshot')
    need(type(snapshot['schema_version']) is int and snapshot['schema_version'] == 2, 'unsupported schema version')
    provenance = snapshot['provenance']
    fields(provenance, ('kind', 'source'), ('kind', 'source'), 'provenance')
    need(provenance['kind'] in ('synthetic', 'existing') and type(provenance['source']) is str and provenance['source'],
         'explicit input provenance required')
    records = snapshot['records']
    need(type(records) is list and len(records) <= 64, 'record count bound')
    envelope = snapshot['envelope']
    definition = CONTRACT['$defs']['envelope']
    fields(envelope, definition['properties'], definition['required'], 'envelope')
    need(type(envelope['candidate_id']) is str and re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', envelope['candidate_id']), 'candidate identity required')
    need(type(envelope['capture_complete']) is bool and type(envelope['truncated']) is bool, 'invalid completeness flags')
    need(type(envelope['incomplete_reason']) is str and envelope['handle_limit'] == 64 and type(envelope['handle_limit']) is int, 'invalid completeness contract')
    count = uint(envelope['reported_handles'], 32)
    completeness = []
    if not envelope['capture_complete'] or envelope['truncated'] or envelope['incomplete_reason']:
        completeness.append('capture incomplete/truncated or reported reason')
    if count > 64 or count != len(records):
        completeness.append('handle count exceeds limit or records missing')
    parsed = []; ids = set()
    for record in records:
        definition = CONTRACT['$defs']['record']
        fields(record, definition['properties'], definition['required'], 'record')
        label = record['id']
        need(type(label) is str and re.fullmatch(r'[a-zA-Z0-9_-]{1,40}', label), 'invalid local record id')
        need(label not in ids, 'duplicate record id'); ids.add(label)
        need(record['status'] in CONTRACT['$defs']['record']['properties']['status']['enum'] and
             type(record['reason']) is str and type(record['truncated']) is bool, 'invalid item status')
        if record['status'] != 'ok' or record['truncated'] or record['reason']:
            completeness.append('candidate record unread/failed/changed')
            parsed.append((record, None, None))
        else:
            parsed.append((record, media_fields(record), device_path(record['device_path_hex'])))
    gpt = snapshot.get('gpt_reference')
    if gpt is not None:
        definition = CONTRACT['$defs']['gpt']
        fields(gpt, definition['properties'], definition['required'], 'GPT reference')
        need(type(gpt['evidence_ref']) is str and gpt['evidence_ref'], 'missing GPT provenance')
        need(type(gpt['logical_block_bytes']) is int and gpt['logical_block_bytes'] == 4096,
             'GPT logical block bytes must be4096, not Linux512-byte sectors')
        first, last = uint(gpt['first_lba']), uint(gpt['last_lba_inclusive'])
        need(first <= last and (last + 1) * 4096 < 1 << 64, 'GPT window overflow/reversed')
        if 'total_bytes' in gpt:
            total = uint(gpt['total_bytes'])
            need(total % 4096 == 0 and (last + 1) * 4096 <= total, 'GPT window outside capacity')
        if 'partition_number' in gpt:
            uint(gpt['partition_number'], 32)
        if 'partition_signature_hex' in gpt:
            need(len(raw_hex(gpt['partition_signature_hex'], 16)) == 16, 'invalid GPT signature bytes')
        if 'input_sha256' in gpt:
            need(type(gpt['input_sha256']) is str and re.fullmatch(r'[a-f0-9]{64}', gpt['input_sha256']), 'invalid GPT input hash')
        if 'partition_name' in gpt:
            need(gpt['partition_name'] == 'userdata', 'reference must identify userdata')
    # These optional cached/public observations cannot grant existence/ownership.
    legal = snapshot.get('legal_target_luns', [])
    need(type(legal) is list and len(legal) <= 64, 'legal target list bound')
    for item in legal:
        fields(item, ('target_hex', 'lun'), ('target_hex', 'lun'), 'legal target/lun')
        raw_hex(item['target_hex'], 16); uint(item['lun'])
    public = snapshot.get('public_evidence', {})
    fields(public, ('selector', 'iort_route_reference'), (), 'public evidence')
    if 'selector' in public:
        uint(public['selector'], 32)
    if 'iort_route_reference' in public:
        need(type(public['iort_route_reference']) is str, 'invalid public table reference')
    results = []
    for record, media, path in parsed:
        if path is None:
            results.append({'id': record['id'], 'synthetic': provenance['kind'] == 'synthetic', 'partition_association': 'UNKNOWN',
                            'reasons': [record['status'], record['reason'] or 'unread/truncated candidate'], 'device_exists_now': 'UNKNOWN'})
            continue
        reasons = list(completeness); association = 'UNKNOWN'; hd = path['hd']
        same_path = [r for r, _, p in parsed if p is not None and p['bytes'] == path['bytes']]
        if len(same_path) != 1:
            reasons.append('duplicate/ambiguous complete path')
        if len(path['transport']) > 1:
            reasons.append('ambiguous transport nodes; no target/LUN chosen')
        if any(n['type'] not in (1, 2) for n in path['unknown_nodes']):
            reasons.append('unsupported non-controller path node; no UFS identity inferred')
        if hd is not None:
            parents = [(r, m, p) for r, m, p in parsed if p is not None and p['hd'] is None and p['bytes'] == hd['parent_bytes']]
            if len(parents) != 1:
                reasons.append('missing/ambiguous complete parent path')
            else:
                parent, parent_media, _ = parents[0]
                if parent_media['LogicalPartition'] or not media['LogicalPartition'] or not hd['last_node']:
                    reasons.append('partition/parent path role not established')
                elif media['BlockSize'] != parent_media['BlockSize'] or media['BlockSize'] != 4096:
                    reasons.append('4096/512 logical-block unit mismatch')
                elif media['LastBlock'] + 1 != hd['count'] or hd['start'] + hd['count'] > parent_media['LastBlock'] + 1:
                    reasons.append('HD geometry disagrees with cached media bounds')
                elif gpt is not None and 'total_bytes' in gpt and gpt['total_bytes'] != (parent_media['LastBlock'] + 1) * parent_media['BlockSize']:
                    reasons.append('cached parent capacity contradicts GPT reference; capacity is not identity')
                elif gpt is None or not {'partition_signature_hex', 'partition_number', 'input_sha256', 'partition_name'} <= set(gpt):
                    reasons.append('independent GPT signature/provenance missing; capacity alone insufficient')
                else:
                    signature = raw_hex(gpt['partition_signature_hex'], 16)
                    need(len(signature) == 16, 'invalid GPT signature bytes')
                    if hd['mbr'] != 2 or hd['signature_type'] != 2 or signature == bytes(16) or hd['number'] == 0:
                        reasons.append('GPT signature type/partition number not matched')
                    elif signature != hd['signature'] or uint(gpt['partition_number'], 32) != hd['number']:
                        reasons.append('partition signature/number mismatch')
                    elif hd['start'] != gpt['first_lba'] or hd['count'] != gpt['last_lba_inclusive'] - gpt['first_lba'] + 1:
                        reasons.append('GPT/HD geometry mismatch; units are logical blocks, not Linux sectors')
                    elif not reasons:
                        association = 'MATCHED_WITHIN_SYNTHETIC_SNAPSHOT' if provenance['kind'] == 'synthetic' else 'MATCHED_CACHED_SNAPSHOT_ONLY'
        else:
            reasons.append('whole-device path only; capacity is not unique identity')
        results.append({'id': record['id'], 'synthetic': provenance['kind'] == 'synthetic',
            'path_sha256': hashlib.sha256(path['bytes']).hexdigest(),
            'path_transport': path['transport'][0] if len(path['transport']) == 1 else 'UNKNOWN',
            'unknown_path_nodes': path['unknown_nodes'], 'partition_association': association, 'reasons': reasons,
            'media_present': 'cached only, not current existence', 'media_id_identity': 'UNKNOWN: not persistent',
            'device_exists_now': 'UNKNOWN', 'passthru_mode_lun': 'UNKNOWN: Mode is adapter information',
            'sid_context_exclusivity': 'UNKNOWN: selector/public IORT route is not SID or ownership'})
    matches = [r for r in results if r['partition_association'] != 'UNKNOWN']
    ufs = 'UNKNOWN'; match = 'UNKNOWN'; reason = completeness[0] if completeness else 'NO_UNIQUE_USERDATA_MATCH'
    if not completeness and len(matches) == 1:
        match = 'MATCH_CACHED_ONLY'
        transport = matches[0]['path_transport']
        if isinstance(transport, dict) and transport['kind'] == 'UFS':
            ufs = transport['lun']; reason = 'CACHED_ONLY_NOT_LIVE_EXISTENCE'
        else:
            reason = 'SCSI_ONLY_OR_UNSUPPORTED_UFS_TRANSPORT'
    elif len(matches) > 1:
        reason = 'AMBIGUOUS_USERDATA_MATCHES'
        for r in matches:
            r['partition_association'] = 'UNKNOWN'; r['reasons'].append(reason)
    return {'validation': 'self-checked host parsing only', 'provenance': provenance,
            'synthetic': provenance['kind'] == 'synthetic', 'records': results,
            'envelope': envelope, 'global_uniqueness_eligible': not completeness,
            'summary': {'label': 'CACHED ONLY', 'userdata': match, 'ufs_lun_candidate': ufs, 'reason': reason},
            'legal_target_existence': 'UNKNOWN: legal GetNextTargetLun position does not prove presence',
            'activation_readiness': 'UNKNOWN', 'current_device_identity': 'UNKNOWN',
            'limits': 'No protocol/device calls; cached matching is not runtime identity, DMA ownership or permission to collect/enable.'}


def gpt_reference_from_report(report):
    """Reuse sanitized original-GPT evidence, never manufacture its UEFI association."""
    gpt = report['gpt']
    need(gpt['status'] == 'primary_snapshot_checked', 'GPT report not checked original input')
    return {'evidence_ref': '.cache/ufs-evidence/report.json#gpt (historical primary only)',
            'logical_block_bytes': gpt['logical_block_bytes'], 'total_bytes': gpt['total_bytes'],
            'first_lba': gpt['userdata']['first_lba'], 'last_lba_inclusive': gpt['userdata']['last_lba_inclusive']}


def historical_gpt_reference():
    """Read existing host capture only. GUID bytes stay in ignored output, never console."""
    path = ROOT / '.cache/live-capture/20261107T141941555586Z'
    raw = (path / 'sda_first_32768.bin').read_bytes()
    spec = importlib.util.spec_from_file_location('gpt_evidence', ROOT / 'scripts/check-enuma-ufs-evidence.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    block = int((path / 'sda_logical_block_size.txt').read_text())
    geometry = helper.gpt_evidence(raw, block, int((path / 'sda_sectors.txt').read_text()))
    entries, count, stride = struct.unpack_from('<QII', raw, block + 72)
    matches = []
    for index in range(count):
        entry = raw[entries * block + index * stride:entries * block + (index + 1) * stride]
        if entry[:16] != bytes(16) and entry[56:128].decode('utf-16-le').split('\0', 1)[0] == 'userdata':
            matches.append((index + 1, entry[16:32]))
    need(len(matches) == 1 and matches[0][1] != bytes(16), 'missing/ambiguous GPT userdata GUID')
    number, signature = matches[0]
    return dict(gpt_reference_from_report({'gpt': geometry}), partition_name='userdata', partition_number=number,
                partition_signature_hex=signature.hex(), input_sha256=hashlib.sha256(raw).hexdigest(),
                evidence_ref='.cache/live-capture/20261107T141941555586Z/sda_first_32768.bin (historical primary)')


def synthetic_demo():
    # Fabricated byte paths/partition signature. No real device/GUID is used.
    opaque_root = struct.pack('<BBH', 1, 4, 20) + bytes(range(16))
    parent = opaque_root + bytes((3, 0x19, 6, 0, 1, 3)) + END
    signature = bytes(range(16))
    hd = struct.pack('<BBHIQQ16sBB', 4, 1, 42, 7, 10, 20, signature, 2, 2)
    media = dict(MediaId=5, RemovableMedia=False, MediaPresent=True, LogicalPartition=False,
                 ReadOnly=False, WriteCaching=False, BlockSize=4096, IoAlign=8, LastBlock=99)
    return {'schema_version': 2, 'provenance': {'kind': 'synthetic', 'source': 'self-generated cached-data fixture, not enuma observation'},
            'envelope': {'candidate_id': 'synthetic-host', 'capture_complete': True, 'reported_handles': 2, 'handle_limit': 64, 'truncated': False, 'incomplete_reason': ''},
            'records': [{'id': 'fabricated-parent', 'status': 'ok', 'reason': '', 'truncated': False, 'block_io_revision': 0x10000, 'media': media, 'device_path_hex': parent.hex()},
                        {'id': 'fabricated-partition', 'status': 'ok', 'reason': '', 'truncated': False, 'block_io_revision': 0x10000, 'media': dict(media, LogicalPartition=True, LastBlock=19),
                         'device_path_hex': (parent[:-4] + hd + END).hex()}],
            'gpt_reference': {'evidence_ref': 'self-generated synthetic partition table', 'logical_block_bytes': 4096,
                 'first_lba': 10, 'last_lba_inclusive': 29, 'partition_number': 7,
                 'partition_signature_hex': signature.hex(), 'partition_name': 'userdata', 'input_sha256': hashlib.sha256(b'synthetic-gpt').hexdigest()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, nargs='?')
    parser.add_argument('--synthetic-demo', action='store_true')
    parser.add_argument('--historical-gpt-reference', action='store_true')
    args = parser.parse_args()
    need(sum((bool(args.input), args.synthetic_demo, args.historical_gpt_reference)) == 1, 'choose one explicit input mode')
    directory = ROOT / '.cache/ufs-identity-snapshot'
    subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '-q', str(directory / 'report.json')], check=True)
    directory.mkdir(parents=True, exist_ok=True)
    if args.historical_gpt_reference:
        (directory / 'historical-gpt-reference.json').write_text(json.dumps(historical_gpt_reference(), indent=2) + '\n')
        print('self-checked historical GPT reference extracted locally; no UEFI identity observed')
        return 0
    try:
        if args.synthetic_demo:
            snapshot = synthetic_demo()
            (directory / 'synthetic-input.json').write_text(json.dumps(snapshot, indent=2) + '\n')
        else:
            need(args.input.resolve().is_relative_to((ROOT / '.cache').resolve()), 'input must be local ignored enuma cache')
            snapshot = json.loads(args.input.read_text())
        result = parse(snapshot)
    except (ValueError, KeyError, TypeError, struct.error) as exc:
        (directory / 'report.json').write_text(json.dumps({'validation': 'REJECTED', 'reason': str(exc)}) + '\n')
        print('REJECTED snapshot contract/bytes; no device identity established')
        return 1
    (directory / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print('self-checked host parse; synthetic=' + str(result['synthetic']) + '; current device identity UNKNOWN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
