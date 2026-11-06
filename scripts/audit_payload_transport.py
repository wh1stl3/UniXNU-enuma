"""Quantify saved boot-v3 inputs; no runtime FDT/mapping or firmware claim."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bp_matches(blob):
    if len(blob) < 512:
        return False
    sectors = struct.unpack_from('<H', blob, 19)[0] or struct.unpack_from('<I', blob, 32)[0]
    return (blob[510:512] == b'\x55\xaa' and struct.unpack_from('<H', blob, 11)[0] == 512
            and sectors * 512 == len(blob))


def main():
    lock = json.loads((ROOT / 'config/system-reuse-sources.lock.json').read_text())['references'][0]
    relative = 'overlay/Platforms/Xiaomi/umiPkg/Drivers/UmiRamPayloadDxe/UmiRamPayload.c'
    source = ROOT / Path(lock['local'].replace('\\', '/')) / relative
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_sha != lock['files'][relative]['sha256']:
        raise ValueError('umi template changed')
    vendor = (ROOT / 'out/device-tests/20261022T201404/vendor_boot_a.bin').read_bytes()
    if hashlib.sha256(vendor).hexdigest() != '3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba':
        raise ValueError('stock vendor_boot differs')
    if vendor[:8] != b'VNDRBOOT' or struct.unpack_from('<I', vendor, 8)[0] != 3:
        raise ValueError('expected stock boot v3')
    page = struct.unpack_from('<I', vendor, 12)[0]
    length = struct.unpack_from('<I', vendor, 24)[0]
    header = struct.unpack_from('<I', vendor, 2096)[0]
    if page != 4096 or header != 2112:
        raise ValueError('unexpected vendor geometry')
    offset = (header + page - 1) // page * page
    prefix = vendor[offset:offset + length]
    if len(prefix) != length:
        raise ValueError('truncated vendor ramdisk')
    payload = (ROOT / 'out/full-boot/payload/payload.img').read_bytes()
    expected = json.loads((ROOT / 'reports/enuma-full-payload.json').read_text())['payload_sha256']
    if hashlib.sha256(payload).hexdigest() != expected or not bp_matches(payload):
        raise ValueError('FAT identity or exact BPB span mismatch')
    variants = []
    for label, front in [('raw-vendor-prefix', prefix), ('page-padded-vendor-prefix', prefix + bytes(-length % page))]:
        combined = front + payload
        if bp_matches(combined):
            raise ValueError('unexpected whole-initrd FAT acceptance')
        variants.append(dict(hypothesis=label, not_runtime_observation=True,
                             prefix_bytes=len(front), relative_fat_offset_sector_aligned=len(front) % 512 == 0,
                             whole_span_passes_umi_bpb_check=False,
                             exact_fat_subrange_passes_bpb_check=bp_matches(combined[len(front):])))
    report = dict(scope='offline saved files and pinned template; synthetic combinations only',
                  umi_template_sha256=source_sha, vendor_ramdisk_bytes=length,
                  vendor_ramdisk_sha256=hashlib.sha256(prefix).hexdigest(),
                  fat_bytes=len(payload), fat_sha256=expected, hypotheses=variants,
                  runtime_initrd_layout='unknown; neither prefix form is selected by this audit',
                  firmware_changed=False, hardware_tested=False,
                  next_requirements=['actual entry FDT initrd start/end and exact combination rule',
                                     'reviewed mapped/reserved lifetime before dereferencing FDT or initrd',
                                     'derive exact FAT subrange, reject ambiguity/overflow/overlap; never scan arbitrary RAM',
                                     'reuse read-only BlockIO and require SFS binding plus file identity evidence'])
    (ROOT / 'reports/enuma-payload-transport.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: pure FAT BPB exact; saved vendor prefix is 2230 bytes; both hypothetical whole-initrd forms rejected')


if __name__ == '__main__':
    main()
