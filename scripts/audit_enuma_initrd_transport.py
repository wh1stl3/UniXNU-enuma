"""Audit retained stock v3 headers and Android FDT; no device or candidate boot."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from audit_inputs import parse_fdt, strings

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup', type=Path, required=True)
    parser.add_argument('--fdt', type=Path, required=True)
    args = parser.parse_args()
    expected = {'boot_a.bin': '8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959',
                'vendor_boot_a.bin': '3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba'}
    evidence = {}
    headers = {}
    for name, wanted in expected.items():
        path = args.backup / name
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            headers[name] = stream.read(4096)
            stream.seek(0)
            while chunk := stream.read(4 << 20):
                digest.update(chunk)
        if digest.hexdigest() != wanted:
            raise ValueError('Backup digest mismatch: ' + name)
        evidence[name] = {'sha256': wanted, 'partition_bytes': path.stat().st_size}
    boot, vendor = headers['boot_a.bin'], headers['vendor_boot_a.bin']
    if boot[:8] != b'ANDROID!' or struct.unpack_from('<I', boot, 40)[0] != 3:
        raise ValueError('Expected retained stock boot v3')
    if vendor[:8] != b'VNDRBOOT' or struct.unpack_from('<I', vendor, 8)[0] != 3:
        raise ValueError('Expected retained stock vendor_boot v3')
    kernel_size, generic_size, _, boot_header = struct.unpack_from('<4I', boot, 8)
    page = struct.unpack_from('<I', vendor, 12)[0]
    vendor_size = struct.unpack_from('<I', vendor, 24)[0]
    vendor_header, dtb_size = struct.unpack_from('<II', vendor, 2096)
    if boot_header != 1580 or vendor_header != 2112 or page != 4096:
        raise ValueError('Unexpected retained v3 geometry')
    fdt = args.fdt.read_bytes()
    retained = json.loads((ROOT / 'reports/enuma-uart-discovery.json').read_text())
    fdt_hash = hashlib.sha256(fdt).hexdigest()
    if fdt_hash != retained['fdt_sha256']:
        raise ValueError('Expected the retained UART-discovery Android FDT')
    nodes = parse_fdt(fdt)
    if strings(nodes['/'].get('model', b'')) != ['Qualcomm Technologies, Inc. xiaomi enuma']:
        raise ValueError('FDT device identity mismatch')
    chosen = nodes.get('/chosen', {})
    values = []
    for key in ('linux,initrd-start', 'linux,initrd-end'):
        raw = chosen.get(key, b'')
        if len(raw) not in (4, 8):
            raise ValueError('Missing or malformed retained chosen initrd')
        values.append(int.from_bytes(raw, 'big'))
    start, end = values
    if end <= start:
        raise ValueError('Invalid retained Android initrd range')
    length = end - start
    report = {
        'scope': 'retained stock headers and historical Android FDT only; not temporary UEFI candidate',
        'stock_backups': evidence,
        'stock_boot': {'version': 3, 'kernel_bytes': kernel_size, 'generic_ramdisk_bytes': generic_size},
        'stock_vendor_boot': {'version': 3, 'page_bytes': page, 'vendor_ramdisk_bytes': vendor_size,
                              'dtb_bytes': dtb_size},
        'android_fdt': {'captured_at': retained['captured_at'], 'sha256': fdt_hash,
                        'initrd_start': hex(start), 'initrd_end': hex(end), 'initrd_bytes': length,
                        'length_mod_512': length % 512,
                        'delta_from_declared_ramdisk_sum': length - generic_size - vendor_size},
        'whole_initrd_sector_precondition_met_for_historical_android': length % 512 == 0,
        'temporary_candidate_chosen_observed': False,
        'candidate_fat_offset_known': False,
        'readable_uefi_memory_span_established': False,
        'new_device_trials': 0,
        'conclusion': 'Do not infer candidate initrd geometry, FAT offset, ownership or discovery from this Android snapshot',
    }
    (ROOT / 'reports/enuma-initrd-transport.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: retained v3 headers/FDT; Android initrd {length} bytes, mod512={length % 512}; candidate transport unknown')


if __name__ == '__main__':
    main()
